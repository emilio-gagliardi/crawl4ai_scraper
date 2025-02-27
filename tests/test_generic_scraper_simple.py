"""
Simple test to verify the GenericWebScraper functionality.
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crawl4ai_scraper.backend.services.custom_scraper import GenericWebScraper


@pytest.fixture
def mock_crawler():
    with patch("crawl4ai.AsyncWebCrawler") as mock_crawler_class:
        mock_crawler = AsyncMock()
        mock_crawler_class.return_value = mock_crawler
        mock_crawler.__aenter__.return_value = mock_crawler
        yield mock_crawler


@pytest.fixture
def mock_browser_config():
    with patch("crawl4ai.BrowserConfig") as mock_config:
        yield mock_config


@pytest.fixture
def mock_crawler_config():
    with patch("crawl4ai.CrawlerRunConfig") as mock_config:
        yield mock_config


@pytest.fixture
def mock_llm_strategy():
    with patch("crawl4ai.LLMExtractionStrategy") as mock_strategy:
        mock_instance = MagicMock()
        mock_strategy.return_value = mock_instance
        yield mock_strategy


def test_validate_url():
    """Test URL validation."""
    assert GenericWebScraper.validate_url("https://example.com") is True
    assert GenericWebScraper.validate_url("http://example.com") is True
    assert GenericWebScraper.validate_url("example.com") is False
    assert GenericWebScraper.validate_url("not-a-url") is False


@pytest.mark.asyncio
async def test_scrape_url_success(
    mock_crawler, mock_browser_config, mock_crawler_config, mock_llm_strategy
):
    """Test successful URL scraping."""
    # Arrange
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.extracted_content = {
        "title": "Test Page",
        "content": "Test Content",
    }
    mock_crawler.arun.return_value = mock_result

    # Create a scraper with mocked dependencies
    with patch("os.makedirs"):
        scraper = GenericWebScraper(
            extraction_config={
                "type": "llm",
                "api_token": "test_key",
                "schema": {"title": "str", "content": "str"},
            }
        )
        scraper.crawler = mock_crawler
        scraper.get_success = MagicMock(return_value=True)
        scraper.get_extracted_content = MagicMock(
            return_value={"title": "Test Page", "content": "Test Content"}
        )

    # Act
    result = await scraper.scrape_url("https://example.com")

    # Assert
    assert result is not None
    assert "title" in result
    assert result["title"] == "Test Page"
    mock_crawler.arun.assert_called_once()


@pytest.mark.asyncio
async def test_bulk_scrape(
    mock_crawler, mock_browser_config, mock_crawler_config, mock_llm_strategy
):
    """Test bulk scraping."""
    # Arrange
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.extracted_content = {
        "title": "Test Page",
        "content": "Test Content",
    }
    mock_crawler.arun_many.return_value = [mock_result]

    # Create a scraper with mocked dependencies
    with patch("os.makedirs"), patch.object(
        GenericWebScraper, "validate_url", return_value=True
    ):
        scraper = GenericWebScraper(
            extraction_config={
                "type": "llm",
                "api_token": "test_key",
                "schema": {"title": "str", "content": "str"},
            }
        )
        scraper.bulk_crawler = mock_crawler

    # Act
    results = await scraper.bulk_scrape(["https://example.com"])

    # Assert
    assert len(results) == 1
    mock_crawler.arun_many.assert_called_once()


def test_get_progress():
    """Test progress tracking."""
    # Arrange
    with patch("os.makedirs"), patch("crawl4ai.AsyncWebCrawler"), patch(
        "crawl4ai.BrowserConfig"
    ), patch("crawl4ai.CrawlerRunConfig"), patch(
        "crawl4ai.LLMExtractionStrategy"
    ):
        scraper = GenericWebScraper()
        scraper.progress = {
            "total_urls": 10,
            "processed_urls": 5,
            "successful_urls": 4,
            "failed_urls": 1,
            "start_time": "2023-01-01T00:00:00",
            "end_time": None,
        }

    # Act
    progress = scraper.get_progress()

    # Assert
    assert progress["total_urls"] == 10
    assert progress["processed_urls"] == 5
    assert progress["successful_urls"] == 4
    assert progress["failed_urls"] == 1
    assert progress["completion_percentage"] == 50.0


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
