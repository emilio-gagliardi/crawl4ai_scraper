from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Status of a response."""

    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class APIStatusCode(int, Enum):
    """Status codes for API responses."""

    SUCCESS = 200
    CREATED = 201
    INVALID_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Base API response model."""

    status: ResponseStatus
    message: str
    code: APIStatusCode
    data: Optional[T] = None


# Credentials schemas
class CredentialBase(BaseModel):
    """Base model for credential schemas."""

    name: str
    username: str
    password: str
    is_active: bool = True


class CredentialCreate(CredentialBase):
    """Schema for creating a new credential."""

    provider_name: str = Field(
        ..., description="Name of the LLM provider", example="openrouter"
    )
    model_name: str = Field(
        ...,
        description="Name of the model to use",
        example="google/gemini-2.0-pro-exp-02-05:free",
    )
    api_key: str = Field(
        ..., description="API key for the provider", example="sk-or-v1-..."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider_name": "openrouter",
                "model_name": "google/gemini-2.0-pro-exp-02-05:free",
                "api_key": "sk-or-v1-...",
            }
        }
    }


# Credential Response Models
class ProviderInfo(BaseModel):
    """Schema for provider and model information."""

    provider_name: str = Field(
        ..., description="Name of the LLM provider", example="openrouter"
    )
    model_name: str = Field(
        ...,
        description="Name of the model",
        example="google/gemini-2.0-pro-exp-02-05:free",
    )
    description: str = Field(
        ...,
        description="Human-readable description",
        example="Google Gemini Pro via OpenRouter",
    )


class CredentialData(BaseModel):
    """Schema for credential operation result data."""

    provider: str = Field(
        ..., description="Name of the LLM provider", example="openrouter"
    )
    model: str = Field(
        ...,
        description="Name of the model",
        example="google/gemini-2.0-pro-exp-02-05:free",
    )
    provider_identifier: str = Field(
        ...,
        description="Combined provider/model identifier",
        example="openrouter/google/gemini-2.0-pro-exp-02-05:free",
    )
    created_at: datetime = Field(
        ...,
        description="When these credentials were created",
        example="2025-02-25T15:46:14Z",
    )
    is_active: bool = Field(
        ..., description="Whether these credentials are active", example=True
    )


# Scraping Request Models
class BrowserConfig(BaseModel):
    """Schema for browser configuration."""

    browser_type: str = Field(
        ..., description="Type of browser to use", example="chromium"
    )
    headless: bool = Field(
        ...,
        description="Whether to run browser in headless mode",
        example=True,
    )
    viewport_width: int = Field(
        ..., description="Browser viewport width in pixels", example=1920
    )
    viewport_height: int = Field(
        ..., description="Browser viewport height in pixels", example=1080
    )


class CrawlerConfig(BaseModel):
    """Schema for crawler configuration."""

    word_count_threshold: int = Field(
        ..., description="Minimum word count for content", example=100
    )
    exclude_external_links: bool = Field(
        ..., description="Whether to exclude external links", example=True
    )
    wait_until: str = Field(
        ..., description="Page load event to wait for", example="networkidle"
    )
    css_selector: Optional[str] = Field(
        None,
        description="CSS selector for content extraction",
        example="article.main-content",
    )
    excluded_tags: List[str] = Field(
        ...,
        description="HTML tags to exclude from content",
        example=["nav", "footer", "script"],
    )
    excluded_selector: Optional[str] = Field(
        None,
        description="CSS selector for elements to exclude",
        example=".advertisement",
    )
    mean_delay: float = Field(
        ..., description="Mean delay between requests in seconds", example=2.0
    )
    max_range: float = Field(
        ..., description="Maximum random range for delay", example=1.0
    )


class ScrapeRequest(BaseModel):
    """Schema for defining a scrape request."""

    urls: List[str] = Field(
        ...,
        description="List of URLs to scrape",
        example=["https://example.com/page1"],
    )
    config: Dict[str, Any] = Field(
        ...,
        description="Scraping configuration",
        example={
            "browser": {
                "browser_type": "chromium",
                "headless": True,
                "viewport_width": 1920,
                "viewport_height": 1080,
            },
            "crawler": {
                "word_count_threshold": 100,
                "exclude_external_links": True,
                "wait_until": "networkidle",
                "excluded_tags": ["nav", "footer"],
            },
        },
    )


# Scraping Response Models
class ScrapeData(BaseModel):
    """Schema for scrape operation result data."""

    job_id: str = Field(
        ...,
        description="Unique identifier for the scrape job",
        example="job_123456",
    )
    results: Dict[str, Any] = Field(
        ...,
        description="Scraping results for each URL",
        example={
            "https://example.com/page1": {
                "content": "Extracted content...",
                "page_metadata": {"title": "Page Title", "word_count": 500},
            }
        },
    )
    errors: Optional[Dict[str, str]] = Field(
        None,
        description="Any errors encountered during scraping",
        example={
            "https://example.com/error": "Failed to access URL: 404 Not Found"
        },
    )


# CRUD schemas for scrape metadata
class ScrapeMetadataCreate(BaseModel):
    """Schema for creating a new scrape metadata record.

    Attributes:
        user_id: Identifier for the user initiating the scrape
        urls: List of URLs to be scraped
        config: Dictionary containing browser and crawler configuration
    """

    user_id: str = Field(..., description="User identifier")
    urls: List[str] = Field(..., description="URLs to scrape")
    config: Dict = Field(..., description="Scraping configuration")


class ScrapeMetadataRead(BaseModel):
    """Schema for reading scrape metadata.

    Attributes:
        id: Database identifier
        job_id: Unique identifier for the scrape job
        user_id: Identifier for the user who initiated the scrape
        created_at: Timestamp when the scrape was initiated
        urls: List of URLs that were scraped
        config: Configuration used for the scrape
        status: Current status of the scrape job
        error: Optional error message if the scrape failed
        total_urls: Total number of URLs to scrape
        successful_urls: Number of successfully scraped URLs
        failed_urls: Number of failed URL scrapes
    """

    id: int = Field(..., description="Database identifier")
    job_id: str = Field(..., description="Unique job identifier")
    user_id: str = Field(..., description="User identifier")
    created_at: datetime = Field(..., description="Scrape creation timestamp")
    urls: List[str] = Field(..., description="URLs to scrape")
    config: Dict = Field(..., description="Scraping configuration")
    status: str = Field(..., description="Current job status")
    error: Optional[str] = Field(None, description="Error message if failed")
    total_urls: int = Field(..., description="Total URLs to scrape")
    successful_urls: int = Field(..., description="Successfully scraped URLs")
    failed_urls: int = Field(..., description="Failed URL scrapes")


class ScrapeMetadataUpdate(BaseModel):
    """Schema for updating scrape metadata.

    Attributes:
        status: Updated job status
        error: Updated error message
        successful_urls: Updated count of successful scrapes
        failed_urls: Updated count of failed scrapes
    """

    status: Optional[str] = Field(None, description="Updated job status")
    error: Optional[str] = Field(None, description="Updated error message")
    successful_urls: Optional[int] = Field(
        None, description="Updated successful count"
    )
    failed_urls: Optional[int] = Field(
        None, description="Updated failed count"
    )


class ScrapeMetadataResponse(APIResponse[ScrapeMetadataRead]):
    """Response wrapper for scrape metadata operations."""

    pass


class ScrapeMetadataListResponse(APIResponse[List[ScrapeMetadataRead]]):
    """Response wrapper for listing scrape metadata."""

    pass


# CRUD schemas for scrape data
class ScrapeDataCreate(BaseModel):
    """Schema for creating a new scrape data record.

    Attributes:
        scrape_id: ID of the associated scrape metadata
        url: URL that was scraped
        content: Optional extracted content
        page_metadata: Additional metadata about the scrape
        error: Optional error message if scrape failed
    """

    scrape_id: int = Field(..., description="Associated scrape metadata ID")
    url: str = Field(..., description="Scraped URL")
    content: Optional[str] = Field(None, description="Extracted content")
    page_metadata: Dict = Field(..., description="Additional scrape metadata")
    error: Optional[str] = Field(None, description="Error message if failed")


class ScrapeDataRead(BaseModel):
    """Schema for reading scrape data.

    Attributes:
        id: Database identifier
        scrape_id: ID of the associated scrape metadata
        url: URL that was scraped
        content: Optional extracted content
        page_metadata: Additional metadata about the scrape
        error: Optional error message if scrape failed
        created_at: Timestamp when the data was created
    """

    id: int = Field(..., description="Database identifier")
    scrape_id: int = Field(..., description="Associated scrape metadata ID")
    url: str = Field(..., description="Scraped URL")
    content: Optional[str] = Field(None, description="Extracted content")
    page_metadata: Dict = Field(..., description="Additional scrape metadata")
    error: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Creation timestamp")


class ScrapeDataUpdate(BaseModel):
    """Schema for updating scrape data.

    Attributes:
        content: Updated content
        page_metadata: Updated metadata
        error: Updated error message
    """

    content: Optional[str] = Field(None, description="Updated content")
    page_metadata: Optional[Dict] = Field(None, description="Updated metadata")
    error: Optional[str] = Field(None, description="Updated error message")


class ScrapeDataResponse(APIResponse[ScrapeDataRead]):
    """Response wrapper for scrape data operations."""

    pass


class ScrapeDataListResponse(APIResponse[List[ScrapeDataRead]]):
    """Response wrapper for listing scrape data."""

    pass


# Type aliases for common response types
CredentialResponse = APIResponse[CredentialData]
ProviderListResponse = APIResponse[List[ProviderInfo]]
ScrapeResponse = APIResponse[ScrapeData]
