# House Scraper - Deployment Guide

## 🌐 Deploy Your Web Application for FREE

Your House Scraper is already a complete web application! Here's how to deploy it online:

### Option 1: Railway (Recommended)

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Initialize and deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Your app will be live** at: `https://your-project.up.railway.app`

### Option 2: Render

1. **Push to GitHub** (if not already)
2. **Connect to Render:** https://render.com
3. **Create new Web Service** from your GitHub repo
4. **Use these settings:**
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn api:app --host 0.0.0.0 --port $PORT`

### Option 3: Fly.io

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Deploy:**
   ```bash
   fly auth login
   fly launch
   fly deploy
   ```

### Option 4: PythonAnywhere

1. **Create free account:** https://pythonanywhere.com
2. **Upload your code**
3. **Configure WSGI file** to point to your FastAPI app

## 🔧 Production Configuration

### Environment Variables
Set these in your deployment platform:

```bash
# Database
DATABASE_FILE=/app/database.json

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
FROM_EMAIL=your-email@gmail.com

# Security
JWT_SECRET_KEY=your-super-secret-key-here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Database Persistence
For production, consider:
- **JSON file**: Works for small apps (included)
- **SQLite**: Better for larger datasets
- **PostgreSQL**: Best for production (free on most platforms)

## 🚀 Quick Start

1. **Test locally first:**
   ```bash
   cd backend
   uvicorn api:app --reload
   ```
   Visit: http://localhost:8000

2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

3. **Choose deployment platform** and follow their specific guide

## 📱 Features Available

Your deployed web app will have:
- ✅ User registration and authentication
- ✅ Search profile management
- ✅ Real-time house scraping
- ✅ Email notifications
- ✅ Automatic periodic updates
- ✅ Modern responsive UI
- ✅ RESTful API

## 💰 Costs

All suggested platforms offer **generous free tiers**:
- **Railway**: $5/month credit (free)
- **Render**: 750 hours/month (free)
- **Fly.io**: 3 apps + 256MB RAM (free)
- **PythonAnywhere**: Always-on web app (free)

## 🌍 Custom Domain

Once deployed, you can add a custom domain:
1. **Buy domain** from Namecheap, Cloudflare, etc. (~$10/year)
2. **Point DNS** to your deployment platform
3. **Enable SSL** (automatic on most platforms)

Your House Scraper will be live at `https://yourdomain.com`!
