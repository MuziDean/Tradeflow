# Retail Module — Architecture Validation Report

**Date:** 2026-07-20
**Module:** Retail — Product Catalog
**Status:** Review Complete → Hardening Required

---

## 1. Overall Scores

| Category | Score | Description |
|----------|-------|-------------|
| **Architecture Score** | **7.0/10** | Good structure with notable gaps in repository completeness |
| **Security Score** | **7.5/10** | Tenant isolation and RBAC present, but missing event emission in several services |
| **Maintainability Score** | **7.0/10** | Good separation of concerns, but missing repository methods cause fragility |
| **Production Readiness** | **6.5/10** | Requires hardening before production deployment |

---

## 2. Clean Architecture Compliance

### ✅ What's Correct

- **Domain layer** (`domain/entities.py`): Pure Python dataclasses, no framework dependencies.
- **Application layer** (`application/`): Services depend only on repositories and domain entities. One service per file.
- **Infrastructure layer** (`infrastructure/`): Models are Django ORM; repositories convert ORM ↔ domain entities.
- **API layer** (`api/`): Views are thin — authenticate, validate, call service, return response.
- **No business logic in repositories** — all repositories are persistence-only.
- **No business logic in serializers** — serializers validate/format only.
- **No ORM queries in services** — all data access through repositories.

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| Missing repository methods (SupplierProduct) | HIGH | No `get_by_id()`, `update()`, or `delete()` — services call non-existent methods |
| Missing repository methods (ProductBarcode) | HIGH | No `delete()` method — service calls non-existent method |
| Missing repository methods (ProductImage) | MEDIUM | No `update()` method — `set_primary()` cannot update `is_primary` on existing images |
| ProductImageService.set_primary() deletes images | CRITICAL | Line 41 calls `delete()` instead of `update()` — destroys previous primary image |
| SupplierProductService.set_preferred() calls non-existent `get_by_id()` | HIGH | Line 44 calls `self.supplier_product_repository.get_by_id()` — doesn't exist |
| Vendor entities (Sale/SaleItem) in domain | LOW | Dead code — no tables, repositories, services, or endpoints for them |
| Category service: no flat-list fetch | LOW | `list_for_tenant(parent_id=None)` only returns root categories, not all |

---

## 3. Tenant Isolation

### ✅ What's Correct

- All repositories filter by `tenant_id` on every query.
- All models inherit from `TenantModel`.
- All nested resources (variants, images, barcodes, supplier products) verify ownership through parent's `tenant_id`.
- No cross-tenant access paths identified.

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| None | — | Tenant isolation is properly enforced across all layers |

---

## 4. RBAC

### ✅ What's Correct

- Every endpoint declares `required_permission` via `HasPermission` class.
- All endpoints require `IsAuthenticated`.
- Permission names follow `retail.{resource}.{action}` pattern.
- Write, update, delete actions each have distinct permissions.

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| Typo in permission name | MEDIUM | `ProductVariantListCreateView` uses `"retal.products.read"` — missing 'i' |
| Missing `required_permission` on `UnitOfMeasureDetailView.destroy` | MEDIUM | Delete action could bypass permission |
| Variant create permission inconsistency | LOW | Uses `"retail.products.create"` instead of `"retail.products.update"` as in Platform branch pattern |

---

## 5. API Consistency

### ✅ What's Correct

- All responses use `{"data": ...}` envelope.
- All errors use `{"success": false, "error": {"code": ..., "message": ...}}`.
- All list endpoints paginated via `StandardPagination`.
- Search, ordering, filtering configured on all list endpoints.
- UUID primary keys throughout.
- HTTP methods match semantic actions.
- Versioned under `/api/v1/retail/`.

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| Unused imports (views.py) | LOW | `extend_schema` imported and unused; `CategorySerializer` and `CategoryListSerializer` aliases mismatch |
| Error response format inconsistency | LOW | Some views use `_error_response()`, others let DRF raise exceptions directly |

---

## 6. Security Review

### ✅ What's Correct

- Authentication required on all endpoints.
- RBAC enforced via `HasPermission`.
- Soft delete respected (Brand, Category, Product, Variant, Supplier).
- Hard delete via repository only (Image, Barcode, SupplierProduct).
- Input validation on all writes via `serializer.is_valid(raise_exception=True)`.
- No stack traces exposed — errors wrapped in standard envelope.

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| Soft delete not implemented for SupplierProduct repository | MEDIUM | Service calls `delete()` which doesn't exist |

---

## 7. Repository Review

### ✅ What's Correct

- All repositories convert ORM → domain entities via `_to_entity()`.
- Business logic is absent from repositories.
- `list_for_tenant()` methods include active-only filtering.
- `get_by_id()` methods return domain entities or `None`.
- Basic CRUD operations follow consistent patterns.

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| `SupplierProductRepository` missing: `get_by_id()`, `update()`, `delete()` | CRITICAL | Services depend on these but they don't exist |
| `ProductBarcodeRepository` missing: `delete()`, `get_for_entity()` | HIGH | Service calls non-existent `delete()` — `remove_barcode()` will fail at runtime |
| `ProductImageRepository` missing: `update()` | MEDIUM | `set_primary()` needs to set `is_primary=False` on old primary without deleting it |
| `ProductBarcodeRepository` no `get_for_entity()` | LOW | Cannot list barcodes for a specific entity |

---

## 8. Services Review

### ✅ What's Correct

- All services use `transaction.atomic()` for write operations.
- Constructor injection for repository dependencies.
- Logging present on all write operations.
- Domain events emitted after successful commits.
- Business rules enforced (e.g., archive blocked if child categories exist).

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| Missing events on UnitOfMeasureService | MEDIUM | `create/update/soft_delete` — no domain events emitted (Platform pattern would emit them) |
| `ProductService.get_by_barcode()` is O(n) | MEDIUM | Loads all products into memory instead of querying by barcode |
| Unused import in `supplier_product_service.py` | LOW | `SupplierUpdated` imported but never used |
| `set_primary()` deletes previous primary image | CRITICAL | Should unset `is_primary` on old primary, not hard-delete it |

---

## 9. Events Review

### ✅ What's Correct

- All events inherit from `DomainEvent` base class.
- Events are emitted only from services.
- Event naming follows `{Entity}{Action}` pattern.
- Events carry tenant_id for cross-tenant event routing.
- Event emission happens after successful transaction commit.

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| Missing events: UnitOfMeasure | MEDIUM | No `UnitOfMeasureCreated`, `UnitOfMeasureUpdated`, `UnitOfMeasureDeleted` events defined or emitted |
| Missing events: ProductImage updates | LOW | `set_primary()` emits event but should also emit for image updates |
| `PreferredSupplierChanged` aggregate_type wrong | LOW | Uses `"SupplierProduct"` instead of more specific type |

---

## 10. Code Quality Review

### ✅ What's Correct

- Type hints present on all function signatures.
- Module-level loggers with consistent naming.
- Docstrings on all classes and methods.
- One class per file in application layer.
- Consistent formatting (imports sorted, etc.).

### ❌ What's Wrong

| Issue | Severity | Details |
|-------|----------|---------|
| Dead code: Sale, SaleItem entities | LOW | Domain entities with no corresponding tables, repos, services, or endpoints |
| Unused import: `SupplierUpdated` in supplier_product_service.py | LOW | Imported but never used |
| Unused import: `extend_schema` in views.py | LOW | Imported but never used |
| Serializer import aliases misnamed in views.py | LOW | `CategorySerializer` ≠ `ProductCategorySerializer` |
| Inconsistent method naming: `soft_delete` vs `delete` vs `archive` | LOW | Some services call it `archive()`, some call `soft_delete()`, some call `delete()` |
| `get_by_barcode` in ProductService is Python iteration | MEDIUM | Inefficient — should use repository barcode lookup |

---

## 11. Technical Debt Summary

| # | Item | Severity | Effort to Fix | Impact if Not Fixed |
|---|------|----------|---------------|---------------------|
| 1 | ProductImageService.set_primary() hard-deletes old primary | CRITICAL | 15 min | Data loss during image primary change |
| 2 | SupplierProductRepository missing 3 methods | HIGH | 30 min | `set_preferred()` and `remove_link()` crash at runtime |
| 3 | ProductBarcodeRepository missing `delete()` | HIGH | 15 min | `remove_barcode()` crashes at runtime |
| 4 | Typo `"retal.products.read"` → `"retail.products.read"` | MEDIUM | 2 min | Users with correct permission get denied |
| 5 | Missing events on UnitOfMeasureService | MEDIUM | 15 min | No audit trail for UOM changes |
| 6 | ProductService.get_by_barcode() O(n) | MEDIUM | 10 min | Performance degrades with product count |
| 7 | Dead Sale/SaleItem entities | LOW | 5 min | Minor confusion |
| 8 | Unused imports | LOW | 5 min | Linting noise |

---

## 12. Strengths

1. **Solid architecture foundation** — Clean Architecture + DDD properly followed.
2. **Tenant isolation** — Correctly enforced at all layers.
3. **RBAC integration** — Every endpoint protected with explicit permissions.
4. **Service decomposition** — One service per file improves maintainability.
5. **Event-driven design** — Domain events emitted from services.
6. **Repository pattern** — Clean ORM/domain conversion with no business logic leakage.
7. **API consistency** — Standard envelopes, pagination, search, filtering.
8. **Soft delete** — Preserved for master data entities.

---

## 13. Weaknesses

1. **Repository completeness** — Several repositories missing essential CRUD methods that services depend on. This will cause runtime crashes.
2. **Critical bug in `set_primary()`** — Hard-deletes previous primary image instead of unsetting it. Data loss risk.
3. **Missing events** — UnitOfMeasure operations lack event emission.
4. **Inefficient barcode lookup** — Python iteration instead of database query.
5. **Typo in permission name** — Single-character error causes incorrect authorization.

---

## 14. Recommendations

### Immediate (Pre-Production)
1. Fix `set_primary()` to unset `is_primary` on old primary image (not delete)
2. Add missing repository methods to `SupplierProductRepository` and `ProductBarcodeRepository`
3. Fix `"retal.products.read"` typo → `"retail.products.read"`
4. Add events to `UnitOfMeasureService`
5. Optimize `ProductService.get_by_barcode()` to use repository query

### Short Term
6. Remove dead Sale/SaleItem entities
7. Clean up unused imports
8. Fix import aliases in `views.py`
9. Add `barcode_repository.get_for_entity()` method

### Medium Term
10. Add flat-list category fetch method
11. Standardize service method names (`archive` vs `soft_delete`)
12. Consider adding event emission for all entity lifecycle operations

---

## 15. Verification Required Before Hardening

- [x] Repository structure reviewed — **FAIL** (missing methods)
- [x] Service logic reviewed — **FAIL** (set_primary bug, missing events)
- [x] API permissions reviewed — **FAIL** (typo in permission name)
- [x] Event emission reviewed — **FAIL** (UnitOfMeasure missing)
- [x] Import cleanliness reviewed — **FAIL** (unused imports)
- [x] Dead code detected — **INFO** (Sale/SaleItem entities)

---

**Last Updated:** 2026-07-20
**Reviewed By:** Architecture validation analysis