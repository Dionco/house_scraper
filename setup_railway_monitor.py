#!/usr/bin/env python3
"""
Quick setup script for Railway monitoring.
This script will help you configure and run the Railway monitoring.
"""

import os
import subprocess
import sys
from datetime import datetime
import pytz

def install_requirements():
    """Install required packages."""
    packages = ['requests', 'pytz']
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"✅ {package} installed successfully")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def setup_email_config():
    """Help user set up email configuration."""
    print("\n📧 Email Configuration Setup")
    print("=" * 40)
    print("To send the monitoring report, you need to configure email settings.")
    print("\nFor Gmail:")
    print("1. Enable 2-factor authentication")
    print("2. Generate an App Password (not your regular password)")
    print("3. Go to: https://myaccount.google.com/apppasswords")
    print()
    
    email = input("Enter your email address: ").strip()
    print(f"\nTo set up your email password, run these commands:")
    print(f"export EMAIL_USER='{email}'")
    print("export EMAIL_PASSWORD='your-app-password'")
    print()
    print("Then run: python railway_monitor.py")
    
    return email

def get_railway_url():
    """Get Railway app URL."""
    print("\n🚀 Railway App URL")
    print("=" * 40)
    
    # Try to get from railway CLI
    try:
        result = subprocess.run(['railway', 'status'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Railway CLI detected")
            
            # Try to get URL from railway
            domain_result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
            if domain_result.returncode == 0 and domain_result.stdout.strip():
                url = f"https://{domain_result.stdout.strip()}"
                print(f"📡 Found Railway URL: {url}")
                return url
                
    except FileNotFoundError:
        print("⚠️ Railway CLI not found")
    
    # Manual input
    url = input("Enter your Railway app URL (e.g., https://your-app.railway.app): ").strip()
    return url

def create_monitor_script(railway_url, email):
    """Create a customized monitor script."""
    script_content = f'''#!/usr/bin/env python3
"""
Customized Railway Monitor Script
Auto-generated for your specific configuration.
"""

import os
os.environ['EMAIL_USER'] = '{email}'
# Set EMAIL_PASSWORD environment variable before running

# Import and run the main monitor
from railway_monitor import RailwayScrapingMonitor
from datetime import datetime
import pytz

CEST = pytz.timezone('Europe/Amsterdam')

def main():
    print("🏠 Railway Periodic Scraping Monitor")
    print("=" * 50)
    print(f"Monitoring: {railway_url}")
    print(f"Email: {email}")
    print(f"Current time: {{datetime.now(CEST).strftime('%Y-%m-%d %H:%M:%S CEST')}}")
    print()
    
    # Check if email password is set
    if not os.getenv('EMAIL_PASSWORD'):
        print("❌ EMAIL_PASSWORD environment variable not set")
        print("Please run: export EMAIL_PASSWORD='your-app-password'")
        return
    
    # Create and run monitor
    monitor = RailwayScrapingMonitor("{railway_url}", "{email}")
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
'''
    
    with open('run_railway_monitor.py', 'w') as f:
        f.write(script_content)
    
    print(f"✅ Created customized monitor script: run_railway_monitor.py")

def test_railway_connection(url):
    """Test connection to Railway app."""
    try:
        import requests
        response = requests.get(f"{url}/health", timeout=10)
        if response.status_code == 200:
            print(f"✅ Railway app is accessible: {response.status_code}")
            return True
        else:
            print(f"⚠️ Railway app returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Could not connect to Railway app: {e}")
        return False

def main():
    """Main setup function."""
    print("🏠 Railway Periodic Scraping Monitor Setup")
    print("=" * 50)
    
    # Install requirements
    print("📦 Installing requirements...")
    install_requirements()
    
    # Get Railway URL
    railway_url = get_railway_url()
    
    # Test connection
    print(f"\n🔍 Testing connection to {railway_url}...")
    test_railway_connection(railway_url)
    
    # Setup email
    email = setup_email_config()
    
    # Create customized script
    create_monitor_script(railway_url, email)
    
    print("\n🎯 Setup Complete!")
    print("=" * 50)
    print("Next steps:")
    print("1. Set your email password:")
    print(f"   export EMAIL_PASSWORD='your-app-password'")
    print("2. Run the monitor:")
    print("   python run_railway_monitor.py")
    print()
    print("The monitor will run until 07:00 CEST and send you a report.")

if __name__ == "__main__":
    main()
