"""
Application service for PurchaseReturn.

Business rules:
- Draft return can be updated
- Approved return can be shipped to supplier
- Shipped return can be received and credited
- Full audit trail preserved
- Links back to original PurchaseOrder and GoodsReceipt
"""

import logging

from django.db import transaction

from apps.purchasing.domain.entities import PurchaseReturn, PurchaseReturnLine
from apps.purchasing.infrastructure.repositories import PurchaseReturnLineRepository, PurchaseReturnRepository
from shared.events.purchasing_events import PurchaseReturnApproved, PurchaseReturnCreated, PurchaseReturnCredited, PurchaseReturnShipped
from shared.types.enums import PurchaseReturnStatus
from shared.time.helpers import now

logger = logging.getLogger("tradeflow.purchasing")


class PurchaseReturnService:
    """Service for PurchaseReturn."""

    def __init__(self, return_repository: PurchaseReturnRepository,
                 line_repository: PurchaseReturnLineRepository):
        self.return_repository = return_repository
        self.line_repository = line_repository

    def list_for_supplier(self, tenant_id: str, supplier_id: str, status: str = "") -> list[PurchaseReturn]:
        return self.return_repository.list_for_tenant(tenant_id, status)

    def get_by_id(self, return_id: str, tenant_id: str) -> PurchaseReturn | None:
        return self.return_repository.get_by_id(return_id, tenant_id)

    def create(self, return_obj: PurchaseReturn, lines: list[PurchaseReturnLine]) -> PurchaseReturn:
        with transaction.atomic():
            created = self.return_repository.create(return_obj)
            for line in lines:
                line.purchase_return_id = created.id
                self.line_repository.create(line)
            PurchaseReturnCreated(
                tenant_id=return_obj.tenant_id,
                return_id=created.id,
                purchase_order_id=created.purchase_order_id,
                supplier_id=created.supplier_id,
            ).emit()
            logger.info(f"PurchaseReturn created: {created.id} tenant={return_obj.tenant_id}")
            return created

    def approve(self, return_id: str, tenant_id: str, approved_by: str) -> PurchaseReturn | None:
        with transaction.atomic():
            return_obj = self.return_repository.get_by_id(return_id, tenant_id)
            if not return_obj or return_obj.status != PurchaseReturnStatus.DRAFT:
                return None
            updated = self.return_repository.update(
                PurchaseReturn(
                    id=return_obj.id,
                    tenant_id=return_obj.tenant_id,
                    purchase_order_id=return_obj.purchase_order_id,
                    goods_receipt_id=return_obj.goods_receipt_id,
                    supplier_id=return_obj.supplier_id,
                    warehouse_id=return_obj.warehouse_id,
                    return_number=return_obj.return_number,
                    return_date=return_obj.return_date,
                    status=PurchaseReturnStatus.APPROVED,
                    total_amount=return_obj.total_amount,
                    currency=return_obj.currency,
                    approved_by=approved_by,
                    approved_at=now(),
                    received_at=return_obj.received_at,
                    credited_at=return_obj.credited_at,
                    notes=return_obj.notes,
                )
            )
            PurchaseReturnApproved(
                tenant_id=tenant_id,
                return_id=return_id,
                approved_by=approved_by,
            ).emit()
            logger.info(f"PurchaseReturn approved: {return_id} tenant={tenant_id}")
            return updated

    def ship(self, return_id: str, tenant_id: str) -> PurchaseReturn | None:
        with transaction.atomic():
            return_obj = self.return_repository.get_by_id(return_id, tenant_id)
            if not return_obj or return_obj.status != PurchaseReturnStatus.APPROVED:
                return None
            updated = self.return_repository.update(
                PurchaseReturn(
                    id=return_obj.id,
                    tenant_id=return_obj.tenant_id,
                    purchase_order_id=return_obj.purchase_order_id,
                    goods_receipt_id=return_obj.goods_receipt_id,
                    supplier_id=return_obj.supplier_id,
                    warehouse_id=return_obj.warehouse_id,
                    return_number=return_obj.return_number,
                    return_date=return_obj.return_date,
                    status=PurchaseReturnStatus.SHIPPED,
                    total_amount=return_obj.total_amount,
                    currency=return_obj.currency,
                    approved_by=return_obj.approved_by,
                    approved_at=return_obj.approved_at,
                    received_at=return_obj.received_at,
                    credited_at=return_obj.credited_at,
                    notes=return_obj.notes,
                )
            )
            PurchaseReturnShipped(
                tenant_id=tenant_id,
                return_id=return_id,
                supplier_id=return_obj.supplier_id,
            ).emit()
            logger.info(f"PurchaseReturn shipped: {return_id} tenant={tenant_id}")
            return updated

    def receive_credit(self, return_id: str, tenant_id: str) -> PurchaseReturn | None:
        with transaction.atomic():
            return_obj = self.return_repository.get_by_id(return_id, tenant_id)
            if not return_obj or return_obj.status != PurchaseReturnStatus.SHIPPED:
                return None
            updated = self.return_repository.update(
                PurchaseReturn(
                    id=return_obj.id,
                    tenant_id=return_obj.tenant_id,
                    purchase_order_id=return_obj.purchase_order_id,
                    goods_receipt_id=return_obj.goods_receipt_id,
                    supplier_id=return_obj.supplier_id,
                    warehouse_id=return_obj.warehouse_id,
                    return_number=return_obj.return_number,
                    return_date=return_obj.return_date,
                    status=PurchaseReturnStatus.CREDITED,
                    total_amount=return_obj.total_amount,
                    currency=return_obj.currency,
                    approved_by=return_obj.approved_by,
                    approved_at=return_obj.approved_at,
                    received_at=now(),
                    credited_at=now(),
                    notes=return_obj.notes,
                )
            )
            PurchaseReturnCredited(
                tenant_id=tenant_id,
                return_id=return_id,
                supplier_id=return_obj.supplier_id,
            ).emit()
            logger.info(f"PurchaseReturn credited: {return_id} tenant={tenant_id}")
            return updated

    def cancel(self, return_id: str, tenant_id: str) -> PurchaseReturn | None:
        with transaction.atomic():
            return_obj = self.return_repository.get_by_id(return_id, tenant_id)
            if not return_obj or return_obj.status != PurchaseReturnStatus.DRAFT:
                return None
            updated = self.return_repository.update(
                PurchaseReturn(
                    id=return_obj.id,
                    tenant_id=return_obj.tenant_id,
                    purchase_order_id=return_obj.purchase_order_id,
                    goods_receipt_id=return_obj.goods_receipt_id,
                    supplier_id=return_obj.supplier_id,
                    warehouse_id=return_obj.warehouse_id,
                    return_number=return_obj.return_number,
                    return_date=return_obj.return_date,
                    status=PurchaseReturnStatus.CANCELLED,
                    total_amount=return_obj.total_amount,
                    currency=return_obj.currency,
                    approved_by=return_obj.approved_by,
                    approved_at=return_obj.approved_at,
                    received_at=return_obj.received_at,
                    credited_at=return_obj.credited_at,
                    notes=return_obj.notes,
                )
            )
            logger.info(f"PurchaseReturn cancelled: {return_id} tenant={tenant_id}")
            return updated