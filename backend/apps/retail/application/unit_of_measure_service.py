"""
Application service for UnitOfMeasure.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import UnitOfMeasure
from apps.retail.infrastructure.repositories import UnitOfMeasureRepository
from shared.events.retail_events import (
    UnitOfMeasureCreated,
    UnitOfMeasureDeleted,
    UnitOfMeasureUpdated,
)

logger = logging.getLogger("tradeflow.retail")


class UnitOfMeasureService:
    """Service for UnitOfMeasure."""

    def __init__(self, unit_of_measure_repository: UnitOfMeasureRepository):
        self.unit_of_measure_repository = unit_of_measure_repository

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[UnitOfMeasure]:
        return self.unit_of_measure_repository.list_for_tenant(tenant_id, active_only)

    def get_by_id(self, unit_id: str, tenant_id: str) -> UnitOfMeasure | None:
        return self.unit_of_measure_repository.get_by_id(unit_id, tenant_id)

    def get_by_symbol(self, symbol: str, tenant_id: str) -> UnitOfMeasure | None:
        return self.unit_of_measure_repository.get_by_symbol(symbol, tenant_id)

    def create(self, unit: UnitOfMeasure) -> UnitOfMeasure:
        with transaction.atomic():
            created = self.unit_of_measure_repository.create(unit)
            UnitOfMeasureCreated(
                tenant_id=unit.tenant_id,
                unit_id=created.id,
                name=created.name,
                symbol=created.symbol,
            ).emit()
            logger.info(f"UnitOfMeasure created: {created.id} tenant={unit.tenant_id}")
            return created

    def update(self, unit: UnitOfMeasure) -> UnitOfMeasure:
        with transaction.atomic():
            updated = self.unit_of_measure_repository.update(unit)
            UnitOfMeasureUpdated(
                tenant_id=unit.tenant_id,
                unit_id=updated.id,
                name=updated.name,
            ).emit()
            logger.info(f"UnitOfMeasure updated: {updated.id} tenant={unit.tenant_id}")
            return updated

    def soft_delete(self, unit_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            success = self.unit_of_measure_repository.soft_delete(unit_id, tenant_id)
            if success:
                UnitOfMeasureDeleted(tenant_id=tenant_id, unit_id=unit_id).emit()
                logger.info(f"UnitOfMeasure deleted: {unit_id} tenant={tenant_id}")
            return success
