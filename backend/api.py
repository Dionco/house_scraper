
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import json
import os
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from scrape_api import router as scrape_router
app = FastAPI()

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LISTINGS_FILE = os.path.join(os.path.dirname(__file__), "funda_simple_listings.json")

app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")
app.include_router(scrape_router)

# Load all listings into memory at startup
@app.get("/")
def root():
    """Serve the listings HTML page."""
    from fastapi.responses import HTMLResponse
    html_path = os.path.join(os.path.dirname(__file__), "listings.html")
    with open(html_path, encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Load all listings into memory at startup (from JSON array)
@app.on_event("startup")
def load_listings():
    app.state.listings = []
    if os.path.exists(LISTINGS_FILE):
        with open(LISTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                listings = json.load(f)
                if isinstance(listings, list):
                    app.state.listings = listings
            except Exception:
                pass




# Return all listings, but map fields to the frontend HTML expectations, with filtering
from fastapi import Query
@app.get("/listings")
def get_listings(
    city: str = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    property_type: str = Query(None),
    listed_since_days: int = Query(None),
    status: str = Query(None),
    min_floor_area: int = Query(None),
    max_floor_area: int = Query(None),
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
    service_costs_included: bool = Query(None),
    service_costs_excluded: bool = Query(None),
    construction_type: str = Query(None),
    build_period: str = Query(None),
    balcony: bool = Query(None),
    roof_terrace: bool = Query(None),
    garden: bool = Query(None),
    lift: bool = Query(None),
    single_floor: bool = Query(None),
    disabled_access: bool = Query(None),
    elderly_access: bool = Query(None),
    keyword: str = Query(None)
):
    mapped = []
    from datetime import datetime, timedelta
    today = datetime.now().date()
    for l in app.state.listings:
        mapped_listing = {
            'address.street_name': l.get('address') or l.get('address.street_name'),
            'address.house_number': l.get('address.house_number'),
            'address.postal_code': l.get('area_code') or l.get('address.postal_code'),
            'address.city': l.get('city') or l.get('address.city'),
            'price.rent_price': l.get('price') or l.get('price.rent_price'),
            'price.rent_price_type': l.get('price.rent_price_type', 'per maand'),
            'floor_area': l.get('area') or l.get('floor_area'),
            'plot_area': l.get('plot_area'),
            'number_of_rooms': l.get('bedrooms') or l.get('number_of_rooms'),
            'number_of_bedrooms': l.get('bedrooms') or l.get('number_of_bedrooms'),
            'number_of_bathrooms': l.get('bathrooms') or l.get('number_of_bathrooms'),
            'energy_label': l.get('energy_label'),
            'object_type': l.get('object_type'),
            'type': l.get('type'),
            'status': l.get('status'),
            'agent.name': l.get('agent.name'),
            'publish_date': l.get('publish_date'),
            'object_detail_page_relative_url': l.get('funda_url') or l.get('object_detail_page_relative_url'),
            'image_url': l.get('image_url'),
            'listed_since': l.get('listed_since'),
            'listed_days_ago': l.get('listed_days_ago'),
            'furnished': l.get('furnished'),
            'partly_furnished': l.get('partly_furnished'),
            'service_costs_included': l.get('service_costs_included'),
            'service_costs_excluded': l.get('service_costs_excluded'),
            'construction_type': l.get('construction_type'),
            'build_period': l.get('build_period'),
            'balcony': l.get('balcony'),
            'roof_terrace': l.get('roof_terrace'),
            'garden': l.get('garden'),
            'lift': l.get('lift'),
            'single_floor': l.get('single_floor'),
            'disabled_access': l.get('disabled_access'),
            'elderly_access': l.get('elderly_access'),
            'description': l.get('description', ''),
        }
        # Filtering
        if city:
            city_val = (mapped_listing['address.city'] or '').lower()
            if city.lower() not in city_val:
                continue
        # Price range
        price = mapped_listing['price.rent_price']
        if isinstance(price, str):
            try:
                price = int(''.join(filter(str.isdigit, price)))
            except:
                price = 0
        if min_price is not None and (not price or price < min_price):
            continue
        if max_price is not None and (not price or price > max_price):
            continue
        # Property type
        if property_type:
            type_val = (mapped_listing['object_type'] or mapped_listing['type'] or '').lower()
            if property_type.lower() not in type_val:
                continue
        # Listed since days
        if listed_since_days is not None:
            pub_date = mapped_listing['publish_date']
            try:
                pub_date_dt = datetime.strptime(pub_date[:10], '%Y-%m-%d').date()
                if (today - pub_date_dt).days > listed_since_days:
                    continue
            except:
                continue
        # Status
        if status:
            if not mapped_listing['status'] or status.lower() not in mapped_listing['status'].lower():
                continue
        # Living area
        floor_area = mapped_listing['floor_area']
        if isinstance(floor_area, str):
            try:
                floor_area = int(''.join(filter(str.isdigit, floor_area)))
            except:
                floor_area = 0
        if min_floor_area is not None and (not floor_area or floor_area < min_floor_area):
            continue
        if max_floor_area is not None and (not floor_area or floor_area > max_floor_area):
            continue
        # Plot area
        plot_area = mapped_listing['plot_area']
        if isinstance(plot_area, str):
            try:
                plot_area = int(''.join(filter(str.isdigit, plot_area)))
            except:
                plot_area = 0
        if min_plot_area is not None and (not plot_area or plot_area < min_plot_area):
            continue
        if max_plot_area is not None and (not plot_area or plot_area > max_plot_area):
            continue
        # Rooms
        rooms = mapped_listing['number_of_rooms']
        if isinstance(rooms, str):
            try:
                rooms = int(''.join(filter(str.isdigit, rooms)))
            except:
                rooms = 0
        if min_rooms is not None and (not rooms or rooms < min_rooms):
            continue
        if max_rooms is not None and (not rooms or rooms > max_rooms):
            continue
        # Bedrooms
        bedrooms = mapped_listing['number_of_bedrooms']
        if isinstance(bedrooms, str):
            try:
                bedrooms = int(''.join(filter(str.isdigit, bedrooms)))
            except:
                bedrooms = 0
        if min_bedrooms is not None and (not bedrooms or bedrooms < min_bedrooms):
            continue
        if max_bedrooms is not None and (not bedrooms or bedrooms > max_bedrooms):
            continue
        # Bathrooms
        bathrooms = mapped_listing.get('number_of_bathrooms')
        if isinstance(bathrooms, str):
            try:
                bathrooms = int(''.join(filter(str.isdigit, bathrooms)))
            except:
                bathrooms = 0
        if min_bathrooms is not None and (not bathrooms or bathrooms < min_bathrooms):
            continue
        if max_bathrooms is not None and (not bathrooms or bathrooms > max_bathrooms):
            continue
        # Energy label
        if energy_label:
            if not mapped_listing['energy_label'] or energy_label.upper() != mapped_listing['energy_label'].upper():
                continue
        # Furnishing
        if furnished is not None:
            if bool(mapped_listing.get('furnished')) != furnished:
                continue
        if partly_furnished is not None:
            if bool(mapped_listing.get('partly_furnished')) != partly_furnished:
                continue
        # Service costs
        if service_costs_included is not None:
            if bool(mapped_listing.get('service_costs_included')) != service_costs_included:
                continue
        if service_costs_excluded is not None:
            if bool(mapped_listing.get('service_costs_excluded')) != service_costs_excluded:
                continue
        # Construction type
        if construction_type:
            if not mapped_listing.get('construction_type') or construction_type.lower() not in mapped_listing['construction_type'].lower():
                continue
        # Build period
        if build_period:
            if not mapped_listing.get('build_period') or build_period not in mapped_listing['build_period']:
                continue
        # Outdoor space
        if balcony is not None:
            if bool(mapped_listing.get('balcony')) != balcony:
                continue
        if roof_terrace is not None:
            if bool(mapped_listing.get('roof_terrace')) != roof_terrace:
                continue
        if garden is not None:
            if bool(mapped_listing.get('garden')) != garden:
                continue
        # Accessibility
        if lift is not None:
            if bool(mapped_listing.get('lift')) != lift:
                continue
        if single_floor is not None:
            if bool(mapped_listing.get('single_floor')) != single_floor:
                continue
        if disabled_access is not None:
            if bool(mapped_listing.get('disabled_access')) != disabled_access:
                continue
        if elderly_access is not None:
            if bool(mapped_listing.get('elderly_access')) != elderly_access:
                continue
        # Keyword search
        if keyword:
            if keyword.lower() not in (mapped_listing.get('description', '').lower()):
                continue
        mapped.append(mapped_listing)
    return mapped

@app.get("/listings/{listing_id}")
def get_listing(listing_id: int):
    """Return full info for a single listing by id"""
    for l in app.state.listings:
        if l["summary"].get("id") == listing_id:
            return l
    raise HTTPException(status_code=404, detail="Listing not found")

@app.get("/listings/{listing_id}/summary")
def get_listing_summary(listing_id: int):
    for l in app.state.listings:
        if l["summary"].get("id") == listing_id:
            return l["summary"]
    raise HTTPException(status_code=404, detail="Listing not found")

@app.get("/listings/{listing_id}/full")
def get_listing_full(listing_id: int):
    for l in app.state.listings:
        if l["summary"].get("id") == listing_id:
            return l["full"]
    raise HTTPException(status_code=404, detail="Listing not found")
