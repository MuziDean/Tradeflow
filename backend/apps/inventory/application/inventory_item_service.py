"""
Application service for InventoryItem.
"""

import logging

from django.db import transaction

from apps.inventory.domain.entities import InventoryItem
from apps.inventory.infrastructure.repositories import InventoryItemRepository
from shared.events.inventory_events import (
    InventoryItemArchived,
    InventoryItemCreated,
    InventoryItemUpdated,
)

logger = logging.getLogger("tradeflow.inventory")


class InventoryItemService:
    """Service for InventoryItem."""

    def __init__(self, item_repository: InventoryItemRepository):
        self.item_repository = item_repository

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str, active_only: bool = True) -> list[InventoryItem]:
        return self.item_repository.list_for_warehouse(tenant_id, warehouse_id, active_only)

    def list_for_product(self, tenant_id: str, product_id: str) -> list[InventoryItem]:
        return self.item_repository.list_for_product(tenant_id, product_id)

    def get_by_id(self, item_id: str, tenant_id: str) -> InventoryItem | None:
        return self.item_repository.get_by_id(item_id, tenant_id)

    def get_by_product(self, tenant_id: str, warehouse_id: str, product_id: str,
                       variant_id: str | None = None, batch_number: str = "", serial_number: str = "") -> InventoryItem | None:
        return self.item_repository.get_by_product(tenant_id, warehouse_id, product_id, variant_id, batch_number, serial_number)

    def create(self, item: InventoryItem) -> InventoryItem:
        with transaction.atomic():
            created = self.item_repository.create(item)
            InventoryItemCreated(
                tenant_id=item.tenant_id,
                item_id=created.id,
                warehouse_id=created.warehouse_id,
                product_id=created.product_id,
                variant_id=created.variant_id,
            ).emit()
            logger.info(f"InventoryItem created: {created.id} warehouse={item.warehouse_id} product={item.product_id} tenant={item.tenant_id}")
            return created

    def update(self, item: InventoryItem) -> InventoryItem:
        with transaction.atomic():
            updated = self.item_repository.update(item)
            InventoryItemUpdated(
                tenant_id=item.tenant_id,
                item_id=updated.id,
                warehouse_id=updated.warehouse_id,
                product_id=updated.product_id,
            ).emit()
            logger.info(f"InventoryItem updated: {updated.id} warehouse={item.warehouse_id} product={item.product_id} tenant={item.tenant_id}")
            return updated

    def archive(self, item_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            item = self.item_repository.get_by_id(item_id, tenant_id)
            if not item:
                return False
            updated = self.item_repository.update(
                InventoryItem(
                    id=item.id,
                    tenant_id=item.tenant_id,
                    warehouse_id=item.warehouse_id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    quantity_on_hand=item.quantity_on_hand,
                    quantity_reserved=item.quantity_reserved,
                    quantity_available=item.quantity_available,
                    quantity_in_transit=item.quantity_in_transit,
                    quantity_committed=item.quantity_committed,
                    quantity_damaged=item.quantity_damaged,
                    quantity_quarantine=item.quantity_quarantine,
                    reorder_point=item.reorder_point,
                    reorder_quantity=item.reorder_quantity,
                    preferred_supplier_id=item.preferred_supplier_id,
                    batch_number=item.batch_number,
                    lot_number=item.lot_number,
                    serial_number=item.serial_number,
                    expiry_date=item.expiry_date,
                    manufacturing_date=item.manufacturing_date,
                    last_stocked_at=item.last_stocked_at,
                    last_counted_at=item.last_counted_at,
                    last_movement_at=item.last_movement_at,
                    is_active=False,
                )
            )
            InventoryItemArchived(
                tenant_id=tenant_id,
                item_id=item_id,
                warehouse_id=item.warehouse_id,
                product_id=item.product_id,
            ).emit()
            logger.info(f"InventoryItem archived: {item_id} tenant={tenant_id}")
            return True

    def adjust_quantity(self, item_id: str, tenant_id: str, delta: float) -> InventoryItem | None:
        with transaction.atomic():
            updated = self.item_repository.adjust_quantity(item_id, tenant_id, delta)
            if updated:
                logger.info(f"InventoryItem quantity adjusted: {item_id} delta={delta} tenant={tenant_id}")
            return updated