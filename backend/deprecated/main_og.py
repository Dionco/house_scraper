from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# Allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Scrape funda.nl for new listings (example: Amsterdam, for sale)


from fastapi import HTTPException
import logging
import time
import re
from urllib.parse import urljoin
from dataclasses import dataclass
from typing import List, Optional

# Playwright import
try:
    from playwright.sync_api import sync_playwright
    print("Playwright is installed. Using it for advanced scraping.")
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    print("Playwright is not installed. Some features may not work.")
    PLAYWRIGHT_AVAILABLE = False

# Custom exceptions for different failure modes
class FundaNetworkError(Exception):
    pass

class FundaPageStructureError(Exception):
    pass

class FundaNoListingsError(Exception):
    pass


# --- Advanced FundaListing dataclass and FundaSearchScraper ---
@dataclass
class FundaListing:
    """Data class to store property listing information"""
    url: str
    title: str
    price: str
    address: str
    area: Optional[str] = None
    rooms: Optional[str] = None
    living_area: Optional[str] = None
    lot_size: Optional[str] = None
    year_built: Optional[str] = None
    listing_type: Optional[str] = None  # koop/huur
    agent: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None

class FundaSearchScraper:
    """Scraper for Funda search results"""
    def __init__(self, delay_between_requests=1):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.delay = delay_between_requests
        self.base_url = 'https://www.funda.nl'

    def get_search_results(self, search_url: str, max_pages: int = 1) -> List[FundaListing]:
        all_listings = []
        current_page = 1
        max_retries = 5
        while current_page <= max_pages:
            # Construct page URL
            if current_page == 1:
                page_url = search_url
            else:
                separator = '&' if '?' in search_url else '?'
                page_url = f"{search_url}{separator}search_result={current_page}"
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = self.session.get(page_url, timeout=10)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Check for Funda's anti-bot/interstitial page
                    page_text = soup.get_text(separator=' ', strip=True).lower()
                    if (
                        'je bent bijna op de pagina' in page_text or
                        'almost at the page' in page_text or
                        'controleer hieronder' in page_text or
                        'check below' in page_text
                    ):
                        logging.warning(f"Funda interstitial/anti-bot page detected. Waiting and retrying... (attempt {retry_count+1})")
                        time.sleep(3 + retry_count * 2)
                        retry_count += 1
                        continue
                    # If we get here, it's a real page
                    break
                except Exception as e:
                    logging.error(f"Error scraping page {current_page} (attempt {retry_count+1}): {e}")
                    time.sleep(2)
                    retry_count += 1
            else:
                logging.error(f"Failed to get a real Funda page after {max_retries} retries. Giving up on this page.")
                break
            page_listings = self._extract_listings_from_page(soup)
            if not page_listings:
                break
            all_listings.extend(page_listings)
            if not self._has_next_page(soup):
                break
            current_page += 1
            time.sleep(self.delay)
        return all_listings

    def _extract_listings_from_page(self, soup: BeautifulSoup) -> List[FundaListing]:
        listings = []
        listing_selectors = [
            'div[data-test="search-result-item"]',
            'div.search-result-item',
            'div.search-result',
            'article.search-result',
            'div[class*="search-result"]'
        ]
        listing_elements = []
        for selector in listing_selectors:
            listing_elements = soup.select(selector)
            logging.info(f"Selector '{selector}' found {len(listing_elements)} elements.")
            if listing_elements:
                break
        if not listing_elements:
            logging.warning("No listing elements found with main selectors. Trying fallback link search.")
            links = soup.find_all('a', href=re.compile(r'/(koop|huur)/[^/]+/(huis|appartement|woning)'))
            listing_elements = [link.find_parent() for link in links if link.find_parent()]
            logging.info(f"Fallback link search found {len(listing_elements)} elements.")
            if not listing_elements:
                # Log a snippet of the HTML for debugging
                html_snippet = soup.prettify()[:1500]
                logging.warning(f"No listings found. HTML snippet: {html_snippet}")
        for element in listing_elements:
            try:
                listing = self._extract_listing_data(element, soup)
                if listing and self._is_valid_listing(listing):
                    listings.append(listing)
            except Exception as e:
                logging.warning(f"Error extracting listing data: {e}")
                continue
        return listings

    def _extract_listing_data(self, element: BeautifulSoup, full_soup: BeautifulSoup) -> Optional[FundaListing]:
        url = self._extract_url(element)
        if not url:
            return None
        title = self._extract_title(element)
        price = self._extract_price(element)
        address = self._extract_address(element)
        area = self._extract_area(element)
        rooms = self._extract_rooms(element)
        living_area = self._extract_living_area(element)
        lot_size = self._extract_lot_size(element)
        year_built = self._extract_year_built(element)
        listing_type = self._extract_listing_type(element, url)
        agent = self._extract_agent(element)
        image_url = self._extract_image_url(element)
        description = self._extract_description(element)
        return FundaListing(
            url=url,
            title=title,
            price=price,
            address=address,
            area=area,
            rooms=rooms,
            living_area=living_area,
            lot_size=lot_size,
            year_built=year_built,
            listing_type=listing_type,
            agent=agent,
            image_url=image_url,
            description=description
        )

    def _extract_url(self, element: BeautifulSoup) -> Optional[str]:
        link_patterns = [
            r'/(koop|huur)/[^/]+/(huis|appartement|woning)-\d+',
            r'/(koop|huur)/[^/]+/\d+'
        ]
        for pattern in link_patterns:
            link = element.find('a', href=re.compile(pattern))
            if link:
                href = link.get('href')
                if href:
                    return urljoin(self.base_url, href)
        return None

    def _extract_title(self, element: BeautifulSoup) -> str:
        title_selectors = [
            'h2',
            'h3',
            '.search-result-title',
            '[data-test="street-name-house-number"]',
            'a[href*="/koop/"], a[href*="/huur/"]'
        ]
        for selector in title_selectors:
            title_element = element.select_one(selector)
            if title_element:
                return title_element.get_text(strip=True)
        return "No title found"

    def _extract_price(self, element: BeautifulSoup) -> str:
        price_selectors = [
            '[data-test="price-sale"]',
            '[data-test="price-rent"]',
            '.search-result-price',
            '.price'
        ]
        for selector in price_selectors:
            price_element = element.select_one(selector)
            if price_element:
                return price_element.get_text(strip=True)
        price_text = element.find(string=re.compile(r'€\s*[\d.,]+'))
        if price_text:
            return price_text.strip()
        return "Price not found"

    def _extract_address(self, element: BeautifulSoup) -> str:
        address_selectors = [
            '[data-test="street-name-house-number"]',
            '.search-result-address',
            '.address'
        ]
        for selector in address_selectors:
            address_element = element.select_one(selector)
            if address_element:
                return address_element.get_text(strip=True)
        return "Address not found"

    def _extract_area(self, element: BeautifulSoup) -> Optional[str]:
        area_text = element.find(string=re.compile(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*'))
        return area_text.strip() if area_text else None

    def _extract_rooms(self, element: BeautifulSoup) -> Optional[str]:
        rooms_text = element.find(string=re.compile(r'\d+\s*kamers?'))
        return rooms_text.strip() if rooms_text else None

    def _extract_living_area(self, element: BeautifulSoup) -> Optional[str]:
        area_text = element.find(string=re.compile(r'\d+\s*m²'))
        return area_text.strip() if area_text else None

    def _extract_lot_size(self, element: BeautifulSoup) -> Optional[str]:
        lot_text = element.find(string=re.compile(r'perceel\s*\d+\s*m²'))
        return lot_text.strip() if lot_text else None

    def _extract_year_built(self, element: BeautifulSoup) -> Optional[str]:
        year_text = element.find(string=re.compile(r'(19|20)\d{2}'))
        return year_text.strip() if year_text else None

    def _extract_listing_type(self, element: BeautifulSoup, url: str) -> Optional[str]:
        if '/koop/' in url:
            return 'koop'
        elif '/huur/' in url:
            return 'huur'
        return None

    def _extract_agent(self, element: BeautifulSoup) -> Optional[str]:
        agent_selectors = [
            '.search-result-makelaar',
            '.makelaar',
            '[data-test="agent-name"]'
        ]
        for selector in agent_selectors:
            agent_element = element.select_one(selector)
            if agent_element:
                return agent_element.get_text(strip=True)
        return None

    def _extract_image_url(self, element: BeautifulSoup) -> Optional[str]:
        img = element.find('img')
        if img and img.get('src'):
            return urljoin(self.base_url, img.get('src'))
        return None

    def _extract_description(self, element: BeautifulSoup) -> Optional[str]:
        desc_selectors = [
            '.search-result-description',
            '.description',
            '[data-test="description"]'
        ]
        for selector in desc_selectors:
            desc_element = element.select_one(selector)
            if desc_element:
                return desc_element.get_text(strip=True)
        return None

    def _is_valid_listing(self, listing: FundaListing) -> bool:
        return (
            listing.url and 
            (listing.title != "No title found" or listing.address != "Address not found") and
            listing.price != "Price not found"
        )

    def _has_next_page(self, soup: BeautifulSoup) -> bool:
        next_selectors = [
            'a[rel="next"]',
            'a[aria-label="Volgende"]',
            '.pagination-next',
            '.next-page'
        ]
        for selector in next_selectors:
            if soup.select_one(selector):
                return True
        return False

class FundaPlaywrightScraper:
    def __init__(self):
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright is not installed. Run 'pip install playwright' and 'playwright install'.")
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )
        self.context = self.browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='nl-NL'
        )
        self.page = self.context.new_page()

    def scrape_funda_search(self, search_url):
        try:
            logging.info(f"[Playwright] Navigating to {search_url}")
            self.page.goto(search_url, timeout=30000)
            time.sleep(4)
            # Wait for anti-bot to clear if present
            for _ in range(3):
                if self._check_anti_bot():
                    logging.warning("[Playwright] Anti-bot detected, waiting...")
                    time.sleep(10)
                    self.page.reload()
                    time.sleep(5)
                else:
                    break
            # Wait for search results
            self.page.wait_for_selector('[data-test="search-result-item"], .search-result', timeout=20000)
            # Extract listings
            listings = self.page.evaluate('''
                () => {
                    const listings = [];
                    const elements = document.querySelectorAll('[data-test="search-result-item"], .search-result');
                    elements.forEach(element => {
                        try {
                            const titleEl = element.querySelector('h2, h3, .search-result-title');
                            const priceEl = element.querySelector('[data-test="price-sale"], [data-test="price-rent"], .price');
                            const linkEl = element.querySelector('a[href*="/koop/"], a[href*="/huur/"]');
                            if (titleEl && priceEl && linkEl) {
                                listings.push({
                                    title: titleEl.textContent.trim(),
                                    price: priceEl.textContent.trim(),
                                    url: linkEl.href
                                });
                            }
                        } catch (e) {}
                    });
                    return listings;
                }
            ''')
            return listings
        except Exception as e:
            logging.error(f"[Playwright] Error: {e}")
            return []

    def _check_anti_bot(self):
        page_content = self.page.content().lower()
        return any(indicator in page_content for indicator in [
            'je bent bijna op de pagina', 'checking your browser', 'cloudflare', 'just a moment', 'controleer hieronder', 'check below'
        ])

    def close(self):
        self.browser.close()
        self.playwright.stop()

def build_funda_url(
    city: str = "Leiden",
    min_price: int = None,
    max_price: int = None,
    min_rooms: int = None,
    max_rooms: int = None,
    min_area: int = None,
    max_area: int = None,
    property_type: str = None,  # e.g. 'appartement', 'huis'
    construction_year_from: int = None,
    construction_year_to: int = None
):
    city = city.lower().replace(" ", "-")
    price_segment = ""
    if (min_price is not None and min_price > 0) or (max_price is not None and max_price > 0):
        min_str = str(min_price) if min_price is not None and min_price > 0 else ""
        max_str = str(max_price) if max_price is not None and max_price > 0 else ""
        price_segment = f"/{min_str}-{max_str}" if min_str or max_str else ""
    rooms_segment = ""
    if (min_rooms is not None and min_rooms > 0) or (max_rooms is not None and max_rooms > 0):
        min_r = str(min_rooms) if min_rooms is not None and min_rooms > 0 else ""
        max_r = str(max_rooms) if max_rooms is not None and max_rooms > 0 else ""
        if min_r and not max_r:
            rooms_segment = f"/{min_r}-kamers"
        elif min_r or max_r:
            rooms_segment = f"/{min_r}-{max_r}-kamers"
    area_segment = ""
    if (min_area is not None and min_area > 0) or (max_area is not None and max_area > 0):
        min_a = str(min_area) if min_area is not None and min_area > 0 else ""
        max_a = str(max_area) if max_area is not None and max_area > 0 else ""
        if min_a and not max_a:
            area_segment = f"/{min_a}-woonopp"
        elif min_a or max_a:
            area_segment = f"/{min_a}-{max_a}-woonopp"
    valid_types = ["appartement", "huis", "eengezinswoning", "hoekwoning", "tussenwoning", "vrijstaande-woning", "2-onder-1-kapwoning"]
    type_segment = f"/{property_type}" if property_type in valid_types and property_type else ""
    year_segment = ""
    if (construction_year_from and construction_year_from > 1800) or (construction_year_to and construction_year_to > 1800):
        from_str = str(construction_year_from) if construction_year_from and construction_year_from > 1800 else ""
        to_str = str(construction_year_to) if construction_year_to and construction_year_to > 1800 else ""
        if from_str and not to_str:
            year_segment = f"/{from_str}-bouwjaar"
        elif from_str or to_str:
            year_segment = f"/{from_str}-{to_str}-bouwjaar"
    url = f"https://www.funda.nl/koop/{city}{price_segment}{rooms_segment}{area_segment}{type_segment}{year_segment}/"
    logging.info(f"Constructed Funda URL: {url}")
    return url

def scrape_funda(
    city: str = "Leiden",
    min_price: int = None,
    max_price: int = None,
    min_rooms: int = None,
    max_rooms: int = None,
    min_area: int = None,
    max_area: int = None,
    property_type: str = None,  # e.g. 'appartement', 'huis'
    construction_year_from: int = None,
    construction_year_to: int = None
):
    used_url = build_funda_url(city, min_price, max_price, min_rooms, max_rooms, min_area, max_area, property_type, construction_year_from, construction_year_to)
    scraper = FundaSearchScraper(delay_between_requests=1)
    try:
        listings = scraper.get_search_results(used_url, max_pages=1)
    except Exception as e:
        logging.error(f"Error scraping Funda: {e}")
        raise FundaNetworkError(f"Failed to fetch listings from Funda. URL: {used_url}")
    if not listings:
        raise FundaNoListingsError(f"No valid listings found on Funda. URL: {used_url}")
    # Convert dataclass objects to dicts for API response
    listings_dicts = [l.__dict__ for l in listings]
    return {"used_url": used_url, "listings": listings_dicts, "num_results": len(listings_dicts)}

from fastapi import Query


@app.get("/listings")
def get_listings(
    city: str = Query("Leiden", description="City to search for listings"),
    min_price: int = Query(None, description="Minimum price in euros"),
    max_price: int = Query(None, description="Maximum price in euros"),
    min_rooms: int = Query(None, description="Minimum number of rooms"),
    max_rooms: int = Query(None, description="Maximum number of rooms"),
    min_area: int = Query(None, description="Minimum living area in m²"),
    max_area: int = Query(None, description="Maximum living area in m²"),
    property_type: str = Query(None, description="Property type, e.g. 'appartement', 'huis'"),
    construction_year_from: int = Query(None, description="Earliest construction year"),
    construction_year_to: int = Query(None, description="Latest construction year")
):
    try:
        result = scrape_funda(
            city, min_price, max_price, min_rooms, max_rooms, min_area, max_area, property_type, construction_year_from, construction_year_to
        )
        return result
    except FundaNetworkError as e:
        return {"used_url": None, "error": str(e)}
    except FundaPageStructureError as e:
        return {"used_url": None, "error": str(e)}
    except FundaNoListingsError as e:
        return {"used_url": None, "error": str(e)}
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"used_url": None, "error": "Unexpected error occurred."}

@app.get("/")
def root():
    return {"message": "House Scraper API is running!"}

@app.get("/listings_playwright")
def get_listings_playwright(
    city: str = Query("Leiden", description="City to search for listings"),
    min_price: int = Query(None, description="Minimum price in euros"),
    max_price: int = Query(None, description="Maximum price in euros"),
    min_rooms: int = Query(None, description="Minimum number of rooms"),
    max_rooms: int = Query(None, description="Maximum number of rooms"),
    min_area: int = Query(None, description="Minimum living area in m²"),
    max_area: int = Query(None, description="Maximum living area in m²"),
    property_type: str = Query(None, description="Property type, e.g. 'appartement', 'huis'"),
    construction_year_from: int = Query(None, description="Earliest construction year"),
    construction_year_to: int = Query(None, description="Latest construction year")
):
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "Playwright is not installed. Run 'pip install playwright' and 'playwright install'."}
    search_url = build_funda_url(city, min_price, max_price, min_rooms, max_rooms, min_area, max_area, property_type, construction_year_from, construction_year_to)
    scraper = FundaPlaywrightScraper()
    try:
        raw_listings = scraper.scrape_funda_search(search_url)
        # Convert to API format (simulate FundaListing fields)
        listings = []
        for i, l in enumerate(raw_listings):
            listings.append({
                "id": i+1,
                "title": l.get("title", ""),
                "price": l.get("price", ""),
                "url": l.get("url", "")
            })
        return {"used_url": search_url, "listings": listings, "num_results": len(listings)}
    finally:
        scraper.close()
