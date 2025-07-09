#!/bin/bash
# This script is designed to run on Railway startup to ensure timezone_utils is available

# Log the current directory and path
echo "Current directory: $(pwd)"
echo "PYTHONPATH: $PYTHONPATH"

# Run the timezone_utils fixer script
echo "Running fix_timezone_utils.py..."
python fix_timezone_utils.py

# Add app directories to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/app:/app/backend"
echo "Updated PYTHONPATH: $PYTHONPATH"

# Test importing timezone_utils
echo "Testing timezone_utils import..."
python -c "import timezone_utils; print(f'Success: {timezone_utils.now_cest_iso()}')" || echo "Import failed"

# Continue with normal startup - change this to your actual startup command
echo "Starting application..."
cd backend && exec python -m uvicorn api:app --host 0.0.0.0 --port $PORT
