# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    S3_BUCKET_NAME="" \
    AWS_REGION="us-east-1"

# Set working directory
WORKDIR /app

# Install system dependencies including xvfb and xauth
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

# Install Google Chrome and its dependencies
RUN playwright install chrome
RUN playwright install-deps chrome

# Copy the rest of the application
COPY . .

# Set entry point using xvfb-run to provide a virtual display
CMD ["xvfb-run", "--server-args=-screen 0 1024x768x24", "python", "main.py"]
