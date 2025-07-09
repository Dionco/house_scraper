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
        """Check for new or updated profiles and reschedule if needed."""
        try:
            current_jobs = {job.id for job in self.scheduler.get_jobs()}
            
            # Load current profiles
            db_path = os.getenv('DB_PATH', 'database.json')
            if os.path.exists(db_path):
                with open(db_path, 'r') as f:
                    db = json.load(f)
                
                profiles = db.get('profiles', {})
                expected_jobs = {f"scrape_profile_{pid}" for pid in profiles.keys()}
                
                # Remove jobs for deleted profiles
                for job_id in current_jobs - expected_jobs:
                    if job_id.startswith("scrape_profile_"):
                        self.scheduler.remove_job(job_id)
                        logger.info(f"Removed job for deleted profile: {job_id}")
                
                # Add jobs for new profiles
                for profile_id in expected_jobs - current_jobs:
                    profile = profiles[profile_id.replace("scrape_profile_", "")]
                    self._schedule_profile_scrape(profile_id.replace("scrape_profile_", ""), profile)
                    logger.info(f"Added job for new profile: {profile_id}")
                        
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
            
            # Schedule new job
            self.scheduler.add_job(
                func=self._scrape_profile_wrapper,
                trigger=IntervalTrigger(hours=interval_hours),
                id=job_id,
                args=[profile_id],
                name=f"Scrape {profile.get('name', 'Unknown')} ({profile_id})",
                max_instances=1,
                coalesce=True,
                next_run_time=datetime.now() + timedelta(minutes=1)  # Start after 1 minute
            )
            
            logger.info(f"Scheduled scraping for profile '{profile.get('name')}' every {interval_hours} hours")
            
        except Exception as e:
            logger.error(f"Error scheduling profile {profile_id}: {e}")
    
    def _scrape_profile_wrapper(self, profile_id: str):
        """Wrapper for profile scraping with concurrency control."""
        with self.scrape_semaphore:
            try:
                self._scrape_profile(profile_id)
            except Exception as e:
                logger.error(f"Error scraping profile {profile_id}: {e}")
                # Don't raise - we want the job to continue being scheduled
    
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
            url = build_rental_url(filters)
            
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
