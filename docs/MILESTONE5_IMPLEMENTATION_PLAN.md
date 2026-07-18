# TradeFlow — Milestone 5 Implementation Plan

**Milestone:** Product & Inventory Foundation
**Status:** Planning — Awaiting Approval
**Date:** 2026-07-18

---

## Overview

Milestone 5 establishes the **product catalog**, **inventory management**, and **pricing** foundation for TradeFlow. It builds on the multi-tenant platform and RBAC foundation from Milestones 1-4.

---

## Step 1: Units of Measure, Brands, Categories

### Domain Entities

**UnitOfMeasure**
- `id` (str, UUID)
- `tenant_id` (str)
- `name` (str) — e.g., "Each", "Kilogram", "Liter"
- `symbol` (str) — e.g., "ea", "kg", "L"
- `unit_type` (enum) — COUNT, WEIGHT, VOLUME, LENGTH, TIME
- `conversion_factor` (float, optional) — base unit conversion
- `is_active` (bool)

**Brand**
- `id` (str, UUID)
- `tenant_id` (str)
- `name` (str)
- `description` (str, optional)
- `website` (str, optional)
- `logo_path` (str, optional)
- `is_active` (bool)

**Category**
- `id` (str, UUID)
- `tenant_id` (str)
- `name` (str)
- `description` (str, optional)
- `parent_id` (str, nullable) — self-join for hierarchy
- `image_path` (str, optional)
- `sort_order` (int)
- `is_active` (bool)

### Django Models

- `UnitOfMeasureModel` — `unit_type` CharField with choices
- `BrandModel` — standard fields
- `CategoryModel` — parent FK to self, `parent_id`

### Repositories

- `UnitOfMeasureRepository`
  - `list_for_tenant(tenant_id, active_only=True)`
  - `get_by_id(uom_id, tenant_id)`
  - `get_by_symbol(symbol, tenant_id)`
  - `create(uom)`
  - `update(uom)`
  - `soft_delete(uom_id, tenant_id)`

- `BrandRepository`
  - `list_for_tenant(tenant_id, active_only=True)`
  - `get_by_id(brand_id, tenant_id)`
  - `create(brand)`
  - `update(brand)`

- `CategoryRepository`
  - `list_for_tenant(tenant_id, parent_id=None)` — flat by level
  - `get_by_id(category_id, tenant_id)`
  - `list_tree(tenant_id)` — hierarchical
  - `create(category)`
  - `update(category)`
  - `soft_delete(category_id, tenant_id)`

### Services

- `UnitOfMeasureService`
- `BrandService`
- `CategoryService`

Each service delegates to repository. No cross-service calls for this step.

### Validators

- `UnitOfMeasureValidator`
  - `name` required, unique per tenant
  - `symbol` required, unique per tenant
  - `unit_type` must be valid enum

- `BrandValidator`
  - `name` required, unique per tenant

- `CategoryValidator`
  - `name` required
  - `parent_id` must belong to same tenant
  - Prevent circular parent references

### Events

- `UnitOfMeasureCreated`, `UnitOfMeasureUpdated`, `UnitOfMeasureDeleted`
- `BrandCreated`, `BrandUpdated`, `BrandDeleted`
- `CategoryCreated`, `CategoryUpdated`, `CategoryDeleted`

### API Endpoints

| Method | Path | Permission |
|--------|------|------------|
| GET | `/inventory/uoms/` | `inventory.uoms.read` |
| POST | `/inventory/uoms/` | `inventory.uoms.create` |
| GET | `/inventory/uoms/{id}/` | `inventory.uoms.read` |
| PUT | `/inventory/uoms/{id}/` | `inventory.uoms.edit` |
| DELETE | `/inventory/uoms/{id}/` | `inventory.uoms.delete` |
| GET | `/inventory/brands/` | `inventory.brands.read` |
| POST | `/inventory/brands/` | `inventory.brands.create` |
| GET | `/inventory/brands/{id}/` | `inventory.brands.read` |
| PUT | `/inventory/brands/{id}/` | `inventory.brands.edit` |
| DELETE | `/inventory/brands/{id}/` | `inventory.brands.delete` |
| GET | `/inventory/categories/` | `inventory.categories.read` |
| POST | `/inventory/categories/` | `inventory.categories.create` |
| GET | `/inventory/categories/{id}/` | `inventory.categories.read` |
| PUT | `/inventory/categories/{id}/` | `inventory.categories.edit` |
| DELETE | `/inventory/categories/{id}/` | `inventory.categories.delete` |

---

## Step 2: Products, Product Variants, Product Images, Barcodes

### Domain Entities

**Product**
- `id` (str, UUID)
- `tenant_id` (str)
- `sku` (str) — stock-keeping unit, unique per tenant
- `name` (str)
- `description` (str, optional)
- `brand_id` (str, nullable)
- `category_id` (str, nullable)
- `unit_of_measure_id` (str)
- `barcode` (str, nullable)
- `status` (enum) — DRAFT, ACTIVE, DISCONTINUED, ARCHIVED
- `is_trackable` (bool) — track inventory
- `is_serialized` (bool) — unique serial numbers
- `is_batched` (bool) — batch tracking
- `attributes` (JSON) — extensible key-value
- `created_at`, `updated_at`

**ProductVariant**
- `id` (str, UUID)
- `tenant_id` (str)
- `product_id` (str)
- `sku` (str) — e.g., "PROD-001-RED-M"
- `name` (str) — e.g., "Red - Medium"
- `barcode` (str, nullable)
- `attributes` (JSON) — e.g., {"color": "red", "size": "M"}
- `is_active` (bool)

**ProductImage**
- `id` (str, UUID)
- `tenant_id` (str)
- `product_id` (str)
- `variant_id` (str, nullable)
- `storage_provider` (str)
- `storage_path` (str)
- `original_filename` (str)
- `mime_type` (str)
- `file_size` (int)
- `sort_order` (int)
- `is_primary` (bool)
- `created_at`

**Barcode**
- `id` (str, UUID)
- `tenant_id` (str)
- `entity_type` (str) — "product", "variant", "batch"
- `entity_id` (str)
- `barcode` (str) — EAN-13, UPC-A, Code128, QR
- `barcode_type` (enum) — EAN13, UPC_A, CODE128, QR
- `created_at`

### Repositories

- `ProductRepository`
  - `list_for_tenant(tenant_id, category_id, brand_id, status, search)`
  - `get_by_id(product_id, tenant_id)`
  - `get_by_sku(sku, tenant_id)`
  - `get_by_barcode(barcode, tenant_id)`
  - `create(product)`
  - `update(product)`
  - `soft_delete(product_id, tenant_id)`

- `ProductVariantRepository`
  - `list_for_product(tenant_id, product_id)`
  - `get_by_id(variant_id, tenant_id)`
  - `get_by_sku(sku, tenant_id)`
  - `create(variant)`
  - `update(variant)`
  - `soft_delete(variant_id, tenant_id)`

- `ProductImageRepository`
  - `list_for_product(tenant_id, product_id, variant_id=None)`
  - `get_primary(tenant_id, product_id)`
  - `create(image)`
  - `update(image)`
  - `delete(image_id, tenant_id)`

- `BarcodeRepository`
  - `get_by_barcode(barcode, tenant_id)`
  - `get_for_entity(tenant_id, entity_type, entity_id)`
  - `create(barcode)`
  - `bulk_create(barcodes)`

### Services

- `ProductService`
  - `list_products(tenant_id, filters)`
  - `get_product(product_id, tenant_id)`
  - `get_product_by_sku(sku, tenant_id)`
  - `create_product(product, variant_data_list, image_data_list)`
  - `update_product(product_id, tenant_id, updates)`
  - `add_variant(product_id, tenant_id, variant)`
  - `archive_product(product_id, tenant_id)`

- `BarcodeService`
  - `lookup(barcode, tenant_id)` — find product/variant by barcode
  - `generate_for_product(product_id, tenant_id)`

### Validators

- `ProductValidator`
  - `sku` required, unique per tenant
  - `name` required
  - `unit_of_measure_id` required, must exist
  - `brand_id` must exist if provided
  - `category_id` must exist if provided

- `ProductVariantValidator`
  - `sku` required, unique per tenant
  - `product_id` required

### Events

- `ProductCreated`, `ProductUpdated`, `ProductArchived`
- `ProductVariantCreated`, `ProductVariantUpdated`
- `ProductImageUploaded`

### API Endpoints

| Method | Path | Permission |
|--------|------|------------|
| GET | `/inventory/products/` | `inventory.products.read` |
| POST | `/inventory/products/` | `inventory.products.create` |
| GET | `/inventory/products/{id}/` | `inventory.products.read` |
| PUT | `/inventory/products/{id}/` | `inventory.products.edit` |
| DELETE | `/inventory/products/{id}/` | `inventory.products.delete` |
| POST | `/inventory/products/{id}/variants/` | `inventory.products.edit` |
| GET | `/inventory/products/{id}/images/` | `inventory.products.read` |
| POST | `/inventory/products/{id}/images/` | `inventory.products.edit` |
| DELETE | `/inventory/images/{id}/` | `inventory.products.edit` |
| GET | `/inventory/barcodes/lookup/` | `inventory.barcodes.read` |

---

## Step 3: Price Lists, Product Pricing, Tax Mapping

### Domain Entities

**PriceList**
- `id` (str, UUID)
- `tenant_id` (str)
- `name` (str)
- `description` (str, optional)
- `currency_code` (str) — default ZAR
- `is_default` (bool)
- `is_active` (bool)
- `effective_from` (datetime)
- `effective_to` (datetime, nullable)
- `created_at`, `updated_at`

**ProductPrice**
- `id` (str, UUID)
- `tenant_id` (str)
- `price_list_id` (str)
- `product_id` (str)
- `variant_id` (str, nullable)
- `price` (Decimal)
- `cost` (Decimal, optional)
- `created_at`, `updated_at`

**TaxMapping**
- `id` (str, UUID)
- `tenant_id` (str)
- `product_id` (str)
- `variant_id` (str, nullable)
- `tax_config_id` (str)
- `is_default` (bool)
- `created_at`, `updated_at`

### Repositories

- `PriceListRepository`
  - `list_for_tenant(tenant_id, active_only=True)`
  - `get_default(tenant_id)`
  - `get_by_id(price_list_id, tenant_id)`
  - `create(price_list)`
  - `update(price_list)`
  - `archive(price_list_id, tenant_id)`

- `ProductPriceRepository`
  - `list_for_price_list(tenant_id, price_list_id)`
  - `get_for_product(tenant_id, price_list_id, product_id, variant_id=None)`
  - `bulk_update(tenant_id, price_list_id, prices)`
  - `create(product_price)`

- `TaxMappingRepository`
  - `list_for_product(tenant_id, product_id)`
  - `get_default_for_product(tenant_id, product_id)`
  - `create(tax_mapping)`
  - `update(tax_mapping)`

### Services

- `PricingService`
  - `get_product_price(tenant_id, product_id, variant_id, price_list_id=None)`
  - `set_product_price(price_list_id, product_id, variant_id, price, cost)`
  - `bulk_set_prices(price_list_id, prices)`
  - `get_default_price_list(tenant_id)`
  - `set_default_price_list(tenant_id, price_list_id)`

- `TaxMappingService`
  - `get_tax_for_product(tenant_id, product_id, variant_id)`
  - `set_tax_mapping(tenant_id, product_id, variant_id, tax_config_id)`
  - `remove_tax_mapping(tenant_id, product_id, variant_id)`

### Validators

- `PriceListValidator`
  - `name` required, unique per tenant
  - `effective_from` required
  - `effective_to` must be after `effective_from`

- `ProductPriceValidator`
  - `price_list_id` required
  - `product_id` required
  - `price` >= 0

### Events

- `PriceListCreated`, `PriceListUpdated`, `PriceListArchived`
- `ProductPriceUpdated`, `BulkPricesUpdated`
- `TaxMappingCreated`, `TaxMappingUpdated`

### API Endpoints

| Method | Path | Permission |
|--------|------|------------|
| GET | `/inventory/price-lists/` | `inventory.pricing.read` |
| POST | `/inventory/price-lists/` | `inventory.pricing.create` |
| GET | `/inventory/price-lists/{id}/` | `inventory.pricing.read` |
| PUT | `/inventory/price-lists/{id}/` | `inventory.pricing.edit` |
| DELETE | `/inventory/price-lists/{id}/` | `inventory.pricing.delete` |
| GET | `/inventory/price-lists/{id}/prices/` | `inventory.pricing.read` |
| POST | `/inventory/price-lists/{id}/prices/` | `inventory.pricing.edit` |
| POST | `/inventory/price-lists/{id}/prices/bulk/` | `inventory.pricing.edit` |
| GET | `/inventory/products/{id}/prices/` | `inventory.pricing.read` |
| GET | `/inventory/products/{id}/tax-mapping/` | `inventory.pricing.read` |
| POST | `/inventory/products/{id}/tax-mapping/` | `inventory.pricing.edit` |

---

## Step 4: Inventory Items, Warehouse Stock, Stock Movements, Stock Adjustments

### Domain Entities

**InventoryItem**
- `id` (str, UUID)
- `tenant_id` (str)
- `product_id` (str)
- `variant_id` (str, nullable)
- `warehouse_id` (str)
- `quantity_on_hand` (Decimal)
- `quantity_reserved` (Decimal)
- `quantity_available` (Decimal) — computed: on_hand - reserved
- `reorder_point` (Decimal, optional)
- `reorder_quantity` (Decimal, optional)
- `last_stocked_at` (datetime, nullable)
- `created_at`, `updated_at`

**StockMovement**
- `id` (str, UUID)
- `tenant_id` (str)
- `inventory_item_id` (str)
- `warehouse_id` (str)
- `movement_type` (enum) — RECEIPT, ISSUE, TRANSFER, ADJUSTMENT, RETURN
- `quantity` (Decimal) — positive or negative
- `reason` (str, optional)
- `reference_type` (str, optional) — "purchase_order", "sales_order", "stock_take"
- `reference_id` (str, optional)
- `performed_by` (str) — user ID
- `performed_at` (datetime)
- `created_at`

**StockAdjustment**
- `id` (str, UUID)
- `tenant_id` (str)
- `inventory_item_id` (str)
- `warehouse_id` (str)
- `adjustment_type` (enum) — CORRECTION, DAMAGE, LOSS, FOUND
- `quantity_before` (Decimal)
- `quantity_after` (Decimal)
- `quantity_delta` (Decimal)
- `reason` (str)
- `performed_by` (str)
- `approved_by` (str, nullable)
- `performed_at` (datetime)

### Repositories

- `InventoryItemRepository`
  - `get_by_id(item_id, tenant_id)`
  - `get_by_product(tenant_id, product_id, variant_id, warehouse_id)`
  - `list_for_warehouse(tenant_id, warehouse_id, product_id, low_stock_only)`
  - `create(item)`
  - `update(item)`
  - `adjust_quantity(item_id, tenant_id, delta)` — atomic

- `StockMovementRepository`
  - `list_for_item(tenant_id, inventory_item_id, movement_type, date_from, date_to)`
  - `list_for_warehouse(tenant_id, warehouse_id, movement_type, date_from, date_to)`
  - `create(movement)`
  - `bulk_create(movements)`

- `StockAdjustmentRepository`
  - `list_for_item(tenant_id, inventory_item_id)`
  - `list_for_warehouse(tenant_id, warehouse_id)`
  - `create(adjustment)`

### Services

- `InventoryService`
  - `get_item(tenant_id, product_id, variant_id, warehouse_id)`
  - `create_item(tenant_id, product_id, variant_id, warehouse_id, initial_quantity)`
  - `adjust_quantity(item_id, tenant_id, delta, reason, reference)`
  - `transfer_item(item_id, from_warehouse_id, to_warehouse_id, quantity)`
  - `list_low_stock(tenant_id, warehouse_id)`

- `StockMovementService`
  - `record_receipt(tenant_id, inventory_item_id, quantity, reference, performed_by)`
  - `record_issue(tenant_id, inventory_item_id, quantity, reason, reference, performed_by)`
  - `record_transfer(tenant_id, from_item_id, to_item_id, quantity, reason, performed_by)`
  - `list_movements(tenant_id, filters)`

- `StockAdjustmentService`
  - `create_adjustment(tenant_id, item_id, adjustment_type, delta, reason, performed_by, approved_by)`
  - `list_adjustments(tenant_id, filters)`

### Validators

- `InventoryItemValidator`
  - `product_id` required
  - `warehouse_id` required
  - `quantity_on_hand` >= 0

- `StockMovementValidator`
  - `movement_type` required
  - `quantity` != 0
  - `warehouse_id` required

- `StockAdjustmentValidator`
  - `adjustment_type` required
  - `reason` required
  - For DAMAGE/LOSS: `quantity_delta` < 0
  - For FOUND/CORRECTION: `quantity_delta` can be positive or negative
  - `approved_by` required for large adjustments (> threshold)

### Events

- `InventoryItemCreated`, `InventoryItemUpdated`
- `StockMovementRecorded`
- `StockAdjustmentCreated`

### API Endpoints

| Method | Path | Permission |
|--------|------|------------|
| GET | `/inventory/items/` | `inventory.items.read` |
| POST | `/inventory/items/` | `inventory.items.create` |
| GET | `/inventory/items/{id}/` | `inventory.items.read` |
| PUT | `/inventory/items/{id}/` | `inventory.items.edit` |
| DELETE | `/inventory/items/{id}/` | `inventory.items.delete` |
| POST | `/inventory/items/transfer/` | `inventory.items.transfer` |
| GET | `/inventory/items/low-stock/` | `inventory.items.read` |
| GET | `/inventory/stock-movements/` | `inventory.movements.read` |
| POST | `/inventory/stock-movements/` | `inventory.movements.create` |
| GET | `/inventory/stock-adjustments/` | `inventory.adjustments.read` |
| POST | `/inventory/stock-adjustments/` | `inventory.adjustments.create` |

---

## Step 5: API Layer, Validation, Documentation, Hardening

### Serializers

For each domain entity, create:
- `ListSerializer` — minimal fields for list views
- `DetailSerializer` — full fields for detail views
- `CreateSerializer` — write-only fields for POST
- `UpdateSerializer` — write-only fields for PUT/PATCH

Special serializers:
- `ProductListSerializer` — includes brand name, category name, primary image
- `ProductDetailSerializer` — includes variants, images, barcodes, current price, tax
- `InventoryItemListSerializer` — includes product name, SKU, warehouse name

### Views

- Use generic views (`ListAPIView`, `CreateAPIView`, `RetrieveAPIView`, `UpdateAPIView`, `DestroyAPIView`)
- Add filtering: `category_id`, `brand_id`, `status`, `warehouse_id`, `product_id`
- Add search: `name`, `sku`, `barcode`
- Add ordering: `name`, `created_at`, `updated_at`
- All views declare `required_permission`

### URLs

- Add all endpoints to `apps/inventory/api/urls.py`
- Register in `config/api_urls.py`

### OpenAPI Documentation

- drf-spectacular auto-generates schema
- Add `@extend_schema` decorators for custom request/response examples
- Ensure all endpoints have descriptions

### Validation Documentation

- `docs/STEP5_VALIDATION.md`

### Hardening

- Audit all services for logging coverage
- Remove dead code
- Ensure consistent error envelopes
- Verify RBAC enforcement
- Verify tenant isolation
- Cross-tenant security tests

---

## Implementation Order

### Day 1-2: Step 1
- Models, repositories, services for UOM, Brand, Category
- Basic CRUD endpoints

### Day 3-5: Step 2
- Product and Variant entities
- Product service with variant creation
- Image upload via presigned URLs
- Barcode lookup endpoint

### Day 6-7: Step 3
- PriceList and ProductPrice entities
- Pricing service with bulk operations
- TaxMapping service
- Price list management endpoints

### Day 8-10: Step 4
- InventoryItem, StockMovement, StockAdjustment
- Stock adjustment service with approval flow
- Movement tracking endpoints
- Low stock alerts endpoint

### Day 11-12: Step 5
- API layer polish (filters, search, ordering)
- Validation report
- Hardening pass

---

## Dependencies

### Backend

- Django 4.2+
- Django REST Framework
- drf-spectacular
- Existing tenants from Milestone 1
- Existing RBAC from Milestone 3
- Existing platform from Milestone 4

### Frontend (Future)

- Price list management UI
- Product catalog UI with search/filter
- Product detail with variants/images
- Inventory dashboard with low-stock alerts
- Stock movement history table

---

## Success Criteria

- All 5 steps deliver working API endpoints
- Tenant isolation verified for all queries
- RBAC permissions enforced on all endpoints
- All write operations emit domain events
- OpenAPI schema documented and accessible
- No N+1 queries (use select_related/prefetch_related)
- All endpoints return standard envelope `{ data }` or `{ success, error }`

---

**Last Updated:** 2026-07-18