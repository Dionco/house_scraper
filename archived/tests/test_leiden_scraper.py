#!/usr/bin/env python3
"""
Test script to debug Leiden scraping issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html
import json

def test_leiden_scraper():
    """Test the scraper with a Leiden URL"""
    # Test URL for Leiden
    url = "https://www.funda.nl/zoeken/koop/?selected_area=[%22leiden%22]"
    
    print(f"Testing scraper with URL: {url}")
    
    # Scrape the HTML
    html = scrape_funda_html(url, max_retries=1)
    
    if not html:
        print("❌ Failed to scrape HTML")
        return False
    
    print(f"✓ Successfully scraped {len(html)} characters")
    
    # Extract listings
    listings = extract_simple_listings_from_html(html)
    
    print(f"✓ Successfully extracted {len(listings)} listings")
    
    # Print detailed info about each listing
    for i, listing in enumerate(listings, 1):
        print(f"\n--- Listing {i} ---")
        for key, value in listing.items():
            print(f"{key}: {value}")
    
    # Save HTML for debugging
    with open('debug_leiden_current.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Saved HTML to debug_leiden_current.html")
    
    # Save listings as JSON
    with open('debug_leiden_listings.json', 'w', encoding='utf-8') as f:
        json.dump(listings, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved listings to debug_leiden_listings.json")
    
    print("\n✓ Test completed!")
    return True

if __name__ == "__main__":
    test_leiden_scraper()
