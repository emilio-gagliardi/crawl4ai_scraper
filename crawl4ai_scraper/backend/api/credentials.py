from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
from ..services.credentials import CredentialsService
from ..database import get_db

router = APIRouter(prefix="/api/credentials", tags=["credentials"])

class CredentialCreate(BaseModel):
    """Schema for creating new credentials."""
    provider_name: str
    model_name: str
    api_key: str

class CredentialUpdate(BaseModel):
    """Schema for updating credentials."""
    api_key: str

class Provider(BaseModel):
    """Schema for provider information."""
    provider_name: str
    model_name: str
    description: str

@router.get("/providers", response_model=List[Provider])
async def get_providers(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Get list of available LLM providers and models."""
    service = CredentialsService(db)
    return service.get_available_providers()

@router.post("/", status_code=201)
async def create_credentials(
    creds: CredentialCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Save new LLM provider credentials."""
    service = CredentialsService(db)
    result = service.save_credentials(
        provider_name=creds.provider_name,
        model_name=creds.model_name,
        api_key=creds.api_key
    )
    
    if not result:
        raise HTTPException(
            status_code=500,
            detail="Failed to save credentials"
        )
    
    return {
        "message": "Credentials saved successfully",
        "provider": result.provider_name,
        "model": result.model_name
    }

@router.put("/{cred_id}")
async def update_credentials(
    cred_id: int,
    creds: CredentialUpdate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update existing credentials with new API key."""
    service = CredentialsService(db)
    result = service.update_credentials(
        cred_id=cred_id,
        api_key=creds.api_key
    )
    
    if not result:
        raise HTTPException(
            status_code=404,
            detail="Credentials not found"
        )
    
    return {
        "message": "Credentials updated successfully",
        "provider": result.provider_name,
        "model": result.model_name
    }

@router.delete("/{cred_id}")
async def delete_credentials(
    cred_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Delete credentials by ID."""
    service = CredentialsService(db)
    if not service.delete_credentials(cred_id):
        raise HTTPException(
            status_code=404,
            detail="Credentials not found"
        )
    
    return {"message": "Credentials deleted successfully"}

@router.get("/active")
async def get_active_credentials(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get currently active credentials."""
    service = CredentialsService(db)
    creds = service.get_active_credentials()
    
    if not creds:
        raise HTTPException(
            status_code=404,
            detail="No active credentials found"
        )
    
    return {
        "provider": creds.provider_name,
        "model": creds.model_name,
        "provider_identifier": creds.provider_identifier
    } 