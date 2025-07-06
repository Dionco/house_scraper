#!/usr/bin/env python3
"""
Debug script to check what HTML elements we're getting from Funda
"""
import logging
from scrape_funda import scrape_funda_html
from bs4 import BeautifulSoup

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_funda_html():
    """Debug the HTML structure from Funda"""
    # Test URL (Haarlem rentals 3000-5000)
    test_url = "https://www.funda.nl/zoeken/huur/?selected_area=[%22haarlem%22]&price=3000-5000"
    
    print(f"Debugging Funda HTML structure for: {test_url}")
    
    try:
        # Scrape HTML
        html = scrape_funda_html(test_url, max_retries=1, timeout=30)
        
        if html:
            print(f"✓ Successfully scraped {len(html)} characters")
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            
            # Check for common listing selectors
            selectors_to_check = [
                '[data-test-id="search-result-item"]',
                '.search-result',
                '.object-list-item',
                '.search-result-item',
                '[data-test-id="search-result"]',
                '.search-result-content',
                '.search-result-wrapper'
            ]
            
            found_elements = False
            for selector in selectors_to_check:
                try:
                    elements = soup.select(selector)
                    if elements:
                        print(f"✓ Found {len(elements)} elements with selector: {selector}")
                        found_elements = True
                        
                        # Show the first element structure
                        if elements:
                            first_element = elements[0]
                            print(f"  First element classes: {first_element.get('class', [])}")
                            print(f"  First element attributes: {list(first_element.attrs.keys())}")
                            
                            # Look for title or link
                            title_elem = first_element.find(['h2', 'h3', 'a'])
                            if title_elem:
                                print(f"  Title/Link found: {title_elem.get_text(strip=True)[:100]}...")
                    else:
                        print(f"✗ No elements found with selector: {selector}")
                except Exception as e:
                    print(f"✗ Error checking selector {selector}: {e}")
            
            if not found_elements:
                print("\n✗ No listing elements found with any selector")
                # Check if we have any content at all
                body = soup.find('body')
                if body:
                    print(f"  Body content length: {len(body.get_text(strip=True))}")
                    print(f"  Body classes: {body.get('class', [])}")
                    
                    # Check for any search-related content
                    search_elements = soup.find_all(text=lambda text: text and ('zoek' in text.lower() or 'huur' in text.lower()))
                    if search_elements:
                        print(f"  Found {len(search_elements)} search-related text elements")
                    
                    # Check for pagination or result count
                    result_elements = soup.find_all(text=lambda text: text and ('result' in text.lower() or 'gevonden' in text.lower()))
                    if result_elements:
                        print(f"  Found {len(result_elements)} result-related text elements")
                        for elem in result_elements[:3]:  # Show first 3
                            print(f"    - {elem.strip()}")
                else:
                    print("  No body element found")
                    
        else:
            print("✗ Failed to scrape HTML")
            
    except Exception as e:
        print(f"✗ Error during debugging: {e}")

if __name__ == "__main__":
    debug_funda_html()
