#!/usr/bin/env python3
"""
Railway import verifier for the import issues in railway_periodic_scraper.py
This script tests if the fix has resolved the import errors
"""
import os
import sys
import importlib
import traceback
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("import_verifier")

def is_railway():
    """Check if running on Railway"""
    return any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("PORT")  # Railway sets this automatically
    ])

def verify_imports():
    """Verify that the critical imports for railway_periodic_scraper work"""
    logger.info("Starting import verification")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running on Railway: {is_railway()}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Dictionary to track import results
    import_results = {}
    
    # Test timezone_utils imports
    try:
        from timezone_utils import now_cest_iso, now_cest, CEST
        logger.info("✅ Successfully imported from timezone_utils")
        import_results["timezone_utils"] = "SUCCESS"
        # Test the functions
        now_time = now_cest()
        now_iso = now_cest_iso()
        logger.info(f"Current time (CEST): {now_time}")
        logger.info(f"Current time (ISO): {now_iso}")
    except ImportError as e:
        logger.error(f"❌ Failed to import timezone_utils: {e}")
        import_results["timezone_utils"] = f"FAILED: {e}"
    except Exception as e:
        logger.error(f"❌ Error with timezone_utils: {e}")
        import_results["timezone_utils"] = f"ERROR: {e}"
        
    # Test email_utils import
    try:
        from email_utils import send_new_listings_email
        logger.info("✅ Successfully imported from email_utils")
        import_results["email_utils"] = "SUCCESS"
    except ImportError as e:
        logger.error(f"❌ Failed to import email_utils: {e}")
        import_results["email_utils"] = f"FAILED: {e}"
    except Exception as e:
        logger.error(f"❌ Error with email_utils: {e}")
        import_results["email_utils"] = f"ERROR: {e}"
        
    # Check if we can import railway_periodic_scraper itself
    try:
        import railway_periodic_scraper
        logger.info("✅ Successfully imported railway_periodic_scraper")
        import_results["railway_periodic_scraper"] = "SUCCESS"
    except ImportError as e:
        logger.error(f"❌ Failed to import railway_periodic_scraper: {e}")
        import_results["railway_periodic_scraper"] = f"FAILED: {e}"
    except Exception as e:
        logger.error(f"❌ Error with railway_periodic_scraper: {e}")
        import_results["railway_periodic_scraper"] = f"ERROR: {e}"
    
    # Summary
    logger.info("=== Import Verification Summary ===")
    for module, result in import_results.items():
        logger.info(f"{module}: {result}")
    
    # Return overall success/failure
    return all(result.startswith("SUCCESS") for result in import_results.values())

if __name__ == "__main__":
    try:
        success = verify_imports()
        if success:
            logger.info("✅ All imports verified successfully!")
            sys.exit(0)
        else:
            logger.error("❌ Some imports failed verification")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Verification script failed: {e}")
        traceback.print_exc()
        sys.exit(2)
