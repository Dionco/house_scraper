"""
Railway-optimized periodic scraper with persistent scheduling.
This version handles Railway's restart scenarios and ensures scraping continues.
"""
import os
import json
import logging
import gc
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.jobstores.memory import MemoryJobStore
import signal
import sys
import threading
import time

def is_running_on_railway() -> bool:
    """Check if the application is running on Railway."""
    return any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("PORT")  # Railway sets this automatically
    ])

try:
    from .timezone_utils import now_cest_iso, now_cest, CEST
except ImportError:
    try:
        from timezone_utils import now_cest_iso, now_cest, CEST
    except ImportError:
        from datetime import datetime
        import pytz
        
        def now_cest_iso():
            return datetime.now(pytz.timezone('Europe/Amsterdam')).isoformat()
        
        def now_cest():
            return datetime.now(pytz.timezone('Europe/Amsterdam'))
        
        CEST = pytz.timezone('Europe/Amsterdam')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import scraping functions
try:
    from .funda_url_builder import build_rental_url
    from .scrape_funda import scrape_funda_html
    from .extract_funda_listings import extract_simple_listings_from_html
    from .listing_mapping import map_listing_for_frontend
    from .email_utils import send_new_listings_email
except ImportError:
    from funda_url_builder import build_rental_url
    from scrape_funda import scrape_funda_html
    from extract_funda_listings import extract_simple_listings_from_html
    from listing_mapping import map_listing_for_frontend
    from email_utils import send_new_listings_email

class RailwayPeriodicScraper:
    """
    Railway-optimized periodic scraper that handles restarts and ensures continuous operation.
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler(
            jobstores={'default': MemoryJobStore()},
            timezone=CEST
        )
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
        self.is_running = False
        self._shutdown_event = threading.Event()
        
        # Railway-specific configuration
        self.railway_mode = is_running_on_railway()
        self.heartbeat_interval = 30  # seconds
        self.max_concurrent_scrapes = 3
        self.scrape_semaphore = threading.Semaphore(self.max_concurrent_scrapes)
        
        # Register shutdown handlers
        signal.signal(signal.SIGTERM, self._shutdown_handler)
        signal.signal(signal.SIGINT, self._shutdown_handler)
        
        logger.info(f"Railway mode: {self.railway_mode}")
        logger.info(f"Initializing scraper with timezone: {CEST}")
    
    def _shutdown_handler(self, signum, frame):
        """Handle graceful shutdown on Railway restart."""
        logger.info(f"Received shutdown signal {signum}, shutting down gracefully...")
        self._shutdown_event.set()
        self.stop()
        sys.exit(0)
    
    def _job_listener(self, event):
        """Log job events for monitoring."""
        if event.exception:
            logger.error(f"Job {event.job_id} failed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} completed successfully")
    
    def start(self):
        """Start the periodic scraper with Railway optimizations."""
        if self.is_running:
            logger.warning("Scraper is already running")
            return
        
        try:
            # First, sanitize any invalid intervals in the database
            logger.info("Sanitizing database intervals...")
            self.sanitize_db_intervals()
            
            # Load existing profiles and schedule them
            self._load_and_schedule_profiles()
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            
            logger.info("Periodic scraper started successfully")
            
            # Start heartbeat for Railway monitoring
            if self.railway_mode:
                self._start_heartbeat()
                
        except Exception as e:
            logger.error(f"Failed to start periodic scraper: {e}")
            raise
    
    def stop(self):
        """Stop the periodic scraper."""
        if not self.is_running:
            return
        
        try:
            self.scheduler.shutdown(wait=True)
            self.is_running = False
            logger.info("Periodic scraper stopped")
        except Exception as e:
            logger.error(f"Error stopping scraper: {e}")
    
    def _start_heartbeat(self):
        """Start Railway heartbeat to prevent sleeping."""
        def heartbeat():
            while not self._shutdown_event.is_set():
                try:
                    # Log heartbeat
                    logger.debug(f"Heartbeat: {datetime.now().isoformat()}")
                    
                    # Check if we need to reschedule any profiles
                    self._check_and_reschedule_profiles()
                    
                    # Wait for next heartbeat
                    if self._shutdown_event.wait(self.heartbeat_interval):
                        break
                        
                except Exception as e:
                    logger.error(f"Heartbeat error: {e}")
                    time.sleep(60)  # Wait a minute before retrying
        
        heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
        heartbeat_thread.start()
        logger.info("Railway heartbeat started")
    
    def _check_and_reschedule_profiles(self):
        """Check for new or updated profiles and reschedule if needed. Also check for incorrect intervals."""
        try:
            # Get current jobs and their information
            current_jobs = {}
            job_intervals = {}
            
            for job in self.scheduler.get_jobs():
                if job.id.startswith("scrape_profile_"):
                    current_jobs[job.id] = job
                    
                    # Check if job has an interval trigger
                    if hasattr(job.trigger, 'interval'):
                        total_seconds = job.trigger.interval.total_seconds()
                        job_intervals[job.id] = total_seconds
            
            # Load current profiles
            db_path = os.getenv('DB_PATH', 'database.json')
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    db = json.load(f)
                
                profiles = db.get('profiles', {})
                expected_jobs = {f"scrape_profile_{pid}" for pid in profiles.keys()}
                
                # Remove jobs for deleted profiles
                for job_id in set(current_jobs.keys()) - expected_jobs:
                    if job_id.startswith("scrape_profile_"):
                        self.scheduler.remove_job(job_id)
                        logger.info(f"Removed job for deleted profile: {job_id}")
                
                # Add jobs for new profiles
                for profile_id in expected_jobs - set(current_jobs.keys()):
                    profile = profiles[profile_id.replace("scrape_profile_", "")]
                    self._schedule_profile_scrape(profile_id.replace("scrape_profile_", ""), profile)
                    logger.info(f"Added job for new profile: {profile_id}")
                
                # Check for jobs with incorrect intervals
                for job_id in set(current_jobs.keys()) & expected_jobs:
                    profile_id = job_id.replace("scrape_profile_", "")
                    profile = profiles.get(profile_id, {})
                    
                    # Calculate expected interval
                    hours = profile.get("scrape_interval_hours", 1)
                    mins = profile.get("scrape_interval_minutes", 0)
                    
                    # Railway safety check
                    if self.railway_mode:
                        total_mins = (hours * 60) + mins
                        if total_mins < 30:
                            hours = 0
                            mins = 30
                            
                    expected_seconds = (hours * 3600) + (mins * 60)
                    
                    # Give a buffer of 10 seconds for comparison
                    if job_id in job_intervals:
                        actual_seconds = job_intervals[job_id]
                        if abs(actual_seconds - expected_seconds) > 10:
                            logger.warning(f"Job {job_id} has incorrect interval: expected {expected_seconds}s, actual {actual_seconds}s. Rescheduling.")
                            self._schedule_profile_scrape(profile_id, profile)
                            
                        # Also check for extreme values (less than 60 seconds)
                        elif actual_seconds < 60:
                            logger.error(f"Job {job_id} has dangerous interval of {actual_seconds}s. Rescheduling with safe interval.")
                            self._schedule_profile_scrape(profile_id, profile)
                        
        except Exception as e:
            logger.error(f"Error checking profiles: {e}")
    
    def _load_and_schedule_profiles(self):
        """Load profiles from database and schedule scraping jobs."""
        try:
            db_path = os.getenv('DB_PATH', 'database.json')
            if not os.path.exists(db_path):
                logger.warning(f"Database file not found: {db_path}")
                return
            
            with open(db_path, 'r') as f:
                db = json.load(f)
            
            profiles = db.get('profiles', {})
            logger.info(f"Found {len(profiles)} profiles to schedule")
            
            for profile_id, profile in profiles.items():
                self._schedule_profile_scrape(profile_id, profile)
                
        except Exception as e:
            logger.error(f"Error loading profiles: {e}")
    
    def _schedule_profile_scrape(self, profile_id: str, profile: dict):
        """Schedule a scraping job for a profile."""
        try:
            interval_hours = profile.get('scrape_interval_hours', 4)
            
            # Create job ID
            job_id = f"scrape_profile_{profile_id}"
            
            # Remove existing job if it exists
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass
            
            # Get combined interval in minutes for Railway optimization
            combined_minutes = profile.get('scrape_interval_minutes', 0)
            combined_hours = profile.get('scrape_interval_hours', interval_hours)
            
            # For Railway, enforce minimum intervals to prevent resource exhaustion
            if self.railway_mode:
                # In Railway, enforce minimum interval of 30 minutes
                total_minutes = (combined_hours * 60) + combined_minutes
                
                # Safety check for extremely low values (like 1 second)
                if total_minutes < 1:
                    logger.error(f"Critical: Found invalid interval for profile {profile_id} (less than 1 minute). Setting to 30 minutes.")
                    combined_hours = 0
                    combined_minutes = 30
                elif total_minutes < 30:
                    logger.warning(f"Adjusting interval for profile {profile_id} from {total_minutes} to minimum 30 minutes in Railway environment")
                    combined_hours = 0
                    combined_minutes = 30
            
            # Validate interval values
            if combined_minutes < 0:
                logger.warning(f"Invalid negative minutes value: {combined_minutes} for profile {profile_id}. Setting to 0.")
                combined_minutes = 0
                
            if combined_hours < 0:
                logger.warning(f"Invalid negative hours value: {combined_hours} for profile {profile_id}. Setting to 1.")
                combined_hours = 1
                
            # Calculate total interval in minutes for logging
            total_minutes = (combined_hours * 60) + combined_minutes
            
            # Add staggered start delay to prevent all jobs starting at once
            import random
            start_delay_minutes = 2 + random.randint(0, 5)  # 2-7 minutes staggered delay
            next_run_time = datetime.now() + timedelta(minutes=start_delay_minutes)
            
            # Schedule new job with appropriate trigger
            self.scheduler.add_job(
                func=self._scrape_profile_wrapper,
                trigger=IntervalTrigger(hours=combined_hours, minutes=combined_minutes),
                id=job_id,
                args=[profile_id],
                name=f"Scrape {profile.get('name', 'Unknown')} ({profile_id})",
                max_instances=1,
                coalesce=True,
                next_run_time=next_run_time,
                misfire_grace_time=300  # Allow jobs to run up to 5 minutes late if needed
            )
            
            logger.info(f"Scheduled scraping for profile '{profile.get('name')}' every {total_minutes} minutes (h={combined_hours}, m={combined_minutes}) starting at {next_run_time.isoformat()}")
            
        except Exception as e:
            logger.error(f"Error scheduling profile {profile_id}: {e}")
    
    def _scrape_profile_wrapper(self, profile_id: str):
        """Wrapper for profile scraping with concurrency control and timeouts."""
        # Implement a timeout mechanism to prevent jobs from running too long
        import threading
        import ctypes
        
        def raise_exception_in_thread(thread, exception):
            """Force an exception in a thread"""
            if not thread.is_alive():
                return
                
            thread_id = thread.ident
            if not thread_id:
                return
                
            # Raise the exception in the thread
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(thread_id), 
                ctypes.py_object(exception)
            )
            
            if res == 0:
                raise ValueError("Invalid thread ID")
            elif res > 1:
                # If more than one thread affected, clear the exception
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(thread_id), None)
                raise SystemError("PyThreadState_SetAsyncExc failed")
        
        # Get a semaphore with timeout
        if not self.scrape_semaphore.acquire(timeout=120):  # 2 minute timeout for semaphore
            logger.error(f"Failed to acquire semaphore for profile {profile_id} - too many concurrent scrapes")
            return
        
        try:
            # Create a separate thread to run the scrape with timeout
            result = {"success": False, "error": None}
            
            def scrape_with_timeout():
                try:
                    self._scrape_profile(profile_id)
                    result["success"] = True
                except Exception as e:
                    result["error"] = str(e)
                    logger.error(f"Error scraping profile {profile_id}: {e}")
            
            # Start the thread
            scrape_thread = threading.Thread(target=scrape_with_timeout)
            scrape_thread.start()
            
            # Wait for completion with timeout (10 minutes)
            scrape_thread.join(timeout=600)
            
            # If thread is still running after timeout, force it to stop
            if scrape_thread.is_alive():
                logger.error(f"Scrape operation for profile {profile_id} timed out after 10 minutes. Forcing termination.")
                raise_exception_in_thread(scrape_thread, TimeoutError("Scrape operation timed out"))
                scrape_thread.join(timeout=30)  # Give it 30 more seconds to clean up
                
                # If still running, we'll have to let it go and hope it terminates eventually
                if scrape_thread.is_alive():
                    logger.error(f"Failed to terminate scrape thread for profile {profile_id}")
            
            # Check result
            if not result["success"] and result["error"]:
                logger.error(f"Scrape failed for profile {profile_id}: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error in scrape wrapper for profile {profile_id}: {e}")
        finally:
            # Always release the semaphore
            self.scrape_semaphore.release()
    
    def _scrape_profile(self, profile_id: str):
        """Scrape a single profile (Railway-optimized version)."""
        start_time = time.time()
        logger.info(f"Starting scrape for profile {profile_id}")
        
        try:
            # Load current database
            db_path = os.getenv('DB_PATH', 'database.json')
            with open(db_path, 'r') as f:
                db = json.load(f)
            
            profile = db.get('profiles', {}).get(profile_id)
            if not profile:
                logger.error(f"Profile {profile_id} not found")
                return
            
            # Build URL and scrape
            filters = profile.get('filters', {})
            url = build_rental_url(**filters)
            
            logger.info(f"Scraping URL: {url}")
            html_content = scrape_funda_html(url)
            
            if not html_content:
                logger.error(f"Failed to scrape HTML for profile {profile_id}")
                return
            
            # Extract listings
            raw_listings = extract_simple_listings_from_html(html_content)
            if not raw_listings:
                logger.warning(f"No listings found for profile {profile_id}")
                raw_listings = []
            
            # Map listings for frontend
            mapped_listings = [map_listing_for_frontend(listing) for listing in raw_listings]
            
            # Process new listings
            existing_listings = profile.get('listings', [])
            existing_urls = {listing.get('object_detail_page_relative_url') for listing in existing_listings}
            
            new_listings = []
            for listing in mapped_listings:
                if listing.get('object_detail_page_relative_url') not in existing_urls:
                    listing['is_new'] = True
                    listing['added_timestamp'] = time.time()
                    new_listings.append(listing)
                else:
                    # Update existing listing
                    for existing in existing_listings:
                        if existing.get('object_detail_page_relative_url') == listing.get('object_detail_page_relative_url'):
                            existing.update(listing)
                            existing['is_new'] = False
                            break
            
            # Update profile
            profile['listings'] = existing_listings + new_listings
            profile['last_scraped'] = now_cest_iso()
            profile['last_new_listings_count'] = len(new_listings)
            
            # Save database
            with open(db_path, 'w') as f:
                json.dump(db, f, indent=2)
            
            # Send email notifications
            if new_listings and profile.get('emails'):
                try:
                    send_new_listings_email(
                        profile.get('emails', []),
                        new_listings,
                        profile.get('name', 'Unknown Profile')
                    )
                    logger.info(f"Sent email notification for {len(new_listings)} new listings")
                except Exception as e:
                    logger.error(f"Failed to send email notification: {e}")
            
            # Log results
            duration = time.time() - start_time
            logger.info(f"Scrape completed for profile {profile_id}: {len(new_listings)} new listings in {duration:.2f}s")
            
            # Force garbage collection for memory management
            gc.collect()
            
        except Exception as e:
            logger.error(f"Error in scrape_profile for {profile_id}: {e}")
            raise
    
    def add_profile(self, profile_id: str, profile: dict):
        """Add or update a profile's scraping schedule."""
        if self.is_running:
            self._schedule_profile_scrape(profile_id, profile)
    
    def remove_profile(self, profile_id: str):
        """Remove a profile's scraping schedule."""
        if self.is_running:
            job_id = f"scrape_profile_{profile_id}"
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed scraping job for profile {profile_id}")
            except:
                pass
    
    def get_status(self):
        """Get scraper status for monitoring."""
        jobs = self.scheduler.get_jobs()
        return {
            'is_running': self.is_running,
            'railway_mode': self.railway_mode,
            'scheduled_jobs': len(jobs),
            'jobs': [
                {
                    'id': job.id,
                    'name': job.name,
                    'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
    
    def sanitize_db_intervals(self):
        """
        Scan database for invalid scrape intervals and correct them.
        This is important for Railway deployments to prevent excessive resource usage.
        """
        try:
            db_path = os.getenv('DB_PATH', 'database.json')
            if not os.path.exists(db_path):
                logger.warning(f"Database file not found: {db_path}")
                return
                
            with open(db_path, 'r') as f:
                db = json.load(f)
            
            profiles = db.get('profiles', {})
            db_updated = False
            
            for profile_id, profile in profiles.items():
                combined_hours = profile.get('scrape_interval_hours', 1)
                combined_minutes = profile.get('scrape_interval_minutes', 0)
                
                # Check for invalid values
                if combined_hours < 0 or combined_minutes < 0:
                    logger.warning(f"Found invalid negative interval in profile {profile_id}. Fixing...")
                    profile['scrape_interval_hours'] = max(0, combined_hours)
                    profile['scrape_interval_minutes'] = max(0, combined_minutes)
                    db_updated = True
                
                total_minutes = (combined_hours * 60) + combined_minutes
                if total_minutes < 1:
                    logger.warning(f"Found invalid interval (less than 1 minute) in profile {profile_id}. Setting to 30 minutes.")
                    profile['scrape_interval_hours'] = 0
                    profile['scrape_interval_minutes'] = 30
                    db_updated = True
                elif self.railway_mode and total_minutes < 30:
                    logger.warning(f"Found interval below Railway minimum (30 min) in profile {profile_id}. Adjusting...")
                    profile['scrape_interval_hours'] = 0
                    profile['scrape_interval_minutes'] = 30
                    db_updated = True
            
            if db_updated:
                logger.info("Saving sanitized intervals to database")
                with open(db_path, 'w') as f:
                    json.dump(db, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error sanitizing database intervals: {e}")
            raise

    def sync_jobs_with_profiles(self):
        """
        Synchronize scheduled jobs with current profiles in database.
        Also sanitizes intervals to prevent resource exhaustion.
        """
        if not self.is_running:
            logger.warning("Scheduler not running, can't sync jobs")
            return
            
        try:
            # First sanitize database intervals
            self.sanitize_db_intervals()
            
            # Remove all existing profile jobs
            for job in self.scheduler.get_jobs():
                if job.id.startswith("scrape_profile_"):
                    self.scheduler.remove_job(job.id)
            
            # Load all profiles and create new jobs
            self._load_and_schedule_profiles()
            
            logger.info("Successfully synchronized jobs with profiles")
            
        except Exception as e:
            logger.error(f"Error synchronizing jobs with profiles: {e}")

# Global instance
periodic_scraper = RailwayPeriodicScraper()

# Railway-specific startup
def ensure_scraper_running():
    """Ensure the scraper is running (Railway restart recovery)."""
    if not periodic_scraper.is_running:
        logger.info("Scraper not running, starting...")
        periodic_scraper.start()

# Auto-start on import in Railway environment
if is_running_on_railway():
    logger.info("Railway environment detected, auto-starting scraper")
    ensure_scraper_running()
