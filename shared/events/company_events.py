"""
Company domain events.

Emitted by CompanyService on state changes.
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