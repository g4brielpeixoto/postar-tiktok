# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DISPLAY=:99

# Set working directory
WORKDIR /app

# Install system dependencies including xvfb for virtual display
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    xvfb \
    xauth \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Google Chrome and its dependencies via Playwright
RUN playwright install chrome
RUN playwright install-deps chrome

# Copy the rest of the application and the start script
COPY . .
RUN chmod +x start.sh

# Use start.sh to launch Xvfb and then the Python script
CMD ["./start.sh"]
