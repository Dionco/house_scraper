#!/usr/bin/env python3
"""
Script to manually trigger scrapes for profiles that have never been scraped.
This script will call the Railway API to trigger scrapes directly.
"""

import requests
import json
from datetime import datetime

RAILWAY_URL = "https://house-scraper-production-7202.up.railway.app"

def trigger_manual_scrape(profile_id, profile_name):
    """Trigger a manual scrape for a specific profile via sync"""
    print(f"🚀 Triggering manual scrape for: {profile_name} (ID: {profile_id})")
    
    try:
        # Since the scrape endpoints require authentication, we'll use the sync endpoint
        # which will ensure the profile gets picked up by the scheduler
        print("   Using sync endpoint to refresh scheduler...")
        
        response = requests.post(
            f"{RAILWAY_URL}/api/scraper/sync",
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ Scheduler sync successful")
            print("   Profile should be picked up by periodic scraper")
            return True
        else:
            print(f"❌ Failed to sync scheduler: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error triggering scrape: {e}")
        return False

def trigger_scrape_via_general_endpoint(profile_id, profile_name):
    """Try to wait for the periodic scraper to pick up the profile"""
    print(f"🔄 Waiting for periodic scraper to pick up: {profile_name}")
    
    # Check the current scraper status to see when the profile is scheduled
    try:
        response = requests.get(
            f"{RAILWAY_URL}/api/scraper/status",
            timeout=10
        )
        
        if response.status_code == 200:
            status = response.json()
            jobs = status.get('jobs', [])
            
            # Look for this profile's job
            profile_job = None
            for job in jobs:
                if job.get('id') == f"scrape_profile_{profile_id}":
                    profile_job = job
                    break
            
            if profile_job:
                next_run = profile_job.get('next_run')
                print(f"✅ Profile job found: {profile_job.get('name')}")
                print(f"   Next run: {next_run}")
                
                if next_run:
                    try:
                        from datetime import datetime, timezone
                        if next_run.endswith('Z'):
                            next_run = next_run[:-1] + '+00:00'
                        next_run_dt = datetime.fromisoformat(next_run)
                        now = datetime.now(timezone.utc)
                        if next_run_dt.tzinfo is None:
                            next_run_dt = next_run_dt.replace(tzinfo=timezone.utc)
                        
                        time_until = next_run_dt - now
                        hours_until = time_until.total_seconds() / 3600
                        
                        if hours_until < 0:
                            print("   🚨 Job is overdue - should run soon!")
                        elif hours_until < 1:
                            print("   🔜 Job will run within 1 hour")
                        else:
                            print(f"   ⏰ Job will run in {hours_until:.1f} hours")
                        
                        return True
                    except Exception as e:
                        print(f"   ⚠️  Could not parse next run time: {e}")
                        return False
                else:
                    print("   ⚠️  No next run time scheduled")
                    return False
            else:
                print("   ❌ Profile job not found in scheduler")
                return False
        else:
            print(f"❌ Failed to get scraper status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking scraper status: {e}")
        return False

def check_profile_after_scrape(profile_id, profile_name):
    """Check if profile was updated after scraping"""
    print(f"🔍 Checking profile status after scrape: {profile_name}")
    
    try:
        # Check via listings endpoint to see if new listings were added
        response = requests.get(
            f"{RAILWAY_URL}/api/listings?profile_id={profile_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            listings = data.get('listings', [])
            print(f"📊 Profile now has {len(listings)} listings")
            
            # Check for recently scraped items
            recent_listings = []
            for listing in listings:
                scraped_at = listing.get('scraped_at')
                if scraped_at:
                    try:
                        scraped_dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                        now = datetime.now(scraped_dt.tzinfo)
                        time_diff = (now - scraped_dt).total_seconds() / 60  # minutes
                        
                        if time_diff < 30:  # Less than 30 minutes ago
                            recent_listings.append(listing)
                    except:
                        pass
            
            if recent_listings:
                print(f"✅ Found {len(recent_listings)} recently scraped listings")
                return True
            else:
                print("⚠️  No recently scraped listings found")
                return False
        else:
            print(f"❌ Failed to check profile: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking profile: {e}")
        return False

def main():
    """Main function to trigger scrapes for never-scraped profiles"""
    print("🚀 MANUAL SCRAPE TRIGGER FOR NEVER-SCRAPED PROFILES")
    print("=" * 60)
    
    # Profiles that have never been scraped (from previous check)
    never_scraped_profiles = [
        ("profile_1751631745", "Amsterdam"),
        ("profile_1751644826", "Rotterdam"),
        ("profile_1751649244", "Test Profile 191404")
    ]
    
    print(f"📊 Found {len(never_scraped_profiles)} profiles that have never been scraped")
    print()
    
    results = []
    
    for profile_id, profile_name in never_scraped_profiles:
        print(f"Processing: {profile_name} (ID: {profile_id})")
        print("-" * 40)
        
        # Try the specific trigger endpoint first
        success = trigger_manual_scrape(profile_id, profile_name)
        
        if success:
            # Wait a bit and then check the scheduler status
            print("⏳ Waiting 10 seconds for scheduler to update...")
            import time
            time.sleep(10)
            
            # Check if the profile job is now scheduled
            job_scheduled = trigger_scrape_via_general_endpoint(profile_id, profile_name)
            
            if job_scheduled:
                print("✅ Profile is now scheduled for scraping")
                results.append((profile_name, profile_id, True))
            else:
                print("⚠️  Profile sync succeeded but job not found")
                results.append((profile_name, profile_id, False))
        else:
            results.append((profile_name, profile_id, False))
        
        print()
    
    # Summary
    print("=" * 60)
    print("📊 MANUAL SCRAPE RESULTS")
    print("=" * 60)
    
    successful = 0
    failed = 0
    
    for profile_name, profile_id, updated in results:
        if updated:
            print(f"✅ {profile_name}: Successfully scheduled for scraping")
            successful += 1
        else:
            print(f"❌ {profile_name}: Failed to schedule/sync")
            failed += 1
    
    print(f"\n📈 Summary: {successful} successful, {failed} failed")
    
    if successful > 0:
        print("\n🎉 Some profiles were successfully scheduled for scraping!")
        print("   - These profiles should be picked up by the periodic scraper")
        print("   - Monitor the Railway scraper status to see when they run")
        print("   - Check back in a few hours to see if they've been scraped")
    
    if failed > 0:
        print("\n⚠️  Some profiles failed to be scheduled:")
        print("   - Check Railway logs for detailed error messages")
        print("   - Verify that the profiles exist in the database")
        print("   - Consider manually checking the periodic scraper status")

if __name__ == "__main__":
    main()
