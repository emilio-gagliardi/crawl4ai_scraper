"""Encryption utilities for sensitive data."""

import os
from typing import Optional

from cryptography.fernet import Fernet

# Global variable to store the encryption key
_encryption_key = None

# Global variable to store the Fernet instance
_fernet = None


def get_encryption_key() -> bytes:
    """
    Get the encryption key from the environment or generate a new one.

    Returns:
        bytes: The encryption key
    """
    global _encryption_key

    # If we already have the key, return it
    if _encryption_key:
        return _encryption_key

    # Try to get the key from the environment
    key_str = os.getenv("ENCRYPTION_KEY")
    if key_str:
        _encryption_key = key_str.encode()
        return _encryption_key

    # Generate a new key
    _encryption_key = Fernet.generate_key()

    # Store the key in the environment
    os.environ["ENCRYPTION_KEY"] = _encryption_key.decode()

    return _encryption_key


def get_fernet() -> Fernet:
    """
    Get a Fernet instance for encryption/decryption.

    Returns:
        Fernet: A Fernet instance
    """
    global _fernet

    # If we already have a Fernet instance, return it
    if _fernet:
        return _fernet

    # Create a new Fernet instance
    key = get_encryption_key()
    _fernet = Fernet(key)

    return _fernet


def encrypt_value(value: str) -> str:
    """
    Encrypt a string value.

    Args:
        value: The string to encrypt

    Returns:
        str: The encrypted string
    """
    if not value:
        return value

    fernet = get_fernet()
    encrypted = fernet.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(value: str) -> Optional[str]:
    """
    Decrypt an encrypted string value.

    Args:
        value: The encrypted string

    Returns:
        str: The decrypted string, or None if decryption fails
    """
    if not value:
        return value

    try:
        fernet = get_fernet()
        decrypted = fernet.decrypt(value.encode())
        return decrypted.decode()
    except Exception:
        return None
