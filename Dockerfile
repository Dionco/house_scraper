# Production Dockerfile for House Scraper
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Chrome and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    wget \
    gnupg \
    unzip \
    xvfb \
    fonts-liberation \
    libxss1 \
    libappindicator3-1 \
    libasound2 \
    libgbm1 \
    xdg-utils \
    libnspr4 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY database.json search_profiles.json ./

# Create non-root user and give Chrome access
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# Ensure Chrome can be run as non-root
RUN mkdir -p /home/appuser/.cache/undetected_chromedriver \
    && chown -R appuser:appuser /home/appuser/.cache
USER appuser
# Verify Chrome installation and path
RUN google-chrome --version || echo "Chrome not found in PATH"

# Expose port (Railway will set PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run application with Railway port handling
CMD python -m uvicorn backend.api:app --host 0.0.0.0 --port ${PORT:-8000}
