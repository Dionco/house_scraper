#!/usr/bin/env python3
"""
Comprehensive diagnostic script for Railway deployment.
Checks periodic scraping functionality, profile status, and system health.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Railway deployment URL
RAILWAY_URL = "https://house-scraper-production-7202.up.railway.app"

def check_railway_health():
    """Check if Railway app is running and responsive"""
    print("=== RAILWAY HEALTH CHECK ===")
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Railway app is running and responsive")
            return True
        else:
            print(f"❌ Railway app returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Railway app is not accessible: {e}")
        return False

def check_scraper_status():
    """Check the periodic scraper status"""
    print("\n=== SCRAPER STATUS CHECK ===")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/scraper/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Scraper is running: {status.get('is_running', False)}")
            print(f"📊 Total jobs: {status.get('total_jobs', 0)}")
            
            jobs = status.get('jobs', [])
            if jobs:
                print("\n📋 Active Jobs:")
                for job in jobs:
                    next_run = job.get('next_run')
                    if next_run:
                        try:
                            # Handle timezone-aware datetime
                            if next_run.endswith('Z'):
                                next_run = next_run[:-1] + '+00:00'
                            next_run_dt = datetime.fromisoformat(next_run)
                            # Convert to UTC for comparison
                            from datetime import timezone
                            now = datetime.now(timezone.utc)
                            if next_run_dt.tzinfo is None:
                                next_run_dt = next_run_dt.replace(tzinfo=timezone.utc)
                            time_until = next_run_dt - now
                            print(f"  - {job['name']}: Next run in {time_until}")
                        except Exception as e:
                            print(f"  - {job['name']}: Next run at {next_run}")
                    else:
                        print(f"  - {job['name']}: No next run scheduled")
            else:
                print("⚠️  No active jobs found")
            
            return status
        else:
            print(f"❌ Failed to get scraper status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error checking scraper status: {e}")
        return None

def check_profiles_status():
    """Check all profiles and their last scraped times"""
    print("\n=== PROFILES STATUS CHECK ===")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/profiles", timeout=10)
        if response.status_code == 200:
            profiles = response.json()
            print(f"📊 Total profiles: {len(profiles)}")
            
            never_scraped = []
            recently_scraped = []
            old_scraped = []
            
            now = datetime.now()
            
            for profile in profiles:
                name = profile.get('name', 'Unnamed')
                last_scraped = profile.get('last_scraped')
                
                if not last_scraped:
                    never_scraped.append(name)
                else:
                    try:
                        last_scraped_dt = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
                        time_since = now - last_scraped_dt
                        
                        if time_since < timedelta(hours=6):
                            recently_scraped.append((name, time_since))
                        else:
                            old_scraped.append((name, time_since))
                    except:
                        never_scraped.append(name)
            
            print(f"\n✅ Recently scraped ({len(recently_scraped)}):")
            for name, time_since in recently_scraped:
                print(f"  - {name}: {time_since.total_seconds()/3600:.1f} hours ago")
            
            print(f"\n⚠️  Old scraped ({len(old_scraped)}):")
            for name, time_since in old_scraped:
                print(f"  - {name}: {time_since.days} days, {time_since.seconds//3600} hours ago")
            
            print(f"\n❌ Never scraped ({len(never_scraped)}):")
            for name in never_scraped:
                print(f"  - {name}")
            
            return profiles
        else:
            print(f"❌ Failed to get profiles: {response.status_code}")
            if response.status_code == 401:
                print("⚠️  Authentication required - profiles endpoint requires login")
            return None
    except Exception as e:
        print(f"❌ Error checking profiles: {e}")
        return None

def sync_scraper_jobs():
    """Sync scraper jobs with profiles"""
    print("\n=== SYNCING SCRAPER JOBS ===")
    try:
        response = requests.post(f"{RAILWAY_URL}/api/scraper/sync", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Jobs synchronized')}")
            return True
        else:
            print(f"❌ Failed to sync jobs: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error syncing jobs: {e}")
        return False

def start_scraper_if_needed():
    """Start the scraper if it's not running"""
    print("\n=== STARTING SCRAPER IF NEEDED ===")
    try:
        response = requests.post(f"{RAILWAY_URL}/api/scraper/start", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Scraper started')}")
            return True
        else:
            print(f"❌ Failed to start scraper: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error starting scraper: {e}")
        return False

def test_manual_scrape():
    """Test manual scraping functionality"""
    print("\n=== TESTING MANUAL SCRAPE ===")
    print("Note: This requires authentication, so it may fail in automated test")
    try:
        # This will likely fail due to authentication requirements
        response = requests.post(f"{RAILWAY_URL}/api/scrape", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Manual scrape successful: {len(result.get('listings', []))} listings")
            return True
        else:
            print(f"⚠️  Manual scrape failed: {response.status_code}")
            if response.status_code == 401:
                print("   (Expected - authentication required)")
            return False
    except Exception as e:
        print(f"⚠️  Manual scrape error: {e}")
        return False

def check_database_directly():
    """Check database via API to see profile details"""
    print("\n=== DATABASE DIRECT CHECK ===")
    try:
        # Try to get listings to see if database is accessible
        response = requests.get(f"{RAILWAY_URL}/api/listings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            listings = data.get('listings', [])
            print(f"✅ Database accessible: {len(listings)} listings found")
            
            # Check for new listings
            new_listings = [l for l in listings if l.get('is_new', False)]
            print(f"📊 New listings: {len(new_listings)}")
            
            return True
        else:
            print(f"❌ Database access failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Database access error: {e}")
        return False

def main():
    """Run comprehensive Railway diagnostic"""
    print("🚂 RAILWAY PERIODIC SCRAPING DIAGNOSTIC")
    print("=" * 50)
    
    # Check basic health
    if not check_railway_health():
        print("\n❌ Railway app is not accessible. Cannot continue diagnostics.")
        return
    
    # Check scraper status
    scraper_status = check_scraper_status()
    
    # Check profiles (may require auth)
    profiles = check_profiles_status()
    
    # Sync jobs
    sync_scraper_jobs()
    
    # Start scraper if needed
    start_scraper_if_needed()
    
    # Test manual scrape
    test_manual_scrape()
    
    # Check database
    check_database_directly()
    
    # Final status check
    print("\n=== FINAL STATUS CHECK ===")
    final_status = check_scraper_status()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    
    if final_status:
        if final_status.get('is_running', False):
            print("✅ Periodic scraper is running")
            print(f"✅ {final_status.get('total_jobs', 0)} jobs are scheduled")
        else:
            print("❌ Periodic scraper is NOT running")
    else:
        print("❌ Could not determine scraper status")
    
    if profiles:
        never_scraped_count = sum(1 for p in profiles if not p.get('last_scraped'))
        if never_scraped_count > 0:
            print(f"⚠️  {never_scraped_count} profiles have never been scraped")
        else:
            print("✅ All profiles have been scraped at least once")
    
    print("\n🔍 RECOMMENDATIONS:")
    
    if scraper_status and not scraper_status.get('is_running', False):
        print("- Start the periodic scraper")
    
    if profiles:
        never_scraped_count = sum(1 for p in profiles if not p.get('last_scraped'))
        if never_scraped_count > 0:
            print(f"- Check why {never_scraped_count} profiles have never been scraped")
            print("- Consider manually triggering scrapes for these profiles")
    
    print("- Monitor Railway logs for any scraping errors")
    print("- Check Railway resource usage and limits")

if __name__ == "__main__":
    main()
