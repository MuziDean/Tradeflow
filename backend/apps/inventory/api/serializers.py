"""
Serializers for the inventory module.

Per Backend Engineering Standards §5.2: Serializers validate and serialize
only. No business logic is implemented here.
"""

from rest_framework import serializers

from apps.inventory.domain.entities import (
    AdjustmentLine,
    CycleCount,
    CycleCountLine,
    InventoryItem,
    MovementLine,
    StockAdjustment,
    StockBalance,
    StockMovement,
    StockReservation,
    StockTransfer,
    TransferLine,
)


class InventoryItemSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity_on_hand = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_reserved = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_available = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_in_transit = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_committed = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_damaged = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_quarantine = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    reorder_point = serializers.DecimalField(max_digits=18, decimal_places=3, allow_null=True, required=False)
    reorder_quantity = serializers.DecimalField(max_digits=18, decimal_places=3, allow_null=True, required=False)
    preferred_supplier_id = serializers.CharField(allow_null=True, required=False)
    batch_number = serializers.CharField(allow_blank=True, required=False)
    lot_number = serializers.CharField(allow_blank=True, required=False)
    serial_number = serializers.CharField(allow_blank=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    manufacturing_date = serializers.DateTimeField(allow_null=True, required=False)
    last_stocked_at = serializers.DateTimeField(allow_null=True, required=False)
    last_counted_at = serializers.DateTimeField(allow_null=True, required=False)
    last_movement_at = serializers.DateTimeField(allow_null=True, required=False)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class InventoryItemListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True)
    quantity_on_hand = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_reserved = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_available = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_in_transit = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_committed = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_damaged = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_quarantine = serializers.DecimalField(max_digits=18, decimal_places=3)
    batch_number = serializers.CharField(allow_blank=True)
    serial_number = serializers.CharField(allow_blank=True)
    expiry_date = serializers.DateTimeField(allow_null=True)
    is_active = serializers.BooleanField()
    created_at = serializers.CharField(read_only=True)


class StockMovementSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    movement_type = serializers.CharField()
    status = serializers.CharField(read_only=True)
    reference_type = serializers.CharField(allow_blank=True, required=False)
    reference_id = serializers.CharField(allow_null=True, required=False)
    reference_number = serializers.CharField(allow_blank=True, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    performed_by = serializers.CharField()
    approved_by = serializers.CharField(allow_null=True, required=False)
    posted_at = serializers.DateTimeField(allow_null=True, read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class StockMovementListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    movement_type = serializers.CharField()
    status = serializers.CharField()
    reference_number = serializers.CharField(allow_blank=True)
    description = serializers.CharField(allow_blank=True)
    performed_by = serializers.CharField()
    posted_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.CharField(read_only=True)


class MovementLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    movement_id = serializers.CharField(read_only=True)
    inventory_item_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True, required=False)
    total_cost = serializers.DecimalField(max_digits=20, decimal_places=4, allow_null=True, required=False)
    batch_number = serializers.CharField(allow_blank=True, required=False)
    serial_number = serializers.CharField(allow_blank=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    line_number = serializers.IntegerField(default=0)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)


class StockAdjustmentSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    adjustment_type = serializers.CharField()
    status = serializers.CharField(read_only=True)
    reason = serializers.CharField()
    reference_number = serializers.CharField(allow_blank=True, required=False)
    performed_by = serializers.CharField()
    approved_by = serializers.CharField(allow_null=True, required=False)
    posted_at = serializers.DateTimeField(allow_null=True, read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class StockAdjustmentListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    adjustment_type = serializers.CharField()
    status = serializers.CharField()
    reason = serializers.CharField()
    reference_number = serializers.CharField(allow_blank=True)
    performed_by = serializers.CharField()
    posted_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.CharField(read_only=True)


class AdjustmentLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    adjustment_id = serializers.CharField(read_only=True)
    inventory_item_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity_before = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_after = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_delta = serializers.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True, required=False)
    batch_number = serializers.CharField(allow_blank=True, required=False)
    serial_number = serializers.CharField(allow_blank=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    line_number = serializers.IntegerField(default=0)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)


class StockTransferSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    source_warehouse_id = serializers.CharField()
    destination_warehouse_id = serializers.CharField()
    status = serializers.CharField(read_only=True)
    reference_number = serializers.CharField(allow_blank=True, required=False)
    description = serializers.CharField(allow_blank=True, required=False)
    performed_by = serializers.CharField()
    approved_by = serializers.CharField(allow_null=True, required=False)
    shipped_at = serializers.DateTimeField(allow_null=True, read_only=True)
    received_at = serializers.DateTimeField(allow_null=True, read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class StockTransferListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    source_warehouse_id = serializers.CharField()
    destination_warehouse_id = serializers.CharField()
    status = serializers.CharField()
    reference_number = serializers.CharField(allow_blank=True)
    description = serializers.CharField(allow_blank=True)
    performed_by = serializers.CharField()
    shipped_at = serializers.DateTimeField(allow_null=True)
    received_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.CharField(read_only=True)


class TransferLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    transfer_id = serializers.CharField(read_only=True)
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_received = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True, required=False)
    batch_number = serializers.CharField(allow_blank=True, required=False)
    serial_number = serializers.CharField(allow_blank=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    line_number = serializers.IntegerField(default=0)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)


class StockReservationSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    inventory_item_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    warehouse_id = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_allocated = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    status = serializers.CharField(read_only=True)
    reference_type = serializers.CharField(allow_blank=True, required=False)
    reference_id = serializers.CharField(allow_null=True, required=False)
    reference_line_id = serializers.CharField(allow_null=True, required=False)
    reserved_by = serializers.CharField()
    released_by = serializers.CharField(allow_null=True, required=False)
    expires_at = serializers.DateTimeField(allow_null=True, required=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class StockReservationListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    inventory_item_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True)
    warehouse_id = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_allocated = serializers.DecimalField(max_digits=18, decimal_places=3)
    status = serializers.CharField()
    reference_type = serializers.CharField(allow_blank=True)
    reference_id = serializers.CharField(allow_null=True)
    reserved_by = serializers.CharField()
    expires_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.CharField(read_only=True)


class CycleCountSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    zone_id = serializers.CharField(allow_null=True, required=False)
    count_type = serializers.CharField(default="scheduled")
    status = serializers.CharField(read_only=True)
    reference_number = serializers.CharField(allow_blank=True, required=False)
    scheduled_date = serializers.DateField()
    counted_by = serializers.CharField()
    verified_by = serializers.CharField(allow_null=True, required=False)
    variance_threshold_percent = serializers.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    notes = serializers.CharField(allow_blank=True, required=False)
    completed_at = serializers.DateTimeField(allow_null=True, read_only=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class CycleCountListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    zone_id = serializers.CharField(allow_null=True)
    count_type = serializers.CharField()
    status = serializers.CharField()
    reference_number = serializers.CharField(allow_blank=True)
    scheduled_date = serializers.DateField()
    counted_by = serializers.CharField()
    verified_by = serializers.CharField(allow_null=True)
    variance_threshold_percent = serializers.DecimalField(max_digits=5, decimal_places=2)
    completed_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.CharField(read_only=True)


class CycleCountLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    cycle_count_id = serializers.CharField(read_only=True)
    inventory_item_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    bin_location = serializers.CharField(allow_blank=True, required=False)
    system_quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    counted_quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    variance_quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True, required=False)
    variance_value = serializers.DecimalField(max_digits=20, decimal_places=4, allow_null=True, required=False)
    is_adjusted = serializers.BooleanField(default=False)
    batch_number = serializers.CharField(allow_blank=True, required=False)
    serial_number = serializers.CharField(allow_blank=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    line_number = serializers.IntegerField(default=0)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)


class StockBalanceSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    inventory_item_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True)
    snapshot_date = serializers.DateField()
    quantity_on_hand = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_reserved = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_available = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_in_transit = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_damaged = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_quarantine = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True, required=False)
    total_value = serializers.DecimalField(max_digits=20, decimal_places=4, allow_null=True, required=False)
    costing_method = serializers.CharField(allow_blank=True, required=False)
    is_finalized = serializers.BooleanField(default=False)
    created_at = serializers.CharField(read_only=True)


class StockBalanceListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    inventory_item_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True)
    snapshot_date = serializers.DateField()
    quantity_on_hand = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_reserved = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_available = serializers.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True)
    total_value = serializers.DecimalField(max_digits=20, decimal_places=4, allow_null=True)
    is_finalized = serializers.BooleanField()
    created_at = serializers.CharField(read_only=True)