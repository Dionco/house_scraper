#!/usr/bin/env python3
"""
Manual test to trigger a scrape and verify the process works.
"""

import sys
import os
sys.path.append('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/backend')

from periodic_scraper import periodic_scraper
import json

def test_manual_scrape():
    """Test manual scraping of a profile"""
    
    # Load database to see profiles
    db_file = "/Users/Dion/Downloads/Documenten/Code projects/House_scraper/database.json"
    with open(db_file, 'r') as f:
        db = json.load(f)
    
    profiles = db.get('profiles', {})
    print("Available profiles:")
    
    never_scraped = []
    for pid, profile in profiles.items():
        name = profile.get('name', 'Unnamed')
        last_scraped = profile.get('last_scraped')
        print(f"- {name} ({pid}): Last scraped: {last_scraped or 'Never'}")
        if not last_scraped:
            never_scraped.append(pid)
    
    if never_scraped:
        print(f"\nTesting scrape for profile that was never scraped: {never_scraped[0]}")
        profile_id = never_scraped[0]
        
        print("Before scrape:")
        profile = profiles[profile_id]
        print(f"  Last scraped: {profile.get('last_scraped', 'Never')}")
        print(f"  Listings count: {len(profile.get('listings', []))}")
        
        # Trigger manual scrape
        print("\nTriggering scrape...")
        try:
            periodic_scraper.scrape_profile(profile_id)
            print("✅ Scrape completed")
            
            # Reload database to see results
            with open(db_file, 'r') as f:
                updated_db = json.load(f)
            
            updated_profile = updated_db['profiles'][profile_id]
            print("\nAfter scrape:")
            print(f"  Last scraped: {updated_profile.get('last_scraped', 'Never')}")
            print(f"  Listings count: {len(updated_profile.get('listings', []))}")
            print(f"  New listings: {updated_profile.get('last_new_listings_count', 0)}")
            
            if 'last_scrape_error' in updated_profile:
                print(f"  ❌ Error: {updated_profile['last_scrape_error']}")
            
        except Exception as e:
            print(f"❌ Error during scrape: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\nAll profiles have been scraped before.")

if __name__ == "__main__":
    test_manual_scrape()
