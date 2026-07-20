# Milestone 6 — Step 1: Inventory Domain Foundation Validation

**Module:** Inventory — Stock Management Foundation
**Date:** 2026-07-20
**Status:** Complete ✅

---

## 1. Entity Relationship Summary

```
Tenant (implicit via tenant_id)
└── InventoryItem (1:N per warehouse/product/variant/batch/serial)
    ├── StockBalance (1:N periodic snapshots)
    ├── StockReservation (1:N reservations)
    ├── StockMovement (N:1 header)
    │   └── MovementLine (1:N lines)
    ├── StockAdjustment (N:1 header)
    │   └── AdjustmentLine (1:N lines)
    ├── StockTransfer (N:1 header)
    │   └── TransferLine (1:N lines)
    └── CycleCount (N:1 header)
        └── CycleCountLine (1:N lines)
```

## 2. Architecture

```
apps/inventory/
├── __init__.py
├── domain/
│   ├── __init__.py
│   └── entities.py              # 11 domain entities
└── infrastructure/
    ├── __init__.py
    ├── models.py                 # 11 Django ORM models
    └── repositories.py           # 11 repository classes
```

### Key Architecture Decision

**Inventory is completely separated from Retail.**
- Retail owns products (catalog, brands, categories, suppliers).
- Inventory owns stock (quantities, movements, balances, adjustments, transfers, reservations, cycle counts).
- No stock quantities are stored on Product or ProductVariant.
- Cross-module FK references to `retail.Product`, `retail.ProductVariant`, `retail.Supplier`, and `platform.Warehouse` are acceptable because inventory tracks stock *for* these entities.
- In the future when these become separate services/microservices, FKs become logical references.

---

## 3. Entity List

| Entity | Description | Key Fields |
|--------|-------------|------------|
| **InventoryItem** | Core inventory record linking product to warehouse | warehouse_id, product_id, variant_id, quantity fields, batch/serial, reorder settings |
| **StockBalance** | Periodic snapshot for reporting | inventory_item_id, snapshot_date, quantity fields, unit_cost, total_value, costing_method |
| **StockMovement** | Header-level inventory transaction | warehouse_id, movement_type, status, reference_type/id, performed_by |
| **MovementLine** | Line item within a stock movement | movement_id, inventory_item_id, product_id, quantity, unit_cost, batch/serial |
| **StockAdjustment** | Header-level stock adjustment | warehouse_id, adjustment_type, status, reason, performed_by, approved_by |
| **AdjustmentLine** | Line item within an adjustment | adjustment_id, inventory_item_id, quantity_before, quantity_after, quantity_delta |
| **StockTransfer** | Header-level warehouse transfer | source_warehouse_id, destination_warehouse_id, status, shipped_at, received_at |
| **TransferLine** | Line item within a transfer | transfer_id, product_id, quantity, quantity_received |
| **StockReservation** | Inventory reservation for orders | inventory_item_id, quantity, quantity_allocated, status, reference_type/id |
| **CycleCount** | Scheduled/ad-hoc inventory count | warehouse_id, zone_id, status, scheduled_date, counted_by |
| **CycleCountLine** | Line item within a cycle count | cycle_count_id, inventory_item_id, system_quantity, counted_quantity, variance |

---

## 4. Repository List

| Repository | Key Methods |
|------------|-------------|
| **InventoryItemRepository** | list_for_warehouse, list_for_product, get_by_id, get_by_product, create, update, adjust_quantity |
| **StockBalanceRepository** | list_for_warehouse, get_for_item_date, create |
| **StockMovementRepository** | list_for_warehouse, get_by_id, create, update |
| **MovementLineRepository** | list_for_movement, create |
| **StockAdjustmentRepository** | list_for_warehouse, get_by_id, create, update |
| **AdjustmentLineRepository** | list_for_adjustment, create |
| **StockTransferRepository** | list_for_warehouse, get_by_id, create, update |
| **TransferLineRepository** | list_for_transfer, create |
| **StockReservationRepository** | list_for_inventory_item, list_for_reference, get_by_id, create, update |
| **CycleCountRepository** | list_for_warehouse, get_by_id, create, update |
| **CycleCountLineRepository** | list_for_cycle_count, create |

All repositories:
- Return domain entities, not ORM models
- Use `_to_entity()` for ORM → domain conversion
- Contain **no business logic** — persistence only
- Support tenant-scoped queries via explicit `tenant_id` parameters

---

## 5. Enums Added

| Enum | Values | Location |
|------|--------|----------|
| **MovementStatus** | draft, posted, cancelled | `shared/types/enums.py` |
| **AdjustmentType** | correction, damage, loss, found, write_off, manual | `shared/types/enums.py` |
| **ReservationStatus** | pending, allocated, released, completed, cancelled | `shared/types/enums.py` |
| **CycleCountStatus** | scheduled, in_progress, completed, adjusted, cancelled | `shared/types/enums.py` |

### Movement Types Expanded

The existing `StockMovementType` enum was expanded from 7 to 12 values:

| Before | After |
|--------|-------|
| sale, grn, transfer_in, transfer_out, adjustment, return, stock_take | purchase_receipt, sale, sale_return, purchase_return, transfer_in, transfer_out, adjustment_in, adjustment_out, opening_balance, stock_count, production_in, production_out |

---

## 6. Inventory Rules Enforced

- Stock quantities are NEVER stored on Product (Retail).
- Inventory items belong to: Tenant + Warehouse + Product + Variant(optional) + Batch(optional) + Serial(optional).
- Movement status lifecycle: Draft → Posted → Cancelled.
- Reservation status lifecycle: Pending → Allocated → Released → Completed.
- Transfer status lifecycle: Draft → In Transit → Completed → Cancelled.
- Cycle count status lifecycle: Scheduled → In Progress → Completed → Adjusted.
- Adjustment requires approval (via `approved_by` field).
- Quantity is always positive; direction implied by `movement_type`.

---

## 7. Tenant Isolation Review

| Entity | Tenant-Scoped | Mechanism |
|--------|---------------|-----------|
| InventoryItem | Yes (tenant_id) | Inherits TenantModel |
| StockBalance | Yes (tenant_id) | Inherits TenantModel |
| StockMovement | Yes (tenant_id) | Inherits TenantModel |
| MovementLine | Yes (tenant_id) | Inherits TenantModel |
| StockAdjustment | Yes (tenant_id) | Inherits TenantModel |
| AdjustmentLine | Yes (tenant_id) | Inherits TenantModel |
| StockTransfer | Yes (tenant_id) | Inherits TenantModel |
| TransferLine | Yes (tenant_id) | Inherits TenantModel |
| StockReservation | Yes (tenant_id) | Inherits TenantModel |
| CycleCount | Yes (tenant_id) | Inherits TenantModel |
| CycleCountLine | Yes (tenant_id) | Inherits TenantModel |

All models inherit from `TenantModel`, which injects `tenant_id` on save and auto-filters reads via `TenantAwareManager`.

Every repository method filters by `tenant_id` explicitly, ensuring defense-in-depth.

---

## 8. Index Strategy

### Composite Indexes (tenant-first)
All composite indexes lead with `tenant_id` to support tenant-aware queries:
- `tenant_id + warehouse` — warehouse item listings
- `tenant_id + product` — product stock across warehouses
- `tenant_id + variant` — variant stock
- `tenant_id + batch_number`, `tenant_id + serial_number` — traceability lookups
- `tenant_id + expiry_date` — expiry tracking
- `tenant_id + quantity_on_hand`, `tenant_id + quantity_available` — stock level queries
- `tenant_id + reorder_point + quantity_on_hand` — low stock detection (named `idx_low_stock`)
- `tenant_id + warehouse + movement_type` — movement filtering
- `tenant_id + movement_type + status` — status-based queries
- `tenant_id + reference_type + reference_id` — document cross-referencing
- `tenant_id + snapshot_date + is_finalized` — balance snapshots
- `tenant_id + status + expires_at` — reservation expiry
- `tenant_id + status + scheduled_date` — cycle count scheduling

### Single-Field Indexes
- `status` — common status filtering
- `performed_by` — user action audit
- `posted_at` — time-range queries
- `reference_number` — document lookups
- `scheduled_date` — scheduling queries

---

## 9. Unique Constraints

| Entity | Constraint |
|--------|------------|
| InventoryItem | (tenant_id, warehouse, product, variant, batch_number, serial_number) |
| StockBalance | (tenant_id, inventory_item, snapshot_date) |

---

## 10. Future Extensibility

| Future Feature | Current Foundation |
|----------------|-------------------|
| **Batch Tracking** | `batch_number`, `lot_number` fields on InventoryItem, MovementLine, AdjustmentLine, TransferLine, CycleCountLine |
| **Serial Tracking** | `serial_number` fields on InventoryItem and all line-level entities |
| **Expiry Tracking** | `expiry_date` on InventoryItem and all line-level entities |
| **Warehouse Zones** | `zone_id` (UUID FK placeholder) on CycleCount |
| **Warehouse Bins** | `bin_location` on CycleCountLine |
| **Multiple Units of Measure** | `unit_cost` prepared on all value-tracking entities |
| **FIFO/LIFO/Weighted Average** | `costing_method` and `unit_cost`/`total_value` on StockBalance |
| **Negative Stock Policy** | `quantity_available` computed separately from `quantity_on_hand` |
| **Reserved Stock** | `quantity_reserved` and `StockReservation` entity |
| **Committed Stock** | `quantity_committed` on InventoryItem |
| **Damaged Stock** | `quantity_damaged` and `quantity_quarantine` on InventoryItem |
| **Manufacturing** | `PRODUCTION_IN`, `PRODUCTION_OUT` movement types |
| **Procurement** | `PURCHASE_RECEIPT`, `PURCHASE_RETURN` movement types; `reference_type = "purchase_order"` |
| **Sales** | `SALE`, `SALE_RETURN` movement types; `reference_type = "sales_order"` |
| **Reporting** | `StockBalance` snapshots provide daily/weekly/monthly data |
| **Costing** | `unit_cost`, `total_value`, `costing_method` on StockBalance |

---

## 11. Constraints

### InventoryItem
- **PK:** id (UUID)
- **Unique:** (tenant_id, warehouse, product, variant, batch_number, serial_number)
- **Indexes:** 10 composite indexes including low-stock detection index
- **F-Keys:** warehouse → platform.Warehouse, product → retail.Product, variant → retail.ProductVariant, preferred_supplier → retail.Supplier

### StockBalance
- **PK:** id (UUID)
- **Unique:** (tenant_id, inventory_item, snapshot_date)
- **Indexes:** 3 composite indexes
- **F-Keys:** inventory_item → InventoryItem, warehouse → platform.Warehouse, product → retail.Product, variant → retail.ProductVariant

### StockMovement
- **PK:** id (UUID)
- **Indexes:** 5 composite indexes
- **F-Keys:** warehouse → platform.Warehouse

### MovementLine
- **PK:** id (UUID)
- **Indexes:** 5 composite indexes
- **F-Keys:** movement → StockMovement, inventory_item → InventoryItem, product → retail.Product, variant → retail.ProductVariant

### StockAdjustment
- **PK:** id (UUID)
- **Indexes:** 4 composite indexes
- **F-Keys:** warehouse → platform.Warehouse

### AdjustmentLine
- **PK:** id (UUID)
- **Indexes:** 3 composite indexes
- **F-Keys:** adjustment → StockAdjustment, inventory_item → InventoryItem, product → retail.Product, variant → retail.ProductVariant

### StockTransfer
- **PK:** id (UUID)
- **Indexes:** 4 composite indexes
- **F-Keys:** source_warehouse → platform.Warehouse, destination_warehouse → platform.Warehouse

### TransferLine
- **PK:** id (UUID)
- **Indexes:** 2 composite indexes
- **F-Keys:** transfer → StockTransfer, product → retail.Product, variant → retail.ProductVariant

### StockReservation
- **PK:** id (UUID)
- **Indexes:** 4 composite indexes
- **F-Keys:** inventory_item → InventoryItem, product → retail.Product, variant → retail.ProductVariant, warehouse → platform.Warehouse

### CycleCount
- **PK:** id (UUID)
- **Indexes:** 3 composite indexes
- **F-Keys:** warehouse → platform.Warehouse

### CycleCountLine
- **PK:** id (UUID)
- **Indexes:** 3 composite indexes
- **F-Keys:** cycle_count → CycleCount, inventory_item → InventoryItem, product → retail.Product, variant → retail.ProductVariant

---

## 12. Repository Pattern Compliance

All repositories:
- [x] Return domain entities, not ORM models
- [x] Accept domain entities as parameters
- [x] Use `_to_entity()` for ORM → domain conversion
- [x] Contain **no business logic** — persistence only
- [x] Support tenant-scoped queries via explicit `tenant_id` parameters

---

## 13. Validation Checklist

- [x] All 11 entities defined with correct fields
- [x] Tenant-scoped models inherit TenantModel
- [x] UUID primary keys on all models
- [x] created_at / updated_at on all models
- [x] Proper unique constraints
- [x] Proper indexes (tenant-first composites)
- [x] No stock quantities stored on Retail.Product
- [x] Future serial number tracking supported
- [x] Future batch/lot tracking supported
- [x] Future expiry tracking supported
- [x] Future bin/zone tracking prepared
- [x] Future costing methods prepared (FIFO/LIFO/WA)
- [x] Movement types support purchasing, sales, POS, manufacturing, reporting
- [x] Reservation status lifecycle defined
- [x] All 11 repositories implemented with _to_entity()
- [x] No business logic in repositories
- [x] All repositories filter by tenant_id
- [x] All enums in shared/types/enums.py (not duplicated)
- [x] 11 infrastructure models with proper FKs and indexes
- [x] No services, no API, no serializers, no views, no tests created

---

## 14. Known Assumptions

1. **WarehouseZone** does not exist yet — CycleCount stores `zone_id` as a raw UUID FK placeholder.
2. **Decimal precision** uses 3 decimal places for quantities (supports fractional units) and 4 decimal places for costs.
3. **Batch/Serial granularity** is at the InventoryItem level — each unique batch/serial creates its own InventoryItem record.
4. **Movement direction** is implied by `movement_type` — quantity is always stored as positive on lines.
5. **Financial valuation** is not tracked in inventory — `unit_cost`/`total_value` are informational only.
6. **No approval workflows** are enforced at the persistence layer — `approved_by` is stored but not validated.
7. **Inventory snapshots** (StockBalance) are created by application services, not by database triggers.
8. **Cross-module FK references** to Retail and Platform modules are acceptable for a modular monolith.

---

## 15. Ready for Step 2

All domain entities, Django models, and repositories are defined and validated. Ready for service layer implementation.

**Next Steps:**
- Step 2: Application services
- Step 3: API layer (serializers, views, URLs)
- Step 4: Validation + hardening

---

**Last Updated:** 2026-07-20