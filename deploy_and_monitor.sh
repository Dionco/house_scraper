#!/bin/bash
"""
One-Click Railway Deployment and Monitoring
This script deploys your app to Railway and starts monitoring.
"""

echo "🏠 Railway Deployment and Monitoring Setup"
echo "=========================================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please log in to Railway:"
    railway login
fi

# Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

# Get Railway URL
echo "📡 Getting Railway URL..."
RAILWAY_DOMAIN=$(railway domain 2>/dev/null)
if [ -z "$RAILWAY_DOMAIN" ]; then
    echo "⚠️ Could not get Railway domain automatically"
    echo "🌐 Setting up custom domain..."
    railway domain
    RAILWAY_DOMAIN=$(railway domain 2>/dev/null)
fi

if [ -n "$RAILWAY_DOMAIN" ]; then
    RAILWAY_URL="https://$RAILWAY_DOMAIN"
    echo "✅ Railway URL: $RAILWAY_URL"
    
    # Test the deployment
    echo "🔍 Testing deployment..."
    sleep 30  # Wait for deployment to be ready
    
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$RAILWAY_URL/health")
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo "✅ Deployment successful!"
        
        # Start monitoring
        echo "📊 Starting monitoring until 07:00 CEST..."
        echo "💡 Tip: You can stop monitoring anytime with Ctrl+C"
        echo ""
        
        # Update the simple monitor with the correct URL
        sed -i '' "s|https://your-app.railway.app|$RAILWAY_URL|g" simple_railway_monitor.py
        
        # Run the monitor
        python3 simple_railway_monitor.py
        
    else
        echo "❌ Deployment check failed (HTTP $HTTP_STATUS)"
        echo "🔍 Check Railway logs:"
        railway logs
    fi
else
    echo "❌ Could not determine Railway URL"
    echo "Please run manually: python3 simple_railway_monitor.py"
fi

echo ""
echo "✅ Setup complete!"
echo "📊 Your monitoring results are saved in local files"
echo "📧 Don't forget to email the results to dioncobelens@me.com"
