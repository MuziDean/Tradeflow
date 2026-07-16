"""
Django ORM models for the Platform module.

Implements company, branches, warehouses, settings, and metadata.
All tenant-scoped unless noted. Soft delete via is_active/deleted_at.
"""

from uuid import uuid4

from django.db import models

from shared.types.enums import (
    FiscalYearStatus,
    NumberSequenceResetPolicy,
    TaxCategory,
    TaxType,
    WarehouseType,
)


class TenantModel(models.Model):
    """
    Abstract base for tenant-scoped models.
    Ensures all queries are filtered by tenant_id.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Abstract base for soft-deletable models.
    """

    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True


class Company(TenantModel, SoftDeleteModel):
    """
    Legal business entity.
    Soft delete only. One per tenant.
    """

    legal_name = models.CharField(max_length=255)
    trading_name = models.CharField(max_length=255, blank=True)
    registration_number = models.CharField(max_length=100, unique=True)
    tax_number = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=50)
    website = models.URLField(blank=True)
    logo_path = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = "platform_companies"
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        unique_together = ("tenant_id", "registration_number")
        indexes = [
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "deleted_at"]),
            models.Index(fields=["registration_number"]),
            models.Index(fields=["tax_number"]),
        ]

    def __str__(self) -> str:
        return f"{self.legal_name} ({self.tenant_id})"


class BusinessPreferences(TenantModel):
    """
    Operational configuration for the tenant.
    One-to-one with tenant.
    """

    default_currency_code = models.CharField(max_length=3, default="ZAR")
    timezone = models.CharField(max_length=50, default="Africa/Johannesburg")
    locale = models.CharField(max_length=10, default="en-ZA")
    date_format = models.CharField(max_length=50, default="YYYY-MM-DD")
    time_format = models.CharField(max_length=10, default="24h")
    first_day_of_week = models.IntegerField(default=1)  # Monday
    allow_negative_stock = models.BooleanField(default=False)
    receipt_footer = models.TextField(blank=True)
    fiscal_year_start_month = models.IntegerField(default=1)  # January
    decimal_precision = models.IntegerField(default=2)
    quantity_decimal_places = models.IntegerField(default=2)
    price_decimal_places = models.IntegerField(default=2)

    class Meta:
        db_table = "platform_business_preferences"
        verbose_name = "Business Preferences"
        verbose_name_plural = "Business Preferences"
        unique_together = ("tenant_id",)
        indexes = [
            models.Index(fields=["tenant_id"]),
        ]

    def __str__(self) -> str:
        return f"Preferences for tenant {self.tenant_id}"


class Branch(TenantModel, SoftDeleteModel):
    """
    Physical business location.
    Structured address fields.
    """

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="branches")
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    street = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    latitude = models.CharField(max_length=20, blank=True)
    longitude = models.CharField(max_length=20, blank=True)
    is_head_office = models.BooleanField(default=False)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    manager_user_id = models.UUIDField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "platform_branches"
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        unique_together = ("tenant_id", "code")
        indexes = [
            models.Index(fields=["tenant_id", "company"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["company", "is_head_office"]),
            models.Index(fields=["tenant_id", "deleted_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Warehouse(TenantModel, SoftDeleteModel):
    """
    Storage location within a branch.
    Supports future zones/aisles/bins.
    """

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="warehouses")
    warehouse_type = models.CharField(
        max_length=20,
        choices=[(t.value, t.value.title()) for t in WarehouseType],
        default=WarehouseType.MAIN.value,
        db_index=True,
    )
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    street = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    manager_user_id = models.UUIDField(null=True, blank=True, db_index=True)
    supports_bins = models.BooleanField(default=False)
    supports_serial_tracking = models.BooleanField(default=False)
    supports_batch_tracking = models.BooleanField(default=False)

    class Meta:
        db_table = "platform_warehouses"
        verbose_name = "Warehouse"
        verbose_name_plural = "Warehouses"
        unique_together = ("tenant_id", "code")
        indexes = [
            models.Index(fields=["tenant_id", "branch"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "warehouse_type"]),
            models.Index(fields=["tenant_id", "deleted_at"]),
            models.Index(fields=["branch", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class Currency(models.Model):
    """
    Global currency definition (not tenant-scoped).
    Seeded from ISO 4217.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    code = models.CharField(max_length=3, unique=True, db_index=True)  # ISO 4217
    name = models.CharField(max_length=100)  # e.g., South African Rand
    symbol = models.CharField(max_length=10)  # e.g., R
    decimal_places = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "platform_currencies"
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class TaxConfiguration(TenantModel):
    """
    Tax rate configuration.
    Historical records never overwritten. Future rate changes create new records.
    """

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    tax_type = models.CharField(
        max_length=20,
        choices=[(t.value, t.value) for t in TaxType],
        db_index=True,
    )
    tax_category = models.CharField(
        max_length=20,
        choices=[(t.value, t.value.title()) for t in TaxCategory],
        db_index=True,
    )
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 15.00%
    is_recoverable = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    effective_from = models.DateTimeField(db_index=True)
    effective_to = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "platform_tax_configurations"
        verbose_name = "Tax Configuration"
        verbose_name_plural = "Tax Configurations"
        indexes = [
            models.Index(fields=["tenant_id", "tax_type"]),
            models.Index(fields=["tenant_id", "tax_category"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["effective_from", "effective_to"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.rate}%)"


class FiscalYear(TenantModel):
    """
    Accounting fiscal period.
    Status: OPEN, CLOSED, ARCHIVED.
    """

    name = models.CharField(max_length=50)
    start_date = models.DateField(db_index=True)
    end_date = models.DateField(db_index=True)
    status = models.CharField(
        max_length=20,
        choices=[(s.value, s.value.title()) for s in FiscalYearStatus],
        default=FiscalYearStatus.OPEN.value,
        db_index=True,
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "platform_fiscal_years"
        verbose_name = "Fiscal Year"
        verbose_name_plural = "Fiscal Years"
        unique_together = ("tenant_id", "name")
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "start_date", "end_date"]),
            models.Index(fields=["tenant_id", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"


class NumberSequence(TenantModel):
    """
    Auto-incrementing document number sequence.
    Generation must be atomic.
    """

    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=20, blank=True)
    suffix = models.CharField(max_length=20, blank=True)
    current_number = models.BigIntegerField(default=1)
    padding_length = models.IntegerField(default=6)
    reset_policy = models.CharField(
        max_length=20,
        choices=[(p.value, p.value.title()) for p in NumberSequenceResetPolicy],
        default=NumberSequenceResetPolicy.NEVER.value,
        db_index=True,
    )
    last_generated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "platform_number_sequences"
        verbose_name = "Number Sequence"
        verbose_name_plural = "Number Sequences"
        unique_together = ("tenant_id", "name")
        indexes = [
            models.Index(fields=["tenant_id", "name"]),
            models.Index(fields=["tenant_id", "reset_policy"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} - {self.prefix}{self.current_number:0{self.padding_length}d}"


class StoredFile(TenantModel):
    """
    File metadata tracker.
    Binary data stored in external object storage (S3/minio).
    """

    module = models.CharField(max_length=50, db_index=True)  # e.g., "platform"
    entity_type = models.CharField(max_length=50, db_index=True)  # e.g., "company"
    entity_id = models.UUIDField(db_index=True)
    storage_provider = models.CharField(max_length=20)  # s3, minio, local
    storage_path = models.CharField(max_length=500)  # tenant_id/module/entity_id/filename
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    checksum = models.CharField(max_length=64)  # SHA256
    file_size = models.BigIntegerField()  # bytes
    uploaded_by = models.UUIDField(db_index=True)
    uploaded_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = "platform_stored_files"
        verbose_name = "Stored File"
        verbose_name_plural = "Stored Files"
        indexes = [
            models.Index(fields=["tenant_id", "module", "entity_type", "entity_id"]),
            models.Index(fields=["tenant_id", "uploaded_by"]),
            models.Index(fields=["storage_path"]),
        ]

    def __str__(self) -> str:
        return f"{self.original_filename} ({self.module}/{self.entity_type})"