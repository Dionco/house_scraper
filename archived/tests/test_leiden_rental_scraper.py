#!/usr/bin/env python3
"""
Test script to debug rental listings in Leiden
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html
import json

def test_leiden_rental_scraper():
    """Test the scraper with a Leiden rental URL"""
    # Test URL for Leiden rentals
    url = "https://www.funda.nl/zoeken/huur/?selected_area=[%22leiden%22]"
    
    print(f"Testing scraper with rental URL: {url}")
    
    # Scrape the HTML
    html = scrape_funda_html(url, max_retries=1)
    
    if not html:
        print("❌ Failed to scrape HTML")
        return False
    
    print(f"✓ Successfully scraped {len(html)} characters")
    
    # Extract listings
    listings = extract_simple_listings_from_html(html)
    
    print(f"✓ Successfully extracted {len(listings)} listings")
    
    # Print first few listings
    for i, listing in enumerate(listings[:5], 1):
        print(f"\n--- Rental Listing {i} ---")
        for key, value in listing.items():
            print(f"{key}: {value}")
    
    # Save listings as JSON
    with open('debug_leiden_rental_listings.json', 'w', encoding='utf-8') as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved rental listings to debug_leiden_rental_listings.json")
    
    print("\n✓ Rental test completed!")
    return True

if __name__ == "__main__":
    test_leiden_rental_scraper()
