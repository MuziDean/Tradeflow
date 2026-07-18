"""
Platform domain events for TradeFlow.

These events represent immutable business facts emitted by Platform services.
"""

from shared.events.base import DomainEvent


class CompanyCreated(DomainEvent):
    def __init__(self, tenant_id: str, company_id: str, legal_name: str):
        super().__init__(
            "company.created",
            {"tenant_id": tenant_id, "company_id": company_id, "legal_name": legal_name},
        )


class CompanyUpdated(DomainEvent):
    def __init__(self, tenant_id: str, company_id: str):
        super().__init__("company.updated", {"tenant_id": tenant_id, "company_id": company_id})


class CompanyArchived(DomainEvent):
    def __init__(self, tenant_id: str, company_id: str):
        super().__init__("company.archived", {"tenant_id": tenant_id, "company_id": company_id})


class BranchCreated(DomainEvent):
    def __init__(self, tenant_id: str, branch_id: str, name: str):
        super().__init__(
            "branch.created",
            {"tenant_id": tenant_id, "branch_id": branch_id, "name": name},
        )


class WarehouseCreated(DomainEvent):
    def __init__(self, tenant_id: str, warehouse_id: str, name: str):
        super().__init__(
            "warehouse.created",
            {"tenant_id": tenant_id, "warehouse_id": warehouse_id, "name": name},
        )


class FiscalYearClosed(DomainEvent):
    def __init__(self, tenant_id: str, fiscal_year_id: str):
        super().__init__(
            "fiscal_year.closed",
            {"tenant_id": tenant_id, "fiscal_year_id": fiscal_year_id},
        )


class NumberSequenceReset(DomainEvent):
    def __init__(self, tenant_id: str, sequence_name: str):
        super().__init__(
            "number_sequence.reset",
            {"tenant_id": tenant_id, "sequence_name": sequence_name},
        )