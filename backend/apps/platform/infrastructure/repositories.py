"""
Repository implementations for the Platform module.

Tenant-scoped queries for organization entities.
Currency repository is global (no tenant_id).
"""

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
from apps.platform.infrastructure.models import (
    Branch as BranchModel,
    BusinessPreferences as BusinessPreferencesModel,
    Company as CompanyModel,
    Currency as CurrencyModel,
    FiscalYear as FiscalYearModel,
    NumberSequence as NumberSequenceModel,
    StoredFile as StoredFileModel,
    TaxConfiguration as TaxConfigurationModel,
    Warehouse as WarehouseModel,
)
from shared.types.enums import WarehouseType


class CompanyRepository:
    """Repository for Company (legal entity)."""

    def get_current(self, tenant_id: str) -> Company | None:
        try:
            model = CompanyModel.objects.filter(tenant_id=tenant_id).first()
            return self._to_entity(model) if model else None
        except Exception:
            return None

    def create(self, company: Company) -> Company:
        model = CompanyModel(
            id=company.id,
            tenant_id=company.tenant_id,
            legal_name=company.legal_name,
            trading_name=company.trading_name,
            registration_number=company.registration_number,
            tax_number=company.tax_number,
            email=company.email,
            phone=company.phone,
            website=company.website,
            logo_path=company.logo_path,
        )
        model.save()
        return self._to_entity(model)

    def update(self, company: Company) -> Company:
        model = CompanyModel.objects.get(id=company.id, tenant_id=company.tenant_id)
        model.legal_name = company.legal_name
        model.trading_name = company.trading_name
        model.registration_number = company.registration_number
        model.tax_number = company.tax_number
        model.email = company.email
        model.phone = company.phone
        model.website = company.website
        model.logo_path = company.logo_path
        model.is_active = company.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, company_id: str, tenant_id: str) -> bool:
        updated = CompanyModel.objects.filter(id=company_id, tenant_id=tenant_id).update(
            is_active=False, deleted_at=timezone.now()
        )
        return updated > 0

    def _to_entity(self, model: CompanyModel) -> Company:
        return Company(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            legal_name=model.legal_name,
            trading_name=model.trading_name,
            registration_number=model.registration_number,
            tax_number=model.tax_number,
            email=model.email,
            phone=model.phone,
            website=model.website or "",
            logo_path=model.logo_path or "",
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class BusinessPreferencesRepository:
    """Repository for BusinessPreferences."""

    def get_for_tenant(self, tenant_id: str) -> BusinessPreferences | None:
        try:
            model = BusinessPreferencesModel.objects.get(tenant_id=tenant_id)
            return self._to_entity(model)
        except BusinessPreferencesModel.DoesNotExist:
            return None

    def create_or_update(self, prefs: BusinessPreferences) -> BusinessPreferences:
        model, _ = BusinessPreferencesModel.objects.update_or_create(
            tenant_id=prefs.tenant_id,
            defaults={
                "default_currency_code": prefs.default_currency_code,
                "timezone": prefs.timezone,
                "locale": prefs.locale,
                "date_format": prefs.date_format,
                "time_format": prefs.time_format,
                "first_day_of_week": prefs.first_day_of_week,
                "allow_negative_stock": prefs.allow_negative_stock,
                "receipt_footer": prefs.receipt_footer,
                "fiscal_year_start_month": prefs.fiscal_year_start_month,
                "decimal_precision": prefs.decimal_precision,
                "quantity_decimal_places": prefs.quantity_decimal_places,
                "price_decimal_places": prefs.price_decimal_places,
            },
        )
        return self._to_entity(model)

    def _to_entity(self, model: BusinessPreferencesModel) -> BusinessPreferences:
        return BusinessPreferences(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            default_currency_code=model.default_currency_code,
            timezone=model.timezone,
            locale=model.locale,
            date_format=model.date_format,
            time_format=model.time_format,
            first_day_of_week=model.first_day_of_week,
            allow_negative_stock=model.allow_negative_stock,
            receipt_footer=model.receipt_footer or "",
            fiscal_year_start_month=model.fiscal_year_start_month,
            decimal_precision=model.decimal_precision,
            quantity_decimal_places=model.quantity_decimal_places,
            price_decimal_places=model.price_decimal_places,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class BranchRepository:
    """Repository for Branch."""

    def get_by_id(self, branch_id: str, tenant_id: str) -> Branch | None:
        try:
            model = BranchModel.objects.get(id=branch_id, tenant_id=tenant_id)
            return self._to_entity(model)
        except BranchModel.DoesNotExist:
            return None

    def list_for_company(self, tenant_id: str, company_id: str) -> list[Branch]:
        return [
            self._to_entity(m)
            for m in BranchModel.objects.filter(tenant_id=tenant_id, company_id=company_id)
        ]

    def create(self, branch: Branch) -> Branch:
        model = BranchModel(
            id=branch.id,
            tenant_id=branch.tenant_id,
            company_id=branch.company_id,
            name=branch.name,
            code=branch.code,
            street=branch.street,
            suburb=branch.suburb,
            city=branch.city,
            province=branch.province,
            postal_code=branch.postal_code,
            country=branch.country,
            latitude=branch.latitude,
            longitude=branch.longitude,
            is_head_office=branch.is_head_office,
            contact_email=branch.contact_email,
            contact_phone=branch.contact_phone,
            manager_user_id=branch.manager_user_id,
        )
        model.save()
        return self._to_entity(model)

    def update(self, branch: Branch) -> Branch:
        model = BranchModel.objects.get(id=branch.id, tenant_id=branch.tenant_id)
        model.name = branch.name
        model.code = branch.code
        model.street = branch.street
        model.suburb = branch.suburb
        model.city = branch.city
        model.province = branch.province
        model.postal_code = branch.postal_code
        model.country = branch.country
        model.latitude = branch.latitude
        model.longitude = branch.longitude
        model.is_head_office = branch.is_head_office
        model.contact_email = branch.contact_email
        model.contact_phone = branch.contact_phone
        model.manager_user_id = branch.manager_user_id
        model.is_active = branch.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, branch_id: str, tenant_id: str) -> bool:
        updated = BranchModel.objects.filter(id=branch_id, tenant_id=tenant_id).update(
            is_active=False, deleted_at=timezone.now()
        )
        return updated > 0

    def _to_entity(self, model: BranchModel) -> Branch:
        return Branch(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            company_id=str(model.company_id),
            name=model.name,
            code=model.code,
            street=model.street,
            suburb=model.suburb or "",
            city=model.city,
            province=model.province,
            postal_code=model.postal_code,
            country=model.country,
            latitude=model.latitude,
            longitude=model.longitude,
            is_head_office=model.is_head_office,
            contact_email=model.contact_email or "",
            contact_phone=model.contact_phone or "",
            manager_user_id=str(model.manager_user_id) if model.manager_user_id else None,
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class WarehouseRepository:
    """Repository for Warehouse."""

    def get_by_id(self, warehouse_id: str, tenant_id: str) -> Warehouse | None:
        try:
            model = WarehouseModel.objects.get(id=warehouse_id, tenant_id=tenant_id)
            return self._to_entity(model)
        except WarehouseModel.DoesNotExist:
            return None

    def list_for_branch(self, tenant_id: str, branch_id: str) -> list[Warehouse]:
        return [
            self._to_entity(m)
            for m in WarehouseModel.objects.filter(tenant_id=tenant_id, branch_id=branch_id)
        ]

    def create(self, warehouse: Warehouse) -> Warehouse:
        model = WarehouseModel(
            id=warehouse.id,
            tenant_id=warehouse.tenant_id,
            branch_id=warehouse.branch_id,
            warehouse_type=warehouse.warehouse_type.value,
            code=warehouse.code,
            name=warehouse.name,
            street=warehouse.street,
            city=warehouse.city,
            province=warehouse.province,
            country=warehouse.country,
            manager_user_id=warehouse.manager_user_id,
            supports_bins=warehouse.supports_bins,
            supports_serial_tracking=warehouse.supports_serial_tracking,
            supports_batch_tracking=warehouse.supports_batch_tracking,
        )
        model.save()
        return self._to_entity(model)

    def update(self, warehouse: Warehouse) -> Warehouse:
        model = WarehouseModel.objects.get(id=warehouse.id, tenant_id=warehouse.tenant_id)
        model.warehouse_type = warehouse.warehouse_type.value
        model.code = warehouse.code
        model.name = warehouse.name
        model.street = warehouse.street
        model.city = warehouse.city
        model.province = warehouse.province
        model.country = warehouse.country
        model.manager_user_id = warehouse.manager_user_id
        model.supports_bins = warehouse.supports_bins
        model.supports_serial_tracking = warehouse.supports_serial_tracking
        model.supports_batch_tracking = warehouse.supports_batch_tracking
        model.is_active = warehouse.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, warehouse_id: str, tenant_id: str) -> bool:
        updated = WarehouseModel.objects.filter(id=warehouse_id, tenant_id=tenant_id).update(
            is_active=False, deleted_at=timezone.now()
        )
        return updated > 0

    def _to_entity(self, model: WarehouseModel) -> Warehouse:
        return Warehouse(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            branch_id=str(model.branch_id),
            warehouse_type=WarehouseType(model.warehouse_type),
            code=model.code,
            name=model.name,
            street=model.street or "",
            city=model.city or "",
            province=model.province or "",
            country=model.country or "",
            manager_user_id=str(model.manager_user_id) if model.manager_user_id else None,
            is_active=model.is_active,
            supports_bins=model.supports_bins,
            supports_serial_tracking=model.supports_serial_tracking,
            supports_batch_tracking=model.supports_batch_tracking,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class CurrencyRepository:
    """Repository for global Currency records."""

    def list_all(self) -> list[Currency]:
        return [self._to_entity(m) for m in CurrencyModel.objects.filter(is_active=True)]

    def get_by_code(self, code: str) -> Currency | None:
        try:
            model = CurrencyModel.objects.get(code=code.upper())
            return self._to_entity(model)
        except CurrencyModel.DoesNotExist:
            return None

    def bulk_create(self, currencies: list[Currency]) -> None:
        models = [
            CurrencyModel(
                id=c.id,
                code=c.code.upper(),
                name=c.name,
                symbol=c.symbol,
                decimal_places=c.decimal_places,
                is_active=c.is_active,
            )
            for c in currencies
        ]
        CurrencyModel.objects.bulk_create(models, ignore_conflicts=True)

    def _to_entity(self, model: CurrencyModel) -> Currency:
        return Currency(
            id=str(model.id),
            code=model.code,
            name=model.name,
            symbol=model.symbol,
            decimal_places=model.decimal_places,
            is_active=model.is_active,
            created_at=model.created_at,
        )


class TaxConfigurationRepository:
    """Repository for TaxConfiguration."""

    def get_by_id(self, tax_id: str, tenant_id: str) -> TaxConfiguration | None:
        try:
            model = TaxConfigurationModel.objects.get(id=tax_id, tenant_id=tenant_id)
            return self._to_entity(model)
        except TaxConfigurationModel.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[TaxConfiguration]:
        qs = TaxConfigurationModel.objects.filter(tenant_id=tenant_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_entity(m) for m in qs]

    def create(self, tax: TaxConfiguration) -> TaxConfiguration:
        model = TaxConfigurationModel(
            id=tax.id,
            tenant_id=tax.tenant_id,
            name=tax.name,
            code=tax.code,
            tax_type=tax.tax_type,
            tax_category=tax.tax_category,
            rate=tax.rate,
            is_recoverable=tax.is_recoverable,
            is_default=tax.is_default,
            effective_from=tax.effective_from,
            effective_to=tax.effective_to,
        )
        model.save()
        return self._to_entity(model)

    def _to_entity(self, model: TaxConfigurationModel) -> TaxConfiguration:
        return TaxConfiguration(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            code=model.code,
            tax_type=model.tax_type,
            tax_category=model.tax_category,
            rate=float(model.rate),
            is_recoverable=model.is_recoverable,
            is_default=model.is_default,
            effective_from=model.effective_from,
            effective_to=model.effective_to,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class FiscalYearRepository:
    """Repository for FiscalYear."""

    def get_by_id(self, fiscal_year_id: str, tenant_id: str) -> FiscalYear | None:
        try:
            model = FiscalYearModel.objects.get(id=fiscal_year_id, tenant_id=tenant_id)
            return self._to_entity(model)
        except FiscalYearModel.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str) -> list[FiscalYear]:
        return [self._to_entity(m) for m in FiscalYearModel.objects.filter(tenant_id=tenant_id)]

    def create(self, fiscal_year: FiscalYear) -> FiscalYear:
        model = FiscalYearModel(
            id=fiscal_year.id,
            tenant_id=fiscal_year.tenant_id,
            name=fiscal_year.name,
            start_date=fiscal_year.start_date,
            end_date=fiscal_year.end_date,
            status=fiscal_year.status,
        )
        model.save()
        return self._to_entity(model)

    def close(self, fiscal_year_id: str, tenant_id: str) -> FiscalYear | None:
        try:
            model = FiscalYearModel.objects.get(id=fiscal_year_id, tenant_id=tenant_id)
            model.status = "closed"
            model.save()
            return self._to_entity(model)
        except FiscalYearModel.DoesNotExist:
            return None

    def _to_entity(self, model: FiscalYearModel) -> FiscalYear:
        return FiscalYear(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            start_date=model.start_date,
            end_date=model.end_date,
            status=model.status,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class NumberSequenceRepository:
    """Repository for NumberSequence with atomic generation."""

    def get_by_id(self, sequence_id: str, tenant_id: str) -> NumberSequence | None:
        try:
            model = NumberSequenceModel.objects.get(id=sequence_id, tenant_id=tenant_id)
            return self._to_entity(model)
        except NumberSequenceModel.DoesNotExist:
            return None

    def get_by_name(self, tenant_id: str, name: str) -> NumberSequence | None:
        try:
            model = NumberSequenceModel.objects.get(tenant_id=tenant_id, name=name)
            return self._to_entity(model)
        except NumberSequenceModel.DoesNotExist:
            return None

    def create(self, seq: NumberSequence) -> NumberSequence:
        model = NumberSequenceModel(
            id=seq.id,
            tenant_id=seq.tenant_id,
            name=seq.name,
            prefix=seq.prefix,
            suffix=seq.suffix,
            current_number=seq.current_number,
            padding_length=seq.padding_length,
            reset_policy=seq.reset_policy,
        )
        model.save()
        return self._to_entity(model)

    def create_or_update(self, seq: NumberSequence) -> NumberSequence:
        model, _ = NumberSequenceModel.objects.update_or_create(
            id=seq.id,
            tenant_id=seq.tenant_id,
            defaults={
                "name": seq.name,
                "prefix": seq.prefix,
                "suffix": seq.suffix,
                "current_number": seq.current_number,
                "padding_length": seq.padding_length,
                "reset_policy": seq.reset_policy,
            },
        )
        return self._to_entity(model)

    @transaction.atomic
    def get_next_number(self, tenant_id: str, name: str) -> int:
        """Atomically increment and return next number."""
        model = NumberSequenceModel.objects.select_for_update().get(tenant_id=tenant_id, name=name)
        number = model.current_number
        model.current_number += 1
        model.last_generated_at = timezone.now()
        model.save()
        return number

    def _to_entity(self, model: NumberSequenceModel) -> NumberSequence:
        return NumberSequence(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            prefix=model.prefix or "",
            suffix=model.suffix or "",
            current_number=model.current_number,
            padding_length=model.padding_length,
            reset_policy=model.reset_policy,
            last_generated_at=model.last_generated_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class StoredFileRepository:
    """Repository for StoredFile metadata."""

    def create(self, stored_file: StoredFile) -> StoredFile:
        model = StoredFileModel(
            id=stored_file.id,
            tenant_id=stored_file.tenant_id,
            module=stored_file.module,
            entity_type=stored_file.entity_type,
            entity_id=stored_file.entity_id,
            storage_provider=stored_file.storage_provider,
            storage_path=stored_file.storage_path,
            original_filename=stored_file.original_filename,
            mime_type=stored_file.mime_type,
            checksum=stored_file.checksum,
            file_size=stored_file.file_size,
            uploaded_by=stored_file.uploaded_by,
            uploaded_at=stored_file.uploaded_at,
        )
        model.save()
        return self._to_entity(model)

    def get_by_entity(self, tenant_id: str, entity_type: str, entity_id: str) -> list[StoredFile]:
        qs = StoredFileModel.objects.filter(
            tenant_id=tenant_id, entity_type=entity_type, entity_id=entity_id
        )
        return [self._to_entity(m) for m in qs]

    def _to_entity(self, model: StoredFileModel) -> StoredFile:
        return StoredFile(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            module=model.module,
            entity_type=model.entity_type,
            entity_id=str(model.entity_id),
            storage_provider=model.storage_provider,
            storage_path=model.storage_path,
            original_filename=model.original_filename,
            mime_type=model.mime_type,
            checksum=model.checksum,
            file_size=model.file_size,
            uploaded_by=str(model.uploaded_by),
            uploaded_at=model.uploaded_at,
            created_at=model.created_at,
        )