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

# Install Chrome with proper setup for containerized environment
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor > /usr/share/keyrings/google-chrome-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Create Chrome directories for non-root user
RUN mkdir -p /tmp/chrome-user-data \
    && chmod 777 /tmp/chrome-user-data

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY database.json search_profiles.json ./

# Create non-root user with proper Chrome setup
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
# Ensure Chrome can be run as non-root with all necessary directories
RUN mkdir -p /home/appuser/.cache/undetected_chromedriver \
    && mkdir -p /home/appuser/.config/google-chrome \
    && mkdir -p /tmp/chrome_tmp \
    && chown -R appuser:appuser /home/appuser/.cache \
    && chown -R appuser:appuser /home/appuser/.config \
    && chown -R appuser:appuser /tmp/chrome-user-data \
    && chown -R appuser:appuser /tmp/chrome_tmp \
    && chmod -R 777 /tmp/chrome_tmp

# Set environment variables for Chrome
ENV CHROME_USER_DATA_DIR=/tmp/chrome-user-data
ENV CHROME_CACHE_DIR=/tmp/chrome_tmp
ENV PYTHONUNBUFFERED=1

USER appuser
# Verify Chrome installation and path
RUN google-chrome --version

# Expose port (Railway will set PORT environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Run application with Railway port handling
CMD python -m uvicorn backend.api:app --host 0.0.0.0 --port ${PORT:-8000}
