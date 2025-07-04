"""
Funda.nl session-based scraper using requests.Session, browser cookies, and CSRF token handling.
- Loads cookies from Selenium/undetected-chromedriver session (cookies.pkl)
- Extracts CSRF token from HTML or cookies
- Sets headers to mimic browser
- Attempts to fetch a Funda page as a logged-in/session user
"""
import requests
import pickle
import os
import re
from bs4 import BeautifulSoup

URL = "https://www.funda.nl/huur/utrecht/1000-2000/sorteer-datum-af/"
COOKIES_FILE = "cookies.pkl"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.funda.nl/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}

def load_cookies(filename):
    if not os.path.exists(filename):
        print(f"[ERROR] Cookie file {filename} not found. Run undetected-chromedriver first.")
        return None
    with open(filename, "rb") as f:
        cookies = pickle.load(f)
    # Convert Selenium cookies to requests format
    return {c['name']: c['value'] for c in cookies}

def extract_csrf_token(html):
    # Try to extract CSRF token from meta tags or hidden inputs
    soup = BeautifulSoup(html, "html.parser")
    # Example: <meta name="csrf-token" content="...">
    meta = soup.find("meta", attrs={"name": re.compile("csrf", re.I)})
    if meta and meta.get("content"):
        return meta["content"]
    # Example: <input type="hidden" name="__RequestVerificationToken" value="...">
    inp = soup.find("input", attrs={"name": re.compile("csrf|verification", re.I)})
    if inp and inp.get("value"):
        return inp["value"]
    return None

def main():
    session = requests.Session()
    session.headers.update(HEADERS)
    cookies = load_cookies(COOKIES_FILE)
    if not cookies:
        return
    session.cookies.update(cookies)
    print("[INFO] Cookies loaded and set in session.")
    # Initial GET to fetch page and CSRF token
    resp = session.get(URL)
    print(f"[INFO] GET {URL} status: {resp.status_code}")
    if resp.status_code != 200:
        print("[WARN] Non-200 response. You may be blocked or need to update cookies.")
    # Try to extract CSRF token
    csrf_token = extract_csrf_token(resp.text)
    if csrf_token:
        print(f"[INFO] CSRF token found: {csrf_token}")
        # Example: set as header or form field for POST requests
        session.headers["X-CSRF-Token"] = csrf_token
    else:
        print("[INFO] No CSRF token found in page.")

    # Save HTML for inspection
    with open("funda_session_debug.html", "w", encoding="utf-8") as f:
        f.write(resp.text)
    print("[INFO] Page HTML saved to funda_session_debug.html")

    # --- Extract listings from HTML ---
    def parse_listings(html):
        """Extract Funda listings from HTML using BeautifulSoup."""
        soup = BeautifulSoup(html, "html.parser")
        listings = []
        for result in soup.select('.search-result'):
            title = result.select_one('.search-result__header-title')
            price = result.select_one('.search-result-price')
            address = result.select_one('.search-result__header-subtitle')
            url = result.select_one('a.search-result__header-title-container')
            image_url = result.select_one('img')
            description = result.select_one('.search-result__description')
            features = [li.get_text(strip=True) for li in result.select('.search-result-kenmerken li')]
            item = {
                'title': title.get_text(strip=True) if title else None,
                'price': price.get_text(strip=True) if price else None,
                'address': address.get_text(strip=True) if address else None,
                'url': url['href'] if url and url.has_attr('href') else None,
                'image_url': image_url['src'] if image_url and image_url.has_attr('src') else None,
                'description': description.get_text(strip=True) if description else None,
                'features': ', '.join(features) if features else None,
            }
            # Fix relative URLs
            if item['url'] and item['url'].startswith('/'):
                item['url'] = 'https://www.funda.nl' + item['url']
            listings.append(item)
        return listings

    def save_listings(listings, filename="session_listings.jsonl"):
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            for item in listings:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"[INFO] Saved {len(listings)} listings to {filename}")

    listings = parse_listings(resp.text)
    print(f"[INFO] Found {len(listings)} listings on the page.")
    for i, item in enumerate(listings, 1):
        print(f"--- Listing {i} ---")
        for k, v in item.items():
            print(f"{k}: {v}")
        print()
    save_listings(listings)

if __name__ == "__main__":
    main()

# This file is not imported by any main code. Move to deprecated/ if not needed.
