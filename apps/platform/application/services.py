"""
Application services for the Platform module.

Each service handles one business capability:
- CompanyService — Company (legal entity)
- BusinessPreferencesService — Operational settings
- BranchService — Branch management
- WarehouseService — Warehouse management
- CurrencyService — Read-only currency (seed/update admin)
- TaxConfigurationService — Immutable tax history
- FiscalYearService — Fiscal period management
- NumberSequenceService — Atomic document numbers
- StoredFileService — File metadata management

Domain events emitted for state changes.
"""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

from django.db import transaction

from apps.platform.domain.entities import (
    Branch,
    BusinessPreferences,
    Company,
    Currency,
    FiscalYear,
    NumberSequence,
    StoredFile,
    TaxConfiguration,
    Warehouse,
)
from apps.platform.infrastructure.repositories import (
    BranchRepository,
    BusinessPreferencesRepository,
    CompanyRepository,
    CurrencyRepository,
    FiscalYearRepository,
    NumberSequenceRepository,
    StoredFileRepository,
    TaxConfigurationRepository,
    WarehouseRepository,
)
from shared.events.base import DomainEvent

logger = logging.getLogger("tradeflow.platform")


# Domain Events
class CompanyCreated(DomainEvent):
    def __init__(self, tenant_id: str, company_id: str, legal_name: str):
        super().__init__("company.created", {"tenant_id": tenant_id, "company_id": company_id, "legal_name": legal_name})


class CompanyUpdated(DomainEvent):
    def __init__(self, tenant_id: str, company_id: str):
        super().__init__("company.updated", {"tenant_id": tenant_id, "company_id": company_id})


class CompanyArchived(DomainEvent):
    def __init__(self, tenant_id: str, company_id: str):
        super().__init__("company.archived", {"tenant_id": tenant_id, "company_id": company_id})


class BranchCreated(DomainEvent):
    def __init__(self, tenant_id: str, branch_id: str, name: str):
        super().__init__("branch.created", {"tenant_id": tenant_id, "branch_id": branch_id, "name": name})


class WarehouseCreated(DomainEvent):
    def __init__(self, tenant_id: str, warehouse_id: str, name: str):
        super().__init__("warehouse.created", {"tenant_id": tenant_id, "warehouse_id": warehouse_id, "name": name})


class FiscalYearClosed(DomainEvent):
    def __init__(self, tenant_id: str, fiscal_year_id: str):
        super().__init__("fiscal_year.closed", {"tenant_id": tenant_id, "fiscal_year_id": fiscal_year_id})


class NumberSequenceReset(DomainEvent):
    def __init__(self, tenant_id: str, sequence_name: str):
        super().__init__("number_sequence.reset", {"tenant_id": tenant_id, "sequence_name": sequence_name})


class CompanyService:
    """Service for Company (legal entity)."""

    def __init__(self, company_repository: CompanyRepository):
        self.company_repository = company_repository

    def get_company(self, tenant_id: str) -> Optional[Company]:
        return self.company_repository.get_current(tenant_id)

    def create_company(self, company: Company) -> Company:
        """Create new company. Soft create only."""
        with transaction.atomic():
            created = self.company_repository.create(company)
            CompanyCreated(tenant_id=company.tenant_id, company_id=created.id, legal_name=created.legal_name).emit()
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


class BusinessPreferencesService:
    """Service for BusinessPreferences."""

    def __init__(self, prefs_repository: BusinessPreferencesRepository):
        self.prefs_repository = prefs_repository

    def get_preferences(self, tenant_id: str) -> Optional[BusinessPreferences]:
        return self.prefs_repository.get_for_tenant(tenant_id)

    def update_preferences(self, prefs: BusinessPreferences) -> BusinessPreferences:
        with transaction.atomic():
            return self.prefs_repository.create_or_update(prefs)


class BranchService:
    """Service for Branch management."""

    def __init__(self, branch_repository: BranchRepository, company_repository: CompanyRepository):
        self.branch_repository = branch_repository
        self.company_repository = company_repository

    def list_branches(self, tenant_id: str, company_id: str) -> list[Branch]:
        return self.branch_repository.list_for_company(tenant_id, company_id)

    def get_branch(self, branch_id: str, tenant_id: str) -> Optional[Branch]:
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
            BranchCreated(tenant_id=branch.tenant_id, branch_id=created.id, name=created.name).emit()
            return created

    def update_branch(self, branch: Branch) -> Branch:
        with transaction.atomic():
            if branch.is_head_office:
                existing = self.branch_repository.list_for_company(branch.tenant_id, branch.company_id)
                for b in existing:
                    if b.is_head_office and b.id != branch.id:
                        b.is_head_office = False
                        self.branch_repository.update(b)

            return self.branch_repository.update(branch)

    def delete_branch(self, branch_id: str, tenant_id: str) -> bool:
        """Soft delete only."""
        return self.branch_repository.soft_delete(branch_id, tenant_id)


class WarehouseService:
    """Service for Warehouse management."""

    def __init__(self, warehouse_repository: WarehouseRepository):
        self.warehouse_repository = warehouse_repository

    def list_warehouses(self, tenant_id: str, branch_id: str) -> list[Warehouse]:
        return self.warehouse_repository.list_for_branch(tenant_id, branch_id)

    def get_warehouse(self, warehouse_id: str, tenant_id: str) -> Optional[Warehouse]:
        return self.warehouse_repository.get_by_id(warehouse_id, tenant_id)

    def create_warehouse(self, warehouse: Warehouse) -> Warehouse:
        with transaction.atomic():
            created = self.warehouse_repository.create(warehouse)
            WarehouseCreated(
                tenant_id=warehouse.tenant_id, warehouse_id=created.id, name=created.name
            ).emit()
            return created

    def update_warehouse(self, warehouse: Warehouse) -> Warehouse:
        with transaction.atomic():
            return self.warehouse_repository.update(warehouse)

    def delete_warehouse(self, warehouse_id: str, tenant_id: str) -> bool:
        return self.warehouse_repository.soft_delete(warehouse_id, tenant_id)


class CurrencyService:
    """Service for global Currency (read-only except admin seed)."""

    def __init__(self, currency_repository: CurrencyRepository):
        self.currency_repository = currency_repository

    def list_currencies(self) -> list[Currency]:
        return self.currency_repository.list_all()

    def get_currency(self, code: str) -> Optional[Currency]:
        return self.currency_repository.get_by_code(code)

    def seed_currencies(self, currencies: list[Currency]) -> None:
        """Admin operation: seed ISO 4217 currencies."""
        self.currency_repository.bulk_create(currencies)


class TaxConfigurationService:
    """Service for TaxConfiguration with immutable history."""

    def __init__(self, tax_repository: TaxConfigurationRepository):
        self.tax_repository = tax_repository

    def list_tax_configs(self, tenant_id: str, active_only: bool = True) -> list[TaxConfiguration]:
        return self.tax_repository.list_for_tenant(tenant_id, active_only)

    def get_tax_config(self, tax_id: str, tenant_id: str) -> Optional[TaxConfiguration]:
        return self.tax_repository.get_by_id(tax_id, tenant_id)

    def create_tax_config(self, tax: TaxConfiguration) -> TaxConfiguration:
        """Create new tax config. Never overwrites history."""
        with transaction.atomic():
            return self.tax_repository.create(tax)

    def update_tax_config(self, tax: TaxConfiguration) -> TaxConfiguration:
        """Update creates new version (new record) to preserve history."""
        with transaction.atomic():
            # Deactivate old record
            old = self.tax_repository.get_by_id(tax.id, tax.tenant_id)
            if old and old.is_active:
                # Create new version with new effective_from
                new_version = TaxConfiguration(
                    tenant_id=tax.tenant_id,
                    name=tax.name,
                    code=tax.code,
                    tax_type=tax.tax_type,
                    tax_category=tax.tax_category,
                    rate=tax.rate,
                    is_recoverable=tax.is_recoverable,
                    is_default=tax.is_default,
                    effective_from=datetime.now(),
                    effective_to=None,
                )
                return self.tax_repository.create(new_version)
            return self.tax_repository.create(tax)


class FiscalYearService:
    """Service for FiscalYear management."""

    def __init__(self, fiscal_year_repository: FiscalYearRepository):
        self.fiscal_year_repository = fiscal_year_repository

    def list_fiscal_years(self, tenant_id: str) -> list[FiscalYear]:
        return self.fiscal_year_repository.list_for_tenant(tenant_id)

    def get_fiscal_year(self, fiscal_year_id: str, tenant_id: str) -> Optional[FiscalYear]:
        return self.fiscal_year_repository.get_by_id(fiscal_year_id, tenant_id)

    def create_fiscal_year(self, fiscal_year: FiscalYear) -> FiscalYear:
        with transaction.atomic():
            return self.fiscal_year_repository.create(fiscal_year)

    def close_fiscal_year(self, fiscal_year_id: str, tenant_id: str) -> Optional[FiscalYear]:
        with transaction.atomic():
            closed = self.fiscal_year_repository.close(fiscal_year_id, tenant_id)
            if closed:
                FiscalYearClosed(tenant_id=tenant_id, fiscal_year_id=fiscal_year_id).emit()
            return closed


class NumberSequenceService:
    """Service for atomic document number generation."""

    def __init__(self, number_sequence_repository: NumberSequenceRepository):
        self.number_sequence_repository = number_sequence_repository

    def get_next_number(self, tenant_id: str, name: str) -> str:
        """
        Return next formatted document number.
        Atomic via repository select_for_update.
        """
        with transaction.atomic():
            number = self.number_sequence_repository.get_next_number(tenant_id, name)
            seq = self.number_sequence_repository.get_by_name(tenant_id, name)
            formatted = f"{seq.prefix}{number:0{seq.padding_length}d}{seq.suffix}"
            return formatted

    def reset_sequence(self, tenant_id: str, name: str) -> bool:
        """Reset current_number to 1. Emits event."""
        with transaction.atomic():
            seq = self.number_sequence_repository.get_by_name(tenant_id, name)
            if not seq:
                return False
            seq.current_number = 1
            self.number_sequence_repository.create_or_update(seq)
            NumberSequenceReset(tenant_id=tenant_id, sequence_name=name).emit()
            return True


class StoredFileService:
    """Service for StoredFile metadata management."""

    def __init__(self, stored_file_repository: StoredFileRepository):
        self.stored_file_repository = stored_file_repository

    def create_file(self, stored_file: StoredFile) -> StoredFile:
        return self.stored_file_repository.create(stored_file)

    def get_files_for_entity(self, tenant_id: str, entity_type: str, entity_id: str) -> list[StoredFile]:
        return self.stored_file_repository.get_by_entity(tenant_id, entity_type, entity_id)