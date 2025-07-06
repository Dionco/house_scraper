#!/usr/bin/env python3
"""
Comprehensive test script to verify the scraper works across different cities and search types
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html
import json

def test_comprehensive_scraper():
    """Test the scraper with different cities and search types"""
    
    test_cases = [
        {
            "name": "Leiden - Buying",
            "url": "https://www.funda.nl/zoeken/koop/?selected_area=[%22leiden%22]",
            "expected_min_listings": 10
        },
        {
            "name": "Leiden - Rental",
            "url": "https://www.funda.nl/zoeken/huur/?selected_area=[%22leiden%22]",
            "expected_min_listings": 10
        },
        {
            "name": "Utrecht - Buying",
            "url": "https://www.funda.nl/zoeken/koop/?selected_area=[%22utrecht%22]",
            "expected_min_listings": 10
        },
        {
            "name": "Amsterdam - Rental",
            "url": "https://www.funda.nl/zoeken/huur/?selected_area=[%22amsterdam%22]",
            "expected_min_listings": 10
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n=== Testing {test_case['name']} ===")
        print(f"URL: {test_case['url']}")
        
        # Scrape the HTML
        html = scrape_funda_html(test_case['url'], max_retries=1)
        
        if not html:
            print("❌ Failed to scrape HTML")
            results.append({
                "test": test_case['name'],
                "success": False,
                "error": "Failed to scrape HTML"
            })
            continue
        
        print(f"✓ Successfully scraped {len(html)} characters")
        
        # Extract listings
        listings = extract_simple_listings_from_html(html)
        
        print(f"✓ Successfully extracted {len(listings)} listings")
        
        # Check if we got the minimum expected listings
        if len(listings) < test_case['expected_min_listings']:
            print(f"⚠️  Warning: Got {len(listings)} listings, expected at least {test_case['expected_min_listings']}")
        
        # Check data quality
        valid_listings = 0
        for listing in listings:
            if listing.get('address') and listing.get('price') and listing.get('funda_url'):
                valid_listings += 1
        
        quality_score = valid_listings / len(listings) if listings else 0
        print(f"✓ Data quality: {valid_listings}/{len(listings)} listings have required fields ({quality_score:.1%})")
        
        # Print a sample listing
        if listings:
            sample = listings[0]
            print(f"✓ Sample listing:")
            print(f"  Address: {sample.get('address', 'N/A')}")
            print(f"  Price: {sample.get('price', 'N/A')}")
            print(f"  Area: {sample.get('area', 'N/A')} m²")
            print(f"  Bedrooms: {sample.get('bedrooms', 'N/A')}")
            print(f"  Energy label: {sample.get('energy_label', 'N/A')}")
        
        results.append({
            "test": test_case['name'],
            "success": True,
            "listings_count": len(listings),
            "quality_score": quality_score,
            "sample_listing": listings[0] if listings else None
        })
    
    # Save results
    with open('comprehensive_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved test results to comprehensive_test_results.json")
    
    # Summary
    print(f"\n=== SUMMARY ===")
    successful_tests = sum(1 for r in results if r.get('success', False))
    print(f"✓ {successful_tests}/{len(test_cases)} tests passed")
    
    for result in results:
        if result.get('success'):
            print(f"✓ {result['test']}: {result['listings_count']} listings, {result['quality_score']:.1%} quality")
        else:
            print(f"❌ {result['test']}: {result.get('error', 'Unknown error')}")
    
    return successful_tests == len(test_cases)

if __name__ == "__main__":
    success = test_comprehensive_scraper()
    print(f"\n{'✓ ALL TESTS PASSED!' if success else '❌ SOME TESTS FAILED!'}")
