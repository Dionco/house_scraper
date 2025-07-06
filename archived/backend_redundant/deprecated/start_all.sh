#!/bin/zsh
# Start the Funda scraper and API server

# Activate the virtual environment
source ../.venv/bin/activate

# Start the scraper in the background with unbuffered output
nohup env PYTHONUNBUFFERED=1 ../.venv/bin/python main.py > scraper.log 2>&1 &
echo "Scraper started in background (logs: scraper.log)"

# Start the FastAPI server (api_server.py) in the foreground
python3 -m uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
