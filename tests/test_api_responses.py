import pytest
from fastapi.testclient import TestClient

from crawl4ai_scraper.backend.main import app
from crawl4ai_scraper.backend.schemas import APIStatusCode, ResponseStatus

client = TestClient(app)


def test_root_endpoint():
    """Test that the root endpoint returns proper response structure."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "status" in data
    assert "message" in data
    assert "code" in data
    assert "data" in data

    # Verify response content
    assert data["status"] == ResponseStatus.SUCCESS
    assert data["code"] == APIStatusCode.SUCCESS
    assert isinstance(data["data"], dict)
    assert "service" in data["data"]
    assert "version" in data["data"]


def test_get_providers():
    """Test that the providers endpoint returns proper response structure."""
    response = client.get("/api/credentials/providers")
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["status"] == ResponseStatus.SUCCESS
    assert data["code"] == APIStatusCode.SUCCESS
    assert isinstance(data["data"], list)

    # Verify provider data structure
    provider = data["data"][0]
    assert "provider_name" in provider
    assert "model_name" in provider
    assert "description" in provider


def test_create_credentials_error():
    """Test error response structure for invalid credentials."""
    response = client.post(
        "/api/credentials/",
        json={
            "provider_name": "invalid",
            "model_name": "invalid",
            "api_key": "invalid",
        },
    )
    data = response.json()

    # Verify error response structure
    assert data["status"] == ResponseStatus.ERROR
    assert data["code"] == APIStatusCode.INVALID_REQUEST
    assert data["data"] is None
    assert "message" in data


def test_scrape_error():
    """Test error response structure for invalid scrape request."""
    response = client.post(
        "/api/scrape/", json={"urls": ["invalid-url"], "config": {}}
    )
    data = response.json()

    # Verify error response structure
    assert data["status"] == ResponseStatus.ERROR
    assert data["code"] == APIStatusCode.INVALID_REQUEST
    assert "message" in data
