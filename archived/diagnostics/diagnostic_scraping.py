#!/usr/bin/env python3
"""
Comprehensive monitoring script for periodic scraping functionality.
This script helps diagnose and fix issues with profiles showing 'Never' for last scraped.
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

def check_railway_deployment():
    """Check Railway deployment status and scraper functionality"""
    base_url = "https://house-scraper-production-7202.up.railway.app"
    
    print("🚂 Railway Deployment Status Check")
    print("=" * 50)
    
    # 1. Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health: {health['status']} at {health['timestamp']}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # 2. Scraper status
    try:
        response = requests.get(f"{base_url}/api/scraper/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Scraper running: {status['is_running']}")
            print(f"✅ Total jobs: {status['total_jobs']}")
            
            # Check job schedules
            now_utc = datetime.utcnow()
            print("\n📅 Job Schedule Analysis:")
            for job in status['jobs']:
                if 'scrape_profile_' in job['id']:
                    profile_id = job['id'].replace('scrape_profile_', '')
                    next_run = datetime.fromisoformat(job['next_run'].replace('Z', '+00:00'))
                    time_until = next_run - now_utc.replace(tzinfo=next_run.tzinfo)
                    
                    if time_until.total_seconds() > 0:
                        hours = int(time_until.total_seconds() // 3600)
                        minutes = int((time_until.total_seconds() % 3600) // 60)
                        print(f"   • {profile_id}: Next run in {hours}h {minutes}m")
                    else:
                        print(f"   • {profile_id}: ⚠️  Overdue by {abs(time_until)}")
            
        else:
            print(f"❌ Scraper status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Scraper status error: {e}")
        return False
    
    return True

def force_sync_jobs():
    """Force sync jobs on Railway"""
    base_url = "https://house-scraper-production-7202.up.railway.app"
    
    try:
        response = requests.post(f"{base_url}/api/scraper/sync", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Job sync: {result['message']}")
            return True
        else:
            print(f"❌ Job sync failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Job sync error: {e}")
        return False

def analyze_profile_gaps():
    """Analyze why some profiles show 'Never' for last scraped"""
    print("\n🔍 Profile Analysis")
    print("=" * 30)
    
    # Load local database to understand the profile structure
    try:
        with open('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/database.json', 'r') as f:
            db = json.load(f)
        
        profiles = db.get('profiles', {})
        never_scraped = []
        recently_scraped = []
        old_scraped = []
        
        now = datetime.now()
        
        for pid, profile in profiles.items():
            name = profile.get('name', 'Unnamed')
            last_scraped = profile.get('last_scraped')
            
            if not last_scraped:
                never_scraped.append((pid, name))
            else:
                try:
                    scraped_time = datetime.fromisoformat(last_scraped)
                    age = now - scraped_time
                    
                    if age.total_seconds() < 3600 * 24:  # Less than 24 hours
                        recently_scraped.append((pid, name, age))
                    else:
                        old_scraped.append((pid, name, age))
                except:
                    never_scraped.append((pid, name))
        
        print(f"📊 Profile Status Summary:")
        print(f"   • Never scraped: {len(never_scraped)}")
        print(f"   • Recently scraped (< 24h): {len(recently_scraped)}")
        print(f"   • Old scrapes (> 24h): {len(old_scraped)}")
        
        if never_scraped:
            print(f"\n❗ Profiles that were NEVER scraped:")
            for pid, name in never_scraped:
                print(f"   • {name} ({pid})")
        
        if old_scraped:
            print(f"\n⏰ Profiles with old scrapes:")
            for pid, name, age in old_scraped:
                days = int(age.total_seconds() // (3600 * 24))
                hours = int((age.total_seconds() % (3600 * 24)) // 3600)
                print(f"   • {name} ({pid}): {days}d {hours}h ago")
        
        return never_scraped, old_scraped
        
    except Exception as e:
        print(f"❌ Error analyzing profiles: {e}")
        return [], []

def recommend_fixes(never_scraped, old_scraped):
    """Recommend fixes for periodic scraping issues"""
    print("\n🔧 Recommendations")
    print("=" * 30)
    
    if never_scraped:
        print("❗ For profiles that were NEVER scraped:")
        print("   1. Check if jobs were created when profiles were added")
        print("   2. Verify profile creation triggers job scheduling")
        print("   3. Manually trigger sync to create missing jobs")
        print("   4. Check profile filters for validity")
        
    if old_scraped:
        print("⏰ For profiles with old scrapes:")
        print("   1. Check if scraper is encountering errors")
        print("   2. Verify job intervals are set correctly")
        print("   3. Check Railway memory/timeout limits")
        print("   4. Look for scraping failures in logs")
    
    print("\n🚀 Immediate Actions:")
    print("   1. Run job sync to ensure all profiles have jobs")
    print("   2. Check Railway logs for scraping errors")
    print("   3. Verify timezone handling between local and Railway")
    print("   4. Monitor next few scheduled runs")

def main():
    print("🔍 Periodic Scraping Diagnostic Tool")
    print("=" * 50)
    
    # Check Railway deployment
    railway_ok = check_railway_deployment()
    
    if railway_ok:
        print("\n🔄 Forcing job synchronization...")
        sync_ok = force_sync_jobs()
        
        if sync_ok:
            print("✅ Job sync completed")
            
            # Wait a moment and check status again
            print("\n⏳ Waiting 5 seconds for changes to take effect...")
            time.sleep(5)
            
            print("\n🔄 Checking status after sync...")
            check_railway_deployment()
        
    # Analyze local profiles
    never_scraped, old_scraped = analyze_profile_gaps()
    
    # Provide recommendations
    recommend_fixes(never_scraped, old_scraped)
    
    print(f"\n✅ Diagnostic completed at {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()
