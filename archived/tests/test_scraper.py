#!/usr/bin/env python3
"""
Quick test script to verify the scraping functionality works
"""
import logging
from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraper():
    """Test the scraper with a simple Funda search"""
    # Test URL (Haarlem rentals 3000-5000)
    test_url = "https://www.funda.nl/zoeken/huur/?selected_area=[%22haarlem%22]&price=3000-5000"
    
    print(f"Testing scraper with URL: {test_url}")
    
    try:
        # Scrape HTML
        html = scrape_funda_html(test_url, max_retries=1, timeout=30)
        
        if html:
            print(f"✓ Successfully scraped {len(html)} characters")
            
            # Try to extract listings
            listings = extract_simple_listings_from_html(html)
            print(f"✓ Successfully extracted {len(listings)} listings")
            
            if listings:
                print(f"✓ Sample listing: {listings[0].get('title', 'No title')}")
                return True
            else:
                print("✗ No listings found in HTML")
                return False
        else:
            print("✗ Failed to scrape HTML")
            return False
            
    except Exception as e:
        print(f"✗ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_scraper()
    if success:
        print("\n✓ Test passed - scraper is working!")
    else:
        print("\n✗ Test failed - scraper needs debugging")
