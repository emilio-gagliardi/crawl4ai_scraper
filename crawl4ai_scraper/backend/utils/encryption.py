"""Encryption utilities for sensitive data."""

import base64
import os
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Get encryption key from environment or generate one
def get_encryption_key() -> bytes:
    """Get or generate the encryption key."""
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        # Generate a new key if none exists
        key = Fernet.generate_key()
        # Save the key to .env file
        with open(".env", "a") as f:
            f.write(f"\nENCRYPTION_KEY={key.decode()}")
    else:
        # Ensure the key is properly formatted
        try:
            # Try to decode and re-encode to validate format
            key_bytes = key.encode() if isinstance(key, str) else key
            Fernet(key_bytes)  # This will raise an error if the key is invalid
            key = key_bytes
        except Exception:
            # If the key is invalid, generate a new one
            key = Fernet.generate_key()
            # Save the key to .env file
            with open(".env", "a") as f:
                f.write(f"\nENCRYPTION_KEY={key.decode()}")

    return key


# Initialize Fernet cipher with the key
_fernet = Fernet(get_encryption_key())


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value.

    Args:
        value: The string to encrypt

    Returns:
        str: The encrypted value as a base64 string
    """
    if not value:
        return ""
    return _fernet.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> Optional[str]:
    """
    Decrypt an encrypted string value.

    Args:
        encrypted_value: The encrypted string to decrypt

    Returns:
        Optional[str]: The decrypted value, or None if decryption fails
    """
    if not encrypted_value:
        return None
    try:
        return _fernet.decrypt(encrypted_value.encode()).decode()
    except Exception:
        return None
