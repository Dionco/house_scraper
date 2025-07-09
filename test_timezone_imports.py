"""
Test script to verify timezone_utils import works properly in Railway environment.
"""
import os
import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("timezone_test")

def test_timezone_imports():
    """Test importing timezone_utils with different approaches."""
    
    logger.info("Starting timezone import tests")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Python path: {sys.path}")
    
    # Test 1: Direct import from the root module
    success1 = False
    try:
        import timezone_utils
        logger.info(f"✅ Direct import successful: {timezone_utils.__file__}")
        logger.info(f"   now_cest_iso() result: {timezone_utils.now_cest_iso()}")
        success1 = True
    except Exception as e:
        logger.error(f"❌ Direct import failed: {e}")
    
    # Test 2: Import from backend module
    success2 = False
    try:
        from backend import timezone_utils as backend_timezone
        logger.info(f"✅ Backend import successful: {backend_timezone.__file__}")
        logger.info(f"   now_cest_iso() result: {backend_timezone.now_cest_iso()}")
        success2 = True
    except Exception as e:
        logger.error(f"❌ Backend import failed: {e}")
    
    # Test 3: Import functions directly
    success3 = False
    try:
        try:
            from timezone_utils import now_cest_iso, now_cest
            source = "root module"
        except ImportError:
            from backend.timezone_utils import now_cest_iso, now_cest
            source = "backend module"
        
        logger.info(f"✅ Function import successful from {source}")
        logger.info(f"   now_cest_iso() result: {now_cest_iso()}")
        logger.info(f"   now_cest() result: {now_cest()}")
        success3 = True
    except Exception as e:
        logger.error(f"❌ Function import failed: {e}")
    
    # Test 4: Railway periodic scraper import
    success4 = False
    try:
        try:
            from railway_periodic_scraper import safe_iso_timestamp
        except ImportError:
            from backend.railway_periodic_scraper import safe_iso_timestamp
        
        logger.info(f"✅ Railway scraper safe_iso_timestamp import successful")
        logger.info(f"   safe_iso_timestamp() result: {safe_iso_timestamp()}")
        success4 = True
    except Exception as e:
        logger.error(f"❌ Railway scraper import failed: {e}")
        
    # Summary
    logger.info("\nTest Summary:")
    logger.info(f"Direct import: {'✅ Success' if success1 else '❌ Failed'}")
    logger.info(f"Backend import: {'✅ Success' if success2 else '❌ Failed'}")
    logger.info(f"Function import: {'✅ Success' if success3 else '❌ Failed'}")
    logger.info(f"Railway scraper import: {'✅ Success' if success4 else '❌ Failed'}")
    
    return any([success1, success2, success3, success4])

if __name__ == "__main__":
    if test_timezone_imports():
        print("\n✅ At least one timezone import method works successfully!")
        sys.exit(0)
    else:
        print("\n❌ All timezone import methods failed!")
        sys.exit(1)
