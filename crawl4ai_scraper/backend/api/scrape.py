import asyncio
import logging
import sys

from fastapi import APIRouter, Depends
from sqlmodel import Session

from ..database import get_db
from ..schemas import (
    APIStatusCode,
    ResponseStatus,
    ScrapeRequest,
    ScrapeResponse,
)
from ..services.credentials import CredentialsService
from ..services.custom_scraper import GenericWebScraper

# Configure logging
logger = logging.getLogger(__name__)

# Use ProactorEventLoop on Windows for subprocess support
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

router = APIRouter(prefix="/api/scrape", tags=["scrape"])


@router.post(
    "/",
    response_model=ScrapeResponse,
    responses={
        200: {
            "description": "Successfully completed scraping",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Scraping completed successfully",
                        "code": 200,
                        "data": {
                            "job_id": "job_12345678",
                            "results": {
                                "https://example.com": {
                                    "content": "Extracted content...",
                                    "metadata": {
                                        "title": "Example Page",
                                        "word_count": 500,
                                    },
                                }
                            },
                            "errors": None,
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Failed to scrape: Invalid URL format",
                        "code": 400,
                        "data": None,
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "Failed to decrypt API key",
                        "code": 401,
                        "data": None,
                    }
                }
            },
        },
    },
)
async def scrape_urls(
    request: ScrapeRequest, db: Session = Depends(get_db)
) -> ScrapeResponse:
    """
    Scrape URLs using the provided configuration.
    Uses active LLM credentials if extraction strategy requires them.

    Args:
        request: Scraping configuration containing:
            - urls: List of URLs to scrape
            - config: Dictionary with browser and crawler settings
        db: Database session

    Returns:
        ScrapeResponse containing:
        - job_id: Unique identifier for this scrape operation
        - results: Dictionary of results for each URL
        - errors: Optional dictionary of errors for failed URLs
    """
    logger.info("Scrape endpoint called with URLs: %s", request.urls)

    try:
        # Get active credentials if they exist
        logger.info("Getting credentials service")
        creds_service = CredentialsService(db)
        logger.info("Fetching active credentials")
        active_creds = creds_service.get_active_credentials()
        logger.info(
            "Active credentials: %s", "Found" if active_creds else "None"
        )

        # If using LLM extraction, ensure we have credentials
        extraction_config = None
        if active_creds:
            logger.info("Decrypting API key")
            api_key = creds_service.decrypt_api_key(active_creds)
            if not api_key:
                logger.error("Failed to decrypt API key")
                return ScrapeResponse(
                    status=ResponseStatus.ERROR,
                    message="Failed to decrypt API key",
                    code=APIStatusCode.UNAUTHORIZED,
                    data=None,
                )
            logger.info("API key decrypted successfully")
            extraction_config = {
                "provider": active_creds.provider,
                "model": active_creds.model,
                "api_token": api_key,
                "type": "llm",
            }
            logger.info("Extraction config prepared")

        # Initialize scraper with config
        logger.info("Initializing web scraper")
        scraper = GenericWebScraper(
            browser_config=request.config.get("browser", {}),
            crawler_config=request.config.get("crawler", {}),
            extraction_config=extraction_config,
        )
        logger.info("Web scraper initialized successfully")

        # Scrape URLs
        results = {}
        errors = {}
        for url in request.urls:
            try:
                logger.info("Scraping URL: %s", url)
                result = await scraper.scrape_url(url)
                logger.info("Successfully scraped URL: %s", url)
                results[url] = result
            except Exception as e:
                logger.error("Error scraping URL %s: %s", url, str(e))
                errors[url] = str(e)

        # Return results
        logger.info(
            "Scraping completed with %d successful results and %d errors",
            len(results),
            len(errors),
        )
        return ScrapeResponse(
            status=ResponseStatus.SUCCESS,
            message="Scraping completed successfully",
            code=APIStatusCode.SUCCESS,
            data={
                "job_id": "job_" + str(hash(tuple(request.urls)))[:8],
                "results": results,
                "errors": errors if errors else None,
            },
        )

    except Exception as e:
        logger.exception("Unhandled exception in scrape_urls: %s", str(e))
        return ScrapeResponse(
            status=ResponseStatus.ERROR,
            message=f"Scraping failed: {str(e)}",
            code=APIStatusCode.INVALID_REQUEST,
            data=None,
        )
    finally:
        if 'scraper' in locals():
            logger.info("Closing scraper")
            await scraper.close()
            logger.info("Scraper closed successfully")
