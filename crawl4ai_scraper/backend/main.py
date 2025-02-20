from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from crawl4ai_scraper.backend.custom_scraper import MicrosoftKbScraper
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="KB Article Scraper API",
    description="API for scraping Microsoft Knowledge Base articles.",
    version="0.1.0",
)

class ScrapeRequest(BaseModel):
    """
    Request model for the /scrape endpoint.

    Attributes:
        url (str): The URL of the Microsoft KB article to scrape.
    """
    url: str

@app.post("/scrape")
async def scrape(request: ScrapeRequest) -> dict:
    """
    Scrapes a Microsoft Knowledge Base article.

    Args:
        request (ScrapeRequest): The request containing the URL to scrape.

    Returns:
        dict: The extracted content from the KB article.

    Raises:
        HTTPException: If the OPENROUTER_API_KEY is not set, if no content
            is extracted, or if any other error occurs during scraping.
    """
    try:
        # Initialize the scraper (consider moving OPENROUTER_API_KEY to config)
        openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        if not openrouter_api_key:
            raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not set")

        scraper = MicrosoftKbScraper(extraction_method="llm")
        await scraper.scrape_kb_article(request.url)

        extracted_content = scraper.get_extracted_content()

        if extracted_content:
            return extracted_content
        else:
            raise HTTPException(status_code=404, detail="No content extracted")

    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
