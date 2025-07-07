#!/usr/bin/env python3
"""
Debug authentication script for House Scraper
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import json
from auth_utils import AuthUtils

# Load the database
with open('database.json', 'r') as f:
    db = json.load(f)

# Find the admin user
admin_user = None
for user_id, user in db.get('users', {}).items():
    if user.get('username') == 'admin':
        admin_user = user
        break

if admin_user:
    print(f"Found admin user: {admin_user['username']}")
    print(f"Email: {admin_user['email']}")
    print(f"Active: {admin_user['is_active']}")
    print(f"Password hash: {admin_user['password_hash']}")
    
    # Test common passwords
    test_passwords = ['admin123', 'admin', 'password', 'Admin123', 'Admin', 'PASSWORD']
    
    for password in test_passwords:
        try:
            if AuthUtils.verify_password(password, admin_user['password_hash']):
                print(f"✓ Password '{password}' works!")
                break
        except Exception as e:
            print(f"✗ Error checking password '{password}': {e}")
    else:
        print("✗ None of the test passwords work.")
        
    # Let's also try to create a new admin with a known password
    print("\n--- Creating new admin with password 'admin123' ---")
    new_hash = AuthUtils.hash_password('admin123')
    print(f"New hash: {new_hash}")
    
    # Verify the new hash works
    if AuthUtils.verify_password('admin123', new_hash):
        print("✓ New hash verification works!")
    else:
        print("✗ New hash verification failed!")
        
else:
    print("No admin user found in database")
    
    # Let's see what users exist
    print("\nExisting users:")
    for user_id, user in db.get('users', {}).items():
        print(f"- {user['username']} ({user['email']})")
