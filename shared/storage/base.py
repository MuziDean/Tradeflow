"""
Storage abstraction for TradeFlow.

Per Backend Engineering Standards Section 14: Storage abstraction layer
so providers can change (AWS S3, MinIO, etc.) without touching business code.
"""

from abc import ABC, abstractmethod
from typing import Optional


class StorageBackend(ABC):
    """Abstract storage backend interface."""

    @abstractmethod
    def upload(self, path: str, data: bytes, content_type: str) -> str:
        """Upload data and return the accessible URL."""
        pass

    @abstractmethod
    def download(self, path: str) -> bytes:
        """Download data from storage."""
        pass

    @abstractmethod
    def delete(self, path: str) -> bool:
        """Delete a file from storage."""
        pass

    @abstractmethod
    def exists(self, path: str) -> bool:
        """Check if a file exists."""
        pass

    @abstractmethod
    def signed_url(self, path: str, expiry: int = 900) -> str:
        """Generate a signed URL for temporary access."""
        pass


class S3StorageBackend(StorageBackend):
    """S3-compatible storage implementation."""

    def upload(self, path: str, data: bytes, content_type: str) -> str:
        # Phase 1: Implement with boto3
        raise NotImplementedError("S3StorageBackend.upload() not yet implemented")

    def download(self, path: str) -> bytes:
        raise NotImplementedError("S3StorageBackend.download() not yet implemented")

    def delete(self, path: str) -> bool:
        raise NotImplementedError("S3StorageBackend.delete() not yet implemented")

    def exists(self, path: str) -> bool:
        raise NotImplementedError("S3StorageBackend.exists() not yet implemented")

    def signed_url(self, path: str, expiry: int = 900) -> str:
        raise NotImplementedError("S3StorageBackend.signed_url() not yet implemented")