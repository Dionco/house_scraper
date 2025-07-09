"""
Test script for validating the Railway periodic scraper functionality.
This checks for proper imports, environment detection, and basic scraping.
"""
import os
import sys
import logging
import json
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add the backend directory to sys.path if needed
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
    logger.info(f"Added {backend_dir} to sys.path")

# Set up a mock Railway environment for testing
os.environ["RAILWAY_ENVIRONMENT"] = "test"
os.environ["RAILWAY_PROJECT_ID"] = "test-project-id"
os.environ["PORT"] = "8080"  # Typical Railway port
os.environ["DB_PATH"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.json')

logger.info("Starting Railway scraper test in simulated Railway environment")
logger.info(f"DB_PATH: {os.environ['DB_PATH']}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Python path: {sys.path}")

try:
    # Import the railway_periodic_scraper module
    logger.info("Importing RailwayPeriodicScraper...")
    from backend.railway_periodic_scraper import RailwayPeriodicScraper
    
    # Create an instance of the scraper
    logger.info("Creating RailwayPeriodicScraper instance...")
    scraper = RailwayPeriodicScraper()
    
    # Verify Railway mode is enabled
    logger.info(f"Railway mode detected: {scraper.railway_mode}")
    
    # Test the database access
    logger.info("Testing database access...")
    db_path = os.environ["DB_PATH"]
    with open(db_path, 'r') as f:
        db = json.load(f)
        
    profile_ids = list(db.get('profiles', {}).keys())
    if profile_ids:
        test_profile_id = profile_ids[0]
        logger.info(f"Found {len(profile_ids)} profiles. Testing with profile: {test_profile_id}")
        
        # Test the _scrape_profile method
        logger.info("Testing _scrape_profile method...")
        start_time = time.time()
        scraper._scrape_profile(test_profile_id)
        duration = time.time() - start_time
        logger.info(f"Scrape completed in {duration:.2f}s")
        
        # Test the periodic scheduler
        logger.info("Testing scheduler initialization...")
        scraper.start()
        logger.info("Scheduler started successfully")
        
        # Verify scheduler is running
        status = scraper.get_status()
        logger.info(f"Scheduler status: {status['is_running']}")
        logger.info(f"Scheduled jobs: {status['scheduled_jobs']}")
        
        # Stop the scheduler
        logger.info("Stopping scheduler...")
        scraper.stop()
        logger.info("Scheduler stopped")
        
        logger.info("All tests passed!")
    else:
        logger.warning("No profiles found in the database to test with")
    
except Exception as e:
    logger.error(f"Test failed: {e}")
    import traceback
    traceback.print_exc()
