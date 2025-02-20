import asyncio
import dataclasses
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, Optional, List
from urllib.parse import urlparse

from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from crawl4ai.async_dispatcher import RateLimiter, MemoryAdaptiveDispatcher
from crawl4ai.extraction_strategy import (
    LLMExtractionStrategy,
    JsonCssExtractionStrategy,
)
from pydantic import BaseModel, ValidationError
log_file_path = os.path.join(
    "microsoft_cve_rag",
    "application",
    "data",
    "logs",
    "scraping",
    "kb_scraper.log"
)
# Configure logging
logging.basicConfig(
    filename=log_file_path,
    filemode='w',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
))
logging.getLogger('').addHandler(console_handler)

logger = logging.getLogger(__name__)


# Define KBArticle schema at module level for reuse
class KBArticle(BaseModel):
    """
    Represents a Microsoft Knowledge Base article.

    Attributes:
        title (str): The title of the KB article.
        url (str): The URL of the KB article.
        applies_to (list[str]): A list of products or operating systems the article applies to.
        os_builds (str): The OS builds the article applies to.
        page_introduction (str): The introductory text of the article.
        highlights (list[str]): A list of highlights from the article.
        improvements (dict[str, list[str]]): A dictionary of improvements, categorized by type.
        servicing_stack_update (dict[str, str]): Information about servicing stack updates.
        known_issues_and_workaround (list[dict[str, Any]]): A list of known issues and their workarounds.
        how_to_get_update (list[dict[str, Any]]): Instructions on how to get the update.
    """
    title: str
    url: str
    applies_to: list[str]
    os_builds: str
    page_introduction: str
    highlights: list[str]
    improvements: dict[str, list[str]]
    servicing_stack_update: dict[str, str]
    known_issues_and_workaround: list[dict[str, Any]]
    how_to_get_update: list[dict[str, Any]]


class BaseScraper:
    """Base class for web scrapers.

    Configures and initializes the AsyncWebCrawler and core extraction
    strategy. This class centralizes default configurations for crawling
    and provides a unified method to process crawl results. Real-world
    suggestion: Tune the default parameters (viewport size, wait conditions,
    etc.) based on the target website's behavior, and consider applying
    preprocessing to filter out ads or non-relevant sections.
    """

    def __init__(
        self,
        browser_config: Optional[BrowserConfig] = None,
        run_config: Optional[CrawlerRunConfig] = None
    ) -> None:
        """Initializes the base scraper with crawler configuration, an optional
        extraction strategy, and configurable browser and crawler settings.

        Args:
            extraction_strategy (Optional[Any]): An object implementing an 'extract'
                method to convert raw HTML to structured data.
            browser_config (Optional[BrowserConfig]): Configuration for the browser.
            run_config (Optional[CrawlerRunConfig]): Configuration for crawling
                operations.
        """
        logger.info("Initializing BaseScraper.")
        self.crawl_result: Optional[Any] = None
        self.crawl_results: List[Any] = []
        self.output_dir: Optional[str] = None
        self.urls: List[str] = []
        if browser_config is None:
            browser_config = BrowserConfig(
                browser_type="chromium",      # Recommended: use Chromium for reliable rendering.
                headless=True,               # Enable headless mode for performance.
                viewport_width=1920,         # Standard desktop width.
                viewport_height=1080,        # Standard desktop height.
                verbose=True                 # Detailed logging enabled.
            )
            logger.info("No BrowserConfig provided, using default configuration.")
        self.browser_config = browser_config
        logger.info(f"BrowserConfig: {self.browser_config}")

        if run_config is None:
            run_config = CrawlerRunConfig(
                word_count_threshold=0,
                exclude_external_links=True,
                wait_until="networkidle",
                extraction_strategy=None,
                display_mode="DETAILED"
            )
            logger.info("No CrawlerRunConfig provided, using default configuration.")
        self.run_config = run_config
        logger.info(f"CrawlerRunConfig: {self.run_config}")

        try:
            self.crawler = AsyncWebCrawler(config=self.browser_config)
            logger.info("AsyncWebCrawler initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize crawler: {str(e)}")
            self.crawler = None

    def get_url(self) -> str:
        """Returns the URL from the crawl result."""
        return getattr(self.crawl_result, "url", "")

    def get_html(self) -> str:
        """Returns the raw HTML from the crawl result."""
        return getattr(self.crawl_result, "html", "")

    def get_success(self) -> bool:
        """Returns whether the crawl was successful."""
        return getattr(self.crawl_result, "success", False)

    def get_cleaned_html(self) -> str:
        """Returns the cleaned HTML (after preprocessing) from the crawl result."""
        return getattr(self.crawl_result, "cleaned_html", "")

    def get_media(self) -> any:
        """Returns any media captured during the crawl (e.g., images, videos)."""
        return getattr(self.crawl_result, "media", None)

    def get_links(self) -> any:
        """Returns any links found during the crawl."""
        return getattr(self.crawl_result, "links", None)

    def get_downloaded_files(self) -> any:
        """Returns any files downloaded during the crawl."""
        return getattr(self.crawl_result, "downloaded_files", None)

    def get_screenshot(self) -> any:
        """Returns a screenshot captured during the crawl, if available."""
        return getattr(self.crawl_result, "screenshot", None)

    def get_pdf(self) -> any:
        """Returns a PDF generated during the crawl, if available."""
        return getattr(self.crawl_result, "pdf", None)

    def get_markdown(self) -> str:
        """Returns the markdown representation of the page."""
        return getattr(self.crawl_result, "markdown", "")

    def get_extracted_content(self) -> Optional[Dict[str, Any]]:
        """Returns structured data extracted from the crawl result.

        Attempts to get the extracted content from the crawl result and parse it
        as JSON if it's a string. The content may be under either 'extracted_data'
        or 'extracted_content'.

        Returns:
            Optional[Dict[str, Any]]: Parsed JSON data as a dictionary, or None if
            no data is available or parsing fails.
        """
        content = getattr(self.crawl_result, "extracted_content", None)
        if not content:
            return None

        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse extracted content as JSON: {e}")
                return None

        return content  # If it's already a dictionary, return as is

    def get_metadata(self) -> any:
        """Returns metadata from the crawl result."""
        return getattr(self.crawl_result, "metadata", None)

    def get_error_message(self) -> str:
        """Returns any error message resulting from the crawl."""
        return getattr(self.crawl_result, "error_message", "")

    def get_session_id(self) -> str:
        """Returns the session ID associated with this crawl."""
        return getattr(self.crawl_result, "session_id", "")

    def get_response_headers(self) -> any:
        """Returns the response headers of the crawl."""
        return getattr(self.crawl_result, "response_headers", None)

    def get_status_code(self) -> int:
        """Returns the HTTP status code returned by the crawl."""
        return getattr(self.crawl_result, "status_code", 0)

    def get_browser_config(self) -> BrowserConfig:
        """Returns the BrowserConfig associated with the scraper."""
        return self.browser_config

    def get_run_config(self) -> CrawlerRunConfig:
        """Returns the CrawlerRunConfig associated with the scraper."""
        return self.run_config

    @staticmethod
    def get_safe_filename(filename: str) -> str:
        """Clean a string to make it safe for use as a filename.

        If the input appears to be a URL, extracts the meaningful portion after
        the last forward slash and before any query parameters.
        Otherwise, removes or replaces unsafe characters.

        Args:
            filename: String to clean (could be URL or filename)

        Returns:
            str: Safe version of string for use in filenames

        Example:
            From URL: https://support.microsoft.com/topic/kb123456-preview
            To: kb123456-preview

            From filename: "My File: Part 1"
            To: my-file-part-1
        """
        if not filename:
            return "unnamed"

        # If it looks like a URL, extract the meaningful portion
        if '://' in filename:
            try:
                # Get everything after the last slash, before any query params
                filename = filename.rstrip('/').split('/')[-1].split('?')[0]
            except Exception:
                pass  # Fall back to normal filename cleaning

        # Replace problematic characters
        filename = filename.lower()
        filename = re.sub(r'[^\w\s-]', '', filename)
        filename = re.sub(r'[-\s]+', '-', filename).strip('-')

        return filename or "unnamed"

    def save_crawl_result(
        self,
        output_dir: str,
        html: bool = True,
        markdown: bool = False,
        json_output: bool = False,
        pdf: bool = False,
        thumbnail: bool = False,
        filename_prefix: Optional[str] = None
    ) -> None:
        """
        Saves the crawl result in one or more formats (HTML, Markdown, JSON, PDF, Thumbnail).
        The output_dir folder is created if it doesn't exist.

        Args:
            output_dir (str): Path to the directory where files should be saved.
            html (bool): Save raw HTML to 'page.html' if True. Defaults to True.
            markdown (bool): Save markdown to 'page.md' if True. Defaults to False.
            json_output (bool): Save extracted JSON to 'extracted_data.json' if True. Defaults to False.
            pdf (bool): Save PDF content to 'page.pdf' if True. Defaults to False.
            thumbnail (bool): Save screenshot (PNG) to 'thumbnail.png' if True. Defaults to False.
            filename_prefix: Optional prefix to add to all generated filenames.
                   For example, "kb_article_" would result in
                   "kb_article_domain_path_timestamp.html"
        Notes:
    - Files are saved with format: {prefix}{domain}_{path}_{timestamp}.{ext}
    - Timestamp format: YYYYMMDD_HHMMSS
    - URL components are sanitized for safe filenames
        """
        if not self.crawl_result:
            logger.warning("No crawl_result found, nothing to save.")
            return

        os.makedirs(output_dir, exist_ok=True)
        base_filename = self.get_safe_filename(self.get_url())
        if filename_prefix:
            base_filename = f"{filename_prefix}{base_filename}"

        if html:
            html_path = os.path.join(output_dir, f"{base_filename}.html")
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(self.get_cleaned_html())
            logger.info(f"HTML saved to {html_path}")

        if markdown:
            md = self.get_markdown()
            if md:
                md_path = os.path.join(output_dir, f"{base_filename}.md")
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(md)
                logger.info(f"Markdown saved to {md_path}")
            else:
                logger.warning("No markdown found in crawl_result.")

        if json_output:
            data = self.get_extracted_content()
            if data:
                json_path = os.path.join(output_dir, f"{base_filename}.json")
                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                logger.info(f"JSON saved to {json_path}")
            else:
                logger.warning("No extracted data found in crawl_result.")

        if pdf:
            pdf_content = self.get_pdf()
            if pdf_content:
                pdf_path = os.path.join(output_dir, f"{base_filename}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(pdf_content)
                logger.info(f"PDF saved to {pdf_path}")
            else:
                logger.warning("No PDF found in crawl_result.")

        if thumbnail:
            screenshot = self.get_screenshot()
            if screenshot:
                thumbnail_path = os.path.join(output_dir, f"{base_filename}.png")
                with open(thumbnail_path, "wb") as f:
                    f.write(screenshot)
                logger.info(f"Thumbnail saved to {thumbnail_path}")
            else:
                logger.warning("No screenshot found in crawl_result.")

        logger.info("save_crawl_result completed.")

    async def bulk_crawl(
        self,
        urls: List[str],
        session_id: Optional[str] = None,
        max_retries: Optional[int] = 3
    ) -> List[Any]:
        """Process multiple URLs using Crawl4AI's native batch processing.

        Uses the instance's configured browser_config and run_config to process
        multiple URLs concurrently. Maintains session state if session_id is provided.

        Args:
            urls: List of URLs to process in bulk
            session_id: Optional identifier for session management. If provided,
                       must be a string containing alphanumeric characters,
                       underscores, or hyphens.
            max_retries: Maximum number of retry attempts per URL

        Returns:
            List[Any]: List of crawl results from Crawl4AI

        Raises:
            ValueError: If session_id is provided but invalid

        Notes:
            - Maintains extraction strategy from instance configuration
            - Logs failures for monitoring and retry logic
            - When using session_id, processing becomes sequential to maintain state
        """
        if not urls:
            logger.warning("No URLs provided for bulk processing")
            return []

        if not self.crawler:
            logger.error("Crawler not initialized")
            return []

        # Validate session ID if provided
        session_id = self._validate_session_id(session_id)

        try:
            async with self.crawler as crawler:
                # Create a new config with session if provided
                config = self.run_config
                if session_id:
                    logger.info(f"Using session ID: {session_id}")
                    config = dataclasses.replace(
                        self.run_config,
                        session_id=session_id
                    )

                # If using session, process sequentially
                if session_id:
                    self.crawl_results = []
                    for url in urls:
                        url_config = dataclasses.replace(
                            config,
                            url=url
                        )
                        result = await crawler.arun(config=url_config)
                        self.crawl_results.append(result)
                        self.urls.append(url)
                else:
                    # Without session, use parallel processing
                    crawl_results = await crawler.arun_many(
                        urls=urls,
                        config=config
                    )

                    # Handle both List and AsyncGenerator return types
                    if hasattr(crawl_results, '__aiter__'):
                        self.crawl_results = []
                        async for result in crawl_results:
                            self.crawl_results.append(result)
                    else:
                        self.crawl_results = crawl_results

                    self.urls.extend(urls)

                logger.info(
                    f"Bulk crawl completed with {len(self.crawl_results)} results"
                )

                # Clean up session if it was used
                if session_id:
                    try:
                        await crawler.crawler_strategy.kill_session(session_id)
                        logger.info(f"Session {session_id} cleaned up")
                    except Exception as e:
                        logger.warning(
                            f"Failed to clean up session {session_id}: {str(e)}"
                        )

                # Store last result in crawl_result for backwards compatibility
                self.crawl_result = self.crawl_results[-1] if self.crawl_results else None

                return self.crawl_results

        except Exception as e:
            logger.error(f"Bulk processing failed: {str(e)}")
            if session_id:
                try:
                    await self.crawler.crawler_strategy.kill_session(session_id)
                except Exception as cleanup_error:
                    logger.warning(
                        f"Failed to clean up session after error: {str(cleanup_error)}"
                    )
            return []

    def _validate_session_id(self, session_id: Optional[str]) -> Optional[str]:
        """Validate and sanitize the session ID.

        Args:
            session_id: The session ID to validate

        Returns:
            Optional[str]: The sanitized session ID

        Raises:
            ValueError: If session_id is provided but invalid
        """
        if session_id is None:
            return None

        if not isinstance(session_id, str):
            raise ValueError("session_id must be a string")

        # Remove any whitespace and special characters
        sanitized = "".join(
            c for c in session_id.strip()
            if c.isalnum() or c in "_-"
        )

        if not sanitized:
            raise ValueError(
                "session_id must contain valid characters (alphanumeric, underscore, or hyphen)"
            )

        return sanitized

    async def save_bulk_results(
        self,
        results: List[Any],
        output_dir: Optional[str] = None,
        formats: Optional[List[str]] = None
    ) -> Optional[str]:
        """Save bulk processing results in specified formats.

        Args:
            results: List of crawl results
            output_dir: Custom output directory path
            formats: List of formats to save (html, md, json, pdf, png)

        Returns:
            Optional[str]: Path to output directory if successful

        Notes:
            - Default formats: ['html', 'json']
            - Saves metadata with processing statistics
        """
        if not results:
            logger.warning("No results to save")
            return None

        formats = formats or ['html', 'json']
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Use output_dir from instance if not provided
        if output_dir:
            self.output_dir = output_dir

        try:
            os.makedirs(self.output_dir, exist_ok=True)

            # Process each result
            for i, result in enumerate(results, 1):
                url = getattr(result, "url", "unknown")
                clean_url = self.get_safe_filename(url)
                base_filename = f"kb_article_{clean_url}_{timestamp}"

                # Save requested formats
                if 'html' in formats and hasattr(result, "cleaned_html"):
                    self._save_text_content(
                        result.cleaned_html,
                        os.path.join(self.output_dir, f"{base_filename}.html")
                    )

                if 'json' in formats:
                    self._save_json_content(
                        result,
                        os.path.join(self.output_dir, f"{base_filename}.json")
                    )

                if 'md' in formats and hasattr(result, "markdown"):
                    self._save_text_content(
                        result.markdown,
                        os.path.join(self.output_dir, f"{base_filename}.md")
                    )

            # Create a summary file
            summary = {
                "timestamp": timestamp,
                "total_urls": len(results),
                "successful_crawls": sum(
                    1 for r in results
                    if getattr(r, "success", False)
                ),
                "urls": [
                    getattr(r, "url", "unknown")
                    for r in results
                ]
            }

            summary_file = os.path.join(
                self.output_dir,
                f"kb_articles_summary_{timestamp}.json"
            )
            self._save_json_content(summary, summary_file)

            logger.info(f"Results saved to: {self.output_dir}")
            return self.output_dir

        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            return None

    def _save_text_content(
        self,
        directory: str,
        filename: str,
        content: str
    ) -> None:
        """Save text content to file.

        Args:
            directory (str): The directory to save the file in.
            filename (str): The name of the file to save.
            content (str): The text content to save.
        """
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def _save_binary_content(
        self,
        directory: str,
        filename: str,
        content: bytes
    ) -> None:
        """Save binary content to file.

        Args:
            directory (str): The directory to save the file in.
            filename (str): The name of the file to save.
            content (bytes): The binary content to save.
        """
        path = os.path.join(directory, filename)
        with open(path, "wb") as f:
            f.write(content)

    def _save_json_content(
        self,
        directory: str,
        filename: str,
        content: Dict[str, Any]
    ) -> None:
        """Save JSON content to file.

        Args:
            directory (str): The directory to save the file in.
            filename (str): The name of the file to save.
            content (Dict[str, Any]): The JSON content to save.
        """
        path = os.path.join(directory, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, indent=2, ensure_ascii=False)

    def _parse_json_content(self, content: Any) -> Dict[str, Any]:
        """Parse JSON content, handling string inputs.

        Args:
            content (Any): The content to parse.

        Returns:
            Dict[str, Any]: The parsed JSON content.
        """
        if isinstance(content, str):
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"raw": content}
        return content if isinstance(content, dict) else {"raw": str(content)}

    async def close(self) -> None:
        """Close the crawler and clean up resources."""
        if self.crawler:
            await self.crawler.close()


class MicrosoftKbScraper(BaseScraper):
    """Scraper for Microsoft Knowledge Base articles.

    Uses crawl4ai to obtain raw HTML, then applies an exclusion-based filtering
    mechanism to remove unwanted sections (e.g., navigation and footer elements).
    Finally, it extracts structured data using one of two extraction strategies:
      - LLMExtractionStrategy: Uses an LLM with a descriptive prompt.
      - JsonCssExtractionStrategy: Uses CSS selectors provided in a JSON schema.
    The caller can choose which extraction method to use.
    """
    def __init__(
        self,
        output_dir: Optional[str] = None,
        extraction_method: str = "llm",
        json_schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initializes the KB article scraper with custom Browser and Crawler configs,
        and sets up the extraction strategy according to the specified method using
        a Pydantic-based schema.

        Args:
            output_dir (Optional[str]): Directory to save scraped content.
            extraction_method (str): Extraction method to use. Allowed values are "llm" or "json".
                - "llm" will use LLMExtractionStrategy with a custom instruction prompt.
                - "json" will use JsonCssExtractionStrategy with a defined CSS extraction schema.
            json_schema (Optional[Dict[str, Any]]): Optional JSON schema for the extraction strategy.
               If not provided, a default schema using a Pydantic model for KB articles is used.
        """
        logger.info("Initializing MicrosoftKbScraper.")
        # Create custom BrowserConfig for KB articles.
        kb_browser_config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            viewport_width=1920,
            viewport_height=1080,
            verbose=True
        )
        logger.info(f"Custom BrowserConfig for KB: {kb_browser_config}")

        # Factory-style decision for extraction strategy.
        extraction_strategy: Optional[Any] = None
        # Define a default Pydantic model for KB articles if no schema is provided.
        if not json_schema:
            class KBArticle(BaseModel):
                title: str
                url: str
                applies_to: list[str]
                os_builds: str
                page_introduction: str
                highlights: list[str]
                improvements: dict[str, list[str]]
                servicing_stack_update: dict[str, str]
                known_issues_and_workaround: list[dict[str, Any]]
                how_to_get_update: list[dict[str, Any]]
            json_schema = KBArticle.model_json_schema()

        if extraction_method.lower() == "llm":
            logger.info("Using LLM extraction strategy.")
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_api_key:
                logger.error("OpenRouter API key not found in environment variables for LLM extraction.")

            # Build the instruction prompt using the JSON schema.
            prompt = (
                "Extract a structured JSON object from the following HTML that represents a Microsoft KB report. "
                "The JSON object must conform to the following schema:\n\n"
                f"{json.dumps(json_schema, indent=4)}\n\n"
                "Ensure that each field is extracted correctly from the HTML. Return only the JSON object."
            )
            extraction_strategy = LLMExtractionStrategy(
                provider="openrouter/google/gemini-2.0-pro-exp-02-05:free",
                api_token=openrouter_api_key,
                schema=json_schema,
                extraction_type="schema",
                instruction=prompt,
                chunk_token_threshold=2000,  # Adjust based on expected HTML size.
                overlap_rate=0.07,
                apply_chunking=True,
                input_format="html",
                verbose=True
            )

        elif extraction_method.lower() == "json":
            logger.info("Using JsonCss extraction strategy.")
            extraction_strategy = JsonCssExtractionStrategy(json_schema)
        else:
            logger.error(f"Unknown extraction_method: {extraction_method}. Defaulting to LLM extraction.")
            openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
            if not openrouter_api_key:
                logger.error("OpenRouter API key not found in environment variables for LLM extraction.")

            # Build the instruction prompt using the JSON schema.
            prompt = (
                "Extract a structured JSON object from the following HTML that represents a Microsoft KB report. "
                "The JSON object must conform to the following schema:\n\n"
                f"{json.dumps(json_schema, indent=4)}\n\n"
                "Ensure that each field is extracted correctly from the HTML. Return only the JSON object."
            )
            extraction_strategy = LLMExtractionStrategy(
                provider="google/gemini-2.0-flash-exp:free",
                api_token=openrouter_api_key,
                schema=json_schema,
                extraction_type="schema",
                instruction=prompt,
                chunk_token_threshold=2000,
                overlap_rate=0.07,
                apply_chunking=True,
                input_format="html",
                verbose=True
            )
        # Create custom CrawlerRunConfig for KB articles with simple delay settings
        kb_run_config = CrawlerRunConfig(
            cache_mode=CacheMode.DISABLED,
            extraction_strategy=extraction_strategy,
            word_count_threshold=0,
            exclude_external_links=False,
            wait_until="domcontentloaded",
            css_selector=None,
            excluded_tags=["nav", "footer"],
            excluded_selector=".col-1-5, .supLeftNavMobileView, .supLeftNavMobileViewContent.grd, .teachingCalloutHidden.teachingCalloutPopover, .popoverMessageWrapper, .f-multi-column.f-multi-column-6, .c-uhfh-actions, .c-uhfh-gcontainer-st, .ocArticleFooterShareContainer, .ocArticleFooterShareLinksWrapper, .ocArticleFooterFeedPickerContainer, .ocArticleFooterSection.articleSupportBridge, #ocFooterWrapper",
            verbose=True,
            mean_delay=2.0,  # Base delay between requests
            max_range=1.0    # Add up to 1 second of random delay
        )
        logger.info(f"Custom CrawlerRunConfig for KB: {kb_run_config}")

        # Initialize base scraper with configs for single URL operations
        super().__init__(
            browser_config=kb_browser_config,
            run_config=kb_run_config
        )

        # Setup bulk crawler with memory-adaptive dispatcher
        rate_limiter = RateLimiter(
            base_delay=(2.0, 4.0),  # Random delay between 2-4 seconds
            max_delay=60.0,         # Maximum delay after rate limit hits
            max_retries=3,          # Retries before giving up
            rate_limit_codes=[429, 503, 504, 408]  # Status codes to handle
        )

        bulk_dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=90.0,  # Adjust based on system resources
            max_session_permit=20,         # Maximum concurrent sessions
            rate_limiter=rate_limiter
        )

        self.bulk_crawler = AsyncWebCrawler(
            config=kb_browser_config,
            dispatcher=bulk_dispatcher
        )
        logger.info("Initialized bulk crawler with memory-adaptive dispatcher")

        # Set output directory
        self.output_dir: str = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),  # Go up to microsoft_cve_rag root
            "application",
            "data",
            "scrapes",
            "kb_articles"
        )
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory set to: {self.output_dir}")

    def _update_rate_limiter(self, max_retries: int | None) -> None:
        """Update the rate limiter's max_retries setting if a new value is provided.

        Updates the max_retries parameter of the bulk crawler's rate limiter. If
        max_retries is None, maintains the default value set during initialization.

        Args:
            max_retries (int | None): New maximum number of retry attempts. If None,
                keeps the default value set during initialization.

        Notes:
            - Only updates if max_retries is not None
            - Requires bulk_crawler and rate_limiter to be properly initialized
        """
        if max_retries is None:
            logger.debug("Using default max_retries value from initialization")
            return

        if hasattr(self, 'bulk_crawler') and self.bulk_crawler.dispatcher.rate_limiter:
            self.bulk_crawler.dispatcher.rate_limiter.max_retries = max_retries
            logger.info(f"Updated rate limiter max_retries to {max_retries}")

    @staticmethod
    def _is_kb_article_url(url: str) -> bool:
        """Check if the URL is a valid HTML URL.

        Args:
            url: URL to validate

        Returns:
            bool: True if URL is a valid HTML URL
        """
        if not isinstance(url, str):
            return False

        try:
            result = urlparse(url)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False

    async def scrape_kb_article(self, url: str) -> None:
        """Scrape content from a Microsoft KB article.

        Uses the AsyncWebCrawler to obtain raw HTML, then processes the crawl result
        (including HTML preprocessing and LLM-based extraction) to obtain structured content.

        Args:
            url (str): URL of the KB article to scrape.

        Returns:
            Optional[Dict[str, Any]]: Structured content as a JSON dictionary if successful,
            or None otherwise.
        """
        logger.info(f"Starting crawl for KB article: {url}")
        if not self.crawler:
            logger.error("Crawler not initialized.")

        try:
            async with self.crawler as crawler:
                self.urls.append(url)
                result = await crawler.arun(url=url, config=self.run_config)
                self.crawl_result = result
                logger.info(f"CrawlResult populated with {len(self.get_html())} characters of HTML")
                logger.info("CrawlResult structure:\n%s", json.dumps({
                    'html': bool(self.crawl_result.html),
                    'cleaned_html': bool(self.crawl_result.cleaned_html),
                    'structured_data': bool(self.crawl_result.extracted_content),
                    'screenshot': bool(self.crawl_result.screenshot)
                }, indent=4))
                if not self.get_success():
                    logger.error(f"No valid content retrieved from {url}")
                    if self.get_error_message():
                        logger.error(f"Error message: {self.get_error_message()}")

                logger.info(f"Status code: {self.get_status_code()}")
                logger.info("KB article scraped and processed successfully.")
                # Log content lengths to check for truncation
                raw_html = self.get_html()
                llm_extraction = self.get_extracted_content()
                logger.info(f"Raw HTML length: {len(raw_html)} characters")
                logger.info(f"LLM Extraction length: {len(llm_extraction)}")

                # Log browser and run configurations
                browser_config = self.get_browser_config()
                run_config = self.get_run_config()
                logger.info(f"Browser Config: {browser_config}")
                logger.info(f"Run Config: {run_config}")

        except Exception as e:
            logger.error(f"Error scraping KB article {url}: {str(e)}")

    async def bulk_crawl_kb_articles(
        self,
        urls: List[str],
        session_id: Optional[str] = None,
        max_retries: Optional[int] = None
    ) -> List[Any]:
        """Process multiple KB articles using memory-adaptive dispatcher.

        Args:
            urls: List of KB article URLs to process
            session_id: Optional identifier for session management
            max_retries: Maximum number of retry attempts per URL

        Returns:
            List[Any]: List of crawl results
        """
        logger.info(f"Starting bulk crawl of {len(urls)} KB articles")

        # Update rate limiter with provided max_retries
        self._update_rate_limiter(max_retries)

        try:
            # Use context manager with existing bulk_crawler
            async with self.bulk_crawler as crawler:
                results = await crawler.arun_many(
                    urls=urls,
                    config=self.run_config,
                    session_id=session_id
                )
                logger.info(f"Completed bulk crawl of {len(urls)} KB articles")
                return results

        except Exception as e:
            logger.error(f"Error during bulk crawl: {str(e)}")
            raise

    async def save_kb_bulk_results(
        self,
        results: List[Any],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Save bulk crawl results to disk.

        Args:
            results: List of crawl results to save
            output_dir: Optional directory to save results

        Returns:
            str: Path to output directory if successful, None otherwise

        Notes:
            - Saves all available formats: HTML, Markdown, JSON, PDF, PNG
            - Creates directory if it doesn't exist
            - Handles filesystem errors gracefully
            - Tracks success/failure for each save operation
        """
        if not results:
            logger.warning("No results to save")
            return None

        try:
            # Update output_dir if provided
            if output_dir:
                self.output_dir = output_dir

            os.makedirs(self.output_dir, exist_ok=True)

            successful_saves = 0
            failed_saves = 0
            save_errors = []

            # Process each result
            for i, result in enumerate(results, 1):
                url = getattr(result, "url", "unknown")
                clean_url = self.get_safe_filename(url)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"kb_article_{clean_url}_{timestamp}"

                try:
                    # Save HTML content
                    if hasattr(result, "cleaned_html"):
                        html_path = os.path.join(
                            self.output_dir,
                            f"{base_filename}.html"
                        )
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(result.cleaned_html)

                    # Save Markdown content
                    if hasattr(result, "markdown"):
                        md_path = os.path.join(
                            self.output_dir,
                            f"{base_filename}.md"
                        )
                        with open(md_path, "w", encoding="utf-8") as f:
                            f.write(result.markdown)

                    # Save JSON content (extracted_content)
                    content = result.get_extracted_content()
                    if content:
                        if isinstance(content, list):
                            valid_items = []
                            for item in content:
                                if isinstance(item, dict):
                                    try:
                                        kb_item = KBArticle(**item)
                                        valid_items.append(kb_item.model_dump())
                                    except ValidationError as e:
                                        logger.error(f"Validation error for an element in {url}: {str(e)}")
                                        continue
                                else:
                                    logger.error(f"Element in content list for {url} is not a mapping")
                            if not valid_items:
                                logger.error(f"No valid KBArticle objects in list for {url}")
                                error_path = os.path.join(
                                    self.output_dir,
                                    f"{base_filename}_error.json"
                                )
                                with open(error_path, "w", encoding="utf-8") as f:
                                    json.dump({
                                        "error": True,
                                        "url": url,
                                        "validation_errors": "No valid KBArticle objects in list",
                                        "raw_content": content
                                    }, f, indent=2)
                                failed_saves += 1
                                continue
                            json_path = os.path.join(
                                self.output_dir,
                                f"{base_filename}.json"
                            )
                            with open(json_path, "w", encoding="utf-8") as f:
                                json.dump(valid_items, f, indent=2)
                            successful_saves += 1
                        else:
                            try:
                                validated_content = KBArticle(**content)
                                json_path = os.path.join(
                                    self.output_dir,
                                    f"{base_filename}.json"
                                )
                                with open(json_path, "w", encoding="utf-8") as f:
                                    json.dump(validated_content.model_dump(), f, indent=2)
                                successful_saves += 1
                            except ValidationError as e:
                                logger.error(f"Failed to validate content for {url}: {str(e)}")
                                error_path = os.path.join(
                                    self.output_dir,
                                    f"{base_filename}_error.json"
                                )
                                with open(error_path, "w", encoding="utf-8") as f:
                                    json.dump({
                                        "error": True,
                                        "url": url,
                                        "validation_errors": str(e),
                                        "raw_content": content
                                    }, f, indent=2)
                                failed_saves += 1
                                continue

                    # Save PDF content
                    if hasattr(result, "pdf") and result.pdf:
                        pdf_path = os.path.join(
                            self.output_dir,
                            f"{base_filename}.pdf"
                        )
                        with open(pdf_path, "wb") as f:
                            f.write(result.pdf)

                    # Save screenshot/thumbnail
                    if hasattr(result, "screenshot") and result.screenshot:
                        png_path = os.path.join(
                            self.output_dir,
                            f"{base_filename}.png"
                        )
                        with open(png_path, "wb") as f:
                            f.write(result.screenshot)

                    # Save raw HTML if available
                    if hasattr(result, "raw_html"):
                        raw_path = os.path.join(
                            self.output_dir,
                            f"{base_filename}_raw.html"
                        )
                        with open(raw_path, "w", encoding="utf-8") as f:
                            f.write(result.raw_html)

                    successful_saves += 1
                    logger.info(f"Saved result {i} to {base_filename}")

                except (OSError, IOError) as e:
                    failed_saves += 1
                    error_msg = f"Failed to save result {i} ({url}): {str(e)}"
                    logger.error(error_msg)
                    save_errors.append(error_msg)
                    continue

            # Save summary with detailed error information
            try:
                summary = {
                    "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                    "total_results": len(results),
                    "successful_saves": successful_saves,
                    "failed_saves": failed_saves,
                    "urls": [
                        getattr(r, "url", "unknown") for r in results
                    ],
                    "errors": save_errors
                }
                summary_path = os.path.join(
                    self.output_dir,
                    f"kb_articles_bulk_scrape_summary_{timestamp}.json"
                )
                with open(summary_path, "w", encoding="utf-8") as f:
                    json.dump(summary, f, indent=2)

                logger.info(
                    f"Saved {successful_saves} results "
                    f"({failed_saves} failed) to {self.output_dir}"
                )
                return self.output_dir

            except (OSError, IOError) as e:
                logger.error(f"Failed to save summary file: {str(e)}")
                return None if failed_saves == len(results) else self.output_dir

        except Exception as e:
            logger.error(f"Failed to save bulk results: {str(e)}")
            return None


class GenericWebScraper(BaseScraper):
    """A general-purpose web scraper that exposes all crawl4ai configuration options.
    
    This scraper allows full customization of browser config, crawler config, and extraction
    strategy through a frontend interface. It supports both LLM-based and CSS/XPath-based
    extraction strategies.
    """
    def __init__(
        self,
        output_dir: Optional[str] = None,
        browser_config: Optional[Dict[str, Any]] = None,
        crawler_config: Optional[Dict[str, Any]] = None,
        extraction_config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize the generic scraper with fully customizable configuration.

        Args:
            output_dir: Directory to save scraped content
            browser_config: Dictionary of BrowserConfig parameters
            crawler_config: Dictionary of CrawlerRunConfig parameters
            extraction_config: Dictionary specifying extraction strategy and its parameters
        """
        logger.info("Initializing GenericWebScraper")

        # Set output directory
        self.output_dir = output_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "application",
            "data",
            "scrapes",
            "generic"
        )
        os.makedirs(self.output_dir, exist_ok=True)
        logger.info(f"Output directory set to: {self.output_dir}")

        # Configure browser settings
        browser_cfg = BrowserConfig(
            browser_type=browser_config.get("browser_type", "chromium"),
            headless=browser_config.get("headless", True),
            viewport_width=browser_config.get("viewport_width", 1920),
            viewport_height=browser_config.get("viewport_height", 1080),
            verbose=browser_config.get("verbose", True)
        ) if browser_config else None

        # Configure extraction strategy
        extraction_strategy = None
        if extraction_config:
            strategy_type = extraction_config.get("type", "llm")
            if strategy_type == "llm":
                # LLM-based extraction
                extraction_strategy = LLMExtractionStrategy(
                    provider=extraction_config.get("provider"),
                    api_token=extraction_config.get("api_token"),
                    schema=extraction_config.get("schema"),
                    extraction_type=extraction_config.get("extraction_type", "schema"),
                    instruction=extraction_config.get("instruction", "Extract structured data from the content."),
                    chunk_token_threshold=extraction_config.get("chunk_token_threshold", 2000),
                    overlap_rate=extraction_config.get("overlap_rate", 0.07),
                    apply_chunking=extraction_config.get("apply_chunking", True),
                    input_format=extraction_config.get("input_format", "html"),
                    verbose=extraction_config.get("verbose", True)
                )
                
                if not extraction_strategy.api_token:
                    raise ValueError("API token is required for LLM-based extraction")
                    
            elif strategy_type == "css":
                # CSS-based extraction
                extraction_strategy = JsonCssExtractionStrategy(
                    schema=extraction_config.get("schema", {}),
                    verbose=extraction_config.get("verbose", True)
                )
            elif strategy_type == "xpath":
                # XPath-based extraction
                extraction_strategy = JsonXPathExtractionStrategy(
                    schema=extraction_config.get("schema", {}),
                    verbose=extraction_config.get("verbose", True)
                )

        # Configure crawler settings
        crawler_cfg = CrawlerRunConfig(
            cache_mode=crawler_config.get("cache_mode", CacheMode.DISABLED),
            extraction_strategy=extraction_strategy,
            word_count_threshold=crawler_config.get("word_count_threshold", 0),
            exclude_external_links=crawler_config.get("exclude_external_links", True),
            wait_until=crawler_config.get("wait_until", "domcontentloaded"),
            css_selector=crawler_config.get("css_selector"),
            excluded_tags=crawler_config.get("excluded_tags", []),
            excluded_selector=crawler_config.get("excluded_selector"),
            verbose=crawler_config.get("verbose", True),
            mean_delay=crawler_config.get("mean_delay", 2.0),
            max_range=crawler_config.get("max_range", 1.0)
        ) if crawler_config else None

        # Initialize base scraper
        super().__init__(
            browser_config=browser_cfg,
            run_config=crawler_cfg
        )

        # Setup bulk crawler with memory-adaptive dispatcher
        rate_limiter = RateLimiter(
            base_delay=(2.0, 4.0),
            max_delay=60.0,
            max_retries=3,
            rate_limit_codes=[429, 503, 504, 408]
        )

        bulk_dispatcher = MemoryAdaptiveDispatcher(
            memory_threshold_percent=90.0,
            max_session_permit=20,
            rate_limiter=rate_limiter
        )

        self.bulk_crawler = AsyncWebCrawler(
            config=browser_cfg,
            dispatcher=bulk_dispatcher
        )
        logger.info("Initialized bulk crawler with memory-adaptive dispatcher")

    async def scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape content from a single URL.

        Args:
            url: URL to scrape

        Returns:
            Optional[Dict[str, Any]]: Extracted content if successful, None otherwise
        """
        logger.info(f"Starting scrape for URL: {url}")
        if not self.crawler:
            logger.error("Crawler not initialized")
            return None

        try:
            async with self.crawler as crawler:
                self.urls.append(url)
                result = await crawler.arun(url=url, config=self.run_config)
                self.crawl_result = result

                if not self.get_success():
                    logger.error(f"Failed to retrieve content from {url}")
                    if self.get_error_message():
                        logger.error(f"Error message: {self.get_error_message()}")
                    return None

                extracted_content = self.get_extracted_content()
                if not extracted_content:
                    logger.warning("No content was extracted")
                    return None

                logger.info("URL scraped and processed successfully")
                return extracted_content

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return None

    async def bulk_scrape(
        self,
        urls: List[str],
        session_id: Optional[str] = None,
        max_retries: Optional[int] = None
    ) -> List[Any]:
        """Process multiple URLs using memory-adaptive dispatcher.

        Args:
            urls: List of URLs to process
            session_id: Optional identifier for session management
            max_retries: Maximum number of retry attempts per URL

        Returns:
            List[Any]: List of crawl results
        """
        logger.info(f"Starting bulk scrape of {len(urls)} URLs")

        if max_retries is not None:
            self.bulk_crawler.dispatcher.rate_limiter.max_retries = max_retries

        try:
            async with self.bulk_crawler as crawler:
                results = await crawler.arun_many(
                    urls=urls,
                    config=self.run_config,
                    session_id=session_id
                )
                logger.info(f"Completed bulk scrape of {len(urls)} URLs")
                return results

        except Exception as e:
            logger.error(f"Error during bulk scrape: {str(e)}")
            raise

    async def save_results(
        self,
        results: List[Any],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Save crawl results to disk.

        Args:
            results: List of crawl results to save
            output_dir: Optional directory to save results

        Returns:
            str: Path to output directory if successful, None otherwise
        """
        if not results:
            logger.warning("No results to save")
            return None

        try:
            # Update output_dir if provided
            if output_dir:
                self.output_dir = output_dir

            os.makedirs(self.output_dir, exist_ok=True)

            successful_saves = 0
            failed_saves = 0
            save_errors = []

            # Process each result
            for i, result in enumerate(results, 1):
                url = getattr(result, "url", "unknown")
                clean_url = self.get_safe_filename(url)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                base_filename = f"scrape_{clean_url}_{timestamp}"

                try:
                    # Save HTML content
                    if hasattr(result, "cleaned_html"):
                        html_path = os.path.join(
                            self.output_dir,
                            f"{base_filename}.html"
                        )
                        with open(html_path, "w", encoding="utf-8") as f:
                            f.write(result.cleaned_html)

                    # Save extracted content
                    content = result.get_extracted_content()
                    if content:
                        json_path = os.path.join(
                            self.output_dir,
                            f"{base_filename}.json"
                        )
                        with open(json_path, "w", encoding="utf-8") as f:
                            json.dump(content, f, indent=2)

                    successful_saves += 1
                    logger.info(f"Saved result {i} to {base_filename}")

                except (OSError, IOError) as e:
                    failed_saves += 1
                    error_msg = f"Failed to save result {i} ({url}): {str(e)}"
                    logger.error(error_msg)
                    save_errors.append(error_msg)
                    continue

            # Save summary
            summary = {
                "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "total_results": len(results),
                "successful_saves": successful_saves,
                "failed_saves": failed_saves,
                "urls": [getattr(r, "url", "unknown") for r in results],
                "errors": save_errors
            }
            summary_path = os.path.join(
                self.output_dir,
                f"scrape_summary_{timestamp}.json"
            )
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2)

            logger.info(
                f"Saved {successful_saves} results "
                f"({failed_saves} failed) to {self.output_dir}"
            )
            return self.output_dir

        except Exception as e:
            logger.error(f"Failed to save results: {str(e)}")
            return None

async def main() -> None:
    """Test the generic scraper with different configurations."""
    logger.info("Starting generic scraper test")

    # Test URLs
    urls = [
        "https://example.com/page1",
        "https://example.com/page2"
    ]

    try:
        # Example configuration
        browser_config = {
            "browser_type": "chromium",
            "headless": True,
            "viewport_width": 1920,
            "viewport_height": 1080
        }

        crawler_config = {
            "word_count_threshold": 0,
            "exclude_external_links": True,
            "wait_until": "domcontentloaded",
            "css_selector": "main",
            "excluded_tags": ["nav", "footer"]
        }

        # Load API credentials from environment
        extraction_config = {
            "type": "llm",
            "provider": os.getenv("LLM_PROVIDER"),
            "api_token": os.getenv("LLM_API_KEY"),
            "schema": {
                "title": "str",
                "content": "str"
            },
            "instruction": "Extract the title and main content from the page."
        }

        # Initialize scraper
        scraper = GenericWebScraper(
            browser_config=browser_config,
            crawler_config=crawler_config,
            extraction_config=extraction_config
        )
        logger.info("GenericWebScraper initialized")

        # Test bulk scraping
        logger.info("\n=== Testing Bulk Scraping ===")
        logger.info(f"Processing {len(urls)} URLs in batch")

        batch_results = await scraper.bulk_scrape(urls)
        logger.info("Batch processing complete")

        # Save results
        output_path = await scraper.save_results(batch_results)
        if output_path:
            logger.info(f"Results saved to: {output_path}")

    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
    finally:
        if scraper and scraper.crawler:
            await scraper.crawler.close()
        logger.info("Test complete")

if __name__ == "__main__":
    asyncio.run(main())
