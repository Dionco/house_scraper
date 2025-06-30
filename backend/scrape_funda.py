# scrape_funda.py: Contains the undetected_chromedriver scraping logic (fetches HTML, returns string)
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import random
from fake_useragent import UserAgent

def scrape_funda_html(url):
    ua = UserAgent()
    user_agent = ua.random
    print(f"Using User-Agent: {user_agent}")
    options = uc.ChromeOptions()
    options.add_argument(f'--user-agent={user_agent}')
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--lang=nl-NL,nl')
    proxies = []
    if proxies:
        proxy = random.choice(proxies)
        print(f"Using proxy: {proxy}")
        options.add_argument(f'--proxy-server=http://{proxy}')
    driver = uc.Chrome(options=options)
    time.sleep(random.uniform(2, 8))
    driver.get(url)
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
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body'))
        )
        print("[INFO] Page loaded.")
    except Exception as e:
        print(f"[WARN] Page may not be fully loaded: {e}")
    html = driver.page_source
    driver.quit()
    return html
