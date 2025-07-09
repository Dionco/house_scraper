"""
Timezone utilities for the House Scraper application.
This is a copy of the module placed at the root level for easier imports in Railway.
"""
# Import from the actual module to maintain a single source of truth
try:
    from backend.timezone_utils import *
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Root-level timezone_utils successfully imported from backend.timezone_utils")
except ImportError as e:
    # If the backend version can't be imported, create a standalone implementation
    import logging
    from datetime import datetime, timezone, timedelta
    import sys
    import os
    
    logger = logging.getLogger(__name__)
    logger.warning(f"Failed to import from backend.timezone_utils: {e}, creating standalone implementation")

    # Try to use pytz if available
    try:
        import pytz
        CEST = pytz.timezone('Europe/Amsterdam')
        TIMEZONE_TYPE = "pytz"
        logger.info("Using pytz for timezone handling")
    except ImportError:
        # Fallback to fixed offset (UTC+2)
        CEST = timezone(timedelta(hours=2))
        TIMEZONE_TYPE = "fixed_offset"
        logger.warning("pytz not available, using fixed UTC+2 offset for CEST")

    def now_cest():
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

    def now_cest_iso():
        """Get current time in CEST timezone as ISO string"""
        try:
            return now_cest().isoformat()
        except Exception as e:
            logger.error(f"Error in now_cest_iso(): {e}")
            # Ultimate fallback - never fail
            return datetime.now().isoformat() + "+02:00"
            
    def convert_to_cest(dt):
        """Convert a datetime to CEST timezone"""
        if dt is None:
            return None
            
        try:
            if dt.tzinfo is None:
                # Assume UTC if no timezone specified
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(CEST)
        except Exception as e:
            logger.error(f"Error converting to CEST: {e}")
            # Fallback to adding 2 hours (rough approximation of CEST)
            return dt + timedelta(hours=2)
