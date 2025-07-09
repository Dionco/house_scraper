# scrape_funda.py: Contains the undetected_chromedriver scraping logic (fetches HTML, returns string)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from fake_useragent import UserAgent
import logging

logger = logging.getLogger(__name__)

def is_running_on_railway():
    """Check if the application is running on Railway."""
    import os
    return any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("PORT")  # Railway sets this automatically
    ])

def is_running_in_container():
    """Check if running in a Docker container."""
    try:
        with open('/proc/1/cgroup', 'rt') as f:
            return 'docker' in f.read() or 'kubepods' in f.read()
    except:
        try:
            import os
            return os.path.exists('/.dockerenv')
        except:
            return False

def get_chrome_binary_path():
    """Get the appropriate Chrome binary path for the environment."""
    import os
    import platform
    
    if is_running_on_railway() or is_running_in_container():
        # Standard locations in Linux-based containers
        possible_paths = [
            '/usr/bin/google-chrome',
            '/usr/bin/google-chrome-stable',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            # Add Railway-specific paths if they differ
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return None  # Let the driver try to find it
    else:
        # For local development, let undetected_chromedriver find the binary
        return None

def scrape_funda_html(url, max_retries=3, timeout=60):
    """
    Scrape Funda HTML with improved stability for Railway deployment
    
    Args:
        url: The URL to scrape
        max_retries: Maximum number of retry attempts (increased from 2 to 3)
        timeout: Timeout in seconds for page load (increased for reliability)
    
    Returns:
        str: HTML content or None if failed
    """
    for attempt in range(max_retries):
        driver = None
        try:
            # Explicitly free memory before each attempt
            import gc
            gc.collect()
            
            # Introduce increasing delay between retries to reduce resource contention
            if attempt > 0:
                wait_time = 5 * attempt
                logger.info(f"Waiting {wait_time}s before retry {attempt+1}")
                time.sleep(wait_time)
                
            logger.info(f"Scraping attempt {attempt + 1}/{max_retries} for URL: {url}")
            
            # Use a fixed, reliable user agent instead of random
            user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            
            options = uc.ChromeOptions()
            options.add_argument(f'--user-agent={user_agent}')
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # More conservative settings to reduce resource usage
            options.add_argument('--window-size=800,600')  # Even smaller window
            options.add_argument('--lang=nl-NL,nl')
            options.add_argument('--disable-gpu')
            options.add_argument('--disable-extensions')
            options.add_argument('--disable-images')  # Speed up loading
            options.add_argument('--disable-background-networking')
            options.add_argument('--disable-default-apps')
            
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
            
            # Configure Chrome binary path for containerized environments
            chrome_binary = get_chrome_binary_path()
            if chrome_binary:
                logger.info(f"Using Chrome binary path: {chrome_binary}")
                options.binary_location = chrome_binary
                
            # Handle Railway/container environments
            if is_running_on_railway() or is_running_in_container():
                logger.info("Running in Railway/Container environment, using container-specific settings")
                options.add_argument('--disable-setuid-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                options.add_argument('--headless=new')
                
                # Use shared memory for Railway
                options.add_argument('--disable-dev-shm-usage')
                
                # Memory optimization for containerized environment
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-audio-output')
                options.add_argument('--mute-audio')
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--disable-3d-apis')
                options.add_argument('--disable-accelerated-2d-canvas')
                options.add_argument('--disable-accelerated-jpeg-decoding')
                options.add_argument('--disable-accelerated-mjpeg-decode')
                options.add_argument('--disable-accelerated-video-decode')
                options.add_argument('--disable-accelerated-video-encode')
                options.add_argument('--disable-app-list-dismiss-on-blur')
                options.add_argument('--disable-breakpad')
                options.add_argument('--disable-component-extensions-with-background-pages')
                
                # Increase timeout for Railway environment
                timeout = max(timeout, 45)
                
            # Initialize driver with more robust error handling
            logger.info("Initializing Chrome driver...")
            
            # Set Chrome version for better compatibility
            chrome_version = None
            if is_running_on_railway() or is_running_in_container():
                try:
                    import subprocess
                    chrome_version_output = subprocess.check_output(['google-chrome', '--version']).decode('utf-8').strip()
                    # Extract version number (e.g., "Google Chrome 93.0.4577.63" -> 93)
                    version_parts = chrome_version_output.split()
                    if len(version_parts) >= 3:
                        chrome_version = int(version_parts[2].split('.')[0])
                        logger.info(f"Detected Chrome version: {chrome_version}")
                except Exception as e:
                    logger.warning(f"Could not detect Chrome version: {e}")
            
            # Use a temporary directory for Chrome data
            import tempfile
            import os
            
            # Create temporary user data directory
            temp_dir = tempfile.mkdtemp()
            user_data_dir = os.path.join(temp_dir, "chrome-data")
            os.makedirs(user_data_dir, exist_ok=True)
            logger.info(f"Using temporary user data directory: {user_data_dir}")
            options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Add more connection stability options
            options.add_argument("--disable-application-cache")
            options.add_argument("--disable-session-crashed-bubble")
            options.add_argument("--disable-site-isolation-trials")
            
            # Increase connection timeouts
            options.add_argument("--host-resolver-timeout=60000")
            options.add_argument("--dns-prefetch-timeout=60000")
            
            # Specify log file location to avoid filling container logs
            if is_running_on_railway() or is_running_in_container():
                log_path = os.path.join(temp_dir, "chrome.log")
                options.add_argument(f"--log-file={log_path}")
                options.add_argument("--v=0")  # Minimal logging
            
            # Initialize with error handling and more resilient settings
            driver = uc.Chrome(
                options=options,
                version_main=chrome_version,
                driver_executable_path=None,
                headless=True,
                use_subprocess=True,
                browser_executable_path=chrome_binary if chrome_binary else None
            )
            
            # Set proper timeouts for reliability
            driver.set_page_load_timeout(timeout)
            driver.set_script_timeout(timeout)
            driver.implicitly_wait(5)
            
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
            error_msg = str(e)
            logger.error(f"Scraping attempt {attempt + 1} failed: {error_msg}")
            
            # Better error diagnosis for Chrome binary issues
            if "binary location" in error_msg.lower():
                import os
                # Log available Chrome binaries
                chrome_paths = [
                    '/usr/bin/google-chrome',
                    '/usr/bin/google-chrome-stable',
                    '/usr/bin/chromium',
                    '/usr/bin/chromium-browser'
                ]
                for path in chrome_paths:
                    logger.info(f"Chrome path {path} exists: {os.path.exists(path)}")
                
                # Try to get Chrome version
                try:
                    import subprocess
                    chrome_version = subprocess.check_output(['google-chrome', '--version']).decode('utf-8').strip()
                    logger.info(f"Chrome version: {chrome_version}")
                except Exception as chrome_err:
                    logger.error(f"Failed to get Chrome version: {chrome_err}")
            
            if attempt < max_retries - 1:
                wait_time = 5 + (attempt * 5)  # Shorter backoff for Railway
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            
        finally:
            # Always close the driver and free resources with enhanced cleanup
            if driver:
                try:
                    # First try to close all windows
                    try:
                        for handle in driver.window_handles:
                            driver.switch_to.window(handle)
                            driver.close()
                    except:
                        pass
                    
                    # Then quit the driver
                    driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing driver: {e}")
                    
                    # If normal quit fails, try to kill Chrome processes
                    if is_running_on_railway() or is_running_in_container():
                        try:
                            import subprocess
                            # Try to kill orphaned Chrome processes
                            logger.info("Attempting to kill orphaned Chrome processes")
                            subprocess.call("pkill -f chrome", shell=True)
                        except Exception as kill_err:
                            logger.warning(f"Failed to kill Chrome processes: {kill_err}")
                
                # Clean up temporary directory
                try:
                    if 'temp_dir' in locals() and os.path.exists(temp_dir):
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
                except Exception as e:
                    logger.debug(f"Error cleaning temp directory: {e}")
                
                # Force garbage collection
                import gc
                driver = None
                gc.collect()
                
                # Sleep briefly to allow system to reclaim resources
                time.sleep(1)
                    
    logger.error(f"All {max_retries} scraping attempts failed for URL: {url}")
    return None
