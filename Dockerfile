# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright 
    S3_BUCKET_NAME="" 
    AWS_ACCESS_KEY_ID="" 
    AWS_SECRET_ACCESS_KEY="" 
    AWS_REGION="us-east-1"

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y 
    wget 
    gnupg 
    libglib2.0-0 
    libnss3 
    libnspr4 
    libatk1.0-0 
    libatk-bridge2.0-0 
    libcups2 
    libdbus-1-3 
    libdrm2 
    libexpat1 
    libfontconfig1 
    libgbm1 
    libgcc1 
    libgconf-2-4 
    libgdk-pixbuf2.0-0 
    libglx0 
    libgtk-3-0 
    libpango-1.0-0 
    libpangocairo-1.0-0 
    libstdc++6 
    libx11-6 
    libx11-xcb1 
    libxcb1 
    libxcomposite1 
    libxcursor1 
    libxdamage1 
    libxext6 
    libxfixes3 
    libxi6 
    libxrandr2 
    libxrender1 
    libxshmfence1 
    libxtst6 
    ca-certificates 
    fonts-liberation 
    libappindicator3-1 
    lsb-release 
    xdg-utils 
    --no-install-recommends 
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers and their dependencies
RUN playwright install chromium
RUN playwright install-deps chromium

# Copy the rest of the application
COPY . .

# Ensure cookies.txt exists or is provided via volume
# If it doesn't exist, we might want to warn the user

# Set entry point
CMD ["python", "main.py"]
