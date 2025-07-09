import logging
logging.basicConfig(level=logging.INFO)

from railway_periodic_scraper import RailwayPeriodicScraper
import os
import sys
import json

# Initialize the scraper
scraper = RailwayPeriodicScraper()

# Call the _scrape_profile method with a test profile ID
try:
    # Set the correct DB_PATH environment variable to point to the project root
    os.environ['DB_PATH'] = os.path.join(os.path.dirname(os.getcwd()), 'database.json')
    db_path = os.environ['DB_PATH']
    
    print(f"Using database at: {db_path}")
    
    # Read the current database
    with open(db_path, 'r') as f:
        db = json.load(f)
    
    # Get the first profile ID or create a test one if none exist
    profile_ids = list(db.get('profiles', {}).keys())
    test_profile_id = profile_ids[0] if profile_ids else None
    
    if test_profile_id:
        print(f"Testing with existing profile ID: {test_profile_id}")
        scraper._scrape_profile(test_profile_id)
        print("Profile scrape completed successfully!")
    else:
        print("No profiles found in the database to test with")
        
except Exception as e:
    print(f"Error testing _scrape_profile: {e}")
    import traceback
    traceback.print_exc()
