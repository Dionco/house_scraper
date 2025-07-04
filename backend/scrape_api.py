
from fastapi import APIRouter, Query
from funda_url_builder import build_rental_url
from scrape_funda import scrape_funda_html
from extract_funda_listings import extract_simple_listings_from_html
from listing_mapping import map_listing_for_frontend

router = APIRouter()

@router.get("/scrape_listings")
def scrape_listings(
    city: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    property_type: str = Query(None),
    min_floor_area: int = Query(None),
    max_floor_area: int = Query(None),
    min_area: int = Query(None),
    max_area: int = Query(None),
    min_plot_area: int = Query(None),
    max_plot_area: int = Query(None),
    min_rooms: int = Query(None),
    max_rooms: int = Query(None),
    min_bedrooms: int = Query(None),
    max_bedrooms: int = Query(None),
    min_bathrooms: int = Query(None),
    max_bathrooms: int = Query(None),
    energy_label: str = Query(None),
    furnished: bool = Query(None),
    partly_furnished: bool = Query(None),
    balcony: bool = Query(None),
    roof_terrace: bool = Query(None),
    garden: bool = Query(None),
    garden_orientation: str = Query(None),
    parking: bool = Query(None),
    garage: bool = Query(None),
    lift: bool = Query(None),
    single_floor: bool = Query(None),
    disabled_access: bool = Query(None),
    elderly_access: bool = Query(None),
    construction_type: str = Query(None),
    build_period: str = Query(None),
    listed_since: int = Query(None),
    status: str = Query(None),
    available_from: str = Query(None),
    service_costs_included: bool = Query(None),
    service_costs_excluded: bool = Query(None),
    min_service_costs: int = Query(None),
    max_service_costs: int = Query(None),
    keyword: str = Query(None),
    object_type: str = Query(None),
    sort_by: str = Query(None),
    page: int = Query(None),
    per_page: int = Query(None),
    use_modern_url: bool = Query(True)
):
    import os, json
    # Prefer min_area/max_area if present (from frontend), else fallback to min_floor_area/max_floor_area
    min_floor_area_final = min_area if min_area is not None else min_floor_area
    max_floor_area_final = max_area if max_area is not None else max_floor_area
    # Parse list-like fields (object_type, garden_orientation, energy_label)
    object_type_list = object_type.split(',') if object_type else None
    garden_orientation_list = garden_orientation.split(',') if garden_orientation else None
    energy_label_list = [energy_label] if energy_label else None
    print("[DEBUG] Building Funda URL with:", dict(
        city=city, property_type=property_type, min_price=min_price, max_price=max_price,
        min_floor_area=min_floor_area_final, max_floor_area=max_floor_area_final,
        min_plot_area=min_plot_area, max_plot_area=max_plot_area,
        min_rooms=min_rooms, max_rooms=max_rooms,
        min_bedrooms=min_bedrooms, max_bedrooms=max_bedrooms,
        min_bathrooms=min_bathrooms, max_bathrooms=max_bathrooms,
        energy_label=energy_label_list, furnished=furnished, partly_furnished=partly_furnished,
        balcony=balcony, roof_terrace=roof_terrace, garden=garden, garden_orientation=garden_orientation_list,
        parking=parking, garage=garage, lift=lift, single_floor=single_floor, disabled_access=disabled_access, elderly_access=elderly_access,
        construction_type=construction_type, build_period=build_period, listed_since=listed_since, status=status, available_from=available_from,
        service_costs_included=service_costs_included, service_costs_excluded=service_costs_excluded, min_service_costs=min_service_costs, max_service_costs=max_service_costs,
        keyword=keyword, object_type=object_type_list, sort_by=sort_by, page=page, per_page=per_page, use_modern_url=use_modern_url
    ))
    url = build_rental_url(
        city=city,
        property_type=property_type,
        min_price=min_price,
        max_price=max_price,
        min_floor_area=min_floor_area_final,
        max_floor_area=max_floor_area_final,
        min_plot_area=min_plot_area,
        max_plot_area=max_plot_area,
        min_rooms=min_rooms,
        max_rooms=max_rooms,
        min_bedrooms=min_bedrooms,
        max_bedrooms=max_bedrooms,
        min_bathrooms=min_bathrooms,
        max_bathrooms=max_bathrooms,
        energy_label=energy_label_list,
        furnished=furnished,
        partly_furnished=partly_furnished,
        balcony=balcony,
        roof_terrace=roof_terrace,
        garden=garden,
        garden_orientation=garden_orientation_list,
        parking=parking,
        garage=garage,
        lift=lift,
        single_floor=single_floor,
        disabled_access=disabled_access,
        elderly_access=elderly_access,
        construction_type=construction_type,
        build_period=build_period,
        listed_since_days=listed_since,
        status=status,
        available_from=available_from,
        service_costs_included=service_costs_included,
        service_costs_excluded=service_costs_excluded,
        min_service_costs=min_service_costs,
        max_service_costs=max_service_costs,
        keyword=keyword,
        object_type=object_type_list,
        sort_by=sort_by,
        page=page,
        per_page=per_page,
        use_modern_url=use_modern_url
    )
    print(f"[DEBUG] Built Funda URL: {url}")
    html = scrape_funda_html(url)
    print(f"[DEBUG] Scraped HTML length: {len(html) if html else 'None'}")
    listings = extract_simple_listings_from_html(html)
    print(f"[DEBUG] Extracted {len(listings)} listings from HTML")

    # Map all listings to frontend-compatible format before saving/returning
    mapped_listings = [map_listing_for_frontend(l) for l in listings]

    # Deduplicate and append to funda_simple_listings.json
    json_path = os.path.join(os.path.dirname(__file__), "funda_simple_listings.json")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        print(f"[DEBUG] Loaded {len(existing)} existing listings from JSON")
    except Exception as e:
        print(f"[DEBUG] Could not load existing JSON: {e}")
        existing = []
    # Use funda_url as unique key
    existing_urls = {l.get("object_detail_page_relative_url") or l.get("funda_url") for l in existing if l.get("object_detail_page_relative_url") or l.get("funda_url")}
    new_unique = [l for l in mapped_listings if (l.get("object_detail_page_relative_url") or l.get("funda_url")) and (l.get("object_detail_page_relative_url") or l.get("funda_url")) not in existing_urls]
    print(f"[DEBUG] {len(new_unique)} new unique listings to add")
    if new_unique:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(existing + new_unique, f, ensure_ascii=False, indent=2)
        print(f"[DEBUG] Wrote {len(existing) + len(new_unique)} total listings to JSON")
    return {"url": url, "count": len(mapped_listings), "added": len(new_unique), "listings": mapped_listings}
