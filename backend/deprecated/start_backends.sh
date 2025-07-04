#!/bin/zsh
# Start all backend servers for House_scraper

# Start FastAPI backend (in backend directory)
echo "Starting FastAPI backend..."
# cd "$(dirname "$0")/backend" || exit 1
uvicorn backend.api:app --reload &
FASTAPI_PID=$!
cd ..

echo "All backend servers started. (FastAPI PID: $FASTAPI_PID)"
echo "To stop all, run: kill $FASTAPI_PID"
