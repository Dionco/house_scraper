#!/usr/bin/env python3
"""
Monitor the next scheduled scrapes and track their progress.
"""

import requests
import json
import time
from datetime import datetime, timezone

RAILWAY_URL = "https://house-scraper-production-7202.up.railway.app"

def get_next_scrape_times():
    """Get the next scheduled scrape times for all profiles"""
    try:
        response = requests.get(f"{RAILWAY_URL}/api/scraper/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            jobs = status.get('jobs', [])
            
            next_scrapes = []
            now = datetime.now(timezone.utc)
            
            for job in jobs:
                if job.get('id', '').startswith('scrape_profile_'):
                    profile_id = job.get('id', '').replace('scrape_profile_', '')
                    next_run = job.get('next_run')
                    
                    if next_run:
                        try:
                            if next_run.endswith('Z'):
                                next_run = next_run[:-1] + '+00:00'
                            next_run_dt = datetime.fromisoformat(next_run)
                            if next_run_dt.tzinfo is None:
                                next_run_dt = next_run_dt.replace(tzinfo=timezone.utc)
                            
                            time_until = next_run_dt - now
                            hours_until = time_until.total_seconds() / 3600
                            
                            next_scrapes.append({
                                'profile_id': profile_id,
                                'job_name': job.get('name', ''),
                                'next_run': next_run_dt,
                                'hours_until': hours_until
                            })
                        except Exception as e:
                            print(f"Error parsing time for {profile_id}: {e}")
            
            # Sort by next run time
            next_scrapes.sort(key=lambda x: x['next_run'])
            return next_scrapes
        else:
            print(f"Failed to get scraper status: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error getting scraper status: {e}")
        return []

def check_profile_last_scraped():
    """Check the last scraped times by looking at listings"""
    try:
        response = requests.get(f"{RAILWAY_URL}/api/listings", timeout=10)
        if response.status_code == 200:
            data = response.json()
            listings = data.get('listings', [])
            
            # Get the most recent scraped_at time
            latest_scrape = None
            for listing in listings:
                scraped_at = listing.get('scraped_at')
                if scraped_at:
                    try:
                        scraped_dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                        if scraped_dt.tzinfo is None:
                            scraped_dt = scraped_dt.replace(tzinfo=timezone.utc)
                        
                        if latest_scrape is None or scraped_dt > latest_scrape:
                            latest_scrape = scraped_dt
                    except:
                        pass
            
            return latest_scrape
        else:
            print(f"Failed to get listings: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error checking listings: {e}")
        return None

def monitor_scrapes():
    """Monitor the scraping progress"""
    print("🔍 MONITORING PERIODIC SCRAPES")
    print("=" * 50)
    
    while True:
        print(f"\n📅 Status at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 30)
        
        # Get next scrape times
        next_scrapes = get_next_scrape_times()
        
        if next_scrapes:
            print("📋 Next scheduled scrapes:")
            for scrape in next_scrapes[:5]:  # Show first 5
                profile_name = scrape['job_name'].replace('Scrape Profile ', '')
                
                if scrape['hours_until'] < 0:
                    status = "🚨 OVERDUE"
                elif scrape['hours_until'] < 0.5:
                    status = "🔜 SOON (< 30 min)"
                elif scrape['hours_until'] < 1:
                    status = "⏰ Within 1 hour"
                else:
                    status = f"⏰ {scrape['hours_until']:.1f} hours"
                
                print(f"  - {profile_name}: {status}")
        else:
            print("❌ No scheduled scrapes found")
        
        # Check latest scrape activity
        latest_scrape = check_profile_last_scraped()
        if latest_scrape:
            now = datetime.now(timezone.utc)
            time_since = now - latest_scrape
            minutes_since = time_since.total_seconds() / 60
            
            print(f"\n🕐 Latest scrape activity: {minutes_since:.1f} minutes ago")
            
            if minutes_since < 5:
                print("✅ Very recent scraping activity detected!")
            elif minutes_since < 30:
                print("✅ Recent scraping activity detected")
            elif minutes_since < 60:
                print("⚠️  Scraping activity within last hour")
            else:
                print("⚠️  No recent scraping activity")
        else:
            print("❌ Could not determine latest scrape activity")
        
        print("\n" + "=" * 50)
        print("Press Ctrl+C to stop monitoring")
        print("Checking again in 5 minutes...")
        
        try:
            time.sleep(300)  # Wait 5 minutes
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped by user")
            break

def one_time_check():
    """Do a single check of the scraping status"""
    print("🔍 ONE-TIME SCRAPING STATUS CHECK")
    print("=" * 40)
    
    # Get next scrape times
    next_scrapes = get_next_scrape_times()
    
    print(f"📊 Found {len(next_scrapes)} scheduled scrape jobs")
    
    if next_scrapes:
        print("\n📋 All scheduled scrapes:")
        for i, scrape in enumerate(next_scrapes, 1):
            profile_name = scrape['job_name'].replace('Scrape Profile ', '')
            
            if scrape['hours_until'] < 0:
                status = "🚨 OVERDUE"
            elif scrape['hours_until'] < 0.5:
                status = "🔜 SOON (< 30 min)"
            elif scrape['hours_until'] < 1:
                status = "⏰ Within 1 hour"
            else:
                status = f"⏰ {scrape['hours_until']:.1f} hours"
            
            print(f"{i:2d}. {profile_name}")
            print(f"    Profile ID: {scrape['profile_id']}")
            print(f"    Next run: {scrape['next_run'].strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"    Status: {status}")
            print()
    
    # Check latest scrape activity
    latest_scrape = check_profile_last_scraped()
    if latest_scrape:
        now = datetime.now(timezone.utc)
        time_since = now - latest_scrape
        minutes_since = time_since.total_seconds() / 60
        
        print(f"🕐 Latest scrape activity:")
        print(f"    Time: {latest_scrape.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        print(f"    Minutes ago: {minutes_since:.1f}")
        
        if minutes_since < 5:
            print("    Status: ✅ Very recent activity")
        elif minutes_since < 30:
            print("    Status: ✅ Recent activity")
        elif minutes_since < 60:
            print("    Status: ⚠️  Within last hour")
        else:
            print("    Status: ⚠️  No recent activity")
    else:
        print("❌ Could not determine latest scrape activity")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_scrapes()
    else:
        one_time_check()

if __name__ == "__main__":
    main()
