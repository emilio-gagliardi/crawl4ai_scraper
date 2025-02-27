"""
Simple test to verify that the GenericWebScraper defaults to using OpenRouter and Gemini model.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from crawl4ai_scraper.backend.services.custom_scraper import GenericWebScraper


def test_provider_and_model_defaults():
    """Test that the scraper defaults to openrouter and gemini model."""
    # Mock the necessary components
    with patch("crawl4ai.AsyncWebCrawler"), patch(
        "crawl4ai.BrowserConfig"
    ), patch("crawl4ai.CrawlerRunConfig"), patch(
        "crawl4ai.LLMExtractionStrategy"
    ) as mock_llm_strategy, patch(
        "os.getenv", return_value="test_api_key"
    ):

        # Create a mock for the LLMExtractionStrategy
        mock_strategy_instance = MagicMock()
        mock_llm_strategy.return_value = mock_strategy_instance

        # Create extraction config with no provider or model specified
        extraction_config = {
            "type": "llm",
            "api_token": "test_api_key",
            "schema": {"title": "str", "content": "str"},
        }

        # Initialize the scraper
        GenericWebScraper(extraction_config=extraction_config)

        # Check that LLMExtractionStrategy was called with the correct defaults
        provider_arg = mock_llm_strategy.call_args[1]["provider"]
        assert "openrouter" in provider_arg
        assert (
            "google/gemini-2.0-flash-exp:free" in provider_arg
            or "gemini" in provider_arg
        )


if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
