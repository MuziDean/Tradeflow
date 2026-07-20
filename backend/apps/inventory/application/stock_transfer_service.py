"""
Application service for StockTransfer.

Business rules:
- Transfer Out creates movement from source warehouse
- Transfer In creates movement to destination warehouse
- Destination stock updated only on Receive
- Full audit trail via TransferLine
"""

import logging

from django.db import transaction

from apps.inventory.domain.entities import StockTransfer, TransferLine
from apps.inventory.infrastructure.repositories import (
    InventoryItemRepository,
    StockMovementRepository,
    StockTransferRepository,
    TransferLineRepository,
)
from shared.events.inventory_events import (
    StockTransferCancelled,
    StockTransferCreated,
    StockTransferReceived,
    StockTransferShipped,
)

logger = logging.getLogger("tradeflow.inventory")


class StockTransferService:
    """Service for StockTransfer."""

    def __init__(self, transfer_repository: StockTransferRepository,
                 line_repository: TransferLineRepository,
                 movement_repository: StockMovementRepository,
                 item_repository: InventoryItemRepository):
        self.transfer_repository = transfer_repository
        self.line_repository = line_repository
        self.movement_repository = movement_repository
        self.item_repository = item_repository

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str) -> list[StockTransfer]:
        return self.transfer_repository.list_for_warehouse(tenant_id, warehouse_id)

    def get_by_id(self, transfer_id: str, tenant_id: str) -> StockTransfer | None:
        return self.transfer_repository.get_by_id(transfer_id, tenant_id)

    def create(self, transfer: StockTransfer, lines: list[TransferLine]) -> StockTransfer:
        with transaction.atomic():
            created = self.transfer_repository.create(transfer)
            for line in lines:
                line.transfer_id = created.id
                self.line_repository.create(line)
            StockTransferCreated(
                tenant_id=transfer.tenant_id,
                transfer_id=created.id,
                source_warehouse_id=created.source_warehouse_id,
                destination_warehouse_id=created.destination_warehouse_id,
            ).emit()
            logger.info(f"StockTransfer created: {created.id} tenant={transfer.tenant_id}")
            return created

    def ship(self, transfer_id: str, tenant_id: str) -> StockTransfer | None:
        with transaction.atomic():
            transfer = self.transfer_repository.get_by_id(transfer_id, tenant_id)
            if not transfer or transfer.status != "draft":
                return None
            updated = self.transfer_repository.update(
                StockTransfer(
                    id=transfer.id,
                    tenant_id=transfer.tenant_id,
                    source_warehouse_id=transfer.source_warehouse_id,
                    destination_warehouse_id=transfer.destination_warehouse_id,
                    status="in_transit",
                    reference_number=transfer.reference_number,
                    description=transfer.description,
                    performed_by=transfer.performed_by,
                    approved_by=transfer.approved_by,
                    shipped_at=now(),
                    received_at=transfer.received_at,
                )
            )
            StockTransferShipped(
                tenant_id=tenant_id,
                transfer_id=transfer_id,
                source_warehouse_id=transfer.source_warehouse_id,
                destination_warehouse_id=transfer.destination_warehouse_id,
            ).emit()
            logger.info(f"StockTransfer shipped: {transfer_id} tenant={tenant_id}")
            return updated

    def receive(self, transfer_id: str, tenant_id: str) -> StockTransfer | None:
        with transaction.atomic():
            transfer = self.transfer_repository.get_by_id(transfer_id, tenant_id)
            if not transfer or transfer.status != "in_transit":
                return None
            updated = self.transfer_repository.update(
                StockTransfer(
                    id=transfer.id,
                    tenant_id=transfer.tenant_id,
                    source_warehouse_id=transfer.source_warehouse_id,
                    destination_warehouse_id=transfer.destination_warehouse_id,
                    status="completed",
                    reference_number=transfer.reference_number,
                    description=transfer.description,
                    performed_by=transfer.performed_by,
                    approved_by=transfer.approved_by,
                    shipped_at=transfer.shipped_at,
                    received_at=now(),
                )
            )
            lines = self.line_repository.list_for_transfer(tenant_id, transfer_id)
            for line in lines:
                self.item_repository.adjust_quantity(line.inventory_item_id, tenant_id, float(line.quantity))
            StockTransferReceived(
                tenant_id=tenant_id,
                transfer_id=transfer_id,
                source_warehouse_id=transfer.source_warehouse_id,
                destination_warehouse_id=transfer.destination_warehouse_id,
            ).emit()
            logger.info(f"StockTransfer received: {transfer_id} tenant={tenant_id}")
            return updated

    def cancel(self, transfer_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            transfer = self.transfer_repository.get_by_id(transfer_id, tenant_id)
            if not transfer or transfer.status != "draft":
                return False
            self.transfer_repository.update(
                StockTransfer(
                    id=transfer.id,
                    tenant_id=transfer.tenant_id,
                    source_warehouse_id=transfer.source_warehouse_id,
                    destination_warehouse_id=transfer.destination_warehouse_id,
                    status="cancelled",
                    reference_number=transfer.reference_number,
                    description=transfer.description,
                    performed_by=transfer.performed_by,
                    approved_by=transfer.approved_by,
                    shipped_at=transfer.shipped_at,
                    received_at=transfer.received_at,
                )
            )
            StockTransferCancelled(
                tenant_id=tenant_id,
                transfer_id=transfer_id,
                source_warehouse_id=transfer.source_warehouse_id,
                destination_warehouse_id=transfer.destination_warehouse_id,
            ).emit()
            logger.info(f"StockTransfer cancelled: {transfer_id} tenant={tenant_id}")
            return True


# Local import to avoid circular dependency
from shared.time.helpers import now