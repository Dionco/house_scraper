#!/usr/bin/env python3
"""
Script to clean up invalid listings and test the profile scraping system
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def clean_database():
    """Clean up invalid listings from the database"""
    
    # Load database
    database_path = "/Users/Dion/Downloads/Documenten/Code projects/House_scraper/database.json"
    
    with open(database_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    print("=== CLEANING DATABASE ===")
    
    total_cleaned = 0
    
    # Clean listings in profiles
    for profile_id, profile in db.get("profiles", {}).items():
        print(f"\nCleaning profile: {profile.get('name', profile_id)}")
        
        listings = profile.get("listings", [])
        original_count = len(listings)
        
        # Remove invalid listings
        cleaned_listings = []
        for listing in listings:
            address = listing.get("address.street_name", "")
            city = listing.get("address.city", "")
            url = listing.get("object_detail_page_relative_url", "")
            
            # Skip invalid listings
            if ("Zoek een" in address or 
                "English" in address or 
                not city or 
                "zoeken/huur" in url):
                print(f"  Removing invalid listing: {address}")
                total_cleaned += 1
            else:
                cleaned_listings.append(listing)
        
        profile["listings"] = cleaned_listings
        cleaned_count = len(cleaned_listings)
        removed_count = original_count - cleaned_count
        
        if removed_count > 0:
            print(f"  Removed {removed_count} invalid listings, kept {cleaned_count}")
        else:
            print(f"  No invalid listings found, kept {cleaned_count}")
    
    # Save cleaned database
    with open(database_path, 'w', encoding='utf-8') as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ Database cleaned! Removed {total_cleaned} invalid listings total")
    
    return db

def test_profile_scraping():
    """Test the profile-based scraping system"""
    
    print("\n=== TESTING PROFILE SCRAPING ===")
    
    # Test the Leiden profile scraping via API
    import requests
    
    try:
        # Trigger a scrape for the Leiden profile
        leiden_response = requests.get(
            "http://localhost:8000/api/scrape_listings",
            params={
                "city": "Leiden", 
                "min_price": 1500, 
                "max_price": 4000
            },
            timeout=30
        )
        
        if leiden_response.status_code == 200:
            data = leiden_response.json()
            print(f"✓ Scraping successful!")
            print(f"  URL: {data.get('url', 'N/A')}")
            print(f"  Found: {data.get('count', 0)} listings")
            print(f"  Added: {data.get('added', 0)} new listings")
            
            # Show sample listings
            listings = data.get('listings', [])
            if listings:
                print(f"\n  Sample listings:")
                for i, listing in enumerate(listings[:3], 1):
                    address = listing.get('address', 'Unknown')
                    price = listing.get('price', 'Unknown')
                    bedrooms = listing.get('bedrooms', 'Unknown')
                    energy = listing.get('energy_label', 'Unknown')
                    print(f"    {i}. {address} - €{price} - {bedrooms} bedrooms - Energy: {energy}")
            
        else:
            print(f"❌ Scraping failed with status {leiden_response.status_code}")
            print(f"   Response: {leiden_response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
    
    # Test the listings endpoint
    try:
        listings_response = requests.get("http://localhost:8000/api/listings", timeout=10)
        
        if listings_response.status_code == 200:
            data = listings_response.json()
            listings = data.get('listings', [])
            
            # Count by city
            city_counts = {}
            for listing in listings:
                city = listing.get('address.city', 'Unknown')
                city_counts[city] = city_counts.get(city, 0) + 1
            
            print(f"\n✓ Listings endpoint working!")
            print(f"  Total listings: {len(listings)}")
            print(f"  By city:")
            for city, count in sorted(city_counts.items()):
                print(f"    {city}: {count}")
                
        else:
            print(f"❌ Listings endpoint failed with status {listings_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Listings request failed: {e}")

if __name__ == "__main__":
    db = clean_database()
    test_profile_scraping()
