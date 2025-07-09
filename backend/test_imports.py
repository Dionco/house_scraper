#!/usr/bin/env python3
"""
Test script to verify that all required imports are working correctly.
This is useful for diagnosing import issues in different environments.
"""
import logging
import sys
import os
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_import(module_name, function_name=None):
    """Test importing a module and optionally a function from it"""
    try:
        if '.' in module_name:
            # Try relative import first
            try:
                exec(f"from .{module_name} import {function_name if function_name else '*'}")
                logger.info(f"✅ Successfully imported {function_name if function_name else module_name} with relative import")
                return True
            except ImportError as e:
                logger.info(f"❌ Relative import failed for {module_name}: {e}")
                # Now try direct import
                try:
                    if function_name:
                        exec(f"from {module_name} import {function_name}")
                    else:
                        exec(f"import {module_name}")
                    logger.info(f"✅ Successfully imported {function_name if function_name else module_name} with direct import")
                    return True
                except ImportError as e:
                    logger.error(f"❌ Failed to import {module_name}: {e}")
                    return False
        else:
            # Direct import
            try:
                if function_name:
                    exec(f"from {module_name} import {function_name}")
                else:
                    exec(f"import {module_name}")
                logger.info(f"✅ Successfully imported {function_name if function_name else module_name}")
                return True
            except ImportError as e:
                logger.error(f"❌ Failed to import {module_name}: {e}")
                return False
    except Exception as e:
        logger.error(f"❌ Error testing import {module_name}: {e}")
        return False

def is_running_on_railway():
    """Check if the application is running on Railway."""
    import os
    return any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("PORT")  # Railway sets this automatically
    ])

def test_all_imports():
    """Test all imports needed for the application"""
    results = {
        "success": 0,
        "fail": 0,
        "total": 0
    }
    
    # Log environment info
    logger.info(f"Running on Railway: {is_running_on_railway()}")
    
    # List of modules to test
    imports_to_test = [
        ("timezone_utils", "now_cest_iso"),
        ("timezone_utils", "now_cest"),
        ("funda_url_builder", "build_rental_url"),
        ("scrape_funda", "scrape_funda_html"),
        ("extract_funda_listings", "extract_simple_listings_from_html"),
        ("listing_mapping", "map_listing_for_frontend"),
        ("email_utils", "send_new_listings_email"),
        ("pytz", None),
        ("undetected_chromedriver", None),
        ("selenium", None),
    ]
    
    for module, function in imports_to_test:
        results["total"] += 1
        if test_import(module, function):
            results["success"] += 1
        else:
            results["fail"] += 1
    
    # Check for Python path issues
    logger.info(f"Python path: {sys.path}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Summary
    logger.info(f"Import test summary: {results['success']} succeeded, {results['fail']} failed out of {results['total']} total")
    
    return results

if __name__ == "__main__":
    logger.info("Starting import tests")
    try:
        results = test_all_imports()
        if results["fail"] > 0:
            sys.exit(1)
        else:
            logger.info("All imports succeeded!")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)
