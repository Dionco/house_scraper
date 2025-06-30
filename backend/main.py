"""
main.py: Orchestrates the workflow—calls the scraper, passes HTML to the extractor, writes output.
"""

from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html
import json

FUNDALIST_URL = "https://www.funda.nl/huur/utrecht/3000-5000/sorteer-datum-af/"
OUTPUT_JSON = "funda_simple_listings.json"


def main():
    print(f"[INFO] Scraping Funda: {FUNDALIST_URL}")
    html = scrape_funda_html(FUNDALIST_URL)
    print("[INFO] Extracting listings from HTML...")
    listings = extract_simple_listings_from_html(html)


    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Extracted {len(listings)} listings to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()

# This file is not imported by any main code. Move to deprecated/ if not needed.
