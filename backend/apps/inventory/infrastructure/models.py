"""
Django ORM models for the inventory module.

Stock management foundation: inventory items, stock balances, movements,
adjustments, transfers, reservations, and cycle counts.

Inventory is completely separated from Retail. Retail owns products.
Inventory owns stock. Cross-module reference to Product is acceptable
because inventory tracks stock FOR products.
"""

from django.db import models

from infrastructure.db.base_model import TenantModel


class InventoryItemModel(TenantModel):
    """Core inventory record linking a product to warehouse stock."""

    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="inventory_items")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="inventory_items")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="inventory_items")

    # Quantity fields
    quantity_on_hand = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_reserved = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_available = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_in_transit = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_committed = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_damaged = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_quarantine = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    # Reorder settings
    reorder_point = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    reorder_quantity = models.DecimalField(max_digits=18, decimal_places=3, null=True, blank=True)
    preferred_supplier = models.ForeignKey("retail.Supplier", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    # Future: batch/lot tracking
    batch_number = models.CharField(max_length=100, blank=True, db_index=True)
    lot_number = models.CharField(max_length=100, blank=True, db_index=True)
    serial_number = models.CharField(max_length=100, blank=True, db_index=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    manufacturing_date = models.DateTimeField(null=True, blank=True)

    # Audit
    last_stocked_at = models.DateTimeField(null=True, blank=True)
    last_counted_at = models.DateTimeField(null=True, blank=True)
    last_movement_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "inventory_items"
        verbose_name = "Inventory Item"
        verbose_name_plural = "Inventory Items"
        unique_together = ("tenant_id", "warehouse", "product", "variant", "batch_number", "serial_number")
        indexes = [
            models.Index(fields=["tenant_id", "warehouse"]),
            models.Index(fields=["tenant_id", "product"]),
            models.Index(fields=["tenant_id", "variant"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "is_deleted"]),
            models.Index(fields=["tenant_id", "batch_number"]),
            models.Index(fields=["tenant_id", "serial_number"]),
            models.Index(fields=["tenant_id", "expiry_date"]),
            models.Index(fields=["tenant_id", "quantity_on_hand"]),
            models.Index(fields=["tenant_id", "quantity_available"]),
            models.Index(fields=["tenant_id", "reorder_point", "quantity_on_hand"], name="idx_low_stock"),
        ]


class StockBalanceModel(TenantModel):
    """Periodic snapshot of stock quantities for reporting."""

    inventory_item = models.ForeignKey(InventoryItemModel, on_delete=models.CASCADE, related_name="stock_balances")
    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="+")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")

    snapshot_date = models.DateField(db_index=True)
    quantity_on_hand = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_reserved = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_available = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_in_transit = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_damaged = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_quarantine = models.DecimalField(max_digits=18, decimal_places=3, default=0)

    # Costing (future: FIFO, LIFO, Weighted Average)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    total_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    costing_method = models.CharField(max_length=20, blank=True)

    is_finalized = models.BooleanField(default=False)

    class Meta:
        db_table = "inventory_stock_balances"
        verbose_name = "Stock Balance"
        verbose_name_plural = "Stock Balances"
        unique_together = ("tenant_id", "inventory_item", "snapshot_date")
        indexes = [
            models.Index(fields=["tenant_id", "warehouse", "snapshot_date"]),
            models.Index(fields=["tenant_id", "product", "snapshot_date"]),
            models.Index(fields=["tenant_id", "snapshot_date", "is_finalized"]),
        ]


class StockMovementModel(TenantModel):
    """Header-level inventory transaction."""

    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="stock_movements")
    movement_type = models.CharField(max_length=30, db_index=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.UUIDField(null=True, blank=True, db_index=True)
    reference_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    performed_by = models.UUIDField()
    approved_by = models.UUIDField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_stock_movements"
        verbose_name = "Stock Movement"
        verbose_name_plural = "Stock Movements"
        indexes = [
            models.Index(fields=["tenant_id", "warehouse", "movement_type"]),
            models.Index(fields=["tenant_id", "movement_type", "status"]),
            models.Index(fields=["tenant_id", "reference_type", "reference_id"]),
            models.Index(fields=["tenant_id", "posted_at"]),
            models.Index(fields=["tenant_id", "performed_by"]),
        ]


class MovementLineModel(TenantModel):
    """Line item within a stock movement."""

    movement = models.ForeignKey(StockMovementModel, on_delete=models.CASCADE, related_name="lines")
    inventory_item = models.ForeignKey(InventoryItemModel, on_delete=models.PROTECT, related_name="+")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    line_number = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "inventory_movement_lines"
        verbose_name = "Movement Line"
        verbose_name_plural = "Movement Lines"
        indexes = [
            models.Index(fields=["tenant_id", "movement", "line_number"]),
            models.Index(fields=["tenant_id", "inventory_item"]),
            models.Index(fields=["tenant_id", "product"]),
            models.Index(fields=["tenant_id", "batch_number"]),
            models.Index(fields=["tenant_id", "serial_number"]),
        ]


class StockAdjustmentModel(TenantModel):
    """Header-level stock adjustment transaction."""

    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="stock_adjustments")
    adjustment_type = models.CharField(max_length=30, db_index=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    reason = models.TextField()
    reference_number = models.CharField(max_length=100, blank=True)
    performed_by = models.UUIDField()
    approved_by = models.UUIDField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_stock_adjustments"
        verbose_name = "Stock Adjustment"
        verbose_name_plural = "Stock Adjustments"
        indexes = [
            models.Index(fields=["tenant_id", "warehouse", "adjustment_type"]),
            models.Index(fields=["tenant_id", "adjustment_type", "status"]),
            models.Index(fields=["tenant_id", "performed_by"]),
            models.Index(fields=["tenant_id", "posted_at"]),
        ]


class AdjustmentLineModel(TenantModel):
    """Line item within a stock adjustment."""

    adjustment = models.ForeignKey(StockAdjustmentModel, on_delete=models.CASCADE, related_name="lines")
    inventory_item = models.ForeignKey(InventoryItemModel, on_delete=models.PROTECT, related_name="+")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity_before = models.DecimalField(max_digits=18, decimal_places=3)
    quantity_after = models.DecimalField(max_digits=18, decimal_places=3)
    quantity_delta = models.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    line_number = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "inventory_adjustment_lines"
        verbose_name = "Adjustment Line"
        verbose_name_plural = "Adjustment Lines"
        indexes = [
            models.Index(fields=["tenant_id", "adjustment", "line_number"]),
            models.Index(fields=["tenant_id", "inventory_item"]),
            models.Index(fields=["tenant_id", "product"]),
        ]


class StockTransferModel(TenantModel):
    """Header-level stock transfer between warehouses."""

    source_warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="transfers_out")
    destination_warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="transfers_in")
    status = models.CharField(max_length=20, default="draft", db_index=True)
    reference_number = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    performed_by = models.UUIDField()
    approved_by = models.UUIDField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_stock_transfers"
        verbose_name = "Stock Transfer"
        verbose_name_plural = "Stock Transfers"
        indexes = [
            models.Index(fields=["tenant_id", "source_warehouse", "status"]),
            models.Index(fields=["tenant_id", "destination_warehouse", "status"]),
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "reference_number"]),
        ]


class TransferLineModel(TenantModel):
    """Line item within a stock transfer."""

    transfer = models.ForeignKey(StockTransferModel, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    quantity_received = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    line_number = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "inventory_transfer_lines"
        verbose_name = "Transfer Line"
        verbose_name_plural = "Transfer Lines"
        indexes = [
            models.Index(fields=["tenant_id", "transfer", "line_number"]),
            models.Index(fields=["tenant_id", "product"]),
        ]


class StockReservationModel(TenantModel):
    """Reservation of inventory for a specific purpose."""

    inventory_item = models.ForeignKey(InventoryItemModel, on_delete=models.PROTECT, related_name="reservations")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="+")
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    quantity_allocated = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    status = models.CharField(max_length=20, default="pending", db_index=True)
    reference_type = models.CharField(max_length=50, blank=True)
    reference_id = models.UUIDField(null=True, blank=True, db_index=True)
    reference_line_id = models.UUIDField(null=True, blank=True)
    reserved_by = models.UUIDField()
    released_by = models.UUIDField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_stock_reservations"
        verbose_name = "Stock Reservation"
        verbose_name_plural = "Stock Reservations"
        indexes = [
            models.Index(fields=["tenant_id", "inventory_item", "status"]),
            models.Index(fields=["tenant_id", "reference_type", "reference_id"]),
            models.Index(fields=["tenant_id", "warehouse", "status"]),
            models.Index(fields=["tenant_id", "status", "expires_at"]),
        ]


class CycleCountModel(TenantModel):
    """Scheduled or ad-hoc cycle count of inventory."""

    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="cycle_counts")
    zone_id = models.UUIDField(null=True, blank=True)  # Future: WarehouseZone FK
    count_type = models.CharField(max_length=20, default="scheduled")
    status = models.CharField(max_length=20, default="scheduled", db_index=True)
    reference_number = models.CharField(max_length=100, blank=True)
    scheduled_date = models.DateField(db_index=True)
    counted_by = models.UUIDField()
    verified_by = models.UUIDField(null=True, blank=True)
    variance_threshold_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "inventory_cycle_counts"
        verbose_name = "Cycle Count"
        verbose_name_plural = "Cycle Counts"
        indexes = [
            models.Index(fields=["tenant_id", "warehouse", "status"]),
            models.Index(fields=["tenant_id", "status", "scheduled_date"]),
            models.Index(fields=["tenant_id", "count_type"]),
        ]


class CycleCountLineModel(TenantModel):
    """Line item within a cycle count."""

    cycle_count = models.ForeignKey(CycleCountModel, on_delete=models.CASCADE, related_name="lines")
    inventory_item = models.ForeignKey(InventoryItemModel, on_delete=models.PROTECT, related_name="+")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    bin_location = models.CharField(max_length=100, blank=True)
    system_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    counted_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    variance_quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    variance_value = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    is_adjusted = models.BooleanField(default=False)
    batch_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    line_number = models.IntegerField(default=0)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "inventory_cycle_count_lines"
        verbose_name = "Cycle Count Line"
        verbose_name_plural = "Cycle Count Lines"
        indexes = [
            models.Index(fields=["tenant_id", "cycle_count", "line_number"]),
            models.Index(fields=["tenant_id", "inventory_item", "is_adjusted"]),
            models.Index(fields=["tenant_id", "product"]),
        ]