"""
Run script for Crawl4AI Scraper.

This script provides a convenient way to start the FastAPI application
using uvicorn with the appropriate settings.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "crawl4ai_scraper.main:app",
        host="localhost",
        port=8002,
        reload=True,
    )
