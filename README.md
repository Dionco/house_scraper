# House Scraper Web App

This is a simple web app for scraping and displaying housing listings.

## Structure
- **backend/**: FastAPI server (Python) serving housing listings via API
- **frontend/**: Minimal HTML/JavaScript frontend to display listings

## Getting Started

### Backend
1. Install dependencies:
   ```sh
   cd backend
   pip install -r requirements.txt
   ```
2. Run the FastAPI server:
   ```sh
   uvicorn main:app --reload
   ```

### Frontend
Open `frontend/index.html` in your browser. The page will fetch listings from the backend API.

---

Future improvements: add real scraping, user accounts, and notifications.
