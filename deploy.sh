#!/bin/bash

echo "🚀 House Scraper - Quick Deploy Script"
echo "======================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    git branch -M main
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Ready for deployment - House Scraper Web App"

echo ""
echo "✅ Your project is ready for deployment!"
echo ""
echo "🌐 Choose a deployment platform:"
echo ""
echo "1. Railway (Recommended - Easy):"
echo "   npm install -g @railway/cli"
echo "   railway login"
echo "   railway init"
echo "   railway up"
echo ""
echo "2. Render (Python-friendly):"
echo "   - Push to GitHub"
echo "   - Connect at https://render.com"
echo "   - Use the provided render.yaml"
echo ""
echo "3. Fly.io (Docker-based):"
echo "   curl -L https://fly.io/install.sh | sh"
echo "   fly auth login"
echo "   fly launch"
echo ""
echo "4. PythonAnywhere (Python-specific):"
echo "   - Upload code to https://pythonanywhere.com"
echo "   - Configure WSGI file"
echo ""
echo "📚 See DEPLOYMENT.md for detailed instructions"
echo ""
echo "🎉 Your House Scraper web app is ready to go live!"
