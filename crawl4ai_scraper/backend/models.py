from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from cryptography.fernet import Fernet
import os

Base = declarative_base()

class LLMCredentials(Base):
    """Model for storing LLM provider credentials securely."""
    __tablename__ = 'llm_credentials'

    id = Column(Integer, primary_key=True)
    provider_name = Column(String(255), nullable=False)  # e.g. "OpenAI", "Anthropic"
    model_name = Column(String(255), nullable=False)     # e.g. "gpt-4", "claude-2"
    api_key = Column(Text, nullable=False)               # Encrypted API key
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def provider_identifier(self) -> str:
        """Get the full provider identifier used by crawl4ai."""
        return f"{self.provider_name.lower()}/{self.model_name}"

    def encrypt_api_key(self, api_key: str) -> None:
        """Encrypt the API key before storing."""
        fernet = Fernet(os.getenv('ENCRYPTION_KEY').encode())
        self.api_key = fernet.encrypt(api_key.encode()).decode()

    def decrypt_api_key(self) -> str:
        """Decrypt the stored API key."""
        fernet = Fernet(os.getenv('ENCRYPTION_KEY').encode())
        return fernet.decrypt(self.api_key.encode()).decode()

class ProviderModel(Base):
    """Model for storing available LLM providers and their models."""
    __tablename__ = 'provider_models'

    id = Column(Integer, primary_key=True)
    provider_name = Column(String(255), nullable=False)
    model_name = Column(String(255), nullable=False)
    description = Column(Text)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    class Config:
        """Sample configurations for different providers."""
        SUPPORTED_PROVIDERS = {
            "openai": {
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "base_url": "https://api.openai.com/v1"
            },
            "anthropic": {
                "models": ["claude-2", "claude-instant"],
                "base_url": "https://api.anthropic.com/v1"
            },
            "openrouter": {
                "models": [
                    "google/gemini-2.0-pro-exp-02-05:free",
                    "google/gemini-1.0-pro",
                    "anthropic/claude-2",
                    "openai/gpt-4"
                ],
                "base_url": "https://openrouter.ai/api/v1"
            }
        } 