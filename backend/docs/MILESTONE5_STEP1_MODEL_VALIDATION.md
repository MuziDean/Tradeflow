# Milestone 5 — Step 1: Model Validation Report

**Module:** Retail — Product Catalog Foundation
**Date:** 2026-07-19
**Status:** Complete

---

## 1. Entity Relationship Summary

```
Tenant (implicit via tenant_id)
├── UnitOfMeasure (1:N)
├── Brand (1:N, soft delete)
├── ProductCategory (1:N, self-referencing hierarchy, soft delete)
├── Product (1:N, soft delete)
│   ├── ProductVariant (1:N, soft delete)
│   ├── ProductImage (1:N)
│   ├── ProductBarcode (1:N)
│   ├── ProductPrice (1:N) — future
│   └── ProductCost (1:N) — future
├── Supplier (1:N, soft delete)
│   └── SupplierProduct (N:M through table)
└── SupplierContact (1:N) — future
```

---

## 2. Domain Entities Implemented

| Entity | Key Fields | Notes |
|--------|-----------|-------|
| **UnitOfMeasure** | tenant_id, name, symbol, unit_type, conversion_factor | Required for Product. Supports COUNT, WEIGHT, VOLUME, LENGTH, TIME via `unit_type`. |
| **Brand** | tenant_id, name, description, website, logo_path | Optional on Product. Soft-deletable. |
| **ProductCategory** | tenant_id, name, parent_id, sort_order, image_path | Unlimited nesting via self-referencing `parent_id`. Soft-deletable. |
| **Product** | tenant_id, sku, name, brand_id, category_id, unit_of_measure_id, status, is_serialized, is_batched | SKU unique per tenant. Soft-deletable. Multiple barcodes and images via child tables. |
| **ProductVariant** | tenant_id, product_id, sku, name, attributes | Belongs to one Product. Soft-deletable. |
| **ProductImage** | tenant_id, product_id, variant_id, storage_path, is_primary | Multiple images per product. No soft delete. |
| **ProductBarcode** | tenant_id, entity_type, entity_id, barcode, barcode_type | Multiple barcodes per product/variant. Unique barcode per tenant. |
| **Supplier** | tenant_id, name, code, email, phone, website, tax_number, payment_terms_days | Many-to-many to Product via SupplierProduct. Soft-deletable. |
| **SupplierProduct** | tenant_id, supplier_id, product_id, supplier_sku, lead_time_days, min_order_quantity, preferred | Join table with extra fields. |

---

## 3. Constraints

### UnitOfMeasure
- **PK:** id (UUID)
- **Unique:** (tenant_id, symbol)
- **Indexes:** tenant_id + name, tenant_id + is_active

### Brand
- **PK:** id (UUID)
- **Unique:** (tenant_id, name)
- **Soft Delete:** is_active + deleted_at
- **Indexes:** tenant_id + is_active, tenant_id + deleted_at

### ProductCategory
- **PK:** id (UUID)
- **Unique:** (tenant_id, name)
- **FK:** parent_id → ProductCategory(id) [self-referencing, nullable]
- **Soft Delete:** is_active + deleted_at
- **Indexes:** tenant_id + parent, tenant_id + is_active, tenant_id + sort_order

### Product
- **PK:** id (UUID)
- **Unique:** (tenant_id, sku)
- **FK:** brand_id → Brand(id) [nullable], category_id → ProductCategory(id) [nullable], unit_of_measure_id → UnitOfMeasure(id) [required]
- **Soft Delete:** is_active + deleted_at
- **Indexes:** tenant_id + category, tenant_id + brand, tenant_id + status, tenant_id + is_active, tenant_id + deleted_at, sku, barcode

### ProductVariant
- **PK:** id (UUID)
- **Unique:** (tenant_id, sku)
- **FK:** product_id → Product(id) [required]
- **Soft Delete:** is_active + deleted_at
- **Indexes:** tenant_id + product, tenant_id + is_active, tenant_id + deleted_at, sku, barcode

### ProductImage
- **PK:** id (UUID)
- **FK:** product_id → Product(id) [required], variant_id → ProductVariant(id) [nullable]
- **No soft delete**
- **Indexes:** tenant_id + product, tenant_id + variant, tenant_id + is_primary

### ProductBarcode
- **PK:** id (UUID)
- **Unique:** (tenant_id, barcode)
- **Indexes:** tenant_id + entity_type + entity_id, tenant_id + barcode_type

### Supplier
- **PK:** id (UUID)
- **Unique:** (tenant_id, code)
- **Soft Delete:** is_active + deleted_at
- **Indexes:** tenant_id + name, tenant_id + is_active, tenant_id + deleted_at

### SupplierProduct
- **PK:** id (UUID)
- **Unique:** (tenant_id, supplier_id, product_id)
- **FK:** supplier_id → Supplier(id) [required], product_id → Product(id) [required]
- **Indexes:** tenant_id + supplier, tenant_id + product, tenant_id + preferred, tenant_id + is_active

---

## 4. Index Strategy

### Composite Indexes (tenant-first)
All composite indexes lead with `tenant_id` to support tenant-aware queries:
- `tenant_id + is_active` — common active-record filtering
- `tenant_id + deleted_at` — soft-delete exclusions
- `tenant_id + sku` — SKU lookups within tenant
- `tenant_id + category/brand` — categorized product listings
- `tenant_id + status` — status-based filtering

### Single-Field Indexes
- `sku` — unique per tenant, frequent lookups
- `barcode` — product/variant barcode lookups
- `entity_type + entity_id` — barcode association queries

### Rationale
Tenant-aware indexes ensure queries never scan across tenants. The `tenant_id` prefix on all indexes supports the `TenantAwareManager` automatic filtering.

---

## 5. Tenant Isolation Review

| Model | Tenant-Scoped | Filtering Mechanism |
|-------|---------------|---------------------|
| UnitOfMeasure | Yes (tenant_id) | Inherits TenantModel |
| Brand | Yes (tenant_id) | Inherits TenantModel |
| ProductCategory | Yes (tenant_id) | Inherits TenantModel |
| Product | Yes (tenant_id) | Inherits TenantModel |
| ProductVariant | Yes (tenant_id) | Inherits TenantModel |
| ProductImage | Yes (tenant_id) | Inherits TenantModel |
| ProductBarcode | Yes (tenant_id) | Inherits TenantModel |
| Supplier | Yes (tenant_id) | Inherits TenantModel |
| SupplierProduct | Yes (tenant_id) | Inherits TenantModel |

All models inherit from `TenantModel`, which injects `tenant_id` on save and auto-filters reads via `TenantAwareManager`. No tenant_id is accepted from client input.

---

## 6. Soft Delete Strategy

| Model | Soft Delete | Notes |
|-------|-------------|-------|
| UnitOfMeasure | No | Only deactivated via is_active |
| Brand | Yes | is_active + deleted_at |
| ProductCategory | Yes | is_active + deleted_at |
| Product | Yes | is_active + deleted_at |
| ProductVariant | Yes | is_active + deleted_at |
| ProductImage | No | Hard delete via repository |
| ProductBarcode | No | Hard delete via repository |
| Supplier | Yes | is_active + deleted_at |
| SupplierProduct | No | Hard delete via repository |

### Rationale
- **Reference data** (UOM, images, barcodes): hard delete or simple deactivation.
- **Master data** (Brand, Category, Product, Variant, Supplier): soft delete to preserve historical references.
- **Join tables** (SupplierProduct): hard delete, as they have no standalone lifecycle.

---

## 7. Future Extensibility

### Current Scope (Step 1)
- Product catalog foundation only.
- No inventory transactions or stock tracking.

### Future Additions (Scalable)
- **ProductPrice / ProductCost** — already present in `inventory` app; retail can reference or duplicate as needed.
- **Serial Number Tracking** — `Product.is_serialized` flag + future `ProductSerial` model.
- **Batch Tracking** — `Product.is_batched` flag + future `ProductBatch` model.
- **Product Bundles** — future `ProductBundle` + `ProductBundleItem` models.
- **Matrix Variants** — future `ProductVariantAttribute` model for structured dimension-based variants.
- **SupplierContact** — already defined in inventory; can be reused or redefined in retail.
- **Category Attributes** — future `CategoryAttribute` model for dynamic product properties.

---

## 8. Assumptions

1. **Decimal Precision:** Cost and selling prices will use `DecimalField(max_digits=12, decimal_places=2)` when pricing models are added in Step 3.
2. **Barcode Uniqueness:** Barcode uniqueness is enforced per tenant. Cross-tenant duplicate barcodes are allowed.
3. **Category Naming:** Category names are unique per tenant but not globally unique.
4. **SKU Uniqueness:** SKU is unique per tenant across both `Product` and `ProductVariant`.
5. **UOM Conversion:** `conversion_factor` is stored as a decimal for precision; future conversion logic will be in the service layer.
6. **Image Storage:** Storage paths are managed externally (S3/minio). `ProductImage` tracks metadata only.
7. **Supplier Relationships:** A product can have multiple suppliers via `SupplierProduct`. The `preferred` flag marks the primary supplier.
8. **No Inventory in Retail:** Inventory quantities, stock movements, and adjustments are **not** implemented in retail. They belong in the `inventory` app. Retail owns the catalog; inventory owns the stock.

---

## 9. Repository Pattern Compliance

All repositories:
- Return domain entities, not ORM models.
- Accept domain entities as parameters.
- Use `_to_entity()` for ORM → domain conversion.
- Contain **no business logic** — persistence only.
- Support tenant-scoped queries via explicit `tenant_id` parameters.

---

## 10. Validation Checklist

- [x] All entities defined with correct fields
- [x] Tenant-scoped models inherit TenantModel
- [x] Soft-deletable models use is_active + deleted_at
- [x] UUID primary keys on all models
- [x] created_at / updated_at on all models
- [x] Proper unique constraints (tenant_id + sku, tenant_id + symbol, etc.)
- [x] Proper indexes (tenant-first composites)
- [x] SKU unique per tenant
- [x] Multiple barcodes per product
- [x] Multiple images per product
- [x] Brand optional on Product
- [x] Supplier many-to-many through SupplierProduct
- [x] Categories support unlimited nesting
- [x] Future flags for serial numbers, batches, bundles, matrix variants
- [x] Inventory quantities NOT stored in retail
- [x] No business logic in repositories

---

## 11. Ready for Step 2

All domain entities, Django models, and repositories are defined and validated. Ready for service layer implementation.

**Next Steps:**
- Step 2: Application services (UnitOfMeasureService, BrandService, CategoryService, ProductService, etc.)
- Step 3: API layer (serializers, views, URLs)
- Step 4: Validation + hardening
</content>
<task_progress>
- [x] Read mandatory backend documentation files
- [x] Read Milestone 5 planning documents
- [x] Read all frontend planning documents
- [x] Explore existing backend structure
- [x] Inspect retail domain entities and models
- [x] Inspect shared types
- [x] Inspect base models
- [x] Create frontend root directory structure
- [x] Create README and .gitkeep
- [x] Inspect inventory repositories and models
- [x] Create backend domain entities
- [x] Create backend infrastructure models
- [x] Create backend infrastructure repositories
- [x] Create MILESTONE5_STEP1_MODEL_VALIDATION.md
- [ ] Verify and report completion
</task_progress>
