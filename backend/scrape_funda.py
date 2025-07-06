# scrape_funda.py: Contains the undetected_chromedriver scraping logic (fetches HTML, returns string)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

def scrape_funda_html(url, max_retries=2, timeout=30):
    """
    Scrape Funda HTML with performance optimizations
    
    Args:
        url: The URL to scrape
        max_retries: Maximum number of retry attempts
        timeout: Timeout in seconds for page load (reduced for speed)
    
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
            options.add_argument('--window-size=1024,768')  # Smaller window for speed
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
            
            # Performance optimizations
            options.add_argument('--aggressive-cache-discard')
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-default-apps')
            options.add_argument('--disable-sync')
            options.add_argument('--disable-web-resources')
            options.add_argument('--disable-client-side-phishing-detection')
            options.add_argument('--disable-component-update')
            options.add_argument('--disable-domain-reliability')
            options.add_argument('--disable-features=AudioServiceOutOfProcess')
            options.add_argument('--disable-hang-monitor')
            options.add_argument('--disable-logging')
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-permissions-api')
            options.add_argument('--disable-popup-blocking')
            options.add_argument('--disable-prompt-on-repost')
            options.add_argument('--disable-renderer-backgrounding')
            options.add_argument('--disable-backgrounding-occluded-windows')
            options.add_argument('--disable-background-timer-throttling')
            options.add_argument('--disable-features=VizDisplayCompositor')
            
            # Set page load strategy to eager for faster loading
            options.add_argument('--page-load-strategy=eager')
            
            # Initialize driver with shorter timeout
            logger.info("Initializing Chrome driver...")
            driver = uc.Chrome(options=options, version_main=None, driver_executable_path=None)
            
            # Set shorter timeouts for speed
            driver.set_page_load_timeout(timeout)
            driver.implicitly_wait(3)  # Reduced from 5 to 3
            
            # Add minimal delay to avoid detection
            time.sleep(random.uniform(0.2, 0.8))  # Reduced delay
            
            # Navigate to URL
            logger.info(f"Navigating to URL: {url}")
            driver.get(url)
            
            # Execute minimal anti-detection scripts
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['nl-NL', 'nl']})")
            
            # Fast cookie handling - try once and move on
            try:
                cookie_selectors = [
                    'button[data-test-id="didomi-notice-agree-button"]',
                    'button[id="didomi-notice-agree-button"]',
                    'button[class*="didomi-notice-agree-button"]',
                    'button[aria-label*="Akkoord"]',
                    'button[aria-label*="Agree"]'
                ]
                
                for selector in cookie_selectors:
                    try:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            elements[0].click()
                            logger.info(f"Clicked cookie consent button: {selector}")
                            time.sleep(0.5)  # Minimal wait
                            break
                    except:
                        continue
                        
            except Exception as e:
                logger.debug(f"Cookie handling skipped: {e}")
            
            # Minimal wait for page load
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            try:
                # Wait for body to be present with shorter timeout
                WebDriverWait(driver, min(timeout, 15)).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
                )
                
                # Quick check for listings with minimal wait
                time.sleep(random.uniform(0.5, 1.5))  # Reduced wait time
                
            except Exception as e:
                logger.warning(f"Page load timeout: {e}")
                # Continue anyway, partial content might be available
            
            # Get the HTML
            html = driver.page_source
            
            # Quick validation
            if not html or len(html) < 3000:  # Reduced threshold
                raise Exception(f"HTML too short or empty: {len(html) if html else 0} characters")
                
            # Quick check for Funda content
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
