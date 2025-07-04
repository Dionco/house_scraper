import json
import os
import time
from datetime import datetime
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

PROFILES_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "search_profiles.json")
LISTINGS_FILE = os.path.join(os.path.dirname(__file__), "funda_simple_listings.json")
API_URL = "http://localhost:8000/scrape_listings"


def run_scrape():
    # Load search profiles
    if not os.path.exists(PROFILES_FILE):
        print("No search_profiles.json found.")
        return
    with open(PROFILES_FILE, "r", encoding="utf-8") as f:
        profiles = json.load(f)
    if not profiles:
        print("No search profiles saved.")
        return
    # Load existing listings
    if os.path.exists(LISTINGS_FILE):
        with open(LISTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                all_listings_data = json.load(f)
                if isinstance(all_listings_data, dict) and "listings" in all_listings_data:
                    listings = all_listings_data["listings"]
                elif isinstance(all_listings_data, list):
                    listings = all_listings_data
                else:
                    listings = []
            except Exception:
                listings = []
    else:
        listings = []
    existing_urls = {l.get("funda_url") for l in listings if l.get("funda_url")}
    newly_found_listings = []
    # Scrape for each profile
    for profile in profiles:
        print(f"Scraping with profile: {profile}")
        try:
            response = requests.get(API_URL, params=profile, timeout=60)
            response.raise_for_status()
            data = response.json()
            new_listings = []
            for l in data.get("listings", []):
                print(f"Processing listing: {l.get('funda_url', 'No URL')}")
                if l.get("funda_url") and l["funda_url"] not in existing_urls:
                    l["is_new"] = True
                    new_listings.append(l)
                    listings.append(l)
                    existing_urls.add(l["funda_url"])
            if new_listings:
                print(f"Found {len(new_listings)} new listings for profile {profile}")
                newly_found_listings.extend(new_listings)
            else:
                print(f"No new listings for profile {profile}")
        except Exception as e:
            print(f"Error scraping for profile {profile}: {e}")
    # Save updated listings
    if newly_found_listings:
        with open(LISTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(listings)} total listings (including {len(newly_found_listings)} new)")
    else:
        print("No new listings found.")
    return newly_found_listings

def send_notification_email(new_listings):
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    email_address = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASSWORD')
    recipient_email = os.environ.get('RECIPIENT_EMAIL')
    if not (email_address and email_password and recipient_email):
        print("[WARN] Email credentials not set in .env. Skipping email notification.")
        return
    if not new_listings:
        print("[INFO] No new listings to notify.")
        return
    subject = f"Funda Scraper: {len(new_listings)} New Listing(s) Found!"
    body = ""
    for l in new_listings:
        body += f"<b>{l.get('address', l.get('address.street_name', ''))}</b><br>"
        body += f"Price: €{l.get('price', l.get('price.rent_price', ''))}<br>"
        body += f"<a href='{l.get('funda_url', l.get('object_detail_page_relative_url', '#'))}'>View Listing</a><br><br>"
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    try:
        with smtplib.SMTP('smtp.mail.me.com', 587) as server:
            server.starttls()
            server.login(email_address, email_password)
            server.sendmail(email_address, recipient_email, msg.as_string())
        print(f"[INFO] Notification email sent to {recipient_email}")
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")

if __name__ == "__main__":
    new = run_scrape()
    send_notification_email(new)
