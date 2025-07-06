#!/usr/bin/env python3
"""
Debug bedroom extraction specifically
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup
import re

def debug_bedroom_extraction():
    """Debug bedroom extraction from the HTML"""
    
    # Load the saved HTML
    with open('debug_leiden_current.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    
    # Find all headers with bedroom info
    print("=== FINDING HEADERS ===")
    headers = soup.find_all("header", class_="bg-secondary-10")
    for i, header in enumerate(headers, 1):
        header_text = header.get_text(strip=True)
        print(f"Header {i}: {header_text}")
        bedroom_match = re.search(r"(\d+)\s*slaapkamer", header_text, re.IGNORECASE)
        if bedroom_match:
            print(f"  -> Found {bedroom_match.group(1)} bedrooms")
        
    print("\n=== FINDING ADDRESS LINKS ===")
    address_links = soup.find_all("a", attrs={"data-testid": "listingDetailsAddress"})
    for i, link in enumerate(address_links, 1):
        print(f"Address link {i}: {link.get('href')}")
        
        # Try different approaches to find the header
        approaches = [
            # Approach 1: Find previous sibling header
            link.find_previous("header", class_="bg-secondary-10"),
            # Approach 2: Go up levels and look for header
            link.parent.find_previous("header", class_="bg-secondary-10") if link.parent else None,
            link.parent.parent.find_previous("header", class_="bg-secondary-10") if link.parent and link.parent.parent else None,
        ]
        
        for j, header in enumerate(approaches, 1):
            if header:
                header_text = header.get_text(strip=True)
                bedroom_match = re.search(r"(\d+)\s*slaapkamer", header_text, re.IGNORECASE)
                print(f"  Approach {j}: {header_text[:50]}...")
                if bedroom_match:
                    print(f"    -> Found {bedroom_match.group(1)} bedrooms")
                break
        else:
            print("  No header found with any approach")

if __name__ == "__main__":
    debug_bedroom_extraction()
