def extract_simple_listings_from_html(html):
    """
    Extracts address, area code, city, price, area, number of bedrooms, image, and url from the HTML listing cards.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []
    # Track URLs to avoid duplicates
    found_urls = set()

    # First, extract from div.border-b.pb-3 (old logic)
    for card in soup.find_all("div", class_="border-b pb-3"):
        h2 = card.find("h2")
        a = h2.find("a", href=True) if h2 else None
        address = None
        url = None
        if a:
            span = a.find("span", class_="truncate")
            address = span.get_text(strip=True) if span else None
            url = a.get("href")
            if url and url.startswith("/"):
                url = "https://www.funda.nl" + url
        area_code = city = None
        if a:
            area_city_div = a.find("div", class_="truncate text-neutral-80")
            area_city = area_city_div.get_text(strip=True) if area_city_div else ""
            if area_city:
                parts = area_city.split()
                area_code = " ".join(parts[:2])
                city = " ".join(parts[2:])
        import re
        price = None
        price_div = card.find("div", class_="font-semibold mt-2 mb-0")
        if price_div:
            price_trunc = price_div.find("div", class_="truncate")
            price_raw = price_trunc.get_text(strip=True) if price_trunc else price_div.get_text(strip=True)
            match = re.search(r"([\d\.]+)", price_raw)
            if match:
                price = int(match.group(1).replace('.', ''))
            else:
                price = None
        area = bedrooms = energy_label = None
        for li in card.find_all("li"):
            text = li.get_text(strip=True)
            if "m²" in text and not area:
                area = text.split()[0]
            elif text.isdigit() and not bedrooms:
                bedrooms = text
            elif len(text) == 1 and text.isalpha() and text.upper() in "ABCDEFG" and not energy_label:
                energy_label = text.upper()
        image_url = None
        img = card.find("img")
        if img and img.get("src"):
            image_url = img["src"]
        # Find listing date info (look for previous sibling with class 'font-semibold mb-4')
        listed_since = None
        prev = card.find_previous_sibling()
        for _ in range(3):
            if prev and prev.has_attr('class') and 'font-semibold' in prev['class'] and 'mb-4' in prev['class']:
                listed_since = prev.get_text(strip=True)
                break
            prev = prev.find_previous_sibling() if prev else None
        if url and url not in found_urls:
            found_urls.add(url)
            results.append({
                "address": address,
                "area_code": area_code,
                "city": city,
                "price": price,
                "area": area,
                "bedrooms": bedrooms,
                "energy_label": energy_label,
                "listed_since": listed_since,
                "image_url": image_url,
                "funda_url": url
            })

    # Second, extract from <a> tags with href matching /detail/huur/utrecht/huis-
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/detail/huur/utrecht/huis-") and ("/" in href[1:]):
            url = href
            if url.startswith("/"):
                url = "https://www.funda.nl" + url
            if url in found_urls:
                continue
            # Try to get address
            address = None
            span = a.find("span", class_="truncate")
            if span:
                address = span.get_text(strip=True)
            # Area code and city
            area_code = city = None
            area_city_div = a.find("div", class_="truncate text-neutral-80")
            area_city = area_city_div.get_text(strip=True) if area_city_div else ""
            if area_city:
                parts = area_city.split()
                area_code = " ".join(parts[:2])
                city = " ".join(parts[2:])
            # If not found, look for h2 sibling or parent with address/city
            if not address or not area_code or not city:
                # Try next siblings and parents for h2
                h2 = None
                sib = a
                for _ in range(3):
                    if sib is None:
                        break
                    sib = sib.find_next_sibling()
                    if sib and sib.name == "h2":
                        h2 = sib
                        break
                # If not found, check parents
                if not h2:
                    parent = a.parent if a else None
                    for _ in range(3):
                        if not parent:
                            break
                        h2 = parent.find("h2")
                        if h2:
                            break
                        parent = parent.parent
                if h2:
                    a2 = h2.find("a", href=True)
                    if a2:
                        span2 = a2.find("span", class_="truncate")
                        if span2 and not address:
                            address = span2.get_text(strip=True)
                        area_city_div2 = a2.find("div", class_="truncate text-neutral-80")
                        area_city2 = area_city_div2.get_text(strip=True) if area_city_div2 else ""
                        if area_city2:
                            parts2 = area_city2.split()
                            if not area_code:
                                area_code = " ".join(parts2[:2])
                            if not city:
                                city = " ".join(parts2[2:])
            # Find parent container for price, area, bedrooms, image
            parent = a.parent
            price = area = bedrooms = energy_label = image_url = None
            # Look for price
            price_div = None
            for _ in range(3):
                if parent is None:
                    break
                price_div = parent.find("div", class_="font-semibold mt-2 mb-0")
                if price_div:
                    break
                parent = parent.parent
            if price_div:
                price_trunc = price_div.find("div", class_="truncate")
                price_raw = price_trunc.get_text(strip=True) if price_trunc else price_div.get_text(strip=True)
                match = re.search(r"([\d\.]+)", price_raw)
                if match:
                    price = int(match.group(1).replace('.', ''))
                else:
                    price = None
            # Area and bedrooms
            parent = a.parent
            for _ in range(3):
                if parent is None:
                    break
                for li in parent.find_all("li"):
                    text = li.get_text(strip=True)
                    if "m²" in text and not area:
                        area = text.split()[0]
                    elif text.isdigit() and not bedrooms:
                        bedrooms = text
                    elif len(text) == 1 and text.isalpha() and text.upper() in "ABCDEFG" and not energy_label:
                        energy_label = text.upper()
                parent = parent.parent
            # Image
            parent = a.parent
            for _ in range(3):
                if parent is None:
                    break
                img = parent.find("img")
                if img and img.get("src"):
                    image_url = img["src"]
                    break
                parent = parent.parent
            # Find listing date info (look for previous sibling with class 'font-semibold mb-4')
            listed_since = None
            parent = a.parent
            for _ in range(5):
                if parent is None:
                    break
                prev = parent.find_previous_sibling()
                for _ in range(3):
                    if prev and prev.has_attr('class') and 'font-semibold' in prev['class'] and 'mb-4' in prev['class']:
                        listed_since = prev.get_text(strip=True)
                        break
                    prev = prev.find_previous_sibling() if prev else None
                if listed_since:
                    break
                parent = parent.parent
            found_urls.add(url)
            results.append({
                "address": address,
                "area_code": area_code,
                "city": city,
                "price": price,
                "area": area,
                "bedrooms": bedrooms,
                "energy_label": energy_label,
                "listed_since": listed_since,
                "image_url": image_url,
                "funda_url": url
            })
    # Add listed_days_ago field to each result
    import re
    from datetime import datetime
    from timezone_utils import now_cest
    today = now_cest()
    month_map = {
        'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12
    }
    for l in results:
        listed_since = l.get('listed_since')
        days_ago = None
        if listed_since:
            # Handle 'Sinds X weken'
            match = re.match(r"Sinds (\d+) weken", listed_since)
            if match:
                days_ago = int(match.group(1)) * 7
            else:
                # Handle 'Sinds X maanden'
                match = re.match(r"Sinds (\d+) maanden", listed_since)
                if match:
                    days_ago = int(match.group(1)) * 30
                else:
                    # Try to parse Dutch date, e.g. 'Donderdag 19 juni'
                    match = re.search(r"(\d{1,2}) ([a-z]+)", listed_since, re.IGNORECASE)
                    if match:
                        day = int(match.group(1))
                        month_str = match.group(2).lower()
                        month = month_map.get(month_str)
                        if month:
                            year = today.year
                            try:
                                dt = datetime(year, month, day)
                            except ValueError:
                                dt = None
                            if dt and dt > today:
                                dt = datetime(year-1, month, day)
                            if dt:
                                days_ago = (today - dt).days
        l['listed_days_ago'] = days_ago
    return results

# ---
# To run the new extraction and save to a new file:
def main_simple():
    with open("funda_uc_debug.html", "r", encoding="utf-8") as f:
        html = f.read()
    import re
    from datetime import datetime, timedelta
    from timezone_utils import now_cest
    listings = extract_simple_listings_from_html(html)
    today = now_cest()
    month_map = {
        'januari': 1, 'februari': 2, 'maart': 3, 'april': 4, 'mei': 5, 'juni': 6,
        'juli': 7, 'augustus': 8, 'september': 9, 'oktober': 10, 'november': 11, 'december': 12
    }
    for l in listings:
        listed_since = l.get('listed_since')
        days_ago = None
        if listed_since:
            # Handle 'Sinds X weken'
            match = re.match(r"Sinds (\d+) weken", listed_since)
            if match:
                days_ago = int(match.group(1)) * 7
            else:
                # Try to parse Dutch date, e.g. 'Donderdag 19 juni'
                match = re.search(r"(\d{1,2}) ([a-z]+)", listed_since, re.IGNORECASE)
                if match:
                    day = int(match.group(1))
                    month_str = match.group(2).lower()
                    month = month_map.get(month_str)
                    if month:
                        year = today.year
                        # If the date is in the future, it must be from last year
                        try:
                            dt = datetime(year, month, day)
                        except ValueError:
                            dt = None
                        if dt and dt > today:
                            dt = datetime(year-1, month, day)
                        if dt:
                            days_ago = (today - dt).days
        l['listed_days_ago'] = days_ago
    with open("funda_simple_listings.json", "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2)
    print(f"Extracted {len(listings)} listings to funda_simple_listings.json")

from bs4 import BeautifulSoup
import json


# The following code is for manual testing only. It should not run on import.
if __name__ == "__main__":
    # Load the HTML file
    try:
        with open("funda_uc_debug.html", "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        print("funda_uc_debug.html not found. Skipping manual test.")
        html = None
    if html:
        # Parse HTML
        soup = BeautifulSoup(html, "html.parser")
        # Find the script tag with the listing data
        script = soup.find("script", {"id": "__NUXT_DATA__"})
        if not script:
            print("No __NUXT_DATA__ script tag found.")
            exit(1)
        data = json.loads(script.string)
        # --- Extraction logic ---first test if it works


def resolve_listing(ref, data):
    # Recursively resolve until we get a dict
    seen = set()
    while True:
        if isinstance(ref, dict):
            return ref
        if isinstance(ref, list):
            # If it's a list of ints, treat as group of references
            if all(isinstance(x, int) for x in ref):
                dicts = []
                for idx in ref:
                    if 0 <= idx < len(data):
                        resolved = resolve_listing(data[idx], data)
                        if isinstance(resolved, dict):
                            dicts.append(resolved)
                return dicts
            elif len(ref) == 2 and ref[0] in ('Ref', 'Reactive') and isinstance(ref[1], int):
                ref = data[ref[1]]
            else:
                return ref
        elif isinstance(ref, int):
            if ref in seen:
                return None
            seen.add(ref)
            ref = data[ref]
        else:
            return ref

def resolve_value(val, data, _seen=None):
    # Recursively resolve through ints, lists, dicts until primitive, for all nested fields
    if _seen is None:
        _seen = set()
    if id(val) in _seen:
        return None
    _seen.add(id(val))
    # Resolve integer references
    if isinstance(val, int) and 0 <= val < len(data):
        return resolve_value(data[val], data, _seen)
    # Resolve reference structures
    if isinstance(val, list):
        # Handle ['Ref', N], ['Reactive', N], ['ShallowReactive', N]
        if len(val) == 2 and val[0] in ('Ref', 'Reactive', 'ShallowReactive') and isinstance(val[1], int):
            return resolve_value(data[val[1]], data, _seen)
        # Recursively resolve all elements in the list
        return [resolve_value(v, data, _seen) for v in val]
    # Resolve dicts
    if isinstance(val, dict):
        # If dict has a 'value' key, resolve it
        if 'value' in val and len(val) == 1:
            return resolve_value(val['value'], data, _seen)
        # Otherwise, resolve all fields
        return {k: resolve_value(v, data, _seen) for k, v in val.items()}
    return val

# Find the listings array by following the reference chain
def get_listings_obj(data):
    if isinstance(data, list) and len(data) > 30 and isinstance(data[30], dict):
        d30 = data[30]
        search_idx = d30.get('search')
        if isinstance(search_idx, int) and 0 <= search_idx < len(data):
            search_obj = data[search_idx]
            if isinstance(search_obj, dict):
                listings_idx = search_obj.get('listings')
                if isinstance(listings_idx, int) and 0 <= listings_idx < len(data):
                    listings_obj = data[listings_idx]
                    if isinstance(listings_obj, list):
                        return listings_obj
    return None


def flatten_dict(d, parent_key='', sep='.'): 
    # Recursively flatten a nested dictionary
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.update(flatten_dict(item, f"{new_key}[{i}]", sep=sep))
                else:
                    items[f"{new_key}[{i}]"] = item
        else:
            items[new_key] = v
    return items

def extract_numeric_field(val):
    # Try to extract a single number from a value that may be a list, dict, or primitive
    if isinstance(val, list):
        # If it's a list of numbers, return the first number
        for v in val:
            if isinstance(v, (int, float)):
                return v
            if isinstance(v, list):
                # Nested list: try to extract from first element
                num = extract_numeric_field(v)
                if num is not None:
                    return num
            if isinstance(v, dict):
                num = extract_numeric_field(list(v.values()))
                if num is not None:
                    return num
        return None
    if isinstance(val, dict):
        # Try to extract from values
        for v in val.values():
            num = extract_numeric_field(v)
            if num is not None:
                return num
        return None
    if isinstance(val, (int, float)):
        return val
    # Sometimes a string number
    if isinstance(val, str):
        try:
            return int(val)
        except Exception:
            try:
                return float(val)
            except Exception:
                return None
    return None

def listing_to_flatdict(listing, data):
    # Recursively resolve and flatten all fields, fully resolving references
    resolved = {}
    for k, v in listing.items():
        val = resolve_value(v, data)
        # Debug: print all keys and values for the first listing (Wolvenplein)
        if k == "address" and "wolvenplein" in str(val).lower():
            print("DEBUG: Full resolved listing for Wolvenplein:")
            import pprint
            pprint.pprint({kk: resolve_value(vv, data) for kk, vv in listing.items()})
        if k == "floor_area":
            print(f"DEBUG: Raw floor_area value: {val}")
        if k in ("floor_area", "plot_area", "number_of_rooms", "number_of_bedrooms"):
            resolved[k] = extract_numeric_field(val)
        elif isinstance(val, dict):
            for fk, fv in flatten_dict(val, k).items():
                resolved[fk] = fv
        elif isinstance(val, list) and val and isinstance(val[0], dict):
            for i, item in enumerate(val):
                if isinstance(item, dict):
                    for fk, fv in flatten_dict(item, f"{k}[{i}]").items():
                        resolved[fk] = fv
                else:
                    resolved[f"{k}[{i}]"] = item
        else:
            resolved[k] = val
    return resolved


def main():
    listings_obj = get_listings_obj(data)
    if not listings_obj:
        print(json.dumps({"error": "No listings found."}, ensure_ascii=False, indent=2))
        return
    all_listings = []
    all_full = []
    for ref in listings_obj:
        actual_listing = resolve_listing(ref, data)
        if isinstance(actual_listing, dict):
            flat = listing_to_flatdict(actual_listing, data)
            all_listings.append(flat)
            all_full.append(actual_listing)
        elif isinstance(actual_listing, list):
            for d in actual_listing:
                if isinstance(d, dict):
                    flat = listing_to_flatdict(d, data)
                    all_listings.append(flat)
                    all_full.append(d)

    # Select most important fields for summary
    important_keys = [
        'id',
        'object_type',
        'type',
        'address.street_name',
        'address.house_number',
        'address.postal_code',
        'address.city',
        'price.rent_price',
        'price.rent_price_type',
        'energy_label',
        'floor_area',
        'plot_area',
        'object_detail_page_relative_url',
        'publish_date',
        'status',
        'number_of_bedrooms',
        'number_of_rooms',
        'construction_type',
        'offering_type',
        'zoning',
        'agent.name',
        'agent.id',
    ]

    combined_listings = []
    for flat, full in zip(all_listings, all_full):
        summary = {k: flat.get(k) for k in important_keys if k in flat}
        combined_listings.append({
            "summary": summary,
            "full": flat
        })

    with open("funda_uc_listings.jsonl", "w", encoding="utf-8") as f:
        for obj in combined_listings:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

    print(f"Saved {len(combined_listings)} listings to funda_uc_listings.jsonl (summary+full per object)")

if __name__ == "__main__":
    main()
