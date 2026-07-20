"""
Serializers for the Purchasing API.

Serializers validate and format data only.
No business logic is implemented here.
"""

from rest_framework import serializers

from apps.purchasing.domain.entities import (
    GoodsReceipt,
    GoodsReceiptLine,
    PurchaseOrder,
    PurchaseOrderLine,
    PurchaseRequisition,
    PurchaseRequisitionLine,
    PurchaseReturn,
    PurchaseReturnLine,
    SupplierPriceList,
    SupplierQuotation,
    SupplierQuotationLine,
)


class PurchaseRequisitionLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    requisition_id = serializers.CharField(read_only=True)
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    unit_of_measure = serializers.CharField(default="count")
    estimated_unit_price = serializers.DecimalField(max_digits=18, decimal_places=4, allow_null=True, required=False)
    estimated_total = serializers.DecimalField(max_digits=20, decimal_places=4, allow_null=True, required=False)
    notes = serializers.CharField(allow_blank=True, required=False)
    line_number = serializers.IntegerField(default=0)
    created_at = serializers.CharField(read_only=True)


class PurchaseRequisitionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    requested_by = serializers.CharField()
    required_date = serializers.DateTimeField(allow_null=True, required=False)
    justification = serializers.CharField()
    status = serializers.CharField(read_only=True)
    approved_by = serializers.CharField(read_only=True)
    rejected_reason = serializers.CharField(allow_blank=True, read_only=True)
    total_estimated_amount = serializers.DecimalField(max_digits=20, decimal_places=2, allow_null=True, required=False)
    currency = serializers.CharField(default="ZAR")
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class PurchaseRequisitionListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    warehouse_id = serializers.CharField()
    requested_by = serializers.CharField()
    required_date = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    total_estimated_amount = serializers.DecimalField(max_digits=20, decimal_places=2, allow_null=True)
    created_at = serializers.CharField(read_only=True)


class SupplierQuotationLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    quotation_id = serializers.CharField(read_only=True)
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity = serializers.DecimalField(max_digits=18, decimal_places=3)
    unit_price = serializers.DecimalField(max_digits=18, decimal_places=4)
    discount_percent = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    total_price = serializers.DecimalField(max_digits=20, decimal_places=4)
    lead_time_days = serializers.IntegerField(default=0)
    validity_days = serializers.IntegerField(default=30)
    notes = serializers.CharField(allow_blank=True, required=False)
    line_number = serializers.IntegerField(default=0)
    created_at = serializers.CharField(read_only=True)


class SupplierQuotationSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    supplier_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    quotation_reference = serializers.CharField(allow_blank=True, required=False)
    quotation_date = serializers.DateTimeField(allow_null=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    validity_days = serializers.IntegerField(default=30)
    currency = serializers.CharField(default="ZAR")
    payment_terms = serializers.CharField(allow_blank=True, required=False)
    delivery_terms = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, allow_null=True, required=False)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class SupplierQuotationListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    supplier_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    quotation_reference = serializers.CharField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, allow_null=True)
    created_at = serializers.CharField(read_only=True)


class PurchaseOrderLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    purchase_order_id = serializers.CharField(read_only=True)
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity_ordered = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_received = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_invoiced = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit_price = serializers.DecimalField(max_digits=18, decimal_places=4)
    discount_percent = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    tax_rate = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    tax_amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    line_total = serializers.DecimalField(max_digits=20, decimal_places=4, default=0)
    currency = serializers.CharField(default="ZAR")
    expected_delivery_date = serializers.DateTimeField(allow_null=True, required=False)
    notes = serializers.CharField(allow_blank=True, required=False)
    line_number = serializers.IntegerField(default=0)
    created_at = serializers.CharField(read_only=True)


class PurchaseOrderSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    supplier_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    order_type = serializers.CharField(default="standard")
    order_number = serializers.CharField(read_only=True)
    order_date = serializers.DateTimeField(read_only=True)
    required_delivery_date = serializers.DateTimeField(allow_null=True, required=False)
    currency = serializers.CharField(default="ZAR")
    payment_terms = serializers.CharField(allow_blank=True, required=False)
    delivery_terms = serializers.CharField(allow_blank=True, required=False)
    status = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=20, decimal_places=2, default=0)
    tax_total = serializers.DecimalField(max_digits=20, decimal_places=2, default=0)
    grand_total = serializers.DecimalField(max_digits=20, decimal_places=2, default=0)
    approved_by = serializers.CharField(read_only=True)
    approved_at = serializers.DateTimeField(allow_null=True, read_only=True)
    sent_at = serializers.DateTimeField(allow_null=True, read_only=True)
    acknowledged_at = serializers.DateTimeField(allow_null=True, read_only=True)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class PurchaseOrderListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    supplier_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    order_type = serializers.CharField()
    order_number = serializers.CharField()
    order_date = serializers.DateTimeField(allow_null=True)
    required_delivery_date = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    grand_total = serializers.DecimalField(max_digits=20, decimal_places=2)
    created_at = serializers.CharField(read_only=True)


class GoodsReceiptLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    goods_receipt_id = serializers.CharField(read_only=True)
    purchase_order_line_id = serializers.CharField(allow_null=True, required=False)
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity_received = serializers.DecimalField(max_digits=18, decimal_places=3)
    quantity_accepted = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    quantity_rejected = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4)
    line_total = serializers.DecimalField(max_digits=20, decimal_places=4, default=0)
    batch_number = serializers.CharField(allow_blank=True, required=False)
    serial_number = serializers.CharField(allow_blank=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    rejection_reason = serializers.CharField(allow_blank=True, required=False)
    notes = serializers.CharField(allow_blank=True, required=False)
    line_number = serializers.IntegerField(default=0)
    created_at = serializers.CharField(read_only=True)


class GoodsReceiptSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    purchase_order_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    receipt_number = serializers.CharField(read_only=True)
    receipt_date = serializers.DateTimeField(allow_null=True, read_only=True)
    status = serializers.CharField(read_only=True)
    posted_by = serializers.CharField(read_only=True)
    posted_at = serializers.DateTimeField(allow_null=True, read_only=True)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class GoodsReceiptListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    purchase_order_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    receipt_number = serializers.CharField()
    receipt_date = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    created_at = serializers.CharField(read_only=True)


class PurchaseReturnLineSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    purchase_return_id = serializers.CharField(read_only=True)
    goods_receipt_line_id = serializers.CharField(allow_null=True, required=False)
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    quantity_returned = serializers.DecimalField(max_digits=18, decimal_places=3)
    unit_cost = serializers.DecimalField(max_digits=18, decimal_places=4)
    line_total = serializers.DecimalField(max_digits=20, decimal_places=4, default=0)
    batch_number = serializers.CharField(allow_blank=True, required=False)
    serial_number = serializers.CharField(allow_blank=True, required=False)
    expiry_date = serializers.DateTimeField(allow_null=True, required=False)
    return_reason = serializers.CharField(allow_blank=True, required=False)
    notes = serializers.CharField(allow_blank=True, required=False)
    line_number = serializers.IntegerField(default=0)
    created_at = serializers.CharField(read_only=True)


class PurchaseReturnSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    purchase_order_id = serializers.CharField()
    goods_receipt_id = serializers.CharField()
    supplier_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    return_number = serializers.CharField(read_only=True)
    return_date = serializers.DateTimeField(allow_null=True, read_only=True)
    status = serializers.CharField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2, default=0)
    currency = serializers.CharField(default="ZAR")
    approved_by = serializers.CharField(read_only=True)
    approved_at = serializers.DateTimeField(allow_null=True, read_only=True)
    received_at = serializers.DateTimeField(allow_null=True, read_only=True)
    credited_at = serializers.DateTimeField(allow_null=True, read_only=True)
    notes = serializers.CharField(allow_blank=True, required=False)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class PurchaseReturnListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    purchase_order_id = serializers.CharField()
    goods_receipt_id = serializers.CharField()
    supplier_id = serializers.CharField()
    warehouse_id = serializers.CharField()
    return_number = serializers.CharField()
    return_date = serializers.DateTimeField(allow_null=True)
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    created_at = serializers.CharField(read_only=True)


class SupplierPriceListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    tenant_id = serializers.CharField(read_only=True)
    supplier_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True, required=False)
    price = serializers.DecimalField(max_digits=18, decimal_places=4)
    discount_percent = serializers.DecimalField(max_digits=5, decimal_places=2, default=0)
    discount_amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    effective_price = serializers.DecimalField(max_digits=18, decimal_places=4)
    currency = serializers.CharField(default="ZAR")
    valid_from = serializers.DateTimeField(allow_null=True, required=False)
    valid_to = serializers.DateTimeField(allow_null=True, required=False)
    minimum_order_quantity = serializers.DecimalField(max_digits=18, decimal_places=3, default=0)
    lead_time_days = serializers.IntegerField(default=0)
    is_active = serializers.BooleanField(default=True)
    created_at = serializers.CharField(read_only=True)
    updated_at = serializers.CharField(read_only=True)


class SupplierPriceListListSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    supplier_id = serializers.CharField()
    product_id = serializers.CharField()
    variant_id = serializers.CharField(allow_null=True)
    price = serializers.DecimalField(max_digits=18, decimal_places=4)
    effective_price = serializers.DecimalField(max_digits=18, decimal_places=4)
    valid_from = serializers.DateTimeField(allow_null=True)
    valid_to = serializers.DateTimeField(allow_null=True)
    is_active = serializers.BooleanField()
    created_at = serializers.CharField(read_only=True)