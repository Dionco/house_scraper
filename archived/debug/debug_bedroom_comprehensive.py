#!/usr/bin/env python3
"""
Debug script to understand bedroom extraction issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
import re

def debug_bedroom_extraction():
    """Debug bedroom extraction from the saved HTML"""
    
    # Read the saved HTML
    with open('debug_leiden_current.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    print("=== DEBUGGING BEDROOM EXTRACTION ===\n")
    
    # Find all address links
    address_links = soup.find_all("a", attrs={"data-testid": "listingDetailsAddress"})
    print(f"Found {len(address_links)} address links")
    
    for i, address_link in enumerate(address_links[:5], 1):  # Debug first 5 listings
        print(f"\n--- Listing {i} ---")
        
        # Extract address
        address_span = address_link.find("span", class_="truncate")
        address = address_span.get_text(strip=True) if address_span else "Unknown"
        print(f"Address: {address}")
        
        # Try to find header
        header = address_link.find_previous("header", class_="bg-secondary-10")
        if header:
            header_text = header.get_text(strip=True)
            print(f"Header text: {header_text}")
            
            # Test different bedroom patterns
            patterns = [
                r"(\d+)\s*slaapkamers?",  # 2 slaapkamers
                r"(\d+)\s*slk",           # 2 slk
                r"(\d+)\s*bedroom",       # 2 bedroom
                r"(\d+)\s*kamer",         # 2 kamer
            ]
            
            found_bedrooms = False
            for pattern in patterns:
                match = re.search(pattern, header_text, re.IGNORECASE)
                if match:
                    bedrooms = match.group(1)
                    print(f"Found bedrooms with pattern '{pattern}': {bedrooms}")
                    found_bedrooms = True
                    break
            
            if not found_bedrooms:
                print("No bedroom pattern matched")
        else:
            print("No header found")
            
        # Also check if there are any characteristics in the listing card
        parent = address_link.parent
        while parent and parent.name != "div":
            parent = parent.parent
        
        if parent:
            card = parent
            while card and not (card.name == "div" and card.find("h2")):
                card = card.parent
                
            if card:
                # Look for bedroom info in characteristics
                characteristics = []
                for li in card.find_all("li"):
                    text = li.get_text(strip=True)
                    if text:
                        characteristics.append(text)
                
                if characteristics:
                    print(f"Characteristics: {characteristics}")
                    
                    # Check if any characteristic contains bedroom info
                    for char in characteristics:
                        if re.search(r"\d+.*slaapkamer", char, re.IGNORECASE):
                            print(f"Found bedroom info in characteristics: {char}")
                else:
                    print("No characteristics found")
    
    print("\n=== HEADER ANALYSIS ===")
    
    # Find all headers and their text
    headers = soup.find_all("header", class_="bg-secondary-10")
    print(f"Found {len(headers)} headers")
    
    for i, header in enumerate(headers[:10], 1):
        header_text = header.get_text(strip=True)
        print(f"Header {i}: {header_text}")
        
        # Check for bedroom patterns
        bedroom_match = re.search(r"(\d+)\s*slaapkamers?", header_text, re.IGNORECASE)
        if bedroom_match:
            print(f"  -> Bedrooms: {bedroom_match.group(1)}")
        else:
            print(f"  -> No bedrooms found")

if __name__ == "__main__":
    debug_bedroom_extraction()
