# scrape_funda.py: Contains the undetected_chromedriver scraping logic (fetches HTML, returns string)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

def scrape_funda_html(url, max_retries=3, timeout=60):
    """
    Scrape Funda HTML with improved error handling and retries
    
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
            
            ua = UserAgent()
            user_agent = ua.random
            print(f"Using User-Agent: {user_agent}")
            
            options = uc.ChromeOptions()
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')  # Fix for Railway memory issues
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--lang=nl-NL,nl')
            options.add_argument('--disable-gpu')  # Reduce resource usage
            options.add_argument('--disable-web-security')
            options.add_argument('--disable-features=VizDisplayCompositor')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-plugins')
            options.add_argument('--disable-images')  # Speed up loading
            options.add_argument('--disable-javascript')  # Speed up loading if not needed
            
            # Set timeouts
            options.add_argument(f'--timeout={timeout}')
            options.add_argument('--page-load-strategy=eager')  # Don't wait for all resources
            
            # Initialize driver with retries
            driver = uc.Chrome(options=options, version_main=None)
            
            # Set timeouts
            driver.set_page_load_timeout(timeout)
            driver.implicitly_wait(10)
            
            # Add random delay to avoid detection
            time.sleep(random.uniform(1, 3))
            
            # Navigate to URL
            driver.get(url)
            
            # Execute anti-detection scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['nl-NL', 'nl']})")
            driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
            driver.execute_script("delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;")
            driver.execute_script("delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;")
            driver.execute_script("delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;")
            driver.execute_script("Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1})")
            driver.execute_script("Object.defineProperty(navigator, 'hardwareConcurrency', {get: () => 8})")
            driver.execute_script("Object.defineProperty(navigator, 'deviceMemory', {get: () => 8})")
            driver.execute_script("Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'})")
            driver.execute_script("Object.defineProperty(navigator, 'appVersion', {get: () => '5.0 (Windows)'});")
            driver.execute_script("Object.defineProperty(navigator, 'appName', {get: () => 'Netscape'});")
            driver.execute_script("Object.defineProperty(navigator, 'appCodeName', {get: () => 'Mozilla'});")
            driver.execute_script("Object.defineProperty(navigator, 'cookieEnabled', {get: () => true})")
            driver.execute_script("Object.defineProperty(navigator, 'doNotTrack', {get: () => null})")
            driver.execute_script("Object.defineProperty(navigator, 'onLine', {get: () => true})")
            driver.execute_script("Object.defineProperty(navigator, 'product', {get: () => 'Gecko'})")
            driver.execute_script("Object.defineProperty(navigator, 'productSub', {get: () => '20030107'})")
            driver.execute_script("Object.defineProperty(navigator, 'userAgentData', {get: () => undefined})")
            
            # Wait for page to load with shorter timeout for Railway
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            try:
                WebDriverWait(driver, min(timeout, 30)).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
                )
                print("[INFO] Page loaded.")
                
                # Additional wait for dynamic content
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                logger.warning(f"Page may not be fully loaded: {e}")
                # Continue anyway, partial content might be available
            
            # Get the HTML
            html = driver.page_source
            
            if html and len(html) > 1000:  # Basic validation
                logger.info(f"Successfully scraped {len(html)} characters")
                return html
            else:
                raise Exception(f"HTML too short or empty: {len(html) if html else 0} characters")
                
        except Exception as e:
            logger.error(f"Scraping attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 10  # Exponential backoff
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
