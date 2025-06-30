# Playwright + ZenRows browser test for Funda
# Usage: python test_zenrows_playwright.py

import asyncio
from playwright.async_api import async_playwright

ZENROWS_WSS = "wss://browser.zenrows.com?apikey=1dbfc0004dfeecd4e0c4ca33d3690ead634c7df1&proxy_country=nl"
TEST_URL = "https://www.funda.nl/huur/utrecht/1000-2000/sorteer-datum-af/"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(ZENROWS_WSS)
        page = await browser.new_page()
        await page.goto(TEST_URL)
        print("Page title:", await page.title())
        print("Page URL:", page.url)
        # Extract listings
        listings = await page.query_selector_all('.search-result')
        print(f"Found {len(listings)} listings on the page.")
        results = []
        for idx, listing in enumerate(listings):
            title = await listing.query_selector_eval('.search-result__header-title', 'el => el.innerText') if await listing.query_selector('.search-result__header-title') else None
            price = await listing.query_selector_eval('.search-result-price', 'el => el.innerText') if await listing.query_selector('.search-result-price') else None
            address = await listing.query_selector_eval('.search-result__header-subtitle', 'el => el.innerText') if await listing.query_selector('.search-result__header-subtitle') else None
            url = await listing.query_selector_eval('a.search-result__header-title-container', 'el => el.href') if await listing.query_selector('a.search-result__header-title-container') else None
            image_url = await listing.query_selector_eval('img', 'el => el.src') if await listing.query_selector('img') else None
            description = await listing.query_selector_eval('.search-result__description', 'el => el.innerText') if await listing.query_selector('.search-result__description') else None
            features = []
            feature_els = await listing.query_selector_all('.search-result-kenmerken li')
            for f in feature_els:
                features.append(await f.inner_text())
            results.append({
                'title': title,
                'price': price,
                'address': address,
                'url': url,
                'image_url': image_url,
                'description': description,
                'features': features
            })
        import json
        print(json.dumps(results, indent=2, ensure_ascii=False))
        # Print the full HTML for debugging
        content = await page.content()
        with open("funda_page_debug.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("Full HTML written to funda_page_debug.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

# This file is not imported by any main code. Move to deprecated/ if not needed.
