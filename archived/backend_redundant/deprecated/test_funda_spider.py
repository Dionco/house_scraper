#!/usr/bin/env python3
"""
Standalone test runner for FundaSpider
Run this to check if the spider works outside the Twisted/scheduler context.
"""
# --- Ensure correct Twisted reactor for Scrapy/asyncio compatibility ---
import sys
if sys.platform == "darwin":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
from twisted.internet import asyncioreactor
asyncioreactor.install()

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from main import FundaSpider

if __name__ == "__main__":
    print("[TEST] Standalone FundaSpider test starting...")
    settings = get_project_settings()
    settings.update({
        'USER_AGENT': 'funda-scraper (+http://www.yourdomain.com)',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 1,
        'LOG_LEVEL': 'DEBUG',
    })
    process = CrawlerProcess(settings)
    process.crawl(FundaSpider, start_urls=[
        'https://www.funda.nl/huur/utrecht/1000-2000/sorteer-datum-af/'
    ])
    process.start()
    print("[TEST] Standalone FundaSpider test finished.")

# This file is not imported by any main code. Move to deprecated/ if not needed.
