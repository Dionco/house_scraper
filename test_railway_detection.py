#!/usr/bin/env python3
"""
Test the Railway detection and import logic
"""

import os
import sys
sys.path.append('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/backend')

def test_railway_detection():
    # Import the function
    from auth_utils import is_running_on_railway
    
    print("🔍 Testing Railway detection...")
    
    # Test current environment
    print(f"Current environment:")
    print(f"  RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
    print(f"  RAILWAY_PROJECT_ID: {os.getenv('RAILWAY_PROJECT_ID', 'Not set')}")
    print(f"  RAILWAY_SERVICE_ID: {os.getenv('RAILWAY_SERVICE_ID', 'Not set')}")
    print(f"  PORT: {os.getenv('PORT', 'Not set')}")
    
    is_railway = is_running_on_railway()
    print(f"\n🎯 Railway detection result: {is_railway}")
    
    if is_railway:
        print("✅ Running on Railway - will use relative import (.api)")
    else:
        print("✅ Running locally - will use absolute import (api)")
    
    # Test the import logic
    print("\n🧪 Testing import logic...")
    try:
        if is_railway:
            print("Attempting: from .api import load_db")
            # We can't actually test this without being in the right context
            print("ℹ️  This would use relative import in Railway environment")
        else:
            print("Attempting: from api import load_db")
            try:
                from api import load_db
                print("✅ Local import successful")
            except ImportError as e:
                print(f"❌ Local import failed: {e}")
                print("ℹ️  This is expected if not running from the right directory")
    except Exception as e:
        print(f"❌ Import test failed: {e}")

if __name__ == "__main__":
    test_railway_detection()
