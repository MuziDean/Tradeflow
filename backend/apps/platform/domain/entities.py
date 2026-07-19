"""
Domain entities for the Platform module.

Covers company profile, branches, warehouses, settings, and metadata.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from shared.ids.uuid import new_id_str
from shared.time.helpers import now
from shared.types.enums import (
    FiscalYearStatus,
    NumberSequenceResetPolicy,
    WarehouseType,
)


@dataclass
class Address:
    """Value object for structured address."""
    street: str = ""
    suburb: str = ""
    city: str = ""
    province: str = ""
    postal_code: str = ""
    country: str = ""
    latitude: Optional[str] = None
    longitude: Optional[str] = None


@dataclass
class Company:
    """
    Legal business entity.
    Soft delete only. Contains legal/business registration information.
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    legal_name: str = ""
    trading_name: str = ""
    registration_number: str = ""
    tax_number: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    logo_path: str = ""
    is_active: bool = True
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class BusinessPreferences:
    """
    Operational configuration for the tenant.
    One-to-one with tenant.
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    default_currency_code: str = "ZAR"
    timezone: str = "Africa/Johannesburg"
    locale: str = "en-ZA"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "24h"
    first_day_of_week: int = 1  # Monday
    allow_negative_stock: bool = False
    receipt_footer: str = ""
    fiscal_year_start_month: int = 1  # January
    decimal_precision: int = 2
    quantity_decimal_places: int = 2
    price_decimal_places: int = 2
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class Branch:
    """
    Physical business location.
    Structured address fields. Soft delete via is_active.
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    company_id: str = ""
    name: str = ""
    code: str = ""
    street: str = ""
    suburb: str = ""
    city: str = ""
    province: str = ""
    postal_code: str = ""
    country: str = ""
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    is_head_office: bool = False
    contact_email: str = ""
    contact_phone: str = ""
    manager_user_id: Optional[str] = None
    is_active: bool = True
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class Warehouse:
    """
    Storage location within a branch.
    Supports future zones/aisles/bins via optional fields.
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    branch_id: str = ""
    warehouse_type: WarehouseType = WarehouseType.MAIN
    code: str = ""
    name: str = ""
    street: str = ""
    city: str = ""
    province: str = ""
    country: str = ""
    manager_user_id: Optional[str] = None
    is_active: bool = True
    # Future bin/zone compatibility
    supports_bins: bool = False
    supports_serial_tracking: bool = False
    supports_batch_tracking: bool = False
    deleted_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class Currency:
    """
    Global currency definition (not tenant-scoped).
    Seeded from ISO 4217.
    """
    id: str = field(default_factory=new_id_str)
    code: str = ""  # e.g., ZAR
    name: str = ""  # e.g., South African Rand
    symbol: str = ""  # e.g., R
    decimal_places: int = 2
    is_active: bool = True
    created_at: datetime = field(default_factory=now)


@dataclass
class TaxConfiguration:
    """
    Tax rate configuration.
    Historical records never overwritten. Future rate changes create new records.
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    code: str = ""
    tax_type: str = ""  # VAT, SALES_TAX, INCOME_TAX
    tax_category: str = ""  # standard, reduced, zero, exempt
    rate: float = 0.0
    is_recoverable: bool = False
    is_default: bool = False
    effective_from: datetime = field(default_factory=now)
    effective_to: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class FiscalYear:
    """
    Accounting fiscal period.
    Status: OPEN, CLOSED, ARCHIVED.
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    start_date: datetime = field(default_factory=now)
    end_date: datetime = field(default_factory=now)
    status: str = FiscalYearStatus.OPEN
    is_active: bool = True
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class NumberSequence:
    """
    Auto-incrementing document number sequence.
    Generation must be atomic.
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    prefix: str = ""
    suffix: str = ""
    current_number: int = 1
    padding_length: int = 6
    reset_policy: str = NumberSequenceResetPolicy.NEVER
    last_generated_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class StoredFile:
    """
    File metadata tracker.
    Binary data stored in external object storage (S3/minio).
    """
    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    module: str = ""  # e.g., "platform", "retail", "iam"
    entity_type: str = ""  # e.g., "company", "product", "user"
    entity_id: str = ""
    storage_provider: str = ""  # e.g., "s3", "minio", "local"
    storage_path: str = ""  # e.g., "tenant_id/module/entity_id/filename"
    original_filename: str = ""
    mime_type: str = ""
    checksum: str = ""  # SHA256 for integrity
    file_size: int = 0  # bytes
    uploaded_by: str = ""
    uploaded_at: datetime = field(default_factory=now)
    created_at: datetime = field(default_factory=now)