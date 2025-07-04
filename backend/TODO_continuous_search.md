
# 📝 To-Do List: Funda Scraper & Notifier

>This plan breaks the project into four main parts for clarity and step-by-step development.

---

## 1. Backend: Saving & Managing Search Profiles
**Goal:** Persistently save user filter specifications for the automated scraper.

### a. Create Storage File
- In your project root, create a file named `search_profiles.json`.
- Initialize it with an empty list: `[]`.

### b. Build API Endpoint to Save Profiles
- **File:** Your main backend file (e.g., `main.py`).
- **Action:** Create a new `POST` endpoint at `/profiles`.
- **Logic:**
    1. The endpoint should accept a JSON object containing the filter criteria.
    2. Read the contents of `search_profiles.json`.
    3. Append the new profile object to the list.
    4. Write the updated list back to `search_profiles.json`.

### c. Update Frontend to Use the Endpoint
- **File:** `index.html`.
- **Action:** Add a "Save Search" button to your form.
    ```html
    <button type="button" id="save-search-btn" class="w-full text-center px-6 py-2 bg-gray-600 text-white font-semibold rounded-lg hover:bg-gray-700 transition-all mt-2">
        Save This Search
    </button>
    ```
- **Script:** Add a click event listener to the new button that sends the form data to the `/profiles` endpoint using a POST request.

---

## 2. Backend: The Automated Scraper
**Goal:** Create a standalone script to periodically scrape Funda based on saved profiles and identify new listings.

### a. Create the Scraper Script
- Create a new Python file named `scraper.py`.

### b. Implement the Core Scraping Logic
- **Function:** Define a main function like `def run_scrape():`.
- **Logic:**
    1. Load Data: Read and parse both `search_profiles.json` and your main `listings.json`.
    2. Create a URL Lookup Set: For high-performance checking, create a Python set of all `funda_url` values from your existing `listings.json`.
        ```python
        # In scraper.py
        with open('listings.json', 'r', encoding='utf-8') as f:
            all_listings_data = json.load(f)
        existing_urls = {listing['funda_url'] for listing in all_listings_data['listings']}
        ```
    3. Iterate and Scrape: Loop through each profile in `search_profiles.json` and execute your scraping logic with its specific filters.
    4. Identify New Listings: For each listing returned from the scrape, check if its `funda_url` is not in the `existing_urls` set.
    5. Flag and Collect: If a listing is new, add a new key-value pair to its dictionary, such as `"is_new": true`. Append this entire new listing object to both the main list of listings and a separate `newly_found_listings` list for this run.
    6. Save Results: After the loop finishes, if any new listings were found, overwrite `listings.json` with the updated list of all listings.

### c. Schedule the Script
- **Option A (OS-level):** Use a Cron Job (macOS/Linux) or Task Scheduler (Windows) to run `python scraper.py` at a set interval (e.g., every hour). This is the most robust method.
- **Option B (Python-level):** Use a library like `schedule` (`pip install schedule`) within `scraper.py` to create a long-running process.

---

## 3. Backend: Email Notification System
**Goal:** Notify the user via email when new listings are discovered.

### a. Handle Credentials Securely
- Create a `.env` file in your project root. **Do not commit this file to Git.**
- Add your email credentials:
    ```env
    EMAIL_ADDRESS="your_email@gmail.com"
    EMAIL_PASSWORD="your_gmail_app_password" # Generate this from your Google account
    RECIPIENT_EMAIL="email_to_send_to@example.com"
    ```
- Install `python-dotenv`: `pip install python-dotenv`.

### b. Create the Email Function
- **File:** `scraper.py`.
- **Action:** Define a function `send_notification_email(new_listings)`.
- **Logic:**
    1. Use Python's built-in `smtplib` and `email` modules.
    2. Load credentials securely from the `.env` file using `os.environ.get()`.
    3. Construct an email body that loops through the `new_listings` list, formatting each property with its address, price, and a direct link.
    4. Connect to your provider's SMTP server (e.g., `smtp.gmail.com`) and send the email.

### c. Integrate with Scraper
- In your `run_scrape()` function, after the main loop, check if the `newly_found_listings` list is not empty.
- If it contains listings, call `send_notification_email(newly_found_listings)`.

---

## 4. Frontend: Displaying New Listings
**Goal:** Add a visual indicator in the UI for newly found listings and reset their "new" status after viewing.

### a. Update Card Rendering Logic
- **File:** `index.html` (in the `<script>` tag).
- **Function:** `renderListingCard(listing)`.
- **Action:** Check for the `is_new: true` flag on each listing object. If it's true, conditionally add a "New" badge to the card's HTML.
    ```js
    // Example for inside the card's image container
    ${listing.is_new ? `
        <div class="absolute top-3 left-3 bg-accent text-white px-2.5 py-1 rounded-full text-xs font-bold shadow-lg" style="background-color: #10b981;">
            ✨ NEW
        </div>` : ''}
    ```

### b. Add a Global Notification Banner
- **File:** `index.html` (in the `<script>` tag).
- **Function:** `loadInitialListings()` (or your main data fetching function).
- **Action:** After fetching the listings, check if any of them have the `is_new` flag. If so, display a dismissible banner at the top of the listings area informing the user that new properties have been added.

### c. Implement "New" Status Reset
- **File:** Your main backend file (e.g., `main.py`).
- **Endpoint:** The `GET /listings` endpoint that serves data to the frontend.
- **Action:**
    1. Read `listings.json`.
    2. Before sending the data, create a copy of the listings to be sent as the response.
    3. Iterate through the original list of listings and change every `is_new: true` to `is_new: false`.
    4. Save the modified data (with all flags reset) back to `listings.json`.
    5. Return the original, unmodified copy (which still has the true flags) to the frontend. This ensures the user sees the "New" badges for that session only.







