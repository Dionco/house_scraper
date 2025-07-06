"""
Background scheduler service for periodic scraping of saved search profiles.
Uses APScheduler to run periodic tasks for each profile.
"""
import os
import json
import logging
import gc  # For memory management
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from timezone_utils import now_cest_iso, now_cest, CEST

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our existing scraping functions
from funda_url_builder import build_rental_url
from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html
from listing_mapping import map_listing_for_frontend
from email_utils import send_new_listings_email

class PeriodicScraper:
    def __init__(self, database_file: str = None):
        self.database_file = database_file or os.path.join(os.path.dirname(__file__), "../database.json")
        self.scheduler = BackgroundScheduler(timezone=CEST)
        self.scheduler.add_listener(self._job_listener, EVENT_JOB_ERROR | EVENT_JOB_EXECUTED)
        self.is_running = False
        
        # Configuration for scraping intervals
        self.default_interval_hours = 4  # Default scraping interval in hours
        self.max_listings_per_profile = 1000  # Limit to prevent database bloat
        
    def _job_listener(self, event):
        """Log job execution events"""
        if event.exception:
            logger.error(f"Job {event.job_id} crashed: {event.exception}")
        else:
            logger.info(f"Job {event.job_id} executed successfully")
    
    def load_database(self) -> Dict:
        """Load the database from JSON file"""
        try:
            if os.path.exists(self.database_file):
                with open(self.database_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return {}
    
    def save_database(self, db: Dict):
        """Save the database to JSON file"""
        try:
            with open(self.database_file, "w", encoding="utf-8") as f:
                json.dump(db, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def scrape_profile(self, profile_id: str):
        """
        Scrape a single profile and update the database with new listings.
        Send email notifications if new listings are found.
        """
        try:
            logger.info(f"Starting scrape for profile: {profile_id}")
            
            # Force garbage collection before scraping to free memory
            gc.collect()
            
            # Load current database
            db = self.load_database()
            
            # Get profiles from the nested structure
            profiles = db.get("profiles", {})
            if profile_id not in profiles:
                logger.warning(f"Profile {profile_id} not found in database")
                return
                
            profile = profiles[profile_id]
            filters = profile.get("filters", {})
            
            # Build URL and scrape
            try:
                # Clean filters to avoid unexpected parameters
                clean_filters = {}
                for key, value in filters.items():
                    if value is not None and value != "":
                        # Handle price parameter conversion
                        if key == "price" and isinstance(value, str):
                            # Convert price range like "3000-5000" to min_price and max_price
                            if "-" in value:
                                try:
                                    min_p, max_p = value.split("-", 1)
                                    clean_filters["min_price"] = int(min_p.strip())
                                    clean_filters["max_price"] = int(max_p.strip())
                                except ValueError:
                                    logger.warning(f"Invalid price format: {value}")
                            else:
                                try:
                                    # Single price value, use as max_price
                                    clean_filters["max_price"] = int(value.strip())
                                except ValueError:
                                    logger.warning(f"Invalid price value: {value}")
                        else:
                            clean_filters[key] = value
                        
                url = build_rental_url(**clean_filters)
                logger.info(f"Scraping URL: {url}")
            except Exception as url_error:
                logger.error(f"Failed to build URL for profile {profile_id}: {url_error}")
                profile["last_scraped"] = now_cest_iso()
                profile["last_new_listings_count"] = 0
                profile["last_scrape_error"] = f"URL building error: {url_error}"
                self.save_database(db)
                return
            
            # Try scraping with Railway-optimized settings
            html = None
            try:
                # Use shorter timeout and fewer retries for Railway
                html = scrape_funda_html(url, max_retries=1, timeout=30)  # Reduced further for Railway
                if html:
                    logger.info(f"Successfully scraped {len(html)} characters for profile {profile_id}")
                else:
                    logger.warning(f"Scraping returned empty HTML for profile {profile_id}")
            except Exception as scrape_error:
                logger.error(f"Failed to scrape HTML for profile {profile_id}: {scrape_error}")
                
                # Update profile with failed scrape info but don't crash
                profile["last_scraped"] = now_cest_iso()
                profile["last_new_listings_count"] = 0
                profile["last_scrape_error"] = str(scrape_error)
                self.save_database(db)
                return
                
            if not html:
                logger.error(f"No HTML content received for profile {profile_id}")
                
                # Update profile with empty result
                profile["last_scraped"] = now_cest_iso()
                profile["last_new_listings_count"] = 0
                profile["last_scrape_error"] = "No HTML content received"
                self.save_database(db)
                return
                
            # Extract listings
            try:
                listings = extract_simple_listings_from_html(html)
                logger.info(f"Extracted {len(listings)} listings for profile {profile_id}")
            except Exception as extract_error:
                logger.error(f"Failed to extract listings for profile {profile_id}: {extract_error}")
                
                # Update profile with extraction error
                profile["last_scraped"] = now_cest_iso()
                profile["last_new_listings_count"] = 0
                profile["last_scrape_error"] = f"Extraction error: {extract_error}"
                self.save_database(db)
                return
            
            # Clear any previous error
            if "last_scrape_error" in profile:
                del profile["last_scrape_error"]
            
            # Get existing URLs to avoid duplicates
            existing_urls = set()
            for listing in profile.get("listings", []):
                url = listing.get("funda_url") or listing.get("object_detail_page_relative_url")
                if url:
                    existing_urls.add(url)
            
            # Find new listings
            new_listings = []
            current_time = now_cest()
            
            for listing in listings:
                url = listing.get("funda_url") or listing.get("object_detail_page_relative_url")
                if url and url not in existing_urls:
                    mapped = map_listing_for_frontend(listing)
                    mapped["is_new"] = True
                    mapped["scraped_at"] = current_time.isoformat()
                    mapped["added_timestamp"] = current_time.timestamp()  # Add timestamp for easier comparison
                    new_listings.append(mapped)
                    existing_urls.add(url)
            
            if new_listings:
                logger.info(f"Found {len(new_listings)} new listings for profile {profile_id}")
                
                # Add new listings to profile
                current_listings = profile.get("listings", [])
                
                # Update existing listings - check if they're still "new" (less than 24 hours old)
                for listing in current_listings:
                    if not listing.get("added_timestamp"):
                        # Legacy listing without timestamp, add one based on scraped_at or current time
                        scraped_at = listing.get("scraped_at")
                        if scraped_at:
                            try:
                                dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                                listing["added_timestamp"] = dt.timestamp()
                            except:
                                listing["added_timestamp"] = current_time.timestamp()
                        else:
                            listing["added_timestamp"] = current_time.timestamp()
                            listing["scraped_at"] = current_time.isoformat()
                    
                    # Check if listing is still new (less than 24 hours old)
                    time_diff = current_time.timestamp() - listing.get("added_timestamp", 0)
                    listing["is_new"] = time_diff < 86400  # 24 hours = 86400 seconds
                
                # Add new listings at the beginning
                current_listings = new_listings + current_listings
                
                # Limit total listings to prevent database bloat
                if len(current_listings) > self.max_listings_per_profile:
                    current_listings = current_listings[:self.max_listings_per_profile]
                
                profile["listings"] = current_listings
                profile["last_scraped"] = now_cest_iso()
                profile["last_new_listings_count"] = len(new_listings)
                
                # Save database
                self.save_database(db)
                
                # Send email notification if emails are configured
                emails = profile.get("emails", [])
                if emails:
                    try:
                        send_new_listings_email(
                            emails, 
                            profile.get("name", profile_id), 
                            new_listings
                        )
                        logger.info(f"Sent email notification to {len(emails)} addresses for profile {profile_id}")
                    except Exception as e:
                        logger.error(f"Failed to send email notification for profile {profile_id}: {e}")
                
            else:
                logger.info(f"No new listings found for profile {profile_id}")
                
                # Update last scraped time even if no new listings
                profile["last_scraped"] = now_cest_iso()
                profile["last_new_listings_count"] = 0
                self.save_database(db)
                
        except Exception as e:
            logger.error(f"Error scraping profile {profile_id}: {e}")
        finally:
            # Clean up memory after scraping
            gc.collect()
            logger.info(f"Completed scrape for profile: {profile_id}")
    
    def add_profile_job(self, profile_id: str, interval_hours: int = None):
        """Add a periodic job for a profile"""
        if interval_hours is None:
            interval_hours = self.default_interval_hours
            
        job_id = f"scrape_profile_{profile_id}"
        
        # Remove existing job if it exists
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass
        
        # Add new job
        self.scheduler.add_job(
            func=self.scrape_profile,
            trigger=IntervalTrigger(hours=interval_hours),
            args=[profile_id],
            id=job_id,
            name=f"Scrape Profile {profile_id}",
            max_instances=1,  # Prevent overlapping jobs
            replace_existing=True
        )
        
        logger.info(f"Added periodic job for profile {profile_id} (every {interval_hours} hours)")
    
    def remove_profile_job(self, profile_id: str):
        """Remove a periodic job for a profile"""
        job_id = f"scrape_profile_{profile_id}"
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed periodic job for profile {profile_id}")
        except:
            logger.warning(f"Job {job_id} not found or already removed")
    
    def sync_jobs_with_profiles(self):
        """Synchronize scheduler jobs with current profiles in database"""
        try:
            db = self.load_database()
            
            # Get current profile IDs from the nested structure
            profiles = db.get("profiles", {})
            current_profile_ids = set(profiles.keys())
            
            # Get existing job IDs
            existing_job_ids = set()
            for job in self.scheduler.get_jobs():
                if job.id.startswith("scrape_profile_"):
                    profile_id = job.id.replace("scrape_profile_", "")
                    existing_job_ids.add(profile_id)
            
            # Add jobs for new profiles
            for profile_id in current_profile_ids:
                if profile_id not in existing_job_ids:
                    # Get profile-specific interval or use default
                    profile = profiles[profile_id]
                    interval = profile.get("scrape_interval_hours", self.default_interval_hours)
                    self.add_profile_job(profile_id, interval)
            
            # Remove jobs for deleted profiles
            for profile_id in existing_job_ids:
                if profile_id not in current_profile_ids:
                    self.remove_profile_job(profile_id)
                    
            logger.info(f"Synchronized jobs: {len(current_profile_ids)} profiles, {len(self.scheduler.get_jobs())} jobs")
            
        except Exception as e:
            logger.error(f"Error synchronizing jobs: {e}")
    
    def start(self):
        """Start the periodic scraper"""
        if not self.is_running:
            # Sync jobs with current profiles
            self.sync_jobs_with_profiles()
            
            # Add a recurring job to sync profiles every hour
            self.scheduler.add_job(
                func=self.sync_jobs_with_profiles,
                trigger=CronTrigger(minute=0),  # Run every hour at minute 0
                id="sync_profiles",
                name="Sync Profiles",
                replace_existing=True
            )
            
            # Start the scheduler
            self.scheduler.start()
            self.is_running = True
            logger.info("Periodic scraper started")
            
            # Log current jobs
            jobs = self.scheduler.get_jobs()
            logger.info(f"Active jobs: {len(jobs)}")
            for job in jobs:
                logger.info(f"  - {job.id}: {job.name}")
    
    def stop(self):
        """Stop the periodic scraper"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Periodic scraper stopped")
    
    def get_status(self) -> Dict:
        """Get current status of the periodic scraper"""
        jobs = self.scheduler.get_jobs() if self.is_running else []
        
        return {
            "is_running": self.is_running,
            "total_jobs": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in jobs
            ]
        }
    
    def trigger_profile_scrape(self, profile_id: str):
        """Manually trigger a scrape for a specific profile"""
        try:
            self.scrape_profile(profile_id)
            return {"success": True, "message": f"Scrape triggered for profile {profile_id}"}
        except Exception as e:
            logger.error(f"Error triggering scrape for profile {profile_id}: {e}")
            return {"success": False, "message": str(e)}

# Global instance
periodic_scraper = PeriodicScraper()
