from datetime import datetime

import pytest

from crawl4ai_scraper.backend.models import Credentials
from crawl4ai_scraper.backend.schemas import APIStatusCode, ResponseStatus


def test_create_credentials_success(client, test_db):
    """Test successful credential creation response."""
    response = client.post(
        "/api/credentials/",
        json={
            "provider_name": "openrouter",
            "model_name": "google/gemini-2.0-pro-exp-02-05:free",
            "api_key": "test-key",
        },
    )
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert data["status"] == ResponseStatus.SUCCESS
    assert data["code"] == APIStatusCode.CREATED
    assert isinstance(data["data"], dict)

    # Verify credential data
    cred_data = data["data"]
    assert cred_data["provider"] == "openrouter"
    assert cred_data["model"] == "google/gemini-2.0-pro-exp-02-05:free"
    assert (
        cred_data["provider_identifier"]
        == "openrouter/google/gemini-2.0-pro-exp-02-05:free"
    )
    assert cred_data["is_active"] is True
    assert isinstance(
        datetime.fromisoformat(cred_data["created_at"].replace("Z", "+00:00")),
        datetime,
    )


def test_get_active_credentials_not_found(client):
    """Test response when no active credentials exist."""
    response = client.get("/api/credentials/active")
    assert response.status_code == 200
    data = response.json()

    # Verify error response
    assert data["status"] == ResponseStatus.ERROR
    assert data["code"] == APIStatusCode.NOT_FOUND
    assert data["data"] is None
    assert "No active credentials found" in data["message"]


def test_get_active_credentials_success(client, test_db):
    """Test successful retrieval of active credentials."""
    # Create test credentials
    creds = Credentials(
        provider="openrouter",
        model="google/gemini-2.0-pro-exp-02-05:free",
        api_key="encrypted-key",
        is_active=True,
        created_at=datetime.utcnow(),
    )
    test_db.add(creds)
    test_db.commit()

    response = client.get("/api/credentials/active")
    assert response.status_code == 200
    data = response.json()

    # Verify success response
    assert data["status"] == ResponseStatus.SUCCESS
    assert data["code"] == APIStatusCode.SUCCESS
    assert isinstance(data["data"], dict)

    # Verify credential data
    cred_data = data["data"]
    assert cred_data["provider"] == "openrouter"
    assert cred_data["model"] == "google/gemini-2.0-pro-exp-02-05:free"
    assert cred_data["is_active"] is True
