"""
Application service for StockMovement.

Business rules:
- Movement starts as Draft
- Only Posted movements affect stock
- Cancelled movements never affect stock
- Posted movements become immutable
- Every posting updates InventoryItem quantities
"""

import logging

from django.db import transaction

from apps.inventory.domain.entities import MovementLine, StockMovement
from apps.inventory.infrastructure.repositories import InventoryItemRepository, MovementLineRepository, StockMovementRepository
from shared.events.inventory_events import (
    StockMovementCancelled,
    StockMovementCreated,
    StockMovementPosted,
)
from shared.types.enums import MovementStatus

logger = logging.getLogger("tradeflow.inventory")


class StockMovementService:
    """Service for StockMovement."""

    def __init__(self, movement_repository: StockMovementRepository,
                 line_repository: MovementLineRepository,
                 item_repository: InventoryItemRepository):
        self.movement_repository = movement_repository
        self.line_repository = line_repository
        self.item_repository = item_repository

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str,
                           movement_type: str = "", status: str = "") -> list[StockMovement]:
        return self.movement_repository.list_for_warehouse(tenant_id, warehouse_id, movement_type, status)

    def get_by_id(self, movement_id: str, tenant_id: str) -> StockMovement | None:
        return self.movement_repository.get_by_id(movement_id, tenant_id)

    def create(self, movement: StockMovement, lines: list[MovementLine]) -> StockMovement:
        with transaction.atomic():
            created = self.movement_repository.create(movement)
            for line in lines:
                line.movement_id = created.id
                self.line_repository.create(line)
            StockMovementCreated(
                tenant_id=movement.tenant_id,
                movement_id=created.id,
                warehouse_id=created.warehouse_id,
                movement_type=created.movement_type,
                status=created.status,
            ).emit()
            logger.info(f"StockMovement created: {created.id} type={created.movement_type} tenant={movement.tenant_id}")
            return created

    def post(self, movement_id: str, tenant_id: str) -> StockMovement | None:
        with transaction.atomic():
            movement = self.movement_repository.get_by_id(movement_id, tenant_id)
            if not movement or movement.status != MovementStatus.DRAFT:
                return None
            updated = self.movement_repository.update(
                StockMovement(
                    id=movement.id,
                    tenant_id=movement.tenant_id,
                    warehouse_id=movement.warehouse_id,
                    movement_type=movement.movement_type,
                    status=MovementStatus.POSTED,
                    reference_type=movement.reference_type,
                    reference_id=movement.reference_id,
                    reference_number=movement.reference_number,
                    description=movement.description,
                    performed_by=movement.performed_by,
                    approved_by=movement.approved_by,
                    posted_at=now(),
                )
            )
            lines = self.line_repository.list_for_movement(tenant_id, movement_id)
            for line in lines:
                self.item_repository.adjust_quantity(line.inventory_item_id, tenant_id, float(line.quantity))
            StockMovementPosted(
                tenant_id=tenant_id,
                movement_id=movement_id,
                warehouse_id=movement.warehouse_id,
                movement_type=movement.movement_type,
            ).emit()
            logger.info(f"StockMovement posted: {movement_id} tenant={tenant_id}")
            return updated

    def cancel(self, movement_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            movement = self.movement_repository.get_by_id(movement_id, tenant_id)
            if not movement or movement.status != MovementStatus.DRAFT:
                return False
            self.movement_repository.update(
                StockMovement(
                    id=movement.id,
                    tenant_id=movement.tenant_id,
                    warehouse_id=movement.warehouse_id,
                    movement_type=movement.movement_type,
                    status=MovementStatus.CANCELLED,
                    reference_type=movement.reference_type,
                    reference_id=movement.reference_id,
                    reference_number=movement.reference_number,
                    description=movement.description,
                    performed_by=movement.performed_by,
                    approved_by=movement.approved_by,
                    posted_at=movement.posted_at,
                )
            )
            StockMovementCancelled(
                tenant_id=tenant_id,
                movement_id=movement_id,
                warehouse_id=movement.warehouse_id,
                movement_type=movement.movement_type,
            ).emit()
            logger.info(f"StockMovement cancelled: {movement_id} tenant={tenant_id}")
            return True


# Local import to avoid circular dependency
from shared.time.helpers import now