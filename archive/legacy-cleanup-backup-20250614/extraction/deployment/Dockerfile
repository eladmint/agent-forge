# Dockerfile for Steel Browser Enhanced Extraction Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Node.js for Steel Browser MCP
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libatspi2.0-0 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxss1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for Steel Browser MCP server
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Copy requirements files (enterprise structure)
# This assumes the build context is the project root
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install additional Steel Browser dependencies
RUN pip install --no-cache-dir \
    playwright==1.40.0 \
    websockets==12.0 \
    aiofiles==23.2.1

# Copy enterprise project structure
COPY src/ ./src/
COPY utils/ ./utils/ 2>/dev/null || echo "No utils directory"
COPY mcp_tools/ ./mcp_tools/ 2>/dev/null || echo "No mcp_tools directory"

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps chromium

# Build Steel Browser MCP server if available
WORKDIR /app
RUN if [ -d "mcp_tools" ]; then \
        cd mcp_tools && \
        npm install && \
        npm run build; \
    fi
WORKDIR /app

# Set Python path for enterprise structure
ENV PYTHONPATH="/app:/app/src:${PYTHONPATH}"

# Set Steel Browser environment variables
ENV STEEL_BROWSER_ENABLED=true
ENV MCP_BROWSER_ENABLED=true
ENV PLAYWRIGHT_BROWSERS_PATH=/app/.playwright
ENV NODE_ENV=production

# Create a non-root user
RUN useradd -m extractor
RUN chown -R extractor:extractor /app
USER extractor

# Expose the port
EXPOSE 8080

# Health check for Steel Browser enhanced service
HEALTHCHECK CMD curl --fail http://localhost:8080/health_enhanced || curl --fail http://localhost:8080/health

# Set environment variables for FastAPI
ENV UVICORN_HOST=0.0.0.0
ENV UVICORN_PORT=8080

# Run the Steel Browser enhanced extraction service (enterprise structure)
CMD ["python", "-m", "uvicorn", "src.api.enhanced_multi_region_service:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"] 