"""
Application service for Company (legal entity).

Domain events emitted:
- CompanyCreated
- CompanyUpdated
- CompanyArchived
"""

import logging

from django.db import transaction

from apps.platform.domain.entities import Company
from apps.platform.infrastructure.repositories import CompanyRepository
from shared.events.company_events import CompanyArchived, CompanyCreated, CompanyUpdated

logger = logging.getLogger("tradeflow.platform")


class CompanyService:
    """Service for Company (legal entity)."""

    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    def get_company(self, tenant_id: str) -> Company | None:
        return self.company_repository.get_current(tenant_id)

    def create_company(self, company: Company) -> Company:
        """Create new company. Soft create only."""
        with transaction.atomic():
            created = self.company_repository.create(company)
            CompanyCreated(
                tenant_id=company.tenant_id,
                company_id=created.id,
                legal_name=created.legal_name,
            ).emit()
            logger.info(f"Company created: {created.id}")
            return created

    def update_company(self, company: Company) -> Company:
        with transaction.atomic():
            updated = self.company_repository.update(company)
            CompanyUpdated(tenant_id=company.tenant_id, company_id=updated.id).emit()
            return updated

    def archive_company(self, company_id: str, tenant_id: str) -> bool:
        """Soft delete only. Cascade via business rules, never hard-delete."""
        with transaction.atomic():
            success = self.company_repository.soft_delete(company_id, tenant_id)
            if success:
                CompanyArchived(tenant_id=tenant_id, company_id=company_id).emit()
                logger.info(f"Company archived: {company_id}")
            return success