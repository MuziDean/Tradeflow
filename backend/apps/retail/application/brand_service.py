"""
Application service for Brand.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import Brand
from apps.retail.infrastructure.repositories import BrandRepository
from shared.events.retail_events import (
    BrandArchived,
    BrandCreated,
    BrandRestored,
    BrandUpdated,
)

logger = logging.getLogger("tradeflow.retail")


class BrandService:
    """Service for Brand."""

    def __init__(self, brand_repository: BrandRepository):
        self.brand_repository = brand_repository

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[Brand]:
        return self.brand_repository.list_for_tenant(tenant_id, active_only)

    def get_by_id(self, brand_id: str, tenant_id: str) -> Brand | None:
        return self.brand_repository.get_by_id(brand_id, tenant_id)

    def create(self, brand: Brand) -> Brand:
        with transaction.atomic():
            created = self.brand_repository.create(brand)
            BrandCreated(
                tenant_id=brand.tenant_id,
                brand_id=created.id,
                name=created.name,
            ).emit()
            logger.info(f"Brand created: {created.id} tenant={brand.tenant_id}")
            return created

    def update(self, brand: Brand) -> Brand:
        with transaction.atomic():
            updated = self.brand_repository.update(brand)
            BrandUpdated(
                tenant_id=brand.tenant_id,
                brand_id=updated.id,
                name=updated.name,
            ).emit()
            logger.info(f"Brand updated: {updated.id} tenant={brand.tenant_id}")
            return updated

    def archive(self, brand_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            success = self.brand_repository.soft_delete(brand_id, tenant_id)
            if success:
                BrandArchived(tenant_id=tenant_id, brand_id=brand_id).emit()
                logger.info(f"Brand archived: {brand_id} tenant={tenant_id}")
            return success

    def restore(self, brand_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            brand = self.brand_repository.get_by_id(brand_id, tenant_id)
            if not brand:
                return False
            updated = self.brand_repository.update(
                Brand(
                    id=brand.id,
                    tenant_id=brand.tenant_id,
                    name=brand.name,
                    description=brand.description,
                    website=brand.website,
                    logo_path=brand.logo_path,
                    is_active=True,
                )
            )
            BrandRestored(tenant_id=tenant_id, brand_id=brand_id).emit()
            logger.info(f"Brand restored: {brand_id} tenant={tenant_id}")
            return True