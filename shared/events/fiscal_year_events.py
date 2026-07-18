"""
Fiscal year domain events.

Emitted by FiscalYearService on state changes.
"""

from shared.events.base import DomainEvent


class FiscalYearClosed(DomainEvent):
    def __init__(self, tenant_id: str, fiscal_year_id: str):
        super().__init__(
            "fiscal_year.closed",
            {"tenant_id": tenant_id, "fiscal_year_id": fiscal_year_id},
        )