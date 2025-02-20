from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging
from ..models import LLMCredentials, ProviderModel
from datetime import datetime

logger = logging.getLogger(__name__)

class CredentialsService:
    """Service for managing LLM provider credentials."""

    def __init__(self, db: Session):
        self.db = db

    def get_active_credentials(self) -> Optional[LLMCredentials]:
        """Get the currently active credentials."""
        try:
            return self.db.query(LLMCredentials)\
                .filter(LLMCredentials.is_active == True)\
                .first()
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching active credentials: {str(e)}")
            return None

    def save_credentials(
        self,
        provider_name: str,
        model_name: str,
        api_key: str
    ) -> Optional[LLMCredentials]:
        """Save new credentials and make them active."""
        try:
            # Deactivate any existing credentials
            self.db.query(LLMCredentials)\
                .filter(LLMCredentials.is_active == True)\
                .update({"is_active": False})

            # Create new credentials
            creds = LLMCredentials(
                provider_name=provider_name,
                model_name=model_name,
                is_active=True
            )
            creds.encrypt_api_key(api_key)

            self.db.add(creds)
            self.db.commit()
            return creds
        except SQLAlchemyError as e:
            logger.error(f"Database error while saving credentials: {str(e)}")
            self.db.rollback()
            return None

    def update_credentials(
        self,
        cred_id: int,
        api_key: str
    ) -> Optional[LLMCredentials]:
        """Update existing credentials with a new API key."""
        try:
            creds = self.db.query(LLMCredentials)\
                .filter(LLMCredentials.id == cred_id)\
                .first()
            
            if not creds:
                return None

            creds.encrypt_api_key(api_key)
            creds.updated_at = datetime.utcnow()
            
            self.db.commit()
            return creds
        except SQLAlchemyError as e:
            logger.error(f"Database error while updating credentials: {str(e)}")
            self.db.rollback()
            return None

    def delete_credentials(self, cred_id: int) -> bool:
        """Delete credentials by ID."""
        try:
            result = self.db.query(LLMCredentials)\
                .filter(LLMCredentials.id == cred_id)\
                .delete()
            self.db.commit()
            return result > 0
        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting credentials: {str(e)}")
            self.db.rollback()
            return False

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available providers and their models."""
        try:
            providers = self.db.query(ProviderModel)\
                .filter(ProviderModel.is_available == True)\
                .all()
            
            return [
                {
                    "provider_name": p.provider_name,
                    "model_name": p.model_name,
                    "description": p.description
                }
                for p in providers
            ]
        except SQLAlchemyError as e:
            logger.error(f"Database error while fetching providers: {str(e)}")
            return []

    def initialize_providers(self) -> None:
        """Initialize the provider_models table with supported providers."""
        try:
            # Check if we already have providers
            if self.db.query(ProviderModel).count() > 0:
                return

            # Add supported providers from config
            for provider, config in ProviderModel.Config.SUPPORTED_PROVIDERS.items():
                for model in config["models"]:
                    provider_model = ProviderModel(
                        provider_name=provider,
                        model_name=model,
                        description=f"{provider.title()} {model} model",
                        is_available=True
                    )
                    self.db.add(provider_model)
            
            self.db.commit()
        except SQLAlchemyError as e:
            logger.error(f"Database error while initializing providers: {str(e)}")
            self.db.rollback() 