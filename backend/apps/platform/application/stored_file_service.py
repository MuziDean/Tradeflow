"""
Application service for StoredFile metadata management.

No domain events emitted (file lifecycle managed by storage layer).
"""

import logging
from apps.platform.domain.entities import StoredFile
from apps.platform.infrastructure.repositories import StoredFileRepository

logger = logging.getLogger("tradeflow.platform")


class StoredFileService:
    """Service for StoredFile metadata management."""

    def __init__(self, stored_file_repository: StoredFileRepository):
        self.stored_file_repository = stored_file_repository

    def create_file(self, stored_file: StoredFile) -> StoredFile:
        created = self.stored_file_repository.create(stored_file)
        logger.info(
            "Stored file created: %s (entity=%s/%s, tenant=%s)",
            created.id,
            created.entity_type,
            created.entity_id,
            created.tenant_id,
        )
        return created

    def get_files_for_entity(
        self, tenant_id: str, entity_type: str, entity_id: str
    ) -> list[StoredFile]:
        files = self.stored_file_repository.get_by_entity(tenant_id, entity_type, entity_id)
        logger.debug(
            "Retrieved %d files for entity %s/%s (tenant=%s)",
            len(files),
            entity_type,
            entity_id,
            tenant_id,
        )
        return files
