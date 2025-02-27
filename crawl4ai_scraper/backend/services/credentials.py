from typing import Optional

from sqlmodel import Session, select

from ..models import Credentials
from ..utils.encryption import decrypt_value, encrypt_value, get_fernet

# Use the encryption module's Fernet instance
fernet = get_fernet()


class CredentialsService:
    """Service for managing LLM provider credentials."""

    def __init__(self, db: Session):
        """Initialize the service with a database session.

        Args:
            db (Session): SQLModel database session
        """
        self.db = db

    def create_credentials(
        self, provider: str, model: str, api_key: str
    ) -> Credentials:
        """Create new credentials and store them encrypted.

        Args:
            provider: Name of the LLM provider
            model: Name of the model
            api_key: API key to encrypt and store

        Returns:
            Credentials: The created credentials object
        """
        # Encrypt the API key
        encrypted_key = encrypt_value(api_key)

        # Deactivate any existing active credentials
        statement = select(Credentials).where(Credentials.is_active)
        active_creds = self.db.exec(statement).first()
        if active_creds:
            active_creds.is_active = False
            self.db.add(active_creds)

        # Create new credentials
        credentials = Credentials(
            provider=provider,
            model=model,
            api_key=encrypted_key,
            is_active=True,
        )
        self.db.add(credentials)
        self.db.commit()
        self.db.refresh(credentials)

        return credentials

    def get_active_credentials(self) -> Optional[Credentials]:
        """Get the currently active credentials.

        Returns:
            Optional[Credentials]: Active credentials if they exist
        """
        statement = select(Credentials).where(Credentials.is_active)
        return self.db.exec(statement).first()

    def decrypt_api_key(self, credentials: Credentials) -> Optional[str]:
        """Decrypt the API key from credentials.

        Args:
            credentials: Credentials object containing encrypted API key

        Returns:
            Optional[str]: Decrypted API key, or None if decryption fails
        """
        return decrypt_value(credentials.api_key)

    def deactivate_credentials(self, credentials_id: int) -> bool:
        """Deactivate specific credentials.

        Args:
            credentials_id: ID of credentials to deactivate

        Returns:
            bool: True if successful, False if credentials not found
        """
        statement = select(Credentials).where(Credentials.id == credentials_id)
        credentials = self.db.exec(statement).first()
        if not credentials:
            return False

        credentials.is_active = False
        self.db.add(credentials)
        self.db.commit()
        return True
