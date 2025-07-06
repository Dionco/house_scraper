#!/usr/bin/env python3
"""
Comprehensive workspace cleanup script for House Scraper project
"""
import os
import shutil
import json
import glob
from pathlib import Path
from datetime import datetime

def clean_workspace():
    """Perform comprehensive cleanup of the workspace"""
    
    workspace_root = "/Users/Dion/Downloads/Documenten/Code projects/House_scraper"
    backend_root = os.path.join(workspace_root, "backend")
    
    print("🧹 STARTING COMPREHENSIVE WORKSPACE CLEANUP")
    print(f"Root: {workspace_root}")
    print(f"Backend: {backend_root}")
    
    # Create cleanup directories
    cleanup_dirs = {
        "archive": os.path.join(workspace_root, "archive"),
        "test_files": os.path.join(workspace_root, "archive", "test_files"),
        "debug_files": os.path.join(workspace_root, "archive", "debug_files"),
        "old_scripts": os.path.join(workspace_root, "archive", "old_scripts"),
        "deployment_files": os.path.join(workspace_root, "archive", "deployment_files"),
        "backups": os.path.join(workspace_root, "archive", "backups")
    }
    
    for dir_name, dir_path in cleanup_dirs.items():
        os.makedirs(dir_path, exist_ok=True)
        print(f"✓ Created {dir_name}: {dir_path}")
    
    total_moved = 0
    total_deleted = 0
    
    # 1. CLEAN ROOT DIRECTORY
    print("\n📁 CLEANING ROOT DIRECTORY...")
    
    root_files_to_archive = [
        "check_profile_status.py",
        "deployment_analysis.py", 
        "detailed_railway_check.py",
        "diagnostic_scraping.py",
        "investigation_summary.py",
        "migrate_timestamps.py",
        "monitor_local_scraper.py",
        "monitor_railway_scrape.py", 
        "monitor_scrapes.py",
        "railway_diagnostic.py",
        "railway_troubleshooting.py",
        "scraper_investigation.py",
        "test_auth_system.py",
        "test_manual_scrape.py",
        "test_periodic_scraping.py",
        "test_railway.py",
        "test_scraping_system.py",
        "test_timezone_changes.py",
        "trigger_manual_scrapes.py",
        "update_profile_responses.py",
        "verify_scraping_fixed.py"
    ]
    
    for file in root_files_to_archive:
        src = os.path.join(workspace_root, file)
        if os.path.exists(src):
            if file.startswith(('test_', 'check_', 'verify_')):
                dst = os.path.join(cleanup_dirs["test_files"], file)
            elif file.startswith(('monitor_', 'diagnostic', 'investigation')):
                dst = os.path.join(cleanup_dirs["debug_files"], file)
            elif 'railway' in file or 'deploy' in file:
                dst = os.path.join(cleanup_dirs["deployment_files"], file)
            else:
                dst = os.path.join(cleanup_dirs["old_scripts"], file)
            
            shutil.move(src, dst)
            print(f"  ✓ Moved {file}")
            total_moved += 1
    
    # Archive deployment files
    deployment_files = [
        "Dockerfile.minimal",
        "Dockerfile.railway", 
        "netlify.toml",
        "railway.toml",
        "render.yaml"
    ]
    
    for file in deployment_files:
        src = os.path.join(workspace_root, file)
        if os.path.exists(src):
            dst = os.path.join(cleanup_dirs["deployment_files"], file)
            shutil.move(src, dst)
            print(f"  ✓ Moved {file}")
            total_moved += 1
    
    # Archive backup files
    backup_files = [
        "database.json.backup_1751646531",
        "search_profiles.json"
    ]
    
    for file in backup_files:
        src = os.path.join(workspace_root, file)
        if os.path.exists(src):
            dst = os.path.join(cleanup_dirs["backups"], file)
            shutil.move(src, dst)
            print(f"  ✓ Moved {file}")
            total_moved += 1
    
    # 2. CLEAN BACKEND DIRECTORY
    print("\n🔧 CLEANING BACKEND DIRECTORY...")
    
    backend_files_to_archive = [
        "api.py.backup",
        "debug_bedroom_comprehensive.py",
        "debug_bedroom_extraction.py", 
        "debug_funda.py",
        "debug_leiden.html",
        "debug_leiden_current.html",
        "debug_leiden_listings.json",
        "debug_leiden_rental_listings.json",
        "debug_rental_structure.html",
        "debug_rental_structure.py",
        "extract_funda_listings_fast.py",
        "migrate_database.py",
        "migrate_listings_format.py",
        "performance_test.py",
        "performance_test_results_1751826243.json",
        "scrape_funda_async.py",
        "test_comprehensive_scraper.py",
        "test_email.py",
        "test_full_system.py",
        "test_leiden_rental_scraper.py",
        "test_leiden_scraper.py",
        "test_new_today.py",
        "test_rental_system_final.py",
        "test_scraper.py",
        "comprehensive_test_results.json"
    ]
    
    for file in backend_files_to_archive:
        src = os.path.join(backend_root, file)
        if os.path.exists(src):
            if file.startswith('test_') or 'test' in file:
                dst = os.path.join(cleanup_dirs["test_files"], file)
            elif file.startswith('debug_') or file.endswith('.html') or file.endswith('.json') and 'debug' in file:
                dst = os.path.join(cleanup_dirs["debug_files"], file)
            elif 'performance' in file or 'async' in file or 'fast' in file:
                dst = os.path.join(cleanup_dirs["old_scripts"], file)
            elif 'migrate' in file or '.backup' in file:
                dst = os.path.join(cleanup_dirs["backups"], file)
            else:
                dst = os.path.join(cleanup_dirs["old_scripts"], file)
            
            shutil.move(src, dst)
            print(f"  ✓ Moved {file}")
            total_moved += 1
    
    # Clean HTML test files
    html_test_files = [
        "admin-scraper.html",
        "debug-test.html", 
        "listings-simple.html",
        "listings.html",
        "test-listings.html",
        "test.html"
    ]
    
    for file in html_test_files:
        src = os.path.join(backend_root, file)
        if os.path.exists(src):
            dst = os.path.join(cleanup_dirs["test_files"], file)
            shutil.move(src, dst)
            print(f"  ✓ Moved {file}")
            total_moved += 1
    
    # 3. CLEAN PYCACHE AND TEMP FILES
    print("\n🗑️  CLEANING CACHE AND TEMP FILES...")
    
    # Remove __pycache__ directories
    pycache_dirs = glob.glob(os.path.join(workspace_root, "**", "__pycache__"), recursive=True)
    for cache_dir in pycache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"  ✓ Removed {cache_dir}")
            total_deleted += 1
    
    # Remove .pyc files
    pyc_files = glob.glob(os.path.join(workspace_root, "**", "*.pyc"), recursive=True)
    for pyc_file in pyc_files:
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            print(f"  ✓ Removed {pyc_file}")
            total_deleted += 1
    
    # Clean node_modules if not needed
    node_modules_path = os.path.join(backend_root, "node_modules")
    if os.path.exists(node_modules_path):
        print(f"  ⚠️  node_modules found at {node_modules_path}")
        print(f"     Consider removing if not needed: rm -rf {node_modules_path}")
    
    # 4. ORGANIZE DOCUMENTATION
    print("\n📚 ORGANIZING DOCUMENTATION...")
    
    docs_to_keep = [
        "README.md",
        "DEPLOYMENT.md",
        "NEW_TODAY_IMPLEMENTATION.md", 
        "PERFORMANCE_OPTIMIZATIONS.md",
        "PERIODIC_SCRAPING.md"
    ]
    
    docs_to_archive = [
        "CLEANUP_SUMMARY.md"
    ]
    
    for file in docs_to_archive:
        src = os.path.join(workspace_root, file)
        if os.path.exists(src):
            dst = os.path.join(cleanup_dirs["old_scripts"], file)
            shutil.move(src, dst)
            print(f"  ✓ Moved {file}")
            total_moved += 1
    
    # 5. CLEAN DEPRECATED DIRECTORIES
    print("\n🗂️  CLEANING DEPRECATED DIRECTORIES...")
    
    deprecated_dirs = [
        os.path.join(backend_root, "deprecated"),
        os.path.join(backend_root, "debug")
    ]
    
    for dep_dir in deprecated_dirs:
        if os.path.exists(dep_dir):
            dst = os.path.join(cleanup_dirs["old_scripts"], os.path.basename(dep_dir))
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(dep_dir, dst)
            print(f"  ✓ Moved {dep_dir}")
            total_moved += 1
    
    # 6. CLEAN BACKEND ENVIRONMENT FILES
    print("\n🔐 ORGANIZING ENVIRONMENT FILES...")
    
    # Keep only one .env file in backend
    backend_env_files = [".env", ".env.example"]
    backend_env_existing = []
    
    for env_file in backend_env_files:
        env_path = os.path.join(backend_root, env_file)
        if os.path.exists(env_path):
            backend_env_existing.append(env_file)
    
    print(f"  ✓ Backend environment files: {backend_env_existing}")
    
    # 7. CREATE CURRENT PROJECT STRUCTURE SUMMARY
    print("\n📋 CREATING PROJECT STRUCTURE SUMMARY...")
    
    current_structure = {
        "core_files": {
            "backend": [
                "api.py",
                "auth_models.py", 
                "auth_utils.py",
                "email_utils.py",
                "extract_funda_listings.py",
                "funda_url_builder.py",
                "listing_mapping.py",
                "periodic_scraper.py",
                "scrape_api.py",
                "scrape_funda.py",
                "timezone_utils.py"
            ],
            "frontend": [
                "index.html",
                "app.js", 
                "auth.js"
            ],
            "root": [
                "database.json",
                "README.md",
                "Dockerfile"
            ]
        },
        "data_files": [
            "funda_simple_listings.json"
        ],
        "archived_files": total_moved,
        "deleted_files": total_deleted,
        "cleanup_date": datetime.now().isoformat()
    }
    
    structure_file = os.path.join(workspace_root, "PROJECT_STRUCTURE.json")
    with open(structure_file, 'w', encoding='utf-8') as f:
        json.dump(current_structure, f, indent=2, ensure_ascii=False)
    
    print(f"  ✓ Created project structure summary: {structure_file}")
    
    # 8. CREATE CLEANUP SUMMARY
    cleanup_summary = f"""# WORKSPACE CLEANUP SUMMARY

## Cleanup Date
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Statistics
- Files moved to archive: {total_moved}
- Files deleted: {total_deleted}
- Cache directories removed: {len(pycache_dirs)}

## Current Active Project Structure

### Core Backend Files
- api.py - Main FastAPI application
- auth_models.py, auth_utils.py - Authentication system
- extract_funda_listings.py - HTML extraction logic
- scrape_funda.py - Web scraping engine 
- periodic_scraper.py - Automated scraping scheduler
- scrape_api.py - Scraping API endpoints
- listing_mapping.py - Data transformation
- funda_url_builder.py - URL generation
- email_utils.py - Email notifications
- timezone_utils.py - Timezone handling

### Core Frontend Files  
- index.html - Main UI
- app.js - Frontend logic
- auth.js - Authentication UI

### Data Files
- database.json - Main database
- funda_simple_listings.json - Scraped listings cache

### Configuration
- requirements.txt - Python dependencies
- package.json - Node.js dependencies (if needed)
- Dockerfile - Container configuration

## Archived Content
All test files, debug files, old scripts, and temporary files have been moved to:
- archive/test_files/ - Test scripts and HTML files
- archive/debug_files/ - Debug scripts and data dumps
- archive/old_scripts/ - Deprecated code and utilities
- archive/deployment_files/ - Alternative deployment configs
- archive/backups/ - Database backups and old configs

## Next Steps
1. Review archived files before permanent deletion
2. Update dependencies if needed
3. Test core functionality
4. Consider removing node_modules if not used
5. Update documentation if needed
"""
    
    summary_file = os.path.join(workspace_root, "CLEANUP_SUMMARY.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(cleanup_summary)
    
    print(f"  ✓ Created cleanup summary: {summary_file}")
    
    # 9. FINAL VERIFICATION
    print("\n✅ CLEANUP VERIFICATION...")
    
    # Check core files exist
    core_files = [
        os.path.join(backend_root, "api.py"),
        os.path.join(backend_root, "scrape_funda.py"),
        os.path.join(backend_root, "extract_funda_listings.py"),
        os.path.join(workspace_root, "database.json"),
        os.path.join(workspace_root, "frontend", "index.html")
    ]
    
    missing_files = []
    for file in core_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("  ⚠️  WARNING: Missing core files:")
        for file in missing_files:
            print(f"    - {file}")
    else:
        print("  ✓ All core files present")
    
    print(f"\n🎉 CLEANUP COMPLETED!")
    print(f"📊 Summary:")
    print(f"   - {total_moved} files archived")
    print(f"   - {total_deleted} files/directories deleted")
    print(f"   - Project structure documented")
    print(f"   - Archive created at: {cleanup_dirs['archive']}")
    
    return {
        "moved": total_moved,
        "deleted": total_deleted,
        "archive_path": cleanup_dirs["archive"]
    }

if __name__ == "__main__":
    result = clean_workspace()
    print(f"\nCleanup result: {result}")
