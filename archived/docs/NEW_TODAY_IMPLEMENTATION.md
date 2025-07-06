# New Today Functionality - Implementation Summary

## 🎯 What Was Implemented

### 1. **Backend Changes (API)**

#### New Helper Functions
- `calculate_new_today_count(listings)` - Calculates how many listings were added in the last 24 hours
- `update_listing_timestamps(listings)` - Ensures all listings have proper timestamps and correct `is_new` flags

#### Updated Pydantic Model  
- `ProfileResponse` now includes `new_today_count: int = 0` field

#### Updated API Endpoints
- `GET /api/profiles` - Now includes `new_today_count` for each profile
- `POST /api/profiles` - Returns `new_today_count` for newly created profiles  
- `PUT /api/profiles/{profile_id}` - Updates and returns `new_today_count`
- `PUT /api/profiles/{profile_id}/email` - Updates and returns `new_today_count`

#### Database Migration Logic
- Automatically adds `added_timestamp` to existing listings based on their `scraped_at` dates
- Updates `is_new` flags based on 24-hour rule (86400 seconds)
- Saves database when timestamps are added to ensure persistence

### 2. **Periodic Scraper Updates**

The `periodic_scraper.py` already had the correct logic to:
- Add `added_timestamp` to new listings when they are scraped
- Set `is_new = True` for new listings
- Update `is_new` flags for existing listings based on the 24-hour rule

### 3. **Frontend Changes (listings.html)**

#### UI Updates
- Added "new today" count display in the active profile info section
- Shows a clock icon with the count of listings added today
- Color coding: green when count > 0, gray when count = 0

#### JavaScript Updates  
- `updateProfileViewState()` function now updates the new today count display
- Clears the count when no profile is selected
- Fetches updated profile data including `new_today_count` from API

## 🧪 Testing

Created `test_new_today.py` to verify:
- ✅ Timestamp calculation works correctly
- ✅ New today count calculation is accurate  
- ✅ Legacy listings get timestamps added automatically
- ✅ 24-hour rule for "new" classification works

## 🚀 How It Works

1. **When listings are scraped**: New listings get `added_timestamp` and `is_new = True`
2. **When API is called**: Existing listings without timestamps get them added based on `scraped_at`
3. **24-hour rule**: Listings are only considered "new" if `added_timestamp` is less than 24 hours ago
4. **Frontend display**: Shows real-time count of listings added in the last 24 hours

## 📊 Example Output

```json
{
  "id": "profile_123",
  "name": "Utrecht Search", 
  "listings_count": 15,
  "new_today_count": 3,
  "last_new_listings_count": 5,
  // ... other fields
}
```

The `new_today_count` shows listings added in the last 24 hours, while `last_new_listings_count` shows how many were found in the most recent scrape.
