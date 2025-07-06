#!/usr/bin/env python3
"""
Test script to verify email configuration for Railway deployment
"""
import os
from email_utils import EmailSender

def test_email_setup():
    """Test email configuration and connectivity"""
    print("=== Email Configuration Test ===")
    
    # Create email sender
    sender = EmailSender()
    
    # Show current configuration
    print(f"SMTP Host: {sender.smtp_host}")
    print(f"SMTP Port: {sender.smtp_port}")
    print(f"SMTP User: {sender.smtp_user}")
    print(f"SMTP Pass: {'*' * len(sender.smtp_pass) if sender.smtp_pass else 'NOT SET'}")
    print(f"From Email: {sender.from_email}")
    print(f"Use TLS: {sender.use_tls}")
    
    print("\n=== Testing SMTP Connection ===")
    if sender.test_smtp_connection():
        print("✓ Email configuration is working")
        
        # Test sending a simple email
        test_email = "dioncobelens@me.com"  # From the logs
        print(f"\n=== Testing Email Send to {test_email} ===")
        
        sample_listings = [
            {
                'address': 'Test Address 123',
                'area_code': '2300',
                'city': 'Leiden',
                'price': 3500,
                'area': '85',
                'bedrooms': '2',
                'energy_label': 'B',
                'funda_url': 'https://www.funda.nl/test',
                'image_url': 'https://example.com/test.jpg'
            }
        ]
        
        if sender.send_new_listings_email(test_email, "Test Profile", sample_listings):
            print("✓ Test email sent successfully")
        else:
            print("✗ Test email failed")
    else:
        print("✗ Email configuration has issues")
        print("\nTo fix this, set these environment variables in Railway:")
        print("- SMTP_HOST (e.g., smtp.gmail.com)")
        print("- SMTP_PORT (e.g., 587)")
        print("- SMTP_USER (your email address)")
        print("- SMTP_PASS (your email password/app password)")
        print("- FROM_EMAIL (sender email address)")

if __name__ == "__main__":
    test_email_setup()
