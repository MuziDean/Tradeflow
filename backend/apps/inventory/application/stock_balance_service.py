"""
Application service for StockBalance.

Business rules:
- Snapshot captures stock state at a point in time
- Used for historical reporting and reconciliation
- Created by scheduled/daily jobs or ad-hoc queries
"""

import logging
from datetime import date

from apps.inventory.domain.entities import StockBalance
from apps.inventory.infrastructure.repositories import InventoryItemRepository, StockBalanceRepository
from shared.events.inventory_events import StockSnapshotCreated

logger = logging.getLogger("tradeflow.inventory")


class StockBalanceService:
    """Service for StockBalance."""

    def __init__(self, balance_repository: StockBalanceRepository,
                 item_repository: InventoryItemRepository):
        self.balance_repository = balance_repository
        self.item_repository = item_repository

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str,
                           date_from: str = "", date_to: str = "") -> list[StockBalance]:
        return self.balance_repository.list_for_warehouse(tenant_id, warehouse_id, date_from, date_to)

    def get_for_item_date(self, inventory_item_id: str, tenant_id: str, snapshot_date: str) -> StockBalance | None:
        return self.balance_repository.get_for_item_date(inventory_item_id, tenant_id, snapshot_date)

    def generate_daily_snapshot(self, tenant_id: str, warehouse_id: str, snapshot_date: str = "") -> list[StockBalance]:
        """Generate daily stock balance snapshots for all active inventory items in a warehouse."""
        if not snapshot_date:
            snapshot_date = str(date.today())
        items = self.item_repository.list_for_warehouse(tenant_id, warehouse_id, active_only=True)
        snapshots = []
        for item in items:
            existing = self.balance_repository.get_for_item_date(item.id, tenant_id, snapshot_date)
            if existing:
                continue
            snapshot = self.balance_repository.create(
                StockBalance(
                    tenant_id=tenant_id,
                    inventory_item_id=item.id,
                    warehouse_id=warehouse_id,
                    product_id=item.product_id,
                    variant_id=item.variant_id,
                    snapshot_date=snapshot_date,
                    quantity_on_hand=item.quantity_on_hand,
                    quantity_reserved=item.quantity_reserved,
                    quantity_available=item.quantity_available,
                    quantity_in_transit=item.quantity_in_transit,
                    quantity_damaged=item.quantity_damaged,
                    quantity_quarantine=item.quantity_quarantine,
                )
            )
            StockSnapshotCreated(
                tenant_id=tenant_id,
                balance_id=snapshot.id,
                inventory_item_id=item.id,
                snapshot_date=snapshot_date,
            ).emit()
            snapshots.append(snapshot)
        logger.info(f"Generated {len(snapshots)} stock snapshots for warehouse={warehouse_id} date={snapshot_date} tenant={tenant_id}")
        return snapshots