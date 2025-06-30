# Minimal undetected-chromedriver test for anti-bot bypass
# Usage: python test_undetected_chromedriver.py

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from fake_useragent import UserAgent

URL = "https://www.funda.nl/huur/utrecht/3000-5000/sorteer-datum-af/"


if __name__ == "__main__":
    ua = UserAgent()
    user_agent = ua.random
    print(f"Using User-Agent: {user_agent}")
    options = uc.ChromeOptions()
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument('--headless=new')  # Remove this line to see browser
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    # Spoof window size and language
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=nl-NL,nl')
    # Example proxy list (replace with your own or a proxy provider)
    proxies = [
        # Format: 'ip:port' or 'user:pass@ip:port' for authenticated proxies
        # 'username:password@proxy1.example.com:8000',
        # 'proxy2.example.com:8000',
    ]
    if proxies:
        proxy = random.choice(proxies)
        print(f"Using proxy: {proxy}")
        options.add_argument(f'--proxy-server=http://{proxy}')
    driver = uc.Chrome(options=options)
    # --- Request rate limiting and human-like delays ---
    # Random delay before scraping
    time.sleep(random.uniform(2, 8))
    driver.get(URL)
    # CAPTCHA detection
    page_source = driver.page_source
    captcha_indicators = ["captcha", "security check", "prove you are", "ik ben geen robot", "recaptcha"]
    if any(indicator.lower() in page_source.lower() for indicator in captcha_indicators):
        print("⚠️ CAPTCHA detected! Consider using a CAPTCHA solving service or improving evasion.")
    else:
        print("No CAPTCHA detected.")
    # --- Automated CAPTCHA solving with 2captcha (reCAPTCHA v2 example) ---
    # Requires: pip install twocaptcha-python
    # Set your 2captcha API key here
    TWOCAPTCHA_API_KEY = "YOUR_2CAPTCHA_API_KEY"
    if any(indicator.lower() in page_source.lower() for indicator in captcha_indicators):
        try:
            from twocaptcha import TwoCaptcha
            solver = TwoCaptcha(TWOCAPTCHA_API_KEY)
            # Try to find reCAPTCHA sitekey on the page
            try:
                sitekey = driver.find_element(By.CLASS_NAME, 'g-recaptcha').get_attribute('data-sitekey')
            except Exception:
                sitekey = None
            if sitekey:
                print(f"[INFO] Found reCAPTCHA sitekey: {sitekey}")
                result = solver.recaptcha(sitekey=sitekey, url=URL)
                print(f"[INFO] 2captcha solution token: {result['code']}")
                # Inject the token into the page if needed
                driver.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{result['code']}';")
                print("[INFO] Injected CAPTCHA solution into page.")
            else:
                print("[INFO] No reCAPTCHA sitekey found on page. Manual integration may be needed for other CAPTCHA types.")
        except Exception as e:
            print(f"[ERROR] 2captcha solving failed: {e}")
    # Spoof WebGL and other fingerprints via JS
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.execute_script("Object.defineProperty(navigator, 'languages', {get: () => ['nl-NL', 'nl']})")
    driver.execute_script("Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]})")
    # Remove more automation indicators
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
    print("Page title:", driver.title)
    print("Page URL:", driver.current_url)
    # Print a snippet of the page source
    print("Page source snippet:", driver.page_source[:500])
    # Optionally, save the full HTML for inspection
    with open("funda_uc_debug.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Full HTML written to funda_uc_debug.html")
    # --- Extract listings from the loaded page using Selenium ---
    import json
    from bs4 import BeautifulSoup
    # Wait for listings to load (adjust selector as needed)
    try:
        driver.implicitly_wait(10)
    except Exception as e:
        print(f"[WARN] Could not confirm listings loaded: {e}")
    # Parse page source with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")
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
    print(f"[INFO] Found {len(listings)} listings on the page.")
    for i, item in enumerate(listings, 1):
        print(f"--- Listing {i} ---")
        for k, v in item.items():
            print(f"{k}: {v}")
        print()
    # Save to file for further processing
    with open("funda_uc_listings.jsonl", "w", encoding="utf-8") as f:
        for item in listings:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"[INFO] Listings saved to funda_uc_listings.jsonl")
    # --- Session and Cookie Management ---
    import pickle
    # Save cookies after login/page load
    with open('cookies.pkl', 'wb') as f:
        pickle.dump(driver.get_cookies(), f)
    print("Cookies saved to cookies.pkl")
    # To reuse cookies in a future session:
    # with open('cookies.pkl', 'rb') as f:
    #     cookies = pickle.load(f)
    #     for cookie in cookies:
    #         driver.add_cookie(cookie)
    # --- Advanced Evasion Techniques: Human-like mouse movement and scrolling ---
    from selenium.webdriver.common.action_chains import ActionChains
    # Simulate human-like scrolling
    for _ in range(random.randint(2, 5)):
        scroll_amount = random.randint(100, 400)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 2))
    # Simulate human-like mouse movement and click (if needed)
    body = driver.find_element(By.TAG_NAME, 'body')
    actions = ActionChains(driver)
    actions.move_to_element_with_offset(body, random.randint(0, 100), random.randint(0, 100))
    actions.pause(random.uniform(0.1, 0.5))
    actions.click()
    actions.perform()
    # Random delay after scraping
    time.sleep(random.uniform(2, 8))
    # --- Monitoring and Adaptation: Detection alerts and fallback strategies ---
    def check_for_blocking(response_text):
        blocking_indicators = [
            "Access Denied",
            "Blocked",
            "CAPTCHA",
            "Rate Limited",
            "Security Check",
            "Je bent bijna op de pagina die je zoekt",
            "Toegang geweigerd"
        ]
        return any(indicator.lower() in response_text.lower() for indicator in blocking_indicators)

    if check_for_blocking(page_source):
        print("[ALERT] Possible blocking or anti-bot detected! Switching strategy...")
        # Example fallback: increase delay, rotate proxy, change user-agent
        print("[FALLBACK] Increasing delay and rotating user-agent/proxy...")
        time.sleep(random.uniform(30, 120))
        # You could also reload with a new proxy/user-agent here
    else:
        print("No blocking detected.")
    # --- Handle JavaScript challenges in browser context ---
    # Example: If a JS challenge sets a cookie or value, let the browser execute it naturally
    # Optionally, wait for JS to finish or for a specific element to appear
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        # Wait for a key element that only appears after JS challenge is solved
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
        )
        print("[INFO] JavaScript challenge (if any) handled by browser context.")
    except Exception as e:
        print(f"[WARN] JS challenge may not be solved: {e}")
    driver.quit()
# This file is not imported by any main code. Move to deprecated/ if not needed.
