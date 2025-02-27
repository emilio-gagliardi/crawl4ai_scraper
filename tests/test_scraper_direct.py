"""
Direct test script for GenericWebScraper.
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

# Use ProactorEventLoop on Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Load environment variables
load_dotenv()

from crawl4ai_scraper.backend.services.custom_scraper import GenericWebScraper


async def test_scraper():
    """Test the GenericWebScraper directly."""
    print("Initializing scraper...")

    # Get API key from environment
    api_token = os.getenv("OPENROUTER_API_KEY")
    if not api_token:
        print("ERROR: No OPENROUTER_API_KEY found in environment variables")
        return

    # Configure the scraper
    browser_config = {
        "browser_type": "chromium",
        "headless": True,
        "viewport_height": 1080,
        "viewport_width": 1920,
    }

    crawler_config = {
        "exclude_external_links": True,
        "excluded_tags": ["nav", "footer"],
        "wait_until": "networkidle",
        "word_count_threshold": 100,
    }

    extraction_config = {
        "provider": "openrouter",
        "model": "google/gemini-2.0-flash-exp:free",
        "api_token": api_token,
        "type": "llm",
    }

    # Initialize the scraper
    scraper = GenericWebScraper(
        browser_config=browser_config,
        crawler_config=crawler_config,
        extraction_config=extraction_config,
    )

    # Test URL
    url = "https://support.microsoft.com/en-us/topic/february-25-2025-kb5052093-os-build-26100-3323-preview-053856ea-f984-4bdb-866c-5f356f5a451b"

    try:
        print(f"Scraping URL: {url}")
        result = await scraper.scrape_url(url)

        if result:
            print("Scraping successful!")
            print(f"Result: {result}")
        else:
            print("Scraping failed - no result returned")

    except Exception as e:
        print(f"Error during scraping: {str(e)}")
        import traceback

        traceback.print_exc()
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(test_scraper())
