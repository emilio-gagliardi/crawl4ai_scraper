import asyncio
import json
import os
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from crawl4ai import CrawlResult

from crawl4ai_scraper.backend.services.custom_scraper import GenericWebScraper


@pytest.fixture
def mock_crawl_result():
    """Create a mock CrawlResult object."""
    result = MagicMock(spec=CrawlResult)
    result.url = "https://example.com"
    result.success = True
    result.cleaned_html = "<html><body><h1>Test Page</h1></body></html>"
    result.extracted_content = json.dumps(
        {"title": "Test Page", "content": "This is a test."}
    )
    result.error_message = ""
    return result


@pytest.fixture
def mock_failed_crawl_result():
    """Create a mock failed CrawlResult object."""
    result = MagicMock(spec=CrawlResult)
    result.url = "https://example.com/error"
    result.success = False
    result.cleaned_html = ""
    result.extracted_content = None
    result.error_message = "Failed to access URL"
    return result


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return {
        "browser_config": {
            "browser_type": "chromium",
            "headless": True,
            "viewport_width": 1280,
            "viewport_height": 720,
        },
        "crawler_config": {
            "word_count_threshold": 0,
            "exclude_external_links": True,
            "wait_until": "domcontentloaded",
        },
        "extraction_config": {
            "type": "llm",
            "provider": "openrouter",
            "api_token": os.getenv("OPENROUTER_API_KEY", "test_key"),
            "model": "google/gemini-2.0-flash-exp:free",
            "schema": {"title": "str", "content": "str"},
            "instruction": "Extract the title and content from the page.",
        },
    }


class TestGenericWebScraper:
    """Test suite for the GenericWebScraper class."""

    def test_url_validation(self):
        """Test URL validation method."""
        # Valid URLs
        assert GenericWebScraper.validate_url("https://example.com") is True
        assert (
            GenericWebScraper.validate_url(
                "http://example.com/path?query=value"
            )
            is True
        )

        # Invalid URLs
        assert GenericWebScraper.validate_url("example.com") is False
        assert GenericWebScraper.validate_url("not a url") is False
        assert GenericWebScraper.validate_url("") is False

    @pytest.mark.asyncio
    async def test_initialization(self, test_config):
        """Test that the scraper initializes correctly with the provided configuration."""
        # Arrange & Act
        with patch("crawl4ai.AsyncWebCrawler"):
            scraper = GenericWebScraper(
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )

            # Assert
            assert scraper.crawler is not None
            assert scraper.bulk_crawler is not None
            # Check that extraction strategy is configured correctly
            assert scraper.run_config.extraction_strategy is not None
            # The provider might be combined with the model in different ways
            # Just check that both are present in some form
            provider_str = str(scraper.run_config.extraction_strategy.provider)
            assert "openrouter" in provider_str
            assert "gemini" in provider_str or "flash" in provider_str

    @pytest.mark.asyncio
    async def test_default_provider_and_model(self):
        """Test that the scraper defaults to openrouter and gemini model when not specified."""
        # Arrange & Act
        with patch("crawl4ai.AsyncWebCrawler"), patch(
            "os.getenv", return_value="test_key"
        ):  # Mock the API key
            extraction_config = {
                "type": "llm",
                "api_token": "test_key",
                # Deliberately omit provider and model to test defaults
            }

            scraper = GenericWebScraper(extraction_config=extraction_config)

            # Assert
            provider_str = str(scraper.run_config.extraction_strategy.provider)
            assert "openrouter" in provider_str
            assert "gemini" in provider_str or "flash" in provider_str

    @pytest.mark.asyncio
    async def test_scrape_url_success(self, test_config, mock_crawl_result):
        """Test successful URL scraping."""
        # Arrange
        with patch("crawl4ai.AsyncWebCrawler") as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler.arun.return_value = mock_crawl_result
            mock_crawler_class.return_value = mock_crawler
            mock_crawler.__aenter__.return_value = mock_crawler

            scraper = GenericWebScraper(
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )
            scraper.crawler = mock_crawler
            scraper.get_success = MagicMock(return_value=True)
            scraper.get_extracted_content = MagicMock(
                return_value={
                    "title": "Test Page",
                    "content": "This is a test.",
                }
            )

            # Act
            result = await scraper.scrape_url("https://example.com")

            # Assert
            assert result is not None
            assert "title" in result
            assert result["title"] == "Test Page"
            mock_crawler.arun.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_url_failure(
        self, test_config, mock_failed_crawl_result
    ):
        """Test URL scraping failure."""
        # Arrange
        with patch("crawl4ai.AsyncWebCrawler") as mock_crawler_class, patch(
            "asyncio.sleep", return_value=None
        ):  # Mock sleep to speed up test
            mock_crawler = AsyncMock()
            mock_crawler.arun.return_value = mock_failed_crawl_result
            mock_crawler_class.return_value = mock_crawler
            mock_crawler.__aenter__.return_value = mock_crawler

            scraper = GenericWebScraper(
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )
            scraper.crawler = mock_crawler
            scraper.get_success = MagicMock(return_value=False)
            scraper.get_error_message = MagicMock(
                return_value="Failed to access URL"
            )

            # Act
            result = await scraper.scrape_url(
                "https://example.com/error", max_retries=0
            )  # Set max_retries to 0 to avoid retry

            # Assert
            assert result is None
            mock_crawler.arun.assert_called_once()

    @pytest.mark.asyncio
    async def test_scrape_url_retry(
        self, test_config, mock_failed_crawl_result, mock_crawl_result
    ):
        """Test URL scraping with retry logic."""
        # Arrange
        with patch("crawl4ai.AsyncWebCrawler") as mock_crawler_class, patch(
            "asyncio.sleep", return_value=None
        ):  # Mock sleep to speed up test

            mock_crawler = AsyncMock()
            # First call fails, second call succeeds
            mock_crawler.arun.side_effect = [
                mock_failed_crawl_result,
                mock_crawl_result,
            ]
            mock_crawler_class.return_value = mock_crawler
            mock_crawler.__aenter__.return_value = mock_crawler

            scraper = GenericWebScraper(
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )
            scraper.crawler = mock_crawler

            # First call returns failure, second call returns success
            scraper.get_success = MagicMock(side_effect=[False, True])
            scraper.get_error_message = MagicMock(
                return_value="Temporary error"
            )
            scraper.get_extracted_content = MagicMock(
                return_value={
                    "title": "Test Page",
                    "content": "This is a test.",
                }
            )

            # Act
            result = await scraper.scrape_url(
                "https://example.com", max_retries=2
            )

            # Assert
            assert result is not None
            assert mock_crawler.arun.call_count == 2

    @pytest.mark.asyncio
    async def test_bulk_scrape(self, test_config, mock_crawl_result):
        """Test bulk scraping functionality."""
        # Arrange
        with patch("crawl4ai.AsyncWebCrawler") as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler.arun_many.return_value = [
                mock_crawl_result,
                mock_crawl_result,
            ]
            mock_crawler_class.return_value = mock_crawler
            mock_crawler.__aenter__.return_value = mock_crawler

            scraper = GenericWebScraper(
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )
            scraper.bulk_crawler = mock_crawler

            # Act
            results = await scraper.bulk_scrape(
                ["https://example.com", "https://example.com/page2"]
            )

            # Assert
            assert len(results) == 2
            mock_crawler.arun_many.assert_called_once()

            # Check progress tracking
            progress = scraper.get_progress()
            assert progress["total_urls"] == 2
            assert progress["processed_urls"] == 2
            assert progress["successful_urls"] == 2

    @pytest.mark.asyncio
    async def test_bulk_scrape_with_invalid_urls(
        self, test_config, mock_crawl_result
    ):
        """Test bulk scraping with some invalid URLs."""
        # Arrange
        with patch(
            "crawl4ai.AsyncWebCrawler"
        ) as mock_crawler_class, patch.object(
            GenericWebScraper,
            "validate_url",
            side_effect=lambda url: url.startswith("https://"),
        ):
            mock_crawler = AsyncMock()
            mock_crawler.arun_many.return_value = [mock_crawl_result]
            mock_crawler_class.return_value = mock_crawler
            mock_crawler.__aenter__.return_value = mock_crawler

            scraper = GenericWebScraper(
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )
            scraper.bulk_crawler = mock_crawler

            # Act - one valid URL, one invalid
            results = await scraper.bulk_scrape(
                ["https://example.com", "invalid-url"]
            )

            # Assert - only valid URL should be processed
            assert len(results) == 1
            assert mock_crawler.arun_many.call_count == 1
            # Check that only valid URLs were passed to arun_many
            args, _ = mock_crawler.arun_many.call_args
            assert len(args[0]) == 1
            assert "https://example.com" in args[0]

    def test_get_progress(self, test_config):
        """Test the progress tracking functionality."""
        # Arrange
        with patch("crawl4ai.AsyncWebCrawler"):
            scraper = GenericWebScraper(
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )

            # Set some progress data
            scraper.progress = {
                "total_urls": 10,
                "processed_urls": 5,
                "successful_urls": 4,
                "failed_urls": 1,
                "start_time": datetime.now(),
                "end_time": None,
            }

            # Act
            progress = scraper.get_progress()

            # Assert
            assert progress["total_urls"] == 10
            assert progress["processed_urls"] == 5
            assert progress["successful_urls"] == 4
            assert progress["failed_urls"] == 1
            assert "elapsed_seconds" in progress
            assert progress["percent_complete"] == 50.0  # 5/10 * 100


if __name__ == "__main__":
    # Run the tests
    pytest.main(["-xvs", __file__])
