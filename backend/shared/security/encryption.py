"""
Field-level encryption utilities for TradeFlow.

Per Security Architecture: AES-256 encryption for sensitive fields
(ID numbers, banking details, salaries, 2FA secrets).

Uses cryptography.fernet for symmetric encryption.
"""

import os

from cryptography.fernet import Fernet


class EncryptionError(Exception):
    """Raised when encryption/decryption fails."""


class FieldEncryption:
    """
    Provides field-level encryption for sensitive data.

    Usage:
        encryption = FieldEncryption()
        encrypted = encryption.encrypt("1234567890123")
        decrypted = encryption.decrypt(encrypted)
    """

    def __init__(self):
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            # Development fallback (generate deterministic key from secret key)
            import hashlib
            from django.conf import settings
            key_material = settings.SECRET_KEY + "tradeflow-encryption"
            key = hashlib.sha256(key_material.encode()).digest()
            import base64
            key = base64.urlsafe_b64encode(key)

        self.cipher = Fernet(key)

    def encrypt(self, value: str) -> str:
        """Encrypt a string value."""
        if not value:
            return value
        try:
            return self.cipher.encrypt(value.encode()).decode()
        except Exception as exc:
            raise EncryptionError(f"Encryption failed: {exc}") from exc

    def decrypt(self, value: str) -> str:
        """Decrypt an encrypted string value."""
        if not value:
            return value
        try:
            return self.cipher.decrypt(value.encode()).decode()
        except Exception as exc:
            raise EncryptionError(f"Decryption failed: {exc}") from exc