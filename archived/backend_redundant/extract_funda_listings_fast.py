"""
Optimized HTML extraction with faster parsing and better selector efficiency.
"""
import re
from bs4 import BeautifulSoup
import logging
from typing import List, Dict, Set, Optional

logger = logging.getLogger(__name__)

class FastListingExtractor:
    """Optimized listing extractor with caching and smart parsing"""
    
    def __init__(self):
        self.listing_selectors = [
            '[data-test-id="search-result-item"]',
            '.search-result',
            '.object-list-item', 
            '.search-result-item',
            'div[data-test-id*="result"]',
            'div[class*="result"]',
            'article',
            'div.border-b.pb-3'  # Common Funda card structure
        ]
        
        # Pre-compiled regex patterns for better performance
        self.price_pattern = re.compile(r'€?\s*([\d\.]+)', re.IGNORECASE)
        self.area_pattern = re.compile(r'(\d+)\s*m²', re.IGNORECASE)
        self.rooms_pattern = re.compile(r'(\d+)\s*(?:kamers?|rooms?)', re.IGNORECASE)
        self.bedrooms_pattern = re.compile(r'(\d+)\s*(?:slaapkamers?|bedrooms?)', re.IGNORECASE)
        self.postal_pattern = re.compile(r'(\d{4}\s*[A-Z]{2})', re.IGNORECASE)
        
    def extract_listings_fast(self, html: str) -> List[Dict]:
        """
        Fast extraction with optimized parsing strategy
        """
        if not html:
            return []
            
        try:
            # Use lxml parser for speed if available, fallback to html.parser
            try:
                soup = BeautifulSoup(html, "lxml")
            except:
                soup = BeautifulSoup(html, "html.parser")
                
            found_urls = set()
            results = []
            
            # Try multiple extraction strategies
            results.extend(self._extract_modern_cards(soup, found_urls))
            results.extend(self._extract_link_based(soup, found_urls))
            results.extend(self._extract_legacy_cards(soup, found_urls))
            
            logger.info(f"Extracted {len(results)} unique listings")
            return results
            
        except Exception as e:
            logger.error(f"Error in fast extraction: {e}")
            return []
    
    def _extract_modern_cards(self, soup: BeautifulSoup, found_urls: Set[str]) -> List[Dict]:
        """Extract from modern Funda card layout"""
        results = []
        
        for selector in self.listing_selectors[:4]:  # Try modern selectors first
            try:
                cards = soup.select(selector)
                if cards:
                    logger.debug(f"Found {len(cards)} cards with selector: {selector}")
                    
                    for card in cards:
                        listing = self._extract_card_data(card)
                        if listing and listing.get('funda_url'):
                            url = listing['funda_url']
                            if url not in found_urls:
                                found_urls.add(url)
                                results.append(listing)
                    
                    if results:  # If we found listings with this selector, stop trying others
                        break
                        
            except Exception as e:
                logger.debug(f"Error with selector {selector}: {e}")
                continue
                
        return results
    
    def _extract_legacy_cards(self, soup: BeautifulSoup, found_urls: Set[str]) -> List[Dict]:
        """Extract from legacy div.border-b.pb-3 structure"""
        results = []
        
        try:
            cards = soup.find_all("div", class_="border-b pb-3")
            
            for card in cards:
                listing = self._extract_legacy_card_data(card)
                if listing and listing.get('funda_url'):
                    url = listing['funda_url']
                    if url not in found_urls:
                        found_urls.add(url)
                        results.append(listing)
                        
        except Exception as e:
            logger.debug(f"Error in legacy extraction: {e}")
            
        return results
    
    def _extract_link_based(self, soup: BeautifulSoup, found_urls: Set[str]) -> List[Dict]:
        """Extract from direct links"""
        results = []
        
        try:
            # Find all links to rental details
            links = soup.find_all("a", href=True)
            
            for link in links:
                href = link.get("href", "")
                if ("/huur/" in href or "/detail/huur/" in href) and href not in found_urls:
                    listing = self._extract_from_link(link)
                    if listing:
                        found_urls.add(href)
                        results.append(listing)
                        
        except Exception as e:
            logger.debug(f"Error in link-based extraction: {e}")
            
        return results
    
    def _extract_card_data(self, card) -> Optional[Dict]:
        """Extract data from modern card layout"""
        try:
            # Find the main link
            link = card.find("a", href=True)
            if not link:
                return None
                
            url = link.get("href")
            if url and url.startswith("/"):
                url = "https://www.funda.nl" + url
                
            # Extract address
            address = self._extract_text_safely(card, ["h2", ".address", "[data-test-id*='address']"])
            
            # Extract price
            price = self._extract_price(card)
            
            # Extract area and rooms
            area = self._extract_area(card)
            rooms = self._extract_rooms(card)
            bedrooms = self._extract_bedrooms(card)
            
            # Extract location info
            location_info = self._extract_location(card)
            
            # Extract image
            image_url = self._extract_image_url(card)
            
            return {
                "address": address,
                "area_code": location_info.get("area_code"),
                "city": location_info.get("city"),
                "price": price,
                "area": area,
                "bedrooms": bedrooms,
                "rooms": rooms,
                "energy_label": self._extract_energy_label(card),
                "listed_since": self._extract_listed_since(card),
                "image_url": image_url,
                "funda_url": url
            }
            
        except Exception as e:
            logger.debug(f"Error extracting card data: {e}")
            return None
    
    def _extract_legacy_card_data(self, card) -> Optional[Dict]:
        """Extract data from modern Funda card format (div.border-b.pb-3)"""
        try:
            # Find the main listing link in H2
            h2 = card.find("h2")
            link = h2.find("a", href=True) if h2 else None
            
            if not link:
                return None
                
            url = link.get("href")
            if url and url.startswith("/"):
                url = "https://www.funda.nl" + url
                
            # Extract address from the link structure
            address = None
            address_span = link.find("span", class_="truncate")
            if address_span:
                address = address_span.get_text(strip=True)
            
            # Extract postal code and city from the second div in the link
            postal_city_div = link.find("div", class_="truncate text-neutral-80")
            area_code = city = None
            if postal_city_div:
                location_text = postal_city_div.get_text(strip=True)
                # Pattern: "2321 HZ Leiden"
                parts = location_text.split()
                if len(parts) >= 3:
                    area_code = " ".join(parts[:2])  # "2321 HZ"
                    city = " ".join(parts[2:])       # "Leiden"
                elif len(parts) == 2:
                    area_code = parts[0]
                    city = parts[1]
            
            # Extract price from font-semibold divs
            price = None
            price_divs = card.find_all("div", class_="font-semibold")
            for price_div in price_divs:
                price_text = price_div.get_text(strip=True)
                if "€" in price_text and ("maand" in price_text or "/month" in price_text):
                    price_match = self.price_pattern.search(price_text)
                    if price_match:
                        price_str = price_match.group(1).replace('.', '').replace(',', '')
                        try:
                            price = int(price_str)
                        except ValueError:
                            continue
                    break
            
            # Look for additional property details in list items or other elements
            area = bedrooms = energy_label = None
            
            # Search for area, bedrooms, and energy label in all text content
            all_text = card.get_text()
            
            # Extract area (m²)
            area_match = self.area_pattern.search(all_text)
            if area_match:
                area = area_match.group(1)
            
            # Extract bedrooms
            bedrooms_match = self.bedrooms_pattern.search(all_text)
            if bedrooms_match:
                bedrooms = bedrooms_match.group(1)
            
            # Extract energy label (single letter A-G)
            energy_match = re.search(r'\b([A-G])\b', all_text)
            if energy_match:
                energy_label = energy_match.group(1)
            
            # Extract image URL
            image_url = None
            img = card.find("img")
            if img:
                # Try different image attributes
                for attr in ["src", "data-src", "data-nuxt-img"]:
                    src = img.get(attr)
                    if src:
                        image_url = src
                        break
            
            # Extract agent info
            agent_name = None
            agent_links = card.find_all("a", href=True)
            for agent_link in agent_links:
                href = agent_link.get("href", "")
                if "/makelaar/" in href:
                    agent_name = agent_link.get_text(strip=True)
                    break
            
            return {
                "address": address,
                "area_code": area_code,
                "city": city,
                "price": price,
                "area": area,
                "bedrooms": bedrooms,
                "energy_label": energy_label,
                "agent_name": agent_name,
                "image_url": image_url,
                "funda_url": url
            }
            
        except Exception as e:
            logger.debug(f"Error extracting modern card: {e}")
            return None
    
    def _extract_from_link(self, link) -> Optional[Dict]:
        """Extract basic data from link element"""
        try:
            href = link.get("href")
            if not href:
                return None
                
            url = href if href.startswith("http") else "https://www.funda.nl" + href
            
            # Try to extract basic info from link text and surrounding elements
            address = link.get_text(strip=True)
            
            # Look for price in siblings or parent
            price = None
            parent = link.parent
            if parent:
                price_text = parent.get_text()
                price_match = self.price_pattern.search(price_text)
                if price_match:
                    price = int(price_match.group(1).replace('.', ''))
            
            return {
                "address": address,
                "price": price,
                "funda_url": url
            }
            
        except Exception as e:
            logger.debug(f"Error extracting from link: {e}")
            return None
    
    def _extract_text_safely(self, element, selectors: List[str]) -> Optional[str]:
        """Safely extract text using multiple selectors"""
        for selector in selectors:
            try:
                if selector.startswith("["):
                    # CSS selector
                    found = element.select_one(selector)
                else:
                    # Tag name
                    found = element.find(selector)
                    
                if found:
                    return found.get_text(strip=True)
            except:
                continue
        return None
    
    def _extract_price(self, element) -> Optional[int]:
        """Extract price from element"""
        try:
            # Look for price in various places
            price_text = element.get_text()
            match = self.price_pattern.search(price_text)
            if match:
                return int(match.group(1).replace('.', ''))
        except:
            pass
        return None
    
    def _extract_area(self, element) -> Optional[str]:
        """Extract area from element"""
        try:
            area_text = element.get_text()
            match = self.area_pattern.search(area_text)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def _extract_rooms(self, element) -> Optional[str]:
        """Extract number of rooms"""
        try:
            rooms_text = element.get_text()
            match = self.rooms_pattern.search(rooms_text)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def _extract_bedrooms(self, element) -> Optional[str]:
        """Extract number of bedrooms"""
        try:
            bedrooms_text = element.get_text()
            match = self.bedrooms_pattern.search(bedrooms_text)
            if match:
                return match.group(1)
        except:
            pass
        return None
    
    def _extract_location(self, element) -> Dict[str, Optional[str]]:
        """Extract location information"""
        try:
            location_text = element.get_text()
            
            # Look for postal code
            postal_match = self.postal_pattern.search(location_text)
            if postal_match:
                postal_code = postal_match.group(1)
                # Try to extract city from surrounding text
                parts = location_text.split()
                city = None
                for i, part in enumerate(parts):
                    if postal_code.replace(' ', '') in part.replace(' ', ''):
                        if i + 1 < len(parts):
                            city = ' '.join(parts[i+1:])
                        break
                
                return {
                    "area_code": postal_code,
                    "city": city
                }
        except:
            pass
            
        return {"area_code": None, "city": None}
    
    def _extract_energy_label(self, element) -> Optional[str]:
        """Extract energy label"""
        try:
            text = element.get_text()
            # Look for single letters A-G
            for char in text:
                if char.upper() in "ABCDEFG" and len(char) == 1:
                    return char.upper()
        except:
            pass
        return None
    
    def _extract_listed_since(self, element) -> Optional[str]:
        """Extract listing date"""
        try:
            # Look for date patterns
            text = element.get_text()
            date_patterns = [
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
                r'(\d{1,2}\s+\w+\s+\d{4})',
                r'(vandaag|gisteren|today|yesterday)'
            ]
            
            for pattern in date_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
        except:
            pass
        return None
    
    def _extract_image_url(self, element) -> Optional[str]:
        """Extract image URL"""
        try:
            img = element.find("img")
            if img:
                src = img.get("src") or img.get("data-src") or img.get("data-lazy-src")
                if src:
                    return src
        except:
            pass
        return None

# Global instance
fast_extractor = FastListingExtractor()

def extract_listings_fast(html: str) -> List[Dict]:
    """
    Fast extraction function
    """
    return fast_extractor.extract_listings_fast(html)

# Backward compatibility
def extract_simple_listings_from_html_fast(html: str) -> List[Dict]:
    """
    Fast version of the original extraction function
    """
    return extract_listings_fast(html)
