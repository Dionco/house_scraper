# email_sender.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from pathlib import Path
from jinja2 import Template
from dotenv import load_dotenv

load_dotenv()

class EmailSender:
    def __init__(self):
        # Railway-compatible SMTP settings with better defaults
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')  # Gmail as default
        self.smtp_port = int(os.environ.get('SMTP_PORT', 587))  # TLS port as default
        self.smtp_user = os.environ.get('SMTP_USER', None)
        self.smtp_pass = os.environ.get('SMTP_PASS', None)
        self.from_email = os.environ.get('FROM_EMAIL', self.smtp_user or 'noreply@housescraper.com')
        self.use_tls = os.environ.get('SMTP_USE_TLS', 'true').lower() == 'true'
        self.templates_dir = Path(__file__).parent / 'templates'
        
        # Validate SMTP configuration
        if not self.smtp_user or not self.smtp_pass:
            print("[WARNING] SMTP credentials not configured. Email notifications will fail.")
            print("Set SMTP_USER and SMTP_PASS environment variables in Railway.")
    
    def test_smtp_connection(self):
        """Test SMTP connection for debugging"""
        try:
            print(f"Testing SMTP connection to {self.smtp_host}:{self.smtp_port}")
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_pass:
                    server.login(self.smtp_user, self.smtp_pass)
                print("✓ SMTP connection successful")
                return True
        except Exception as e:
            print(f"✗ SMTP connection failed: {e}")
            return False
    
    def load_template(self, template_name):
        """Load and return a Jinja2 template"""
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return Template(f.read())
    
    def format_listing_data(self, listing):
        """Format listing data for template consumption"""
        # Try all possible area keys in order of preference
        area = (
            listing.get('floor_area') or
            listing.get('area') or
            listing.get('living_area') or
            listing.get('surface_area') or
            listing.get('floorArea') or
            listing.get('floor_area_m2') or
            listing.get('address.floor_area') or
            listing.get('address.area') or
            'N/A'
        )
        # Try all possible energy label keys
        energy_label = (
            listing.get('energy_label') or
            listing.get('energyLabel') or
            listing.get('address.energy_label') or
            listing.get('address.energyLabel') or
            'N/A'
        )
        return {
            'url': listing.get('funda_url') or listing.get('object_detail_page_relative_url', '#'),
            'address': listing.get('street_name') or listing.get('address.street_name') or listing.get('address', 'Address not available'),
            'postal_code': listing.get('postal_code') or listing.get('address.postal_code') or 'N/A',
            'price': self._format_price(listing.get('rent_price') or listing.get('price.rent_price') or listing.get('price', 'Price on request')),
            'bedrooms': listing.get('bedrooms') or listing.get('number_of_bedrooms') or 'N/A',
            'area': self._format_area(area),
            'energy_label': energy_label,
            'image_url': listing.get('image_url') or listing.get('main_image_url') or listing.get('photo_url'),
            'raw_data': listing  # Keep original data for any custom needs
        }
    
    def _format_price(self, price):
        """Format price with proper currency symbol"""
        if isinstance(price, (int, float)):
            return f"€{price:,.0f}"
        price_str = str(price)
        if price_str and not price_str.startswith('€') and price_str != 'Price on request':
            return f"€{price_str}"
        return price_str
    
    def _format_area(self, area):
        """Format area with proper unit"""
        if isinstance(area, (int, float)):
            return f"{area} m²"
        area_str = str(area)
        if area_str and area_str != 'N/A' and not area_str.endswith('m²'):
            return f"{area_str} m²"
        return area_str
    
    def send_new_listings_email(self, to_email, profile_name, new_listings, template_name='new_listings.html'):
        """Send new listings email using template. Accepts to_email as string or list."""
        if not to_email:
            return False
        # Support both string and list for to_email
        recipients = to_email
        if isinstance(to_email, list):
            recipients = [e for e in to_email if e]
            if not recipients:
                return False
            to_header = ', '.join(recipients)
        else:
            to_header = to_email
            recipients = [to_email]
        try:
            # Load template
            template = self.load_template(template_name)
            # Prepare data for template
            formatted_listings = [self.format_listing_data(listing) for listing in new_listings]
            template_data = {
                'profile_name': profile_name,
                'listings': formatted_listings,
                'listing_count': len(new_listings)
            }
            # Render HTML
            html_content = template.render(**template_data)
            # Create email
            subject = f"🏠 New Funda listings for {profile_name}"
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_header
            msg['Subject'] = subject
            msg.attach(MIMEText(html_content, 'html'))
            # Send email with proper error handling
            try:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    if self.use_tls:
                        server.starttls()
                    if self.smtp_user and self.smtp_pass:
                        server.login(self.smtp_user, self.smtp_pass)
                    server.sendmail(self.from_email, recipients, msg.as_string())
                print(f"Successfully sent email to {to_header}")
                return True
            except smtplib.SMTPException as e:
                print(f"SMTP error sending email to {to_email}: {e}")
                return False
            except Exception as e:
                print(f"Failed to send email to {to_email}: {e}")
                return False
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

# Usage function (for backward compatibility)
def send_new_listings_email(to_email, profile_name, new_listings):
    """Backward compatible function"""
    sender = EmailSender()
    return sender.send_new_listings_email(to_email, profile_name, new_listings)

# Example usage:
if __name__ == "__main__":
    # Example usage
    sender = EmailSender()
    
    # Sample data
    sample_listings = [
        {
            'street_name': 'Keizersgracht 123',
            'postal_code': '1015 CJ',
            'rent_price': 2500,
            'bedrooms': 3,
            'area': 85,
            'image_url': 'https://example.com/image.jpg',
            'funda_url': 'https://funda.nl/listing/123'
        }
    ]
    
    sender.send_new_listings_email(
        to_email='user@example.com',
        profile_name='Amsterdam City Center',
        new_listings=sample_listings
    )