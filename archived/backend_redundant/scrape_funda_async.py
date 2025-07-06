"""
Async/concurrent scraping implementation for faster scraping.
Uses asyncio and concurrent.futures for parallel execution.
"""
import asyncio
import concurrent.futures
import time
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html
from listing_mapping import map_listing_for_frontend
from funda_url_builder import build_rental_url

logger = logging.getLogger(__name__)

@dataclass
class ScrapeTask:
    """Represents a single scraping task"""
    url: str
    filters: Dict
    profile_id: str
    max_retries: int = 2
    timeout: int = 30  # Reduced timeout for faster execution

class FastScraper:
    """Optimized scraper with concurrent execution and smart caching"""
    
    def __init__(self, max_workers: int = 3, enable_caching: bool = True):
        self.max_workers = max_workers
        self.enable_caching = enable_caching
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 300  # 5 minutes cache TTL
        
    async def scrape_multiple_profiles(self, profiles: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Scrape multiple profiles concurrently for maximum speed.
        
        Args:
            profiles: List of profile dictionaries with filters
            
        Returns:
            Dict mapping profile_id to list of scraped listings
        """
        tasks = []
        
        # Create scraping tasks for each profile
        for profile in profiles:
            profile_id = profile.get('id')
            filters = profile.get('filters', {})
            
            try:
                # Build URL for this profile
                url = self._build_url_from_filters(filters)
                task = ScrapeTask(
                    url=url,
                    filters=filters,
                    profile_id=profile_id,
                    timeout=25  # Shorter timeout for concurrent execution
                )
                tasks.append(task)
                
            except Exception as e:
                logger.error(f"Failed to create task for profile {profile_id}: {e}")
                continue
        
        # Execute all tasks concurrently
        results = await self._execute_concurrent_scraping(tasks)
        
        # Process results
        processed_results = {}
        for profile_id, listings in results.items():
            if listings:
                processed_results[profile_id] = [map_listing_for_frontend(l) for l in listings]
            else:
                processed_results[profile_id] = []
                
        return processed_results
    
    async def _execute_concurrent_scraping(self, tasks: List[ScrapeTask]) -> Dict[str, List[Dict]]:
        """Execute scraping tasks concurrently using ThreadPoolExecutor"""
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self._scrape_single_task, task): task 
                for task in tasks
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_task, timeout=120):
                task = future_to_task[future]
                try:
                    listings = future.result()
                    results[task.profile_id] = listings
                    logger.info(f"Completed scraping for profile {task.profile_id}: {len(listings)} listings")
                    
                except Exception as e:
                    logger.error(f"Failed to scrape profile {task.profile_id}: {e}")
                    results[task.profile_id] = []
        
        return results
    
    def _scrape_single_task(self, task: ScrapeTask) -> List[Dict]:
        """Execute a single scraping task"""
        try:
            # Check cache first
            if self.enable_caching and self._is_cached(task.url):
                logger.info(f"Using cached data for {task.url}")
                return self.cache[task.url]['data']
            
            # Scrape the HTML
            html = scrape_funda_html(task.url, max_retries=task.max_retries, timeout=task.timeout)
            
            if not html:
                logger.warning(f"No HTML received for URL: {task.url}")
                return []
            
            # Extract listings
            listings = extract_simple_listings_from_html(html)
            
            # Cache the result
            if self.enable_caching:
                self._cache_result(task.url, listings)
            
            return listings
            
        except Exception as e:
            logger.error(f"Error scraping task {task.profile_id}: {e}")
            return []
    
    def _build_url_from_filters(self, filters: Dict) -> str:
        """Build Funda URL from filters dictionary"""
        return build_rental_url(
            city=filters.get('city'),
            property_type=filters.get('property_type'),
            min_price=filters.get('min_price'),
            max_price=filters.get('max_price'),
            min_floor_area=filters.get('min_area'),
            max_floor_area=filters.get('max_area'),
            min_rooms=filters.get('min_rooms'),
            max_rooms=filters.get('max_rooms'),
            min_bedrooms=filters.get('min_bedrooms'),
            max_bedrooms=filters.get('max_bedrooms'),
            energy_label=filters.get('energy_label'),
            furnished=filters.get('furnished'),
            partly_furnished=filters.get('partly_furnished'),
            balcony=filters.get('balcony'),
            roof_terrace=filters.get('roof_terrace'),
            garden=filters.get('garden'),
            parking=filters.get('parking'),
            garage=filters.get('garage'),
            lift=filters.get('lift'),
            single_floor=filters.get('single_floor'),
            disabled_access=filters.get('disabled_access'),
            elderly_access=filters.get('elderly_access'),
            listed_since_days=filters.get('listed_since'),
            keyword=filters.get('keyword'),
            sort_by=filters.get('sort_by', 'date_down'),  # Default to newest first
            per_page=50,  # Get more listings per page to reduce requests
            use_modern_url=True
        )
    
    def _is_cached(self, url: str) -> bool:
        """Check if URL result is in cache and still valid"""
        if url not in self.cache:
            return False
            
        cached_time = self.cache[url]['timestamp']
        return time.time() - cached_time < self.cache_ttl
    
    def _cache_result(self, url: str, data: List[Dict]):
        """Cache scraping result"""
        self.cache[url] = {
            'data': data,
            'timestamp': time.time()
        }
        
        # Keep cache size reasonable
        if len(self.cache) > 100:
            # Remove oldest entries
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k]['timestamp'])
            del self.cache[oldest_key]
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'size': len(self.cache),
            'entries': list(self.cache.keys()),
            'oldest': min(self.cache.values(), key=lambda v: v['timestamp'])['timestamp'] if self.cache else None
        }

# Global instance
fast_scraper = FastScraper(max_workers=3, enable_caching=True)

async def scrape_profiles_fast(profiles: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Fast scraping function for multiple profiles.
    
    Args:
        profiles: List of profile dictionaries
        
    Returns:
        Dict mapping profile_id to scraped listings
    """
    return await fast_scraper.scrape_multiple_profiles(profiles)

def scrape_profiles_fast_sync(profiles: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Synchronous wrapper for fast scraping.
    """
    return asyncio.run(scrape_profiles_fast(profiles))
