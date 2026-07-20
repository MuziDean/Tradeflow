"""
Common enumerations and type definitions for TradeFlow.

Centralizes business-relevant enums to ensure consistency across modules.
"""

from enum import StrEnum


class UserStatus(StrEnum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"


class TenantStatus(StrEnum):
    """Tenant (company) subscription status."""

    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class EmploymentType(StrEnum):
    """Employee employment type."""

    PERMANENT = "permanent"
    CONTRACT = "contract"
    PART_TIME = "part_time"
    CASUAL = "casual"


class EmployeeStatus(StrEnum):
    """Employee lifecycle status."""

    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class PayrollRunStatus(StrEnum):
    """Payroll run state machine."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    LOCKED = "locked"


class SaleStatus(StrEnum):
    """Sale transaction status."""

    COMPLETED = "completed"
    VOID = "void"
    REFUNDED = "refunded"


class StockMovementType(StrEnum):
    """Stock movement types for enterprise ERP usage."""

    PURCHASE_RECEIPT = "purchase_receipt"
    SALE = "sale"
    SALE_RETURN = "sale_return"
    PURCHASE_RETURN = "purchase_return"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    ADJUSTMENT_IN = "adjustment_in"
    ADJUSTMENT_OUT = "adjustment_out"
    OPENING_BALANCE = "opening_balance"
    STOCK_COUNT = "stock_count"
    PRODUCTION_IN = "production_in"
    PRODUCTION_OUT = "production_out"


class PaymentMethod(StrEnum):
    """Payment methods."""

    CASH = "cash"
    CARD = "card"
    VOUCHER = "voucher"
    LAY_BY_DEPOSIT = "lay_by_deposit"
    CREDIT_NOTE = "credit_note"


class WarehouseType(StrEnum):
    """Warehouse classification."""

    MAIN = "main"
    RETAIL = "retail"
    TRANSIT = "transit"
    RETURNS = "returns"
    DAMAGED = "damaged"
    VIRTUAL = "virtual"


class TaxCategory(StrEnum):
    """Tax category classification."""

    STANDARD = "standard"
    REDUCED = "reduced"
    ZERO = "zero"
    EXEMPT = "exempt"


class TaxType(StrEnum):
    """Tax type classification."""

    VAT = "VAT"
    SALES_TAX = "SALES_TAX"
    INCOME_TAX = "INCOME_TAX"


class FiscalYearStatus(StrEnum):
    """Fiscal year status."""

    OPEN = "open"
    CLOSED = "closed"
    ARCHIVED = "archived"


class NumberSequenceResetPolicy(StrEnum):
    """Number sequence reset behavior."""

    NEVER = "never"
    YEARLY = "yearly"
    MONTHLY = "monthly"
    DAILY = "daily"


class InventoryStatus(StrEnum):
    """Lifecycle status for products in the inventory catalog."""

    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DISCONTINUED = "discontinued"


class InventoryTransactionType(StrEnum):
    """Inventory movement transaction types."""

    ADJUSTMENT = "adjustment"
    SALE = "sale"
    RETURN = "return"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    GRN = "grn"
    STOCK_TAKE = "stock_take"


class AdjustmentType(StrEnum):
    """Stock adjustment classification."""
    CORRECTION = "correction"
    DAMAGE = "damage"
    LOSS = "loss"
    FOUND = "found"
    WRITE_OFF = "write_off"
    MANUAL = "manual"


class ReservationStatus(StrEnum):
    """Lifecycle status for stock reservations."""
    PENDING = "pending"
    ALLOCATED = "allocated"
    RELEASED = "released"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MovementStatus(StrEnum):
    """Transaction lifecycle for stock movements."""
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"


class CycleCountStatus(StrEnum):
    """Lifecycle status for cycle counts."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ADJUSTED = "adjusted"
    CANCELLED = "cancelled"


class StockTransferStatus(StrEnum):
    """Lifecycle status for stock transfers."""

    DRAFT = "draft"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class StockTakeStatus(StrEnum):
    """Lifecycle status for stock takes."""

    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class UnitOfMeasureType(StrEnum):
    """Unit of measure classification."""

    COUNT = "count"
    WEIGHT = "weight"
    VOLUME = "volume"
    LENGTH = "length"
    TIME = "time"


class BarcodeType(StrEnum):
    """Barcode format classification."""

    EAN13 = "ean13"
    UPC_A = "upc_a"
    CODE128 = "code128"
    QR = "qr"


class PurchaseRequisitionStatus(StrEnum):
    """Lifecycle status for purchase requisitions."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONVERTED = "converted"
    CANCELLED = "cancelled"


class QuotationStatus(StrEnum):
    """Lifecycle status for supplier quotations."""

    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class PurchaseOrderStatus(StrEnum):
    """Lifecycle status for purchase orders."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    PARTIALLY_RECEIVED = "partially_received"
    RECEIVED = "received"
    INVOICED = "invoiced"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class PurchaseOrderType(StrEnum):
    """Purchase order classification."""

    STANDARD = "standard"
    BLANKET = "blanket"
    CONSIGNMENT = "consignment"
    DROP_SHIP = "drop_ship"


class GoodsReceiptStatus(StrEnum):
    """Lifecycle status for goods receipts."""

    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"


class PurchaseReturnStatus(StrEnum):
    """Lifecycle status for purchase returns."""

    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    SHIPPED = "shipped"
    RECEIVED = "received"
    CREDITED = "credited"
    CANCELLED = "cancelled"


class ApprovalStatus(StrEnum):
    """Generic approval status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
