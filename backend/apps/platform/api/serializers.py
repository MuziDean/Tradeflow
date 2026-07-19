"""
API serializers for the Platform module.

Per Backend Engineering Standards §6.2: Serializers handle request parsing
and response formatting only. No business logic.
"""

from rest_framework import serializers

from apps.platform.infrastructure.models import (
    Branch,
    BusinessPreferences,
    Company,
    Currency,
    FiscalYear,
    NumberSequence,
    StoredFile,
    TaxConfiguration,
    Tenant,
    Warehouse,
)
from shared.types.enums import TaxCategory, TaxType


# ──────────────────────────────────────────────
# Tenant
# ──────────────────────────────────────────────


class TenantSerializer(serializers.Serializer):
    """Read-only tenant info response serializer."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.CharField()
    subscription_plan = serializers.CharField()


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Company profile serializer."""

    class Meta:
        model = Company
        fields = [
            "id",
            "legal_name",
            "trading_name",
            "registration_number",
            "tax_number",
            "email",
            "phone",
            "website",
            "logo_path",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class CompanyUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for updating company profile."""

    class Meta:
        model = Company
        fields = [
            "legal_name",
            "trading_name",
            "registration_number",
            "tax_number",
            "email",
            "phone",
            "website",
            "logo_path",
        ]


# ──────────────────────────────────────────────
# Business Preferences
# ──────────────────────────────────────────────


class BusinessPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for business preferences."""

    class Meta:
        model = BusinessPreferences
        fields = [
            "id",
            "default_currency_code",
            "timezone",
            "locale",
            "date_format",
            "time_format",
            "first_day_of_week",
            "allow_negative_stock",
            "receipt_footer",
            "fiscal_year_start_month",
            "decimal_precision",
            "quantity_decimal_places",
            "price_decimal_places",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ──────────────────────────────────────────────
# Branch
# ──────────────────────────────────────────────


class BranchListSerializer(serializers.ModelSerializer):
    """Compact serializer for branch list responses."""

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "code",
            "city",
            "province",
            "country",
            "is_head_office",
            "is_active",
            "created_at",
        ]


class BranchDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single branch response."""

    class Meta:
        model = Branch
        fields = [
            "id",
            "name",
            "code",
            "street",
            "suburb",
            "city",
            "province",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "is_head_office",
            "contact_email",
            "contact_phone",
            "manager_user_id",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class BranchCreateSerializer(serializers.ModelSerializer):
    """Write serializer for branch creation."""

    class Meta:
        model = Branch
        fields = [
            "name",
            "code",
            "street",
            "suburb",
            "city",
            "province",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "is_head_office",
            "contact_email",
            "contact_phone",
            "manager_user_id",
        ]


class BranchUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for branch update."""

    class Meta:
        model = Branch
        fields = [
            "name",
            "code",
            "street",
            "suburb",
            "city",
            "province",
            "postal_code",
            "country",
            "latitude",
            "longitude",
            "is_head_office",
            "contact_email",
            "contact_phone",
            "manager_user_id",
        ]


# ──────────────────────────────────────────────
# Warehouse
# ──────────────────────────────────────────────


class WarehouseListSerializer(serializers.ModelSerializer):
    """Compact serializer for warehouse list responses."""

    warehouse_type = serializers.SerializerMethodField()

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "warehouse_type",
            "is_active",
            "created_at",
        ]

    def get_warehouse_type(self, obj):
        return obj.warehouse_type


class WarehouseDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single warehouse response."""

    class Meta:
        model = Warehouse
        fields = [
            "id",
            "name",
            "code",
            "warehouse_type",
            "street",
            "city",
            "province",
            "country",
            "manager_user_id",
            "supports_bins",
            "supports_serial_tracking",
            "supports_batch_tracking",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class WarehouseCreateSerializer(serializers.ModelSerializer):
    """Write serializer for warehouse creation."""

    class Meta:
        model = Warehouse
        fields = [
            "name",
            "code",
            "warehouse_type",
            "street",
            "city",
            "province",
            "country",
            "manager_user_id",
            "supports_bins",
            "supports_serial_tracking",
            "supports_batch_tracking",
        ]


class WarehouseUpdateSerializer(serializers.ModelSerializer):
    """Write serializer for warehouse update."""

    class Meta:
        model = Warehouse
        fields = [
            "name",
            "code",
            "warehouse_type",
            "street",
            "city",
            "province",
            "country",
            "manager_user_id",
            "supports_bins",
            "supports_serial_tracking",
            "supports_batch_tracking",
        ]


# ──────────────────────────────────────────────
# Currency
# ──────────────────────────────────────────────


class CurrencySerializer(serializers.ModelSerializer):
    """Read-only serializer for currencies."""

    class Meta:
        model = Currency
        fields = [
            "code",
            "name",
            "symbol",
            "decimal_places",
            "is_active",
        ]


# ──────────────────────────────────────────────
# Tax Configuration
# ──────────────────────────────────────────────


class TaxConfigurationListSerializer(serializers.ModelSerializer):
    """Compact serializer for tax config list responses."""

    class Meta:
        model = TaxConfiguration
        fields = [
            "id",
            "name",
            "code",
            "tax_type",
            "tax_category",
            "rate",
            "is_default",
            "is_active",
            "effective_from",
            "created_at",
        ]


class TaxConfigurationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single tax config response."""

    class Meta:
        model = TaxConfiguration
        fields = [
            "id",
            "name",
            "code",
            "tax_type",
            "tax_category",
            "rate",
            "is_recoverable",
            "is_default",
            "effective_from",
            "effective_to",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TaxConfigurationCreateSerializer(serializers.Serializer):
    """Write serializer for tax configuration creation (avoids business logic in serializer)."""

    name = serializers.CharField(max_length=255)
    code = serializers.CharField(max_length=50)
    tax_type = serializers.ChoiceField(choices=[t.value for t in TaxType])
    tax_category = serializers.ChoiceField(choices=[c.value for c in TaxCategory])
    rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    is_recoverable = serializers.BooleanField(default=False)
    is_default = serializers.BooleanField(default=False)
    effective_from = serializers.DateTimeField(required=False)


class TaxConfigurationUpdateSerializer(serializers.Serializer):
    """Write serializer for tax configuration update."""

    name = serializers.CharField(max_length=255, required=False)
    code = serializers.CharField(max_length=50, required=False)
    tax_type = serializers.ChoiceField(
        choices=[t.value for t in TaxType], required=False
    )
    tax_category = serializers.ChoiceField(
        choices=[c.value for c in TaxCategory], required=False
    )
    rate = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)
    is_recoverable = serializers.BooleanField(required=False)
    is_default = serializers.BooleanField(required=False)


# ──────────────────────────────────────────────
# Fiscal Year
# ──────────────────────────────────────────────


class FiscalYearListSerializer(serializers.ModelSerializer):
    """Serializer for fiscal year list responses."""

    class Meta:
        model = FiscalYear
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "status",
            "is_active",
            "created_at",
        ]


class FiscalYearDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single fiscal year response."""

    class Meta:
        model = FiscalYear
        fields = [
            "id",
            "name",
            "start_date",
            "end_date",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class FiscalYearCreateSerializer(serializers.ModelSerializer):
    """Write serializer for fiscal year creation."""

    class Meta:
        model = FiscalYear
        fields = [
            "name",
            "start_date",
            "end_date",
            "status",
        ]


# ──────────────────────────────────────────────
# Number Sequence
# ──────────────────────────────────────────────


class NumberSequenceListSerializer(serializers.ModelSerializer):
    """Serializer for number sequence list responses."""

    class Meta:
        model = NumberSequence
        fields = [
            "id",
            "name",
            "prefix",
            "suffix",
            "current_number",
            "padding_length",
            "reset_policy",
            "last_generated_at",
            "created_at",
        ]


class NumberSequenceDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single number sequence response."""

    class Meta:
        model = NumberSequence
        fields = [
            "id",
            "name",
            "prefix",
            "suffix",
            "current_number",
            "padding_length",
            "reset_policy",
            "last_generated_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "current_number",
            "last_generated_at",
            "created_at",
            "updated_at",
        ]


class NumberSequenceCreateSerializer(serializers.ModelSerializer):
    """Write serializer for number sequence creation."""

    class Meta:
        model = NumberSequence
        fields = [
            "name",
            "prefix",
            "suffix",
            "padding_length",
            "reset_policy",
        ]


# ──────────────────────────────────────────────
# Stored File
# ──────────────────────────────────────────────


class StoredFileListSerializer(serializers.ModelSerializer):
    """Serializer for stored file list responses."""

    class Meta:
        model = StoredFile
        fields = [
            "id",
            "module",
            "entity_type",
            "entity_id",
            "original_filename",
            "mime_type",
            "file_size",
            "uploaded_by",
            "uploaded_at",
            "created_at",
        ]


class StoredFileCreateSerializer(serializers.ModelSerializer):
    """Write serializer for stored file creation."""

    class Meta:
        model = StoredFile
        fields = [
            "module",
            "entity_type",
            "entity_id",
            "storage_provider",
            "storage_path",
            "original_filename",
            "mime_type",
            "checksum",
            "file_size",
        ]




