#!/usr/bin/env python3
"""
Reset admin password script for House Scraper
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
admin_user_id = None
for user_id, user in db.get('users', {}).items():
    if user.get('username') == 'admin':
        admin_user = user
        admin_user_id = user_id
        break

if admin_user:
    print(f"Found admin user: {admin_user['username']}")
    
    # Update the password hash
    new_password = 'admin123'
    new_hash = AuthUtils.hash_password(new_password)
    
    # Update the user in the database
    db['users'][admin_user_id]['password_hash'] = new_hash
    
    # Save the database
    with open('database.json', 'w') as f:
        json.dump(db, f, indent=2)
    
    print(f"✓ Admin password has been reset to: {new_password}")
    print(f"✓ New hash: {new_hash}")
    
    # Verify the change
    if AuthUtils.verify_password(new_password, new_hash):
        print("✓ Password verification successful!")
    else:
        print("✗ Password verification failed!")
        
else:
    print("No admin user found in database")
