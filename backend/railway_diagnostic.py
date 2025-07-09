#!/usr/bin/env python3
"""
Railway diagnostic script to verify imports and environment
This script runs on startup in Railway to diagnose any issues
"""
import os
import sys
import logging
import json
import traceback
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("railway_diagnostic")

def is_railway():
    """Check if running on Railway"""
    return any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("PORT")  # Railway sets this automatically
    ])

def check_file_exists(filepath):
    """Check if a file exists and log the result"""
    exists = os.path.exists(filepath)
    logger.info(f"File {filepath}: {'✅ Exists' if exists else '❌ Missing'}")
    return exists

def check_module(module_name):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        logger.info(f"Module {module_name}: ✅ Importable")
        return True
    except ImportError as e:
        logger.error(f"Module {module_name}: ❌ Import Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Module {module_name}: ❌ Error: {e}")
        return False

def check_module_with_path(module_name, expected_path=None):
    """Check if a module can be imported and report its path"""
    try:
        module = importlib.import_module(module_name)
        file_path = getattr(module, "__file__", "unknown")
        if expected_path and file_path != expected_path:
            logger.warning(f"Module {module_name}: ✅ Imported but path differs")
            logger.warning(f"  Expected: {expected_path}")
            logger.warning(f"  Actual: {file_path}")
        else:
            logger.info(f"Module {module_name}: ✅ Imported from {file_path}")
        return True
    except ImportError as e:
        logger.error(f"Module {module_name}: ❌ Import Error: {e}")
        return False
    except Exception as e:
        logger.error(f"Module {module_name}: ❌ Error: {e}")
        return False

def run_diagnostics():
    """Run all diagnostic checks"""
    logger.info("=== 🔍 Starting Railway Diagnostics ===")
    
    # Environment information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Running on Railway: {is_railway()}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Check Python path
    logger.info(f"Python path: {sys.path}")
    
    # Check critical environment variables
    env_vars = ["RAILWAY_ENVIRONMENT", "RAILWAY_PROJECT_ID", "RAILWAY_SERVICE_ID", "PORT"]
    for var in env_vars:
        logger.info(f"Environment variable {var}: {'✅ Set' if os.getenv(var) else '❌ Not set'}")
    
    # Check for critical files
    critical_files = [
        "timezone_utils.py",
        "funda_url_builder.py",
        "scrape_funda.py",
        "extract_funda_listings.py",
        "listing_mapping.py",
        "email_utils.py",
        "api.py",
        "railway_periodic_scraper.py",
        "__init__.py"
    ]
    
    for file in critical_files:
        check_file_exists(file)
    
    # Check module imports
    modules_to_check = [
        "timezone_utils",
        "funda_url_builder",
        "scrape_funda",
        "extract_funda_listings", 
        "listing_mapping",
        "email_utils",
        "pytz",
        "undetected_chromedriver",
        "selenium"
    ]
    
    for module in modules_to_check:
        check_module_with_path(module)
    
    logger.info("=== 🏁 Railway Diagnostics Completed ===")

if __name__ == "__main__":
    try:
        run_diagnostics()
        logger.info("Diagnostics completed successfully")
    except Exception as e:
        logger.error(f"Diagnostics failed with error: {e}")
        traceback.print_exc()
        sys.exit(1)
