# Milestone 7 — Step 1: Purchasing & Procurement Domain Foundation

**Module:** Purchasing
**Date:** 2026-07-20
**Status:** Complete ✅

---

## 1. Files Created

| File | Purpose |
|------|---------|
| `backend/apps/purchasing/domain/entities.py` | 11 domain entities |
| `backend/apps/purchasing/infrastructure/models.py` | 11 Django ORM models |
| `backend/apps/purchasing/infrastructure/repositories.py` | 11 repositories |
| `backend/docs/MILESTONE7_STEP1_MODEL_VALIDATION.md` | This validation report |

---

## 2. Files Modified

| File | Change |
|------|--------|
| `backend/shared/types/enums.py` | Added 7 purchasing enums |

---

## 3. Entity List

| # | Entity | Type | Key Fields |
|---|--------|------|------------|
| 1 | **PurchaseRequisition** | Header | warehouse, requested_by, status, total_estimated_amount |
| 2 | **PurchaseRequisitionLine** | Line | product, variant, quantity, estimated_unit_price |
| 3 | **SupplierQuotation** | Header | supplier, warehouse, status, total_amount, expiry_date |
| 4 | **SupplierQuotationLine** | Line | product, variant, quantity, unit_price, lead_time_days |
| 5 | **PurchaseOrder** | Header | supplier, warehouse, order_type, status, grand_total |
| 6 | **PurchaseOrderLine** | Line | product, variant, quantity_ordered, unit_price, tax_rate |
| 7 | **GoodsReceipt** | Header | purchase_order, warehouse, status, posted_by |
| 8 | **GoodsReceiptLine** | Line | product, variant, quantity_received, unit_cost, batch_number |
| 9 | **PurchaseReturn** | Header | purchase_order, goods_receipt, supplier, status, total_amount |
| 10 | **PurchaseReturnLine** | Line | product, variant, quantity_returned, unit_cost, return_reason |
| 11 | **SupplierPriceList** | Standalone | supplier, product, price, valid_from, valid_to, is_active |

**Total:** 11 entities (5 headers + 5 lines + 1 standalone)

---

## 4. Repository List

| # | Repository | Entity | Key Methods |
|---|------------|--------|-------------|
| 1 | **PurchaseRequisitionRepository** | PurchaseRequisition | get_by_id, list_for_tenant, create, update, soft_delete |
| 2 | **PurchaseRequisitionLineRepository** | PurchaseRequisitionLine | create, list_for_requisition |
| 3 | **SupplierQuotationRepository** | SupplierQuotation | get_by_id, list_for_tenant, create, update, soft_delete |
| 4 | **SupplierQuotationLineRepository** | SupplierQuotationLine | create, list_for_quotation |
| 5 | **PurchaseOrderRepository** | PurchaseOrder | get_by_id, list_for_tenant, create, update, soft_delete |
| 6 | **PurchaseOrderLineRepository** | PurchaseOrderLine | create, list_for_order |
| 7 | **GoodsReceiptRepository** | GoodsReceipt | get_by_id, list_for_tenant, create, update, soft_delete |
| 8 | **GoodsReceiptLineRepository** | GoodsReceiptLine | create, list_for_receipt |
| 9 | **PurchaseReturnRepository** | PurchaseReturn | get_by_id, list_for_tenant, create, update, soft_delete |
| 10 | **PurchaseReturnLineRepository** | PurchaseReturnLine | create, list_for_return |
| 11 | **SupplierPriceListRepository** | SupplierPriceList | get_by_id, get_active_for_supplier_product, list_for_tenant, create, update, soft_delete |

**Total:** 11 repositories

---

## 5. Enum List

| # | Enum | Values |
|---|------|--------|
| 1 | **PurchaseRequisitionStatus** | draft, pending_approval, approved, rejected, converted, cancelled |
| 2 | **QuotationStatus** | draft, sent, accepted, rejected, expired |
| 3 | **PurchaseOrderStatus** | draft, pending_approval, approved, sent, acknowledged, partially_received, received, invoiced, closed, cancelled |
| 4 | **PurchaseOrderType** | standard, blanket, consignment, drop_ship |
| 5 | **GoodsReceiptStatus** | draft, posted, cancelled |
| 6 | **PurchaseReturnStatus** | draft, pending_approval, approved, shipped, received, credited, cancelled |
| 7 | **ApprovalStatus** | pending, approved, rejected, withdrawn |

**Total:** 7 enums

---

## 6. Architecture Decisions

### 6.1 Entity Relationships
```
PurchaseRequisition (header)
  └─ PurchaseRequisitionLine (lines)

SupplierQuotation (header)
  └─ SupplierQuotationLine (lines)

PurchaseOrder (header)
  └─ PurchaseOrderLine (lines)

GoodsReceipt (header)
  └─ GoodsReceiptLine (lines)
      └─ references PurchaseOrderLine

PurchaseReturn (header)
  └─ PurchaseReturnLine (lines)
      └─ references GoodsReceiptLine

SupplierPriceList (standalone, no lines)
```

### 6.2 Cross-Module Dependencies
- **Products** → `retail.Product`, `retail.ProductVariant`
- **Warehouses** → `platform.Warehouse`
- **Suppliers** → `retail.Supplier`
- **Inventory** → Future: GoodsReceiptPosted event will trigger `inventory.StockMovementService`

### 6.3 No Duplicate Models
- Purchasing does NOT define its own Product, Supplier, or Warehouse models
- Uses cross-module FK references instead
- Keeps single source of truth in respective modules

### 6.4 Event-Driven Integration
Every business transaction emits domain events:
- `PurchaseRequisitionCreated`
- `PurchaseRequisitionApproved`
- `SupplierQuotationAccepted`
- `PurchaseOrderCreated`
- `PurchaseOrderAcknowledged`
- `GoodsReceiptPosted` → Inventory will subscribe
- `PurchaseReturnCreated`

Services will be implemented in Step 2 and will emit these events.

### 6.5 Header/Line Pattern
All multi-line entities follow the same pattern:
- Header entity (PurchaseOrder, GoodsReceipt, etc.)
- Line entity (PurchaseOrderLine, GoodsReceiptLine, etc.)
- Parent FK on line models
- CASCADE delete on parent

### 6.6 Tenant Isolation
- All models inherit from `TenantModel`
- All repositories filter by `tenant_id`
- All queries are tenant-scoped

### 6.7 Index Strategy
All indexes are tenant-first composites:
- `tenant_id + status` — for status-based filtering
- `tenant_id + supplier_id` — for supplier-centric queries
- `tenant_id + warehouse_id` — for warehouse-centric queries
- `tenant_id + created_at` — for listing recent records
- `tenant_id + document_number` — for document lookup

---

## 7. Repository Validation

| Check | Status | Notes |
|-------|--------|-------|
| **Persistence only** | ✅ | No business logic in repositories |
| **Returns domain entities** | ✅ | All methods return domain entities, not ORM models |
| **Tenant filtering** | ✅ | All queries filter by tenant_id |
| **Soft delete support** | ✅ | All headers have soft_delete() |
| **Generic _to_entity()** | ✅ | Reusable converter function |
| **Standard CRUD** | ✅ | get_by_id, list, create, update, soft_delete |

---

## 8. Tenant Isolation

| Entity | Tenant Isolation Method |
|--------|------------------------|
| PurchaseRequisition | `tenant_id` on all queries |
| SupplierQuotation | `tenant_id` on all queries |
| PurchaseOrder | `tenant_id` on all queries |
| GoodsReceipt | `tenant_id` on all queries |
| PurchaseReturn | `tenant_id` on all queries |
| SupplierPriceList | `tenant_id` on all queries |
| All Line entities | `tenant_id` on all queries |

---

## 9. Future Extensibility

| Feature | Design Support |
|---------|----------------|
| **Partial receipts** | GoodsReceiptLine tracks quantity_received vs quantity_accepted |
| **Multiple receipts per PO** | GoodsReceipt has FK to PurchaseOrder, not 1:1 |
| **Partial returns** | PurchaseReturnLine tracks quantity_returned |
| **Supplier lead times** | SupplierQuotationLine.lead_time_days |
| **Multi-currency** | All financial fields have currency field |
| **Tax inclusive/exclusive** | PurchaseOrderLine has tax_rate + tax_amount |
| **Approval workflow** | Approved_by, approved_at on all headers |
| **Attachments** | Notes field available; future: attachment model |
| **Comments** | Notes field available; future: comment model |
| **Audit history** | created_at, updated_at on all entities |
| **Company branding** | Entities designed for tenant-specific rendering later |

---

## 10. Cross-Module Dependencies

| Module | Dependency | Reason |
|--------|------------|--------|
| `retail` | Product, ProductVariant, Supplier | Products and suppliers are owned by Retail |
| `platform` | Warehouse | Warehouses are owned by Platform |
| `inventory` | Future: StockMovement | GoodsReceiptPosted will create stock movements |

**No circular dependencies.** Purchasing only depends on Retail and Platform. Inventory will depend on Purchasing events in future.

---

## 11. Architecture Compliance

| Rule | Status | Notes |
|------|--------|-------|
| **Clean Architecture** | ✅ | Domain entities are pure Python |
| **DDD** | ✅ | Aggregates, entities, value objects |
| **Repository Pattern** | ✅ | Persistence-only, return entities |
| **No business logic in repositories** | ✅ | Pure CRUD |
| **No ORM in domain** | ✅ | Entities use dataclasses |
| **Tenant isolation** | ✅ | All models inherit TenantModel |
| **UUID primary keys** | ✅ | All entities have id field |
| **Soft delete** | ✅ | All headers support soft_delete() |
| **Audit fields** | ✅ | created_at, updated_at on all entities |
| **Indexes** | ✅ | Tenant-first composite indexes |

---

## 12. Known Limitations

1. **No services yet** — Services, API, serializers, views will be implemented in Step 2
2. **No events yet** — Domain events will be created in Step 2
3. **No approval workflow** — Status fields exist but approval logic not implemented
4. **No document numbering** — order_number, receipt_number, etc. are strings; numbering logic in service layer
5. **No currency conversion** — Multi-currency fields exist but conversion logic in service layer
6. **No tax calculation** — Tax fields exist but calculation logic in service layer
7. **No validation** — Entity validation will be in services/serializers
8. **No attachments** — Future: attachment model for PO PDFs, GRN photos, etc.

---

## 13. Ready for Step 2

Domain foundation is complete. Ready for:
- Step 2: Application services + domain events
- Step 3: API layer

---

**Last Updated:** 2026-07-20