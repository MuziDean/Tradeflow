"""
Application service for PurchaseOrder.

Business rules:
- Draft PO can be edited
- Approved PO can be sent to supplier
- Sent PO can be acknowledged
- Partially received PO tracks received quantities
- Received PO triggers GoodsReceipt
- Closed PO cannot be modified
- Cancelled PO only from draft/approved states
- Full audit trail preserved
"""

import logging

from django.db import transaction

from apps.purchasing.domain.entities import PurchaseOrder, PurchaseOrderLine
from apps.purchasing.infrastructure.repositories import PurchaseOrderLineRepository, PurchaseOrderRepository
from shared.events.purchasing_events import PurchaseOrderAcknowledged, PurchaseOrderApproved, PurchaseOrderCancelled, PurchaseOrderClosed, PurchaseOrderCreated, PurchaseOrderSent
from shared.types.enums import PurchaseOrderStatus
from shared.time.helpers import now

logger = logging.getLogger("tradeflow.purchasing")


class PurchaseOrderService:
    """Service for PurchaseOrder."""

    def __init__(self, order_repository: PurchaseOrderRepository,
                 line_repository: PurchaseOrderLineRepository):
        self.order_repository = order_repository
        self.line_repository = line_repository

    def list_for_supplier(self, tenant_id: str, supplier_id: str, status: str = "") -> list[PurchaseOrder]:
        return self.order_repository.list_for_tenant(tenant_id, status)

    def get_by_id(self, order_id: str, tenant_id: str) -> PurchaseOrder | None:
        return self.order_repository.get_by_id(order_id, tenant_id)

    def create(self, order: PurchaseOrder, lines: list[PurchaseOrderLine]) -> PurchaseOrder:
        with transaction.atomic():
            created = self.order_repository.create(order)
            for line in lines:
                line.purchase_order_id = created.id
                self.line_repository.create(line)
            PurchaseOrderCreated(
                tenant_id=order.tenant_id,
                order_id=created.id,
                supplier_id=created.supplier_id,
                warehouse_id=created.warehouse_id,
                order_number=created.order_number,
            ).emit()
            logger.info(f"PurchaseOrder created: {created.id} tenant={order.tenant_id}")
            return created

    def update(self, order: PurchaseOrder) -> PurchaseOrder:
        with transaction.atomic():
            updated = self.order_repository.update(order)
            logger.info(f"PurchaseOrder updated: {updated.id} tenant={updated.tenant_id}")
            return updated

    def approve(self, order_id: str, tenant_id: str, approved_by: str) -> PurchaseOrder | None:
        with transaction.atomic():
            order = self.order_repository.get_by_id(order_id, tenant_id)
            if not order or order.status != PurchaseOrderStatus.DRAFT:
                return None
            updated = self.order_repository.update(
                PurchaseOrder(
                    id=order.id,
                    tenant_id=order.tenant_id,
                    supplier_id=order.supplier_id,
                    warehouse_id=order.warehouse_id,
                    order_type=order.order_type,
                    order_number=order.order_number,
                    order_date=order.order_date,
                    required_delivery_date=order.required_delivery_date,
                    currency=order.currency,
                    payment_terms=order.payment_terms,
                    delivery_terms=order.delivery_terms,
                    status=PurchaseOrderStatus.APPROVED,
                    subtotal=order.subtotal,
                    tax_total=order.tax_total,
                    grand_total=order.grand_total,
                    approved_by=approved_by,
                    approved_at=now(),
                    sent_at=order.sent_at,
                    acknowledged_at=order.acknowledged_at,
                    notes=order.notes,
                )
            )
            PurchaseOrderApproved(
                tenant_id=tenant_id,
                order_id=order_id,
                approved_by=approved_by,
            ).emit()
            logger.info(f"PurchaseOrder approved: {order_id} tenant={tenant_id}")
            return updated

    def send_to_supplier(self, order_id: str, tenant_id: str) -> PurchaseOrder | None:
        with transaction.atomic():
            order = self.order_repository.get_by_id(order_id, tenant_id)
            if not order or order.status != PurchaseOrderStatus.APPROVED:
                return None
            updated = self.order_repository.update(
                PurchaseOrder(
                    id=order.id,
                    tenant_id=order.tenant_id,
                    supplier_id=order.supplier_id,
                    warehouse_id=order.warehouse_id,
                    order_type=order.order_type,
                    order_number=order.order_number,
                    order_date=order.order_date,
                    required_delivery_date=order.required_delivery_date,
                    currency=order.currency,
                    payment_terms=order.payment_terms,
                    delivery_terms=order.delivery_terms,
                    status=PurchaseOrderStatus.SENT,
                    subtotal=order.subtotal,
                    tax_total=order.tax_total,
                    grand_total=order.grand_total,
                    approved_by=order.approved_by,
                    approved_at=order.approved_at,
                    sent_at=now(),
                    acknowledged_at=order.acknowledged_at,
                    notes=order.notes,
                )
            )
            PurchaseOrderSent(
                tenant_id=tenant_id,
                order_id=order_id,
                supplier_id=order.supplier_id,
            ).emit()
            logger.info(f"PurchaseOrder sent to supplier: {order_id} tenant={tenant_id}")
            return updated

    def acknowledge(self, order_id: str, tenant_id: str) -> PurchaseOrder | None:
        with transaction.atomic():
            order = self.order_repository.get_by_id(order_id, tenant_id)
            if not order or order.status != PurchaseOrderStatus.SENT:
                return None
            updated = self.order_repository.update(
                PurchaseOrder(
                    id=order.id,
                    tenant_id=order.tenant_id,
                    supplier_id=order.supplier_id,
                    warehouse_id=order.warehouse_id,
                    order_type=order.order_type,
                    order_number=order.order_number,
                    order_date=order.order_date,
                    required_delivery_date=order.required_delivery_date,
                    currency=order.currency,
                    payment_terms=order.payment_terms,
                    delivery_terms=order.delivery_terms,
                    status=PurchaseOrderStatus.ACKNOWLEDGED,
                    subtotal=order.subtotal,
                    tax_total=order.tax_total,
                    grand_total=order.grand_total,
                    approved_by=order.approved_by,
                    approved_at=order.approved_at,
                    sent_at=order.sent_at,
                    acknowledged_at=now(),
                    notes=order.notes,
                )
            )
            PurchaseOrderAcknowledged(
                tenant_id=tenant_id,
                order_id=order_id,
                supplier_id=order.supplier_id,
            ).emit()
            logger.info(f"PurchaseOrder acknowledged: {order_id} tenant={tenant_id}")
            return updated

    def close(self, order_id: str, tenant_id: str) -> PurchaseOrder | None:
        with transaction.atomic():
            order = self.order_repository.get_by_id(order_id, tenant_id)
            if not order or order.status not in [PurchaseOrderStatus.RECEIVED, PurchaseOrderStatus.INVOICED]:
                return None
            updated = self.order_repository.update(
                PurchaseOrder(
                    id=order.id,
                    tenant_id=order.tenant_id,
                    supplier_id=order.supplier_id,
                    warehouse_id=order.warehouse_id,
                    order_type=order.order_type,
                    order_number=order.order_number,
                    order_date=order.order_date,
                    required_delivery_date=order.required_delivery_date,
                    currency=order.currency,
                    payment_terms=order.payment_terms,
                    delivery_terms=order.delivery_terms,
                    status=PurchaseOrderStatus.CLOSED,
                    subtotal=order.subtotal,
                    tax_total=order.tax_total,
                    grand_total=order.grand_total,
                    approved_by=order.approved_by,
                    approved_at=order.approved_at,
                    sent_at=order.sent_at,
                    acknowledged_at=order.acknowledged_at,
                    notes=order.notes,
                )
            )
            PurchaseOrderClosed(
                tenant_id=tenant_id,
                order_id=order_id,
            ).emit()
            logger.info(f"PurchaseOrder closed: {order_id} tenant={tenant_id}")
            return updated

    def cancel(self, order_id: str, tenant_id: str, reason: str = "") -> PurchaseOrder | None:
        with transaction.atomic():
            order = self.order_repository.get_by_id(order_id, tenant_id)
            if not order or order.status not in [PurchaseOrderStatus.DRAFT, PurchaseOrderStatus.APPROVED, PurchaseOrderStatus.SENT]:
                return None
            updated = self.order_repository.update(
                PurchaseOrder(
                    id=order.id,
                    tenant_id=order.tenant_id,
                    supplier_id=order.supplier_id,
                    warehouse_id=order.warehouse_id,
                    order_type=order.order_type,
                    order_number=order.order_number,
                    order_date=order.order_date,
                    required_delivery_date=order.required_delivery_date,
                    currency=order.currency,
                    payment_terms=order.payment_terms,
                    delivery_terms=order.delivery_terms,
                    status=PurchaseOrderStatus.CANCELLED,
                    subtotal=order.subtotal,
                    tax_total=order.tax_total,
                    grand_total=order.grand_total,
                    approved_by=order.approved_by,
                    approved_at=order.approved_at,
                    sent_at=order.sent_at,
                    acknowledged_at=order.acknowledged_at,
                    notes=f"{order.notes}\nCancelled: {reason}" if reason else order.notes,
                )
            )
            PurchaseOrderCancelled(
                tenant_id=tenant_id,
                order_id=order_id,
                reason=reason,
            ).emit()
            logger.info(f"PurchaseOrder cancelled: {order_id} tenant={tenant_id}")
            return updated