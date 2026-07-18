"""
Application service for TaxConfiguration with immutable history.

No domain events emitted (versioned records preserve history implicitly).
"""

from datetime import datetime
from typing import Optional

from django.db import transaction

from apps.platform.domain.entities import TaxConfiguration
from apps.platform.infrastructure.repositories import TaxConfigurationRepository


class TaxConfigurationService:
    """Service for TaxConfiguration with immutable history."""

    def __init__(self, tax_repository: TaxConfigurationRepository):
        self.tax_repository = tax_repository

    def list_tax_configs(
        self, tenant_id: str, active_only: bool = True
    ) -> list[TaxConfiguration]:
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