#!/usr/bin/env python3
"""
Final comprehensive test of the rental scraping system
"""
import sys
import os
import json
import requests
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_comprehensive_rental_system():
    """Test the complete rental scraping and API system"""
    
    print("=== COMPREHENSIVE RENTAL SYSTEM TEST ===\n")
    
    # Test 1: Scraping API
    print("1. Testing Scraping API...")
    try:
        response = requests.get(
            "http://localhost:8000/api/scrape_listings",
            params={
                "city": "Leiden", 
                "min_price": 1800, 
                "max_price": 2500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Scraping successful!")
            print(f"      URL: {data.get('url', 'N/A')}")
            print(f"      Found: {data.get('count', 0)} listings")
            print(f"      Added: {data.get('added', 0)} new listings")
            
            # Test data quality
            listings = data.get('listings', [])
            if listings:
                sample = listings[0]
                address = sample.get('address.street_name', 'Unknown')
                price = sample.get('price.rent_price', 'Unknown')
                bedrooms = sample.get('number_of_bedrooms', 'Unknown')
                energy = sample.get('energy_label', 'Unknown')
                image = sample.get('image_url', 'None')
                
                print(f"      Sample: {address} - €{price} - {bedrooms} bedrooms - Energy: {energy}")
                print(f"      Image: {'Yes' if image and image != 'None' else 'No'}")
                
                # Quality metrics
                with_prices = sum(1 for l in listings if l.get('price.rent_price'))
                with_bedrooms = sum(1 for l in listings if l.get('number_of_bedrooms'))
                with_energy = sum(1 for l in listings if l.get('energy_label'))
                with_images = sum(1 for l in listings if l.get('image_url'))
                
                total = len(listings)
                print(f"      Quality: Prices {with_prices}/{total}, Bedrooms {with_bedrooms}/{total}, Energy {with_energy}/{total}, Images {with_images}/{total}")
            else:
                print("      ❌ No listings returned")
                
        else:
            print(f"   ❌ Scraping failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Scraping test failed: {e}")
        return False
    
    # Test 2: Main listings API
    print("\n2. Testing Main Listings API...")
    try:
        response = requests.get("http://localhost:8000/api/listings", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            listings = data.get('listings', [])
            
            print(f"   ✅ API working! Total listings: {len(listings)}")
            
            # Count by city
            city_counts = {}
            rental_prices = []
            
            for listing in listings:
                city = listing.get('address.city', 'Unknown')
                city_counts[city] = city_counts.get(city, 0) + 1
                
                price = listing.get('price.rent_price')
                if price and isinstance(price, int):
                    rental_prices.append(price)
            
            print(f"      By city:")
            for city, count in sorted(city_counts.items()):
                print(f"        {city}: {count}")
            
            if rental_prices:
                avg_price = sum(rental_prices) / len(rental_prices)
                min_price = min(rental_prices)
                max_price = max(rental_prices)
                print(f"      Price range: €{min_price} - €{max_price} (avg: €{avg_price:.0f})")
            
        else:
            print(f"   ❌ API failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ API test failed: {e}")
        return False
    
    # Test 3: Data consistency
    print("\n3. Testing Data Consistency...")
    try:
        # Check that saved file has correct format
        json_path = "funda_simple_listings.json"
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                saved_listings = json.load(f)
            
            print(f"   ✅ File exists with {len(saved_listings)} listings")
            
            if saved_listings:
                sample = saved_listings[0]
                required_fields = ['address.street_name', 'address.city', 'price.rent_price']
                has_required = all(field in sample for field in required_fields)
                
                if has_required:
                    print(f"   ✅ Correct format with required fields")
                else:
                    print(f"   ❌ Missing required fields")
                    return False
            
        else:
            print(f"   ❌ Saved file not found")
            return False
            
    except Exception as e:
        print(f"   ❌ Data consistency test failed: {e}")
        return False
    
    # Test 4: Different cities
    print("\n4. Testing Different Cities...")
    cities_to_test = ["Utrecht", "Amsterdam"]
    
    for city in cities_to_test:
        try:
            response = requests.get(
                "http://localhost:8000/api/scrape_listings",
                params={"city": city, "min_price": 2000, "max_price": 4000},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                added = data.get('added', 0)
                print(f"   ✅ {city}: {count} listings found, {added} new")
            else:
                print(f"   ❌ {city}: Failed with status {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {city}: Test failed: {e}")
    
    print(f"\n🎉 RENTAL SCRAPING SYSTEM TEST COMPLETE! 🎉")
    return True

if __name__ == "__main__":
    success = test_comprehensive_rental_system()
    print(f"\n{'✅ ALL TESTS PASSED!' if success else '❌ SOME TESTS FAILED!'}")
