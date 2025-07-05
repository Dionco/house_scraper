#!/usr/bin/env python3
"""
Specific script to check Railway scraper jobs and get detailed information.
"""

import requests
import json
from datetime import datetime, timezone

RAILWAY_URL = "https://house-scraper-production-7202.up.railway.app"

def check_scraper_jobs():
    """Get detailed information about scraper jobs"""
    print("=== DETAILED SCRAPER JOB CHECK ===")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/scraper/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Scraper running: {status.get('is_running', False)}")
            print(f"📊 Total jobs: {status.get('total_jobs', 0)}")
            
            jobs = status.get('jobs', [])
            if jobs:
                print("\n📋 Detailed Job Information:")
                for i, job in enumerate(jobs, 1):
                    print(f"\n{i}. Job: {job.get('name', 'Unknown')}")
                    print(f"   ID: {job.get('id', 'Unknown')}")
                    
                    next_run = job.get('next_run')
                    if next_run:
                        try:
                            # Handle timezone-aware datetime properly
                            if next_run.endswith('Z'):
                                next_run = next_run[:-1] + '+00:00'
                            next_run_dt = datetime.fromisoformat(next_run)
                            
                            # Get current time in UTC
                            now = datetime.now(timezone.utc)
                            
                            # Make sure both times are timezone-aware
                            if next_run_dt.tzinfo is None:
                                next_run_dt = next_run_dt.replace(tzinfo=timezone.utc)
                            
                            time_until = next_run_dt - now
                            hours_until = time_until.total_seconds() / 3600
                            
                            print(f"   Next run: {next_run_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                            print(f"   Time until: {hours_until:.1f} hours")
                            
                            if hours_until < 0:
                                print("   ⚠️  Job is overdue!")
                            elif hours_until < 1:
                                print("   🔜 Job running soon!")
                            
                        except Exception as e:
                            print(f"   Next run: {next_run} (parse error: {e})")
                    else:
                        print("   ❌ No next run scheduled")
            
            return status
        else:
            print(f"❌ Failed to get scraper status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def check_available_endpoints():
    """Check what endpoints are available without authentication"""
    print("\n=== AVAILABLE ENDPOINTS CHECK ===")
    endpoints = [
        "/health",
        "/api/scraper/status",
        "/api/listings",
        "/api/profiles"  # This will likely fail due to auth
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{RAILWAY_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: Available")
                if endpoint == "/api/listings":
                    data = response.json()
                    print(f"   📊 {len(data.get('listings', []))} listings found")
            elif response.status_code == 401:
                print(f"🔒 {endpoint}: Requires authentication")
            else:
                print(f"❌ {endpoint}: Status {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")

def check_database_listings():
    """Check database listings to see if scraping is working"""
    print("\n=== DATABASE LISTINGS CHECK ===")
    try:
        response = requests.get(f"{RAILWAY_URL}/api/listings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            listings = data.get('listings', [])
            print(f"✅ Total listings: {len(listings)}")
            
            # Check for new listings
            new_listings = [l for l in listings if l.get('is_new', False)]
            print(f"📊 New listings: {len(new_listings)}")
            
            # Check scraped_at timestamps
            scraped_times = []
            for listing in listings:
                scraped_at = listing.get('scraped_at')
                if scraped_at:
                    try:
                        scraped_dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                        scraped_times.append(scraped_dt)
                    except:
                        pass
            
            if scraped_times:
                latest_scrape = max(scraped_times)
                now = datetime.now(timezone.utc)
                if latest_scrape.tzinfo is None:
                    latest_scrape = latest_scrape.replace(tzinfo=timezone.utc)
                
                time_since_last = now - latest_scrape
                hours_since = time_since_last.total_seconds() / 3600
                
                print(f"🕐 Latest scrape: {latest_scrape.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"⏱️  Time since last scrape: {hours_since:.1f} hours")
                
                if hours_since < 6:
                    print("✅ Recent scraping activity detected")
                else:
                    print("⚠️  No recent scraping activity")
            else:
                print("⚠️  No scraped timestamps found")
            
            return True
        else:
            print(f"❌ Failed to get listings: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def trigger_scraper_sync():
    """Try to sync scraper jobs"""
    print("\n=== TRIGGERING SCRAPER SYNC ===")
    try:
        response = requests.post(f"{RAILWAY_URL}/api/scraper/sync", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {result.get('message', 'Sync completed')}")
            return True
        else:
            print(f"❌ Sync failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Sync error: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🔍 RAILWAY SCRAPER DETAILED DIAGNOSTIC")
    print("=" * 50)
    
    # Check scraper jobs
    scraper_status = check_scraper_jobs()
    
    # Check available endpoints
    check_available_endpoints()
    
    # Check database listings
    check_database_listings()
    
    # Trigger sync
    trigger_scraper_sync()
    
    # Final job check
    print("\n=== FINAL JOB STATUS ===")
    final_status = check_scraper_jobs()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    if final_status:
        total_jobs = final_status.get('total_jobs', 0)
        is_running = final_status.get('is_running', False)
        
        print(f"✅ Scraper running: {is_running}")
        print(f"📊 Total jobs: {total_jobs}")
        
        if is_running and total_jobs > 0:
            print("✅ Periodic scraping appears to be active")
        elif is_running and total_jobs == 0:
            print("⚠️  Scraper is running but has no jobs")
        else:
            print("❌ Scraper is not running properly")
    else:
        print("❌ Could not determine scraper status")

if __name__ == "__main__":
    main()
