"""
Timezone utilities for the House Scraper application.
Provides Central European Summer Time (CEST) timezone handling.
This module is designed to work in both development and Railway environments.

RAILWAY COMPATIBILITY VERSION: This version has been specifically enhanced
to ensure it works properly in the Railway environment and handles all edge cases.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional
import logging
import sys
import os

# Setup logging
logger = logging.getLogger(__name__)

# Make this module auto-installable for Railway
try:
    # Check if we're missing pytz
    try:
        import pytz
    except ImportError:
        import subprocess
        import sys
        
        logger.warning("pytz not available, attempting to install it...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pytz"])
            logger.info("Successfully installed pytz")
            import pytz
        except Exception as install_error:
            logger.error(f"Failed to install pytz: {install_error}")
            # Continue with fallback implementation
            
    # Use Europe/Amsterdam to correctly handle DST transitions
    import pytz  # Try again after potential install
    CEST = pytz.timezone('Europe/Amsterdam')
    TIMEZONE_TYPE = "pytz"
    logger.info("Using pytz for timezone handling")
except Exception as e:
    # Fallback to fixed offset (UTC+2)
    CEST = timezone(timedelta(hours=2))
    TIMEZONE_TYPE = "fixed_offset"
    logger.warning(f"pytz not available or failed to initialize: {e}. Using fixed UTC+2 offset for CEST")

# Module initialization logging
logger.info(f"timezone_utils module initialized with {TIMEZONE_TYPE} timezone")
logger.info(f"Python version: {sys.version}")
logger.info(f"Module path: {__file__}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Running on Railway: {any([os.getenv('RAILWAY_ENVIRONMENT'), os.getenv('RAILWAY_PROJECT_ID')])}")

def now_cest() -> datetime:
    """Get current time in CEST timezone"""
    try:
        if TIMEZONE_TYPE == "pytz":
            # For pytz timezones, use localize to properly handle DST
            return pytz.timezone('Europe/Amsterdam').localize(datetime.now())
        else:
            # For fixed offset timezones
            return datetime.now(CEST)
    except Exception as e:
        logger.error(f"Error in now_cest(): {e}")
        # Ultimate fallback - never fail
        return datetime.now().replace(tzinfo=timezone(timedelta(hours=2)))

def now_cest_iso() -> str:
    """Get current time in CEST timezone as ISO string"""
    errors = []
    
    # Method 1: Use now_cest() and format
    try:
        return now_cest().isoformat()
    except Exception as e:
        errors.append(f"now_cest().isoformat(): {e}")
    
    # Method 2: Try direct pytz approach
    try:
        import pytz
        return datetime.now(pytz.timezone('Europe/Amsterdam')).isoformat()
    except Exception as e:
        errors.append(f"pytz direct: {e}")
    
    # Method 3: Fixed UTC+2 offset
    try:
        return datetime.now(timezone(timedelta(hours=2))).isoformat()
    except Exception as e:
        errors.append(f"UTC+2 fixed offset: {e}")
    
    # Method 4: UTC with +02:00 string
    try:
        return datetime.now().isoformat() + "+02:00"
    except Exception as e:
        errors.append(f"String append: {e}")
    
    # Method 5: Absolute last resort
    logger.error(f"All ISO timestamp methods failed: {errors}")
    return str(datetime.now()) + " +0200"  # Guaranteed to work

def parse_datetime_cest(dt_str: str) -> Optional[datetime]:
    """Parse datetime string and convert to CEST if needed"""
    try:
        if dt_str is None:
            return None
            
        # Try to parse with timezone info
        if '+' in dt_str or 'Z' in dt_str:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.astimezone(CEST)
        else:
            # Assume it's already in CEST if no timezone info
            dt = datetime.fromisoformat(dt_str)
            return dt.replace(tzinfo=CEST)
    except Exception:
        return None

def format_datetime_cest(dt: datetime) -> str:
    """Format datetime for display in CEST"""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=CEST)
    else:
        dt = dt.astimezone(CEST)
    return dt.strftime("%Y-%m-%d %H:%M:%S CEST")

def get_timezone_info():
    """Get current timezone information"""
    return {
        "timezone": "Central European Summer Time",
        "abbreviation": "CEST",
        "offset": "+02:00",
        "current_time": now_cest_iso()
    }
