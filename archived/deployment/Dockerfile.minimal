FROM python:3.11-slim

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
