#!/usr/bin/env python3
"""
Monitor local scraper execution to ensure it actually works
"""

import requests
import time
from datetime import datetime, timedelta
import json

def monitor_scraper():
    """Monitor scraper execution and report when jobs run"""
    
    print("LOCAL SCRAPER EXECUTION MONITOR")
    print("=" * 60)
    print(f"Start time: {datetime.now()}")
    print()
    
    base_url = "http://localhost:8000"
    
    # Get initial state
    try:
        response = requests.get(f"{base_url}/api/admin/stats")
        if response.status_code == 200:
            initial_stats = response.json()
            initial_scrape = initial_stats.get('latest_scrape')
            print(f"Initial latest scrape: {initial_scrape}")
            
            if initial_scrape:
                initial_dt = datetime.fromisoformat(initial_scrape)
                print(f"Initial latest scrape time: {initial_dt}")
        else:
            print(f"Error getting initial stats: {response.status_code}")
            initial_scrape = None
            
        # Get job schedule
        status_response = requests.get(f"{base_url}/api/scraper/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            jobs = status_data.get('jobs', [])
            profile_jobs = [j for j in jobs if j.get('id', '').startswith('scrape_profile_')]
            
            print(f"Monitoring {len(profile_jobs)} profile jobs:")
            
            soonest_time = None
            for job in profile_jobs:
                next_run = job.get('next_run')
                if next_run:
                    try:
                        dt = datetime.fromisoformat(next_run)
                        dt_naive = dt.replace(tzinfo=None)
                        now = datetime.now()
                        diff = (dt_naive - now).total_seconds() / 60
                        print(f"  {job.get('name', 'Unknown')}: {diff:.1f} minutes")
                        
                        if soonest_time is None or dt_naive < soonest_time:
                            soonest_time = dt_naive
                    except:
                        print(f"  {job.get('name', 'Unknown')}: {next_run}")
            
            if soonest_time:
                now = datetime.now()
                wait_time = (soonest_time - now).total_seconds()
                print(f"\\nNext job in {wait_time/60:.1f} minutes at {soonest_time}")
                
                if wait_time > 0 and wait_time < 3600:  # If within 1 hour
                    print(f"Monitoring execution for {wait_time/60:.1f} minutes...")
                    monitor_until = soonest_time + timedelta(minutes=5)  # Monitor 5 minutes past schedule
                    
                    check_count = 0
                    while datetime.now() < monitor_until:
                        time.sleep(30)  # Check every 30 seconds
                        check_count += 1
                        
                        current_time = datetime.now()
                        print(f"\\nCheck {check_count} at {current_time.strftime('%H:%M:%S')}")
                        
                        # Check if scrape happened
                        try:
                            response = requests.get(f"{base_url}/api/admin/stats")
                            if response.status_code == 200:
                                current_stats = response.json()
                                current_scrape = current_stats.get('latest_scrape')
                                
                                if current_scrape != initial_scrape:
                                    print(f"🎉 SCRAPE DETECTED!")
                                    print(f"New latest scrape: {current_scrape}")
                                    
                                    current_dt = datetime.fromisoformat(current_scrape)
                                    print(f"Scrape occurred at: {current_dt}")
                                    
                                    # Check which profiles were updated
                                    print("\\nChecking profile updates...")
                                    try:
                                        with open('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/database.json', 'r') as f:
                                            db = json.load(f)
                                        
                                        profiles = db.get('profiles', {})
                                        for profile_id, profile in profiles.items():
                                            name = profile.get('name', 'Unknown')
                                            last_scraped = profile.get('last_scraped')
                                            if last_scraped:
                                                dt = datetime.fromisoformat(last_scraped)
                                                if dt >= current_dt - timedelta(minutes=5):
                                                    new_count = profile.get('last_new_listings_count', 0)
                                                    print(f"  ✓ {name}: scraped at {dt}, {new_count} new listings")
                                                else:
                                                    print(f"  - {name}: not updated")
                                            else:
                                                print(f"  - {name}: never scraped")
                                    except Exception as e:
                                        print(f"Error checking profiles: {e}")
                                    
                                    print("\\n✅ SCRAPER WORKING CORRECTLY!")
                                    return True
                                else:
                                    print(f"  No change in latest scrape time")
                            else:
                                print(f"  Error checking stats: {response.status_code}")
                        except Exception as e:
                            print(f"  Error: {e}")
                    
                    print("\\n⚠️  No scrape detected during monitoring period")
                    print("This could indicate a problem with the scheduler")
                    return False
                else:
                    print("Jobs are scheduled too far in the future to monitor")
                    return None
            else:
                print("No jobs scheduled")
                return False
        else:
            print(f"Error getting scraper status: {status_response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = monitor_scraper()
    
    if result is True:
        print("\\n✅ LOCAL SCRAPER IS WORKING")
    elif result is False:
        print("\\n❌ LOCAL SCRAPER HAS ISSUES")
    else:
        print("\\n⏳ MONITORING INCONCLUSIVE")
        
    print("\\nNext steps:")
    print("1. If local scraper works, focus on fixing Railway")
    print("2. If local scraper fails, investigate scheduler issues")
    print("3. Continue monitoring Railway deployment")
