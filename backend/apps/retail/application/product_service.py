"""
Application service for Product.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import Product
from apps.retail.infrastructure.repositories import ProductBarcodeRepository, ProductRepository
from shared.events.retail_events import (
    ProductArchived,
    ProductCreated,
    ProductDeactivated,
    ProductUpdated,
    ProductActivated,
)

logger = logging.getLogger("tradeflow.retail")


class ProductService:
    """Service for Product."""

    def __init__(self, product_repository: ProductRepository):
        self.product_repository = product_repository

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[Product]:
        return self.product_repository.list_for_tenant(tenant_id, active_only)

    def get_by_id(self, product_id: str, tenant_id: str) -> Product | None:
        return self.product_repository.get_by_id(product_id, tenant_id)

    def get_by_sku(self, sku: str, tenant_id: str) -> Product | None:
        return self.product_repository.get_by_sku(sku, tenant_id)

    def get_by_barcode(self, barcode: str, tenant_id: str) -> Product | None:
        barcode_repo = ProductBarcodeRepository()
        barcode_entity = barcode_repo.get_by_barcode(barcode, tenant_id)
        if barcode_entity and barcode_entity.entity_type == "product":
            return self.product_repository.get_by_id(barcode_entity.entity_id, tenant_id)
        return self.product_repository.get_by_barcode(barcode, tenant_id)

    def create(self, product: Product) -> Product:
        with transaction.atomic():
            created = self.product_repository.create(product)
            ProductCreated(
                tenant_id=product.tenant_id,
                product_id=created.id,
                sku=created.sku,
                name=created.name,
            ).emit()
            logger.info(f"Product created: {created.id} tenant={product.tenant_id}")
            return created

    def update(self, product: Product) -> Product:
        with transaction.atomic():
            updated = self.product_repository.update(product)
            ProductUpdated(
                tenant_id=product.tenant_id,
                product_id=updated.id,
                sku=updated.sku,
            ).emit()
            logger.info(f"Product updated: {updated.id} tenant={product.tenant_id}")
            return updated

    def archive(self, product_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            product = self.product_repository.get_by_id(product_id, tenant_id)
            if not product:
                return False
            success = self.product_repository.soft_delete(product_id, tenant_id)
            if success:
                ProductArchived(tenant_id=tenant_id, product_id=product_id).emit()
                logger.info(f"Product archived: {product_id} tenant={tenant_id}")
            return success

    def activate(self, product_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            product = self.product_repository.get_by_id(product_id, tenant_id)
            if not product:
                return False
            updated = self.product_repository.update(
                Product(
                    id=product.id,
                    tenant_id=product.tenant_id,
                    sku=product.sku,
                    name=product.name,
                    description=product.description,
                    brand_id=product.brand_id,
                    category_id=product.category_id,
                    unit_of_measure_id=product.unit_of_measure_id,
                    barcode=product.barcode,
                    status=product.status,
                    is_trackable=product.is_trackable,
                    is_serialized=product.is_serialized,
                    is_batched=product.is_batched,
                    attributes=product.attributes,
                    is_active=True,
                )
            )
            ProductActivated(tenant_id=tenant_id, product_id=product_id).emit()
            logger.info(f"Product activated: {product_id} tenant={tenant_id}")
            return True

    def deactivate(self, product_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            product = self.product_repository.get_by_id(product_id, tenant_id)
            if not product:
                return False
            updated = self.product_repository.update(
                Product(
                    id=product.id,
                    tenant_id=product.tenant_id,
                    sku=product.sku,
                    name=product.name,
                    description=product.description,
                    brand_id=product.brand_id,
                    category_id=product.category_id,
                    unit_of_measure_id=product.unit_of_measure_id,
                    barcode=product.barcode,
                    status=product.status,
                    is_trackable=product.is_trackable,
                    is_serialized=product.is_serialized,
                    is_batched=product.is_batched,
                    attributes=product.attributes,
                    is_active=False,
                )
            )
            ProductDeactivated(tenant_id=tenant_id, product_id=product_id).emit()
            logger.info(f"Product deactivated: {product_id} tenant={tenant_id}")
            return True