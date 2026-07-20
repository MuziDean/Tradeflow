"""
Domain entities for the Purchasing bounded context.

Purchasing manages the procurement lifecycle:
PurchaseRequisition → SupplierQuotation → PurchaseOrder → GoodsReceipt → Inventory

All entities are pure Python objects with business rules.
No framework dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PurchaseRequisitionLine:
    """Line item within a purchase requisition."""

    tenant_id: str
    requisition_id: Optional[str] = None
    product_id: str = ""
    variant_id: Optional[str] = None
    quantity: float = 0.0
    unit_of_measure: str = "count"
    estimated_unit_price: Optional[float] = None
    estimated_total: Optional[float] = None
    notes: str = ""
    line_number: int = 0
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PurchaseRequisition:
    """Purchase requisition header."""

    tenant_id: str
    warehouse_id: str = ""
    requested_by: str = ""
    required_date: Optional[datetime] = None
    justification: str = ""
    status: str = "draft"
    approved_by: Optional[str] = None
    rejected_reason: str = ""
    total_estimated_amount: Optional[float] = None
    currency: str = "ZAR"
    notes: str = ""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SupplierQuotationLine:
    """Line item within a supplier quotation."""

    tenant_id: str
    quotation_id: Optional[str] = None
    product_id: str = ""
    variant_id: Optional[str] = None
    quantity: float = 0.0
    unit_price: float = 0.0
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    total_price: float = 0.0
    lead_time_days: int = 0
    validity_days: int = 30
    notes: str = ""
    line_number: int = 0
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SupplierQuotation:
    """Supplier quotation header."""

    tenant_id: str
    supplier_id: str = ""
    warehouse_id: str = ""
    quotation_reference: str = ""
    quotation_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    validity_days: int = 30
    currency: str = "ZAR"
    payment_terms: str = ""
    delivery_terms: str = ""
    status: str = "draft"
    total_amount: Optional[float] = None
    notes: str = ""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PurchaseOrderLine:
    """Line item within a purchase order."""

    tenant_id: str
    purchase_order_id: Optional[str] = None
    product_id: str = ""
    variant_id: Optional[str] = None
    quantity_ordered: float = 0.0
    quantity_received: float = 0.0
    quantity_invoiced: float = 0.0
    unit_price: float = 0.0
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    line_total: float = 0.0
    currency: str = "ZAR"
    expected_delivery_date: Optional[datetime] = None
    notes: str = ""
    line_number: int = 0
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PurchaseOrder:
    """Purchase order header."""

    tenant_id: str
    supplier_id: str = ""
    warehouse_id: str = ""
    order_type: str = "standard"
    order_number: str = ""
    order_date: Optional[datetime] = None
    required_delivery_date: Optional[datetime] = None
    currency: str = "ZAR"
    payment_terms: str = ""
    delivery_terms: str = ""
    status: str = "draft"
    subtotal: float = 0.0
    tax_total: float = 0.0
    grand_total: float = 0.0
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    acknowledged_at: Optional[datetime] = None
    notes: str = ""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class GoodsReceiptLine:
    """Line item within a goods receipt."""

    tenant_id: str
    goods_receipt_id: Optional[str] = None
    purchase_order_line_id: Optional[str] = None
    product_id: str = ""
    variant_id: Optional[str] = None
    quantity_received: float = 0.0
    quantity_accepted: float = 0.0
    quantity_rejected: float = 0.0
    unit_cost: float = 0.0
    line_total: float = 0.0
    batch_number: str = ""
    serial_number: str = ""
    expiry_date: Optional[datetime] = None
    rejection_reason: str = ""
    notes: str = ""
    line_number: int = 0
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class GoodsReceipt:
    """Goods receipt header."""

    tenant_id: str
    purchase_order_id: str = ""
    warehouse_id: str = ""
    receipt_number: str = ""
    receipt_date: Optional[datetime] = None
    status: str = "draft"
    posted_by: Optional[str] = None
    posted_at: Optional[datetime] = None
    notes: str = ""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PurchaseReturnLine:
    """Line item within a purchase return."""

    tenant_id: str
    purchase_return_id: Optional[str] = None
    goods_receipt_line_id: Optional[str] = None
    product_id: str = ""
    variant_id: Optional[str] = None
    quantity_returned: float = 0.0
    unit_cost: float = 0.0
    line_total: float = 0.0
    batch_number: str = ""
    serial_number: str = ""
    expiry_date: Optional[datetime] = None
    return_reason: str = ""
    notes: str = ""
    line_number: int = 0
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class PurchaseReturn:
    """Purchase return header."""

    tenant_id: str
    purchase_order_id: str = ""
    goods_receipt_id: str = ""
    supplier_id: str = ""
    warehouse_id: str = ""
    return_number: str = ""
    return_date: Optional[datetime] = None
    status: str = "draft"
    total_amount: float = 0.0
    currency: str = "ZAR"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    received_at: Optional[datetime] = None
    credited_at: Optional[datetime] = None
    notes: str = ""
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class SupplierPriceList:
    """Supplier price list for a product."""

    tenant_id: str
    supplier_id: str = ""
    product_id: str = ""
    variant_id: Optional[str] = None
    price: float = 0.0
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    effective_price: float = 0.0
    currency: str = "ZAR"
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    minimum_order_quantity: float = 0.0
    lead_time_days: int = 0
    is_active: bool = True
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None