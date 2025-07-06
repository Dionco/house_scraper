#!/usr/bin/env python3
"""
Performance testing script for the optimized scraping system.
Tests speed improvements and efficiency gains.
"""

import time
import asyncio
import json
import logging
from typing import Dict, List
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_test_profiles() -> List[Dict]:
    """Load test profiles for performance testing"""
    test_profiles = [
        {
            "id": "test_utrecht",
            "name": "Utrecht Test",
            "filters": {
                "city": "Utrecht",
                "min_price": 3000,
                "max_price": 5000,
                "min_area": 50,
                "max_area": 150
            }
        },
        {
            "id": "test_amsterdam",
            "name": "Amsterdam Test", 
            "filters": {
                "city": "Amsterdam",
                "min_price": 2500,
                "max_price": 4500,
                "property_type": "appartement"
            }
        },
        {
            "id": "test_leiden",
            "name": "Leiden Test",
            "filters": {
                "city": "Leiden",
                "min_price": 2000,
                "max_price": 3500,
                "min_bedrooms": 2
            }
        }
    ]
    return test_profiles

def test_single_profile_scraping(profile: Dict) -> Dict:
    """Test scraping a single profile"""
    logger.info(f"Testing single profile scraping: {profile['name']}")
    
    start_time = time.time()
    
    try:
        from funda_url_builder import build_rental_url
        from scrape_funda import scrape_funda_html
        from extract_funda_listings_fast import extract_listings_fast
        
        # Build URL
        url_start = time.time()
        filters = profile['filters']
        url = build_rental_url(
            city=filters.get('city'),
            property_type=filters.get('property_type'),
            min_price=filters.get('min_price'),
            max_price=filters.get('max_price'),
            min_floor_area=filters.get('min_area'),
            max_floor_area=filters.get('max_area'),
            min_bedrooms=filters.get('min_bedrooms'),
            per_page=50
        )
        url_time = time.time() - url_start
        
        # Scrape HTML
        scrape_start = time.time()
        html = scrape_funda_html(url, max_retries=1, timeout=25)
        scrape_time = time.time() - scrape_start
        
        # Extract listings
        extract_start = time.time()
        listings = extract_listings_fast(html) if html else []
        extract_time = time.time() - extract_start
        
        total_time = time.time() - start_time
        
        results = {
            "profile_id": profile['id'],
            "success": True,
            "total_time": total_time,
            "url_build_time": url_time,
            "scrape_time": scrape_time,
            "extract_time": extract_time,
            "listings_found": len(listings),
            "html_size": len(html) if html else 0
        }
        
        logger.info(f"Single scrape completed: {results}")
        return results
        
    except Exception as e:
        logger.error(f"Single scrape failed: {e}")
        return {
            "profile_id": profile['id'],
            "success": False,
            "error": str(e),
            "total_time": time.time() - start_time
        }

async def test_concurrent_scraping(profiles: List[Dict]) -> Dict:
    """Test concurrent scraping of multiple profiles"""
    logger.info(f"Testing concurrent scraping of {len(profiles)} profiles")
    
    start_time = time.time()
    
    try:
        from scrape_funda_async import scrape_profiles_fast
        
        results = await scrape_profiles_fast(profiles)
        
        total_time = time.time() - start_time
        total_listings = sum(len(listings) for listings in results.values())
        
        return {
            "success": True,
            "total_time": total_time,
            "profiles_scraped": len(profiles),
            "total_listings": total_listings,
            "average_time_per_profile": total_time / len(profiles),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Concurrent scraping failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_time": time.time() - start_time
        }

def test_extraction_performance():
    """Test extraction performance comparison"""
    logger.info("Testing extraction performance")
    
    # Load sample HTML file if available
    sample_html_path = Path("funda_uc_debug.html")
    if not sample_html_path.exists():
        logger.warning("No sample HTML file found, skipping extraction performance test")
        return {}
    
    with open(sample_html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Test original extractor
    try:
        from extract_funda_listings import extract_simple_listings_from_html
        
        start_time = time.time()
        original_listings = extract_simple_listings_from_html(html)
        original_time = time.time() - start_time
        
    except Exception as e:
        logger.error(f"Original extractor failed: {e}")
        original_listings = []
        original_time = float('inf')
    
    # Test fast extractor
    try:
        from extract_funda_listings_fast import extract_listings_fast
        
        start_time = time.time()
        fast_listings = extract_listings_fast(html)
        fast_time = time.time() - start_time
        
    except Exception as e:
        logger.error(f"Fast extractor failed: {e}")
        fast_listings = []
        fast_time = float('inf')
    
    results = {
        "html_size": len(html),
        "original_extractor": {
            "time": original_time,
            "listings_found": len(original_listings)
        },
        "fast_extractor": {
            "time": fast_time,
            "listings_found": len(fast_listings)
        },
        "speedup": original_time / fast_time if fast_time > 0 else 0
    }
    
    logger.info(f"Extraction performance: {results}")
    return results

def run_performance_benchmarks():
    """Run comprehensive performance benchmarks"""
    logger.info("Starting performance benchmarks")
    
    results = {
        "timestamp": time.time(),
        "tests": {}
    }
    
    # Load test profiles
    profiles = load_test_profiles()
    
    # Test 1: Single profile scraping
    logger.info("Test 1: Single profile scraping performance")
    single_results = []
    for profile in profiles:
        result = test_single_profile_scraping(profile)
        single_results.append(result)
        time.sleep(2)  # Avoid hitting rate limits
    
    results["tests"]["single_profile_scraping"] = single_results
    
    # Test 2: Concurrent scraping
    logger.info("Test 2: Concurrent scraping performance")
    concurrent_result = asyncio.run(test_concurrent_scraping(profiles))
    results["tests"]["concurrent_scraping"] = concurrent_result
    
    # Test 3: Extraction performance
    logger.info("Test 3: Extraction performance comparison")
    extraction_result = test_extraction_performance()
    results["tests"]["extraction_performance"] = extraction_result
    
    # Calculate summary statistics
    successful_singles = [r for r in single_results if r.get("success")]
    if successful_singles:
        avg_single_time = sum(r["total_time"] for r in successful_singles) / len(successful_singles)
        avg_listings = sum(r["listings_found"] for r in successful_singles) / len(successful_singles)
        
        results["summary"] = {
            "average_single_scrape_time": avg_single_time,
            "average_listings_per_scrape": avg_listings,
            "concurrent_vs_single_speedup": (avg_single_time * len(profiles)) / concurrent_result.get("total_time", float('inf')) if concurrent_result.get("success") else 0,
            "total_profiles_tested": len(profiles),
            "success_rate": len(successful_singles) / len(single_results)
        }
    
    # Save results
    results_file = f"performance_test_results_{int(time.time())}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Performance test completed. Results saved to {results_file}")
    
    # Print summary
    if "summary" in results:
        summary = results["summary"]
        print("\n" + "="*50)
        print("PERFORMANCE TEST SUMMARY")
        print("="*50)
        print(f"Average single scrape time: {summary['average_single_scrape_time']:.2f}s")
        print(f"Average listings per scrape: {summary['average_listings_per_scrape']:.1f}")
        print(f"Concurrent speedup: {summary['concurrent_vs_single_speedup']:.2f}x")
        print(f"Success rate: {summary['success_rate']*100:.1f}%")
        
        if extraction_result:
            print(f"Extraction speedup: {extraction_result.get('speedup', 0):.2f}x")
        
        print("="*50)
    
    return results

if __name__ == "__main__":
    run_performance_benchmarks()
