"""
Domain entities for the inventory module.

Per ADR-004: Entities represent the core business concepts and invariants.
Inventory is completely separated from Retail. Retail owns products.
Inventory owns stock.

Designed for enterprise ERP scalability supporting purchasing, sales,
POS, warehouse management, manufacturing, and reporting.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from shared.ids.uuid import new_id_str
from shared.time.helpers import now


@dataclass
class InventoryItem:
    """
    Core inventory record linking a product to warehouse stock.

    This is the fundamental unit of inventory — a product (or variant)
    stored at a specific warehouse location. Stock quantities are stored
    here, NOT on the Product entity.

    Supports future batch, serial, and bin location tracking.
    Never tracks financial values — those belong in accounting.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    warehouse_id: str = ""
    product_id: str = ""
    variant_id: str | None = None

    # Quantity fields (computed from movements, cached here for performance)
    quantity_on_hand: Decimal = field(default=Decimal("0.000"))
    quantity_reserved: Decimal = field(default=Decimal("0.000"))
    quantity_available: Decimal = field(default=Decimal("0.000"))
    quantity_in_transit: Decimal = field(default=Decimal("0.000"))
    quantity_committed: Decimal = field(default=Decimal("0.000"))
    quantity_damaged: Decimal = field(default=Decimal("0.000"))
    quantity_quarantine: Decimal = field(default=Decimal("0.000"))

    # Reorder settings
    reorder_point: Decimal | None = None
    reorder_quantity: Decimal | None = None
    preferred_supplier_id: str | None = None

    # Future: batch/lot tracking
    batch_number: str | None = None
    lot_number: str | None = None
    serial_number: str | None = None
    expiry_date: str | None = None
    manufacturing_date: str | None = None

    # Audit
    last_stocked_at: str | None = None
    last_counted_at: str | None = None
    last_movement_at: str | None = None
    is_active: bool = True
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class StockBalance:
    """
    Periodic snapshot of stock quantities for reporting.

    Captures the state of inventory at a point in time (daily, weekly,
    monthly) for trend analysis, valuation, and reconciliation.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    inventory_item_id: str = ""
    warehouse_id: str = ""
    product_id: str = ""
    variant_id: str | None = None

    snapshot_date: str = ""
    quantity_on_hand: Decimal = field(default=Decimal("0.000"))
    quantity_reserved: Decimal = field(default=Decimal("0.000"))
    quantity_available: Decimal = field(default=Decimal("0.000"))
    quantity_in_transit: Decimal = field(default=Decimal("0.000"))
    quantity_damaged: Decimal = field(default=Decimal("0.000"))
    quantity_quarantine: Decimal = field(default=Decimal("0.000"))

    # Costing (future: FIFO, LIFO, Weighted Average)
    unit_cost: Decimal | None = None
    total_value: Decimal | None = None
    costing_method: str = ""

    is_finalized: bool = False
    created_at: str = field(default_factory=now)


@dataclass
class StockMovement:
    """
    A header-level inventory transaction.

    Represents a logical inventory event (receipt, sale, transfer, etc.)
    that contains one or more movement lines. Each movement has a status
    lifecycle: Draft → Posted → Cancelled.

    Supports reference to external documents (purchase orders, sales orders,
    production orders) for full audit trail.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    warehouse_id: str = ""
    movement_type: str = ""
    status: str = "draft"
    reference_type: str = ""  # purchase_order, sales_order, transfer, etc.
    reference_id: str = ""  # UUID of the external document
    reference_number: str = ""  # Human-readable document number
    description: str = ""
    performed_by: str = ""
    approved_by: str | None = None
    posted_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class MovementLine:
    """
    A single line item within a stock movement.

    Each line represents one product/variant being moved with a specific
    quantity. Supports batch/serial attribution per line for traceability.
    Quantity is always positive; direction is implied by the movement_type.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    movement_id: str = ""
    inventory_item_id: str = ""
    product_id: str = ""
    variant_id: str | None = None
    quantity: Decimal = field(default=Decimal("0.000"))
    unit_cost: Decimal | None = None
    total_cost: Decimal | None = None
    batch_number: str | None = None
    serial_number: str | None = None
    expiry_date: str | None = None
    line_number: int = 0
    notes: str = ""
    created_at: str = field(default_factory=now)


@dataclass
class StockAdjustment:
    """
    A header-level stock adjustment transaction.

    Used for corrections, damage write-offs, found stock, cycle count
    variances, and manual adjustments. Requires approval for large values.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    warehouse_id: str = ""
    adjustment_type: str = ""
    status: str = "draft"
    reason: str = ""
    reference_number: str = ""
    performed_by: str = ""
    approved_by: str | None = None
    posted_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class AdjustmentLine:
    """
    A single line item within a stock adjustment.

    Captures the before/after quantities for audit trail.
    Supports batch/serial attribution per line.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    adjustment_id: str = ""
    inventory_item_id: str = ""
    product_id: str = ""
    variant_id: str | None = None
    quantity_before: Decimal = field(default=Decimal("0.000"))
    quantity_after: Decimal = field(default=Decimal("0.000"))
    quantity_delta: Decimal = field(default=Decimal("0.000"))
    unit_cost: Decimal | None = None
    batch_number: str | None = None
    serial_number: str | None = None
    expiry_date: str | None = None
    line_number: int = 0
    notes: str = ""
    created_at: str = field(default_factory=now)


@dataclass
class StockTransfer:
    """
    A header-level stock transfer between warehouses.

    Supports single or multi-warehouse transfers. Source warehouse issues stock,
    destination warehouse receives it. Status lifecycle: Draft → In Transit →
    Completed → Cancelled.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    source_warehouse_id: str = ""
    destination_warehouse_id: str = ""
    status: str = "draft"
    reference_number: str = ""
    description: str = ""
    performed_by: str = ""
    approved_by: str | None = None
    shipped_at: str | None = None
    received_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class TransferLine:
    """
    A single line item within a stock transfer.

    Each line represents one product/variant being transferred.
    Supports batch/serial attribution per line.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    transfer_id: str = ""
    product_id: str = ""
    variant_id: str | None = None
    quantity: Decimal = field(default=Decimal("0.000"))
    quantity_received: Decimal = field(default=Decimal("0.000"))
    unit_cost: Decimal | None = None
    batch_number: str | None = None
    serial_number: str | None = None
    expiry_date: str | None = None
    line_number: int = 0
    notes: str = ""
    created_at: str = field(default_factory=now)


@dataclass
class StockReservation:
    """
    A reservation of inventory for a specific purpose.

    Used to reserve stock for sales orders, production orders, or other
    allocations. Status lifecycle: Pending → Allocated → Released → Completed.

    Supports partial allocations and multi-warehouse reservations.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    inventory_item_id: str = ""
    product_id: str = ""
    variant_id: str | None = None
    warehouse_id: str = ""
    quantity: Decimal = field(default=Decimal("0.000"))
    quantity_allocated: Decimal = field(default=Decimal("0.000"))
    status: str = "pending"
    reference_type: str = ""  # sales_order, production_order, etc.
    reference_id: str = ""
    reference_line_id: str = ""
    reserved_by: str = ""
    released_by: str | None = None
    expires_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class CycleCount:
    """
    A scheduled or ad-hoc cycle count of inventory.

    Cycle counts verify stock accuracy by counting a subset of items
    on a rotating basis. Status lifecycle: Scheduled → In Progress →
    Completed → Adjusted.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    warehouse_id: str = ""
    zone_id: str | None = None  # Future: warehouse zones
    count_type: str = "scheduled"  # scheduled, ad_hoc, annual
    status: str = "scheduled"
    reference_number: str = ""
    scheduled_date: str = ""
    counted_by: str = ""
    verified_by: str | None = None
    variance_threshold_percent: Decimal = field(default=Decimal("5.000"))
    notes: str = ""
    completed_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class CycleCountLine:
    """
    A single line item within a cycle count.

    Records the system quantity vs the counted quantity. Variances
    can be automatically adjusted based on configured thresholds.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    cycle_count_id: str = ""
    inventory_item_id: str = ""
    product_id: str = ""
    variant_id: str | None = None
    bin_location: str = ""  # Future: warehouse bin
    system_quantity: Decimal = field(default=Decimal("0.000"))
    counted_quantity: Decimal = field(default=Decimal("0.000"))
    variance_quantity: Decimal = field(default=Decimal("0.000"))
    unit_cost: Decimal | None = None
    variance_value: Decimal | None = None
    is_adjusted: bool = False
    batch_number: str | None = None
    serial_number: str | None = None
    expiry_date: str | None = None
    line_number: int = 0
    notes: str = ""
    created_at: str = field(default_factory=now)