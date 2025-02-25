import requests


def test_create_credentials():
    url = "http://localhost:8002/api/credentials/"
    data = {
        "provider_name": "openrouter",
        "model_name": "google/gemini-2.0-pro-exp-02-05:free",
        "api_key": "test-key-123",
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


if __name__ == "__main__":
    test_create_credentials()
