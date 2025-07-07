#!/usr/bin/env python3
"""
Test authentication flow directly on listings.html page
"""

import time
import subprocess
import sys

def test_direct_auth():
    print("Testing direct authentication on listings.html...")
    
    # Open the listings page directly
    print("1. Opening listings.html directly...")
    print("   URL: http://localhost:8000/listings.html")
    print("   This should show the login/register buttons in the header")
    
    print("\n2. Test authentication flow:")
    print("   - Click 'Login' button in header")
    print("   - Should show authentication modal (not redirect to /)")
    print("   - Enter credentials: admin / admin123")
    print("   - Should login successfully and show user menu with admin dropdown")
    print("   - User dropdown should contain 'Admin Panel' link")
    
    print("\n3. Expected behavior:")
    print("   - Authentication modal appears when clicking Login")
    print("   - Login succeeds with admin/admin123 credentials")
    print("   - User menu shows 'admin' username")
    print("   - Dropdown menu contains 'Admin Panel' option")
    print("   - Admin Panel link should be visible and clickable")
    
    print("\n4. Manual testing instructions:")
    print("   a) Open http://localhost:8000/listings.html in your browser")
    print("   b) Click 'Login' button in the top-right header")
    print("   c) Enter username: admin")
    print("   d) Enter password: admin123")
    print("   e) Click 'Sign In'")
    print("   f) Verify user menu appears with 'admin' username")
    print("   g) Click the dropdown arrow next to 'admin'")
    print("   h) Verify 'Admin Panel' option is visible with gear icon")
    print("   i) Click 'Admin Panel' to test access")
    
    print("\n5. If admin panel link is not visible:")
    print("   - Check browser console for JavaScript errors")
    print("   - Verify updateAuthUI function is called after login")
    print("   - Check if user menu dropdown is working")
    
    return True

if __name__ == "__main__":
    test_direct_auth()
