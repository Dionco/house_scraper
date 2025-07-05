#!/usr/bin/env python3
"""
Script to check profile last scraped times directly from the database.
Uses the database.json file to get detailed profile information.
"""

import json
import os
from datetime import datetime, timezone

def load_database():
    """Load the database file"""
    db_path = os.path.join(os.path.dirname(__file__), "database.json")
    try:
        with open(db_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Database file not found at {db_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading database: {e}")
        return None

def check_profile_scraping_status():
    """Check the last scraped status for all profiles"""
    print("=== PROFILE SCRAPING STATUS CHECK ===")
    
    db = load_database()
    if not db:
        return
    
    profiles = db.get("profiles", {})
    if not profiles:
        print("❌ No profiles found in database")
        return
    
    print(f"📊 Found {len(profiles)} profiles in database\n")
    
    never_scraped = []
    recently_scraped = []
    old_scraped = []
    
    now = datetime.now(timezone.utc)
    
    for profile_id, profile in profiles.items():
        name = profile.get("name", f"Unnamed ({profile_id})")
        last_scraped = profile.get("last_scraped")
        scrape_interval = profile.get("scrape_interval_hours", 4)
        user_id = profile.get("user_id", "unknown")
        
        print(f"Profile: {name}")
        print(f"  ID: {profile_id}")
        print(f"  User ID: {user_id}")
        print(f"  Scrape interval: {scrape_interval} hours")
        
        if not last_scraped:
            print("  ❌ Last scraped: NEVER")
            never_scraped.append((name, profile_id))
        else:
            try:
                # Parse the last scraped time
                last_scraped_dt = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
                if last_scraped_dt.tzinfo is None:
                    last_scraped_dt = last_scraped_dt.replace(tzinfo=timezone.utc)
                
                time_since = now - last_scraped_dt
                hours_since = time_since.total_seconds() / 3600
                
                print(f"  ✅ Last scraped: {last_scraped_dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                print(f"  ⏱️  Time since: {hours_since:.1f} hours ago")
                
                if hours_since < 6:
                    print("  🟢 Status: Recently scraped")
                    recently_scraped.append((name, profile_id, hours_since))
                else:
                    print("  🟡 Status: Not recently scraped")
                    old_scraped.append((name, profile_id, hours_since))
                    
            except Exception as e:
                print(f"  ❌ Error parsing last scraped time: {e}")
                never_scraped.append((name, profile_id))
        
        # Check if profile has listings
        listings_count = len(profile.get("listings", []))
        print(f"  📊 Listings: {listings_count}")
        
        # Check for errors
        last_error = profile.get("last_scrape_error")
        if last_error:
            print(f"  ⚠️  Last error: {last_error}")
        
        print()
    
    # Summary
    print("=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    
    print(f"✅ Recently scraped: {len(recently_scraped)}")
    for name, profile_id, hours in recently_scraped:
        print(f"  - {name}: {hours:.1f} hours ago")
    
    print(f"\n🟡 Not recently scraped: {len(old_scraped)}")
    for name, profile_id, hours in old_scraped:
        print(f"  - {name}: {hours:.1f} hours ago")
    
    print(f"\n❌ Never scraped: {len(never_scraped)}")
    for name, profile_id in never_scraped:
        print(f"  - {name} (ID: {profile_id})")
    
    return {
        "never_scraped": never_scraped,
        "recently_scraped": recently_scraped,
        "old_scraped": old_scraped,
        "total_profiles": len(profiles)
    }

def check_scraper_jobs_vs_profiles():
    """Check if scraper jobs match profiles"""
    print("\n=== JOBS VS PROFILES CHECK ===")
    
    db = load_database()
    if not db:
        return
    
    profiles = db.get("profiles", {})
    profile_ids = set(profiles.keys())
    
    print(f"📊 Profiles in database: {len(profile_ids)}")
    
    # For this check, we'd need to query the Railway API to get job info
    # Let's just show the profile IDs for now
    print("\nProfile IDs in database:")
    for profile_id in sorted(profile_ids):
        name = profiles[profile_id].get("name", "Unnamed")
        print(f"  - {profile_id}: {name}")

def main():
    """Main function"""
    print("🔍 PROFILE SCRAPING STATUS DIAGNOSTIC")
    print("=" * 50)
    
    # Check profile scraping status
    result = check_profile_scraping_status()
    
    # Check jobs vs profiles
    check_scraper_jobs_vs_profiles()
    
    # Recommendations
    if result:
        print("\n" + "=" * 50)
        print("🔍 RECOMMENDATIONS")
        print("=" * 50)
        
        if result["never_scraped"]:
            print(f"⚠️  {len(result['never_scraped'])} profiles have never been scraped:")
            print("   - These profiles were likely created but never had their first scrape")
            print("   - Check if the periodic scraper was running when these profiles were created")
            print("   - Consider manually triggering scrapes for these profiles")
        
        if result["old_scraped"]:
            print(f"⚠️  {len(result['old_scraped'])} profiles haven't been scraped recently:")
            print("   - Check if scraper jobs are running as expected")
            print("   - Monitor Railway logs for any scraping errors")
        
        if result["recently_scraped"]:
            print(f"✅ {len(result['recently_scraped'])} profiles are being scraped regularly")
        
        print("\n📝 Next steps:")
        print("   1. Monitor the next scheduled scrapes in Railway")
        print("   2. Check Railway logs for any errors")
        print("   3. Consider manually triggering scrapes for 'never scraped' profiles")

if __name__ == "__main__":
    main()
