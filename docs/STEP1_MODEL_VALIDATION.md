# Milestone 4 — Step 1: Model Validation Report

**Date:** 2026-07-16  
**Status:** ✅ Complete

---

## Entity Relationship Summary

```
Tenant (implicit via tenant_id)
├── Company (1:1, soft delete)
│   └── Branches (1:N, soft delete)
│       └── Warehouses (1:N, soft delete)
├── BusinessPreferences (1:1)
├── TaxConfigurations (1:N)
├── FiscalYears (1:N)
├── NumberSequences (1:N)
├── StoredFiles (1:N)
└── Currencies (global, no FK)

Warehouse Types: MAIN, RETAIL, TRANSIT, RETURNS, DAMAGED, VIRTUAL
Tax Categories: STANDARD, REDUCED, ZERO, EXEMPT
Tax Types: VAT, SALES_TAX, INCOME_TAX
Fiscal Year Status: OPEN, CLOSED, ARCHIVED
Number Sequence Reset: NEVER, YEARLY, MONTHLY, DAILY
```

---

## Constraints

### Company
- **PK:** id (UUID)
- **Unique:** (tenant_id, registration_number), registration_number, tax_number
- **Soft Delete:** is_active + deleted_at
- **One per tenant:** enforced by unique tenant_id in BusinessPreferences

### Branch
- **PK:** id (UUID)
- **Unique:** (tenant_id, code)
- **FK:** company_id → Company(id)
- **Soft Delete:** is_active + deleted_at

### Warehouse
- **PK:** id (UUID)
- **Unique:** (tenant_id, code)
- **FK:** branch_id → Branch(id)
- **Soft Delete:** is_active + deleted_at

### Currency
- **PK:** id (UUID)
- **Unique:** code (ISO 4217)
- **Global:** no tenant_id

### TaxConfiguration
- **PK:** id (UUID)
- **FK:** tenant_id (implicit)
- **No unique constraint on code** — allows historical rate changes
- **Immutable history:** effective_from/effective_to define validity period

### FiscalYear
- **PK:** id (UUID)
- **Unique:** (tenant_id, name)
- **FK:** tenant_id

### NumberSequence
- **PK:** id (UUID)
- **Unique:** (tenant_id, name)
- **Atomic:** current_number incremented via select_for_update

### BusinessPreferences
- **PK:** id (UUID)
- **Unique:** tenant_id (one-to-one)

### StoredFile
- **PK:** id (UUID)
- **FK:** tenant_id, uploaded_by
- **No binary data:** metadata only

---

## Indexes

### Company
- tenant_id + is_active
- tenant_id + deleted_at
- registration_number
- tax_number

### Branch
- tenant_id + company
- tenant_id + is_active
- company + is_head_office
- tenant_id + deleted_at

### Warehouse
- tenant_id + branch
- tenant_id + is_active
- tenant_id + warehouse_type
- tenant_id + deleted_at
- branch + is_active

### Currency
- code
- is_active

### TaxConfiguration
- tenant_id + tax_type
- tenant_id + tax_category
- tenant_id + is_active
- effective_from + effective_to

### FiscalYear
- tenant_id + status
- tenant_id + start_date + end_date
- tenant_id + is_active

### NumberSequence
- tenant_id + name
- tenant_id + reset_policy

### StoredFile
- tenant_id + module + entity_type + entity_id
- tenant_id + uploaded_by
- storage_path

---

## Soft Delete Strategy

- **Company:** Soft delete only (deleted_at). Cascades to branches/warehouses via is_active.
- **Branch:** Soft delete (is_active + deleted_at). Warehouses remain but inactive.
- **Warehouse:** Soft delete (is_active + deleted_at). Stock movements reference warehouse_id.
- **Others:** No soft delete (TaxConfig, FiscalYear, NumberSequence, Currency, BusinessPreferences, StoredFile).

### Rationale
- Legal entities (Company) must never be hard-deleted for audit/compliance.
- Operational entities (Branch, Warehouse) can be deactivated but history preserved.

---

## Tenant Isolation Verification

| Model | Tenant-Scoped | Filtering |
|-------|--------------|-----------|
| Company | Yes (tenant_id) | All queries filter by tenant_id |
| Branch | Yes (tenant_id) | Inherits from TenantModel |
| Warehouse | Yes (tenant_id) | Inherits from TenantModel |
| Currency | **No (global)** | No tenant filter |
| TaxConfiguration | Yes (tenant_id) | All queries filter by tenant_id |
| FiscalYear | Yes (tenant_id) | All queries filter by tenant_id |
| NumberSequence | Yes (tenant_id) | All queries filter by tenant_id |
| BusinessPreferences | Yes (tenant_id) | Unique per tenant |
| StoredFile | Yes (tenant_id) | All queries filter by tenant_id |

---

## Future Extensibility Notes

### Warehouse Bins/Zones
- Warehouse supports bins via `supports_bins` flag
- Future `WarehouseZone` and `WarehouseAisle` models can FK to Warehouse
- `code` field on Warehouse reserves namespace for bin-level codes

### Multi-Currency
- Currency table is global and seedable
- BusinessPreferences stores `default_currency_code`
- Future `ExchangeRate` model can track historical rates

### Tax History
- TaxConfiguration uses effective_from/effective_to
- New rates create new records (immutable history)
- `is_default` flags current active rate

### Audit Integration
- All models have `created_at`, `updated_at`
- Soft-deletable models have `deleted_at`
- Audit module (Milestone 8) can track changes without schema modifications

### File Storage
- StoredFile tracks metadata only
- Binary data stored in S3/minio via path `tenant_id/module/entity_id/filename`
- Checksum (SHA256) ensures integrity
- No storage provider lock-in

---

## Amendments Applied

1. ✅ Company — legal info only, soft delete
2. ✅ BusinessPreferences — operational config, one-to-one with tenant
3. ✅ Branch — structured address fields, is_head_office, contact info
4. ✅ Warehouse — warehouse_type enum, structured address, future bin support flags
5. ✅ Currency — global, no tenant_id, seeded from ISO 4217
6. ✅ TaxConfiguration — tax_category, is_default, immutable history
7. ✅ FiscalYear — status enum (OPEN, CLOSED, ARCHIVED)
8. ✅ NumberSequence — reset_policy, last_generated_at, atomic generation
9. ✅ StoredFile — metadata only, external storage
10. ✅ Soft delete — Company, Branch, Warehouse
11. ✅ Indexes — all key fields indexed
12. ✅ Auditing — created_at/updated_at on all models

---

## Files Created

- `shared/types/enums.py` — Added WarehouseType, TaxCategory, TaxType, FiscalYearStatus, NumberSequenceResetPolicy
- `apps/platform/domain/entities.py` — All domain entities
- `apps/platform/infrastructure/models.py` — All Django models with base classes

---

## Validation Checklist

- [x] All entities defined with correct fields
- [x] Tenant-scoped models inherit TenantModel
- [x] Soft-deletable models inherit SoftDeleteModel
- [x] Unique constraints enforced
- [x] Indexes on all key fields
- [x] Foreign keys defined
- [x] Enums centralized in shared/types/enums.py
- [x] No circular dependencies
- [x] Company contains legal info only
- [x] BusinessPreferences contains operational config
- [x] Warehouse supports future bins/zones
- [x] Currency is global
- [x] Tax history immutable
- [x] Fiscal year status enum
- [x] Number sequence atomic-ready
- [x] StoredFile metadata only

---

## Ready for Step 2

All domain entities and models are defined, validated, and ready for repository implementation.