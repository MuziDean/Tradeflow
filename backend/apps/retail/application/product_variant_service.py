"""
Application service for ProductVariant.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import ProductVariant
from apps.retail.infrastructure.repositories import ProductVariantRepository
from shared.events.retail_events import (
    ProductVariantArchived,
    ProductVariantCreated,
    ProductVariantUpdated,
)

logger = logging.getLogger("tradeflow.retail")


class ProductVariantService:
    """Service for ProductVariant."""

    def __init__(self, variant_repository: ProductVariantRepository):
        self.variant_repository = variant_repository

    def list_for_product(self, tenant_id: str, product_id: str) -> list[ProductVariant]:
        return self.variant_repository.list_for_product(tenant_id, product_id)

    def get_by_id(self, variant_id: str, tenant_id: str) -> ProductVariant | None:
        return self.variant_repository.get_by_id(variant_id, tenant_id)

    def create(self, variant: ProductVariant) -> ProductVariant:
        with transaction.atomic():
            created = self.variant_repository.create(variant)
            ProductVariantCreated(
                tenant_id=variant.tenant_id,
                variant_id=created.id,
                product_id=created.product_id,
                sku=created.sku,
            ).emit()
            logger.info(f"ProductVariant created: {created.id} tenant={variant.tenant_id}")
            return created

    def update(self, variant: ProductVariant) -> ProductVariant:
        with transaction.atomic():
            updated = self.variant_repository.update(variant)
            ProductVariantUpdated(
                tenant_id=variant.tenant_id,
                variant_id=updated.id,
                sku=updated.sku,
            ).emit()
            logger.info(f"ProductVariant updated: {updated.id} tenant={variant.tenant_id}")
            return updated

    def archive(self, variant_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            success = self.variant_repository.soft_delete(variant_id, tenant_id)
            if success:
                ProductVariantArchived(tenant_id=tenant_id, variant_id=variant_id).emit()
                logger.info(f"ProductVariant archived: {variant_id} tenant={tenant_id}")
            return success