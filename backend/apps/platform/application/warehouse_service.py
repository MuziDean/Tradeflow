"""
Application service for Warehouse management.

Domain events emitted:
- WarehouseCreated
"""

import logging

from django.db import transaction

from apps.platform.domain.entities import Warehouse
from apps.platform.infrastructure.repositories import WarehouseRepository
from shared.events.warehouse_events import WarehouseCreated

logger = logging.getLogger("tradeflow.platform")


class WarehouseService:
    """Service for Warehouse management."""

    def __init__(self, warehouse_repository: WarehouseRepository):
        self.warehouse_repository = warehouse_repository

    def list_warehouses(self, tenant_id: str, branch_id: str) -> list[Warehouse]:
        return self.warehouse_repository.list_for_branch(tenant_id, branch_id)

    def get_warehouse(self, warehouse_id: str, tenant_id: str) -> Warehouse | None:
        return self.warehouse_repository.get_by_id(warehouse_id, tenant_id)

    def create_warehouse(self, warehouse: Warehouse) -> Warehouse:
        with transaction.atomic():
            created = self.warehouse_repository.create(warehouse)
            WarehouseCreated(
                tenant_id=warehouse.tenant_id, warehouse_id=created.id, name=created.name
            ).emit()
            return created

    def update_warehouse(self, warehouse: Warehouse) -> Warehouse:
        with transaction.atomic():
            return self.warehouse_repository.update(warehouse)

    def delete_warehouse(self, warehouse_id: str, tenant_id: str) -> bool:
        return self.warehouse_repository.soft_delete(warehouse_id, tenant_id)