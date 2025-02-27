"""FastAPI application entry point."""

import asyncio
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .backend.api.credentials import router as credentials_router
from .backend.api.crud import router as crud_router
from .backend.api.scrape import router as scrape_router
from .backend.database import DATABASE_URL, create_db_and_tables

# Configure Windows event loop for subprocess support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Print the actual database URL being used (with password masked)
masked_url = DATABASE_URL
if ":" in masked_url and "@" in masked_url:
    # Extract the password part and replace it with asterisks
    parts = masked_url.split("@")
    credentials = parts[0].split(":")
    if len(credentials) > 2:
        # Handle the case where there might be colons in the password
        password_part = ":".join(credentials[2:])
        masked_url = masked_url.replace(password_part, "********")
    else:
        # Simple case: username:password@host
        masked_url = masked_url.replace(credentials[1], "********")

logger.info(f"Main app using database URL: {masked_url}")

app = FastAPI(title="Crawl4AI Scraper API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(credentials_router)
app.include_router(crud_router)
app.include_router(scrape_router)


@app.on_event("startup")
async def on_startup():
    """Create database tables on startup."""
    create_db_and_tables()


@app.get("/")
def root():
    """Root endpoint that returns API status."""
    return {
        "status": "success",
        "message": "Crawl4AI Scraper API is running. Dev mode is active.",
        "code": 200,
    }
