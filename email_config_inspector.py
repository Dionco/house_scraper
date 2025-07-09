#!/usr/bin/env python3
"""
Check the actual email sending in the scraper system
"""

import sys
import os
sys.path.append('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/backend')

import json
from email_utils import EmailSender

def check_profile_email_config():
    print("🔍 Checking profile email configuration...")
    
    # Load database
    with open('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/database.json', 'r') as f:
        database = json.load(f)
    
    profiles = database.get('profiles', {})
    
    for profile_id, profile in profiles.items():
        print(f"\n📋 Profile: {profile.get('name', 'Unknown')}")
        print(f"   ID: {profile_id}")
        print(f"   Email field: {profile.get('email', 'Not set')}")
        print(f"   Emails array: {profile.get('emails', [])}")
        print(f"   Last scraped: {profile.get('last_scraped', 'Never')}")
        print(f"   Last new listings count: {profile.get('last_new_listings_count', 0)}")
        
        # Check if emails are configured
        email_field = profile.get('email')
        emails_array = profile.get('emails', [])
        
        if not email_field and not emails_array:
            print(f"   ⚠️  No email notifications configured for this profile")
        elif email_field and not emails_array:
            print(f"   ⚠️  Email field set but emails array is empty")
        elif emails_array:
            print(f"   ✅ Email notifications configured for: {emails_array}")

def simulate_new_listings_email():
    print("\n🧪 Simulating new listings email...")
    
    # Create sample new listings
    sample_listings = [
        {
            'address.street_name': 'Jordaan Street 45',
            'address.postal_code': '1016 AB',
            'price.rent_price': 2200,
            'number_of_bedrooms': 2,
            'floor_area': 80,
            'energy_label': 'A',
            'image_url': 'https://example.com/image1.jpg',
            'funda_url': 'https://funda.nl/listing/456'
        },
        {
            'address.street_name': 'Canal View 12',
            'address.postal_code': '1017 CD',
            'price.rent_price': 2800,
            'number_of_bedrooms': 3,
            'floor_area': 95,
            'energy_label': 'B',
            'image_url': 'https://example.com/image2.jpg',
            'funda_url': 'https://funda.nl/listing/789'
        }
    ]
    
    sender = EmailSender()
    
    # Test sending to your actual email
    test_email = "dioncobelens@me.com"
    profile_name = "Amsterdam Central - Test"
    
    print(f"Sending simulation email to: {test_email}")
    print(f"Profile: {profile_name}")
    print(f"Number of listings: {len(sample_listings)}")
    
    success = sender.send_new_listings_email(
        to_email=test_email,
        profile_name=profile_name,
        new_listings=sample_listings
    )
    
    if success:
        print("✅ Simulation email sent successfully!")
        print("📧 Check your email for 'New Funda listings for Amsterdam Central - Test'")
    else:
        print("❌ Simulation email failed!")

def check_recent_scraping_activity():
    print("\n📊 Checking recent scraping activity...")
    
    # Load database
    with open('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/database.json', 'r') as f:
        database = json.load(f)
    
    profiles = database.get('profiles', {})
    
    for profile_id, profile in profiles.items():
        name = profile.get('name', 'Unknown')
        last_scraped = profile.get('last_scraped', 'Never')
        last_new_count = profile.get('last_new_listings_count', 0)
        
        print(f"\n📋 {name}:")
        print(f"   Last scraped: {last_scraped}")
        print(f"   Last new listings found: {last_new_count}")
        
        if last_new_count > 0:
            print(f"   ✅ Recently found {last_new_count} new listings")
        else:
            print(f"   ℹ️  No new listings found in last scrape")

if __name__ == "__main__":
    print("🔍 Email Configuration Inspector")
    print("=" * 50)
    
    check_profile_email_config()
    check_recent_scraping_activity()
    simulate_new_listings_email()
    
    print("\n" + "=" * 50)
    print("🎯 Summary:")
    print("1. Check your email inbox and spam folder")
    print("2. Look for emails from 'funda.scraper.alerts.bot@gmail.com'")
    print("3. If you find test emails but not scraper emails, the issue is in the scraper logic")
    print("4. If you don't find any emails, check your email client settings")
