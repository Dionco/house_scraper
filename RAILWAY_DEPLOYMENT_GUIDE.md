# Railway Deployment Guide for 24/7 Periodic Scraping

## 🚀 **Railway Deployment for Continuous Scraping**

### **Overview**
Railway **will** keep your application running 24/7, enabling continuous periodic scraping. Here's what you need to know:

## ✅ **Railway Service Guarantees**

### **1. Always-On Service**
- **✅ 24/7 Operation**: Railway keeps your app running continuously
- **✅ Automatic Restarts**: If your app crashes, Railway restarts it automatically
- **✅ Deployment Restarts**: During deployments, Railway gracefully restarts your app
- **✅ System Maintenance**: Railway handles infrastructure updates transparently

### **2. Service Plans**
- **Free Plan**: 500 execution hours/month (about 16 hours/day)
- **Pro Plan**: Unlimited execution hours + better performance
- **Team Plan**: Multiple projects + collaboration features

### **3. Railway-Optimized Features**
Your app now includes Railway-specific optimizations:
- **Graceful Shutdown**: Handles Railway restarts properly
- **Heartbeat Monitoring**: Prevents sleeping and monitors health
- **Persistent Scheduling**: Automatically reschedules jobs after restarts
- **Memory Management**: Optimized for long-running processes

## 🔧 **Current Configuration**

### **Railway Environment Detection**
```python
# Automatically uses Railway-optimized scraper
if os.getenv('RAILWAY_ENVIRONMENT'):
    from railway_periodic_scraper import periodic_scraper
```

### **Configuration Files**
- **railway.toml**: Deployment configuration
- **Dockerfile**: Container configuration
- **railway_periodic_scraper.py**: Railway-optimized scraper

## 📊 **Monitoring Your Scraper**

### **1. Health Check Endpoint**
```bash
curl https://your-app.railway.app/health
```

### **2. Scraper Status**
```bash
curl https://your-app.railway.app/api/scraper/status
```

### **3. Restart Scraper**
```bash
curl -X POST https://your-app.railway.app/api/scraper/restart
```

## 🚀 **Deployment Steps**

### **1. Deploy to Railway**
```bash
# From your project directory
railway up
```

### **2. Set Environment Variables**
```bash
railway variables set RAILWAY_ENVIRONMENT=production
railway variables set DB_PATH=database.json
```

### **3. Monitor Deployment**
```bash
railway logs --tail
```

## 🔍 **Verifying 24/7 Operation**

### **1. Check Service Status**
```bash
railway status
```

### **2. Monitor Logs**
```bash
railway logs --tail
```

### **3. Test Scraper Status**
Visit: `https://your-app.railway.app/api/scraper/status`

Expected response:
```json
{
  "is_running": true,
  "railway_mode": true,
  "scheduled_jobs": 5,
  "jobs": [
    {
      "id": "scrape_profile_profile_123",
      "name": "Scrape Amsterdam (profile_123)",
      "next_run_time": "2025-07-08T04:00:00+02:00"
    }
  ]
}
```

## 📈 **Cost Considerations**

### **Free Plan Limitations**
- 500 execution hours/month
- Apps may sleep after 30 minutes of inactivity
- Shared resources

### **Pro Plan Benefits ($5/month)**
- Unlimited execution hours
- No sleeping
- Better performance
- Priority support

### **Recommendation**
For 24/7 periodic scraping, the **Pro Plan** is recommended to ensure:
- No interruptions from sleeping
- Better performance and reliability
- Unlimited execution time

## 🛠️ **Alternative Solutions**

### **1. Cron Jobs (External)**
If you prefer external scheduling:
```bash
# Add to crontab
0 */4 * * * curl -X POST https://your-app.railway.app/api/scrape_listings?city=Amsterdam
```

### **2. GitHub Actions (Free)**
```yaml
name: Periodic Scraping
on:
  schedule:
    - cron: '0 */4 * * *'  # Every 4 hours
jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger scrape
        run: curl -X POST https://your-app.railway.app/api/scrape_listings?city=Amsterdam
```

### **3. Cloud Functions**
- AWS Lambda with EventBridge
- Google Cloud Functions with Cloud Scheduler
- Azure Functions with Timer Trigger

## 🎯 **Recommended Approach**

**For your use case, Railway Pro Plan is the best solution:**

1. **✅ Simplicity**: No external dependencies
2. **✅ Reliability**: Built-in monitoring and restarts
3. **✅ Performance**: Optimized for long-running processes
4. **✅ Cost**: $5/month for unlimited execution
5. **✅ Maintenance**: Minimal setup and maintenance

## 🔄 **Deployment Commands**

```bash
# Deploy your updated app
railway up

# Check deployment status
railway status

# Monitor logs
railway logs --tail

# Check scraper status
curl https://your-app.railway.app/api/scraper/status

# Test health
curl https://your-app.railway.app/health
```

## 📝 **Summary**

Your House Scraper is now **Railway-optimized** and ready for 24/7 operation:

- ✅ **Automatic Startup**: Scraper starts automatically when app deploys
- ✅ **Graceful Shutdown**: Handles Railway restarts properly
- ✅ **Persistent Scheduling**: Jobs are rescheduled after restarts
- ✅ **Monitoring**: Built-in status endpoints for monitoring
- ✅ **Memory Management**: Optimized for long-running processes

**Next Steps:**
1. Deploy to Railway with `railway up`
2. Monitor initial deployment with `railway logs --tail`
3. Verify scraper status at `/api/scraper/status`
4. Consider upgrading to Pro Plan for guaranteed 24/7 operation

Your periodic scraping will now run continuously on Railway! 🚀
