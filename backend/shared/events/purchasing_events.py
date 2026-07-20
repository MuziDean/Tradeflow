"""
Domain events for the Purchasing module.

Events are emitted by application services when state transitions occur.
Other modules (Inventory, Finance) subscribe to these events.
"""

from shared.events.base import DomainEvent


class PurchaseRequisitionCreated(DomainEvent):
    """Emitted when a purchase requisition is created."""

    def __init__(self, tenant_id: str, requisition_id: str, warehouse_id: str, requested_by: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseRequisition",
            aggregate_id=requisition_id,
            event_data={
                "warehouse_id": warehouse_id,
                "requested_by": requested_by,
            },
        )


class PurchaseRequisitionApproved(DomainEvent):
    """Emitted when a purchase requisition is approved."""

    def __init__(self, tenant_id: str, requisition_id: str, approved_by: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseRequisition",
            aggregate_id=requisition_id,
            event_data={
                "approved_by": approved_by,
            },
        )


class PurchaseRequisitionRejected(DomainEvent):
    """Emitted when a purchase requisition is rejected."""

    def __init__(self, tenant_id: str, requisition_id: str, rejected_by: str, reason: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseRequisition",
            aggregate_id=requisition_id,
            event_data={
                "rejected_by": rejected_by,
                "reason": reason,
            },
        )


class PurchaseRequisitionConverted(DomainEvent):
    """Emitted when a purchase requisition is converted to a purchase order."""

    def __init__(self, tenant_id: str, requisition_id: str, purchase_order_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseRequisition",
            aggregate_id=requisition_id,
            event_data={
                "purchase_order_id": purchase_order_id,
            },
        )


class SupplierQuotationCreated(DomainEvent):
    """Emitted when a supplier quotation is created."""

    def __init__(self, tenant_id: str, quotation_id: str, supplier_id: str, warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="SupplierQuotation",
            aggregate_id=quotation_id,
            event_data={
                "supplier_id": supplier_id,
                "warehouse_id": warehouse_id,
            },
        )


class SupplierQuotationSubmitted(DomainEvent):
    """Emitted when a supplier quotation is submitted to supplier."""

    def __init__(self, tenant_id: str, quotation_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="SupplierQuotation",
            aggregate_id=quotation_id,
            event_data={
                "supplier_id": supplier_id,
            },
        )


class SupplierQuotationAccepted(DomainEvent):
    """Emitted when a supplier quotation is accepted."""

    def __init__(self, tenant_id: str, quotation_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="SupplierQuotation",
            aggregate_id=quotation_id,
            event_data={
                "supplier_id": supplier_id,
            },
        )


class SupplierQuotationRejected(DomainEvent):
    """Emitted when a supplier quotation is rejected."""

    def __init__(self, tenant_id: str, quotation_id: str, supplier_id: str, reason: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="SupplierQuotation",
            aggregate_id=quotation_id,
            event_data={
                "supplier_id": supplier_id,
                "reason": reason,
            },
        )


class SupplierQuotationExpired(DomainEvent):
    """Emitted when a supplier quotation expires."""

    def __init__(self, tenant_id: str, quotation_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="SupplierQuotation",
            aggregate_id=quotation_id,
            event_data={
                "supplier_id": supplier_id,
            },
        )


class PurchaseOrderCreated(DomainEvent):
    """Emitted when a purchase order is created."""

    def __init__(self, tenant_id: str, order_id: str, supplier_id: str, warehouse_id: str, order_number: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseOrder",
            aggregate_id=order_id,
            event_data={
                "supplier_id": supplier_id,
                "warehouse_id": warehouse_id,
                "order_number": order_number,
            },
        )


class PurchaseOrderApproved(DomainEvent):
    """Emitted when a purchase order is approved."""

    def __init__(self, tenant_id: str, order_id: str, approved_by: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseOrder",
            aggregate_id=order_id,
            event_data={
                "approved_by": approved_by,
            },
        )


class PurchaseOrderSent(DomainEvent):
    """Emitted when a purchase order is sent to supplier."""

    def __init__(self, tenant_id: str, order_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseOrder",
            aggregate_id=order_id,
            event_data={
                "supplier_id": supplier_id,
            },
        )


class PurchaseOrderAcknowledged(DomainEvent):
    """Emitted when a supplier acknowledges a purchase order."""

    def __init__(self, tenant_id: str, order_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseOrder",
            aggregate_id=order_id,
            event_data={
                "supplier_id": supplier_id,
            },
        )


class PurchaseOrderClosed(DomainEvent):
    """Emitted when a purchase order is closed."""

    def __init__(self, tenant_id: str, order_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseOrder",
            aggregate_id=order_id,
            event_data={},
        )


class PurchaseOrderCancelled(DomainEvent):
    """Emitted when a purchase order is cancelled."""

    def __init__(self, tenant_id: str, order_id: str, reason: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseOrder",
            aggregate_id=order_id,
            event_data={
                "reason": reason,
            },
        )


class GoodsReceiptCreated(DomainEvent):
    """Emitted when a goods receipt is created."""

    def __init__(self, tenant_id: str, receipt_id: str, purchase_order_id: str, warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="GoodsReceipt",
            aggregate_id=receipt_id,
            event_data={
                "purchase_order_id": purchase_order_id,
                "warehouse_id": warehouse_id,
            },
        )


class GoodsReceiptPosted(DomainEvent):
    """Emitted when a goods receipt is posted."""

    def __init__(self, tenant_id: str, receipt_id: str, purchase_order_id: str, warehouse_id: str, posted_by: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="GoodsReceipt",
            aggregate_id=receipt_id,
            event_data={
                "purchase_order_id": purchase_order_id,
                "warehouse_id": warehouse_id,
                "posted_by": posted_by,
            },
        )


class GoodsReceiptCancelled(DomainEvent):
    """Emitted when a goods receipt is cancelled."""

    def __init__(self, tenant_id: str, receipt_id: str, reason: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="GoodsReceipt",
            aggregate_id=receipt_id,
            event_data={
                "reason": reason,
            },
        )


class PurchaseReturnCreated(DomainEvent):
    """Emitted when a purchase return is created."""

    def __init__(self, tenant_id: str, return_id: str, purchase_order_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseReturn",
            aggregate_id=return_id,
            event_data={
                "purchase_order_id": purchase_order_id,
                "supplier_id": supplier_id,
            },
        )


class PurchaseReturnApproved(DomainEvent):
    """Emitted when a purchase return is approved."""

    def __init__(self, tenant_id: str, return_id: str, approved_by: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseReturn",
            aggregate_id=return_id,
            event_data={
                "approved_by": approved_by,
            },
        )


class PurchaseReturnShipped(DomainEvent):
    """Emitted when a purchase return is shipped to supplier."""

    def __init__(self, tenant_id: str, return_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseReturn",
            aggregate_id=return_id,
            event_data={
                "supplier_id": supplier_id,
            },
        )


class PurchaseReturnCredited(DomainEvent):
    """Emitted when a purchase return is credited by supplier."""

    def __init__(self, tenant_id: str, return_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="PurchaseReturn",
            aggregate_id=return_id,
            event_data={
                "supplier_id": supplier_id,
            },
        )


class SupplierPriceListActivated(DomainEvent):
    """Emitted when a supplier price list is activated."""

    def __init__(self, tenant_id: str, price_list_id: str, supplier_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="SupplierPriceList",
            aggregate_id=price_list_id,
            event_data={
                "supplier_id": supplier_id,
                "product_id": product_id,
            },
        )


class SupplierPriceListDeactivated(DomainEvent):
    """Emitted when a supplier price list is deactivated."""

    def __init__(self, tenant_id: str, price_list_id: str, supplier_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_type="SupplierPriceList",
            aggregate_id=price_list_id,
            event_data={
                "supplier_id": supplier_id,
                "product_id": product_id,
            },
        )