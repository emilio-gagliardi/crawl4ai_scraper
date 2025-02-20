from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..database import get_db
from ..services.credentials import CredentialsService
from ..custom_scraper import GenericWebScraper
import asyncio

router = APIRouter(prefix="/api/scrape", tags=["scrape"])

class BrowserConfig(BaseModel):
    browser_type: str
    headless: bool
    viewport_width: int
    viewport_height: int

class CrawlerConfig(BaseModel):
    word_count_threshold: int
    exclude_external_links: bool
    wait_until: str
    css_selector: str | None
    excluded_tags: List[str]
    excluded_selector: str | None
    mean_delay: float
    max_range: float

class ScrapeRequest(BaseModel):
    urls: List[str]
    config: Dict[str, Any]

@router.post("/")
async def scrape_urls(
    request: ScrapeRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Scrape URLs using the provided configuration.
    Uses active LLM credentials if extraction strategy requires them.
    """
    try:
        # Get active credentials if they exist
        creds_service = CredentialsService(db)
        active_creds = creds_service.get_active_credentials()
        
        # If using LLM extraction, ensure we have credentials
        extraction_config = None
        if active_creds:
            extraction_config = {
                "type": "llm",
                "provider": active_creds.provider_identifier,
                "api_token": active_creds.decrypt_api_key(),
                "schema": request.config.get("extraction_schema", {}),
                "instruction": request.config.get("extraction_instruction", "Extract structured data from the content.")
            }
        
        # Initialize scraper with provided configuration
        scraper = GenericWebScraper(
            browser_config=request.config["browser_config"],
            crawler_config=request.config["crawler_config"],
            extraction_config=extraction_config
        )
        
        # Process URLs
        results = await scraper.bulk_scrape(request.urls)
        
        # Save results
        output_dir = await scraper.save_results(results)
        
        if not output_dir:
            raise HTTPException(
                status_code=500,
                detail="Failed to save scraping results"
            )
        
        return {
            "message": "Scraping completed successfully",
            "output_dir": output_dir,
            "processed_urls": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}"
        )
    finally:
        if 'scraper' in locals():
            await scraper.close() 