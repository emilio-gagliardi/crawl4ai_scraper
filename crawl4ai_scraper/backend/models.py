from datetime import datetime
from typing import Dict, List, Optional

import pytz
from sqlalchemy import Column, Text, func
from sqlmodel import JSON, Field, SQLModel


class Credentials(SQLModel, table=True):
    """
    Database model for storing LLM provider credentials.

    Stores encrypted API keys and tracks which credential set is currently active.
    Only one set of credentials can be active at a time.
    """

    __tablename__ = "credentials"

    id: Optional[int] = Field(default=None, primary_key=True)
    provider: str = Field(..., description="Name of the LLM provider")
    model: str = Field(..., description="Name of the specific model")
    api_key: str = Field(..., description="Encrypted API key")
    is_active: bool = Field(
        default=True,
        description="Whether these credentials are currently active",
        sa_column_kwargs={"server_default": "true"},
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.UTC),
        description="When these credentials were created",
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(pytz.UTC),
        description="When these credentials were last updated",
        sa_column_kwargs={"server_default": func.now()},
    )


class ScrapeJob(SQLModel, table=True):
    """
    Database model for web scraping jobs.

    Represents a URL to be scraped and tracks the progress and results of the scraping operation.
    """

    __tablename__ = "scrape_jobs"

    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(..., description="URL to scrape")
    status: str = Field(
        ...,
        description=(
            "Current status of the scrape job (pending, processing, completed,"
            " failed)"
        ),
    )
    output_path: Optional[str] = Field(
        default=None, description="Path where scraping results are saved"
    )
    error_message: Optional[str] = Field(
        sa_column=Column(Text),
        description="Error message if the scraping failed",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.UTC),
        description="When this job was created",
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(pytz.UTC),
        description="When this job was last updated",
        sa_column_kwargs={"server_default": func.now()},
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="When this job was completed"
    )


class ScrapeResult(SQLModel, table=True):
    """
    Database model for storing scraping results.

    Contains the extracted and processed content from a scrape job, including
    cleaned HTML, markdown conversion, structured data extraction, and any
    generated files (PDFs, screenshots).
    """

    __tablename__ = "scrape_results"

    id: Optional[int] = Field(default=None, primary_key=True)
    scrape_job_id: int = Field(
        ...,
        foreign_key="scrape_jobs.id",
        description="ID of the associated scrape job",
    )
    cleaned_html: Optional[str] = Field(
        sa_column=Column(Text),
        description="Cleaned HTML content with unwanted elements removed",
    )
    markdown: Optional[str] = Field(
        sa_column=Column(Text),
        description="Markdown conversion of the cleaned HTML",
    )
    extracted_data: Optional[Dict] = Field(
        default=None,
        sa_type=JSON,
        description="Structured data extracted from the page",
    )
    screenshot_path: Optional[str] = Field(
        default=None, description="Path to the screenshot image"
    )
    pdf_path: Optional[str] = Field(
        default=None, description="Path to the generated PDF"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(pytz.UTC),
        description="When this result was created",
        sa_column_kwargs={"server_default": func.now()},
    )
    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(pytz.UTC),
        description="When this result was last updated",
        sa_column_kwargs={"server_default": func.now()},
    )


class ScrapeMetadata(SQLModel, table=True):
    """High-level metadata about a scrape operation"""

    __tablename__ = "scrape_metadata"

    id: Optional[int] = Field(default=None, primary_key=True)
    job_id: str = Field(index=True)
    user_id: str = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    urls: List[str] = Field(sa_type=JSON)
    config: Dict = Field(sa_type=JSON)
    status: str = Field(default="pending")
    error: Optional[str] = Field(default=None)
    total_urls: int = Field(...)
    successful_urls: int = Field(default=0)
    failed_urls: int = Field(default=0)


class ScrapeData(SQLModel, table=True):
    """Detailed results from a scrape operation"""

    __tablename__ = "scrape_data"

    id: Optional[int] = Field(default=None, primary_key=True)
    scrape_id: int = Field(foreign_key="scrape_metadata.id", index=True)
    url: str = Field(...)
    content: Optional[str] = Field(sa_column=Column(Text), default=None)
    page_metadata: Dict = Field(sa_type=JSON)
    error: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
