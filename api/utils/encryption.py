"""
Field-level encryption for PII data using AES-256-GCM.

This module provides:
- AES-256-GCM authenticated encryption
- Custom SQLAlchemy type for transparent encryption/decryption
- Key derivation from environment variable
"""
import os
import base64
import hashlib
from typing import Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from sqlalchemy import String, TypeDecorator


# Encryption key from environment
_ENCRYPTION_KEY: bytes | None = None


def _get_encryption_key() -> bytes:
    """
    Get or derive the 32-byte encryption key from environment.

    The key is cached after first derivation.
    Raises ValueError if ENCRYPTION_KEY is not set.
    """
    global _ENCRYPTION_KEY

    if _ENCRYPTION_KEY is not None:
        return _ENCRYPTION_KEY

    key_material = os.getenv("ENCRYPTION_KEY", "")

    if not key_material:
        raise ValueError(
            "ENCRYPTION_KEY environment variable is not set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )

    # Derive a consistent 32-byte key using SHA-256
    # This allows any length input key while ensuring 256-bit AES key
    _ENCRYPTION_KEY = hashlib.sha256(key_material.encode()).digest()

    return _ENCRYPTION_KEY


def encrypt_value(plaintext: str) -> str:
    """
    Encrypt a string value using AES-256-GCM.

    Args:
        plaintext: The string to encrypt

    Returns:
        Base64-encoded string containing: nonce (12 bytes) + ciphertext + tag (16 bytes)
    """
    if not plaintext:
        return plaintext

    key = _get_encryption_key()
    aesgcm = AESGCM(key)

    # Generate random 96-bit nonce (recommended for GCM)
    nonce = os.urandom(12)

    # Encrypt (GCM automatically appends 16-byte auth tag)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)

    # Combine nonce + ciphertext for storage
    encrypted_data = nonce + ciphertext

    # Base64 encode for safe string storage
    return base64.b64encode(encrypted_data).decode('ascii')


def decrypt_value(encrypted: str) -> str:
    """
    Decrypt a value encrypted with encrypt_value().

    Args:
        encrypted: Base64-encoded encrypted string

    Returns:
        Original plaintext string

    Raises:
        ValueError: If decryption fails (wrong key or corrupted data)
    """
    if not encrypted:
        return encrypted

    try:
        key = _get_encryption_key()
        aesgcm = AESGCM(key)

        # Decode from base64
        encrypted_data = base64.b64decode(encrypted.encode('ascii'))

        # Extract nonce (first 12 bytes) and ciphertext
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        # Decrypt and verify
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext.decode('utf-8')

    except InvalidTag:
        raise ValueError("Decryption failed: invalid key or corrupted data")
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")


def is_encrypted(value: str) -> bool:
    """
    Check if a value appears to be encrypted.

    Encrypted values are base64-encoded and have a minimum length
    (12 bytes nonce + 16 bytes tag + at least 1 byte ciphertext = 29 bytes min).

    This is a heuristic check, not cryptographically guaranteed.
    """
    if not value or len(value) < 40:  # base64 of 29 bytes = ~40 chars
        return False

    try:
        decoded = base64.b64decode(value.encode('ascii'))
        # Minimum: 12 (nonce) + 16 (tag) + 1 (min ciphertext) = 29 bytes
        return len(decoded) >= 29
    except Exception:
        return False


class EncryptedString(TypeDecorator):
    """
    SQLAlchemy type that transparently encrypts/decrypts string values.

    Usage:
        class MyModel(Base):
            sensitive_field: Mapped[str | None] = mapped_column(EncryptedString(255))

    The encrypted value is stored as base64, so the column should be sized
    appropriately (roughly 1.4x the max plaintext length + 40 chars overhead).
    """
    impl = String
    cache_ok = True

    def __init__(self, length: int = None):
        """
        Initialize with optional max length.

        Args:
            length: Maximum length of the encrypted value in the database.
                   Should be larger than plaintext max to accommodate encryption overhead.
                   Rule of thumb: (plaintext_max * 1.4) + 50
        """
        if length:
            # Increase length to accommodate base64 encoding + nonce + tag
            # Formula: ceil((plaintext + 12 + 16) * 4/3) + padding
            super().__init__(length)
        else:
            super().__init__()

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """Encrypt value before storing in database."""
        if value is None:
            return None

        # Skip if already encrypted (for idempotency during migrations)
        if is_encrypted(value):
            return value

        return encrypt_value(value)

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """Decrypt value when reading from database."""
        if value is None:
            return None

        # Handle unencrypted legacy data gracefully
        if not is_encrypted(value):
            return value

        try:
            return decrypt_value(value)
        except ValueError:
            # If decryption fails, return as-is (might be legacy unencrypted data)
            return value


class EncryptedText(TypeDecorator):
    """
    SQLAlchemy type for encrypting Text fields (unlimited length).

    Same as EncryptedString but uses Text as the underlying type.
    """
    impl = String  # Will be overridden
    cache_ok = True

    def load_dialect_impl(self, dialect):
        from sqlalchemy import Text
        return dialect.type_descriptor(Text())

    def process_bind_param(self, value: str | None, dialect) -> str | None:
        """Encrypt value before storing in database."""
        if value is None:
            return None

        if is_encrypted(value):
            return value

        return encrypt_value(value)

    def process_result_value(self, value: str | None, dialect) -> str | None:
        """Decrypt value when reading from database."""
        if value is None:
            return None

        if not is_encrypted(value):
            return value

        try:
            return decrypt_value(value)
        except ValueError:
            return value
