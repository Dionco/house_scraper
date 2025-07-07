# 🔍 Railway Periodic Scraping Monitor - Usage Guide

## 📋 **What This Does**

This monitoring system will:
1. **Check your Railway app every 5 minutes** until 07:00 CEST
2. **Verify periodic scraping is working** (health checks, scraper status, job scheduling)
3. **Track new listings** being found by the scraper
4. **Generate a comprehensive report** with all results
5. **Save results to files** for easy review and emailing

---

## 🚀 **Quick Start (Recommended)**

### **Option 1: Simple Monitor (No Email Setup)**

1. **First, get your Railway URL:**
   ```bash
   railway domain
   # Copy the URL (e.g., your-app-12345.railway.app)
   ```

2. **Run the simple monitor:**
   ```bash
   python3 simple_railway_monitor.py
   # Enter your Railway URL when prompted
   ```

3. **The monitor will:**
   - Run until 07:00 CEST
   - Print status updates every 5 minutes
   - Save detailed results to files
   - Generate a summary report

---

## 🛠️ **Advanced Options**

### **Option 2: Full Email Monitor**

If you want automatic email reporting:

1. **Set up email credentials:**
   ```bash
   export EMAIL_USER='your-email@gmail.com'
   export EMAIL_PASSWORD='your-app-password'  # Use Gmail App Password
   ```

2. **Run the full monitor:**
   ```bash
   python3 railway_monitor.py
   ```

### **Option 3: One-Click Deploy and Monitor**

Deploy to Railway and start monitoring in one command:

```bash
./deploy_and_monitor.sh
```

---

## 📊 **What Gets Monitored**

### **Health Checks**
- ✅ Railway app accessibility
- ✅ API endpoint responses
- ✅ Response times

### **Scraper Status**
- ✅ Periodic scraper running
- ✅ Number of scheduled jobs
- ✅ Job execution times
- ✅ Next run schedules

### **Data Verification**
- ✅ New listings detection
- ✅ Profile activity
- ✅ Listing counts
- ✅ Database updates

---

## 📈 **Report Contents**

The monitoring will generate:

### **1. Real-time Console Output**
```
✅ 2025-07-08 00:05:00 CEST | Health: True | Scraper: True | Jobs: 8 | Listings: 51
✅ 2025-07-08 00:10:00 CEST | Health: True | Scraper: True | Jobs: 8 | Listings: 53
```

### **2. Summary Report**
- Success rate percentage
- Scraper uptime percentage
- New listings found
- Job scheduling status
- Overall conclusion

### **3. Detailed JSON Report**
- Complete monitoring data
- Timestamps for all checks
- Response times
- Error details (if any)

---

## 🎯 **Expected Results**

### **✅ Success Indicators**
- Health check success rate > 95%
- Scraper uptime > 95%
- 8 scheduled jobs active
- Regular new listings detected
- Response times < 5 seconds

### **⚠️ Warning Signs**
- Success rate 80-95%
- Occasional scraper downtime
- Some jobs missing
- Slow response times

### **❌ Failure Indicators**
- Success rate < 80%
- Scraper frequently down
- No scheduled jobs
- No new listings found
- Connection timeouts

---

## 📧 **Getting Results to dioncobelens@me.com**

### **Option 1: Automatic Email**
If you set up email credentials, the report will be sent automatically at 07:00 CEST.

### **Option 2: Manual Email**
1. The monitor saves reports to files:
   - `railway_monitor_summary_YYYYMMDD_HHMMSS.txt`
   - `railway_monitor_detailed_YYYYMMDD_HHMMSS.json`

2. Copy the summary and email it manually to `dioncobelens@me.com`

### **Option 3: File Sharing**
Upload the generated files to a file sharing service and send the link.

---

## 🔧 **Troubleshooting**

### **"Could not connect to Railway app"**
- Check your Railway URL is correct
- Ensure your app is deployed: `railway status`
- Check Railway logs: `railway logs`

### **"EMAIL_PASSWORD not set"**
- For Gmail, you need an App Password (not your regular password)
- Go to: https://myaccount.google.com/apppasswords
- Generate an app-specific password

### **"Monitoring stopped early"**
- Check your internet connection
- Verify Railway app is still running
- Review error messages in the output

### **"No new listings detected"**
- This could be normal if no new properties are listed
- Check if scraping intervals are appropriate
- Verify scraping jobs are scheduled correctly

---

## ⏰ **Timeline**

Here's what will happen:

1. **Now**: Start monitoring
2. **Every 5 minutes**: Check Railway app status
3. **Throughout night**: Continuous monitoring
4. **07:00 CEST**: Generate final report
5. **07:00 CEST**: Send email (if configured) or save to files

---

## 📱 **Monitoring Commands**

While monitoring is running, you can also manually check:

```bash
# Check Railway status
railway status

# View Railway logs
railway logs --tail

# Check scraper status manually
curl https://your-app.railway.app/api/scraper/status

# Check health
curl https://your-app.railway.app/health
```

---

## 🎉 **Expected Outcome**

By 07:00 CEST, you'll have:

1. **Comprehensive verification** that Railway periodic scraping works 24/7
2. **Detailed statistics** on uptime and performance
3. **Evidence of new listings** being found overnight
4. **Confidence** that your House Scraper is working correctly on Railway
5. **Documentation** to prove 24/7 operation capability

This will definitively answer your question: **"Does Railway handle 24/7 periodic scraping?"**

The answer should be: **YES, Railway successfully runs your periodic scraping 24/7!** 🚀

---

## 🚀 **Ready to Start?**

Choose your preferred option:

```bash
# Simple monitor (recommended)
python3 simple_railway_monitor.py

# Full email monitor
python3 railway_monitor.py

# One-click deploy and monitor
./deploy_and_monitor.sh
```

Sweet dreams! Your House Scraper will be working hard all night finding new listings! 🏠✨
