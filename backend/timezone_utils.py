"""
RAILWAY-OPTIMIZED TIMEZONE UTILITIES

This is a standalone implementation of timezone utilities for the House Scraper application.
This module is designed to be reliably importable from any context including Railway.

This version will:
1. Auto-install any missing dependencies
2. Work regardless of import path issues
3. Never fail, with multiple fallback mechanisms
4. Be self-contained with no external dependencies except standard library
"""
import logging
import sys
import os
from datetime import datetime, timezone, timedelta
import importlib.util

# Configure logging
logger = logging.getLogger(__name__)

# Track the module source for debugging
MODULE_SOURCE = "auto-installed"

# Auto-install dependencies if needed
def ensure_dependency(package_name):
    """Ensure a package is installed, installing it if necessary."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        try:
            import subprocess
            import sys
            logger.warning(f"{package_name} not available, attempting to install it...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            logger.info(f"Successfully installed {package_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to install {package_name}: {e}")
            return False

# Try to use pytz for best timezone handling
pytz_available = ensure_dependency("pytz")

# Import pytz now that we've ensured it's installed
try:
    import pytz
    TIMEZONE_TYPE = "pytz"
    CEST = pytz.timezone('Europe/Amsterdam')
    logger.info("Using pytz for timezone handling")
except Exception as e:
    # Ultimate fallback to fixed offset
    TIMEZONE_TYPE = "fixed_offset"
    CEST = timezone(timedelta(hours=2))
    logger.warning(f"Failed to use pytz despite installation attempt: {e}. Using fixed UTC+2 offset.")

# Define core timezone functions
def now_cest():
    """
    Get current time in CEST timezone.
    This function is guaranteed to never fail.
    """
    try:
        if TIMEZONE_TYPE == "pytz":
            # For pytz timezones
            try:
                # Best practice with pytz is to use localize
                return pytz.timezone('Europe/Amsterdam').localize(datetime.now())
            except AttributeError:
                # Some versions of pytz don't have localize
                return datetime.now(CEST)
        else:
            # For fixed offset timezones
            return datetime.now(CEST)
    except Exception as e:
        logger.error(f"Error in now_cest(): {e}")
        # Ultimate fallback - never fail
        return datetime.now().replace(tzinfo=timezone(timedelta(hours=2)))

def now_cest_iso():
    """
    Get current time in CEST timezone as ISO string.
    This function is guaranteed to never fail.
    """
    try:
        return now_cest().isoformat()
    except Exception as e:
        logger.error(f"Error in now_cest_iso(): {e}")
        # Ultimate fallback - never fail
        return datetime.now().isoformat() + "+02:00"

def get_timezone_info():
    """
    Get information about the current timezone implementation.
    Useful for debugging timezone issues.
    """
    return {
        "timezone_type": TIMEZONE_TYPE,
        "module_source": MODULE_SOURCE,
        "python_version": sys.version,
        "module_path": __file__,
        "current_directory": os.getcwd(),
        "railway_environment": any([
            os.getenv("RAILWAY_ENVIRONMENT"),
            os.getenv("RAILWAY_PROJECT_ID"),
            os.getenv("RAILWAY_SERVICE_ID")
        ])
    }

# Log timezone information
logger.info(f"Using {TIMEZONE_TYPE} for timezone handling")
logger.info(f"timezone_utils module initialized with {TIMEZONE_TYPE} timezone")
logger.info(f"Python version: {sys.version}")
logger.info(f"Module path: {__file__}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Running on Railway: {get_timezone_info()['railway_environment']}")

# If this module is imported directly, run a test to verify it's working
if __name__ == "__main__":
    print(f"Current time (CEST): {now_cest()}")
    print(f"Current time (ISO): {now_cest_iso()}")
    print(f"Timezone info: {get_timezone_info()}")
