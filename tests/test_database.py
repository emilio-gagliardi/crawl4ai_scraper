"""
Test script for PostgreSQL database operations.

This script tests the connection to the PostgreSQL database and performs basic CRUD operations
to verify that the database models and operations are working correctly.
"""

import logging
import os
import sys
import uuid
from datetime import datetime

import dotenv
from sqlmodel import Session, SQLModel, create_engine, select

# Import models
from crawl4ai_scraper.backend.models import (
    Credentials,
    ScrapeData,
    ScrapeJob,
    ScrapeMetadata,
    ScrapeResult,
)

# from typing import Dict, List


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()


def get_database_url():
    """Get the database URL from environment variables or use a default for testing."""
    # First try to get from environment
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        # Use the password from docker-compose.yml
        # The password in docker-compose.yml is 'your_secure_password_here'
        database_url = "postgresql://crawl4ai:your_secure_password_here@localhost:5434/crawl4ai"
        logger.warning(
            "DATABASE_URL not found in environment, using default:"
            f" {database_url}"
        )

    return database_url


def create_test_engine():
    """Create a database engine for testing."""
    database_url = get_database_url()
    logger.info(f"Connecting to database: {database_url}")

    # Create engine with echo=True to see SQL statements
    return create_engine(database_url, echo=True)


def init_database(engine):
    """Initialize the database by creating all tables."""
    logger.info("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    logger.info("Database tables created successfully")


def test_credentials_crud(engine):
    """Test CRUD operations for the Credentials model."""
    logger.info("Testing Credentials CRUD operations...")

    with Session(engine) as session:
        # Create
        test_cred = Credentials(
            provider="test_provider",
            model="test_model",
            api_key="test_api_key_encrypted",
            is_active=True,
        )
        session.add(test_cred)
        session.commit()
        session.refresh(test_cred)
        logger.info(f"Created credential with ID: {test_cred.id}")

        # Read
        queried_cred = session.exec(
            select(Credentials).where(Credentials.provider == "test_provider")
        ).first()

        if queried_cred:
            logger.info(
                f"Retrieved credential: {queried_cred.provider},"
                f" {queried_cred.model}"
            )
        else:
            logger.error("Failed to retrieve credential")
            return False

        # Update
        queried_cred.api_key = "updated_api_key_encrypted"
        session.add(queried_cred)
        session.commit()
        session.refresh(queried_cred)
        logger.info(f"Updated credential API key: {queried_cred.api_key}")

        # Delete
        session.delete(queried_cred)
        session.commit()
        logger.info("Deleted credential")

        # Verify deletion
        deleted_check = session.exec(
            select(Credentials).where(Credentials.provider == "test_provider")
        ).first()

        if deleted_check is None:
            logger.info("Credential deletion verified")
            return True
        else:
            logger.error("Failed to delete credential")
            return False


def test_scrape_metadata_crud(engine):
    """Test CRUD operations for the ScrapeMetadata model."""
    logger.info("Testing ScrapeMetadata CRUD operations...")

    with Session(engine) as session:
        # Create
        test_urls = ["https://example.com/1", "https://example.com/2"]
        test_config = {
            "browser": {"browser_type": "chromium", "headless": True},
            "crawler": {
                "word_count_threshold": 100,
                "exclude_external_links": True,
            },
        }

        test_metadata = ScrapeMetadata(
            job_id=f"job_{hash(tuple(test_urls))}"[:8],
            user_id="test_user",
            urls=test_urls,
            config=test_config,
            status="pending",
            total_urls=len(test_urls),
        )

        session.add(test_metadata)
        session.commit()
        session.refresh(test_metadata)
        logger.info(f"Created scrape metadata with ID: {test_metadata.id}")

        # Read
        queried_metadata = session.exec(
            select(ScrapeMetadata).where(ScrapeMetadata.user_id == "test_user")
        ).first()

        if queried_metadata:
            logger.info(
                f"Retrieved metadata: {queried_metadata.job_id}, URLs:"
                f" {queried_metadata.urls}"
            )
        else:
            logger.error("Failed to retrieve metadata")
            return False

        # Update
        queried_metadata.status = "completed"
        queried_metadata.successful_urls = 2
        session.add(queried_metadata)
        session.commit()
        session.refresh(queried_metadata)
        logger.info(f"Updated metadata status: {queried_metadata.status}")

        # Test ScrapeData with foreign key relationship
        test_data = ScrapeData(
            scrape_id=queried_metadata.id,
            url=test_urls[0],
            content="Test content for the page",
            page_metadata={"title": "Test Page", "word_count": 150},
        )

        session.add(test_data)
        session.commit()
        session.refresh(test_data)
        logger.info(
            f"Created scrape data with ID: {test_data.id} for metadata ID:"
            f" {queried_metadata.id}"
        )

        # Read ScrapeData
        queried_data = session.exec(
            select(ScrapeData).where(
                ScrapeData.scrape_id == queried_metadata.id
            )
        ).first()

        if queried_data:
            logger.info(
                f"Retrieved scrape data: {queried_data.url}, content length:"
                f" {len(queried_data.content or '')}"
            )
        else:
            logger.error("Failed to retrieve scrape data")
            return False

        # Delete ScrapeData first (due to foreign key constraint)
        session.delete(queried_data)
        session.commit()
        logger.info("Deleted scrape data")

        # Delete ScrapeMetadata
        session.delete(queried_metadata)
        session.commit()
        logger.info("Deleted scrape metadata")

        # Verify deletion
        deleted_check = session.exec(
            select(ScrapeMetadata).where(ScrapeMetadata.user_id == "test_user")
        ).first()

        if deleted_check is None:
            logger.info("Metadata deletion verified")
            return True
        else:
            logger.error("Failed to delete metadata")
            return False


def test_scrape_job_crud(engine):
    """Test CRUD operations for the ScrapeJob model."""
    logger.info("Testing ScrapeJob CRUD operations...")

    # Use a unique URL for each test run
    test_url = f"https://example.com/test_{uuid.uuid4()}"

    with Session(engine) as session:
        # Create
        test_job = ScrapeJob(
            url=test_url, status="pending", output_path="/app/data/test_job"
        )
        session.add(test_job)
        session.commit()
        session.refresh(test_job)
        logger.info(f"Created scrape job with ID: {test_job.id}")

        # Read
        queried_job = session.exec(
            select(ScrapeJob).where(ScrapeJob.url == test_url)
        ).first()

        if queried_job:
            logger.info(
                f"Retrieved job: {queried_job.url}, status:"
                f" {queried_job.status}"
            )
        else:
            logger.error("Failed to retrieve job")
            return False

        # Update
        queried_job.status = "completed"
        queried_job.completed_at = datetime.utcnow()
        session.add(queried_job)
        session.commit()
        session.refresh(queried_job)
        logger.info(f"Updated job status: {queried_job.status}")

        # Create ScrapeResult with foreign key relationship
        test_result = ScrapeResult(
            scrape_job_id=queried_job.id,
            cleaned_html="<html><body>Test content</body></html>",
            markdown="# Test Content",
        )

        session.add(test_result)
        session.commit()
        session.refresh(test_result)
        logger.info(
            f"Created scrape result with ID: {test_result.id} for job ID:"
            f" {queried_job.id}"
        )

        # Delete ScrapeResult first (due to foreign key constraint)
        session.delete(test_result)
        session.commit()
        logger.info("Deleted scrape result")

        # Delete ScrapeJob
        session.delete(queried_job)
        session.commit()
        logger.info("Deleted scrape job")

        # Verify deletion
        deleted_check = session.exec(
            select(ScrapeJob).where(ScrapeJob.url == test_url)
        ).first()

        if deleted_check is None:
            logger.info("Job deletion verified")
            return True
        else:
            logger.error("Failed to delete job")
            return False


def main():
    """Main function to run database tests."""
    try:
        # Create engine
        engine = create_test_engine()

        # Initialize database
        init_database(engine)

        # Run tests
        credentials_result = test_credentials_crud(engine)
        metadata_result = test_scrape_metadata_crud(engine)
        job_result = test_scrape_job_crud(engine)

        # Report results
        logger.info("=== Test Results ===")
        logger.info(
            f"Credentials CRUD: {'PASSED' if credentials_result else 'FAILED'}"
        )
        logger.info(
            f"ScrapeMetadata CRUD: {'PASSED' if metadata_result else 'FAILED'}"
        )
        logger.info(f"ScrapeJob CRUD: {'PASSED' if job_result else 'FAILED'}")

        if credentials_result and metadata_result and job_result:
            logger.info("All database tests passed successfully!")
            return 0
        else:
            logger.error("Some database tests failed.")
            return 1

    except Exception as e:
        logger.exception(f"Error during database testing: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
