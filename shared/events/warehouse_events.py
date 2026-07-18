"""
Warehouse domain events.

Emitted by WarehouseService on state changes.
"""

from shared.events.base import DomainEvent


class WarehouseCreated(DomainEvent):
    def __init__(self, tenant_id: str, warehouse_id: str, name: str):
        super().__init__(
            "warehouse.created",
            {"tenant_id": tenant_id, "warehouse_id": warehouse_id, "name": name},
        )