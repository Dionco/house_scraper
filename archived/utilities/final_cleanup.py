#!/usr/bin/env python3
"""
Final comprehensive cleanup script for the House Scraper project.
This script organizes the workspace for production-readiness.
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

# Define the project root
PROJECT_ROOT = Path(__file__).parent

# Define cleanup categories
CLEANUP_CATEGORIES = {
    'test_files': {
        'patterns': ['test_*.py', '*_test.py', 'test*.html'],
        'destination': 'archived/tests'
    },
    'debug_files': {
        'patterns': ['debug_*.py', 'debug*.html', 'debug*.json', 'debug*.jsonl'],
        'destination': 'archived/debug'
    },
    'diagnostic_files': {
        'patterns': ['*diagnostic*.py', '*investigation*.py', '*troubleshooting*.py'],
        'destination': 'archived/diagnostics'
    },
    'monitor_files': {
        'patterns': ['monitor_*.py', 'check_*.py', 'verify_*.py'],
        'destination': 'archived/monitoring'
    },
    'backup_files': {
        'patterns': ['*.backup', '*.backup_*', '*_backup.*'],
        'destination': 'archived/backups'
    },
    'temp_files': {
        'patterns': ['comprehensive_test_results.json', 'performance_test_results_*.json'],
        'destination': 'archived/temp'
    },
    'analysis_files': {
        'patterns': ['*_analysis.py', '*analysis*.py', 'trigger_*.py', 'update_*.py'],
        'destination': 'archived/analysis'
    }
}

# Files to keep in root (production essentials)
PRODUCTION_FILES = {
    'README.md',
    'requirements.txt',
    'Dockerfile',
    'Dockerfile.minimal',
    'Dockerfile.railway',
    'railway.toml',
    'netlify.toml',
    'render.yaml',
    'database.json',
    'search_profiles.json',
    '.env',
    '.env.example',
    'migrate_timestamps.py',
    'DEPLOYMENT.md',
    'PERIODIC_SCRAPING.md',
    'NEW_TODAY_IMPLEMENTATION.md',
    'PERFORMANCE_OPTIMIZATIONS.md',
    'CLEANUP_SUMMARY.md',
    'cleanup_workspace.py',
    'final_cleanup.py'
}

# Backend files to keep (production essentials)
PRODUCTION_BACKEND_FILES = {
    'api.py',
    'periodic_scraper.py',
    'scrape_api.py',
    'scrape_funda.py',
    'scrape_funda_async.py',
    'extract_funda_listings.py',
    'extract_funda_listings_fast.py',
    'funda_url_builder.py',
    'listing_mapping.py',
    'email_utils.py',
    'auth_models.py',
    'auth_utils.py',
    'timezone_utils.py',
    'migrate_database.py',
    'migrate_listings_format.py',
    'funda_simple_listings.json',
    'listings.html',
    'listings-simple.html',
    'admin-scraper.html',
    'requirements.txt',
    'package.json',
    'package-lock.json',
    'README.md',
    '__init__.py',
    '.env',
    '.env.example',
    'favicon.ico',
    'auth.js'
}

def should_keep_file(file_path: Path, production_files: set) -> bool:
    """Check if a file should be kept in production."""
    return file_path.name in production_files

def move_file_to_archive(file_path: Path, destination: str):
    """Move a file to the archive directory."""
    archive_path = PROJECT_ROOT / destination
    archive_path.mkdir(parents=True, exist_ok=True)
    
    dest_file = archive_path / file_path.name
    
    # Handle name conflicts by adding timestamp
    if dest_file.exists():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stem = dest_file.stem
        suffix = dest_file.suffix
        dest_file = archive_path / f"{stem}_{timestamp}{suffix}"
    
    shutil.move(str(file_path), str(dest_file))
    return dest_file

def cleanup_pycache():
    """Remove all __pycache__ directories."""
    for pycache_dir in PROJECT_ROOT.rglob('__pycache__'):
        if pycache_dir.is_dir():
            shutil.rmtree(pycache_dir)
            print(f"Removed __pycache__: {pycache_dir}")

def cleanup_node_modules():
    """Remove node_modules if not needed for production."""
    node_modules_path = PROJECT_ROOT / 'backend' / 'node_modules'
    if node_modules_path.exists():
        print(f"Found node_modules at: {node_modules_path}")
        response = input("Remove node_modules? (y/n): ")
        if response.lower() == 'y':
            shutil.rmtree(node_modules_path)
            print("Removed node_modules")

def cleanup_by_patterns():
    """Clean up files based on patterns."""
    moved_files = {}
    
    for category, config in CLEANUP_CATEGORIES.items():
        moved_files[category] = []
        
        for pattern in config['patterns']:
            # Search in root directory
            for file_path in PROJECT_ROOT.glob(pattern):
                if file_path.is_file() and not should_keep_file(file_path, PRODUCTION_FILES):
                    dest_file = move_file_to_archive(file_path, config['destination'])
                    moved_files[category].append(str(dest_file))
            
            # Search in backend directory
            backend_dir = PROJECT_ROOT / 'backend'
            if backend_dir.exists():
                for file_path in backend_dir.glob(pattern):
                    if file_path.is_file() and not should_keep_file(file_path, PRODUCTION_BACKEND_FILES):
                        dest_file = move_file_to_archive(file_path, config['destination'])
                        moved_files[category].append(str(dest_file))
    
    return moved_files

def cleanup_specific_files():
    """Clean up specific files that need special handling."""
    moved_files = []
    
    # Files in root that are not production essentials
    for file_path in PROJECT_ROOT.iterdir():
        if (file_path.is_file() and 
            not should_keep_file(file_path, PRODUCTION_FILES) and
            not file_path.name.startswith('.')):
            
            # Determine destination based on file type
            if 'test' in file_path.name.lower():
                dest = 'archived/tests'
            elif 'debug' in file_path.name.lower():
                dest = 'archived/debug'
            elif any(keyword in file_path.name.lower() for keyword in ['diagnostic', 'investigation', 'troubleshooting']):
                dest = 'archived/diagnostics'
            elif any(keyword in file_path.name.lower() for keyword in ['monitor', 'check', 'verify']):
                dest = 'archived/monitoring'
            else:
                dest = 'archived/misc'
            
            dest_file = move_file_to_archive(file_path, dest)
            moved_files.append(str(dest_file))
    
    # Files in backend that are not production essentials
    backend_dir = PROJECT_ROOT / 'backend'
    if backend_dir.exists():
        for file_path in backend_dir.iterdir():
            if (file_path.is_file() and 
                not should_keep_file(file_path, PRODUCTION_BACKEND_FILES) and
                not file_path.name.startswith('.') and
                file_path.name not in ['test.html', 'debug-test.html']):
                
                # Determine destination based on file type
                if 'test' in file_path.name.lower():
                    dest = 'archived/tests'
                elif 'debug' in file_path.name.lower():
                    dest = 'archived/debug'
                elif 'performance' in file_path.name.lower():
                    dest = 'archived/performance'
                else:
                    dest = 'archived/misc'
                
                dest_file = move_file_to_archive(file_path, dest)
                moved_files.append(str(dest_file))
    
    return moved_files

def create_production_structure_doc():
    """Create a document describing the production structure."""
    structure = {
        "production_structure": {
            "root_files": sorted(list(PRODUCTION_FILES)),
            "backend_files": sorted(list(PRODUCTION_BACKEND_FILES)),
            "directories": {
                "backend/": "Core FastAPI application",
                "frontend/": "Frontend application",
                "docs/": "Documentation",
                "archived/": "Non-production files (tests, debug, etc.)"
            }
        },
        "cleanup_date": datetime.now().isoformat(),
        "purpose": "Production-ready workspace structure"
    }
    
    with open(PROJECT_ROOT / 'PRODUCTION_STRUCTURE.json', 'w') as f:
        json.dump(structure, f, indent=2)

def main():
    """Main cleanup function."""
    print("🧹 Starting final comprehensive cleanup...")
    print(f"Project root: {PROJECT_ROOT}")
    
    # Create archive directory
    archive_dir = PROJECT_ROOT / 'archived'
    archive_dir.mkdir(exist_ok=True)
    
    # Clean up by patterns
    print("\n1. Cleaning up by patterns...")
    pattern_moved = cleanup_by_patterns()
    
    # Clean up specific files
    print("\n2. Cleaning up specific files...")
    specific_moved = cleanup_specific_files()
    
    # Clean up caches
    print("\n3. Cleaning up caches...")
    cleanup_pycache()
    cleanup_node_modules()
    
    # Create production structure documentation
    print("\n4. Creating production structure documentation...")
    create_production_structure_doc()
    
    # Summary
    print("\n✅ Cleanup complete!")
    print(f"📁 Archived files moved to: {archive_dir}")
    
    total_moved = sum(len(files) for files in pattern_moved.values()) + len(specific_moved)
    print(f"📊 Total files moved: {total_moved}")
    
    for category, files in pattern_moved.items():
        if files:
            print(f"  - {category}: {len(files)} files")
    
    if specific_moved:
        print(f"  - specific files: {len(specific_moved)} files")
    
    print(f"\n📝 Production structure documented in: PRODUCTION_STRUCTURE.json")
    print("\n🎯 Workspace is now production-ready!")

if __name__ == "__main__":
    main()
