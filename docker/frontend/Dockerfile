FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/shared

# Expose Streamlit port
EXPOSE 8502

# Run the Streamlit application
CMD ["streamlit", "run", "crawl4ai_scraper/frontend/app.py", "--server.port=8502", "--server.address=0.0.0.0"]
