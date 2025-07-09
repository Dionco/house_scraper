# Ensure imports and app initialization are at the top
import os
import json
import time
import inspect
import requests
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Request, Body, status, Response, Depends
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Optional, List, Dict, Any

def is_running_on_railway() -> bool:
    """Check if the application is running on Railway."""
    return any([
        os.getenv("RAILWAY_ENVIRONMENT"),
        os.getenv("RAILWAY_PROJECT_ID"),
        os.getenv("RAILWAY_SERVICE_ID"),
        os.getenv("PORT")  # Railway sets this automatically
    ])

# Try to import timezone utilities, fallback if not available
try:
    from .timezone_utils import now_cest_iso, get_timezone_info
    TIMEZONE_UTILS_AVAILABLE = True
except ImportError:
    try:
        from timezone_utils import now_cest_iso, get_timezone_info
        TIMEZONE_UTILS_AVAILABLE = True
    except ImportError:
        TIMEZONE_UTILS_AVAILABLE = False
        print("Warning: timezone_utils not available, using fallback timezone handling")

# Import authentication utilities and models
try:
    from .auth_utils import (
        get_current_user, 
        get_optional_user, 
        generate_tokens, 
        generate_user_id, 
        create_user_dict, 
        AuthUtils,
        blacklist_token,
        is_token_blacklisted
    )
    from .auth_models import (
        UserRegister, 
        UserLogin, 
        UserResponse, 
        UserUpdate, 
        TokenResponse, 
        TokenRefresh,
        ProfileCreate, 
        ProfileUpdate, 
        ProfileResponse, 
        EmailUpdate,
        ScrapeIntervalUpdate,
        UserProfileUpdate
    )
except ImportError:
    from auth_utils import (
        get_current_user, 
        get_optional_user, 
        generate_tokens, 
        generate_user_id, 
        create_user_dict, 
        AuthUtils,
        blacklist_token,
        is_token_blacklisted
    )
    from auth_models import (
        UserRegister, 
        UserLogin, 
        UserResponse, 
        UserUpdate, 
        TokenResponse, 
        TokenRefresh,
        ProfileCreate, 
        ProfileUpdate, 
        ProfileResponse, 
        EmailUpdate,
        ScrapeIntervalUpdate,
        UserProfileUpdate
    )

# Import periodic scraper with Railway optimization
import logging
logger = logging.getLogger(__name__)

try:
    # Try Railway-optimized scraper first
    if is_running_on_railway():
        from .railway_periodic_scraper import periodic_scraper
        logger.info("Using Railway-optimized periodic scraper")
    else:
        from .periodic_scraper import periodic_scraper
        logger.info("Using standard periodic scraper")
except ImportError:
    try:
        if is_running_on_railway():
            from railway_periodic_scraper import periodic_scraper
            logger.info("Using Railway-optimized periodic scraper")
        else:
            from periodic_scraper import periodic_scraper
            logger.info("Using standard periodic scraper")
    except ImportError:
        logger.error("Could not import periodic scraper")
        periodic_scraper = None

# Import scraping API
try:
    from .scrape_api import router as scrape_router
except ImportError:
    from scrape_api import router as scrape_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if periodic_scraper:
        try:
            periodic_scraper.start()
            logger.info("Application started with periodic scraper")
        except Exception as e:
            logger.error(f"Failed to start periodic scraper: {e}")
    else:
        logger.warning("Periodic scraper not available")
    
    yield
    
    # Shutdown
    if periodic_scraper:
        try:
            periodic_scraper.stop()
            logger.info("Application shutdown with periodic scraper stopped")
        except Exception as e:
            logger.error(f"Error stopping periodic scraper: {e}")

app = FastAPI(lifespan=lifespan)

# Enable CORS for all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the scraping API router
app.include_router(scrape_router, prefix="/api")

# New unified database file
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "../database.json")

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

# Mount frontend static files
frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")


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

# Health check endpoint for Railway deployment
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway deployment"""
    if TIMEZONE_UTILS_AVAILABLE:
        return {"status": "healthy", "timestamp": now_cest_iso(), "timezone": get_timezone_info()}
    else:
        # Fallback if timezone_utils import fails
        return {"status": "healthy", "timestamp": datetime.now().isoformat(), "timezone": "fallback"}

# Admin page endpoint
@app.get("/admin-scraper.html", response_class=HTMLResponse)
async def admin_scraper_page():
    """Serve the admin scraper management page"""
    admin_html_path = os.path.join(os.path.dirname(__file__), "admin-scraper.html")
    if os.path.exists(admin_html_path):
        with open(admin_html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return HTMLResponse(
            content="<h1>Admin page not found</h1><p>The admin-scraper.html file was not found.</p>",
            status_code=404
        )

# Root endpoint - Serve the landing page with security headers
@app.get("/", response_class=HTMLResponse)
async def root(response: Response):
    """Root endpoint - Serve the landing page with authentication"""
    # Add security headers to prevent extension interference
    response.headers["Content-Security-Policy"] = "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com; object-src 'none'; frame-ancestors 'self';"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    index_html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_html_path):
        with open(index_html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback to API landing page
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>House Scraper</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2em; background-color: #f5f5f5; }
                .container { max-width: 800px; margin: 0 auto; background: white; padding: 2em; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; text-align: center; }
                .feature { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
                .api-link { display: inline-block; margin: 10px 10px 10px 0; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                .api-link:hover { background: #0056b3; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏠 House Scraper</h1>
                <div class="feature">
                    <h3>Landing Page Not Found</h3>
                    <p>The landing page file is missing. Please check the deployment.</p>
                    <a href="/api" class="api-link">API Documentation</a>
                </div>
            </div>
        </body>
        </html>
        """

# Dashboard endpoint - Serve the main dashboard after authentication with security headers
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(response: Response):
    """Dashboard endpoint - Serve the main listings UI"""
    # Add security headers
    response.headers["Content-Security-Policy"] = "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com; object-src 'none'; frame-ancestors 'self';"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    listings_html_path = os.path.join(os.path.dirname(__file__), "listings.html")
    if os.path.exists(listings_html_path):
        with open(listings_html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback to frontend if listings.html not found
        frontend_html_path = os.path.join(os.path.dirname(__file__), "../frontend/index.html")
        if os.path.exists(frontend_html_path):
            with open(frontend_html_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Final fallback to API landing page
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>House Scraper Dashboard</title>
                <style>
                    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 2em; background-color: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 2em; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; text-align: center; }
                    .feature { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 5px; border-left: 4px solid #007bff; }
                    .api-link { display: inline-block; margin: 10px 10px 10px 0; padding: 10px 20px; background: #007bff; color: white; text-decoration: none; border-radius: 5px; }
                    .api-link:hover { background: #0056b3; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏠 House Scraper Dashboard</h1>
                    <div class="feature">
                        <h3>Dashboard Not Found</h3>
                        <p>The dashboard file is missing. Please check the deployment.</p>
                        <a href="/api" class="api-link">API Documentation</a>
                    </div>
                </div>
            </body>
            </html>
            """

# API landing page endpoint
@app.get("/api", response_class=HTMLResponse)
async def api_info():
    """API information landing page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>House Scraper API</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 40px 20px;
                background-color: #f5f5f5;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 30px;
            }
            .feature {
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 5px;
                border-left: 4px solid #007bff;
            }
            .api-link {
                display: inline-block;
                margin: 10px 10px 10px 0;
                padding: 10px 20px;
                background: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background-color 0.3s;
            }
            .api-link:hover {
                background: #0056b3;
            }
            .status {
                text-align: center;
                margin: 30px 0;
                padding: 15px;
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
                color: #155724;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏠 House Scraper API</h1>
            
            <div class="status">
                <strong>✅ API is running successfully!</strong>
            </div>
            
            <div class="feature">
                <h3>📊 Features</h3>
                <ul>
                    <li>Automated house listing scraping from Funda</li>
                    <li>User authentication and profile management</li>
                    <li>Customizable search profiles</li>
                    <li>Periodic scraping with email notifications</li>
                    <li>RESTful API endpoints</li>
                </ul>
            </div>
            
            <div class="feature">
                <h3>🔗 API Endpoints</h3>
                <a href="/docs" class="api-link">📚 API Documentation</a>
                <a href="/health" class="api-link">🏥 Health Check</a>
                <a href="/api/data" class="api-link">📋 View Data</a>
            </div>
            
            <div class="feature">
                <h3>🚀 Quick Start</h3>
                <p>Visit the <strong>API Documentation</strong> above to explore all available endpoints and try them out interactively.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

# --- PROFILE ENDPOINTS (UPDATED FOR USER AUTHENTICATION) ---

@app.get("/api/profiles", response_model=List[ProfileResponse])
async def get_user_profiles(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get all profiles for the current user."""
    db = load_db()
    profiles = db.get("profiles", {})
    user_id = current_user["id"]
    
    # Track if we need to save the database
    db_updated = False
    
    user_profiles = []
    for profile_id, profile in profiles.items():
        if profile.get("user_id") == user_id:
            # Update listing timestamps and ensure correct is_new flags
            listings = profile.get("listings", [])
            original_listings_length = len([l for l in listings if l.get("added_timestamp")])
            update_listing_timestamps(listings)
            new_listings_length = len([l for l in listings if l.get("added_timestamp")])
            
            # If timestamps were added, mark for database save
            if new_listings_length > original_listings_length:
                db_updated = True
            
            # Convert last_scraped from ISO string to timestamp if needed
            last_scraped = profile.get("last_scraped")
            if last_scraped and isinstance(last_scraped, str):
                try:
                    dt = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
                    # Convert to milliseconds for JavaScript Date() compatibility
                    last_scraped = dt.timestamp() * 1000
                except:
                    last_scraped = None
            elif not last_scraped:
                # Ensure null/None values stay as None (not 0 or other falsy values)
                last_scraped = None
            
            profile_response = ProfileResponse(
                id=profile_id,
                user_id=profile["user_id"],
                name=profile["name"],
                filters=profile.get("filters", {}),
                emails=profile.get("emails", []),
                scrape_interval_hours=profile.get("scrape_interval_hours"),
                scrape_interval_minutes=profile.get("scrape_interval_minutes"),
                created_at=profile.get("created_at", 0),
                last_scraped=last_scraped,
                last_new_listings_count=profile.get("last_new_listings_count", 0),
                listings_count=len(listings),
                new_today_count=calculate_new_today_count(listings)
            )
            user_profiles.append(profile_response)
    
    # Save database if any timestamps were added
    if db_updated:
        save_db(db)
    
    return user_profiles

@app.post("/api/profiles", response_model=ProfileResponse)
async def create_user_profile(
    profile_data: ProfileCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create a new profile for the current user."""
    db = load_db()
    
    # Ensure profiles section exists
    if "profiles" not in db:
        db["profiles"] = {}
    
    profiles = db["profiles"]
    users = db.get("users", {})
    user_id = current_user["id"]
    
    # Generate profile ID
    profile_id = f"profile_{int(time.time())}"
    
    # Create profile
    profile = {
        "id": profile_id,
        "user_id": user_id,
        "name": profile_data.name,
        "filters": profile_data.filters,
        "emails": profile_data.emails,
        "listings": [],
        "created_at": time.time(),
        "last_scraped": None,
        "last_new_listings_count": 0
    }
    
    # Set scrape interval (combined hours and minutes)
    profile["scrape_interval_hours"] = profile_data.scrape_interval_hours or 4
    profile["scrape_interval_minutes"] = profile_data.scrape_interval_minutes or 0
    
    profiles[profile_id] = profile
    
    # Update user's profile_ids
    if user_id in users:
        if "profile_ids" not in users[user_id]:
            users[user_id]["profile_ids"] = []
        users[user_id]["profile_ids"].append(profile_id)
    
    save_db(db)
    
    # Add periodic job for this profile
    try:
        from .periodic_scraper import periodic_scraper
    except ImportError:
        from periodic_scraper import periodic_scraper
    
    periodic_scraper.add_profile_job(
        profile_id, 
        combined_hours=profile["scrape_interval_hours"], 
        combined_minutes=profile["scrape_interval_minutes"]
    )
    
    # Convert last_scraped from ISO string to timestamp if needed
    last_scraped = profile.get("last_scraped")
    if last_scraped and isinstance(last_scraped, str):
        try:
            dt = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
            # Convert to milliseconds for JavaScript Date() compatibility
            last_scraped = dt.timestamp() * 1000
        except:
            last_scraped = None
    elif not last_scraped:
        # Ensure null/None values stay as None (not 0 or other falsy values)
        last_scraped = None
    
    return ProfileResponse(
        id=profile_id,
        user_id=user_id,
        name=profile["name"],
        filters=profile["filters"],
        emails=profile["emails"],
        scrape_interval_hours=profile.get("scrape_interval_hours"),
        scrape_interval_minutes=profile.get("scrape_interval_minutes"),
        created_at=profile["created_at"],
        last_scraped=last_scraped,
        last_new_listings_count=profile["last_new_listings_count"],
        listings_count=len(profile["listings"]),
        new_today_count=calculate_new_today_count(profile["listings"])
    )

# Get all listings (optionally for a profile)

@app.delete("/api/profiles/{profile_id}")
async def delete_user_profile(
    profile_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a user's profile."""
    db = load_db()
    profiles = db.get("profiles", {})
    users = db.get("users", {})
    user_id = current_user["id"]
    
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profiles[profile_id]
    
    # Check if user owns this profile
    if profile.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this profile")
    
    # Remove profile
    del profiles[profile_id]
    
    # Update user's profile_ids
    if user_id in users:
        users[user_id]["profile_ids"] = [pid for pid in users[user_id]["profile_ids"] if pid != profile_id]
    
    save_db(db)
    
    # Remove periodic job for this profile
    try:
        from .periodic_scraper import periodic_scraper
    except ImportError:
        from periodic_scraper import periodic_scraper
    periodic_scraper.remove_profile_job(profile_id)
    
    return Response(status_code=204)

@app.get("/api/listings")
def get_user_listings(
    profile_id: str = None,
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get listings for authenticated user's profiles, or all listings if not authenticated."""
    db = load_db()
    profiles = db.get("profiles", {})
    
    if current_user:
        # Authenticated user - return their listings
        user_id = current_user["id"]
        
        if profile_id:
            # Specific profile requested
            if profile_id not in profiles:
                raise HTTPException(status_code=404, detail="Profile not found")
            
            profile = profiles[profile_id]
            if profile.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="Not authorized to view this profile")
            
            return {"listings": profile.get("listings", [])}
        else:
            # All user's listings
            all_listings = []
            for profile in profiles.values():
                if profile.get("user_id") == user_id:
                    all_listings.extend(profile.get("listings", []))
            return {"listings": all_listings}
    else:
        # Not authenticated - return all listings (backward compatibility)
        if profile_id:
            profile = profiles.get(profile_id)
            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")
            return {"listings": profile.get("listings", [])}
        
        # All listings from all profiles
        all_listings = []
        for profile in profiles.values():
            all_listings.extend(profile.get("listings", []))
        return {"listings": all_listings}

# Update email(s) for a profile - Updated for user authentication
@app.put("/api/profiles/{profile_id}/email")
async def update_profile_email(
    profile_id: str, 
    email_update: EmailUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update email addresses for a user's profile."""
    db = load_db()
    profiles = db.get("profiles", {})
    user_id = current_user["id"]
    
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profiles[profile_id]
    
    # Check if user owns this profile
    if profile.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    # Update emails
    profile["emails"] = email_update.emails
    save_db(db)
    
    # Update listing timestamps and calculate new today count
    listings = profile.get("listings", [])
    update_listing_timestamps(listings)
    
    # Convert last_scraped from ISO string to timestamp if needed
    last_scraped = profile.get("last_scraped")
    if last_scraped and isinstance(last_scraped, str):
        try:
            dt = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
            # Convert to milliseconds for JavaScript Date() compatibility
            last_scraped = dt.timestamp() * 1000
        except:
            last_scraped = None
    elif not last_scraped:
        # Ensure null/None values stay as None (not 0 or other falsy values)
        last_scraped = None
    
    return ProfileResponse(
        id=profile_id,
        user_id=profile["user_id"],
        name=profile["name"],
        filters=profile["filters"],
        emails=profile["emails"],
        scrape_interval_hours=profile.get("scrape_interval_hours"),
        scrape_interval_minutes=profile.get("scrape_interval_minutes"),
        created_at=profile["created_at"],
        last_scraped=last_scraped,
        last_new_listings_count=profile.get("last_new_listings_count", 0),
        listings_count=len(listings),
        new_today_count=calculate_new_today_count(listings)
    )

# Update complete profile (name, filters, emails) - Updated for user authentication
@app.put("/api/profiles/{profile_id}")
async def update_profile(
    profile_id: str,
    profile_update: ProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update a user's profile."""
    db = load_db()
    profiles = db.get("profiles", {})
    user_id = current_user["id"]
    
    if profile_id not in profiles:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = profiles[profile_id]
    
    # Check if user owns this profile
    if profile.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    # Update profile fields
    if profile_update.name is not None:
        profile["name"] = profile_update.name
    if profile_update.filters is not None:
        profile["filters"] = profile_update.filters
    if profile_update.emails is not None:
        profile["emails"] = profile_update.emails
    
    # Handle scrape interval updates
    interval_updated = False
    if profile_update.scrape_interval_hours is not None or profile_update.scrape_interval_minutes is not None:
        # For legacy profiles, ensure both fields exist with defaults
        current_hours = profile.get("scrape_interval_hours", 4)
        current_minutes = profile.get("scrape_interval_minutes", 0)
        
        # Update both hours and minutes components
        profile["scrape_interval_hours"] = profile_update.scrape_interval_hours if profile_update.scrape_interval_hours is not None else current_hours
        profile["scrape_interval_minutes"] = profile_update.scrape_interval_minutes if profile_update.scrape_interval_minutes is not None else current_minutes
        interval_updated = True
    
    if interval_updated:
        # Update the periodic job with new interval
        try:
            from .periodic_scraper import periodic_scraper
        except ImportError:
            from periodic_scraper import periodic_scraper
        
        periodic_scraper.add_profile_job(
            profile_id,
            combined_hours=profile["scrape_interval_hours"],
            combined_minutes=profile["scrape_interval_minutes"]
        )
    
    save_db(db)
    
    # Update listing timestamps and calculate new today count
    listings = profile.get("listings", [])
    update_listing_timestamps(listings)
    
    # Convert last_scraped from ISO string to timestamp if needed
    last_scraped = profile.get("last_scraped")
    if last_scraped and isinstance(last_scraped, str):
        try:
            dt = datetime.fromisoformat(last_scraped.replace('Z', '+00:00'))
            # Convert to milliseconds for JavaScript Date() compatibility
            last_scraped = dt.timestamp() * 1000
        except:
            last_scraped = None
    elif not last_scraped:
        # Ensure null/None values stay as None (not 0 or other falsy values)
        last_scraped = None
    
    return ProfileResponse(
        id=profile_id,
        user_id=profile["user_id"],
        name=profile["name"],
        filters=profile["filters"],
        emails=profile["emails"],
        scrape_interval_hours=profile.get("scrape_interval_hours"),
        scrape_interval_minutes=profile.get("scrape_interval_minutes"),
        created_at=profile["created_at"],
        last_scraped=last_scraped,
        last_new_listings_count=profile.get("last_new_listings_count", 0),
        listings_count=len(listings),
        new_today_count=calculate_new_today_count(listings)
    )

@app.get("/api/data")
def get_all_data():
    """Return the entire database.json contents."""
    return load_db()

# --- PERIODIC SCRAPING ENDPOINTS ---

@app.get("/api/scraper/status")
async def get_scraper_status():
    """Get the current status of the periodic scraper with auto-healing"""
    if periodic_scraper:
        # Check if scheduler thread is actually alive
        status = periodic_scraper.get_status()
        
        # Enhanced status check
        if periodic_scraper.is_running:
            if hasattr(periodic_scraper.scheduler, '_thread') and periodic_scraper.scheduler._thread:
                thread_alive = periodic_scraper.scheduler._thread.is_alive()
                status["thread_alive"] = thread_alive
                
                # If thread is dead but marked as running, fix it
                if not thread_alive:
                    logger.warning("Scheduler thread died, restarting...")
                    try:
                        periodic_scraper.stop()
                        periodic_scraper.start()
                        status = periodic_scraper.get_status()
                        status["auto_restarted"] = True
                    except Exception as e:
                        logger.error(f"Auto-restart failed: {e}")
                        status["auto_restart_error"] = str(e)
            else:
                status["thread_alive"] = False
                # Try to restart if no thread
                logger.warning("No scheduler thread found, restarting...")
                try:
                    # Check if periodic_scraper is properly initialized
                    if not hasattr(periodic_scraper, 'stop') or not callable(getattr(periodic_scraper, 'stop')):
                        logger.error("Periodic scraper doesn't have a stop method")
                        status["error"] = "Invalid scraper configuration"
                    else:
                        # Stop and restart
                        periodic_scraper.stop()
                        periodic_scraper.start()
                        status = periodic_scraper.get_status()
                        status["auto_restarted"] = True
                        logger.info("Successfully restarted the periodic scraper")
                except Exception as e:
                    logger.error(f"Auto-restart failed: {e}")
                    status["auto_restart_error"] = str(e)
        
        return status
    else:
        return {"is_running": False, "error": "Periodic scraper not available"}

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

@app.get("/api/scraper/debug")
def debug_scraper():
    """Debug endpoint to check scheduler thread state"""
    import threading
    
    debug_info = {
        "scraper_instance_id": id(periodic_scraper),
        "scraper_is_running": periodic_scraper.is_running if periodic_scraper else None,
        "scheduler_instance_id": id(periodic_scraper.scheduler) if periodic_scraper else None,
        "scheduler_state": periodic_scraper.scheduler.state if periodic_scraper else None,
        "scheduler_running": periodic_scraper.scheduler.running if periodic_scraper else None,
        "scheduler_timezone": str(periodic_scraper.scheduler.timezone) if periodic_scraper else None,
        "active_threads": [],
        "apscheduler_threads": []
    }
    
    # Check all active threads
    for thread in threading.enumerate():
        thread_info = {
            "name": thread.name,
            "alive": thread.is_alive(),
            "daemon": thread.daemon,
            "ident": thread.ident
        }
        debug_info["active_threads"].append(thread_info)
        
        if "APScheduler" in thread.name:
            debug_info["apscheduler_threads"].append(thread_info)
    
    # Check scheduler thread specifically
    if periodic_scraper and hasattr(periodic_scraper.scheduler, '_thread'):
        thread = periodic_scraper.scheduler._thread
        if thread:
            debug_info["scheduler_thread"] = {
                "name": thread.name,
                "alive": thread.is_alive(),
                "daemon": thread.daemon,
                "ident": thread.ident
            }
        else:
            debug_info["scheduler_thread"] = None
    else:
        debug_info["scheduler_thread"] = "No _thread attribute"
    
    # Check jobs
    if periodic_scraper:
        try:
            jobs = periodic_scraper.scheduler.get_jobs()
            debug_info["jobs_count"] = len(jobs)
            debug_info["job_details"] = []
            for job in jobs:
                debug_info["job_details"].append({
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger)
                })
        except Exception as e:
            debug_info["jobs_error"] = str(e)
    
    return debug_info

@app.get("/api/scraper/deep_debug")
async def deep_debug_scheduler():
    """Provide in-depth debug information about the scheduler"""
    import threading
    import gc
    import os
    import sys
    import pytz
    
    if not periodic_scraper:
        return {"error": "Periodic scraper not available"}
    
    try:
        # Process basic information
        # Create very detailed diagnostic information
        debug_info = {
            "process": {
                "pid": os.getpid(),
            },
            "scheduler": {
                "is_running": periodic_scraper.is_running,
                "scheduler_running": periodic_scraper.scheduler.running if hasattr(periodic_scraper.scheduler, 'running') else None,
                "timezone": str(periodic_scraper.scheduler.timezone),
                "jobs_executed_ever": periodic_scraper.jobs_running
            },
            "environment": {
                "on_railway": is_running_on_railway(),
                "python_version": sys.version,
                "current_time_utc": datetime.now(pytz.UTC).isoformat()
            }
        }
        
        # Thread information
        all_threads = []
        for t in threading.enumerate():
            all_threads.append({
                "name": t.name,
                "daemon": t.daemon,
                "alive": t.is_alive(),
                "id": t.ident
            })
        debug_info["threads"] = all_threads
        
        # List all jobs with very detailed information
        jobs_info = []
        try:
            for job in periodic_scraper.scheduler.get_jobs():
                job_info = {
                    "id": job.id,
                    "name": job.name,
                    "function": str(job.func),
                    "args": str(job.args),
                    "kwargs": str(job.kwargs),
                    "trigger": str(job.trigger),
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "pending": job.pending
                }
                
                # Check if the job is late
                if job.next_run_time and job.next_run_time < datetime.now(pytz.UTC):
                    job_info["late_by_seconds"] = (datetime.now(pytz.UTC) - job.next_run_time).total_seconds()
                
                jobs_info.append(job_info)
        except Exception as e:
            jobs_info = [{"error": f"Failed to get jobs: {str(e)}"}]
        
        debug_info["jobs"] = jobs_info
        
        # Add scheduler internals
        try:
            debug_info["scheduler_internals"] = {
                "thread": {
                    "alive": periodic_scraper.scheduler._thread.is_alive() if hasattr(periodic_scraper.scheduler, '_thread') and periodic_scraper.scheduler._thread else None,
                    "daemon": periodic_scraper.scheduler._thread.daemon if hasattr(periodic_scraper.scheduler, '_thread') and periodic_scraper.scheduler._thread else None,
                },
                "executors": str(periodic_scraper.scheduler._executors),
                "jobstores": str(periodic_scraper.scheduler._jobstores),
                "job_defaults": str(periodic_scraper.scheduler._job_defaults),
            }
        except Exception as e:
            debug_info["scheduler_internals_error"] = str(e)
        
        # Try to trigger GC and report
        gc_count_before = gc.get_count()
        collected = gc.collect()
        gc_count_after = gc.get_count()
        
        debug_info["garbage_collection"] = {
            "collected_objects": collected,
            "count_before": gc_count_before,
            "count_after": gc_count_after
        }
        
        return debug_info
    except Exception as e:
        return {"error": f"Error generating debug info: {str(e)}"}

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    """Register a new user."""
    db = load_db()
    
    # Ensure users section exists
    if "users" not in db:
        db["users"] = {}
    
    users = db["users"]
    
    # Check if username already exists
    for user in users.values():
        if user.get("username") == user_data.username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        if user.get("email") == user_data.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    user_id = generate_user_id()
    new_user = create_user_dict(
        user_id=user_id,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    users[user_id] = new_user
    save_db(db)
    
    # Generate tokens
    tokens = generate_tokens(user_id)
    
    # Update last login
    users[user_id]["last_login"] = time.time()
    save_db(db)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse(**new_user)
    )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    """Login user and return tokens."""
    db = load_db()
    users = db.get("users", {})
    
    # Find user by username
    user = None
    user_id = None
    for uid, u in users.items():
        if u.get("username") == user_data.username:
            user = u
            user_id = uid
            break
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not AuthUtils.verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if user is active
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is disabled"
        )
    
    # Generate tokens
    tokens = generate_tokens(user_id)
    
    # Update last login
    user["last_login"] = time.time()
    save_db(db)
    
    return TokenResponse(
        access_token=tokens["access_token"],
        refresh_token=tokens["refresh_token"],
        token_type=tokens["token_type"],
        user=UserResponse(**user)
    )

@app.post("/api/auth/logout")
async def logout(
    request: Request,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Logout user and blacklist token."""
    # Get token from request
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        blacklist_token(token)
    
    return {"message": "Successfully logged out"}

@app.post("/api/auth/refresh", response_model=TokenResponse)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token using refresh token."""
    try:
        payload = AuthUtils.verify_token(token_data.refresh_token, "refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Load user from database
        db = load_db()
        users = db.get("users", {})
        user = users.get(user_id)
        
        if not user or not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Generate new tokens
        tokens = generate_tokens(user_id)
        
        return TokenResponse(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            token_type=tokens["token_type"],
            user=UserResponse(**user)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse(**current_user)

@app.put("/api/auth/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user information."""
    db = load_db()
    
    # Ensure users structure exists
    if "users" not in db:
        db["users"] = {}
    
    user_id = current_user["user_id"]
    
    # Update user fields
    if user_update.username is not None:
        db["users"][user_id]["username"] = user_update.username
    if user_update.email is not None:
        db["users"][user_id]["email"] = user_update.email
    if user_update.password is not None:
        db["users"][user_id]["password"] = AuthUtils.hash_password(user_update.password)
    
    if TIMEZONE_UTILS_AVAILABLE:
        db["users"][user_id]["updated_at"] = now_cest_iso()
    else:
        db["users"][user_id]["updated_at"] = datetime.now().isoformat()
    
    save_db(db)
    return UserResponse(**db["users"][user_id])

@app.put("/api/auth/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile settings."""
    db = load_db()
    
    # Ensure users structure exists
    if "users" not in db:
        db["users"] = {}
    
    user_id = current_user["id"]
    
    # Update user fields
    if profile_update.email is not None:
        db["users"][user_id]["email"] = profile_update.email
    if profile_update.email_notifications is not None:
        db["users"][user_id]["email_notifications"] = profile_update.email_notifications
    if profile_update.daily_summaries is not None:
        db["users"][user_id]["daily_summaries"] = profile_update.daily_summaries
    if profile_update.scrape_interval is not None:
        db["users"][user_id]["scrape_interval"] = profile_update.scrape_interval
    
    if TIMEZONE_UTILS_AVAILABLE:
        db["users"][user_id]["updated_at"] = now_cest_iso()
    else:
        db["users"][user_id]["updated_at"] = datetime.now().isoformat()
    
    save_db(db)
    return UserResponse(**db["users"][user_id])

@app.get("/api/admin/stats")
async def get_admin_stats():
    """Get admin statistics including latest scrape time across all profiles."""
    db = load_db()
    profiles = db.get("profiles", {})
    
    # Find the latest scrape across all profiles
    latest_scrape = None
    for profile in profiles.values():
        if profile.get("last_scraped"):
            try:
                date = datetime.fromisoformat(profile["last_scraped"])
                if not latest_scrape or date > latest_scrape:
                    latest_scrape = date
            except:
                pass
    
    # Count total listings
    total_listings = 0
    new_listings = 0
    for profile in profiles.values():
        profile_listings = profile.get("listings", [])
        total_listings += len(profile_listings)
        new_listings += calculate_new_today_count(profile_listings)
    
    return {
        "total_listings": total_listings,
        "new_listings": new_listings,
        "latest_scrape": latest_scrape.isoformat() if latest_scrape else None
    }

def calculate_new_today_count(listings: List[dict]) -> int:
    """Calculate how many listings were added in the last 24 hours."""
    if not listings:
        return 0
    
    current_time = time.time()
    count = 0
    
    for listing in listings:
        added_timestamp = listing.get("added_timestamp")
        if added_timestamp:
            time_diff = current_time - added_timestamp
            if time_diff < 86400:  # 24 hours = 86400 seconds
                count += 1
        elif listing.get("is_new"):
            # Fallback for listings that might not have timestamps but are marked as new
            count += 1
    
    return count

def update_listing_timestamps(listings: List[dict]) -> None:
    """Update is_new flags based on 24-hour rule and ensure all listings have timestamps."""
    if TIMEZONE_UTILS_AVAILABLE:
        try:
            from .timezone_utils import now_cest
        except ImportError:
            from timezone_utils import now_cest
        current_time = now_cest()
    else:
        current_time = datetime.now()
    
    for listing in listings:
        if not listing.get("added_timestamp"):
            # Legacy listing without timestamp, add one based on scraped_at or current time
            scraped_at = listing.get("scraped_at")
            if scraped_at:
                try:
                    dt = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                    listing["added_timestamp"] = dt.timestamp()
                except:
                    listing["added_timestamp"] = current_time.timestamp()
            else:
                listing["added_timestamp"] = current_time.timestamp()
                listing["scraped_at"] = current_time.isoformat()
        
        # Update is_new flag based on 24-hour rule
        time_diff = current_time.timestamp() - listing.get("added_timestamp", 0)
        listing["is_new"] = time_diff < 86400  # 24 hours = 86400 seconds

# (Final duplicate endpoints removed - using enhanced version at top)

# --- FORCE SCRAPE ENDPOINT ---

@app.post("/api/scraper/force_run/{profile_id}")
async def force_scrape_profile(profile_id: str):
    """Force a profile to scrape immediately - useful for testing"""
    try:
        db = load_db()
        profiles = db.get("profiles", {})
        
        if profile_id not in profiles:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Get the profile
        profile = profiles[profile_id]
        profile_name = profile.get("name", "Unknown")
        
        # Run the scrape job in the scheduler
        job_id = f"force_scrape_{profile_id}"
        
        # Direct access to the scraper's methods for immediate execution
        if periodic_scraper:
            try:
                # Schedule for immediate execution (1 second from now)
                from datetime import datetime, timedelta
                import pytz
                next_run = datetime.now(pytz.UTC) + timedelta(seconds=1)
                
                # Add a one-time job
                periodic_scraper.scheduler.add_job(
                    func=periodic_scraper._scrape_profile,
                    id=job_id,
                    args=[profile_id],
                    name=f"Force Scrape {profile_name}",
                    next_run_time=next_run,
                    replace_existing=True
                )
                
                return {
                    "status": "success", 
                    "message": f"Scheduled immediate scrape for profile: {profile_name}",
                    "scheduled_at": next_run.isoformat()
                }
            except Exception as e:
                logger.error(f"Failed to schedule immediate scrape: {e}")
                return {"status": "error", "message": f"Failed to schedule: {str(e)}"}
        else:
            return {"status": "error", "message": "Periodic scraper not available"}
    except Exception as e:
        logger.error(f"Error in force scrape: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scraper/chrome_debug")
async def chrome_diagnostics():
    """Advanced diagnostic endpoint to test Chrome in the environment"""
    import os
    import sys
    import platform
    import subprocess
    import tempfile
    from pathlib import Path
    import shutil
    
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "on_railway": is_running_on_railway(),
            "python_version": sys.version,
            "platform": platform.platform(),
            "container": False,
            "memory_usage_mb": None,
            "disk_space_mb": None
        },
        "chrome": {
            "detected": False,
            "version": None,
            "binary_path": None,
            "selenium_test": {
                "success": False,
                "error": None,
                "html_length": 0,
                "duration_ms": 0
            }
        }
    }
    
    # Check if running in container
    try:
        diagnostics["environment"]["container"] = os.path.exists('/.dockerenv') or os.path.exists('/.containerenv')
        
        # Try to get container info from /proc/1/cgroup
        try:
            with open('/proc/1/cgroup', 'r') as f:
                cgroup_content = f.read()
                diagnostics["environment"]["cgroup_info"] = cgroup_content.split('\n')[0:3]
                if 'docker' in cgroup_content or 'kubepods' in cgroup_content:
                    diagnostics["environment"]["container"] = True
        except Exception as e:
            diagnostics["environment"]["cgroup_error"] = str(e)
    except Exception as e:
        diagnostics["environment"]["container_check_error"] = str(e)
    
    # Try to get system resources
    try:
        import psutil
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        diagnostics["environment"]["memory_usage_mb"] = {
            "total": memory.total / (1024 * 1024),
            "used": memory.used / (1024 * 1024),
            "percent": memory.percent
        }
        
        diagnostics["environment"]["disk_space_mb"] = {
            "total": disk.total / (1024 * 1024),
            "used": disk.used / (1024 * 1024),
            "free": disk.free / (1024 * 1024),
            "percent": disk.percent
        }
    except Exception as e:
        diagnostics["environment"]["resource_check_error"] = str(e)
    
    # Check for Chrome binary
    chrome_paths = [
        '/usr/bin/google-chrome',
        '/usr/bin/google-chrome-stable',
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser'
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            diagnostics["chrome"]["binary_path"] = path
            diagnostics["chrome"]["detected"] = True
            break
    
    # Try to get Chrome version
    if diagnostics["chrome"]["detected"]:
        try:
            version_cmd = f"{diagnostics['chrome']['binary_path']} --version"
            chrome_version = subprocess.check_output(version_cmd, shell=True, stderr=subprocess.STDOUT).decode('utf-8').strip()
            diagnostics["chrome"]["version"] = chrome_version
        except Exception as e:
            diagnostics["chrome"]["version_error"] = str(e)
    
    # Try a quick Chrome test
    try:
        from .scrape_funda import scrape_funda_html
        
        start_time = time.time()
        html = scrape_funda_html('https://www.funda.nl', max_retries=1, timeout=20)
        end_time = time.time()
        
        diagnostics["chrome"]["selenium_test"]["duration_ms"] = int((end_time - start_time) * 1000)
        
        if html:
            diagnostics["chrome"]["selenium_test"]["success"] = True
            diagnostics["chrome"]["selenium_test"]["html_length"] = len(html)
        else:
            diagnostics["chrome"]["selenium_test"]["error"] = "Empty HTML returned"
    except Exception as e:
        diagnostics["chrome"]["selenium_test"]["error"] = str(e)
    
    return diagnostics

@app.post("/api/profiles/{profile_id}/scrape")
async def scrape_profile_endpoint(
    profile_id: str, 
    request_data: Dict[str, Any] = Body(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Manually trigger a scrape for a specific profile with the provided filters."""
    try:
        # Load database
        db = load_db()
        profiles = db.get("profiles", {})
        
        # Check if profile exists
        if profile_id not in profiles:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile = profiles[profile_id]
        
        # Get user identification - be flexible with field names for maximum compatibility
        user_id = None
        for field in ["id", "user_id", "username"]:
            if field in current_user and current_user[field]:
                user_id = current_user[field]
                break
                
        # For debugging
        logger.info(f"Manual scrape request - profile_id: {profile_id}, user fields: {list(current_user.keys())}")
        
        # Skip authorization check if in development mode or for demo purposes
        # This makes the app more user-friendly for testing
        skip_auth = os.environ.get("SKIP_AUTH_CHECK", "true") == "true"
        
        # Only check authorization if not skipped
        if not skip_auth:
            profile_user_id = profile.get("user_id")
            if not user_id or not profile_user_id or profile_user_id != user_id:
                logger.warning(f"Authorization failed: User ID {user_id} doesn't match profile owner {profile_user_id}")
                logger.warning(f"User data: {current_user}")
                raise HTTPException(status_code=403, detail="Not authorized to access this profile")
        
        # Update profile filters if included in request
        if "filters" in request_data:
            profile["filters"] = request_data["filters"]
            save_db(db)
        
        # Add a direct scrape implementation instead of calling the other endpoint
        try:
            # Schedule for immediate execution 
            job_id = f"manual_scrape_{profile_id}"
            profile_name = profile.get("name", "Unknown")
            logger.info(f"Processing manual scrape request for {profile_name} (ID: {profile_id})")
            
            if periodic_scraper:
                # Use direct method call for immediate execution
                logger.info(f"Performing manual scrape for profile {profile_id} ({profile_name})")
                
                try:
                    # Log that we are going to make a direct call
                    logger.info(f"Attempting direct call to scrape_profile for {profile_id}")
                    
                    # Debug info
                    scraper_type = type(periodic_scraper).__name__
                    has_method = hasattr(periodic_scraper, 'scrape_profile')
                    is_callable = has_method and callable(getattr(periodic_scraper, 'scrape_profile'))
                    logger.info(f"Scraper type: {scraper_type}, has method: {has_method}, is callable: {is_callable}")
                    
                    # Try with a try-except block to catch specific errors
                    try:
                        # Directly call scrape_profile method for immediate execution
                        # This bypasses scheduling and runs immediately
                        periodic_scraper.scrape_profile(profile_id)
                        logger.info(f"Successfully called scrape_profile for {profile_id}")
                    except AttributeError as e:
                        logger.error(f"AttributeError when calling scrape_profile: {e}")
                        # Try the trigger_profile_scrape method as fallback
                        if hasattr(periodic_scraper, 'trigger_profile_scrape'):
                            logger.info(f"Falling back to trigger_profile_scrape for {profile_id}")
                            periodic_scraper.trigger_profile_scrape(profile_id)
                        else:
                            raise
                    
                    # Update last_scraped in the database after successful scrape
                    if TIMEZONE_UTILS_AVAILABLE:
                        profile["last_scraped"] = now_cest_iso()
                    else:
                        profile["last_scraped"] = datetime.now().isoformat()
                    save_db(db)
                    
                    logger.info(f"Manual scrape completed successfully for profile {profile_id}")
                    return {"status": "success", "message": "Scrape completed successfully"}
                    
                except Exception as direct_error:
                    logger.error(f"Direct scrape failed, falling back to scheduled job: {direct_error}")
                    
                    # Fall back to scheduling method if direct call fails
                    from datetime import timedelta
                    import pytz
                    next_run = datetime.now(pytz.UTC) + timedelta(seconds=1)
                    
                    # Add a one-time job as fallback
                    periodic_scraper.scheduler.add_job(
                        func=periodic_scraper.scrape_profile,
                        id=job_id,
                        args=[profile_id],
                        name=f"Manual Scrape {profile_name}",
                        next_run_time=next_run,
                        replace_existing=True
                    )
                    logger.info(f"Successfully added job {job_id} to scheduler")
                except Exception as job_error:
                    logger.error(f"Failed to add job to scheduler: {job_error}")
                    raise
                
                # Update last_scraped in the database
                if TIMEZONE_UTILS_AVAILABLE:
                    profile["last_scraped"] = now_cest_iso()
                else:
                    profile["last_scraped"] = datetime.now().isoformat()
                save_db(db)
                
                return {"status": "success", "message": "Scrape initiated successfully"}
            else:
                logger.error("Periodic scraper not available for manual scrape")
                raise HTTPException(status_code=500, detail="Scraper service is not available")
        except Exception as e:
            logger.error(f"Failed to schedule immediate scrape: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to schedule scrape: {str(e)}")
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error initiating scrape for profile {profile_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate scrape: {str(e)}")

# --- Debug endpoints (disable in production) ---
@app.get("/api/debug/test_scraper")
async def test_scraper():
    """Debug endpoint to test the scraper functionality."""
    try:
        if not periodic_scraper:
            return {"status": "error", "message": "Periodic scraper not available"}
        
        # Log available methods and attributes
        methods = [method for method in dir(periodic_scraper) if not method.startswith('_')]
        
        # Try to access scrape_profile method
        if hasattr(periodic_scraper, 'scrape_profile'):
            method_info = {
                "exists": True,
                "callable": callable(getattr(periodic_scraper, 'scrape_profile')),
                "signature": str(inspect.signature(getattr(periodic_scraper, 'scrape_profile'))) if inspect else "inspect not available"
            }
        else:
            method_info = {"exists": False}
        
        return {
            "status": "success",
            "scraper_type": type(periodic_scraper).__name__,
            "available_methods": methods,
            "scrape_profile_method": method_info
        }
    except Exception as e:
        logger.error(f"Error in test_scraper endpoint: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/debug/test_manual_scrape/{profile_id}")
async def test_manual_scrape(profile_id: str):
    """Debug endpoint to test manual scrape functionality without authentication."""
    try:
        # Load database
        db = load_db()
        profiles = db.get("profiles", {})
        
        # Check if profile exists - create a test one if not
        if profile_id not in profiles:
            logger.info(f"Creating test profile {profile_id} for debug purposes")
            profiles[profile_id] = {
                "id": profile_id,
                "name": "Test Profile",
                "filters": {"type": "koop"},
                "user_id": "test_user",
                "created_at": datetime.now().isoformat()
            }
            save_db(db)
        
        # Get the profile
        profile = profiles[profile_id]
        profile_name = profile.get("name", "Unknown")
        
        if periodic_scraper:
            logger.info(f"Attempting manual scrape for test profile {profile_id}")
            
            try:
                # Direct call
                periodic_scraper.scrape_profile(profile_id)
                
                # Update last_scraped
                profiles[profile_id]["last_scraped"] = datetime.now().isoformat()
                save_db(db)
                
                return {"status": "success", "message": f"Successfully scraped profile {profile_name}"}
            except Exception as e:
                logger.error(f"Error in debug manual scrape: {e}")
                return {
                    "status": "error", 
                    "message": str(e),
                    "scraper_type": type(periodic_scraper).__name__,
                    "has_method": hasattr(periodic_scraper, "scrape_profile")
                }
        else:
            return {"status": "error", "message": "Periodic scraper not available"}
    except Exception as e:
        logger.error(f"Debug endpoint error: {e}")
        return {"status": "error", "message": str(e)}
