#!/usr/bin/env python3
"""
Test Railway deployment and investigate issues
"""

import requests
import time
from datetime import datetime

def test_railway_deployment():
    """Test different Railway URLs and endpoints"""
    
    # Common Railway URL patterns
    railway_urls = [
        "https://house-scraper-production.up.railway.app",
        "https://house-scraper-production-up.railway.app",
        "https://web-production-up.railway.app",
        "https://house-scraper-production-up.railway.app",
    ]
    
    print("TESTING RAILWAY DEPLOYMENT")
    print("=" * 50)
    
    for url in railway_urls:
        print(f"\nTesting: {url}")
        
        try:
            # Test basic health check
            response = requests.get(f"{url}/health", timeout=10)
            print(f"  /health: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✓ Health check passed")
                
                # Test API endpoints
                endpoints = [
                    "/api/scraper/status",
                    "/api/admin/stats",
                    "/admin-scraper.html"
                ]
                
                for endpoint in endpoints:
                    try:
                        resp = requests.get(f"{url}{endpoint}", timeout=10)
                        print(f"  {endpoint}: {resp.status_code}")
                    except Exception as e:
                        print(f"  {endpoint}: ERROR - {e}")
                        
        except requests.exceptions.ConnectionError:
            print(f"  ✗ Connection failed")
        except requests.exceptions.Timeout:
            print(f"  ✗ Timeout")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 50)
    print("If all URLs fail, the Railway deployment may be down")
    print("Check Railway dashboard for deployment status")

if __name__ == "__main__":
    test_railway_deployment()
