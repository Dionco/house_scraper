#!/usr/bin/env python3
"""
Test script to verify that the authentication system is working correctly.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8002"
TEST_USER = {
    "username": "testuser123",
    "email": "testuser123@example.com",
    "password": "testpassword123"
}

def test_authentication_system():
    """Test the complete authentication system."""
    
    print("🔐 Testing House Scraper Authentication System")
    print("=" * 60)
    
    # Test 1: User Registration
    print("\n1. Testing User Registration...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=TEST_USER,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ User registration successful")
            user_data = response.json()
            print(f"   User ID: {user_data['user']['id']}")
            print(f"   Username: {user_data['user']['username']}")
        elif response.status_code == 400 and "already registered" in response.text:
            print("⚠️  User already exists - continuing with login test")
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration request failed: {e}")
        return False
    
    # Test 2: User Login
    print("\n2. Testing User Login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": TEST_USER["username"], "password": TEST_USER["password"]},
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ User login successful")
            login_data = response.json()
            access_token = login_data['access_token']
            print(f"   Access token received: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Login request failed: {e}")
        return False
    
    # Test 3: Authenticated Profile Operations
    print("\n3. Testing Authenticated Profile Operations...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test 3a: Get Profiles
    print("   3a. Getting user profiles...")
    try:
        response = requests.get(f"{BASE_URL}/api/profiles", headers=headers, timeout=10)
        if response.status_code == 200:
            profiles = response.json()
            print(f"   ✅ Retrieved {len(profiles)} profiles")
        else:
            print(f"   ❌ Failed to get profiles: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Get profiles request failed: {e}")
        return False
    
    # Test 3b: Create Profile
    print("   3b. Creating test profile...")
    test_profile = {
        "name": f"Test Profile {datetime.now().strftime('%H%M%S')}",
        "filters": {"city": "Amsterdam", "min_price": "2000", "max_price": "4000"},
        "emails": ["test@example.com"],
        "scrape_interval_hours": 6
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/profiles",
            json=test_profile,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Profile created successfully")
            created_profile = response.json()
            profile_id = created_profile['id']
            print(f"   Profile ID: {profile_id}")
        else:
            print(f"   ❌ Failed to create profile: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Create profile request failed: {e}")
        return False
    
    # Test 3c: Update Profile
    print("   3c. Updating profile...")
    try:
        response = requests.put(
            f"{BASE_URL}/api/profiles/{profile_id}",
            json={"name": "Updated Test Profile", "filters": {"city": "Utrecht", "min_price": "2500"}},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Profile updated successfully")
        else:
            print(f"   ❌ Failed to update profile: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Update profile request failed: {e}")
        return False
    
    # Test 3d: Update Profile Emails
    print("   3d. Updating profile emails...")
    try:
        response = requests.put(
            f"{BASE_URL}/api/profiles/{profile_id}/email",
            json={"emails": ["updated@example.com", "test2@example.com"]},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Profile emails updated successfully")
        else:
            print(f"   ❌ Failed to update profile emails: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Update profile emails request failed: {e}")
        return False
    
    # Test 3e: Update Scrape Interval
    print("   3e. Updating scrape interval...")
    try:
        response = requests.put(
            f"{BASE_URL}/api/profiles/{profile_id}/scrape-interval",
            json={"scrape_interval_hours": 8},
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Scrape interval updated successfully")
        else:
            print(f"   ❌ Failed to update scrape interval: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Update scrape interval request failed: {e}")
        return False
    
    # Test 3f: Trigger Scrape
    print("   3f. Triggering manual scrape...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/profiles/{profile_id}/scrape",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("   ✅ Manual scrape triggered successfully")
        else:
            print(f"   ❌ Failed to trigger scrape: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Trigger scrape request failed: {e}")
        return False
    
    # Test 3g: Delete Profile
    print("   3g. Deleting test profile...")
    try:
        response = requests.delete(
            f"{BASE_URL}/api/profiles/{profile_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code in [200, 204]:
            print("   ✅ Profile deleted successfully")
        else:
            print(f"   ❌ Failed to delete profile: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Delete profile request failed: {e}")
        return False
    
    # Test 4: Test Unauthenticated Access
    print("\n4. Testing Unauthenticated Access Protection...")
    try:
        response = requests.get(f"{BASE_URL}/api/profiles", timeout=10)
        if response.status_code == 401:
            print("✅ Unauthenticated access properly blocked")
        else:
            print(f"❌ Unauthenticated access not blocked: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Unauthenticated access test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! Authentication system is working correctly.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = test_authentication_system()
    exit(0 if success else 1)
