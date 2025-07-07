#!/usr/bin/env python3
"""
Test frontend authentication flow
"""

import time
import requests
import json

# Test the authentication flow
def test_auth_flow():
    print("Testing authentication flow...")
    
    # Test login
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post("http://localhost:8000/api/auth/login", json=login_data)
    print(f"Login response status: {response.status_code}")
    
    if response.status_code == 200:
        auth_data = response.json()
        print(f"Login successful!")
        print(f"Access token: {auth_data['access_token'][:50]}...")
        print(f"User: {auth_data['user']['username']}")
        print(f"Email: {auth_data['user']['email']}")
        print(f"User ID: {auth_data['user']['id']}")
        
        # Test authenticated request
        headers = {"Authorization": f"Bearer {auth_data['access_token']}"}
        
        # Test profile endpoint
        profile_response = requests.get("http://localhost:8000/api/profiles", headers=headers)
        print(f"Profile response status: {profile_response.status_code}")
        
        if profile_response.status_code == 200:
            profiles = profile_response.json()
            print(f"Found {len(profiles)} profiles")
            
        # Test health endpoint
        health_response = requests.get("http://localhost:8000/api/health", headers=headers)
        print(f"Health response status: {health_response.status_code}")
        
        return True
    else:
        print(f"Login failed: {response.text}")
        return False

if __name__ == "__main__":
    test_auth_flow()
