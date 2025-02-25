import requests

# import json

BASE_URL = "http://localhost:8002"  # Debug server port


def test_credentials():
    url = f"{BASE_URL}/api/v1/credentials"
    data = {
        "provider": "openrouter",
        "model": "google/gemini-2.0-flash-exp:free",
        "api_key": "test_key",
    }
    response = requests.post(url, json=data)
    print(f"Credentials Status Code: {response.status_code}")
    print(f"Credentials Response: {response.json()}")
    return response.json()


def test_scrape():
    url = f"{BASE_URL}/api/v1/scrape"
    data = {
        "urls": [
            "https://support.microsoft.com/en-us/topic/kb5034441-windows-11-update-history-ec216756-67c6-4da4-a61b-1e51d52a7aed"
        ]
    }
    response = requests.post(url, json=data)
    print(f"Scrape Status Code: {response.status_code}")
    print(f"Scrape Response: {response.json()}")
    return response.json()


if __name__ == "__main__":
    creds = test_credentials()
    scrape = test_scrape()
