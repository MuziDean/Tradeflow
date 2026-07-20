"""
Application service for GoodsReceipt.

Business rules:
- Draft receipt can be updated
- Posted receipt updates inventory via domain event
- Cancelled receipt reverts inventory
- Partial receipts supported (multiple GRNs per PO)
- Full audit trail preserved

IMPORTANT: This service does NOT directly update Inventory.
It emits GoodsReceiptPosted event. Inventory module subscribes.
"""

import logging

from django.db import transaction

from apps.purchasing.domain.entities import GoodsReceipt, GoodsReceiptLine
from apps.purchasing.infrastructure.repositories import GoodsReceiptLineRepository, GoodsReceiptRepository
from shared.events.purchasing_events import GoodsReceiptCancelled, GoodsReceiptCreated, GoodsReceiptPosted
from shared.types.enums import GoodsReceiptStatus
from shared.time.helpers import now

logger = logging.getLogger("tradeflow.purchasing")


class GoodsReceiptService:
    """Service for GoodsReceipt."""

    def __init__(self, receipt_repository: GoodsReceiptRepository,
                 line_repository: GoodsReceiptLineRepository):
        self.receipt_repository = receipt_repository
        self.line_repository = line_repository

    def list_for_purchase_order(self, tenant_id: str, purchase_order_id: str, status: str = "") -> list[GoodsReceipt]:
        return self.receipt_repository.list_for_tenant(tenant_id, status)

    def get_by_id(self, receipt_id: str, tenant_id: str) -> GoodsReceipt | None:
        return self.receipt_repository.get_by_id(receipt_id, tenant_id)

    def create(self, receipt: GoodsReceipt, lines: list[GoodsReceiptLine]) -> GoodsReceipt:
        with transaction.atomic():
            created = self.receipt_repository.create(receipt)
            for line in lines:
                line.goods_receipt_id = created.id
                self.line_repository.create(line)
            GoodsReceiptCreated(
                tenant_id=receipt.tenant_id,
                receipt_id=created.id,
                purchase_order_id=created.purchase_order_id,
                warehouse_id=created.warehouse_id,
            ).emit()
            logger.info(f"GoodsReceipt created: {created.id} tenant={receipt.tenant_id}")
            return created

    def receive(self, receipt_id: str, tenant_id: str, posted_by: str) -> GoodsReceipt | None:
        """Post a goods receipt. Emits GoodsReceiptPosted event for Inventory to consume."""
        with transaction.atomic():
            receipt = self.receipt_repository.get_by_id(receipt_id, tenant_id)
            if not receipt or receipt.status != GoodsReceiptStatus.DRAFT:
                return None
            updated = self.receipt_repository.update(
                GoodsReceipt(
                    id=receipt.id,
                    tenant_id=receipt.tenant_id,
                    purchase_order_id=receipt.purchase_order_id,
                    warehouse_id=receipt.warehouse_id,
                    receipt_number=receipt.receipt_number,
                    receipt_date=receipt.receipt_date,
                    status=GoodsReceiptStatus.POSTED,
                    posted_by=posted_by,
                    posted_at=now(),
                    notes=receipt.notes,
                )
            )
            GoodsReceiptPosted(
                tenant_id=tenant_id,
                receipt_id=receipt_id,
                purchase_order_id=receipt.purchase_order_id,
                warehouse_id=receipt.warehouse_id,
                posted_by=posted_by,
            ).emit()
            logger.info(f"GoodsReceipt posted: {receipt_id} tenant={tenant_id}")
            return updated

    def cancel(self, receipt_id: str, tenant_id: str, reason: str = "") -> GoodsReceipt | None:
        with transaction.atomic():
            receipt = self.receipt_repository.get_by_id(receipt_id, tenant_id)
            if not receipt or receipt.status != GoodsReceiptStatus.DRAFT:
                return None
            updated = self.receipt_repository.update(
                GoodsReceipt(
                    id=receipt.id,
                    tenant_id=receipt.tenant_id,
                    purchase_order_id=receipt.purchase_order_id,
                    warehouse_id=receipt.warehouse_id,
                    receipt_number=receipt.receipt_number,
                    receipt_date=receipt.receipt_date,
                    status=GoodsReceiptStatus.CANCELLED,
                    posted_by=receipt.posted_by,
                    posted_at=receipt.posted_at,
                    notes=f"{receipt.notes}\nCancelled: {reason}" if reason else receipt.notes,
                )
            )
            GoodsReceiptCancelled(
                tenant_id=tenant_id,
                receipt_id=receipt_id,
                reason=reason,
            ).emit()
            logger.info(f"GoodsReceipt cancelled: {receipt_id} tenant={tenant_id}")
            return updated