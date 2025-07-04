# Ensure imports and app initialization are at the top
import os
import json
import time
import requests
from fastapi import FastAPI, HTTPException, Query, Request, Body, status, Response
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import periodic scraper
from periodic_scraper import periodic_scraper

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    periodic_scraper.start()
    yield
    # Shutdown
    periodic_scraper.stop()

app = FastAPI(lifespan=lifespan)

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# New unified database file
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "../database.json")

app.mount("/static", StaticFiles(directory=os.path.dirname(__file__)), name="static")


# --- NEW PROFILE-DRIVEN ENDPOINTS ---

def load_db():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_db(db):
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# Get all listings (optionally for a profile)

@app.delete("/api/profiles/{profile_id}")
async def delete_profile(profile_id: str):
    db = load_db()
    if profile_id not in db:
        raise HTTPException(status_code=404, detail="Profile not found")
    del db[profile_id]
    save_db(db)
    
    # Remove periodic job for this profile
    periodic_scraper.remove_profile_job(profile_id)
    
    return Response(status_code=204)

@app.get("/api/listings")
def get_listings(profile_id: str = None):
    db = load_db()
    if profile_id:
        profile = db.get(profile_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return {"listings": profile.get("listings", [])}
    # If no profile_id, return all listings from all profiles (flattened)
    all_listings = []
    for p in db.values():
        all_listings.extend(p.get("listings", []))
    return {"listings": all_listings}

# Get all profiles (for frontend dropdown)
@app.get("/api/profiles")
def get_profiles():
    db = load_db()
    # Return a list of profiles with id and main fields for dropdowns
    return [
        {"id": pid, "name": p.get("name"), "filters": p.get("filters", {}), "emails": p.get("emails", []), "listings": p.get("listings", [])}
        for pid, p in db.items()
    ]

# Update email(s) for a profile
@app.put("/api/profiles/{profile_id}/email")
async def update_profile_email(profile_id: str, body: dict = Body(...)):
    db = load_db()
    if profile_id not in db:
        raise HTTPException(status_code=404, detail="Profile not found")
    emails = body.get("emails")
    # Accept both 'email' (legacy) and 'emails' (list)
    if emails is None:
        email = body.get("email", "")
        if isinstance(email, list):
            emails = email
        elif isinstance(email, str) and email:
            emails = [email]
        else:
            emails = []
    db[profile_id]["emails"] = emails
    # Remove legacy 'email' field if present
    if "email" in db[profile_id]:
        del db[profile_id]["email"]
    save_db(db)
    return {"profileId": profile_id, "emails": emails}

# Update complete profile (name, filters, emails)
@app.put("/api/profiles/{profile_id}")
async def update_profile(profile_id: str, request: Request):
    data = await request.json()
    db = load_db()
    if profile_id not in db:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    name = data.get("name")
    filters = data.get("filters")
    emails = data.get("emails")
    scrape_interval_hours = data.get("scrape_interval_hours")
    
    # Accept both 'email' (legacy) and 'emails' (list)
    if emails is None:
        email = data.get("email", "")
        if isinstance(email, list):
            emails = email
        elif isinstance(email, str) and email:
            emails = [email]
        else:
            emails = []
    
    # Update the profile data
    if name:
        db[profile_id]["name"] = name
    if filters is not None:
        db[profile_id]["filters"] = filters
    if emails is not None:
        db[profile_id]["emails"] = emails
        # Remove legacy 'email' field if present
        if "email" in db[profile_id]:
            del db[profile_id]["email"]
    if scrape_interval_hours is not None:
        db[profile_id]["scrape_interval_hours"] = scrape_interval_hours
        # Update the periodic job with new interval
        periodic_scraper.add_profile_job(profile_id, scrape_interval_hours)
    
    save_db(db)
    return {"id": profile_id, **db[profile_id]}


@app.get("/api/data")
def get_all_data():
    """Return the entire database.json contents."""
    return load_db()


@app.post("/api/profiles")
async def create_profile(request: Request):
    data = await request.json()
    name = data.get("name")
    filters = data.get("filters")
    emails = data.get("emails")
    scrape_interval_hours = data.get("scrape_interval_hours", 4)  # Default 4 hours
    
    # Accept both 'email' (legacy) and 'emails' (list)
    if emails is None:
        email = data.get("email", "")
        if isinstance(email, list):
            emails = email
        elif isinstance(email, str) and email:
            emails = [email]
        else:
            emails = []
    if not name or not filters:
        raise HTTPException(status_code=400, detail="Missing name or filters")
    db = load_db()
    profile_id = f"profile_{int(time.time())}"
    db[profile_id] = {
        "name": name,
        "filters": filters,
        "emails": emails,
        "scrape_interval_hours": scrape_interval_hours,
        "listings": [],
        "created_at": time.time(),
        "last_scraped": None,
        "last_new_listings_count": 0
    }
    save_db(db)
    
    # Add periodic job for this profile
    periodic_scraper.add_profile_job(profile_id, scrape_interval_hours)
    
    return {"profileId": profile_id, **db[profile_id]}


# --- PERIODIC SCRAPING ENDPOINTS ---

@app.get("/api/scraper/status")
def get_scraper_status():
    """Get the current status of the periodic scraper"""
    return periodic_scraper.get_status()

@app.post("/api/scraper/start")
def start_scraper():
    """Start the periodic scraper"""
    if not periodic_scraper.is_running:
        periodic_scraper.start()
        return {"message": "Periodic scraper started", "status": "success"}
    return {"message": "Periodic scraper is already running", "status": "info"}

@app.post("/api/scraper/stop")
def stop_scraper():
    """Stop the periodic scraper"""
    if periodic_scraper.is_running:
        periodic_scraper.stop()
        return {"message": "Periodic scraper stopped", "status": "success"}
    return {"message": "Periodic scraper is not running", "status": "info"}

@app.post("/api/scraper/sync")
def sync_scraper():
    """Sync scraper jobs with current profiles"""
    periodic_scraper.sync_jobs_with_profiles()
    return {"message": "Scraper jobs synchronized", "status": "success"}

@app.post("/api/profiles/{profile_id}/scrape")
def trigger_profile_scrape(profile_id: str):
    """Manually trigger a scrape for a specific profile"""
    result = periodic_scraper.trigger_profile_scrape(profile_id)
    if result["success"]:
        return {"message": result["message"], "status": "success"}
    else:
        raise HTTPException(status_code=500, detail=result["message"])

@app.put("/api/profiles/{profile_id}/interval")
async def update_scrape_interval(profile_id: str, body: dict = Body(...)):
    """Update the scraping interval for a specific profile"""
    db = load_db()
    if profile_id not in db:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    interval_hours = body.get("interval_hours")
    if interval_hours is None or interval_hours <= 0:
        raise HTTPException(status_code=400, detail="Invalid interval_hours")
    
    db[profile_id]["scrape_interval_hours"] = interval_hours
    save_db(db)
    
    # Update the periodic job
    periodic_scraper.add_profile_job(profile_id, interval_hours)
    
    return {"profileId": profile_id, "interval_hours": interval_hours}

# --- SCRAPING ENDPOINTS ---

# Use the scrape_api router for /scrape_listings
from scrape_api import router as scrape_router
app.include_router(scrape_router)


@app.post("/api/scrape/{profile_id}")
def scrape_profile(profile_id: str):
    """
    Scrape for a specific profile using the same logic as /scrape_listings.
    """
    from .funda_url_builder import build_rental_url
    from .scrape_funda import scrape_funda_html
    from .extract_funda_listings import extract_simple_listings_from_html
    from .listing_mapping import map_listing_for_frontend
    db = load_db()
    if profile_id not in db:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = db[profile_id]
    filters = profile.get("filters", {})
    # Build URL and scrape
    url = build_rental_url(**filters)
    html = scrape_funda_html(url)
    listings = extract_simple_listings_from_html(html)
    # Deduplicate by funda_url or object_detail_page_relative_url
    existing_urls = set()
    for l in profile["listings"]:
        url = l.get("funda_url") or l.get("object_detail_page_relative_url")
        if url:
            existing_urls.add(url)
    new_listings = []
    for l in listings:
        url = l.get("funda_url") or l.get("object_detail_page_relative_url")
        if url and url not in existing_urls:
            mapped = map_listing_for_frontend(l)
            mapped["is_new"] = True
            new_listings.append(mapped)
            profile["listings"].append(mapped)
            existing_urls.add(url)
    # Mark all others as not new
    for l in profile["listings"]:
        url = l.get("funda_url") or l.get("object_detail_page_relative_url")
        if url and (l not in new_listings):
            l["is_new"] = False

    # Send email notification if new listings and emails are set
    if new_listings and profile.get("emails"):
        from .email_utils import send_new_listings_email
        send_new_listings_email(profile["emails"], profile.get("name", profile_id), new_listings)

    save_db(db)
    return {"listings": profile["listings"]}


# Serve the listings HTML page
@app.get("/")
def root():
    from fastapi.responses import HTMLResponse
    html_path = os.path.join(os.path.dirname(__file__), "listings.html")
    with open(html_path, encoding="utf-8") as f:
        return HTMLResponse(f.read())

# Serve favicon
@app.get("/favicon.ico")
def favicon():
    return Response(content="🏠", media_type="text/plain")

