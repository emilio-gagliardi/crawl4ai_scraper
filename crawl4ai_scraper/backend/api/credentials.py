from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..database import get_db
from ..schemas import (
    APIStatusCode,
    CredentialCreate,
    CredentialResponse,
    ProviderListResponse,
    ResponseStatus,
)
from ..services.credentials import CredentialsService

router = APIRouter(prefix="/api/credentials", tags=["credentials"])


@router.get(
    "/providers",
    response_model=ProviderListResponse,
    responses={
        200: {
            "description": "Successfully retrieved providers",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Retrieved available providers",
                        "code": 200,
                        "data": [{
                            "provider_name": "openrouter",
                            "model_name": (
                                "google/gemini-2.0-pro-exp-02-05:free"
                            ),
                            "description": "Google Gemini Pro via OpenRouter",
                        }],
                    }
                }
            },
        }
    },
)
async def get_providers() -> ProviderListResponse:
    """
    Get available LLM providers and models.

    Returns:
        List of provider information objects containing:
        - provider_name: Name of the LLM provider
        - model_name: Specific model identifier
        - description: Human-readable description of the model
    """
    providers = [
        {
            "provider_name": "openrouter",
            "model_name": "google/gemini-2.0-pro-exp-02-05:free",
            "description": "Google Gemini Pro via OpenRouter",
        },
        {
            "provider_name": "openrouter",
            "model_name": "google/gemini-2.0-flash-exp:free",
            "description": "Google Gemini Flash via OpenRouter",
        },
    ]

    return ProviderListResponse(
        status=ResponseStatus.SUCCESS,
        message="Retrieved available providers",
        code=APIStatusCode.SUCCESS,
        data=providers,
    )


@router.get(
    "/active",
    response_model=CredentialResponse,
    responses={
        200: {
            "description": "Successfully retrieved active credentials",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Retrieved active credentials",
                        "code": 200,
                        "data": {
                            "provider": "openrouter",
                            "model": "google/gemini-2.0-pro-exp-02-05:free",
                            "provider_identifier": "openrouter/google/gemini-2.0-pro-exp-02-05:free",
                            "created_at": "2025-02-25T15:46:14Z",
                            "is_active": True,
                        },
                    }
                }
            },
        },
        404: {
            "description": "No active credentials found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": "No active credentials found",
                        "code": 404,
                        "data": None,
                    }
                }
            },
        },
    },
)
async def get_active_credentials(
    db: Session = Depends(get_db),
) -> CredentialResponse:
    """
    Get currently active credentials.

    Returns:
        Credential response object containing:
        - provider: Name of the active provider
        - model: Name of the active model
        - provider_identifier: Combined provider/model identifier
        - created_at: When the credentials were created
        - is_active: Whether the credentials are active
    """
    creds_service = CredentialsService(db)
    active_creds = creds_service.get_active_credentials()

    if not active_creds:
        return CredentialResponse(
            status=ResponseStatus.ERROR,
            message="No active credentials found",
            code=APIStatusCode.NOT_FOUND,
            data=None,
        )

    return CredentialResponse(
        status=ResponseStatus.SUCCESS,
        message="Retrieved active credentials",
        code=APIStatusCode.SUCCESS,
        data={
            "provider": active_creds.provider,
            "model": active_creds.model,
            "provider_identifier": (
                f"{active_creds.provider}/{active_creds.model}"
            ),
            "created_at": active_creds.created_at,
            "is_active": active_creds.is_active,
        },
    )


@router.post(
    "/",
    response_model=CredentialResponse,
    responses={
        201: {
            "description": "Successfully created credentials",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Credentials created successfully",
                        "code": 201,
                        "data": {
                            "provider": "openrouter",
                            "model": "google/gemini-2.0-pro-exp-02-05:free",
                            "provider_identifier": "openrouter/google/gemini-2.0-pro-exp-02-05:free",
                            "created_at": "2025-02-25T15:46:14Z",
                            "is_active": True,
                        },
                    }
                }
            },
        },
        400: {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "message": (
                            "Failed to create credentials: Invalid API key"
                        ),
                        "code": 400,
                        "data": None,
                    }
                }
            },
        },
    },
)
async def create_credentials(
    creds: CredentialCreate, db: Session = Depends(get_db)
) -> CredentialResponse:
    """Create new credentials and set them as active.

    Args:
        creds: Credential creation data containing:
            - provider_name: Name of the LLM provider
            - model_name: Name of the model to use
            - api_key: API key for the provider

    Returns:
        Newly created credentials

    Raises:
        HTTPException: If credential creation fails
    """
    try:
        creds_service = CredentialsService(db)
        new_creds = creds_service.create_credentials(
            provider=creds.provider_name,
            model=creds.model_name,
            api_key=creds.api_key,
        )

        return CredentialResponse(
            status=ResponseStatus.SUCCESS,
            message="Credentials created successfully",
            code=APIStatusCode.CREATED,
            data={
                "provider": new_creds.provider,
                "model": new_creds.model,
                "provider_identifier": (
                    f"{new_creds.provider}/{new_creds.model}"
                ),
                "created_at": new_creds.created_at,
                "is_active": new_creds.is_active,
            },
        )

    except Exception as e:
        return CredentialResponse(
            status=ResponseStatus.ERROR,
            message=f"Failed to create credentials: {str(e)}",
            code=APIStatusCode.INVALID_REQUEST,
            data=None,
        )
