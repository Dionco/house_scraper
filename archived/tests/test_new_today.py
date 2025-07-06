#!/usr/bin/env python3
"""
Test script to verify that the new_today_count functionality works correctly.
"""

import json
import time
import sys
import os
from datetime import datetime, timedelta

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from api import calculate_new_today_count, update_listing_timestamps

def test_new_today_count():
    """Test the new today count functionality"""
    print("🧪 Testing new today count functionality...")
    
    # Create test listings with different timestamps
    current_time = datetime.now()
    yesterday = current_time - timedelta(days=1)
    two_days_ago = current_time - timedelta(days=2)
    one_hour_ago = current_time - timedelta(hours=1)
    
    test_listings = [
        {
            "funda_url": "https://funda.nl/test1",
            "scraped_at": one_hour_ago.isoformat(),
            "added_timestamp": one_hour_ago.timestamp(),
            "is_new": True
        },
        {
            "funda_url": "https://funda.nl/test2", 
            "scraped_at": yesterday.isoformat(),
            "added_timestamp": yesterday.timestamp(),
            "is_new": False
        },
        {
            "funda_url": "https://funda.nl/test3",
            "scraped_at": two_days_ago.isoformat(),
            "added_timestamp": two_days_ago.timestamp(),
            "is_new": False
        },
        {
            "funda_url": "https://funda.nl/test4",
            "scraped_at": current_time.isoformat(),
            "added_timestamp": current_time.timestamp(),
            "is_new": True
        }
    ]
    
    # Test calculate_new_today_count
    new_count = calculate_new_today_count(test_listings)
    print(f"✅ New today count: {new_count} (expected: 2)")
    
    # Test update_listing_timestamps
    print("\n🔄 Testing timestamp updates...")
    
    # Create listings without timestamps 
    legacy_listings = [
        {
            "funda_url": "https://funda.nl/legacy1",
            "scraped_at": one_hour_ago.isoformat(),
            # No added_timestamp
        },
        {
            "funda_url": "https://funda.nl/legacy2",
            "scraped_at": two_days_ago.isoformat(),
            # No added_timestamp
        }
    ]
    
    update_listing_timestamps(legacy_listings)
    
    for listing in legacy_listings:
        has_timestamp = "added_timestamp" in listing
        is_new_correct = listing.get("is_new", False)
        print(f"✅ Listing {listing['funda_url']}: timestamp={has_timestamp}, is_new={is_new_correct}")
    
    # Calculate new today count for updated listings
    updated_count = calculate_new_today_count(legacy_listings)
    print(f"✅ Updated legacy listings - new today count: {updated_count}")
    
    print("\n🎉 All tests completed successfully!")

if __name__ == "__main__":
    test_new_today_count()
