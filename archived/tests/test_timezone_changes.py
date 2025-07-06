#!/usr/bin/env python3
"""
Test script to verify that timezone changes work correctly in both local and Railway environments.
"""

import requests
import json
from datetime import datetime

def test_timezone_endpoints():
    """Test both local and Railway endpoints for timezone compliance"""
    
    print("=== TIMEZONE VERIFICATION TEST ===")
    
    # Test local endpoint (if running)
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n✅ LOCAL ENDPOINT:")
            print(f"  Timestamp: {data.get('timestamp')}")
            print(f"  Timezone: {data.get('timezone', {}).get('timezone')}")
            print(f"  Offset: {data.get('timezone', {}).get('offset')}")
        else:
            print("\n❌ LOCAL ENDPOINT: Not responding")
    except requests.RequestException:
        print("\n❌ LOCAL ENDPOINT: Not running")
    
    # Test Railway endpoint
    try:
        response = requests.get("https://house-scraper-production-7202.up.railway.app/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\n✅ RAILWAY ENDPOINT:")
            print(f"  Timestamp: {data.get('timestamp')}")
            print(f"  Timezone: {data.get('timezone', {}).get('timezone')}")
            print(f"  Offset: {data.get('timezone', {}).get('offset')}")
            
            # Check if timestamp has proper CEST offset
            timestamp = data.get('timestamp', '')
            if '+02:00' in timestamp:
                print("  ✅ CEST offset detected in timestamp!")
            else:
                print("  ❌ CEST offset not detected in timestamp")
        else:
            print(f"\n❌ RAILWAY ENDPOINT: HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"\n❌ RAILWAY ENDPOINT: Error - {e}")
    
    # Test admin stats for proper timezone handling
    try:
        response = requests.get("https://house-scraper-production-7202.up.railway.app/api/admin/stats", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("\n✅ RAILWAY ADMIN STATS:")
            print(f"  Latest scrape: {data.get('latest_scrape')}")
            print(f"  Total listings: {data.get('total_listings')}")
            print(f"  New listings: {data.get('new_listings')}")
        else:
            print(f"\n❌ RAILWAY ADMIN STATS: HTTP {response.status_code}")
    except requests.RequestException as e:
        print(f"\n❌ RAILWAY ADMIN STATS: Error - {e}")
    
    print("\n=== TIMEZONE TEST COMPLETED ===")

if __name__ == "__main__":
    test_timezone_endpoints()
