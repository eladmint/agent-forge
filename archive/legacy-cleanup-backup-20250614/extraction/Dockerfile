FROM python:3.10-slim

# Install system dependencies for web scraping
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .
COPY ../shared ./shared

# Set environment variables
ENV PYTHONPATH=/app
ENV SERVICE_NAME=extraction
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Run the service
CMD ["python", "main.py"] 