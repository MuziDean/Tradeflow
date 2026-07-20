"""
Application service for Supplier.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import Supplier
from apps.retail.infrastructure.repositories import SupplierRepository
from shared.events.retail_events import (
    SupplierArchived,
    SupplierCreated,
    SupplierRestored,
    SupplierUpdated,
)

logger = logging.getLogger("tradeflow.retail")


class SupplierService:
    """Service for Supplier."""

    def __init__(self, supplier_repository: SupplierRepository):
        self.supplier_repository = supplier_repository

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[Supplier]:
        return self.supplier_repository.list_for_tenant(tenant_id, active_only)

    def get_by_id(self, supplier_id: str, tenant_id: str) -> Supplier | None:
        return self.supplier_repository.get_by_id(supplier_id, tenant_id)

    def create(self, supplier: Supplier) -> Supplier:
        with transaction.atomic():
            created = self.supplier_repository.create(supplier)
            SupplierCreated(
                tenant_id=supplier.tenant_id,
                supplier_id=created.id,
                name=created.name,
                code=created.code,
            ).emit()
            logger.info(f"Supplier created: {created.id} tenant={supplier.tenant_id}")
            return created

    def update(self, supplier: Supplier) -> Supplier:
        with transaction.atomic():
            updated = self.supplier_repository.update(supplier)
            SupplierUpdated(
                tenant_id=supplier.tenant_id,
                supplier_id=updated.id,
                name=updated.name,
            ).emit()
            logger.info(f"Supplier updated: {updated.id} tenant={supplier.tenant_id}")
            return updated

    def archive(self, supplier_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            success = self.supplier_repository.soft_delete(supplier_id, tenant_id)
            if success:
                SupplierArchived(tenant_id=tenant_id, supplier_id=supplier_id).emit()
                logger.info(f"Supplier archived: {supplier_id} tenant={tenant_id}")
            return success

    def restore(self, supplier_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            supplier = self.supplier_repository.get_by_id(supplier_id, tenant_id)
            if not supplier:
                return False
            updated = self.supplier_repository.update(
                Supplier(
                    id=supplier.id,
                    tenant_id=supplier.tenant_id,
                    name=supplier.name,
                    code=supplier.code,
                    email=supplier.email,
                    phone=supplier.phone,
                    website=supplier.website,
                    tax_number=supplier.tax_number,
                    payment_terms_days=supplier.payment_terms_days,
                    is_active=True,
                )
            )
            SupplierRestored(tenant_id=tenant_id, supplier_id=supplier_id).emit()
            logger.info(f"Supplier restored: {supplier_id} tenant={tenant_id}")
            return True