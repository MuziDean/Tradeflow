# Milestone 4 — Step 2: Service Validation Report

**Date:** 2026-07-16  
**Status:** ✅ Complete

## Service Responsibilities

| Service | Responsibility |
|---------|----------------|
| **CompanyService** | Create, update, archive (soft delete) company. Legal entity only. |
| **BusinessPreferencesService** | Get/update operational settings. One-to-one per tenant. |
| **BranchService** | CRUD + list branches. Enforce single head office. Soft delete. |
| **WarehouseService** | CRUD + list warehouses per branch. Soft delete. |
| **CurrencyService** | Read-only list/get. Admin seed ISO 4217. |
| **TaxConfigurationService** | Create, immutable history, version on update. |
| **FiscalYearService** | Create, close fiscal years. |
| **NumberSequenceService** | Atomic document number generation. Reset. |
| **StoredFileService** | Create file metadata, get files by entity. |

## Transaction Boundaries

- CompanyService: create/update/archive → atomic
- BusinessPreferencesService: update → atomic
- BranchService: create/update → atomic; delete → repo-level soft delete
- WarehouseService: create/update → atomic; delete → repo-level soft delete
- TaxConfigurationService: create/update → atomic (new version)
- FiscalYearService: create/close → atomic
- NumberSequenceService: get_next_number → atomic + select_for_update; reset → atomic
- CurrencyService: seed → bulk_create (idempotent)
- StoredFileService: create → repo-level

## Validation Strategy (in Service, not Repository)

1. Branch: first branch auto head office; only one head office per company
2. Tax: historical records never overwritten; new rate = new record
3. Number Sequence: select_for_update prevents race conditions
4. Company: soft delete only
5. Currency: read-only for non-admin

## Domain Events Emitted

- CompanyCreated, CompanyUpdated, CompanyArchived
- BranchCreated, WarehouseCreated
- FiscalYearClosed, NumberSequenceReset

Events inherit `shared.events.base.DomainEvent`, use `.emit()`, logged via logger.

## Repository Interactions

All services depend on repositories for persistence only. No business rules in repositories.
Listed in STEP2: CompanyRepository, BusinessPreferencesRepository, BranchRepository,
WarehouseRepository, CurrencyRepository, TaxConfigurationRepository, FiscalYearRepository,
NumberSequenceRepository, StoredFileRepository.

## Security Considerations

1. Tenant Isolation via tenant_id
2. Deny-by-default (API layer Step 3)
3. Soft Delete for Company/Branch/Warehouse
4. Tax History Immutable
5. Currency Read-only for non-admin
6. Audit Trail via events
7. Transaction Safety

## Future Extensibility

- NumberSequence: reset_policy automation via Celery
- Tax: effective_from/to scheduling
- Warehouse: supports_bins/serial/batch flags → future WarehouseZone/Aisle/Bin
- Branch: manager_user_id → future manager dashboard
- StoredFile: external S3/minio, future async upload + scanning
- Events: future event bus + outbox + audit subscriber

## Validation Checklist

- [x] One service per business capability
- [x] Repositories persistence only
- [x] Validation in services
- [x] Multi-entity ops atomic
- [x] Domain events emitted
- [x] NumberSequenceService concurrency-safe
- [x] CurrencyService read-only except admin
- [x] TaxConfigurationService immutable history
- [x] Company archive cascades via business rules

## Files Modified

- `apps/platform/application/services.py` — All 9 services + domain events

## Ready for Step 3

All services implemented and validated. Ready for API layer.