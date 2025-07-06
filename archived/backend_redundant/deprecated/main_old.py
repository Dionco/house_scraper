
#!/usr/bin/env python3
"""
Funda Scraper - Monitor new housing listings on Funda.nl
Based on the implementation from kortus.nl
"""
# --- Ensure correct Twisted reactor for Scrapy/asyncio compatibility ---
import sys
if sys.platform == "darwin":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
from twisted.internet import asyncioreactor
asyncioreactor.install()

print("[DEBUG] Starting Funda Scraper...")
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
from urllib.parse import urlencode
import re
import schedule
import time
import logging
import os
import json
import requests
import webbrowser
from datetime import datetime
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner

# ============================================================================
# ITEMS DEFINITION
# ============================================================================

# Define the item to store scraped data
class FundaListing(scrapy.Item):
    title = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    address = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    image_url = scrapy.Field(output_processor=TakeFirst())
    description = scrapy.Field(output_processor=TakeFirst())
    features = scrapy.Field(output_processor=Join(", "))

# Item loader for Funda listings
class FundaLoader(ItemLoader):
    default_item_class = FundaListing
    default_output_processor = TakeFirst()

# ============================================================================
# SPIDER DEFINITION
# ============================================================================

# Scrapy spider for Funda.nl
class FundaSpider(scrapy.Spider):
    name = "funda"
    allowed_domains = ["funda.nl"]


    def __init__(self, start_urls=None, search_params=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("[DEBUG] FundaSpider __init__ called", flush=True)
        # Use start_urls if provided, else build from search_params
        if start_urls:
            self.start_urls = start_urls
            print(f"[DEBUG] FundaSpider will search: {self.start_urls}", flush=True)
        else:
            self.search_params = search_params or {}
            self.start_urls = [self.build_search_url(self.search_params)]
            print(f"[DEBUG] FundaSpider will search: {self.start_urls}", flush=True)

    def start_requests(self):
        print(f"[DEBUG] FundaSpider start_requests called with start_urls: {self.start_urls}", flush=True)
        # ...existing code...
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "nl-NL,nl;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        cookies = {
            # Place your cookies here if needed for Playwright parity
        }
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, headers=headers, cookies=cookies)

    def build_search_url(self, params):
        base_url = "https://www.funda.nl/zoeken/huur"
        query = urlencode(params)
        return f"{base_url}/?{query}"

    def parse(self, response):
        print(f"[DEBUG] Parsing: {response.url}", flush=True)
        print(f"[DEBUG] Response status: {response.status}", flush=True)
        print(f"[DEBUG] Response body (first 500 chars): {response.text[:500]}", flush=True)
        listings = response.css(".search-result")
        print(f"[DEBUG] Found {len(listings)} .search-result elements", flush=True)
        for listing in listings:
            loader = FundaLoader(selector=listing)
            loader.add_css('title', '.search-result__header-title::text')
            loader.add_css('price', '.search-result-price::text')
            loader.add_css('address', '.search-result__header-subtitle::text')
            loader.add_css('url', 'a.search-result__header-title-container::attr(href)')
            loader.add_css('image_url', 'img::attr(src)')
            loader.add_css('description', '.search-result__description::text')
            loader.add_css('features', '.search-result-kenmerken li::text')
            item = loader.load_item()
            # Fix relative URLs
            if item.get('url') and item['url'].startswith('/'):
                item['url'] = response.urljoin(item['url'])
            # Save each listing in the same format as the current workflow
            save_new_listing(dict(item), Config.DATABASE)
            yield item

        # Pagination
        next_page = response.css('a.pagination-next::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)

# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration settings for the scraper"""
    
    # Scraper behavior
    ONE_LOOP = False  # Set to True to run only once
    OPEN_LINKS = True  # Open new listings in browser
    SEND_NOTIFICATION = False  # Send push notifications (requires PushBullet token)
    
    # File paths
    DATABASE = "listing_database.jsonl"
    
    # URLs to monitor (sorted by newest first)
    URL_LIST = [
        # 'https://www.funda.nl/koop/heel-nederland/0-400000/sorteer-datum-af/',
        # Add more URLs as needed:
        # 'https://www.funda.nl/koop/amsterdam/200000-500000/sorteer-datum-af/',
        'https://www.funda.nl/huur/utrecht/1000-2000/sorteer-datum-af/',
    ]
    
    # PushBullet token for notifications (get from https://www.pushbullet.com/#settings/account)
    PUSHBULLET_TOKEN = ""  # Add your token here if using notifications
    
    # Scraping interval (minutes)
    CHECK_INTERVAL = 15

# ============================================================================
# NOTIFICATION SYSTEM
# ============================================================================

def pushbullet_notification(title, body, token):
    """Send push notification via PushBullet"""
    if not token:
        print("No PushBullet token provided - skipping notification")
        return
    
    msg = {"type": "note", "title": title, "body": body}
    
    try:
        resp = requests.post(
            'https://api.pushbullet.com/v2/pushes',
            data=json.dumps(msg),
            headers={
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            }
        )
        
        if resp.status_code != 200:
            print(f'Notification error: {resp.status_code}')
        else:
            print('Notification sent!')
    except Exception as e:
        print(f'Failed to send notification: {e}')

# ============================================================================
# DATABASE MANAGEMENT
# ============================================================================

def load_existing_listings(database_file):
    """Load existing listings from database file"""
    if not os.path.exists(database_file):
        return set()
    
    existing_urls = set()
    try:
        with open(database_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    listing = json.loads(line)
                    if 'url' in listing and listing['url']:
                        existing_urls.add(listing['url'])
    except Exception as e:
        print(f"Error loading database: {e}")
    
    return existing_urls

def save_new_listing(listing, database_file):
    """Save new listing to database file"""
    try:
        with open(database_file, 'a', encoding='utf-8') as f:
            json.dump(listing, f, ensure_ascii=False)
            f.write('\n')
    except Exception as e:
        print(f"Error saving listing: {e}")

# ============================================================================
# MAIN SCRAPING LOGIC
# ============================================================================

@defer.inlineCallbacks
def run_spider_async(urls):
    """Run spider asynchronously and return results"""
    print("[DEBUG] run_spider_async called", flush=True)
    process = CrawlerRunner()
    
    # Store results
    results = []
    
    def collect_items(item, response, spider):
        print(f"[DEBUG] run_spider_async: item scraped: {item}", flush=True)
        results.append(dict(item))
    
    # Connect signal to collect items
    from scrapy import signals
    crawler = process.create_crawler(FundaSpider)
    crawler.signals.connect(collect_items, signal=signals.item_scraped)
    
    # Run spider
    print("[DEBUG] run_spider_async: about to yield process.crawl", flush=True)
    yield process.crawl(FundaSpider, start_urls=urls)
    print("[DEBUG] run_spider_async: crawl finished", flush=True)
    defer.returnValue(results)

def periodic_checker():
    """Main function that runs periodically to check for new listings"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new listings...", flush=True)
    print(f"[DEBUG] URLs being searched: {Config.URL_LIST}", flush=True)
    
    # Load existing listings
    existing_urls = load_existing_listings(Config.DATABASE)
    print(f"Loaded {len(existing_urls)} existing listings from database")
    
    # Run spider
    print("[DEBUG] periodic_checker: creating CrawlerRunner", flush=True)
    from scrapy.utils.project import get_project_settings
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'funda-scraper (+http://www.yourdomain.com)',
        'ROBOTSTXT_OBEY': False,  # Disable robots.txt for debugging
        'DOWNLOAD_DELAY': 3,  # Be respectful - 3 second delay between requests
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 1,  # Only one request at a time
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'LOG_LEVEL': 'DEBUG',  # Show all Scrapy logs
    })
    runner = CrawlerRunner(settings)
    

    @defer.inlineCallbacks
    def crawl():
        print("[DEBUG] periodic_checker.crawl: called", flush=True)
        results = []

        def collect_items(item, response, spider):
            print(f"[DEBUG] periodic_checker.crawl: item scraped: {item}", flush=True)
            results.append(dict(item))

        from scrapy import signals
        crawler = runner.create_crawler(FundaSpider)
        crawler.signals.connect(collect_items, signal=signals.item_scraped)

        print(f"[DEBUG] About to crawl with start_urls: {Config.URL_LIST}", flush=True)
        crawl_result = yield runner.crawl(FundaSpider, start_urls=Config.URL_LIST)
        print(f"[DEBUG] Crawl finished. crawl_result: {crawl_result}", flush=True)

        # Process results
        new_listings_found = 0

        for listing in results:
            if listing.get('url') and listing['url'] not in existing_urls:
                new_listings_found += 1
                print(f"\n🏠 NEW LISTING FOUND!")
                print(f"   Address: {listing.get('street_name', 'N/A')}")
                print(f"   Postal Code: {listing.get('postal_code', 'N/A')}")
                print(f"   Price: €{listing.get('price', 'N/A')}")
                print(f"   Living Space: {listing.get('living_space', 'N/A')} m²")
                print(f"   Rooms: {listing.get('nr_of_rooms', 'N/A')}")
                print(f"   URL: {listing.get('url', 'N/A')}")

                # Save to database
                save_new_listing(listing, Config.DATABASE)

                # Send notification
                if Config.SEND_NOTIFICATION:
                    title = "New Funda Listing!"
                    body = f"{listing.get('street_name', 'N/A')} - €{listing.get('price', 'N/A')}"
                    pushbullet_notification(title, body, Config.PUSHBULLET_TOKEN)

                # Open in browser
                if Config.OPEN_LINKS and listing.get('url'):
                    try:
                        webbrowser.open(listing['url'])
                    except Exception as e:
                        print(f"Could not open browser: {e}")

        if new_listings_found == 0:
            print("No new listings found")
        else:
            print(f"\nFound {new_listings_found} new listing(s)!")

        # Stop reactor if ONE_LOOP is True
        if Config.ONE_LOOP:
            reactor.stop()

    d = crawl()
    return d

# ============================================================================
# SCHEDULER AND MAIN EXECUTION
# ============================================================================

def run_scheduler():
    print("[DEBUG] Entered run_scheduler()")
    """Run the scheduler for periodic checking"""
    print("🕷️  Funda Scraper Started!")
    print(f"Monitoring {len(Config.URL_LIST)} URL(s)")
    print(f"Check interval: {Config.CHECK_INTERVAL} minutes")
    print(f"Database: {Config.DATABASE}")
    print(f"Notifications: {'ON' if Config.SEND_NOTIFICATION else 'OFF'}")
    print(f"Auto-open links: {'ON' if Config.OPEN_LINKS else 'OFF'}")
    print("-" * 50)
    
    if Config.ONE_LOOP:
        print("[DEBUG] Running once...")
        periodic_checker()
    else:
        print("[DEBUG] Setting up periodic checks and scheduler thread...")
        # Schedule periodic checks
        schedule.every(Config.CHECK_INTERVAL).minutes.do(lambda: reactor.callFromThread(periodic_checker))
        
        # Run initial check
        print("[DEBUG] Calling reactor.callWhenRunning(periodic_checker)")
        reactor.callWhenRunning(periodic_checker)
        
        # Start scheduler in separate thread
        def run_schedule():
            print("[DEBUG] Scheduler thread started")
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        import threading
        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()
        
        print("[DEBUG] Starting reactor...")
        # Start reactor
        reactor.run()

if __name__ == "__main__":
    print("[DEBUG] Entered __main__ block")
    # Scrapy settings to be more respectful
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'scrapy.settings')
    
    # Configure Scrapy settings
    from scrapy.utils.project import get_project_settings
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'funda-scraper (+http://www.yourdomain.com)',
        'ROBOTSTXT_OBEY': False,  # Disable robots.txt for debugging
        'DOWNLOAD_DELAY': 3,  # Be respectful - 3 second delay between requests
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,
        'CONCURRENT_REQUESTS': 1,  # Only one request at a time
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'LOG_LEVEL': 'DEBUG',  # Show all Scrapy logs
    })
    print("[DEBUG] Scrapy settings configured")
    try:
        run_scheduler()
    except KeyboardInterrupt:
        print("\n\n🛑 Scraper stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
