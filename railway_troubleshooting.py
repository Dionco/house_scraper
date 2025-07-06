#!/usr/bin/env python3
"""
Investigate Railway deployment issues and create alternative solutions
"""

import requests
import subprocess
import time
from datetime import datetime

def check_dockerfile_issues():
    """Check for potential Dockerfile issues"""
    
    print("DOCKERFILE ANALYSIS")
    print("=" * 50)
    
    issues = []
    
    # Read current Dockerfile
    with open('Dockerfile', 'r') as f:
        content = f.read()
    
    print("Current Dockerfile:")
    print("-" * 20)
    print(content)
    print("-" * 20)
    print()
    
    # Check for common issues
    if 'chromium' in content:
        print("⚠️  Chromium installation detected")
        print("   This can cause long build times on Railway")
        print("   Consider using a lighter browser or pre-built image")
        issues.append("chromium_build_time")
    
    if 'uvicorn api:app' in content:
        print("✅ Uvicorn command looks correct")
    else:
        print("❌ Uvicorn command might be incorrect")
        issues.append("uvicorn_command")
    
    if '${PORT:-8000}' in content:
        print("✅ PORT environment variable handling correct")
    else:
        print("❌ PORT environment variable not handled")
        issues.append("port_handling")
    
    if 'WORKDIR /app/backend' in content:
        print("✅ Working directory set to backend")
    else:
        print("❌ Working directory not set to backend")
        issues.append("workdir")
    
    print(f"\\nIssues found: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")
    
    return issues

def test_minimal_deployment():
    """Create a minimal Dockerfile for testing"""
    
    print("\\nCREATING MINIMAL DOCKERFILE FOR TESTING")
    print("=" * 50)
    
    minimal_dockerfile = '''FROM python:3.11-slim

WORKDIR /app

# Install minimal dependencies
RUN pip install fastapi uvicorn requests beautifulsoup4 APScheduler passlib[bcrypt] python-jose[cryptography] python-multipart

# Copy only essential files
COPY backend/ ./backend/
COPY database.json ./

# Set environment
ENV PYTHONPATH=/app
ENV DATABASE_FILE=/app/database.json

# Simple startup
WORKDIR /app/backend
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    print("Minimal Dockerfile (without chromium):")
    print("-" * 20)
    print(minimal_dockerfile)
    print("-" * 20)
    
    # Save minimal version
    with open('Dockerfile.minimal', 'w') as f:
        f.write(minimal_dockerfile)
    
    print("Saved as Dockerfile.minimal")
    print("\\nThis removes:")
    print("- Chromium (major build time reduction)")
    print("- Complex shell commands")
    print("- Unnecessary system packages")
    print("\\nTrade-off: Scraping may not work, but API will")

def create_railway_troubleshooting_plan():
    """Create comprehensive Railway troubleshooting plan"""
    
    print("\\nRAILWAY TROUBLESHOOTING PLAN")
    print("=" * 50)
    
    steps = [
        {
            "step": 1,
            "title": "Check Railway Dashboard",
            "description": "Look for build logs and errors",
            "action": "Manual - check Railway web interface"
        },
        {
            "step": 2,
            "title": "Deploy Minimal Version",
            "description": "Use Dockerfile.minimal to test basic deployment",
            "action": "Replace Dockerfile with minimal version"
        },
        {
            "step": 3,
            "title": "Test Railway CLI",
            "description": "Use railway CLI for more detailed logs",
            "action": "railway logs --tail"
        },
        {
            "step": 4,
            "title": "Check Resource Limits",
            "description": "Railway may have memory/CPU limits",
            "action": "Reduce Docker image size"
        },
        {
            "step": 5,
            "title": "Alternative: Heroku/Render",
            "description": "Deploy to alternative platform",
            "action": "Create Heroku/Render deployment"
        }
    ]
    
    for step in steps:
        print(f"STEP {step['step']}: {step['title']}")
        print(f"  Description: {step['description']}")
        print(f"  Action: {step['action']}")
        print()
    
    return steps

def immediate_action_plan():
    """Create immediate action plan"""
    
    print("IMMEDIATE ACTION PLAN")
    print("=" * 50)
    
    print("TIMELINE:")
    print("- Now: Railway deployment has been building for 10+ minutes")
    print("- +30 min: Local scraper jobs should execute")
    print("- +1 hour: Evaluate Railway vs alternatives")
    print("- +2 hours: Have working production scraper")
    print()
    
    print("PARALLEL TRACKS:")
    print()
    print("TRACK 1: Railway Debugging")
    print("1. Deploy minimal Dockerfile (remove chromium)")
    print("2. Check Railway dashboard for errors")
    print("3. Test basic API deployment")
    print()
    
    print("TRACK 2: Local Monitoring")
    print("1. Monitor local scraper execution (in 30 min)")
    print("2. Verify scraper logic works")
    print("3. Use local as backup if needed")
    print()
    
    print("TRACK 3: Alternative Deployment")
    print("1. Prepare Heroku deployment")
    print("2. Test with minimal setup")
    print("3. Switch if Railway continues to fail")
    print()
    
    print("SUCCESS CRITERIA:")
    print("✅ Local scraper executes successfully")
    print("✅ Railway deployment works OR alternative deployed")
    print("✅ Periodic scraping restored within 2 hours")

def main():
    """Main troubleshooting function"""
    
    print("RAILWAY DEPLOYMENT INVESTIGATION")
    print("=" * 60)
    print(f"Time: {datetime.now()}")
    print()
    
    issues = check_dockerfile_issues()
    test_minimal_deployment()
    create_railway_troubleshooting_plan()
    immediate_action_plan()
    
    print("\\nRECOMMENDATION:")
    if "chromium_build_time" in issues:
        print("🎯 Deploy minimal Dockerfile immediately")
        print("   This will likely fix the deployment timeout")
        print("   Scraping won't work but API will, proving deployment works")
    else:
        print("🔍 Investigate Railway dashboard for build errors")
    
    print("\\nNEXT COMMANDS:")
    print("1. cp Dockerfile.minimal Dockerfile")
    print("2. git add Dockerfile && git commit -m 'Test minimal deployment'")
    print("3. git push")
    print("4. Monitor deployment for 5 minutes")

if __name__ == "__main__":
    main()
