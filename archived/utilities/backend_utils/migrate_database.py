# One-time migration script to map all existing listings in database.json to the frontend-compatible format
import json
from listing_mapping import map_listing_for_frontend

def migrate_database_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    changed = False
    for profile_id, profile in db.items():
        new_listings = []
        for l in profile.get('listings', []):
            # Only map if not already mapped (heuristic: check for 'address.street_name' key)
            if 'address.street_name' in l:
                new_listings.append(l)
            else:
                mapped = map_listing_for_frontend(l)
                # Preserve is_new if present
                if 'is_new' in l:
                    mapped['is_new'] = l['is_new']
                new_listings.append(mapped)
                changed = True
        profile['listings'] = new_listings
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"database.json migrated and updated.")
    else:
        print(f"database.json already up to date.")

if __name__ == "__main__":
    migrate_database_json("database.json")
