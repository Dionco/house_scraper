"""
Timezone utilities for the House Scraper application.
Provides Central European Summer Time (CEST) timezone handling.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

# Define CEST timezone (UTC+2)
CEST = timezone(timedelta(hours=2))

def now_cest() -> datetime:
    """Get current time in CEST timezone"""
    return datetime.now(CEST)

def now_cest_iso() -> str:
    """Get current time in CEST timezone as ISO string"""
    return now_cest().isoformat()

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
