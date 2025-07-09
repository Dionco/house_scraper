#!/usr/bin/env python3
"""
Test the improved email template with images
"""

import sys
import os
sys.path.append('/Users/Dion/Downloads/Documenten/Code projects/House_scraper/backend')

from email_utils import EmailSender

def test_improved_template():
    print("🎨 Testing improved email template with images...")
    
    sender = EmailSender()
    
    # Test with realistic data including images
    sample_listings = [
        {
            'address.street_name': 'Prinsengracht 123',
            'address.postal_code': '1015 CJ',
            'price.rent_price': 2800,
            'number_of_bedrooms': 3,
            'floor_area': 85,
            'energy_label': 'A',
            'image_url': 'https://cloud.funda.nl/valentina_media/187/440/628_1440x960.jpg',
            'funda_url': 'https://funda.nl/listing/123'
        },
        {
            'address.street_name': 'Jordaan Loft 45',
            'address.postal_code': '1016 HH',
            'price.rent_price': 3200,
            'number_of_bedrooms': 2,
            'floor_area': 95,
            'energy_label': 'B',
            'image_url': 'https://cloud.funda.nl/valentina_media/213/162/437.jpg',
            'funda_url': 'https://funda.nl/listing/456'
        },
        {
            'address.street_name': 'Canal View 78',
            'address.postal_code': '1017 AB',
            'price.rent_price': 2400,
            'number_of_bedrooms': 1,
            'floor_area': 65,
            'energy_label': 'C',
            'image_url': 'https://cloud.funda.nl/valentina_media/195/728/293.jpg',
            'funda_url': 'https://funda.nl/listing/789'
        }
    ]
    
    template = sender.load_template('mail_new_listings.html')
    
    formatted_listings = [sender.format_listing_data(listing) for listing in sample_listings]
    
    data = {
        'profile_name': 'Amsterdam Premium Rentals',
        'listing_count': len(sample_listings),
        'listings': formatted_listings
    }
    
    result = template.render(**data)
    
    print(f"✅ Template rendered successfully: {len(result)} characters")
    
    # Save preview
    output_file = '/Users/Dion/Downloads/Documenten/Code projects/House_scraper/improved_email_preview.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(result)
    
    print(f"✅ Preview saved to: {output_file}")
    
    # Send test email
    test_email = "dioncobelens@me.com"
    
    print(f"\n📧 Sending test email to: {test_email}")
    
    success = sender.send_new_listings_email(
        to_email=test_email,
        profile_name="Amsterdam Premium Rentals",
        new_listings=sample_listings
    )
    
    if success:
        print("✅ Test email sent successfully!")
        print("📧 Check your email for the improved template with images")
        print("💡 The email includes:")
        print("  - Property images")
        print("  - Improved layout with statistics")
        print("  - Better visual hierarchy")
        print("  - Enhanced call-to-action buttons")
    else:
        print("❌ Test email failed!")
    
    return success

if __name__ == "__main__":
    test_improved_template()
