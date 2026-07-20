"""
Repository implementations for the inventory module.

These repositories contain persistence operations only. No business logic is
implemented here. Inventory owns stock; Retail owns products.
"""

from apps.inventory.domain.entities import (
    AdjustmentLine,
    CycleCount,
    CycleCountLine,
    InventoryItem,
    MovementLine,
    StockAdjustment,
    StockBalance,
    StockMovement,
    StockReservation,
    StockTransfer,
    TransferLine,
)
from apps.inventory.infrastructure.models import (
    AdjustmentLineModel,
    CycleCountLineModel,
    CycleCountModel,
    InventoryItemModel,
    MovementLineModel,
    StockAdjustmentModel,
    StockBalanceModel,
    StockMovementModel,
    StockReservationModel,
    StockTransferModel,
    TransferLineModel,
)


class InventoryItemRepository:
    """Repository for InventoryItem."""

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str, active_only: bool = True) -> list[InventoryItem]:
        qs = InventoryItemModel.objects.filter(tenant_id=tenant_id, warehouse_id=warehouse_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_entity(m) for m in qs]

    def list_for_product(self, tenant_id: str, product_id: str) -> list[InventoryItem]:
        return [self._to_entity(m) for m in InventoryItemModel.objects.filter(tenant_id=tenant_id, product_id=product_id)]

    def get_by_id(self, item_id: str, tenant_id: str) -> InventoryItem | None:
        try:
            return self._to_entity(InventoryItemModel.objects.get(id=item_id, tenant_id=tenant_id))
        except InventoryItemModel.DoesNotExist:
            return None

    def get_by_product(self, tenant_id: str, warehouse_id: str, product_id: str, variant_id: str | None = None,
                       batch_number: str = "", serial_number: str = "") -> InventoryItem | None:
        try:
            qs = InventoryItemModel.objects.filter(
                tenant_id=tenant_id, warehouse_id=warehouse_id, product_id=product_id
            )
            if variant_id:
                qs = qs.filter(variant_id=variant_id)
            if batch_number:
                qs = qs.filter(batch_number=batch_number)
            if serial_number:
                qs = qs.filter(serial_number=serial_number)
            return self._to_entity(qs.get())
        except InventoryItemModel.DoesNotExist:
            return None

    def create(self, item: InventoryItem) -> InventoryItem:
        model = InventoryItemModel(
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
            batch_number=item.batch_number or "",
            lot_number=item.lot_number or "",
            serial_number=item.serial_number or "",
            expiry_date=item.expiry_date,
            manufacturing_date=item.manufacturing_date,
            last_stocked_at=item.last_stocked_at,
            last_counted_at=item.last_counted_at,
            last_movement_at=item.last_movement_at,
            is_active=item.is_active,
        )
        model.save()
        return self._to_entity(model)

    def update(self, item: InventoryItem) -> InventoryItem:
        model = InventoryItemModel.objects.get(id=item.id, tenant_id=item.tenant_id)
        model.warehouse_id = item.warehouse_id
        model.product_id = item.product_id
        model.variant_id = item.variant_id
        model.quantity_on_hand = item.quantity_on_hand
        model.quantity_reserved = item.quantity_reserved
        model.quantity_available = item.quantity_available
        model.quantity_in_transit = item.quantity_in_transit
        model.quantity_committed = item.quantity_committed
        model.quantity_damaged = item.quantity_damaged
        model.quantity_quarantine = item.quantity_quarantine
        model.reorder_point = item.reorder_point
        model.reorder_quantity = item.reorder_quantity
        model.preferred_supplier_id = item.preferred_supplier_id
        model.batch_number = item.batch_number or ""
        model.lot_number = item.lot_number or ""
        model.serial_number = item.serial_number or ""
        model.expiry_date = item.expiry_date
        model.manufacturing_date = item.manufacturing_date
        model.last_stocked_at = item.last_stocked_at
        model.last_counted_at = item.last_counted_at
        model.last_movement_at = item.last_movement_at
        model.is_active = item.is_active
        model.save()
        return self._to_entity(model)

    def adjust_quantity(self, item_id: str, tenant_id: str, delta: float) -> InventoryItem | None:
        from django.db.models import F
        updated = InventoryItemModel.objects.filter(id=item_id, tenant_id=tenant_id).update(
            quantity_on_hand=F("quantity_on_hand") + delta,
            quantity_available=F("quantity_available") + delta,
        )
        if updated:
            return self.get_by_id(item_id, tenant_id)
        return None

    def _to_entity(self, model: InventoryItemModel) -> InventoryItem:
        return InventoryItem(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            warehouse_id=str(model.warehouse_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            quantity_on_hand=model.quantity_on_hand,
            quantity_reserved=model.quantity_reserved,
            quantity_available=model.quantity_available,
            quantity_in_transit=model.quantity_in_transit,
            quantity_committed=model.quantity_committed,
            quantity_damaged=model.quantity_damaged,
            quantity_quarantine=model.quantity_quarantine,
            reorder_point=model.reorder_point,
            reorder_quantity=model.reorder_quantity,
            preferred_supplier_id=str(model.preferred_supplier_id) if model.preferred_supplier_id else None,
            batch_number=model.batch_number or None,
            lot_number=model.lot_number or None,
            serial_number=model.serial_number or None,
            expiry_date=model.expiry_date,
            manufacturing_date=model.manufacturing_date,
            last_stocked_at=model.last_stocked_at,
            last_counted_at=model.last_counted_at,
            last_movement_at=model.last_movement_at,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class StockBalanceRepository:
    """Repository for StockBalance."""

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str,
                           date_from: str = "", date_to: str = "") -> list[StockBalance]:
        qs = StockBalanceModel.objects.filter(tenant_id=tenant_id, warehouse_id=warehouse_id)
        if date_from:
            qs = qs.filter(snapshot_date__gte=date_from)
        if date_to:
            qs = qs.filter(snapshot_date__lte=date_to)
        return [self._to_entity(m) for m in qs]

    def get_for_item_date(self, inventory_item_id: str, tenant_id: str, snapshot_date: str) -> StockBalance | None:
        try:
            return self._to_entity(StockBalanceModel.objects.get(
                tenant_id=tenant_id, inventory_item_id=inventory_item_id, snapshot_date=snapshot_date
            ))
        except StockBalanceModel.DoesNotExist:
            return None

    def create(self, balance: StockBalance) -> StockBalance:
        model = StockBalanceModel(
            id=balance.id,
            tenant_id=balance.tenant_id,
            inventory_item_id=balance.inventory_item_id,
            warehouse_id=balance.warehouse_id,
            product_id=balance.product_id,
            variant_id=balance.variant_id,
            snapshot_date=balance.snapshot_date,
            quantity_on_hand=balance.quantity_on_hand,
            quantity_reserved=balance.quantity_reserved,
            quantity_available=balance.quantity_available,
            quantity_in_transit=balance.quantity_in_transit,
            quantity_damaged=balance.quantity_damaged,
            quantity_quarantine=balance.quantity_quarantine,
            unit_cost=balance.unit_cost,
            total_value=balance.total_value,
            costing_method=balance.costing_method,
            is_finalized=balance.is_finalized,
        )
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: StockBalanceModel) -> StockBalance:
        return StockBalance(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            inventory_item_id=str(model.inventory_item_id),
            warehouse_id=str(model.warehouse_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            snapshot_date=model.snapshot_date,
            quantity_on_hand=model.quantity_on_hand,
            quantity_reserved=model.quantity_reserved,
            quantity_available=model.quantity_available,
            quantity_in_transit=model.quantity_in_transit,
            quantity_damaged=model.quantity_damaged,
            quantity_quarantine=model.quantity_quarantine,
            unit_cost=model.unit_cost,
            total_value=model.total_value,
            costing_method=model.costing_method,
            is_finalized=model.is_finalized,
            created_at=model.created_at,
        )


class StockMovementRepository:
    """Repository for StockMovement."""

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str,
                           movement_type: str = "", status: str = "") -> list[StockMovement]:
        qs = StockMovementModel.objects.filter(tenant_id=tenant_id, warehouse_id=warehouse_id)
        if movement_type:
            qs = qs.filter(movement_type=movement_type)
        if status:
            qs = qs.filter(status=status)
        return [self._to_entity(m) for m in qs]

    def get_by_id(self, movement_id: str, tenant_id: str) -> StockMovement | None:
        try:
            return self._to_entity(StockMovementModel.objects.get(id=movement_id, tenant_id=tenant_id))
        except StockMovementModel.DoesNotExist:
            return None

    def create(self, movement: StockMovement) -> StockMovement:
        model = StockMovementModel(
            id=movement.id,
            tenant_id=movement.tenant_id,
            warehouse_id=movement.warehouse_id,
            movement_type=movement.movement_type,
            status=movement.status,
            reference_type=movement.reference_type,
            reference_id=movement.reference_id,
            reference_number=movement.reference_number,
            description=movement.description,
            performed_by=movement.performed_by,
            approved_by=movement.approved_by,
            posted_at=movement.posted_at,
        )
        model.save()
        return self._to_entity(model)

    def update(self, movement: StockMovement) -> StockMovement:
        model = StockMovementModel.objects.get(id=movement.id, tenant_id=movement.tenant_id)
        model.status = movement.status
        model.approved_by = movement.approved_by
        model.posted_at = movement.posted_at
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: StockMovementModel) -> StockMovement:
        return StockMovement(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            warehouse_id=str(model.warehouse_id),
            movement_type=model.movement_type,
            status=model.status,
            reference_type=model.reference_type,
            reference_id=str(model.reference_id) if model.reference_id else "",
            reference_number=model.reference_number,
            description=model.description,
            performed_by=str(model.performed_by),
            approved_by=str(model.approved_by) if model.approved_by else None,
            posted_at=model.posted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class MovementLineRepository:
    """Repository for MovementLine."""

    def list_for_movement(self, tenant_id: str, movement_id: str) -> list[MovementLine]:
        return [self._to_entity(m) for m in MovementLineModel.objects.filter(tenant_id=tenant_id, movement_id=movement_id)]

    def create(self, line: MovementLine) -> MovementLine:
        model = MovementLineModel(
            id=line.id,
            tenant_id=line.tenant_id,
            movement_id=line.movement_id,
            inventory_item_id=line.inventory_item_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity=line.quantity,
            unit_cost=line.unit_cost,
            total_cost=line.total_cost,
            batch_number=line.batch_number or "",
            serial_number=line.serial_number or "",
            expiry_date=line.expiry_date,
            line_number=line.line_number,
            notes=line.notes,
        )
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: MovementLineModel) -> MovementLine:
        return MovementLine(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            movement_id=str(model.movement_id),
            inventory_item_id=str(model.inventory_item_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            quantity=model.quantity,
            unit_cost=model.unit_cost,
            total_cost=model.total_cost,
            batch_number=model.batch_number or None,
            serial_number=model.serial_number or None,
            expiry_date=model.expiry_date,
            line_number=model.line_number,
            notes=model.notes,
            created_at=model.created_at,
        )


class StockAdjustmentRepository:
    """Repository for StockAdjustment."""

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str) -> list[StockAdjustment]:
        return [self._to_entity(m) for m in StockAdjustmentModel.objects.filter(tenant_id=tenant_id, warehouse_id=warehouse_id)]

    def get_by_id(self, adjustment_id: str, tenant_id: str) -> StockAdjustment | None:
        try:
            return self._to_entity(StockAdjustmentModel.objects.get(id=adjustment_id, tenant_id=tenant_id))
        except StockAdjustmentModel.DoesNotExist:
            return None

    def create(self, adjustment: StockAdjustment) -> StockAdjustment:
        model = StockAdjustmentModel(
            id=adjustment.id,
            tenant_id=adjustment.tenant_id,
            warehouse_id=adjustment.warehouse_id,
            adjustment_type=adjustment.adjustment_type,
            status=adjustment.status,
            reason=adjustment.reason,
            reference_number=adjustment.reference_number,
            performed_by=adjustment.performed_by,
            approved_by=adjustment.approved_by,
            posted_at=adjustment.posted_at,
        )
        model.save()
        return self._to_entity(model)

    def update(self, adjustment: StockAdjustment) -> StockAdjustment:
        model = StockAdjustmentModel.objects.get(id=adjustment.id, tenant_id=adjustment.tenant_id)
        model.status = adjustment.status
        model.approved_by = adjustment.approved_by
        model.posted_at = adjustment.posted_at
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: StockAdjustmentModel) -> StockAdjustment:
        return StockAdjustment(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            warehouse_id=str(model.warehouse_id),
            adjustment_type=model.adjustment_type,
            status=model.status,
            reason=model.reason,
            reference_number=model.reference_number,
            performed_by=str(model.performed_by),
            approved_by=str(model.approved_by) if model.approved_by else None,
            posted_at=model.posted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class AdjustmentLineRepository:
    """Repository for AdjustmentLine."""

    def list_for_adjustment(self, tenant_id: str, adjustment_id: str) -> list[AdjustmentLine]:
        return [self._to_entity(m) for m in AdjustmentLineModel.objects.filter(tenant_id=tenant_id, adjustment_id=adjustment_id)]

    def create(self, line: AdjustmentLine) -> AdjustmentLine:
        model = AdjustmentLineModel(
            id=line.id,
            tenant_id=line.tenant_id,
            adjustment_id=line.adjustment_id,
            inventory_item_id=line.inventory_item_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity_before=line.quantity_before,
            quantity_after=line.quantity_after,
            quantity_delta=line.quantity_delta,
            unit_cost=line.unit_cost,
            batch_number=line.batch_number or "",
            serial_number=line.serial_number or "",
            expiry_date=line.expiry_date,
            line_number=line.line_number,
            notes=line.notes,
        )
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: AdjustmentLineModel) -> AdjustmentLine:
        return AdjustmentLine(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            adjustment_id=str(model.adjustment_id),
            inventory_item_id=str(model.inventory_item_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            quantity_before=model.quantity_before,
            quantity_after=model.quantity_after,
            quantity_delta=model.quantity_delta,
            unit_cost=model.unit_cost,
            batch_number=model.batch_number or None,
            serial_number=model.serial_number or None,
            expiry_date=model.expiry_date,
            line_number=model.line_number,
            notes=model.notes,
            created_at=model.created_at,
        )


class StockTransferRepository:
    """Repository for StockTransfer."""

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str) -> list[StockTransfer]:
        return [
            self._to_entity(m) for m in StockTransferModel.objects.filter(
                tenant_id=tenant_id
            ).filter(
                source_warehouse_id=warehouse_id
            ) | StockTransferModel.objects.filter(
                tenant_id=tenant_id, destination_warehouse_id=warehouse_id
            )
        ]

    def get_by_id(self, transfer_id: str, tenant_id: str) -> StockTransfer | None:
        try:
            return self._to_entity(StockTransferModel.objects.get(id=transfer_id, tenant_id=tenant_id))
        except StockTransferModel.DoesNotExist:
            return None

    def create(self, transfer: StockTransfer) -> StockTransfer:
        model = StockTransferModel(
            id=transfer.id,
            tenant_id=transfer.tenant_id,
            source_warehouse_id=transfer.source_warehouse_id,
            destination_warehouse_id=transfer.destination_warehouse_id,
            status=transfer.status,
            reference_number=transfer.reference_number,
            description=transfer.description,
            performed_by=transfer.performed_by,
            approved_by=transfer.approved_by,
            shipped_at=transfer.shipped_at,
            received_at=transfer.received_at,
        )
        model.save()
        return self._to_entity(model)

    def update(self, transfer: StockTransfer) -> StockTransfer:
        model = StockTransferModel.objects.get(id=transfer.id, tenant_id=transfer.tenant_id)
        model.status = transfer.status
        model.approved_by = transfer.approved_by
        model.shipped_at = transfer.shipped_at
        model.received_at = transfer.received_at
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: StockTransferModel) -> StockTransfer:
        return StockTransfer(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            source_warehouse_id=str(model.source_warehouse_id),
            destination_warehouse_id=str(model.destination_warehouse_id),
            status=model.status,
            reference_number=model.reference_number,
            description=model.description,
            performed_by=str(model.performed_by),
            approved_by=str(model.approved_by) if model.approved_by else None,
            shipped_at=model.shipped_at,
            received_at=model.received_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class TransferLineRepository:
    """Repository for TransferLine."""

    def list_for_transfer(self, tenant_id: str, transfer_id: str) -> list[TransferLine]:
        return [self._to_entity(m) for m in TransferLineModel.objects.filter(tenant_id=tenant_id, transfer_id=transfer_id)]

    def create(self, line: TransferLine) -> TransferLine:
        model = TransferLineModel(
            id=line.id,
            tenant_id=line.tenant_id,
            transfer_id=line.transfer_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity=line.quantity,
            quantity_received=line.quantity_received,
            unit_cost=line.unit_cost,
            batch_number=line.batch_number or "",
            serial_number=line.serial_number or "",
            expiry_date=line.expiry_date,
            line_number=line.line_number,
            notes=line.notes,
        )
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: TransferLineModel) -> TransferLine:
        return TransferLine(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            transfer_id=str(model.transfer_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            quantity=model.quantity,
            quantity_received=model.quantity_received,
            unit_cost=model.unit_cost,
            batch_number=model.batch_number or None,
            serial_number=model.serial_number or None,
            expiry_date=model.expiry_date,
            line_number=model.line_number,
            notes=model.notes,
            created_at=model.created_at,
        )


class StockReservationRepository:
    """Repository for StockReservation."""

    def list_for_inventory_item(self, tenant_id: str, inventory_item_id: str) -> list[StockReservation]:
        return [self._to_entity(m) for m in StockReservationModel.objects.filter(
            tenant_id=tenant_id, inventory_item_id=inventory_item_id
        )]

    def list_for_reference(self, tenant_id: str, reference_type: str, reference_id: str) -> list[StockReservation]:
        return [self._to_entity(m) for m in StockReservationModel.objects.filter(
            tenant_id=tenant_id, reference_type=reference_type, reference_id=reference_id
        )]

    def get_by_id(self, reservation_id: str, tenant_id: str) -> StockReservation | None:
        try:
            return self._to_entity(StockReservationModel.objects.get(id=reservation_id, tenant_id=tenant_id))
        except StockReservationModel.DoesNotExist:
            return None

    def create(self, reservation: StockReservation) -> StockReservation:
        model = StockReservationModel(
            id=reservation.id,
            tenant_id=reservation.tenant_id,
            inventory_item_id=reservation.inventory_item_id,
            product_id=reservation.product_id,
            variant_id=reservation.variant_id,
            warehouse_id=reservation.warehouse_id,
            quantity=reservation.quantity,
            quantity_allocated=reservation.quantity_allocated,
            status=reservation.status,
            reference_type=reservation.reference_type,
            reference_id=reservation.reference_id,
            reference_line_id=reservation.reference_line_id,
            reserved_by=reservation.reserved_by,
            released_by=reservation.released_by,
            expires_at=reservation.expires_at,
        )
        model.save()
        return self._to_entity(model)

    def update(self, reservation: StockReservation) -> StockReservation:
        model = StockReservationModel.objects.get(id=reservation.id, tenant_id=reservation.tenant_id)
        model.quantity_allocated = reservation.quantity_allocated
        model.status = reservation.status
        model.released_by = reservation.released_by
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: StockReservationModel) -> StockReservation:
        return StockReservation(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            inventory_item_id=str(model.inventory_item_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            warehouse_id=str(model.warehouse_id),
            quantity=model.quantity,
            quantity_allocated=model.quantity_allocated,
            status=model.status,
            reference_type=model.reference_type,
            reference_id=str(model.reference_id) if model.reference_id else "",
            reference_line_id=str(model.reference_line_id) if model.reference_line_id else "",
            reserved_by=str(model.reserved_by),
            released_by=str(model.released_by) if model.released_by else None,
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class CycleCountRepository:
    """Repository for CycleCount."""

    def list_for_warehouse(self, tenant_id: str, warehouse_id: str, status: str = "") -> list[CycleCount]:
        qs = CycleCountModel.objects.filter(tenant_id=tenant_id, warehouse_id=warehouse_id)
        if status:
            qs = qs.filter(status=status)
        return [self._to_entity(m) for m in qs]

    def get_by_id(self, count_id: str, tenant_id: str) -> CycleCount | None:
        try:
            return self._to_entity(CycleCountModel.objects.get(id=count_id, tenant_id=tenant_id))
        except CycleCountModel.DoesNotExist:
            return None

    def create(self, count: CycleCount) -> CycleCount:
        model = CycleCountModel(
            id=count.id,
            tenant_id=count.tenant_id,
            warehouse_id=count.warehouse_id,
            zone_id=count.zone_id,
            count_type=count.count_type,
            status=count.status,
            reference_number=count.reference_number,
            scheduled_date=count.scheduled_date,
            counted_by=count.counted_by,
            verified_by=count.verified_by,
            variance_threshold_percent=count.variance_threshold_percent,
            notes=count.notes,
            completed_at=count.completed_at,
        )
        model.save()
        return self._to_entity(model)

    def update(self, count: CycleCount) -> CycleCount:
        model = CycleCountModel.objects.get(id=count.id, tenant_id=count.tenant_id)
        model.status = count.status
        model.verified_by = count.verified_by
        model.completed_at = count.completed_at
        model.notes = count.notes
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: CycleCountModel) -> CycleCount:
        return CycleCount(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            warehouse_id=str(model.warehouse_id),
            zone_id=str(model.zone_id) if model.zone_id else None,
            count_type=model.count_type,
            status=model.status,
            reference_number=model.reference_number,
            scheduled_date=model.scheduled_date,
            counted_by=str(model.counted_by),
            verified_by=str(model.verified_by) if model.verified_by else None,
            variance_threshold_percent=model.variance_threshold_percent,
            notes=model.notes,
            completed_at=model.completed_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class CycleCountLineRepository:
    """Repository for CycleCountLine."""

    def list_for_cycle_count(self, tenant_id: str, cycle_count_id: str) -> list[CycleCountLine]:
        return [self._to_entity(m) for m in CycleCountLineModel.objects.filter(tenant_id=tenant_id, cycle_count_id=cycle_count_id)]

    def create(self, line: CycleCountLine) -> CycleCountLine:
        model = CycleCountLineModel(
            id=line.id,
            tenant_id=line.tenant_id,
            cycle_count_id=line.cycle_count_id,
            inventory_item_id=line.inventory_item_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            bin_location=line.bin_location,
            system_quantity=line.system_quantity,
            counted_quantity=line.counted_quantity,
            variance_quantity=line.variance_quantity,
            unit_cost=line.unit_cost,
            variance_value=line.variance_value,
            is_adjusted=line.is_adjusted,
            batch_number=line.batch_number or "",
            serial_number=line.serial_number or "",
            expiry_date=line.expiry_date,
            line_number=line.line_number,
            notes=line.notes,
        )
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: CycleCountLineModel) -> CycleCountLine:
        return CycleCountLine(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            cycle_count_id=str(model.cycle_count_id),
            inventory_item_id=str(model.inventory_item_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            bin_location=model.bin_location,
            system_quantity=model.system_quantity,
            counted_quantity=model.counted_quantity,
            variance_quantity=model.variance_quantity,
            unit_cost=model.unit_cost,
            variance_value=model.variance_value,
            is_adjusted=model.is_adjusted,
            batch_number=model.batch_number or None,
            serial_number=model.serial_number or None,
            expiry_date=model.expiry_date,
            line_number=model.line_number,
            notes=model.notes,
            created_at=model.created_at,
        )