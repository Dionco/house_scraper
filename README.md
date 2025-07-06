# House Scraper Web App

A comprehensive web application for scraping and managing Dutch property listings from Funda.nl with automated notifications and profile management.

## 🚀 Features

- **Automated Scraping**: Periodic background scraping with configurable intervals
- **Profile Management**: Save and manage multiple search profiles
- **Email Notifications**: Automatic alerts for new listings matching your criteria
- **Real-time Interface**: Modern web interface with live updates
- **Data Persistence**: JSON-based storage with deduplication
- **Anti-bot Protection**: Advanced scraping techniques to avoid detection

## 📁 Project Structure

```
House_scraper/
├── backend/              # FastAPI backend server
│   ├── api.py           # Main FastAPI application
│   ├── periodic_scraper.py  # Background scraping scheduler
│   ├── scrape_api.py    # Scraping API endpoints
│   ├── listings.html    # Frontend interface
│   ├── utils/           # Maintenance utilities
│   ├── debug/           # Debug files and outputs
│   ├── docs/            # Backend documentation
│   └── deprecated/      # Legacy code
├── frontend/            # React frontend (alternative interface)
├── docs/                # Project documentation
├── database.json        # Main database file
├── search_profiles.json # Saved search profiles
└── PERIODIC_SCRAPING.md # Periodic scraping documentation
```

## 🔧 Getting Started

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd House_scraper
   ```

2. **Install backend dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your email SMTP settings
   ```

4. **Start the application**:
   ```bash
   uvicorn api:app --reload --port 8000
   ```

5. **Access the interface**:
   - Main Interface: http://localhost:8000/listings.html
   - API Documentation: http://localhost:8000/docs

## 📧 Email Configuration

Configure email notifications by setting up SMTP credentials in your `.env` file:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=your-email@gmail.com
```

## 🎯 Quick Start Guide

1. **Open the Interface**: Navigate to `http://localhost:8000/listings.html`
2. **Set Search Criteria**: Use the filter form to specify your preferences
3. **Save as Profile**: Click "Save New Profile" to create a persistent search
4. **Configure Notifications**: Add email addresses and set scraping intervals
5. **Start Monitoring**: The system will automatically scrape and notify you of new listings

## 📖 Documentation

- **[Periodic Scraping Guide](PERIODIC_SCRAPING.md)**: Detailed guide on automated scraping
- **[Backend Documentation](backend/README.md)**: Technical backend documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Production deployment instructions
- **[Anti-bot Strategy](docs/anitbot.md)**: Advanced scraping techniques

## 🔄 Maintenance

### Database Operations
```bash
# Deduplicate database
python backend/utils/deduplicate_database.py

# Migrate database format
python backend/utils/migrate_database.py
```

### Scraper Management
```bash
# Check scraper status
curl http://localhost:8000/api/scraper/status

# Manually trigger scrape
curl -X POST http://localhost:8000/api/profiles/{profile_id}/scrape
```

## 📊 API Endpoints

### Core Operations
- `GET /api/profiles` - List all saved profiles
- `POST /api/profiles` - Create new profile
- `GET /api/listings` - Get all listings
- `GET /api/scraper/status` - Check scraper status

### Scraping Control
- `POST /api/scraper/start` - Start periodic scraper
- `POST /api/scraper/stop` - Stop periodic scraper
- `POST /api/profiles/{id}/scrape` - Trigger manual scrape

See the [API documentation](http://localhost:8000/docs) for complete endpoint reference.

## 🛠️ Development

### Project Organization
- **Core files**: Main application logic in `backend/`
- **Utilities**: Maintenance scripts in `backend/utils/`
- **Debug files**: Debug outputs in `backend/debug/`
- **Documentation**: Project docs in `docs/`
- **Legacy code**: Deprecated files in `backend/deprecated/`

### Running Tests
```bash
# Run API tests
pytest backend/tests/

# Manual scraping test
python backend/utils/debug_listings.js
```

## 📝 Legal Notice

This application is designed for personal use and educational purposes. Please respect Funda's robots.txt and terms of service when scraping their website.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
# Force redeploy for timezone changes
