"""
Application service for ProductCategory.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import ProductCategory
from apps.retail.infrastructure.repositories import ProductCategoryRepository
from shared.events.retail_events import (
    CategoryArchived,
    CategoryCreated,
    CategoryRestored,
    CategoryUpdated,
)

logger = logging.getLogger("tradeflow.retail")


class ProductCategoryService:
    """Service for ProductCategory."""

    def __init__(self, category_repository: ProductCategoryRepository):
        self.category_repository = category_repository

    def list_for_tenant(self, tenant_id: str, parent_id: str | None = None) -> list[ProductCategory]:
        return self.category_repository.list_for_tenant(tenant_id, parent_id)

    def get_by_id(self, category_id: str, tenant_id: str) -> ProductCategory | None:
        return self.category_repository.get_by_id(category_id, tenant_id)

    def create(self, category: ProductCategory) -> ProductCategory:
        with transaction.atomic():
            created = self.category_repository.create(category)
            CategoryCreated(
                tenant_id=category.tenant_id,
                category_id=created.id,
                name=created.name,
            ).emit()
            logger.info(f"ProductCategory created: {created.id} tenant={category.tenant_id}")
            return created

    def update(self, category: ProductCategory) -> ProductCategory:
        with transaction.atomic():
            updated = self.category_repository.update(category)
            CategoryUpdated(
                tenant_id=category.tenant_id,
                category_id=updated.id,
                name=updated.name,
            ).emit()
            logger.info(f"ProductCategory updated: {updated.id} tenant={category.tenant_id}")
            return updated

    def archive(self, category_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            children = self.category_repository.list_for_tenant(tenant_id, parent_id=category_id)
            if children:
                raise ValueError("Cannot archive category with active child categories.")
            success = self.category_repository.soft_delete(category_id, tenant_id)
            if success:
                CategoryArchived(tenant_id=tenant_id, category_id=category_id).emit()
                logger.info(f"ProductCategory archived: {category_id} tenant={tenant_id}")
            return success

    def restore(self, category_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            category = self.category_repository.get_by_id(category_id, tenant_id)
            if not category:
                return False
            updated = self.category_repository.update(
                ProductCategory(
                    id=category.id,
                    tenant_id=category.tenant_id,
                    name=category.name,
                    description=category.description,
                    parent_id=category.parent_id,
                    image_path=category.image_path,
                    sort_order=category.sort_order,
                    is_active=True,
                )
            )
            CategoryRestored(tenant_id=tenant_id, category_id=category_id).emit()
            logger.info(f"ProductCategory restored: {category_id} tenant={tenant_id}")
            return True