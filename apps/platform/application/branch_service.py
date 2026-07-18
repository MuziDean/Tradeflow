"""
Application service for Branch management.

Domain events emitted:
- BranchCreated
"""

import logging

from django.db import transaction

from apps.platform.domain.entities import Branch
from apps.platform.infrastructure.repositories import BranchRepository, CompanyRepository
from shared.events.branch_events import BranchCreated

logger = logging.getLogger("tradeflow.platform")


class BranchService:
    """Service for Branch management."""

    def __init__(self, branch_repository: BranchRepository, company_repository: CompanyRepository):
        self.branch_repository = branch_repository
        self.company_repository = company_repository

    def list_branches(self, tenant_id: str, company_id: str) -> list[Branch]:
        return self.branch_repository.list_for_company(tenant_id, company_id)

    def get_branch(self, branch_id: str, tenant_id: str) -> Branch | None:
        return self.branch_repository.get_by_id(branch_id, tenant_id)

    def create_branch(self, branch: Branch) -> Branch:
        """Create branch. Set head office flag if first branch."""
        with transaction.atomic():
            # Enforce only one head office
            existing = self.branch_repository.list_for_company(branch.tenant_id, branch.company_id)
            if not existing:
                branch.is_head_office = True
            elif branch.is_head_office:
                # Unset other head offices
                for b in existing:
                    if b.is_head_office:
                        b.is_head_office = False
                        self.branch_repository.update(b)

            created = self.branch_repository.create(branch)
            BranchCreated(
                tenant_id=branch.tenant_id, branch_id=created.id, name=created.name
            ).emit()
            return created

    def update_branch(self, branch: Branch) -> Branch:
        with transaction.atomic():
            if branch.is_head_office:
                existing = self.branch_repository.list_for_company(
                    branch.tenant_id, branch.company_id
                )
                for b in existing:
                    if b.is_head_office and b.id != branch.id:
                        b.is_head_office = False
                        self.branch_repository.update(b)

            return self.branch_repository.update(branch)

    def delete_branch(self, branch_id: str, tenant_id: str) -> bool:
        """Soft delete only."""
        return self.branch_repository.soft_delete(branch_id, tenant_id)