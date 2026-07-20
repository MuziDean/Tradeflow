"""
Application service for StockAdjustment.

Business rules:
- Adjustments always produce Stock Movements
- Full audit trail via AdjustmentLine
- Supports damage, loss, found, write-off, manual corrections
"""

import logging

from django.db import transaction

from apps.inventory.domain.entities import AdjustmentLine, StockAdjustment, StockMovement
from apps.inventory.infrastructure.repositories import (
    AdjustmentLineRepository,
    InventoryItemRepository,
    StockAdjustmentRepository,
    StockMovementRepository,
)
from shared.events.inventory_events import StockAdjustmentPosted, StockAdjustmentCreated

logger = logging.getLogger("tradeflow.inventory")


class StockAdjustmentService:
    """Service for StockAdjustment."""

    def __init__(self, adjustment_repository: StockAdjustmentRepository,
                 line_repository: AdjustmentLineRepository,
                 movement_repository: StockMovementRepository,
                 item_repository: InventoryItemRepository):
        self.adjustment_repository = adjustment_repository
        self.line_repository = line_repository
        self.movement_repository = movement_repository
        self.item_repository = item_repository

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str) -> list[StockAdjustment]:
        return self.adjustment_repository.list_for_warehouse(tenant_id, warehouse_id)

    def get_by_id(self, adjustment_id: str, tenant_id: str) -> StockAdjustment | None:
        return self.adjustment_repository.get_by_id(adjustment_id, tenant_id)

    def create(self, adjustment: StockAdjustment, lines: list[AdjustmentLine]) -> StockAdjustment:
        with transaction.atomic():
            created = self.adjustment_repository.create(adjustment)
            for line in lines:
                line.adjustment_id = created.id
                self.line_repository.create(line)
            StockAdjustmentCreated(
                tenant_id=adjustment.tenant_id,
                adjustment_id=created.id,
                warehouse_id=created.warehouse_id,
                adjustment_type=created.adjustment_type,
            ).emit()
            logger.info(f"StockAdjustment created: {created.id} type={created.adjustment_type} tenant={adjustment.tenant_id}")
            return created

    def post(self, adjustment_id: str, tenant_id: str, approved_by: str) -> StockAdjustment | None:
        with transaction.atomic():
            adjustment = self.adjustment_repository.get_by_id(adjustment_id, tenant_id)
            if not adjustment or adjustment.status != "draft":
                return None
            updated = self.adjustment_repository.update(
                StockAdjustment(
                    id=adjustment.id,
                    tenant_id=adjustment.tenant_id,
                    warehouse_id=adjustment.warehouse_id,
                    adjustment_type=adjustment.adjustment_type,
                    status="posted",
                    reason=adjustment.reason,
                    reference_number=adjustment.reference_number,
                    performed_by=adjustment.performed_by,
                    approved_by=approved_by,
                    posted_at=now(),
                )
            )
            lines = self.line_repository.list_for_adjustment(tenant_id, adjustment_id)
            for line in lines:
                self.item_repository.adjust_quantity(line.inventory_item_id, tenant_id, float(line.quantity_delta))
            StockAdjustmentPosted(
                tenant_id=tenant_id,
                adjustment_id=adjustment_id,
                warehouse_id=adjustment.warehouse_id,
                adjustment_type=adjustment.adjustment_type,
            ).emit()
            logger.info(f"StockAdjustment posted: {adjustment_id} tenant={tenant_id}")
            return updated


# Local import to avoid circular dependency
from shared.time.helpers import now