import streamlit as st
import requests
import json
import os
from typing import Dict, Any, List

# Get API URL from environment variable, default to localhost if not set
API_URL = os.getenv('API_URL', 'http://localhost:8000')

def fetch_providers() -> List[Dict[str, Any]]:
    """Fetch available LLM providers and models."""
    try:
        response = requests.get(f"{API_URL}/api/credentials/providers")
        if response.ok:
            return response.json()
        return []
    except Exception:
        return []

def fetch_active_credentials() -> Dict[str, Any]:
    """Fetch currently active credentials."""
    try:
        response = requests.get(f"{API_URL}/api/credentials/active")
        if response.ok:
            return response.json()
        return None
    except Exception:
        return None

def save_credentials(provider_name: str, model_name: str, api_key: str) -> bool:
    """Save new LLM provider credentials."""
    try:
        response = requests.post(
            f"{API_URL}/api/credentials",
            json={
                "provider_name": provider_name,
                "model_name": model_name,
                "api_key": api_key
            }
        )
        return response.ok
    except Exception:
        return False

def main():
    st.set_page_config(page_title="Web Scraper Configuration", layout="wide")
    
    st.title("Web Scraper Configuration")

    # Tabs for different sections
    tab1, tab2 = st.tabs(["LLM Credentials", "Scraping Configuration"])

    with tab1:
        st.header("LLM Provider Credentials")

        # Show active credentials if any
        active_creds = fetch_active_credentials()
        if active_creds:
            st.info(f"Active Provider: {active_creds['provider_identifier']}")

        # Get available providers
        providers = fetch_providers()
        provider_names = list(set(p["provider_name"] for p in providers))

        # Provider selection
        selected_provider = st.selectbox(
            "Select Provider",
            options=provider_names,
            key="provider_select"
        )

        # Model selection based on provider
        if selected_provider:
            available_models = [
                p["model_name"]
                for p in providers
                if p["provider_name"] == selected_provider
            ]
            selected_model = st.selectbox(
                "Select Model",
                options=available_models,
                key="model_select"
            )

            # API Key input
            api_key = st.text_input(
                "API Key",
                type="password",
                help="Your API key will be encrypted before storage"
            )

            if st.button("Save Credentials"):
                if save_credentials(selected_provider, selected_model, api_key):
                    st.success("Credentials saved successfully!")
                    st.rerun()  # Refresh to show new active credentials
                else:
                    st.error("Failed to save credentials")

    with tab2:
        st.header("Scraping Configuration")

        # Browser Configuration
        st.subheader("Browser Settings")
        col1, col2 = st.columns(2)
        with col1:
            browser_type = st.selectbox(
                "Browser Type",
                options=["chromium", "firefox", "webkit"],
                help="Select the browser to use for scraping"
            )
            viewport_width = st.number_input(
                "Viewport Width",
                min_value=800,
                max_value=3840,
                value=1920
            )
        with col2:
            headless = st.checkbox("Headless Mode", value=True)
            viewport_height = st.number_input(
                "Viewport Height",
                min_value=600,
                max_value=2160,
                value=1080
            )

        # Crawler Configuration
        st.subheader("Crawler Settings")
        col1, col2 = st.columns(2)
        with col1:
            word_count_threshold = st.number_input(
                "Word Count Threshold",
                min_value=0,
                value=0,
                help="Minimum number of words required for content extraction"
            )
            wait_until = st.selectbox(
                "Wait Until",
                options=["domcontentloaded", "networkidle", "load"],
                help="Page load wait condition"
            )
        with col2:
            exclude_external = st.checkbox(
                "Exclude External Links",
                value=True,
                help="Exclude links to external domains"
            )
            css_selector = st.text_input(
                "CSS Selector",
                help="Optional CSS selector to target specific content"
            )

        # Advanced Settings
        with st.expander("Advanced Settings"):
            excluded_tags = st.text_input(
                "Excluded Tags",
                value="nav,footer",
                help="Comma-separated list of HTML tags to exclude"
            )
            excluded_selector = st.text_input(
                "Excluded Selector",
                help="CSS selector for elements to exclude"
            )
            mean_delay = st.slider(
                "Mean Delay (seconds)",
                min_value=0.0,
                max_value=10.0,
                value=2.0,
                help="Average delay between requests"
            )
            max_range = st.slider(
                "Max Range (seconds)",
                min_value=0.0,
                max_value=5.0,
                value=1.0,
                help="Maximum random delay variation"
            )

        # Extraction Strategy
        st.subheader("Extraction Strategy")
        extraction_type = st.selectbox(
            "Strategy Type",
            options=["llm", "css", "xpath"],
            help="Choose how to extract data from the pages"
        )

        if extraction_type == "llm":
            extraction_instruction = st.text_area(
                "Extraction Instructions",
                value="Extract structured data from the content.",
                help="Instructions for the LLM on how to extract data"
            )
            extraction_schema = st.text_area(
                "JSON Schema",
                value='{"title": "str", "content": "str"}',
                help="JSON schema defining the structure of extracted data"
            )
        elif extraction_type in ["css", "xpath"]:
            extraction_schema = st.text_area(
                "Selector Schema",
                value='{"title": ".article-title", "content": ".article-content"}',
                help=f"JSON mapping of fields to {extraction_type} selectors"
            )

        # URL Input
        st.subheader("URLs to Scrape")
        url_input = st.text_area(
            "Enter URLs (one per line)",
            height=100,
            help="Enter the URLs you want to scrape, one per line"
        )

        # Save configuration and start scraping
        if st.button("Start Scraping"):
            urls = [url.strip() for url in url_input.split("\n") if url.strip()]
            if not urls:
                st.error("Please enter at least one URL")
                return

            try:
                # Parse extraction schema
                schema = json.loads(extraction_schema)
            except json.JSONDecodeError:
                st.error("Invalid JSON schema")
                return

            # Build configuration
            config = {
                "browser_config": {
                    "browser_type": browser_type,
                    "headless": headless,
                    "viewport_width": viewport_width,
                    "viewport_height": viewport_height
                },
                "crawler_config": {
                    "word_count_threshold": word_count_threshold,
                    "exclude_external_links": exclude_external,
                    "wait_until": wait_until,
                    "css_selector": css_selector or None,
                    "excluded_tags": [t.strip() for t in excluded_tags.split(",")],
                    "excluded_selector": excluded_selector or None,
                    "mean_delay": mean_delay,
                    "max_range": max_range
                },
                "extraction_type": extraction_type,
                "extraction_schema": schema
            }

            if extraction_type == "llm":
                config["extraction_instruction"] = extraction_instruction

            # Start scraping
            try:
                response = requests.post(
                    f"{API_URL}/api/scrape",
                    json={"urls": urls, "config": config}
                )
                if response.ok:
                    result = response.json()
                    st.success(f"Scraping completed! Results saved to: {result['output_dir']}")
                    st.json(result)  # Show full result details
                else:
                    st.error(f"Failed to start scraping: {response.text}")
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
