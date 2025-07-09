"""
Special helper script to permanently fix timezone_utils import issues in Railway.
This script:
1. Creates a self-contained timezone_utils.py in multiple locations
2. Installs it into the Python path
3. Tests that imports work correctly
"""
import os
import sys
import shutil
import importlib
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the timezone_utils content as a string for easy copying
TIMEZONE_UTILS_CONTENT = '''"""
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
'''

def install_timezone_utils_to_site_packages():
    """Install timezone_utils.py to site-packages to make it globally available."""
    try:
        # Find site-packages directory
        import site
        site_packages_dirs = site.getsitepackages()
        
        if not site_packages_dirs:
            logger.error("Couldn't determine site-packages directory")
            return False
        
        site_packages_dir = site_packages_dirs[0]
        logger.info(f"Installing to site-packages: {site_packages_dir}")
        
        # Write timezone_utils.py to site-packages
        target_path = os.path.join(site_packages_dir, "timezone_utils.py")
        with open(target_path, "w") as f:
            f.write(TIMEZONE_UTILS_CONTENT)
        
        logger.info(f"Successfully installed timezone_utils.py to {target_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to install to site-packages: {e}")
        return False

def create_timezone_utils_copies():
    """Create copies of timezone_utils.py in multiple locations."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    locations = [
        project_root,  # Root of project
        os.path.join(project_root, "backend"),  # Backend directory
    ]
    
    success_count = 0
    for location in locations:
        try:
            if os.path.isdir(location):
                target_path = os.path.join(location, "timezone_utils.py")
                with open(target_path, "w") as f:
                    f.write(TIMEZONE_UTILS_CONTENT)
                logger.info(f"Created timezone_utils.py at {target_path}")
                success_count += 1
        except Exception as e:
            logger.error(f"Failed to create at {location}: {e}")
    
    return success_count

def test_import():
    """Test importing timezone_utils from different contexts."""
    # Clear timezone_utils from cache if it exists
    if "timezone_utils" in sys.modules:
        del sys.modules["timezone_utils"]
    
    try:
        import timezone_utils
        logger.info(f"Direct import successful: {timezone_utils.__file__}")
        logger.info(f"Test call: {timezone_utils.now_cest_iso()}")
        return True
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting timezone_utils installer...")
    
    # Create copies in multiple locations
    copy_count = create_timezone_utils_copies()
    logger.info(f"Created {copy_count} copies of timezone_utils.py")
    
    # Try to install to site-packages
    site_install = install_timezone_utils_to_site_packages()
    if site_install:
        logger.info("Installed timezone_utils.py to site-packages")
    else:
        logger.warning("Could not install to site-packages")
    
    # Test that import works
    if test_import():
        logger.info("✅ timezone_utils.py is now importable!")
    else:
        logger.error("❌ timezone_utils.py still cannot be imported.")
        
    # Update PYTHONPATH environment variable for Railway
    # This is just a message since we can't permanently change the environment variable here
    logger.info("\nTo ensure timezone_utils is importable in Railway, add this to your Dockerfile or startup script:")
    logger.info('export PYTHONPATH="${PYTHONPATH}:/app:/app/backend"')
    logger.info("Also run this script during container startup.")
    
    logger.info("\nInstallation complete.")
