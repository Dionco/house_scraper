#!/usr/bin/env python3
"""
Deep investigation script for periodic scraper issues
"""

import requests
import json
import time
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_local_scraper():
    """Test local scraper functionality"""
    print("=" * 60)
    print("TESTING LOCAL SCRAPER")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    try:
        # 1. Test scraper status
        print("\n1. SCRAPER STATUS:")
        response = requests.get(f"{base_url}/api/scraper/status")
        if response.status_code == 200:
            data = response.json()
            print(f"   Running: {data.get('is_running', False)}")
            print(f"   Total jobs: {data.get('total_jobs', 0)}")
            
            jobs = data.get('jobs', [])
            profile_jobs = [j for j in jobs if j.get('id', '').startswith('scrape_profile_')]
            print(f"   Profile jobs: {len(profile_jobs)}")
            
            now = datetime.now()
            for job in profile_jobs:
                next_run = job.get('next_run')
                if next_run:
                    try:
                        dt = datetime.fromisoformat(next_run)
                        dt_naive = dt.replace(tzinfo=None)
                        diff = (dt_naive - now).total_seconds() / 60
                        print(f"     {job.get('name', 'Unknown')}: {diff:.1f} minutes")
                    except:
                        print(f"     {job.get('name', 'Unknown')}: {next_run}")
        else:
            print(f"   ERROR: {response.status_code} - {response.text}")
            
        # 2. Test admin stats
        print("\n2. ADMIN STATS:")
        response = requests.get(f"{base_url}/api/admin/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   Total listings: {data.get('total_listings', 0)}")
            print(f"   New listings: {data.get('new_listings', 0)}")
            latest_scrape = data.get('latest_scrape')
            if latest_scrape:
                dt = datetime.fromisoformat(latest_scrape)
                diff = (datetime.now() - dt).total_seconds() / 3600
                print(f"   Latest scrape: {dt} ({diff:.1f}h ago)")
            else:
                print("   Latest scrape: Never")
        else:
            print(f"   ERROR: {response.status_code} - {response.text}")
            
        # 3. Test database direct access
        print("\n3. DATABASE ANALYSIS:")
        try:
            with open('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/database.json', 'r') as f:
                db = json.load(f)
                
            profiles = db.get('profiles', {})
            print(f"   Profiles in database: {len(profiles)}")
            
            overdue_profiles = []
            for profile_id, profile in profiles.items():
                name = profile.get('name', 'Unknown')
                last_scraped = profile.get('last_scraped')
                interval = profile.get('scrape_interval_hours', 1)
                
                if last_scraped:
                    dt = datetime.fromisoformat(last_scraped)
                    expected_next = dt + timedelta(hours=interval)
                    now = datetime.now()
                    
                    if expected_next < now:
                        overdue_hours = (now - expected_next).total_seconds() / 3600
                        overdue_profiles.append({
                            'name': name,
                            'id': profile_id,
                            'last_scraped': last_scraped,
                            'overdue_hours': overdue_hours
                        })
                        print(f"     {name}: OVERDUE by {overdue_hours:.1f}h")
                    else:
                        print(f"     {name}: On schedule")
                else:
                    print(f"     {name}: Never scraped")
                    
            print(f"   Total overdue profiles: {len(overdue_profiles)}")
            
        except Exception as e:
            print(f"   ERROR reading database: {e}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    return True

def test_railway_scraper():
    """Test Railway scraper functionality"""
    print("\n" + "=" * 60)
    print("TESTING RAILWAY SCRAPER")
    print("=" * 60)
    
    # You'll need to replace this with your actual Railway URL
    railway_url = "https://house-scraper-production.up.railway.app"
    
    try:
        # 1. Test scraper status
        print("\n1. RAILWAY SCRAPER STATUS:")
        response = requests.get(f"{railway_url}/api/scraper/status", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   Running: {data.get('is_running', False)}")
            print(f"   Total jobs: {data.get('total_jobs', 0)}")
            
            jobs = data.get('jobs', [])
            profile_jobs = [j for j in jobs if j.get('id', '').startswith('scrape_profile_')]
            print(f"   Profile jobs: {len(profile_jobs)}")
            
            now = datetime.now()
            for job in profile_jobs:
                next_run = job.get('next_run')
                if next_run:
                    try:
                        dt = datetime.fromisoformat(next_run)
                        dt_naive = dt.replace(tzinfo=None)
                        diff = (dt_naive - now).total_seconds() / 60
                        print(f"     {job.get('name', 'Unknown')}: {diff:.1f} minutes")
                    except:
                        print(f"     {job.get('name', 'Unknown')}: {next_run}")
        else:
            print(f"   ERROR: {response.status_code}")
            
        # 2. Test admin stats
        print("\n2. RAILWAY ADMIN STATS:")
        response = requests.get(f"{railway_url}/api/admin/stats", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   Total listings: {data.get('total_listings', 0)}")
            print(f"   New listings: {data.get('new_listings', 0)}")
            latest_scrape = data.get('latest_scrape')
            if latest_scrape:
                dt = datetime.fromisoformat(latest_scrape)
                diff = (datetime.now() - dt).total_seconds() / 3600
                print(f"   Latest scrape: {dt} ({diff:.1f}h ago)")
            else:
                print("   Latest scrape: Never")
        else:
            print(f"   ERROR: {response.status_code}")
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    return True

def monitor_scraper_execution():
    """Monitor if the scraper actually executes when scheduled"""
    print("\n" + "=" * 60)
    print("MONITORING SCRAPER EXECUTION")
    print("=" * 60)
    
    base_url = "http://localhost:8000"
    
    # Get current stats
    try:
        response = requests.get(f"{base_url}/api/admin/stats")
        if response.status_code == 200:
            initial_stats = response.json()
            initial_scrape = initial_stats.get('latest_scrape')
            print(f"Initial latest scrape: {initial_scrape}")
            
            # Monitor for 5 minutes
            print("Monitoring for 5 minutes...")
            start_time = datetime.now()
            while (datetime.now() - start_time).total_seconds() < 300:  # 5 minutes
                time.sleep(30)  # Check every 30 seconds
                
                response = requests.get(f"{base_url}/api/admin/stats")
                if response.status_code == 200:
                    current_stats = response.json()
                    current_scrape = current_stats.get('latest_scrape')
                    
                    if current_scrape != initial_scrape:
                        print(f"SCRAPE DETECTED! New latest scrape: {current_scrape}")
                        return True
                    else:
                        print(f"No change yet... {datetime.now().strftime('%H:%M:%S')}")
                        
            print("No scrape detected during monitoring period")
            return False
            
    except Exception as e:
        print(f"ERROR monitoring: {e}")
        return False

def main():
    """Main investigation function"""
    print("DEEP SCRAPER INVESTIGATION")
    print("Current time:", datetime.now())
    
    # Test local scraper
    local_ok = test_local_scraper()
    
    # Test Railway scraper
    railway_ok = test_railway_scraper()
    
    # Monitor execution
    if local_ok:
        print("\n" + "=" * 60)
        print("MONITORING EXECUTION")
        print("=" * 60)
        
        # Check if jobs are scheduled to run soon
        response = requests.get("http://localhost:8000/api/scraper/status")
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            profile_jobs = [j for j in jobs if j.get('id', '').startswith('scrape_profile_')]
            
            soonest_job = None
            soonest_time = None
            
            for job in profile_jobs:
                next_run = job.get('next_run')
                if next_run:
                    try:
                        dt = datetime.fromisoformat(next_run)
                        dt_naive = dt.replace(tzinfo=None)
                        if soonest_time is None or dt_naive < soonest_time:
                            soonest_time = dt_naive
                            soonest_job = job
                    except:
                        pass
            
            if soonest_job and soonest_time:
                now = datetime.now()
                diff = (soonest_time - now).total_seconds() / 60
                print(f"Soonest job: {soonest_job.get('name', 'Unknown')} in {diff:.1f} minutes")
                
                if diff < 10:  # If job is within 10 minutes
                    print("Job is scheduled soon - monitoring for execution...")
                    monitor_scraper_execution()
                else:
                    print("Jobs are not scheduled to run soon")
            else:
                print("No jobs scheduled")
    
    print("\n" + "=" * 60)
    print("INVESTIGATION COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
