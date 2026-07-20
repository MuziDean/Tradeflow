"""
Application service for CycleCount.

Business rules:
- Creates cycle count headers and lines
- Generates StockAdjustment for variances exceeding threshold
- Full audit trail preserved
"""

import logging

from django.db import transaction

from apps.inventory.domain.entities import AdjustmentLine, CycleCount, CycleCountLine, StockAdjustment
from apps.inventory.infrastructure.repositories import (
    AdjustmentLineRepository,
    CycleCountLineRepository,
    CycleCountRepository,
    InventoryItemRepository,
    StockAdjustmentRepository,
)
from shared.events.inventory_events import CycleCountAdjusted, CycleCountCompleted, CycleCountStarted

logger = logging.getLogger("tradeflow.inventory")


class CycleCountService:
    """Service for CycleCount."""

    def __init__(self, cycle_count_repository: CycleCountRepository,
                 line_repository: CycleCountLineRepository,
                 adjustment_repository: StockAdjustmentRepository,
                 adjustment_line_repository: AdjustmentLineRepository,
                 item_repository: InventoryItemRepository):
        self.cycle_count_repository = cycle_count_repository
        self.line_repository = line_repository
        self.adjustment_repository = adjustment_repository
        self.adjustment_line_repository = adjustment_line_repository
        self.item_repository = item_repository

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str, status: str = "") -> list[CycleCount]:
        return self.cycle_count_repository.list_for_warehouse(tenant_id, warehouse_id, status)

    def get_by_id(self, cycle_count_id: str, tenant_id: str) -> CycleCount | None:
        return self.cycle_count_repository.get_by_id(cycle_count_id, tenant_id)

    def create(self, cycle_count: CycleCount, lines: list[CycleCountLine]) -> CycleCount:
        with transaction.atomic():
            created = self.cycle_count_repository.create(cycle_count)
            for line in lines:
                line.cycle_count_id = created.id
                self.line_repository.create(line)
            logger.info(f"CycleCount created: {created.id} warehouse={cycle_count.warehouse_id} tenant={cycle_count.tenant_id}")
            return created

    def start(self, cycle_count_id: str, tenant_id: str) -> CycleCount | None:
        with transaction.atomic():
            cycle_count = self.cycle_count_repository.get_by_id(cycle_count_id, tenant_id)
            if not cycle_count or cycle_count.status != "scheduled":
                return None
            updated = self.cycle_count_repository.update(
                CycleCount(
                    id=cycle_count.id,
                    tenant_id=cycle_count.tenant_id,
                    warehouse_id=cycle_count.warehouse_id,
                    zone_id=cycle_count.zone_id,
                    count_type=cycle_count.count_type,
                    status="in_progress",
                    reference_number=cycle_count.reference_number,
                    scheduled_date=cycle_count.scheduled_date,
                    counted_by=cycle_count.counted_by,
                    verified_by=cycle_count.verified_by,
                    variance_threshold_percent=cycle_count.variance_threshold_percent,
                    notes=cycle_count.notes,
                    completed_at=cycle_count.completed_at,
                )
            )
            CycleCountStarted(
                tenant_id=tenant_id,
                cycle_count_id=cycle_count_id,
                warehouse_id=cycle_count.warehouse_id,
            ).emit()
            logger.info(f"CycleCount started: {cycle_count_id} tenant={tenant_id}")
            return updated

    def complete(self, cycle_count_id: str, tenant_id: str, verified_by: str) -> CycleCount | None:
        with transaction.atomic():
            cycle_count = self.cycle_count_repository.get_by_id(cycle_count_id, tenant_id)
            if not cycle_count or cycle_count.status != "in_progress":
                return None
            updated = self.cycle_count_repository.update(
                CycleCount(
                    id=cycle_count.id,
                    tenant_id=cycle_count.tenant_id,
                    warehouse_id=cycle_count.warehouse_id,
                    zone_id=cycle_count.zone_id,
                    count_type=cycle_count.count_type,
                    status="completed",
                    reference_number=cycle_count.reference_number,
                    scheduled_date=cycle_count.scheduled_date,
                    counted_by=cycle_count.counted_by,
                    verified_by=verified_by,
                    variance_threshold_percent=cycle_count.variance_threshold_percent,
                    notes=cycle_count.notes,
                    completed_at=now(),
                )
            )
            CycleCountCompleted(
                tenant_id=tenant_id,
                cycle_count_id=cycle_count_id,
                warehouse_id=cycle_count.warehouse_id,
            ).emit()
            logger.info(f"CycleCount completed: {cycle_count_id} tenant={tenant_id}")
            return updated

    def record_line(self, cycle_count_id: str, tenant_id: str, line: CycleCountLine) -> CycleCountLine | None:
        with transaction.atomic():
            cycle_count = self.cycle_count_repository.get_by_id(cycle_count_id, tenant_id)
            if not cycle_count or cycle_count.status != "in_progress":
                return None
            line.cycle_count_id = cycle_count_id
            created = self.line_repository.create(line)
            logger.info(f"CycleCountLine recorded: {created.id} cycle_count={cycle_count_id} tenant={tenant_id}")
            return created

    def generate_adjustment(self, cycle_count_id: str, tenant_id: str) -> StockAdjustment | None:
        with transaction.atomic():
            cycle_count = self.cycle_count_repository.get_by_id(cycle_count_id, tenant_id)
            if not cycle_count or cycle_count.status != "completed":
                return None
            lines = self.line_repository.list_for_cycle_count(tenant_id, cycle_count_id)
            if not lines:
                return None
            adjustment = self.adjustment_repository.create(
                StockAdjustment(
                    tenant_id=tenant_id,
                    warehouse_id=cycle_count.warehouse_id,
                    adjustment_type="correction",
                    status="posted",
                    reason=f"Auto-generated from cycle count {cycle_count.reference_number}",
                    reference_number=f"CC-ADJ-{cycle_count.reference_number}",
                    performed_by=cycle_count.counted_by,
                    approved_by=cycle_count.verified_by,
                    posted_at=now(),
                )
            )
            for line in lines:
                if line.variance_quantity != 0:
                    self.adjustment_line_repository.create(
                        AdjustmentLine(
                            tenant_id=tenant_id,
                            adjustment_id=adjustment.id,
                            inventory_item_id=line.inventory_item_id,
                            product_id=line.product_id,
                            variant_id=line.variant_id,
                            quantity_before=line.system_quantity,
                            quantity_after=line.counted_quantity,
                            quantity_delta=line.variance_quantity,
                            unit_cost=line.unit_cost,
                            batch_number=line.batch_number,
                            serial_number=line.serial_number,
                            expiry_date=line.expiry_date,
                            line_number=line.line_number,
                            notes=f"Cycle count variance: system={line.system_quantity} counted={line.counted_quantity}",
                        )
                    )
                    self.item_repository.adjust_quantity(line.inventory_item_id, tenant_id, float(line.variance_quantity))
            self.cycle_count_repository.update(
                CycleCount(
                    id=cycle_count.id,
                    tenant_id=cycle_count.tenant_id,
                    warehouse_id=cycle_count.warehouse_id,
                    zone_id=cycle_count.zone_id,
                    count_type=cycle_count.count_type,
                    status="adjusted",
                    reference_number=cycle_count.reference_number,
                    scheduled_date=cycle_count.scheduled_date,
                    counted_by=cycle_count.counted_by,
                    verified_by=cycle_count.verified_by,
                    variance_threshold_percent=cycle_count.variance_threshold_percent,
                    notes=cycle_count.notes,
                    completed_at=cycle_count.completed_at,
                )
            )
            CycleCountAdjusted(
                tenant_id=tenant_id,
                cycle_count_id=cycle_count_id,
                warehouse_id=cycle_count.warehouse_id,
                adjustment_id=adjustment.id,
            ).emit()
            logger.info(f"CycleCount adjustment generated: {adjustment.id} from cycle_count={cycle_count_id} tenant={tenant_id}")
            return adjustment


# Local import to avoid circular dependency
from shared.time.helpers import now