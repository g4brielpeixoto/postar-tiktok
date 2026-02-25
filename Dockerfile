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

# Patch tiktok-uploader to continuously remove joyride overlays using a MutationObserver
RUN SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])") && \
    sed -i "/self.page.goto(upload_url)/a \        self.page.add_init_script(\"\"\"const observer = new MutationObserver(() => { const overlays = document.querySelectorAll('.react-joyride__overlay, .react-joyride__spotlight, [data-test-id=\'joyride-portal\']'); overlays.forEach(el => el.remove()); }); observer.observe(document.documentElement, { childList: true, subtree: true });\"\"\")" \
    $SITE_PACKAGES/tiktok_uploader/upload.py

# Install Google Chrome and its dependencies via Playwright
RUN playwright install chrome
RUN playwright install-deps chrome

# Copy the rest of the application and the start script
COPY . .
RUN chmod +x start.sh

# Use start.sh to launch Xvfb and then the Python script
CMD ["./start.sh"]
