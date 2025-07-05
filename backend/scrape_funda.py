# scrape_funda.py: Contains the undetected_chromedriver scraping logic (fetches HTML, returns string)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

def scrape_funda_html(url, max_retries=2, timeout=45):
    """
    Scrape Funda HTML with Railway-optimized settings
    
    Args:
        url: The URL to scrape
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds for page load
    
    Returns:
        str: HTML content or None if failed
    """
    for attempt in range(max_retries):
        driver = None
        try:
            logger.info(f"Scraping attempt {attempt + 1}/{max_retries} for URL: {url}")
            
            # Use a fixed, reliable user agent instead of random
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            options = uc.ChromeOptions()
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1280,720')  # Smaller window for Railway
            options.add_argument('--lang=nl-NL,nl')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Speed up loading
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-features=TranslateUI')
            options.add_argument('--disable-ipc-flooding-protection')
            options.add_argument('--memory-pressure-off')
            options.add_argument('--max_old_space_size=4096')
            
            # Railway-specific optimizations
            options.add_argument('--single-process')  # Use single process to save memory
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-sync')
            
            # Don't disable JavaScript - Funda needs it!
            # options.add_argument('--disable-javascript')  # REMOVED - Funda requires JS
            
            # Set page load strategy
            options.add_argument('--page-load-strategy=normal')  # Changed from eager to normal
            
            # Initialize driver with shorter timeout
            logger.info("Initializing Chrome driver...")
            driver = uc.Chrome(options=options, version_main=None, driver_executable_path=None)
            
            # Set shorter timeouts for Railway
            driver.set_page_load_timeout(timeout)
            driver.implicitly_wait(5)  # Reduced from 10 to 5
            
            # Add short random delay to avoid detection
            time.sleep(random.uniform(0.5, 1.5))
            
            # Navigate to URL
            logger.info(f"Navigating to URL: {url}")
            driver.get(url)
            
            # Execute minimal anti-detection scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['nl-NL', 'nl']})")
            
            # Handle cookie consent popup
            try:
                # Wait for the cookie popup to appear and dismiss it
                from selenium.webdriver.common.by import By
                cookie_selectors = [
                    'button[data-test-id="didomi-notice-agree-button"]',
                    'button[id="didomi-notice-agree-button"]',
                    'button[class*="didomi-notice-agree-button"]',
                    'button[aria-label*="Akkoord"]',
                    'button[aria-label*="Agree"]',
                    'button:contains("Akkoord")',
                    'button:contains("Agree")',
                    '.didomi-popup-backdrop',
                    '.didomi-notice-component-button--highlight'
                ]
                
                cookie_dismissed = False
                for selector in cookie_selectors:
                    try:
                        if ':contains(' in selector:
                            # Skip CSS selectors with :contains for now
                            continue
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            elements[0].click()
                            logger.info(f"Clicked cookie consent button: {selector}")
                            cookie_dismissed = True
                            time.sleep(1)  # Wait for popup to disappear
                            break
                    except Exception as e:
                        logger.debug(f"Cookie button {selector} not found or not clickable: {e}")
                        continue
                
                if not cookie_dismissed:
                    logger.info("No cookie consent popup found or already dismissed")
                    
            except Exception as e:
                logger.warning(f"Error handling cookie popup: {e}")
            
            # Wait for page to load with Railway-friendly timeout
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            try:
                # Wait for body to be present
                WebDriverWait(driver, min(timeout, 20)).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
                )
                logger.info("Page body loaded.")
                
                # Wait for content to load (but not too long)
                time.sleep(random.uniform(1, 3))
                
                # Check if listings are present
                listings_found = False
                try:
                    # Check for modern Funda listing selectors based on the site structure
                    listing_selectors = [
                        '[data-test-id="search-result-item"]',
                        '.search-result',
                        '.object-list-item',
                        '.search-result-item',
                        '[data-object-url-tracking]',  # Common Funda attribute
                        'a[href*="/huur/"]',           # Rental links
                        'div[data-test-id*="result"]', # Any result divs
                        'div[class*="result"]',        # Any result divs
                        'article',                     # Article elements (common for listings)
                        'div[data-lazy-module]'        # Lazy-loaded modules
                    ]
                    
                    for selector in listing_selectors:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            listings_found = True
                            logger.info(f"Found {len(elements)} listing elements with selector: {selector}")
                            break
                            
                except Exception as e:
                    logger.warning(f"Could not check for listings: {e}")
                
                # If no listings found, wait a bit more for dynamic content
                if not listings_found:
                    logger.info("No listings found immediately, waiting for dynamic content...")
                    time.sleep(random.uniform(3, 6))  # Wait longer for JS to load
                    
                    # Try again after waiting
                    try:
                        for selector in listing_selectors:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            if elements:
                                listings_found = True
                                logger.info(f"Found {len(elements)} listing elements after wait: {selector}")
                                break
                    except Exception as e:
                        logger.warning(f"Could not check for listings after wait: {e}")
                else:
                    # Quick additional wait for content to fully load
                    time.sleep(random.uniform(1, 2))
                
            except Exception as e:
                logger.warning(f"Page may not be fully loaded: {e}")
                # Continue anyway, partial content might be available
            
            # Get the HTML
            html = driver.page_source
            
            # Validate HTML content
            if not html:
                raise Exception("Empty HTML content received")
                
            if len(html) < 5000:  # Too short for a real Funda page
                raise Exception(f"HTML too short: {len(html)} characters")
                
            # Check if page shows an error or has no results
            if "geen resultaten" in html.lower() or "no results" in html.lower():
                logger.warning("Page shows no results - this might be expected")
                
            # Check if page is properly loaded (has the expected structure)
            if "funda.nl" not in html.lower():
                raise Exception("HTML does not appear to be from Funda")
            
            logger.info(f"Successfully scraped {len(html)} characters")
            return html
                
        except Exception as e:
            logger.error(f"Scraping attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 5)  # Shorter backoff for Railway
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            
        finally:
            # Always close the driver
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                    
    logger.error(f"All {max_retries} scraping attempts failed for URL: {url}")
    return None
