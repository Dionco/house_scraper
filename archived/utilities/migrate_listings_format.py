#!/usr/bin/env python3
"""
Migrate listings in funda_simple_listings.json to use consistent mapped format
"""
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from listing_mapping import map_listing_for_frontend

def migrate_listings_file():
    """Migrate all listings to use the mapped format"""
    
    json_path = "funda_simple_listings.json"
    
    if not os.path.exists(json_path):
        print("No listings file found")
        return
    
    # Load existing listings
    with open(json_path, 'r', encoding='utf-8') as f:
        listings = json.load(f)
    
    print(f"Loaded {len(listings)} listings")
    
    # Migrate each listing
    migrated_listings = []
    old_format_count = 0
    new_format_count = 0
    
    for listing in listings:
        # Check if it's already in mapped format
        if 'address.street_name' in listing:
            # Already in mapped format
            migrated_listings.append(listing)
            new_format_count += 1
        else:
            # Old format, needs migration
            mapped = map_listing_for_frontend(listing)
            migrated_listings.append(mapped)
            old_format_count += 1
    
    print(f"Migrated {old_format_count} old format listings")
    print(f"Kept {new_format_count} new format listings")
    
    # Save migrated listings
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(migrated_listings, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Migration complete! All {len(migrated_listings)} listings now use mapped format")

if __name__ == "__main__":
    migrate_listings_file()
