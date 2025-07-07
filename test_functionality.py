#!/usr/bin/env python3
"""
Comprehensive test script for the House Scraper project.
Tests all major functionality including API endpoints, authentication, and data handling.
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_health_endpoint():
    """Test the health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health endpoint: {response.status_code} - {response.json()['status']}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_user_registration():
    """Test user registration"""
    try:
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPass123!"
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User registration successful: {data['user']['username']}")
            return data['access_token'], data['user']['id']
        else:
            print(f"❌ User registration failed: {response.status_code} - {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ User registration error: {e}")
        return None, None

def test_user_login(username, password):
    """Test user login"""
    try:
        login_data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ User login successful: {data['user']['username']}")
            return data['access_token']
        else:
            print(f"❌ User login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ User login error: {e}")
        return None

def test_profile_creation(token):
    """Test profile creation"""
    try:
        profile_data = {
            "name": "Test Profile Amsterdam",
            "filters": {
                "city": "Amsterdam",
                "min_price": "2500",
                "max_price": "4500",
                "min_bedrooms": "2"
            }
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/profiles", json=profile_data, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile creation successful: {data['name']} ({data['id']})")
            return data['id']
        else:
            print(f"❌ Profile creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Profile creation error: {e}")
        return None

def test_profile_listing(token):
    """Test profile listing"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/profiles", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Profile listing successful: {len(data)} profiles found")
            return True
        else:
            print(f"❌ Profile listing failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Profile listing error: {e}")
        return False

def test_manual_scraping(token, profile_id):
    """Test manual scraping trigger"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/api/profiles/{profile_id}/scrape", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Manual scraping successful: {data['message']}")
            return True
        else:
            print(f"❌ Manual scraping failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Manual scraping error: {e}")
        return False

def test_listings_endpoint():
    """Test listings endpoint"""
    try:
        # Test basic listings
        response = requests.get(f"{BASE_URL}/api/listings?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Listings endpoint: {len(data['listings'])} listings retrieved")
            
            # Test with city filter
            response = requests.get(f"{BASE_URL}/api/listings?city=Amsterdam&limit=3")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Listings with city filter: {len(data['listings'])} Amsterdam listings")
                
                # Test with price filter
                response = requests.get(f"{BASE_URL}/api/listings?min_price=3000&max_price=4000&limit=3")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Listings with price filter: {len(data['listings'])} listings in price range")
                    return True
        
        print(f"❌ Listings endpoint failed")
        return False
    except Exception as e:
        print(f"❌ Listings endpoint error: {e}")
        return False

def test_scraper_status():
    """Test scraper status endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/scraper/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scraper status: Running={data['is_running']}, Jobs={data['total_jobs']}")
            return True
        else:
            print(f"❌ Scraper status failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Scraper status error: {e}")
        return False

def test_data_endpoint():
    """Test data endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/data")
        if response.status_code == 200:
            data = response.json()
            user_count = len(data.get('users', {}))
            profile_count = len(data.get('profiles', {}))
            print(f"✅ Data endpoint: {user_count} users, {profile_count} profiles")
            return True
        else:
            print(f"❌ Data endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting House Scraper Comprehensive Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test basic endpoints
    print("📋 Testing Basic Endpoints")
    print("-" * 30)
    if not test_health_endpoint():
        print("❌ Health check failed - stopping tests")
        return
    
    test_data_endpoint()
    test_scraper_status()
    test_listings_endpoint()
    
    print()
    
    # Test authentication flow
    print("🔐 Testing Authentication Flow")
    print("-" * 30)
    
    # Register a new user
    token, user_id = test_user_registration()
    if not token:
        print("❌ Registration failed - stopping auth tests")
        return
    
    # Test profile management
    print()
    print("📊 Testing Profile Management")
    print("-" * 30)
    
    profile_id = test_profile_creation(token)
    if profile_id:
        test_profile_listing(token)
        test_manual_scraping(token, profile_id)
    
    print()
    print("=" * 60)
    print("✅ Test Suite Complete!")
    print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
