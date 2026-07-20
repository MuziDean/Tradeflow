"""
Domain events for the inventory module.

All events inherit from the shared DomainEvent base class and represent
immutable business facts that application services emit after successful
transaction commits.
"""

from shared.events.base import DomainEvent


class InventoryItemCreated(DomainEvent):
    """Emitted when a new inventory item is created."""

    def __init__(self, tenant_id: str, item_id: str, warehouse_id: str, product_id: str, variant_id: str | None):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=item_id,
            aggregate_type="InventoryItem",
            event_data={"warehouse_id": warehouse_id, "product_id": product_id, "variant_id": variant_id},
        )


class InventoryItemUpdated(DomainEvent):
    """Emitted when an inventory item is updated."""

    def __init__(self, tenant_id: str, item_id: str, warehouse_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=item_id,
            aggregate_type="InventoryItem",
            event_data={"warehouse_id": warehouse_id, "product_id": product_id},
        )


class InventoryItemArchived(DomainEvent):
    """Emitted when an inventory item is archived."""

    def __init__(self, tenant_id: str, item_id: str, warehouse_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=item_id,
            aggregate_type="InventoryItem",
            event_data={"warehouse_id": warehouse_id, "product_id": product_id},
        )


class StockSnapshotCreated(DomainEvent):
    """Emitted when a stock balance snapshot is created."""

    def __init__(self, tenant_id: str, balance_id: str, inventory_item_id: str, snapshot_date: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=balance_id,
            aggregate_type="StockBalance",
            event_data={"inventory_item_id": inventory_item_id, "snapshot_date": snapshot_date},
        )


class StockMovementCreated(DomainEvent):
    """Emitted when a stock movement is created."""

    def __init__(self, tenant_id: str, movement_id: str, warehouse_id: str, movement_type: str, status: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=movement_id,
            aggregate_type="StockMovement",
            event_data={"warehouse_id": warehouse_id, "movement_type": movement_type, "status": status},
        )


class StockMovementPosted(DomainEvent):
    """Emitted when a stock movement is posted."""

    def __init__(self, tenant_id: str, movement_id: str, warehouse_id: str, movement_type: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=movement_id,
            aggregate_type="StockMovement",
            event_data={"warehouse_id": warehouse_id, "movement_type": movement_type},
        )


class StockMovementCancelled(DomainEvent):
    """Emitted when a stock movement is cancelled."""

    def __init__(self, tenant_id: str, movement_id: str, warehouse_id: str, movement_type: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=movement_id,
            aggregate_type="StockMovement",
            event_data={"warehouse_id": warehouse_id, "movement_type": movement_type},
        )


class StockAdjustmentCreated(DomainEvent):
    """Emitted when a stock adjustment is created."""

    def __init__(self, tenant_id: str, adjustment_id: str, warehouse_id: str, adjustment_type: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=adjustment_id,
            aggregate_type="StockAdjustment",
            event_data={"warehouse_id": warehouse_id, "adjustment_type": adjustment_type},
        )


class StockAdjustmentPosted(DomainEvent):
    """Emitted when a stock adjustment is posted."""

    def __init__(self, tenant_id: str, adjustment_id: str, warehouse_id: str, adjustment_type: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=adjustment_id,
            aggregate_type="StockAdjustment",
            event_data={"warehouse_id": warehouse_id, "adjustment_type": adjustment_type},
        )


class StockTransferCreated(DomainEvent):
    """Emitted when a stock transfer is created."""

    def __init__(self, tenant_id: str, transfer_id: str, source_warehouse_id: str, destination_warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=transfer_id,
            aggregate_type="StockTransfer",
            event_data={"source_warehouse_id": source_warehouse_id, "destination_warehouse_id": destination_warehouse_id},
        )


class StockTransferShipped(DomainEvent):
    """Emitted when a stock transfer is shipped."""

    def __init__(self, tenant_id: str, transfer_id: str, source_warehouse_id: str, destination_warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=transfer_id,
            aggregate_type="StockTransfer",
            event_data={"source_warehouse_id": source_warehouse_id, "destination_warehouse_id": destination_warehouse_id},
        )


class StockTransferReceived(DomainEvent):
    """Emitted when a stock transfer is received."""

    def __init__(self, tenant_id: str, transfer_id: str, source_warehouse_id: str, destination_warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=transfer_id,
            aggregate_type="StockTransfer",
            event_data={"source_warehouse_id": source_warehouse_id, "destination_warehouse_id": destination_warehouse_id},
        )


class StockTransferCancelled(DomainEvent):
    """Emitted when a stock transfer is cancelled."""

    def __init__(self, tenant_id: str, transfer_id: str, source_warehouse_id: str, destination_warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=transfer_id,
            aggregate_type="StockTransfer",
            event_data={"source_warehouse_id": source_warehouse_id, "destination_warehouse_id": destination_warehouse_id},
        )


class ReservationCreated(DomainEvent):
    """Emitted when a stock reservation is created."""

    def __init__(self, tenant_id: str, reservation_id: str, inventory_item_id: str, quantity: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=reservation_id,
            aggregate_type="StockReservation",
            event_data={"inventory_item_id": inventory_item_id, "quantity": quantity},
        )


class ReservationAllocated(DomainEvent):
    """Emitted when a stock reservation is allocated."""

    def __init__(self, tenant_id: str, reservation_id: str, inventory_item_id: str, quantity_allocated: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=reservation_id,
            aggregate_type="StockReservation",
            event_data={"inventory_item_id": inventory_item_id, "quantity_allocated": quantity_allocated},
        )


class ReservationReleased(DomainEvent):
    """Emitted when a stock reservation is released."""

    def __init__(self, tenant_id: str, reservation_id: str, inventory_item_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=reservation_id,
            aggregate_type="StockReservation",
            event_data={"inventory_item_id": inventory_item_id},
        )


class ReservationCompleted(DomainEvent):
    """Emitted when a stock reservation is completed."""

    def __init__(self, tenant_id: str, reservation_id: str, inventory_item_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=reservation_id,
            aggregate_type="StockReservation",
            event_data={"inventory_item_id": inventory_item_id},
        )


class ReservationCancelled(DomainEvent):
    """Emitted when a stock reservation is cancelled."""

    def __init__(self, tenant_id: str, reservation_id: str, inventory_item_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=reservation_id,
            aggregate_type="StockReservation",
            event_data={"inventory_item_id": inventory_item_id},
        )


class CycleCountStarted(DomainEvent):
    """Emitted when a cycle count is started."""

    def __init__(self, tenant_id: str, cycle_count_id: str, warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=cycle_count_id,
            aggregate_type="CycleCount",
            event_data={"warehouse_id": warehouse_id},
        )


class CycleCountCompleted(DomainEvent):
    """Emitted when a cycle count is completed."""

    def __init__(self, tenant_id: str, cycle_count_id: str, warehouse_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=cycle_count_id,
            aggregate_type="CycleCount",
            event_data={"warehouse_id": warehouse_id},
        )


class CycleCountAdjusted(DomainEvent):
    """Emitted when a cycle count generates an adjustment."""

    def __init__(self, tenant_id: str, cycle_count_id: str, warehouse_id: str, adjustment_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=cycle_count_id,
            aggregate_type="CycleCount",
            event_data={"warehouse_id": warehouse_id, "adjustment_id": adjustment_id},
        )