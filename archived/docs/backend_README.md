# House Scraper Backend

A FastAPI-based backend for scraping and managing Dutch property listings from Funda.nl.

## Project Structure

```
backend/
├── api.py                     # Main FastAPI application
├── periodic_scraper.py        # Background scraping scheduler
├── scrape_api.py             # Scraping API endpoints
├── scrape_funda.py           # Core scraping logic
├── extract_funda_listings.py # HTML parsing and listing extraction
├── funda_url_builder.py      # URL building utilities
├── listing_mapping.py        # Data mapping utilities
├── email_utils.py            # Email notification system
├── listings.html             # Frontend HTML interface
├── requirements.txt          # Python dependencies
├── package.json              # Node.js dependencies
├── .env.example              # Environment variables template
├── funda_simple_listings.json # Current listings data
├── templates/                # Email templates
├── utils/                    # Maintenance utilities
│   ├── deduplicate_database.py
│   ├── migrate_database.py
│   └── debug_listings.js
├── debug/                    # Debug files and outputs
│   ├── cookies.pkl
│   ├── funda_uc_debug.html
│   └── *.jsonl
├── docs/                     # Documentation
│   ├── TODO_ANTIBOT.md
│   └── TODO_continuous_search.md
└── deprecated/               # Legacy and unused files
    ├── main.py
    ├── scraper.py
    ├── session_scraper.py
    ├── test_*.py
    └── *.sh
```

## Core Features

### 🔄 Periodic Scraping
- Automated background scraping with configurable intervals
- Profile-based scraping with different schedules
- APScheduler integration for job management

### 📧 Email Notifications
- Automatic email alerts for new listings
- HTML email templates with listing details
- SMTP configuration via environment variables

### 🎯 Profile Management
- Save search criteria as profiles
- CRUD operations for profiles
- Per-profile email lists and intervals

### 🔍 Real-time Search
- Live scraping via API endpoints
- Comprehensive filter support
- Deduplication and data persistence

## Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env` and update SMTP settings

3. **Start the Application**:
   ```bash
   uvicorn api:app --reload --port 8000
   ```

4. **Access Interface**:
   - Frontend: http://localhost:8000/listings.html
   - API Docs: http://localhost:8000/docs

## API Endpoints

### Core Endpoints
- `GET /api/listings` - Get all listings
- `GET /api/profiles` - Get all profiles
- `POST /api/profiles` - Create new profile
- `PUT /api/profiles/{id}` - Update profile
- `DELETE /api/profiles/{id}` - Delete profile

### Scraping Control
- `GET /api/scraper/status` - Get scraper status
- `POST /api/scraper/start` - Start periodic scraper
- `POST /api/scraper/stop` - Stop periodic scraper
- `POST /api/profiles/{id}/scrape` - Trigger manual scrape

### Data Management
- `POST /api/scrape/{profile_id}` - Scrape for specific profile
- `PUT /api/profiles/{id}/interval` - Update scraping interval
- `PUT /api/profiles/{id}/email` - Update email settings

## Maintenance

### Database Operations
- **Deduplicate**: `python utils/deduplicate_database.py`
- **Migrate**: `python utils/migrate_database.py`

### Debugging
- Debug files are stored in `debug/` folder
- HTML outputs and cookies for inspection
- JSONL files for data analysis

## File Organization

### Active Files
All core application files are in the root backend directory for easy access and imports.

### Deprecated Files
Legacy implementations and experimental code moved to `deprecated/` folder:
- Old main.py implementations
- Test scripts and experimental scrapers
- Unused shell scripts

### Utilities
Maintenance and utility scripts organized in `utils/` folder:
- Database management tools
- Debug scripts
- Migration utilities

### Documentation
Project documentation in `docs/` folder:
- TODO lists and planning documents
- Implementation guides
- Anti-bot strategies

## Development Notes

- The application uses absolute imports for core modules
- Periodic scraper auto-starts with the FastAPI application
- Email templates are stored in `templates/` folder
- Debug outputs are automatically organized in `debug/` folder

## Legal & Compliance

This application is designed for personal use and educational purposes. Please respect Funda's robots.txt and terms of service when scraping their website.
