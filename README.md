# House Scraper 🏠

Production-ready Dutch property listing scraper with automated notifications.

## 🚀 Quick Start

```bash
# Install dependencies
cd backend && pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run application
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## 📱 Access

- **Web Interface**: http://localhost:8000/listings
- **Admin Panel**: http://localhost:8000/admin  
- **API Docs**: http://localhost:8000/docs

## 🚢 Deployment

### Railway (Recommended)
```bash
railway login
railway init
railway up
```

### Docker
```bash
docker build -t house-scraper .
docker run -p 8000:8000 house-scraper
```

## 🔧 Configuration

Edit `.env` file:
```env
# Email notifications
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# API settings
API_HOST=0.0.0.0
API_PORT=8000
```

## 📖 Features

- **Automated Scraping**: Periodic funda.nl property scraping
- **Smart Notifications**: Email alerts for new matching listings  
- **Profile Management**: Multiple search profiles with custom criteria
- **Modern Interface**: Clean web UI with real-time updates
- **Production Ready**: Docker, Railway deployment, health checks

## 📊 API Endpoints

- `GET /listings` - Web interface
- `GET /api/listings` - All listings JSON
- `GET /api/scrape` - Trigger manual scrape
- `POST /api/profiles` - Manage search profiles
- `GET /api/health` - Health check

## 🏗️ Architecture

```
backend/
├── api.py              # FastAPI application
├── scrape_funda.py     # Core scraping logic
├── periodic_scraper.py # Background scheduler
├── listings.html       # Web interface
└── requirements.txt    # Dependencies
```

## 📝 License

MIT License - see archived documentation for details.

---

**Note**: All development files (tests, debug tools, alternative configs) are archived in `archived/` directory.
