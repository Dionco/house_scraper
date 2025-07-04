"""
Database migration script to add user authentication to existing House Scraper database.
This script will:
1. Create a 'users' section in the database
2. Create a default admin user 
3. Link existing profiles to the admin user
4. Update the database structure
"""

import os
import json
import time
from auth_utils import AuthUtils, create_user_dict, generate_user_id

# Database file path
DATABASE_FILE = os.path.join(os.path.dirname(__file__), "../database.json")

def load_db():
    """Load the current database."""
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception as e:
                print(f"Error loading database: {e}")
                return {}
    return {}

def save_db(db):
    """Save the database."""
    with open(DATABASE_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

def backup_database():
    """Create a backup of the current database."""
    if os.path.exists(DATABASE_FILE):
        backup_file = f"{DATABASE_FILE}.backup_{int(time.time())}"
        with open(DATABASE_FILE, "r", encoding="utf-8") as src:
            with open(backup_file, "w", encoding="utf-8") as dst:
                dst.write(src.read())
        print(f"Database backed up to: {backup_file}")
        return backup_file
    return None

def migrate_database():
    """Migrate the database to include user authentication."""
    print("Starting database migration...")
    
    # Create backup first
    backup_file = backup_database()
    if backup_file:
        print(f"✓ Database backup created: {backup_file}")
    
    # Load current database
    db = load_db()
    
    # Check if already migrated
    if "users" in db:
        print("Database already migrated!")
        return
    
    # Create users section
    db["users"] = {}
    
    # Create default admin user
    admin_user_id = generate_user_id()
    admin_user = create_user_dict(
        user_id=admin_user_id,
        username="admin",
        email="admin@housescraper.local",
        password="admin123"  # User should change this immediately
    )
    
    db["users"][admin_user_id] = admin_user
    
    # Create profiles section and migrate existing profiles
    existing_profiles = {}
    profile_ids = []
    
    # Move existing profiles to new structure
    for key, value in list(db.items()):
        if key.startswith("profile_") and isinstance(value, dict):
            # This is an existing profile
            profile_id = key
            profile_data = value
            
            # Update profile structure
            profile_data["id"] = profile_id
            profile_data["user_id"] = admin_user_id  # Link to admin user
            
            # Ensure required fields exist
            if "created_at" not in profile_data:
                profile_data["created_at"] = time.time()
            if "last_scraped" not in profile_data:
                profile_data["last_scraped"] = None
            if "last_new_listings_count" not in profile_data:
                profile_data["last_new_listings_count"] = 0
            if "scrape_interval_hours" not in profile_data:
                profile_data["scrape_interval_hours"] = 4
            if "listings" not in profile_data:
                profile_data["listings"] = []
            if "emails" not in profile_data:
                profile_data["emails"] = []
            
            existing_profiles[profile_id] = profile_data
            profile_ids.append(profile_id)
            
            # Remove from root level
            del db[key]
    
    # Create profiles section
    db["profiles"] = existing_profiles
    
    # Update admin user with profile IDs
    db["users"][admin_user_id]["profile_ids"] = profile_ids
    
    # Save migrated database
    save_db(db)
    
    print("✓ Database migration completed successfully!")
    print(f"✓ Created admin user: username='admin', email='admin@housescraper.local'")
    print(f"✓ Migrated {len(profile_ids)} existing profiles")
    print(f"✓ Admin user linked to {len(profile_ids)} profiles")
    print("\n⚠️  IMPORTANT: Change the admin password immediately after first login!")
    print("   Default password: admin123")
    
    return db

def create_sample_user():
    """Create a sample regular user for testing."""
    db = load_db()
    
    if "users" not in db:
        print("Database not migrated yet. Run migrate_database() first.")
        return
    
    # Create sample user
    user_id = generate_user_id()
    sample_user = create_user_dict(
        user_id=user_id,
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    
    db["users"][user_id] = sample_user
    save_db(db)
    
    print(f"✓ Created sample user: username='testuser', email='test@example.com', password='testpass123'")
    return user_id

def verify_migration():
    """Verify that the migration was successful."""
    db = load_db()
    
    print("Verifying database migration...")
    
    # Check users section
    if "users" not in db:
        print("✗ Users section not found")
        return False
    
    users = db["users"]
    print(f"✓ Found {len(users)} users")
    
    # Check profiles section
    if "profiles" not in db:
        print("✗ Profiles section not found")
        return False
    
    profiles = db["profiles"]
    print(f"✓ Found {len(profiles)} profiles")
    
    # Check profile-user links
    for profile_id, profile in profiles.items():
        if "user_id" not in profile:
            print(f"✗ Profile {profile_id} missing user_id")
            return False
        
        user_id = profile["user_id"]
        if user_id not in users:
            print(f"✗ Profile {profile_id} linked to non-existent user {user_id}")
            return False
    
    # Check user-profile links
    for user_id, user in users.items():
        profile_ids = user.get("profile_ids", [])
        for profile_id in profile_ids:
            if profile_id not in profiles:
                print(f"✗ User {user_id} linked to non-existent profile {profile_id}")
                return False
    
    print("✓ Database migration verification passed!")
    return True

if __name__ == "__main__":
    """Run migration when script is executed directly."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        verify_migration()
    elif len(sys.argv) > 1 and sys.argv[1] == "sample":
        create_sample_user()
    else:
        migrate_database()
        verify_migration()
