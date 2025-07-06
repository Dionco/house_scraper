#!/usr/bin/env python3
"""
Debug script to understand rental listing structure and improve extraction
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrape_funda import scrape_funda_html
from bs4 import BeautifulSoup
import re

def debug_rental_structure():
    """Debug the structure of rental listings"""
    
    # Scrape fresh rental data
    url = "https://www.funda.nl/zoeken/huur/?selected_area=[%22leiden%22]"
    print(f"Scraping rental URL: {url}")
    
    html = scrape_funda_html(url, max_retries=1)
    
    if not html:
        print("❌ Failed to scrape HTML")
        return
    
    print(f"✓ Successfully scraped {len(html)} characters")
    
    # Save HTML for debugging
    with open('debug_rental_structure.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("✓ Saved HTML to debug_rental_structure.html")
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find rental listings
    address_links = soup.find_all("a", attrs={"data-testid": "listingDetailsAddress"})
    print(f"Found {len(address_links)} rental address links")
    
    for i, address_link in enumerate(address_links[:3], 1):  # Debug first 3 rental listings
        print(f"\n--- Rental Listing {i} ---")
        
        # Extract address
        address_span = address_link.find("span", class_="truncate")
        address = address_span.get_text(strip=True) if address_span else "Unknown"
        print(f"Address: {address}")
        
        # Find the parent container
        parent = address_link.parent
        while parent and parent.name != "div":
            parent = parent.parent
        
        if parent:
            # Go up to find the listing card container
            card = parent
            while card and not (card.name == "div" and card.find("h2")):
                card = card.parent
                
            if card:
                print("✓ Found listing card")
                
                # Look for all images
                images = card.find_all("img")
                print(f"Found {len(images)} images in card")
                for j, img in enumerate(images, 1):
                    src = img.get("src")
                    alt = img.get("alt", "")
                    print(f"  Image {j}: {src[:80]}... (alt: {alt})")
                
                # Look for energy labels in various places
                energy_labels = []
                
                # Check all text content for energy labels
                all_text = card.get_text()
                energy_matches = re.findall(r'\b[A-G]\b', all_text)
                if energy_matches:
                    print(f"Potential energy labels in text: {energy_matches}")
                
                # Check specifically for energy label spans/divs
                for el in card.find_all(["span", "div", "li"]):
                    text = el.get_text(strip=True)
                    if len(text) == 1 and text.upper() in "ABCDEFG":
                        # Check if this looks like an energy label
                        classes = el.get("class", [])
                        parent_classes = el.parent.get("class", []) if el.parent else []
                        print(f"  Possible energy label '{text}' with classes: {classes}, parent classes: {parent_classes}")
                        energy_labels.append(text)
                
                # Look for price information
                price_divs = card.find_all("div", class_="font-semibold")
                print(f"Found {len(price_divs)} price divs")
                for j, price_div in enumerate(price_divs, 1):
                    price_text = price_div.get_text(strip=True)
                    print(f"  Price div {j}: {price_text}")
                
                # Look for characteristics
                characteristics = []
                for li in card.find_all("li"):
                    text = li.get_text(strip=True)
                    if text:
                        characteristics.append(text)
                
                print(f"Characteristics: {characteristics}")
                
                # Look for header info
                header = address_link.find_previous("header", class_="bg-secondary-10")
                if header:
                    header_text = header.get_text(strip=True)
                    print(f"Header: {header_text}")
                else:
                    print("No header found")
                
                print("-" * 60)

if __name__ == "__main__":
    debug_rental_structure()
