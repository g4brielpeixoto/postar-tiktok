# Use official Python image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    DISPLAY=:99

# Set working directory
WORKDIR /app

# Install system dependencies including xvfb and x11vnc
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    xvfb \
    xauth \
    x11vnc \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Patch tiktok-uploader to inject localStorage
RUN SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])") && \
    sed -i "/self.context.add_cookies(self.cookies)/a \        import json, os\n        if os.path.exists('localStorage.json'):\n            with open('localStorage.json', 'r') as f: storage_data = json.load(f)\n            self.page.goto('https://www.tiktok.com')\n            self.page.evaluate('(data) => { for (const key in data) { localStorage.setItem(key, data[key]); } }', storage_data)" \
    $SITE_PACKAGES/tiktok_uploader/upload.py

# Install Google Chrome and its dependencies via Playwright
RUN playwright install chrome
RUN playwright install-deps chrome

# Copy the rest of the application and the start script
COPY . .
RUN chmod +x start.sh

# Use start.sh to launch Xvfb and then the Python script
CMD ["./start.sh"]
