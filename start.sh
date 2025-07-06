#!/bin/bash
# Railway startup script for House Scraper

# Set the port from Railway's PORT environment variable, default to 8000
PORT=${PORT:-8000}

echo "Starting House Scraper on port $PORT"

# Start the FastAPI application
exec python -m uvicorn backend.api:app --host 0.0.0.0 --port $PORT
