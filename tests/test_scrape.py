import requests


def test_scrape():
    url = "http://localhost:8002/api/scrape/"
    data = {
        "urls": [
            "https://support.microsoft.com/en-us/topic/january-14-2025-kb5050009-os-build-26100-2894-bdbfb097-ea20-487d-9171-718d15e26f1b"
        ],
        "config": {
            "browser_config": {
                "browser_type": "chromium",
                "headless": True,
                "viewport_width": 1920,
                "viewport_height": 1080,
            },
            "crawler_config": {
                "word_count_threshold": 100,
                "exclude_external_links": True,
                "wait_until": "networkidle",
                "css_selector": "main",
                "excluded_tags": ["script", "style", "nav", "footer"],
                "excluded_selector": None,
                "mean_delay": 1.0,
                "max_range": 0.5,
            },
            "extraction_schema": {
                "title": "string",
                "release_date": "date",
                "kb_number": "string",
                "os_build": "string",
                "content": "string",
                "applies_to": "list",
            },
            "extraction_instruction": (
                "Extract structured data from the Microsoft KB article,"
                " including title, release date, KB number, OS build, content"
                " sections, and what systems this applies to."
            ),
        },
    }

    # First, ensure we have the correct credentials
    creds_url = "http://localhost:8002/api/credentials/"
    creds_data = {
        "provider_name": "openrouter",
        "model_name": "google/gemini-2.0-flash-exp:free",
        "api_key": "test-key-123",
    }
    headers = {"Content-Type": "application/json"}

    # Create/update credentials
    creds_response = requests.post(creds_url, json=creds_data, headers=headers)
    print(f"Credentials Status Code: {creds_response.status_code}")
    print(f"Credentials Response: {creds_response.json()}")

    # Now make the scrape request
    scrape_response = requests.post(url, json=data, headers=headers)
    print(f"\nScrape Status Code: {scrape_response.status_code}")
    print(f"Scrape Response: {scrape_response.json()}")


if __name__ == "__main__":
    test_scrape()
