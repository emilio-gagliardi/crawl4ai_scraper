"""FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .backend.api.credentials import router as credentials_router
from .backend.api.crud import router as crud_router
from .backend.api.scrape import router as scrape_router
from .backend.database import create_db_and_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

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
app.include_router(scrape_router)
app.include_router(crud_router)


@app.on_event("startup")
async def on_startup():
    """Create database tables on startup."""
    create_db_and_tables()


@app.get("/")
async def root():
    """Root endpoint that returns API status."""
    return {
        "service": "Crawl4AI Scraper",
        "version": "1.0.0",
        "status": "healthy",
    }
