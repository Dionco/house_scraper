#!/usr/bin/env python3
"""
Deep Production Cleanup Script
Performs aggressive cleanup for production-ready deployment
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent

# Files to keep for PRODUCTION (minimal essential set)
PRODUCTION_ESSENTIAL = {
    'root': {
        # Core application files
        'database.json',
        'search_profiles.json',
        
        # Single deployment configs (keep only the best)
        'railway.toml',  # Most flexible deployment
        'Dockerfile',    # Standard Docker
        
        # Environment
        '.env.example',
        
        # Essential docs only
        'README.md',
        
        # Git files
        '.gitignore'
    },
    'backend': {
        # Core application
        'api.py',
        'periodic_scraper.py',
        'scrape_api.py',
        'scrape_funda.py',
        'extract_funda_listings.py',
        'funda_url_builder.py',
        'listing_mapping.py',
        'email_utils.py',
        'auth_models.py',
        'auth_utils.py',
        'timezone_utils.py',
        
        # Data files
        'funda_simple_listings.json',
        
        # Web interface
        'listings.html',
        'admin-scraper.html',
        
        # Config
        'requirements.txt',
        '.env.example',
        '__init__.py',
        'favicon.ico'
    }
}

# Files to archive (non-essential but keep for reference)
ARCHIVE_CATEGORIES = {
    'docs_archive': {
        'patterns': ['*.md'],
        'exceptions': {'README.md'},  # Keep main README
        'destination': 'archived/docs'
    },
    'deployment_archive': {
        'files': [
            'Dockerfile.minimal',
            'Dockerfile.railway', 
            'netlify.toml',
            'render.yaml'
        ],
        'destination': 'archived/deployment'
    },
    'utility_archive': {
        'patterns': ['*cleanup*.py', 'migrate_*.py'],
        'destination': 'archived/utilities'
    },
    'config_archive': {
        'patterns': ['*.toml', '*.yaml'],
        'exceptions': {'railway.toml'},  # Keep primary deployment config
        'destination': 'archived/config'
    }
}

def should_keep_file(file_path: Path, location: str) -> bool:
    """Check if file should be kept in production."""
    if location == 'root':
        return file_path.name in PRODUCTION_ESSENTIAL['root']
    elif location == 'backend':
        return file_path.name in PRODUCTION_ESSENTIAL['backend']
    return False

def archive_file(file_path: Path, destination: str) -> Path:
    """Archive a file to specified destination."""
    archive_path = PROJECT_ROOT / destination
    archive_path.mkdir(parents=True, exist_ok=True)
    
    dest_file = archive_path / file_path.name
    
    # Handle conflicts
    if dest_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = dest_file.stem
        suffix = dest_file.suffix
        dest_file = archive_path / f"{stem}_{timestamp}{suffix}"
    
    shutil.move(str(file_path), str(dest_file))
    return dest_file

def consolidate_dockerfiles():
    """Create single optimized Dockerfile and archive others."""
    dockerfile_content = '''# Production Dockerfile for House Scraper
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY database.json search_profiles.json ./

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "backend.api:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    # Write optimized Dockerfile
    with open(PROJECT_ROOT / 'Dockerfile', 'w') as f:
        f.write(dockerfile_content)
    
    # Archive other Docker files
    archived_files = []
    for dockerfile in ['Dockerfile.minimal', 'Dockerfile.railway']:
        dockerfile_path = PROJECT_ROOT / dockerfile
        if dockerfile_path.exists():
            archived_file = archive_file(dockerfile_path, 'archived/deployment')
            archived_files.append(str(archived_file))
    
    return archived_files

def cleanup_documentation():
    """Keep only essential documentation."""
    archived_files = []
    
    # Archive docs directory
    docs_dir = PROJECT_ROOT / 'docs'
    if docs_dir.exists():
        for doc_file in docs_dir.rglob('*'):
            if doc_file.is_file():
                archived_file = archive_file(doc_file, 'archived/docs')
                archived_files.append(str(archived_file))
        
        # Remove empty docs directory
        if docs_dir.exists() and not any(docs_dir.iterdir()):
            docs_dir.rmdir()
    
    # Archive redundant markdown files in root
    md_files = [
        'CLEANUP_SUMMARY.md',
        'DEPLOYMENT.md', 
        'NEW_TODAY_IMPLEMENTATION.md',
        'PERFORMANCE_OPTIMIZATIONS.md',
        'PERIODIC_SCRAPING.md',
        'FINAL_CLEANUP_SUMMARY.md',
        'PRODUCTION_STRUCTURE.json'
    ]
    
    for md_file in md_files:
        md_path = PROJECT_ROOT / md_file
        if md_path.exists():
            archived_file = archive_file(md_path, 'archived/docs')
            archived_files.append(str(archived_file))
    
    return archived_files

def cleanup_config_files():
    """Keep only railway.toml for deployment."""
    archived_files = []
    
    config_files = ['netlify.toml', 'render.yaml']
    for config_file in config_files:
        config_path = PROJECT_ROOT / config_file
        if config_path.exists():
            archived_file = archive_file(config_path, 'archived/deployment')
            archived_files.append(str(archived_file))
    
    return archived_files

def cleanup_utility_scripts():
    """Archive utility scripts."""
    archived_files = []
    
    utility_scripts = [
        'cleanup_workspace.py',
        'final_cleanup.py',
        'migrate_timestamps.py'
    ]
    
    for script in utility_scripts:
        script_path = PROJECT_ROOT / script
        if script_path.exists():
            archived_file = archive_file(script_path, 'archived/utilities')
            archived_files.append(str(archived_file))
    
    return archived_files

def cleanup_backend_redundancies():
    """Clean up backend redundancies."""
    archived_files = []
    backend_dir = PROJECT_ROOT / 'backend'
    
    # Files to remove/archive from backend
    redundant_files = [
        'api.py.backup',
        'extract_funda_listings_fast.py',  # Keep only main extract file
        'scrape_funda_async.py',  # Keep only main scrape file
        'listings-simple.html',  # Keep only main listings.html
        'migrate_database.py',  # Archive utility
        'migrate_listings_format.py',  # Archive utility
        'package.json',  # Remove if not using Node.js
        'package-lock.json',  # Remove if not using Node.js
        'auth.js'  # Remove if not needed
    ]
    
    for file_name in redundant_files:
        file_path = backend_dir / file_name
        if file_path.exists():
            if 'migrate' in file_name or file_name.endswith('.backup'):
                archived_file = archive_file(file_path, 'archived/utilities')
            elif file_name.endswith(('.json', '.js')):
                archived_file = archive_file(file_path, 'archived/frontend_legacy')
            else:
                archived_file = archive_file(file_path, 'archived/backend_redundant')
            archived_files.append(str(archived_file))
    
    return archived_files

def optimize_frontend():
    """Optimize frontend structure."""
    frontend_dir = PROJECT_ROOT / 'frontend'
    if frontend_dir.exists():
        # Check if frontend is actually being used
        has_react = (frontend_dir / 'package.json').exists()
        has_components = any(frontend_dir.rglob('*.jsx')) or any(frontend_dir.rglob('*.tsx'))
        
        if not has_react or not has_components:
            # Archive entire frontend if not actively used
            archived_frontend = PROJECT_ROOT / 'archived' / 'frontend_unused'
            archived_frontend.mkdir(parents=True, exist_ok=True)
            shutil.move(str(frontend_dir), str(archived_frontend / 'frontend'))
            return [str(archived_frontend / 'frontend')]
    
    return []

def create_optimized_structure_doc():
    """Create documentation for optimized structure."""
    structure = {
        "production_structure": {
            "description": "Minimal production-ready structure",
            "root_files": {
                "database.json": "Main application database",
                "search_profiles.json": "User search profiles",
                "railway.toml": "Deployment configuration",
                "Dockerfile": "Optimized container configuration",
                ".env.example": "Environment variables template",
                "README.md": "Project documentation"
            },
            "backend_files": {
                "api.py": "Main FastAPI application",
                "periodic_scraper.py": "Background scraping scheduler",
                "scrape_api.py": "Scraping API endpoints", 
                "scrape_funda.py": "Core scraping logic",
                "extract_funda_listings.py": "HTML parsing and extraction",
                "funda_url_builder.py": "URL building utilities",
                "listing_mapping.py": "Data mapping and transformation",
                "email_utils.py": "Email notification system",
                "auth_models.py": "Authentication data models",
                "auth_utils.py": "Authentication utilities",
                "timezone_utils.py": "Timezone handling",
                "funda_simple_listings.json": "Scraped listings cache",
                "listings.html": "Web interface",
                "admin-scraper.html": "Admin interface",
                "requirements.txt": "Python dependencies",
                ".env.example": "Environment template",
                "__init__.py": "Python package marker",
                "favicon.ico": "Web icon"
            },
            "directories": {
                "backend/": "Core application (FastAPI + scraping)",
                "archived/": "All non-production files organized by category",
                ".git/": "Version control",
                ".venv/": "Python virtual environment"
            }
        },
        "archived_categories": {
            "archived/docs/": "Documentation files",
            "archived/deployment/": "Alternative deployment configs",
            "archived/utilities/": "Maintenance and migration scripts",
            "archived/tests/": "Test files",
            "archived/debug/": "Debug files and outputs",
            "archived/monitoring/": "Monitoring scripts",
            "archived/backend_redundant/": "Redundant backend files",
            "archived/frontend_legacy/": "Legacy frontend files"
        },
        "cleanup_date": datetime.now().isoformat(),
        "purpose": "Ultra-minimal production structure",
        "total_production_files": len(PRODUCTION_ESSENTIAL['root']) + len(PRODUCTION_ESSENTIAL['backend'])
    }
    
    with open(PROJECT_ROOT / 'STRUCTURE.json', 'w') as f:
        json.dump(structure, f, indent=2)

def create_minimal_readme():
    """Create streamlined README."""
    readme_content = '''# House Scraper 🏠

Production-ready Dutch property listing scraper with automated notifications.

## 🚀 Quick Start

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## 📱 Access

- **Web Interface**: http://localhost:8000/listings
- **Admin Panel**: http://localhost:8000/admin  
- **API Docs**: http://localhost:8000/docs

## 🚢 Deployment

### Railway (Recommended)
```bash
railway login
railway init
railway up
```

### Docker
```bash
docker build -t house-scraper .
docker run -p 8000:8000 house-scraper
```

## 🔧 Configuration

Edit `.env` file:
```env
# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API settings
API_HOST=0.0.0.0
API_PORT=8000
```

## 📖 Features

- **Automated Scraping**: Periodic funda.nl property scraping
- **Smart Notifications**: Email alerts for new matching listings  
- **Profile Management**: Multiple search profiles with custom criteria
- **Modern Interface**: Clean web UI with real-time updates
- **Production Ready**: Docker, Railway deployment, health checks

## 📊 API Endpoints

- `GET /listings` - Web interface
- `GET /api/listings` - All listings JSON
- `GET /api/scrape` - Trigger manual scrape
- `POST /api/profiles` - Manage search profiles
- `GET /api/health` - Health check

## 🏗️ Architecture

```
backend/
├── api.py              # FastAPI application
├── scrape_funda.py     # Core scraping logic
├── periodic_scraper.py # Background scheduler
├── listings.html       # Web interface
└── requirements.txt    # Dependencies
```

## 📝 License

MIT License - see archived documentation for details.

---

**Note**: All development files (tests, debug tools, alternative configs) are archived in `archived/` directory.
'''
    
    with open(PROJECT_ROOT / 'README.md', 'w') as f:
        f.write(readme_content)

def main():
    """Execute deep cleanup."""
    print("🔥 Starting DEEP production cleanup...")
    
    archived_counts = {}
    
    # 1. Consolidate Docker files
    print("\n1. Consolidating Docker files...")
    archived_counts['docker'] = consolidate_dockerfiles()
    
    # 2. Clean up documentation
    print("2. Cleaning up documentation...")
    archived_counts['docs'] = cleanup_documentation()
    
    # 3. Clean up config files
    print("3. Cleaning up config files...")
    archived_counts['config'] = cleanup_config_files()
    
    # 4. Archive utility scripts
    print("4. Archiving utility scripts...")
    archived_counts['utilities'] = cleanup_utility_scripts()
    
    # 5. Clean backend redundancies
    print("5. Cleaning backend redundancies...")
    archived_counts['backend'] = cleanup_backend_redundancies()
    
    # 6. Optimize frontend
    print("6. Optimizing frontend...")
    archived_counts['frontend'] = optimize_frontend()
    
    # 7. Create optimized documentation
    print("7. Creating optimized structure documentation...")
    create_optimized_structure_doc()
    create_minimal_readme()
    
    # Summary
    total_archived = sum(len(files) for files in archived_counts.values())
    
    print(f"\n🎯 DEEP CLEANUP COMPLETE!")
    print(f"📁 Total files archived: {total_archived}")
    
    for category, files in archived_counts.items():
        if files:
            print(f"  - {category}: {len(files)} files")
    
    print(f"\n✨ Production structure optimized!")
    print(f"📝 New structure documented in STRUCTURE.json")
    print(f"📖 Streamlined README.md created")
    
    # Show final structure
    production_files = len(PRODUCTION_ESSENTIAL['root']) + len(PRODUCTION_ESSENTIAL['backend'])
    print(f"🎉 Production footprint: {production_files} essential files only!")

if __name__ == "__main__":
    main()
