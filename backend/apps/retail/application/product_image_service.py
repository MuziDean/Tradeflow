"""
Application service for ProductImage.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import ProductImage
from apps.retail.infrastructure.repositories import ProductImageRepository
from shared.events.retail_events import ImageAdded, ImageRemoved, PrimaryImageSet

logger = logging.getLogger("tradeflow.retail")


class ProductImageService:
    """Service for ProductImage."""

    def __init__(self, image_repository: ProductImageRepository):
        self.image_repository = image_repository

    def list_for_product(self, tenant_id: str, product_id: str) -> list[ProductImage]:
        return self.image_repository.list_for_product(tenant_id, product_id)

    def add_image(self, image: ProductImage) -> ProductImage:
        with transaction.atomic():
            created = self.image_repository.create(image)
            ImageAdded(
                tenant_id=image.tenant_id,
                image_id=created.id,
                product_id=created.product_id,
            ).emit()
            logger.info(f"ProductImage added: {created.id} tenant={image.tenant_id}")
            return created

    def set_primary(self, image_id: str, tenant_id: str, product_id: str) -> bool:
        with transaction.atomic():
            images = self.image_repository.list_for_product(tenant_id, product_id)
            # Unset is_primary on all other images
            for img in images:
                if img.id != image_id and img.is_primary:
                    self.image_repository.unset_primary(img.id, tenant_id)
            # Find and return the new primary image
            target = next((img for img in images if img.id == image_id), None)
            if not target:
                return False
            updated = self.image_repository.update(
                ProductImage(
                    id=target.id,
                    tenant_id=target.tenant_id,
                    product_id=target.product_id,
                    variant_id=target.variant_id,
                    storage_provider=target.storage_provider,
                    storage_path=target.storage_path,
                    original_filename=target.original_filename,
                    mime_type=target.mime_type,
                    file_size=target.file_size,
                    sort_order=target.sort_order,
                    is_primary=True,
                )
            )
            PrimaryImageSet(
                tenant_id=tenant_id,
                product_id=product_id,
                image_id=image_id,
            ).emit()
            logger.info(f"Primary image set: {image_id} tenant={tenant_id}")
            return True

    def remove_image(self, image_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            success = self.image_repository.delete(image_id, tenant_id)
            if success:
                ImageRemoved(tenant_id=tenant_id, image_id=image_id).emit()
                logger.info(f"ProductImage removed: {image_id} tenant={tenant_id}")
            return success