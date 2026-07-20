"""
Application service for StockReservation.

Business rules:
- Reserved quantity reduces available quantity
- Available quantity must never go negative
- Supports partial allocations
- Reservation lifecycle: Pending → Allocated → Released → Completed
"""

import logging

from django.db import transaction

from apps.inventory.domain.entities import StockReservation
from apps.inventory.infrastructure.repositories import InventoryItemRepository, StockReservationRepository
from shared.events.inventory_events import (
    ReservationAllocated,
    ReservationCancelled,
    ReservationCompleted,
    ReservationCreated,
    ReservationReleased,
)

logger = logging.getLogger("tradeflow.inventory")


class StockReservationService:
    """Service for StockReservation."""

    def __init__(self, reservation_repository: StockReservationRepository,
                 item_repository: InventoryItemRepository):
        self.reservation_repository = reservation_repository
        self.item_repository = item_repository

    def list_for_inventory_item(self, tenant_id: str, inventory_item_id: str) -> list[StockReservation]:
        return self.reservation_repository.list_for_inventory_item(tenant_id, inventory_item_id)

    def list_for_reference(self, tenant_id: str, reference_type: str, reference_id: str) -> list[StockReservation]:
        return self.reservation_repository.list_for_reference(tenant_id, reference_type, reference_id)

    def get_by_id(self, reservation_id: str, tenant_id: str) -> StockReservation | None:
        return self.reservation_repository.get_by_id(reservation_id, tenant_id)

    def create(self, reservation: StockReservation) -> StockReservation:
        with transaction.atomic():
            item = self.item_repository.get_by_id(reservation.inventory_item_id, reservation.tenant_id)
            if not item or item.quantity_available < reservation.quantity:
                raise ValueError("Insufficient available quantity for reservation.")
            created = self.reservation_repository.create(reservation)
            self.item_repository.adjust_quantity(reservation.inventory_item_id, reservation.tenant_id, -float(reservation.quantity))
            ReservationCreated(
                tenant_id=reservation.tenant_id,
                reservation_id=created.id,
                inventory_item_id=reservation.inventory_item_id,
                quantity=str(reservation.quantity),
            ).emit()
            logger.info(f"StockReservation created: {created.id} item={reservation.inventory_item_id} tenant={reservation.tenant_id}")
            return created

    def allocate(self, reservation_id: str, tenant_id: str, quantity_allocated: float) -> StockReservation | None:
        with transaction.atomic():
            reservation = self.reservation_repository.get_by_id(reservation_id, tenant_id)
            if not reservation or reservation.status != "pending":
                return None
            updated = self.reservation_repository.update(
                StockReservation(
                    id=reservation.id,
                    tenant_id=reservation.tenant_id,
                    inventory_item_id=reservation.inventory_item_id,
                    product_id=reservation.product_id,
                    variant_id=reservation.variant_id,
                    warehouse_id=reservation.warehouse_id,
                    quantity=reservation.quantity,
                    quantity_allocated=quantity_allocated,
                    status="allocated",
                    reference_type=reservation.reference_type,
                    reference_id=reservation.reference_id,
                    reference_line_id=reservation.reference_line_id,
                    reserved_by=reservation.reserved_by,
                    released_by=reservation.released_by,
                    expires_at=reservation.expires_at,
                )
            )
            ReservationAllocated(
                tenant_id=tenant_id,
                reservation_id=reservation_id,
                inventory_item_id=reservation.inventory_item_id,
                quantity_allocated=str(quantity_allocated),
            ).emit()
            logger.info(f"StockReservation allocated: {reservation_id} tenant={tenant_id}")
            return updated

    def release(self, reservation_id: str, tenant_id: str) -> StockReservation | None:
        with transaction.atomic():
            reservation = self.reservation_repository.get_by_id(reservation_id, tenant_id)
            if not reservation or reservation.status not in ("pending", "allocated"):
                return None
            remaining = reservation.quantity - reservation.quantity_allocated
            self.item_repository.adjust_quantity(reservation.inventory_item_id, tenant_id, float(remaining))
            updated = self.reservation_repository.update(
                StockReservation(
                    id=reservation.id,
                    tenant_id=reservation.tenant_id,
                    inventory_item_id=reservation.inventory_item_id,
                    product_id=reservation.product_id,
                    variant_id=reservation.variant_id,
                    warehouse_id=reservation.warehouse_id,
                    quantity=reservation.quantity,
                    quantity_allocated=reservation.quantity_allocated,
                    status="released",
                    reference_type=reservation.reference_type,
                    reference_id=reservation.reference_id,
                    reference_line_id=reservation.reference_line_id,
                    reserved_by=reservation.reserved_by,
                    released_by=reservation.released_by,
                    expires_at=reservation.expires_at,
                )
            )
            ReservationReleased(
                tenant_id=tenant_id,
                reservation_id=reservation_id,
                inventory_item_id=reservation.inventory_item_id,
            ).emit()
            logger.info(f"StockReservation released: {reservation_id} tenant={tenant_id}")
            return updated

    def complete(self, reservation_id: str, tenant_id: str) -> StockReservation | None:
        with transaction.atomic():
            reservation = self.reservation_repository.get_by_id(reservation_id, tenant_id)
            if not reservation:
                return None
            updated = self.reservation_repository.update(
                StockReservation(
                    id=reservation.id,
                    tenant_id=reservation.tenant_id,
                    inventory_item_id=reservation.inventory_item_id,
                    product_id=reservation.product_id,
                    variant_id=reservation.variant_id,
                    warehouse_id=reservation.warehouse_id,
                    quantity=reservation.quantity,
                    quantity_allocated=reservation.quantity_allocated,
                    status="completed",
                    reference_type=reservation.reference_type,
                    reference_id=reservation.reference_id,
                    reference_line_id=reservation.reference_line_id,
                    reserved_by=reservation.reserved_by,
                    released_by=reservation.released_by,
                    expires_at=reservation.expires_at,
                )
            )
            ReservationCompleted(
                tenant_id=tenant_id,
                reservation_id=reservation_id,
                inventory_item_id=reservation.inventory_item_id,
            ).emit()
            logger.info(f"StockReservation completed: {reservation_id} tenant={tenant_id}")
            return updated

    def cancel(self, reservation_id: str, tenant_id: str) -> StockReservation | None:
        with transaction.atomic():
            reservation = self.reservation_repository.get_by_id(reservation_id, tenant_id)
            if not reservation or reservation.status not in ("pending", "allocated"):
                return None
            remaining = reservation.quantity - reservation.quantity_allocated
            self.item_repository.adjust_quantity(reservation.inventory_item_id, tenant_id, float(remaining))
            updated = self.reservation_repository.update(
                StockReservation(
                    id=reservation.id,
                    tenant_id=reservation.tenant_id,
                    inventory_item_id=reservation.inventory_item_id,
                    product_id=reservation.product_id,
                    variant_id=reservation.variant_id,
                    warehouse_id=reservation.warehouse_id,
                    quantity=reservation.quantity,
                    quantity_allocated=reservation.quantity_allocated,
                    status="cancelled",
                    reference_type=reservation.reference_type,
                    reference_id=reservation.reference_id,
                    reference_line_id=reservation.reference_line_id,
                    reserved_by=reservation.reserved_by,
                    released_by=reservation.released_by,
                    expires_at=reservation.expires_at,
                )
            )
            ReservationCancelled(
                tenant_id=tenant_id,
                reservation_id=reservation_id,
                inventory_item_id=reservation.inventory_item_id,
            ).emit()
            logger.info(f"StockReservation cancelled: {reservation_id} tenant={tenant_id}")
            return updated