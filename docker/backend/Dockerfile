FROM python:3.11-slim

# Define build arguments
ARG DATABASE_URL

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/shared

# Expose API port
EXPOSE 8002

# Run the application
CMD ["uvicorn", "crawl4ai_scraper.main:app", "--host", "0.0.0.0", "--port", "8002"]
