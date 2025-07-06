# Funda House Scraper - Periodic Scraping & Notifications

This enhanced version of the Funda House Scraper includes automated periodic scraping and email notifications for saved search profiles.

## 🚀 New Features

### Periodic Scraping
- **Automatic Background Scraping**: Each saved search profile is automatically scraped at configurable intervals
- **Configurable Intervals**: Set scraping frequency from 1 hour to 168 hours (7 days) per profile
- **Smart Scheduling**: Uses APScheduler for robust background task management
- **Duplicate Detection**: Automatically detects and excludes duplicate listings
- **New Listing Notifications**: Highlights new listings in the UI and sends email alerts

### Email Notifications
- **Automatic Email Alerts**: Get notified when new listings match your saved searches
- **Multi-Email Support**: Configure multiple email addresses per profile
- **Styled Email Templates**: Beautiful HTML emails with property details and images
- **Template Customization**: Easily modify email templates in the `templates/` folder

### Enhanced Profile Management
- **Extended Profile Data**: Each profile now stores scraping interval and last scraped time
- **Status Monitoring**: Real-time status of periodic scraper and individual profile jobs
- **Manual Triggers**: Force immediate scraping for any profile
- **Job Synchronization**: Automatically manages background jobs when profiles are added/removed

## 🛠️ Technical Implementation

### Backend Components

#### 1. Periodic Scraper (`periodic_scraper.py`)
- **APScheduler Integration**: Manages background jobs with configurable intervals
- **Database Integration**: Automatically syncs with profile database
- **Error Handling**: Robust error handling with logging
- **Job Management**: Add, remove, and update scraping jobs dynamically

#### 2. Enhanced API Endpoints
- `GET /api/scraper/status` - Get scraper status and active jobs
- `POST /api/scraper/start` - Start the periodic scraper
- `POST /api/scraper/stop` - Stop the periodic scraper
- `POST /api/scraper/sync` - Sync jobs with current profiles
- `POST /api/profiles/{profile_id}/scrape` - Manually trigger profile scrape
- `PUT /api/profiles/{profile_id}/interval` - Update scraping interval

#### 3. Email System (`email_utils.py`)
- **SMTP Configuration**: Supports various email providers via environment variables
- **Template Engine**: Jinja2-based email templates
- **Multi-recipient Support**: Send to multiple email addresses
- **Error Handling**: Graceful handling of email sending failures

### Frontend Enhancements

#### 1. Periodic Scraping Controls
- **Status Indicator**: Real-time scraper status (Active/Stopped)
- **Interval Configuration**: Set scraping frequency per profile
- **Manual Trigger**: "Scrape Now" button for immediate execution
- **Last Scraped Display**: Shows when profile was last scraped

#### 2. Auto-Refresh Features
- **Status Updates**: Scraper status updates every 30 seconds
- **Listing Refresh**: Automatic listing refresh every 5 minutes
- **New Listing Highlights**: Visual indicators for newly found listings

## 📧 Email Configuration

Configure email settings via environment variables:

```bash
# SMTP Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=your-email@gmail.com
```

### Supported Email Providers
- **Gmail**: Use app passwords for authentication
- **Outlook/Hotmail**: Standard SMTP configuration
- **Custom SMTP**: Any SMTP-compatible email service

## 🔧 Setup & Configuration

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the backend directory:
```bash
# Email Configuration
SMTP_HOST=your-smtp-host
SMTP_PORT=587
SMTP_USER=your-email@domain.com
SMTP_PASS=your-password
FROM_EMAIL=your-email@domain.com
```

### 3. Start the Application
```bash
uvicorn api:app --reload --port 8000
```

The periodic scraper will automatically start and sync with existing profiles.

## 📊 Monitoring & Management

### Scraper Status
- **Real-time Status**: Monitor if the periodic scraper is running
- **Active Jobs**: See all active scraping jobs and their next run times
- **Error Logging**: Comprehensive logging for troubleshooting

### Profile Management
- **Interval Control**: Set different scraping frequencies for each profile
- **Last Scraped Time**: Track when each profile was last updated
- **Manual Override**: Trigger immediate scraping regardless of schedule

## 🎯 Usage Examples

### Basic Profile Setup
1. **Create Search Profile**: Set your search criteria and save as a profile
2. **Configure Emails**: Add notification email addresses
3. **Set Interval**: Choose scraping frequency (default: 4 hours)
4. **Activate**: The scraper will automatically start monitoring

### Advanced Configuration
1. **Multiple Profiles**: Create profiles for different areas/criteria
2. **Varied Intervals**: Set different frequencies based on market activity
3. **Email Groups**: Use different email lists for different profiles
4. **Manual Triggers**: Force immediate updates when needed

## 🔍 Troubleshooting

### Common Issues

#### Scraper Not Running
- Check `/api/scraper/status` endpoint
- Restart with `POST /api/scraper/start`
- Check logs for error messages

#### Email Not Sending
- Verify SMTP configuration in environment variables
- Check email provider's security settings
- Test with a simple email client first

#### Missing New Listings
- Verify profile filters are correct
- Check scraping interval (may be too infrequent)
- Review logs for scraping errors

### Debug Endpoints
- `GET /api/scraper/status` - Check scraper status
- `GET /api/profiles` - List all profiles and their settings
- `POST /api/profiles/{id}/scrape` - Test manual scraping

## 🚀 Future Enhancements

### Planned Features
- **WebSocket Integration**: Real-time listing updates without page refresh
- **Advanced Filtering**: ML-based listing relevance scoring
- **Mobile Notifications**: Push notifications via mobile apps
- **Analytics Dashboard**: Detailed statistics and trends
- **Export Features**: CSV/PDF export of listings and reports

### Scalability Improvements
- **Database Migration**: Move from JSON to PostgreSQL/MongoDB
- **Caching Layer**: Redis for improved performance
- **Rate Limiting**: Advanced anti-bot protection
- **Distributed Scraping**: Multiple worker nodes for large-scale scraping

## 📝 API Documentation

### Periodic Scraping Endpoints

#### Get Scraper Status
```http
GET /api/scraper/status
```
Returns current status and active jobs.

#### Update Profile Interval
```http
PUT /api/profiles/{profile_id}/interval
Content-Type: application/json

{
  "interval_hours": 6
}
```

#### Manual Scrape Trigger
```http
POST /api/profiles/{profile_id}/scrape
```

### Profile Structure
```json
{
  "id": "profile_1234567890",
  "name": "Amsterdam Centrum",
  "filters": { ... },
  "emails": ["user@example.com"],
  "scrape_interval_hours": 4,
  "listings": [...],
  "created_at": 1234567890,
  "last_scraped": "2025-01-04T12:00:00Z",
  "last_new_listings_count": 3
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This application is designed for personal use and educational purposes. Please respect Funda's robots.txt and terms of service when scraping their website.
