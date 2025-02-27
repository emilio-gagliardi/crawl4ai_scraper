import asyncio
import json
import os
import tempfile
from typing import Any, Dict

import pytest

from crawl4ai_scraper.backend.services.custom_scraper import GenericWebScraper


@pytest.mark.integration
class TestGenericScraperIntegration:
    """Integration tests for the GenericWebScraper class.

    These tests require an internet connection and valid API keys.
    They are marked with the 'integration' marker to be skipped by default.
    """

    @pytest.fixture
    def test_config(self) -> Dict[str, Any]:
        """Create a test configuration with real settings."""
        return {
            "browser_config": {
                "browser_type": "chromium",
                "headless": True,
                "viewport_width": 1280,
                "viewport_height": 720,
            },
            "crawler_config": {
                "word_count_threshold": (
                    100
                ),  # Skip pages with less than 100 words
                "exclude_external_links": True,
                "wait_until": "domcontentloaded",
            },
            "extraction_config": {
                "type": "llm",
                "provider": "openrouter",  # Using the default provider
                "api_token": os.getenv(
                    "OPENROUTER_API_KEY"
                ),  # Using the API key from .env
                "model": (
                    "google/gemini-2.0-flash-exp:free"
                ),  # Using the specified model
                "schema": {
                    "title": "str",
                    "main_content": "str",
                    "author": "str?",  # Optional field
                    "publication_date": "str?",  # Optional field
                },
                "instruction": (
                    "Extract the title, main content, author, and publication"
                    " date from the webpage."
                ),
                "apply_chunking": True,
                "chunk_token_threshold": 2000,
            },
        }

    @pytest.mark.asyncio
    async def test_scrape_single_url(self, test_config):
        """Test scraping a single URL with real API calls."""
        # Skip if no API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set in environment")

        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize the scraper
            scraper = GenericWebScraper(
                output_dir=temp_dir,
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )

            # Test URL - using a stable website
            url = "https://en.wikipedia.org/wiki/Web_scraping"

            # Scrape the URL
            result = await scraper.scrape_url(url)

            # Verify the result
            assert result is not None
            assert "title" in result
            assert "main_content" in result
            assert (
                len(result["main_content"]) > 100
            )  # Ensure we got substantial content

            # Check progress tracking
            progress = scraper.get_progress()
            assert progress["total_urls"] == 1
            assert progress["processed_urls"] == 1
            assert progress["successful_urls"] == 1
            assert progress["failed_urls"] == 0

    @pytest.mark.asyncio
    async def test_bulk_scrape(self, test_config):
        """Test bulk scraping with real API calls."""
        # Skip if no API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set in environment")

        # Create a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize the scraper
            scraper = GenericWebScraper(
                output_dir=temp_dir,
                browser_config=test_config["browser_config"],
                crawler_config=test_config["crawler_config"],
                extraction_config=test_config["extraction_config"],
            )

            # Test URLs - using stable websites
            urls = [
                "https://en.wikipedia.org/wiki/Web_scraping",
                "https://en.wikipedia.org/wiki/Web_crawler",
            ]

            # Scrape the URLs
            results = await scraper.bulk_scrape(urls)

            # Verify the results
            assert results is not None
            assert len(results) == 2

            # Save the results
            output_path = await scraper.save_results(results)
            assert output_path == temp_dir

            # Check that files were created
            files = os.listdir(temp_dir)
            assert (
                len(files) >= 5
            )  # At least 2 HTML files, 2 JSON files, and 1 summary file

            # Check progress tracking
            progress = scraper.get_progress()
            assert progress["total_urls"] == 2
            assert progress["processed_urls"] == 2
            assert (
                progress["successful_urls"] > 0
            )  # At least some should be successful

    @pytest.mark.asyncio
    async def test_invalid_url_handling(self, test_config):
        """Test handling of invalid URLs."""
        # Skip if no API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set in environment")

        # Initialize the scraper
        scraper = GenericWebScraper(
            browser_config=test_config["browser_config"],
            crawler_config=test_config["crawler_config"],
            extraction_config=test_config["extraction_config"],
        )

        # Test with an invalid URL
        result = await scraper.scrape_url("invalid-url")

        # Verify the result
        assert result is None

        # Check progress tracking
        progress = scraper.get_progress()
        assert progress["total_urls"] == 1
        assert (
            progress["processed_urls"] == 0
        )  # Should not increment for invalid URLs
        assert progress["successful_urls"] == 0
        assert (
            progress["failed_urls"] == 0
        )  # Should not count as failed since it's invalid format

    @pytest.mark.asyncio
    async def test_nonexistent_url_handling(self, test_config):
        """Test handling of URLs that don't exist but are valid format."""
        # Skip if no API key is available
        if not os.getenv("OPENROUTER_API_KEY"):
            pytest.skip("OPENROUTER_API_KEY not set in environment")

        # Initialize the scraper
        scraper = GenericWebScraper(
            browser_config=test_config["browser_config"],
            crawler_config=test_config["crawler_config"],
            extraction_config=test_config["extraction_config"],
        )

        # Test with a URL that doesn't exist but has valid format
        result = await scraper.scrape_url(
            "https://this-domain-does-not-exist-12345.com"
        )

        # Verify the result
        assert result is None

        # Check progress tracking
        progress = scraper.get_progress()
        assert progress["total_urls"] == 1
        assert progress["processed_urls"] == 1
        assert progress["successful_urls"] == 0
        assert progress["failed_urls"] == 1
