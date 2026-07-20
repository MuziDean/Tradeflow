"""
Repositories for the Purchasing module.

Repositories are persistence-only adapters.
They convert between ORM models and domain entities.
No business logic is contained here.
"""

from typing import Optional

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
from apps.purchasing.infrastructure.models import (
    GoodsReceiptLineModel,
    GoodsReceiptModel,
    PurchaseOrderLineModel,
    PurchaseOrderModel,
    PurchaseRequisitionLineModel,
    PurchaseRequisitionModel,
    PurchaseReturnLineModel,
    PurchaseReturnModel,
    SupplierPriceListModel,
    SupplierQuotationLineModel,
    SupplierQuotationModel,
)


def _to_entity(model, entity_cls):
    """Convert an ORM model instance to a domain entity."""
    if model is None:
        return None
    data = {
        "id": str(model.id),
        "tenant_id": model.tenant_id,
        "created_at": model.created_at,
        "updated_at": model.updated_at,
    }
    for field in entity_cls.__dataclass_fields__:
        if field not in data and hasattr(model, field):
            data[field] = getattr(model, field)
    return entity_cls(**data)


class PurchaseRequisitionRepository:
    """Repository for PurchaseRequisition aggregate."""

    def __init__(self):
        self.model = PurchaseRequisitionModel

    def get_by_id(self, requisition_id: str, tenant_id: str) -> Optional[PurchaseRequisition]:
        try:
            model = self.model.objects.get(id=requisition_id, tenant_id=tenant_id)
            return _to_entity(model, PurchaseRequisition)
        except self.model.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str, status: str = "") -> list[PurchaseRequisition]:
        qs = self.model.objects.filter(tenant_id=tenant_id)
        if status:
            qs = qs.filter(status=status)
        return [_to_entity(m, PurchaseRequisition) for m in qs.order_by("-created_at")]

    def create(self, requisition: PurchaseRequisition) -> PurchaseRequisition:
        model = self.model(
            tenant_id=requisition.tenant_id,
            warehouse_id=requisition.warehouse_id,
            requested_by=requisition.requested_by,
            required_date=requisition.required_date,
            justification=requisition.justification,
            status=requisition.status,
            approved_by=requisition.approved_by,
            rejected_reason=requisition.rejected_reason,
            total_estimated_amount=requisition.total_estimated_amount,
            currency=requisition.currency,
            notes=requisition.notes,
        )
        model.save()
        return _to_entity(model, PurchaseRequisition)

    def update(self, requisition: PurchaseRequisition) -> PurchaseRequisition:
        try:
            model = self.model.objects.get(id=requisition.id, tenant_id=requisition.tenant_id)
        except self.model.DoesNotExist:
            raise ValueError("PurchaseRequisition not found")
        for field in ["warehouse_id", "required_date", "justification", "status", "approved_by", "rejected_reason", "total_estimated_amount", "currency", "notes"]:
            setattr(model, field, getattr(requisition, field))
        model.save()
        return _to_entity(model, PurchaseRequisition)

    def soft_delete(self, requisition_id: str, tenant_id: str) -> bool:
        try:
            model = self.model.objects.get(id=requisition_id, tenant_id=tenant_id)
            model.delete()
            return True
        except self.model.DoesNotExist:
            return False


class PurchaseRequisitionLineRepository:
    """Repository for PurchaseRequisitionLine."""

    def __init__(self):
        self.model = PurchaseRequisitionLineModel

    def create(self, line) -> PurchaseRequisitionLine:
        model = self.model(
            tenant_id=line.tenant_id,
            requisition_id=line.requisition_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity=line.quantity,
            unit_of_measure=line.unit_of_measure,
            estimated_unit_price=line.estimated_unit_price,
            estimated_total=line.estimated_total,
            notes=line.notes,
            line_number=line.line_number,
        )
        model.save()
        return _to_entity(model, PurchaseRequisitionLine)

    def list_for_requisition(self, tenant_id: str, requisition_id: str) -> list[PurchaseRequisitionLine]:
        qs = self.model.objects.filter(tenant_id=tenant_id, requisition_id=requisition_id)
        return [_to_entity(m, PurchaseRequisitionLine) for m in qs.order_by("line_number")]


class SupplierQuotationRepository:
    """Repository for SupplierQuotation aggregate."""

    def __init__(self):
        self.model = SupplierQuotationModel

    def get_by_id(self, quotation_id: str, tenant_id: str) -> Optional[SupplierQuotation]:
        try:
            model = self.model.objects.get(id=quotation_id, tenant_id=tenant_id)
            return _to_entity(model, SupplierQuotation)
        except self.model.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str, status: str = "") -> list[SupplierQuotation]:
        qs = self.model.objects.filter(tenant_id=tenant_id)
        if status:
            qs = qs.filter(status=status)
        return [_to_entity(m, SupplierQuotation) for m in qs.order_by("-created_at")]

    def create(self, quotation: SupplierQuotation) -> SupplierQuotation:
        model = self.model(
            tenant_id=quotation.tenant_id,
            supplier_id=quotation.supplier_id,
            warehouse_id=quotation.warehouse_id,
            quotation_reference=quotation.quotation_reference,
            quotation_date=quotation.quotation_date,
            expiry_date=quotation.expiry_date,
            validity_days=quotation.validity_days,
            currency=quotation.currency,
            payment_terms=quotation.payment_terms,
            delivery_terms=quotation.delivery_terms,
            status=quotation.status,
            total_amount=quotation.total_amount,
            notes=quotation.notes,
        )
        model.save()
        return _to_entity(model, SupplierQuotation)

    def update(self, quotation: SupplierQuotation) -> SupplierQuotation:
        try:
            model = self.model.objects.get(id=quotation.id, tenant_id=quotation.tenant_id)
        except self.model.DoesNotExist:
            raise ValueError("SupplierQuotation not found")
        for field in ["supplier_id", "warehouse_id", "quotation_reference", "quotation_date", "expiry_date", "validity_days", "currency", "payment_terms", "delivery_terms", "status", "total_amount", "notes"]:
            setattr(model, field, getattr(quotation, field))
        model.save()
        return _to_entity(model, SupplierQuotation)

    def soft_delete(self, quotation_id: str, tenant_id: str) -> bool:
        try:
            model = self.model.objects.get(id=quotation_id, tenant_id=tenant_id)
            model.delete()
            return True
        except self.model.DoesNotExist:
            return False


class SupplierQuotationLineRepository:
    """Repository for SupplierQuotationLine."""

    def __init__(self):
        self.model = SupplierQuotationLineModel

    def create(self, line) -> SupplierQuotationLine:
        model = self.model(
            tenant_id=line.tenant_id,
            quotation_id=line.quotation_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity=line.quantity,
            unit_price=line.unit_price,
            discount_percent=line.discount_percent,
            discount_amount=line.discount_amount,
            total_price=line.total_price,
            lead_time_days=line.lead_time_days,
            validity_days=line.validity_days,
            notes=line.notes,
            line_number=line.line_number,
        )
        model.save()
        return _to_entity(model, SupplierQuotationLine)

    def list_for_quotation(self, tenant_id: str, quotation_id: str) -> list[SupplierQuotationLine]:
        qs = self.model.objects.filter(tenant_id=tenant_id, quotation_id=quotation_id)
        return [_to_entity(m, SupplierQuotationLine) for m in qs.order_by("line_number")]


class PurchaseOrderRepository:
    """Repository for PurchaseOrder aggregate."""

    def __init__(self):
        self.model = PurchaseOrderModel

    def get_by_id(self, order_id: str, tenant_id: str) -> Optional[PurchaseOrder]:
        try:
            model = self.model.objects.get(id=order_id, tenant_id=tenant_id)
            return _to_entity(model, PurchaseOrder)
        except self.model.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str, status: str = "") -> list[PurchaseOrder]:
        qs = self.model.objects.filter(tenant_id=tenant_id)
        if status:
            qs = qs.filter(status=status)
        return [_to_entity(m, PurchaseOrder) for m in qs.order_by("-created_at")]

    def create(self, order: PurchaseOrder) -> PurchaseOrder:
        model = self.model(
            tenant_id=order.tenant_id,
            supplier_id=order.supplier_id,
            warehouse_id=order.warehouse_id,
            order_type=order.order_type,
            order_number=order.order_number,
            order_date=order.order_date,
            required_delivery_date=order.required_delivery_date,
            currency=order.currency,
            payment_terms=order.payment_terms,
            delivery_terms=order.delivery_terms,
            status=order.status,
            subtotal=order.subtotal,
            tax_total=order.tax_total,
            grand_total=order.grand_total,
            approved_by=order.approved_by,
            approved_at=order.approved_at,
            sent_at=order.sent_at,
            acknowledged_at=order.acknowledged_at,
            notes=order.notes,
        )
        model.save()
        return _to_entity(model, PurchaseOrder)

    def update(self, order: PurchaseOrder) -> PurchaseOrder:
        try:
            model = self.model.objects.get(id=order.id, tenant_id=order.tenant_id)
        except self.model.DoesNotExist:
            raise ValueError("PurchaseOrder not found")
        for field in ["supplier_id", "warehouse_id", "order_type", "order_number", "order_date", "required_delivery_date", "currency", "payment_terms", "delivery_terms", "status", "subtotal", "tax_total", "grand_total", "approved_by", "approved_at", "sent_at", "acknowledged_at", "notes"]:
            setattr(model, field, getattr(order, field))
        model.save()
        return _to_entity(model, PurchaseOrder)

    def soft_delete(self, order_id: str, tenant_id: str) -> bool:
        try:
            model = self.model.objects.get(id=order_id, tenant_id=tenant_id)
            model.delete()
            return True
        except self.model.DoesNotExist:
            return False


class PurchaseOrderLineRepository:
    """Repository for PurchaseOrderLine."""

    def __init__(self):
        self.model = PurchaseOrderLineModel

    def create(self, line) -> PurchaseOrderLine:
        model = self.model(
            tenant_id=line.tenant_id,
            purchase_order_id=line.purchase_order_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity_ordered=line.quantity_ordered,
            quantity_received=line.quantity_received,
            quantity_invoiced=line.quantity_invoiced,
            unit_price=line.unit_price,
            discount_percent=line.discount_percent,
            discount_amount=line.discount_amount,
            tax_rate=line.tax_rate,
            tax_amount=line.tax_amount,
            line_total=line.line_total,
            currency=line.currency,
            expected_delivery_date=line.expected_delivery_date,
            notes=line.notes,
            line_number=line.line_number,
        )
        model.save()
        return _to_entity(model, PurchaseOrderLine)

    def list_for_order(self, tenant_id: str, order_id: str) -> list[PurchaseOrderLine]:
        qs = self.model.objects.filter(tenant_id=tenant_id, purchase_order_id=order_id)
        return [_to_entity(m, PurchaseOrderLine) for m in qs.order_by("line_number")]


class GoodsReceiptRepository:
    """Repository for GoodsReceipt aggregate."""

    def __init__(self):
        self.model = GoodsReceiptModel

    def get_by_id(self, receipt_id: str, tenant_id: str) -> Optional[GoodsReceipt]:
        try:
            model = self.model.objects.get(id=receipt_id, tenant_id=tenant_id)
            return _to_entity(model, GoodsReceipt)
        except self.model.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str, status: str = "") -> list[GoodsReceipt]:
        qs = self.model.objects.filter(tenant_id=tenant_id)
        if status:
            qs = qs.filter(status=status)
        return [_to_entity(m, GoodsReceipt) for m in qs.order_by("-created_at")]

    def create(self, receipt: GoodsReceipt) -> GoodsReceipt:
        model = self.model(
            tenant_id=receipt.tenant_id,
            purchase_order_id=receipt.purchase_order_id,
            warehouse_id=receipt.warehouse_id,
            receipt_number=receipt.receipt_number,
            receipt_date=receipt.receipt_date,
            status=receipt.status,
            posted_by=receipt.posted_by,
            posted_at=receipt.posted_at,
            notes=receipt.notes,
        )
        model.save()
        return _to_entity(model, GoodsReceipt)

    def update(self, receipt: GoodsReceipt) -> GoodsReceipt:
        try:
            model = self.model.objects.get(id=receipt.id, tenant_id=receipt.tenant_id)
        except self.model.DoesNotExist:
            raise ValueError("GoodsReceipt not found")
        for field in ["purchase_order_id", "warehouse_id", "receipt_number", "receipt_date", "status", "posted_by", "posted_at", "notes"]:
            setattr(model, field, getattr(receipt, field))
        model.save()
        return _to_entity(model, GoodsReceipt)

    def soft_delete(self, receipt_id: str, tenant_id: str) -> bool:
        try:
            model = self.model.objects.get(id=receipt_id, tenant_id=tenant_id)
            model.delete()
            return True
        except self.model.DoesNotExist:
            return False


class GoodsReceiptLineRepository:
    """Repository for GoodsReceiptLine."""

    def __init__(self):
        self.model = GoodsReceiptLineModel

    def create(self, line) -> GoodsReceiptLine:
        model = self.model(
            tenant_id=line.tenant_id,
            goods_receipt_id=line.goods_receipt_id,
            purchase_order_line_id=line.purchase_order_line_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity_received=line.quantity_received,
            quantity_accepted=line.quantity_accepted,
            quantity_rejected=line.quantity_rejected,
            unit_cost=line.unit_cost,
            line_total=line.line_total,
            batch_number=line.batch_number,
            serial_number=line.serial_number,
            expiry_date=line.expiry_date,
            rejection_reason=line.rejection_reason,
            notes=line.notes,
            line_number=line.line_number,
        )
        model.save()
        return _to_entity(model, GoodsReceiptLine)

    def list_for_receipt(self, tenant_id: str, receipt_id: str) -> list[GoodsReceiptLine]:
        qs = self.model.objects.filter(tenant_id=tenant_id, goods_receipt_id=receipt_id)
        return [_to_entity(m, GoodsReceiptLine) for m in qs.order_by("line_number")]


class PurchaseReturnRepository:
    """Repository for PurchaseReturn aggregate."""

    def __init__(self):
        self.model = PurchaseReturnModel

    def get_by_id(self, return_id: str, tenant_id: str) -> Optional[PurchaseReturn]:
        try:
            model = self.model.objects.get(id=return_id, tenant_id=tenant_id)
            return _to_entity(model, PurchaseReturn)
        except self.model.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str, status: str = "") -> list[PurchaseReturn]:
        qs = self.model.objects.filter(tenant_id=tenant_id)
        if status:
            qs = qs.filter(status=status)
        return [_to_entity(m, PurchaseReturn) for m in qs.order_by("-created_at")]

    def create(self, return_obj: PurchaseReturn) -> PurchaseReturn:
        model = self.model(
            tenant_id=return_obj.tenant_id,
            purchase_order_id=return_obj.purchase_order_id,
            goods_receipt_id=return_obj.goods_receipt_id,
            supplier_id=return_obj.supplier_id,
            warehouse_id=return_obj.warehouse_id,
            return_number=return_obj.return_number,
            return_date=return_obj.return_date,
            status=return_obj.status,
            total_amount=return_obj.total_amount,
            currency=return_obj.currency,
            approved_by=return_obj.approved_by,
            approved_at=return_obj.approved_at,
            received_at=return_obj.received_at,
            credited_at=return_obj.credited_at,
            notes=return_obj.notes,
        )
        model.save()
        return _to_entity(model, PurchaseReturn)

    def update(self, return_obj: PurchaseReturn) -> PurchaseReturn:
        try:
            model = self.model.objects.get(id=return_obj.id, tenant_id=return_obj.tenant_id)
        except self.model.DoesNotExist:
            raise ValueError("PurchaseReturn not found")
        for field in ["purchase_order_id", "goods_receipt_id", "supplier_id", "warehouse_id", "return_number", "return_date", "status", "total_amount", "currency", "approved_by", "approved_at", "received_at", "credited_at", "notes"]:
            setattr(model, field, getattr(return_obj, field))
        model.save()
        return _to_entity(model, PurchaseReturn)

    def soft_delete(self, return_id: str, tenant_id: str) -> bool:
        try:
            model = self.model.objects.get(id=return_id, tenant_id=tenant_id)
            model.delete()
            return True
        except self.model.DoesNotExist:
            return False


class PurchaseReturnLineRepository:
    """Repository for PurchaseReturnLine."""

    def __init__(self):
        self.model = PurchaseReturnLineModel

    def create(self, line) -> PurchaseReturnLine:
        model = self.model(
            tenant_id=line.tenant_id,
            purchase_return_id=line.purchase_return_id,
            goods_receipt_line_id=line.goods_receipt_line_id,
            product_id=line.product_id,
            variant_id=line.variant_id,
            quantity_returned=line.quantity_returned,
            unit_cost=line.unit_cost,
            line_total=line.line_total,
            batch_number=line.batch_number,
            serial_number=line.serial_number,
            expiry_date=line.expiry_date,
            return_reason=line.return_reason,
            notes=line.notes,
            line_number=line.line_number,
        )
        model.save()
        return _to_entity(model, PurchaseReturnLine)

    def list_for_return(self, tenant_id: str, return_id: str) -> list[PurchaseReturnLine]:
        qs = self.model.objects.filter(tenant_id=tenant_id, purchase_return_id=return_id)
        return [_to_entity(m, PurchaseReturnLine) for m in qs.order_by("line_number")]


class SupplierPriceListRepository:
    """Repository for SupplierPriceList."""

    def __init__(self):
        self.model = SupplierPriceListModel

    def get_by_id(self, price_list_id: str, tenant_id: str) -> Optional[SupplierPriceList]:
        try:
            model = self.model.objects.get(id=price_list_id, tenant_id=tenant_id)
            return _to_entity(model, SupplierPriceList)
        except self.model.DoesNotExist:
            return None

    def get_active_for_supplier_product(self, tenant_id: str, supplier_id: str, product_id: str, variant_id: str = None) -> Optional[SupplierPriceList]:
        qs = self.model.objects.filter(
            tenant_id=tenant_id,
            supplier_id=supplier_id,
            product_id=product_id,
            is_active=True,
        )
        if variant_id:
            qs = qs.filter(variant_id=variant_id)
        else:
            qs = qs.filter(variant_id__isnull=True)
        model = qs.order_by("-valid_from").first()
        return _to_entity(model, SupplierPriceList) if model else None

    def list_for_tenant(self, tenant_id: str, supplier_id: str = "") -> list[SupplierPriceList]:
        qs = self.model.objects.filter(tenant_id=tenant_id, is_active=True)
        if supplier_id:
            qs = qs.filter(supplier_id=supplier_id)
        return [_to_entity(m, SupplierPriceList) for m in qs.order_by("-valid_from")]

    def create(self, price_list: SupplierPriceList) -> SupplierPriceList:
        model = self.model(
            tenant_id=price_list.tenant_id,
            supplier_id=price_list.supplier_id,
            product_id=price_list.product_id,
            variant_id=price_list.variant_id,
            price=price_list.price,
            discount_percent=price_list.discount_percent,
            discount_amount=price_list.discount_amount,
            effective_price=price_list.effective_price,
            currency=price_list.currency,
            valid_from=price_list.valid_from,
            valid_to=price_list.valid_to,
            minimum_order_quantity=price_list.minimum_order_quantity,
            lead_time_days=price_list.lead_time_days,
            is_active=price_list.is_active,
        )
        model.save()
        return _to_entity(model, SupplierPriceList)

    def update(self, price_list: SupplierPriceList) -> SupplierPriceList:
        try:
            model = self.model.objects.get(id=price_list.id, tenant_id=price_list.tenant_id)
        except self.model.DoesNotExist:
            raise ValueError("SupplierPriceList not found")
        for field in ["supplier_id", "product_id", "variant_id", "price", "discount_percent", "discount_amount", "effective_price", "currency", "valid_from", "valid_to", "minimum_order_quantity", "lead_time_days", "is_active"]:
            setattr(model, field, getattr(price_list, field))
        model.save()
        return _to_entity(model, SupplierPriceList)

    def soft_delete(self, price_list_id: str, tenant_id: str) -> bool:
        try:
            model = self.model.objects.get(id=price_list_id, tenant_id=tenant_id)
            model.delete()
            return True
        except self.model.DoesNotExist:
            return False