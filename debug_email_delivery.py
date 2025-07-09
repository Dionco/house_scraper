#!/usr/bin/env python3
"""
Debug email sending to identify why emails aren't being received
"""

import sys
import os
sys.path.append('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/backend')

from email_utils import EmailSender
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def debug_email_sending():
    print("🔍 Debugging email sending process...")
    
    # Check environment variables
    print("\n📧 SMTP Configuration:")
    print(f"SMTP_HOST: {os.environ.get('SMTP_HOST', 'Not set')}")
    print(f"SMTP_PORT: {os.environ.get('SMTP_PORT', 'Not set')}")
    print(f"SMTP_USER: {os.environ.get('SMTP_USER', 'Not set')}")
    print(f"SMTP_PASS: {'*' * len(os.environ.get('SMTP_PASS', '')) if os.environ.get('SMTP_PASS') else 'Not set'}")
    print(f"FROM_EMAIL: {os.environ.get('FROM_EMAIL', 'Not set')}")
    
    # Create EmailSender instance
    sender = EmailSender()
    
    # Test SMTP connection
    print("\n🔌 Testing SMTP connection...")
    connection_ok = sender.test_smtp_connection()
    
    if not connection_ok:
        print("❌ SMTP connection failed. Email sending will not work.")
        return False
    
    # Test email sending with sample data
    print("\n📨 Testing email sending...")
    
    sample_listings = [
        {
            'address.street_name': 'Test Street 123',
            'address.postal_code': '1000 AA',
            'price.rent_price': 1500,
            'number_of_bedrooms': 2,
            'floor_area': 75,
            'energy_label': 'B',
            'image_url': 'https://example.com/image.jpg',
            'funda_url': 'https://funda.nl/listing/test'
        }
    ]
    
    test_email = "dioncobelens@me.com"
    profile_name = "Debug Test Profile"
    
    print(f"Sending test email to: {test_email}")
    print(f"Profile name: {profile_name}")
    print(f"Number of listings: {len(sample_listings)}")
    
    try:
        success = sender.send_new_listings_email(
            to_email=test_email,
            profile_name=profile_name,
            new_listings=sample_listings
        )
        
        if success:
            print("✅ Email sent successfully!")
            print("\n💡 Check your email inbox and spam folder for the test email.")
            print("If you don't see it, there might be:")
            print("- Email delivery delays")
            print("- Spam filtering")
            print("- Incorrect email address")
            print("- Gmail app password issues")
        else:
            print("❌ Email sending failed!")
            
    except Exception as e:
        print(f"❌ Error during email sending: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return success

def test_gmail_auth():
    """Test Gmail authentication specifically"""
    print("\n🔐 Testing Gmail authentication...")
    
    import smtplib
    
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER')
    smtp_pass = os.environ.get('SMTP_PASS')
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            print("✅ Gmail authentication successful!")
            return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Gmail authentication failed: {e}")
        print("💡 This might mean:")
        print("- App password is incorrect")
        print("- 2FA is not enabled on Gmail account")
        print("- App password needs to be regenerated")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Email Debugging Tool")
    print("=" * 50)
    
    # Test Gmail authentication first
    auth_ok = test_gmail_auth()
    
    if auth_ok:
        # Test full email sending process
        debug_email_sending()
    else:
        print("\n❌ Cannot proceed with email testing due to authentication issues.")
        print("\n🔧 To fix Gmail authentication:")
        print("1. Go to Gmail Settings > See all settings > Accounts and Import")
        print("2. Click 'Other Google Account settings'")
        print("3. Go to Security > 2-Step Verification (enable if not enabled)")
        print("4. Go to Security > App passwords")
        print("5. Generate a new app password for 'Mail'")
        print("6. Update SMTP_PASS in your .env file with the new app password")
