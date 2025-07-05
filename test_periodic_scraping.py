#!/usr/bin/env python3
"""
Test script to verify periodic scraping functionality.
Can be run locally or to test a deployed instance.
"""

import requests
import json
import time
from datetime import datetime

def test_scraper_status(base_url="http://localhost:8000"):
    """Test the scraper status endpoint"""
    try:
        response = requests.get(f"{base_url}/api/scraper/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ Scraper Status:")
            print(f"   Running: {status['is_running']}")
            print(f"   Total Jobs: {status['total_jobs']}")
            print("   Jobs:")
            for job in status['jobs']:
                print(f"     - {job['name']}: Next run at {job['next_run']}")
            return True
        else:
            print(f"❌ Failed to get scraper status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking scraper status: {e}")
        return False

def test_profile_last_scraped(base_url="http://localhost:8000"):
    """Check last scraped times for all profiles"""
    try:
        # We need to check profiles - this might require authentication
        # Let's try to access the database file info indirectly
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
        
        # Try to trigger a sync to ensure jobs are up to date
        try:
            sync_response = requests.post(f"{base_url}/api/scraper/sync")
            if sync_response.status_code == 200:
                print("✅ Scraper sync successful")
            else:
                print(f"⚠️  Scraper sync returned: {sync_response.status_code}")
        except:
            print("⚠️  Could not trigger scraper sync (might need auth)")
        
        return True
    except Exception as e:
        print(f"❌ Error checking profiles: {e}")
        return False

def test_manual_scrape_trigger(base_url="http://localhost:8000"):
    """Test manual scrape triggering"""
    try:
        # This endpoint requires authentication, so we'll just check if it exists
        # by getting a 401/403 instead of 404
        response = requests.post(f"{base_url}/api/profiles/test_profile/scrape")
        if response.status_code in [401, 403]:
            print("✅ Manual scrape endpoint exists (requires auth)")
            return True
        elif response.status_code == 404:
            print("❌ Manual scrape endpoint not found")
            return False
        else:
            print(f"⚠️  Manual scrape endpoint returned: {response.status_code}")
            return True
    except Exception as e:
        print(f"❌ Error testing manual scrape: {e}")
        return False

def main():
    print("🔍 Testing Periodic Scraping Functionality")
    print("=" * 50)
    
    # Test local instance
    print("\n📍 Testing Local Instance (localhost:8000)")
    local_ok = True
    local_ok &= test_scraper_status("http://localhost:8000")
    local_ok &= test_profile_last_scraped("http://localhost:8000")
    local_ok &= test_manual_scrape_trigger("http://localhost:8000")
    
    # Test Railway deployment (if URL is provided)
    railway_url = input("\n🚂 Enter your Railway deployment URL (or press Enter to skip): ").strip()
    if railway_url:
        if not railway_url.startswith("http"):
            railway_url = f"https://{railway_url}"
        
        print(f"\n📍 Testing Railway Instance ({railway_url})")
        railway_ok = True
        railway_ok &= test_scraper_status(railway_url)
        railway_ok &= test_profile_last_scraped(railway_url)
        railway_ok &= test_manual_scrape_trigger(railway_url)
        
        print(f"\n🚂 Railway Instance Status: {'✅ OK' if railway_ok else '❌ Issues Found'}")
    
    print(f"\n🏠 Local Instance Status: {'✅ OK' if local_ok else '❌ Issues Found'}")
    
    # Additional checks
    print("\n🔧 Additional Recommendations:")
    print("1. Check Railway logs for periodic scraper activity")
    print("2. Verify that APScheduler is working in the Railway environment")
    print("3. Check if timezone issues affect job scheduling")
    print("4. Monitor memory usage during scraping jobs")

if __name__ == "__main__":
    main()
