from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
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
    try:
        # Get active credentials if they exist
        creds_service = CredentialsService(db)
        active_creds = creds_service.get_active_credentials()

        # If using LLM extraction, ensure we have credentials
        extraction_config = None
        if active_creds:
            api_key = creds_service.decrypt_api_key(active_creds)
            if not api_key:
                return ScrapeResponse(
                    status=ResponseStatus.ERROR,
                    message="Failed to decrypt API key",
                    code=APIStatusCode.UNAUTHORIZED,
                    data=None,
                )
            extraction_config = {
                "provider": active_creds.provider,
                "model": active_creds.model,
                "api_key": api_key,
            }

        # Initialize scraper with config
        scraper = GenericWebScraper(
            browser_config=request.config.get("browser", {}),
            crawler_config=request.config.get("crawler", {}),
            extraction_config=extraction_config,
        )

        # Scrape URLs
        results = {}
        errors = {}
        for url in request.urls:
            try:
                result = await scraper.scrape(url)
                results[url] = result
            except Exception as e:
                errors[url] = str(e)

        # Return results
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
        return ScrapeResponse(
            status=ResponseStatus.ERROR,
            message=f"Scraping failed: {str(e)}",
            code=APIStatusCode.INVALID_REQUEST,
            data=None,
        )
    finally:
        if 'scraper' in locals():
            await scraper.close()
