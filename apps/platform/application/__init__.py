"""
Application services for the Platform module.

Each service handles one business capability in its own file.
"""

from apps.platform.application.company_service import CompanyService
from apps.platform.application.business_preferences_service import BusinessPreferencesService
from apps.platform.application.branch_service import BranchService
from apps.platform.application.warehouse_service import WarehouseService
from apps.platform.application.currency_service import CurrencyService
from apps.platform.application.tax_configuration_service import TaxConfigurationService
from apps.platform.application.fiscal_year_service import FiscalYearService
from apps.platform.application.number_sequence_service import NumberSequenceService
from apps.platform.application.stored_file_service import StoredFileService

__all__ = [
    "CompanyService",
    "BusinessPreferencesService",
    "BranchService",
    "WarehouseService",
    "CurrencyService",
    "TaxConfigurationService",
    "FiscalYearService",
    "NumberSequenceService",
    "StoredFileService",
]