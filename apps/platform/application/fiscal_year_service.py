"""
Application service for FiscalYear management.

Domain events emitted:
- FiscalYearClosed
"""

import logging

from typing import Optional

from django.db import transaction

from apps.platform.domain.entities import FiscalYear
from apps.platform.infrastructure.repositories import FiscalYearRepository
from shared.events.fiscal_year_events import FiscalYearClosed

logger = logging.getLogger("tradeflow.platform")


class FiscalYearService:
    """Service for FiscalYear management."""

    def __init__(self, fiscal_year_repository: FiscalYearRepository):
        self.fiscal_year_repository = fiscal_year_repository

    def list_fiscal_years(self, tenant_id: str) -> list[FiscalYear]:
        return self.fiscal_year_repository.list_for_tenant(tenant_id)

    def get_fiscal_year(
        self, fiscal_year_id: str, tenant_id: str
    ) -> Optional[FiscalYear]:
        return self.fiscal_year_repository.get_by_id(fiscal_year_id, tenant_id)

    def create_fiscal_year(self, fiscal_year: FiscalYear) -> FiscalYear:
        with transaction.atomic():
            return self.fiscal_year_repository.create(fiscal_year)

    def close_fiscal_year(
        self, fiscal_year_id: str, tenant_id: str
    ) -> Optional[FiscalYear]:
        with transaction.atomic():
            closed = self.fiscal_year_repository.close(fiscal_year_id, tenant_id)
            if closed:
                FiscalYearClosed(
                    tenant_id=tenant_id, fiscal_year_id=fiscal_year_id
                ).emit()
            return closed