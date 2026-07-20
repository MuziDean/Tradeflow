"""
Application service for ProductBarcode.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import ProductBarcode
from apps.retail.infrastructure.repositories import ProductBarcodeRepository, ProductRepository
from shared.events.retail_events import BarcodeAssigned, BarcodeRemoved

logger = logging.getLogger("tradeflow.retail")


class ProductBarcodeService:
    """Service for ProductBarcode."""

    def __init__(self, barcode_repository: ProductBarcodeRepository, product_repository: ProductRepository):
        self.barcode_repository = barcode_repository
        self.product_repository = product_repository

    def get_by_barcode(self, barcode: str, tenant_id: str) -> ProductBarcode | None:
        return self.barcode_repository.get_by_barcode(barcode, tenant_id)

    def assign_barcode(self, barcode: ProductBarcode) -> ProductBarcode:
        with transaction.atomic():
            existing = self.barcode_repository.get_by_barcode(barcode.barcode, barcode.tenant_id)
            if existing:
                raise ValueError("Barcode already assigned.")
            created = self.barcode_repository.create(barcode)
            BarcodeAssigned(
                tenant_id=barcode.tenant_id,
                barcode_id=created.id,
                entity_type=barcode.entity_type,
                entity_id=barcode.entity_id,
                barcode=barcode.barcode,
            ).emit()
            logger.info(f"Barcode assigned: {created.barcode} entity={barcode.entity_id} tenant={barcode.tenant_id}")
            return created

    def remove_barcode(self, barcode_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            success = self.barcode_repository.delete(barcode_id, tenant_id)
            if success:
                BarcodeRemoved(tenant_id=tenant_id, barcode_id=barcode_id).emit()
                logger.info(f"Barcode removed: {barcode_id} tenant={tenant_id}")
            return success