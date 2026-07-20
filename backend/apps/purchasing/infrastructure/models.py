"""
Django ORM models for the Purchasing module.

Purchasing manages the procurement lifecycle:
PurchaseRequisition → SupplierQuotation → PurchaseOrder → GoodsReceipt → Inventory

All models inherit from TenantModel for multi-tenant isolation.
References to Product, Warehouse, and Supplier use cross-module FK relationships.
"""

from django.db import models

from infrastructure.db.base_model import TenantModel


class PurchaseRequisitionModel(TenantModel):
    """Purchase requisition header."""

    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="purchase_requisitions")
    requested_by = models.UUIDField()
    required_date = models.DateTimeField(null=True, blank=True)
    justification = models.TextField(blank=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    approved_by = models.UUIDField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True)
    total_estimated_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, default="ZAR")
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "purchasing_purchase_requisitions"
        verbose_name = "Purchase Requisition"
        verbose_name_plural = "Purchase Requisitions"
        indexes = [
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "warehouse"]),
            models.Index(fields=["tenant_id", "requested_by"]),
            models.Index(fields=["tenant_id", "required_date"]),
            models.Index(fields=["tenant_id", "created_at"]),
        ]


class PurchaseRequisitionLineModel(TenantModel):
    """Line item within a purchase requisition."""

    requisition = models.ForeignKey(PurchaseRequisitionModel, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_of_measure = models.CharField(max_length=20, default="count")
    estimated_unit_price = models.DecimalField(max_digits=18, decimal_places=4, null=True, blank=True)
    estimated_total = models.DecimalField(max_digits=20, decimal_places=4, null=True, blank=True)
    notes = models.TextField(blank=True)
    line_number = models.IntegerField(default=0)

    class Meta:
        db_table = "purchasing_requisition_lines"
        verbose_name = "Purchase Requisition Line"
        verbose_name_plural = "Purchase Requisition Lines"
        indexes = [
            models.Index(fields=["tenant_id", "requisition", "line_number"]),
            models.Index(fields=["tenant_id", "product"]),
        ]


class SupplierQuotationModel(TenantModel):
    """Supplier quotation header."""

    supplier = models.ForeignKey("retail.Supplier", on_delete=models.PROTECT, related_name="quotes")
    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="supplier_quotations")
    quotation_reference = models.CharField(max_length=100, blank=True, db_index=True)
    quotation_date = models.DateTimeField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True, db_index=True)
    validity_days = models.IntegerField(default=30)
    currency = models.CharField(max_length=3, default="ZAR")
    payment_terms = models.CharField(max_length=100, blank=True)
    delivery_terms = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "purchasing_supplier_quotations"
        verbose_name = "Supplier Quotation"
        verbose_name_plural = "Supplier Quotations"
        indexes = [
            models.Index(fields=["tenant_id", "supplier", "status"]),
            models.Index(fields=["tenant_id", "warehouse"]),
            models.Index(fields=["tenant_id", "quotation_date"]),
            models.Index(fields=["tenant_id", "expiry_date"]),
        ]


class SupplierQuotationLineModel(TenantModel):
    """Line item within a supplier quotation."""

    quotation = models.ForeignKey(SupplierQuotationModel, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity = models.DecimalField(max_digits=18, decimal_places=3)
    unit_price = models.DecimalField(max_digits=18, decimal_places=4)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    total_price = models.DecimalField(max_digits=20, decimal_places=4)
    lead_time_days = models.IntegerField(default=0)
    validity_days = models.IntegerField(default=30)
    notes = models.TextField(blank=True)
    line_number = models.IntegerField(default=0)

    class Meta:
        db_table = "purchasing_quotation_lines"
        verbose_name = "Supplier Quotation Line"
        verbose_name_plural = "Supplier Quotation Lines"
        indexes = [
            models.Index(fields=["tenant_id", "quotation", "line_number"]),
            models.Index(fields=["tenant_id", "product"]),
        ]


class PurchaseOrderModel(TenantModel):
    """Purchase order header."""

    supplier = models.ForeignKey("retail.Supplier", on_delete=models.PROTECT, related_name="purchase_orders")
    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="purchase_orders")
    order_type = models.CharField(max_length=20, default="standard", db_index=True)
    order_number = models.CharField(max_length=100, blank=True, db_index=True)
    order_date = models.DateTimeField(null=True, blank=True, db_index=True)
    required_delivery_date = models.DateTimeField(null=True, blank=True)
    currency = models.CharField(max_length=3, default="ZAR")
    payment_terms = models.CharField(max_length=100, blank=True)
    delivery_terms = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    subtotal = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    approved_by = models.UUIDField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "purchasing_purchase_orders"
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        indexes = [
            models.Index(fields=["tenant_id", "supplier", "status"]),
            models.Index(fields=["tenant_id", "warehouse", "status"]),
            models.Index(fields=["tenant_id", "order_type"]),
            models.Index(fields=["tenant_id", "order_number"]),
            models.Index(fields=["tenant_id", "order_date"]),
            models.Index(fields=["tenant_id", "status", "required_delivery_date"]),
        ]


class PurchaseOrderLineModel(TenantModel):
    """Line item within a purchase order."""

    purchase_order = models.ForeignKey(PurchaseOrderModel, on_delete=models.CASCADE, related_name="lines")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity_ordered = models.DecimalField(max_digits=18, decimal_places=3)
    quantity_received = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_invoiced = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit_price = models.DecimalField(max_digits=18, decimal_places=4)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    line_total = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    currency = models.CharField(max_length=3, default="ZAR")
    expected_delivery_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    line_number = models.IntegerField(default=0)

    class Meta:
        db_table = "purchasing_po_lines"
        verbose_name = "Purchase Order Line"
        verbose_name_plural = "Purchase Order Lines"
        indexes = [
            models.Index(fields=["tenant_id", "purchase_order", "line_number"]),
            models.Index(fields=["tenant_id", "product"]),
            models.Index(fields=["tenant_id", "variant"]),
        ]


class GoodsReceiptModel(TenantModel):
    """Goods receipt header."""

    purchase_order = models.ForeignKey(PurchaseOrderModel, on_delete=models.PROTECT, related_name="receipts")
    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="goods_receipts")
    receipt_number = models.CharField(max_length=100, blank=True, db_index=True)
    receipt_date = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    posted_by = models.UUIDField(null=True, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "purchasing_goods_receipts"
        verbose_name = "Goods Receipt"
        verbose_name_plural = "Goods Receipts"
        indexes = [
            models.Index(fields=["tenant_id", "purchase_order", "status"]),
            models.Index(fields=["tenant_id", "warehouse"]),
            models.Index(fields=["tenant_id", "receipt_date"]),
            models.Index(fields=["tenant_id", "posted_by"]),
        ]


class GoodsReceiptLineModel(TenantModel):
    """Line item within a goods receipt."""

    goods_receipt = models.ForeignKey(GoodsReceiptModel, on_delete=models.CASCADE, related_name="lines")
    purchase_order_line = models.ForeignKey(PurchaseOrderLineModel, null=True, blank=True, on_delete=models.SET_NULL, related_name="receipt_lines")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity_received = models.DecimalField(max_digits=18, decimal_places=3)
    quantity_accepted = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_rejected = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4)
    line_total = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    batch_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    line_number = models.IntegerField(default=0)

    class Meta:
        db_table = "purchasing_receipt_lines"
        verbose_name = "Goods Receipt Line"
        verbose_name_plural = "Goods Receipt Lines"
        indexes = [
            models.Index(fields=["tenant_id", "goods_receipt", "line_number"]),
            models.Index(fields=["tenant_id", "product"]),
            models.Index(fields=["tenant_id", "purchase_order_line"]),
        ]


class PurchaseReturnModel(TenantModel):
    """Purchase return header."""

    purchase_order = models.ForeignKey(PurchaseOrderModel, on_delete=models.PROTECT, related_name="returns")
    goods_receipt = models.ForeignKey(GoodsReceiptModel, on_delete=models.PROTECT, related_name="returns")
    supplier = models.ForeignKey("retail.Supplier", on_delete=models.PROTECT, related_name="purchase_returns")
    warehouse = models.ForeignKey("platform.Warehouse", on_delete=models.PROTECT, related_name="purchase_returns")
    return_number = models.CharField(max_length=100, blank=True, db_index=True)
    return_date = models.DateTimeField(null=True, blank=True, db_index=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    total_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default="ZAR")
    approved_by = models.UUIDField(null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(null=True, blank=True)
    credited_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = "purchasing_purchase_returns"
        verbose_name = "Purchase Return"
        verbose_name_plural = "Purchase Returns"
        indexes = [
            models.Index(fields=["tenant_id", "purchase_order", "status"]),
            models.Index(fields=["tenant_id", "supplier", "status"]),
            models.Index(fields=["tenant_id", "warehouse", "status"]),
            models.Index(fields=["tenant_id", "return_date"]),
        ]


class PurchaseReturnLineModel(TenantModel):
    """Line item within a purchase return."""

    purchase_return = models.ForeignKey(PurchaseReturnModel, on_delete=models.CASCADE, related_name="lines")
    goods_receipt_line = models.ForeignKey(GoodsReceiptLineModel, null=True, blank=True, on_delete=models.SET_NULL, related_name="return_lines")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="+")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    quantity_returned = models.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = models.DecimalField(max_digits=18, decimal_places=4)
    line_total = models.DecimalField(max_digits=20, decimal_places=4, default=0)
    batch_number = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    return_reason = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    line_number = models.IntegerField(default=0)

    class Meta:
        db_table = "purchasing_return_lines"
        verbose_name = "Purchase Return Line"
        verbose_name_plural = "Purchase Return Lines"
        indexes = [
            models.Index(fields=["tenant_id", "purchase_return", "line_number"]),
            models.Index(fields=["tenant_id", "product"]),
        ]


class SupplierPriceListModel(TenantModel):
    """Supplier price list for a product."""

    supplier = models.ForeignKey("retail.Supplier", on_delete=models.PROTECT, related_name="price_lists")
    product = models.ForeignKey("retail.Product", on_delete=models.PROTECT, related_name="supplier_price_lists")
    variant = models.ForeignKey("retail.ProductVariant", null=True, blank=True, on_delete=models.SET_NULL, related_name="+")
    price = models.DecimalField(max_digits=18, decimal_places=4)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=18, decimal_places=4, default=0)
    effective_price = models.DecimalField(max_digits=18, decimal_places=4)
    currency = models.CharField(max_length=3, default="ZAR")
    valid_from = models.DateTimeField(null=True, blank=True, db_index=True)
    valid_to = models.DateTimeField(null=True, blank=True, db_index=True)
    minimum_order_quantity = models.DecimalField(max_digits=18, decimal_places=3, default=0)
    lead_time_days = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "purchasing_supplier_price_lists"
        verbose_name = "Supplier Price List"
        verbose_name_plural = "Supplier Price Lists"
        unique_together = ("tenant_id", "supplier", "product", "variant", "valid_from")
        indexes = [
            models.Index(fields=["tenant_id", "supplier", "is_active"]),
            models.Index(fields=["tenant_id", "product", "is_active"]),
            models.Index(fields=["tenant_id", "valid_from", "valid_to"]),
        ]