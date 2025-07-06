#!/usr/bin/env python3
"""
Monitor the next Railway scrape execution to see if it fails due to missing browser
"""

import requests
import json
import time
from datetime import datetime, timezone

RAILWAY_URL = "https://house-scraper-production-7202.up.railway.app"

def check_railway_status():
    """Check Railway scraper status and stats"""
    try:
        # Get current stats
        stats_response = requests.get(f"{RAILWAY_URL}/api/admin/stats", timeout=10)
        stats = stats_response.json()
        
        # Get scraper status
        status_response = requests.get(f"{RAILWAY_URL}/api/scraper/status", timeout=10)
        status = status_response.json()
        
        current_time = datetime.now(timezone.utc)
        
        print(f"\n=== Railway Status Check at {current_time.strftime('%H:%M:%S')} ===")
        print(f"Latest scrape: {stats['latest_scrape']}")
        print(f"Total listings: {stats['total_listings']}")
        print(f"New listings: {stats['new_listings']}")
        print(f"Scheduler running: {status['is_running']}")
        print(f"Total jobs: {status['total_jobs']}")
        
        if status['jobs']:
            next_job = min(status['jobs'], key=lambda x: x['next_run'])
            print(f"Next job: {next_job['name']} at {next_job['next_run']}")
            
            # Check if any job is overdue
            next_run_time = datetime.fromisoformat(next_job['next_run'].replace('Z', '+00:00'))
            if next_run_time <= current_time:
                print("⚠️  Job is overdue! Should have run already.")
            else:
                time_diff = (next_run_time - current_time).total_seconds()
                print(f"⏱️  Next job in {time_diff:.1f} seconds")
        
        return stats, status
        
    except Exception as e:
        print(f"❌ Error checking Railway status: {e}")
        return None, None

def monitor_next_scrape():
    """Monitor Railway until the next scrape completes"""
    print("🔍 Monitoring Railway scraper for next execution...")
    
    # Get initial state
    initial_stats, initial_status = check_railway_status()
    if not initial_stats:
        print("❌ Failed to get initial Railway status")
        return
    
    initial_latest_scrape = initial_stats['latest_scrape']
    print(f"📊 Initial latest scrape: {initial_latest_scrape}")
    
    # Find next scheduled job
    if not initial_status['jobs']:
        print("❌ No jobs scheduled!")
        return
    
    next_job = min(initial_status['jobs'], key=lambda x: x['next_run'])
    next_run_time = datetime.fromisoformat(next_job['next_run'].replace('Z', '+00:00'))
    current_time = datetime.now(timezone.utc)
    
    print(f"⏰ Next job: {next_job['name']} at {next_run_time.strftime('%H:%M:%S')}")
    
    if next_run_time <= current_time:
        print("⚠️  Job is already overdue!")
    else:
        wait_time = (next_run_time - current_time).total_seconds()
        print(f"⏱️  Waiting {wait_time:.1f} seconds for next job...")
        
        # Wait until the job should run
        time.sleep(max(0, wait_time + 10))  # Wait 10 seconds after expected time
    
    # Monitor for changes
    print("\n🔄 Monitoring for scrape completion...")
    for attempt in range(12):  # Monitor for 2 minutes
        time.sleep(10)
        
        current_stats, current_status = check_railway_status()
        if not current_stats:
            continue
            
        current_latest_scrape = current_stats['latest_scrape']
        
        if current_latest_scrape != initial_latest_scrape:
            print(f"✅ SUCCESS! New scrape detected: {current_latest_scrape}")
            print(f"   Previous: {initial_latest_scrape}")
            print(f"   New: {current_latest_scrape}")
            return True
        
        print(f"⏳ Attempt {attempt + 1}: No new scrape yet (latest: {current_latest_scrape})")
    
    print("❌ FAILURE: No new scrape detected after waiting 2 minutes")
    print("   This suggests the scraper failed, likely due to missing browser dependencies")
    return False

if __name__ == "__main__":
    monitor_next_scrape()
