"""
Application service for StoredFile metadata management.

No domain events emitted (file lifecycle managed by storage layer).
"""

from apps.platform.domain.entities import StoredFile
from apps.platform.infrastructure.repositories import StoredFileRepository


class StoredFileService:
    """Service for StoredFile metadata management."""

    def __init__(self, stored_file_repository: StoredFileRepository):
        self.stored_file_repository = stored_file_repository

    def create_file(self, stored_file: StoredFile) -> StoredFile:
        return self.stored_file_repository.create(stored_file)

    def get_files_for_entity(
        self, tenant_id: str, entity_type: str, entity_id: str
    ) -> list[StoredFile]:
        return self.stored_file_repository.get_by_entity(tenant_id, entity_type, entity_id)