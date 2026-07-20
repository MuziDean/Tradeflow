"""
API views for the Purchasing module.

Per Backend Engineering Standards §5.1: Thin views that only:
- Authenticate and authorize
- Parse request input
- Call exactly one use-case
- Format response

All endpoints declare explicit RBAC permissions via required_permission.
All responses use the standard API response envelope.
"""

import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.purchasing.api.serializers import (
    GoodsReceiptLineSerializer,
    GoodsReceiptListSerializer,
    GoodsReceiptSerializer,
    PurchaseOrderLineSerializer,
    PurchaseOrderListSerializer,
    PurchaseOrderSerializer,
    PurchaseRequisitionLineSerializer,
    PurchaseRequisitionListSerializer,
    PurchaseRequisitionSerializer,
    PurchaseReturnLineSerializer,
    PurchaseReturnListSerializer,
    PurchaseReturnSerializer,
    SupplierPriceListListSerializer,
    SupplierPriceListSerializer,
    SupplierQuotationLineSerializer,
    SupplierQuotationListSerializer,
    SupplierQuotationSerializer,
)
from apps.purchasing.application.goods_receipt_service import GoodsReceiptService
from apps.purchasing.application.purchase_order_service import PurchaseOrderService
from apps.purchasing.application.purchase_requisition_service import PurchaseRequisitionService
from apps.purchasing.application.purchase_return_service import PurchaseReturnService
from apps.purchasing.application.supplier_price_list_service import SupplierPriceListService
from apps.purchasing.application.supplier_quotation_service import SupplierQuotationService
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
from apps.purchasing.infrastructure.repositories import (
    GoodsReceiptLineRepository,
    GoodsReceiptRepository,
    PurchaseOrderLineRepository,
    PurchaseOrderRepository,
    PurchaseRequisitionLineRepository,
    PurchaseRequisitionRepository,
    PurchaseReturnLineRepository,
    PurchaseReturnRepository,
    SupplierPriceListRepository,
    SupplierQuotationLineRepository,
    SupplierQuotationRepository,
)
from core.pagination import StandardPagination

logger = logging.getLogger("tradeflow.purchasing")


def _error_response(message: str, code: str = "ERROR", status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response({"success": False, "error": {"code": code, "message": message}}, status=status_code)


# ──────────────────────────────────────────────
# Purchase Requisitions
# ──────────────────────────────────────────────


class PurchaseRequisitionListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.requisitions.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["warehouse_id", "justification"]
    ordering_fields = ["status", "required_date", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PurchaseRequisitionSerializer
        return PurchaseRequisitionListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return PurchaseRequisitionModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        requisition = PurchaseRequisition(tenant_id=tenant_id, **serializer.validated_data)
        lines = [PurchaseRequisitionLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = PurchaseRequisitionService(requisition_repository=PurchaseRequisitionRepository(), line_repository=PurchaseRequisitionLineRepository())
        created = service.create(requisition, lines)
        return Response({"data": PurchaseRequisitionSerializer(created).data}, status=status.HTTP_201_CREATED)


PurchaseRequisitionListCreateView.create.required_permission = "purchasing.requisitions.create"


class PurchaseRequisitionDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.requisitions.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return PurchaseRequisitionSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return PurchaseRequisitionModel.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        existing = PurchaseRequisitionRepository().get_by_id(str(instance.id), tenant_id)
        if not existing:
            from django.http import Http404
            raise Http404
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)
        service = PurchaseRequisitionService(requisition_repository=PurchaseRequisitionRepository(), line_repository=PurchaseRequisitionLineRepository())
        updated = service.update(existing)
        return Response({"data": PurchaseRequisitionSerializer(updated).data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = PurchaseRequisitionService(requisition_repository=PurchaseRequisitionRepository(), line_repository=PurchaseRequisitionLineRepository())
        success = service.cancel(str(instance.id), tenant_id)
        if not success:
            return _error_response("Requisition not found or cannot be cancelled.", code="REQUISITION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": {"cancelled": True}}, status=status.HTTP_200_OK)


PurchaseRequisitionDetailView.update.required_permission = "purchasing.requisitions.update"
PurchaseRequisitionDetailView.destroy.required_permission = "purchasing.requisitions.delete"


class PurchaseRequisitionSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.requisitions.submit"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = PurchaseRequisitionService(requisition_repository=PurchaseRequisitionRepository(), line_repository=PurchaseRequisitionLineRepository())
        requisition = service.submit_for_approval(str(pk), tenant_id)
        if not requisition:
            return _error_response("Requisition not found or cannot be submitted.", code="REQUISITION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseRequisitionSerializer(requisition).data}, status=status.HTTP_200_OK)


class PurchaseRequisitionApproveView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.requisitions.approve"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        approved_by = str(request.actor.id)
        service = PurchaseRequisitionService(requisition_repository=PurchaseRequisitionRepository(), line_repository=PurchaseRequisitionLineRepository())
        requisition = service.approve(str(pk), tenant_id, approved_by)
        if not requisition:
            return _error_response("Requisition not found or cannot be approved.", code="REQUISITION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseRequisitionSerializer(requisition).data}, status=status.HTTP_200_OK)


class PurchaseRequisitionRejectView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.requisitions.reject"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        rejected_by = str(request.actor.id)
        reason = request.data.get("reason", "")
        service = PurchaseRequisitionService(requisition_repository=PurchaseRequisitionRepository(), line_repository=PurchaseRequisitionLineRepository())
        requisition = service.reject(str(pk), tenant_id, rejected_by, reason)
        if not requisition:
            return _error_response("Requisition not found or cannot be rejected.", code="REQUISITION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseRequisitionSerializer(requisition).data}, status=status.HTTP_200_OK)


class PurchaseRequisitionConvertView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.requisitions.convert"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        purchase_order_id = request.data.get("purchase_order_id")
        if not purchase_order_id:
            return _error_response("purchase_order_id is required.", code="VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
        service = PurchaseRequisitionService(requisition_repository=PurchaseRequisitionRepository(), line_repository=PurchaseRequisitionLineRepository())
        requisition = service.convert_to_purchase_order(str(pk), tenant_id, purchase_order_id)
        if not requisition:
            return _error_response("Requisition not found or cannot be converted.", code="REQUISITION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseRequisitionSerializer(requisition).data}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Supplier Quotations
# ──────────────────────────────────────────────


class SupplierQuotationListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.quotations.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["quotation_reference", "supplier_id"]
    ordering_fields = ["status", "quotation_date", "expiry_date"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupplierQuotationSerializer
        return SupplierQuotationListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return SupplierQuotationModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        quotation = SupplierQuotation(tenant_id=tenant_id, **serializer.validated_data)
        lines = [SupplierQuotationLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = SupplierQuotationService(quotation_repository=SupplierQuotationRepository(), line_repository=SupplierQuotationLineRepository())
        created = service.create(quotation, lines)
        return Response({"data": SupplierQuotationSerializer(created).data}, status=status.HTTP_201_CREATED)


SupplierQuotationListCreateView.create.required_permission = "purchasing.quotations.create"


class SupplierQuotationDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.quotations.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return SupplierQuotationSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return SupplierQuotationModel.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        existing = SupplierQuotationRepository().get_by_id(str(instance.id), tenant_id)
        if not existing:
            from django.http import Http404
            raise Http404
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)
        service = SupplierQuotationService(quotation_repository=SupplierQuotationRepository(), line_repository=SupplierQuotationLineRepository())
        updated = service.update(existing)
        return Response({"data": SupplierQuotationSerializer(updated).data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = SupplierQuotationService(quotation_repository=SupplierQuotationRepository(), line_repository=SupplierQuotationLineRepository())
        success = service.expire(str(instance.id), tenant_id)
        if not success:
            return _error_response("Quotation not found or cannot be expired.", code="QUOTATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": {"expired": True}}, status=status.HTTP_200_OK)


SupplierQuotationDetailView.update.required_permission = "purchasing.quotations.update"
SupplierQuotationDetailView.destroy.required_permission = "purchasing.quotations.delete"


class SupplierQuotationSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.quotations.submit"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = SupplierQuotationService(quotation_repository=SupplierQuotationRepository(), line_repository=SupplierQuotationLineRepository())
        quotation = service.submit(str(pk), tenant_id)
        if not quotation:
            return _error_response("Quotation not found or cannot be submitted.", code="QUOTATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": SupplierQuotationSerializer(quotation).data}, status=status.HTTP_200_OK)


class SupplierQuotationAcceptView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.quotations.accept"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = SupplierQuotationService(quotation_repository=SupplierQuotationRepository(), line_repository=SupplierQuotationLineRepository())
        quotation = service.accept(str(pk), tenant_id)
        if not quotation:
            return _error_response("Quotation not found or cannot be accepted.", code="QUOTATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": SupplierQuotationSerializer(quotation).data}, status=status.HTTP_200_OK)


class SupplierQuotationRejectView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.quotations.reject"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        reason = request.data.get("reason", "")
        service = SupplierQuotationService(quotation_repository=SupplierQuotationRepository(), line_repository=SupplierQuotationLineRepository())
        quotation = service.reject(str(pk), tenant_id, reason)
        if not quotation:
            return _error_response("Quotation not found or cannot be rejected.", code="QUOTATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": SupplierQuotationSerializer(quotation).data}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Purchase Orders
# ──────────────────────────────────────────────


class PurchaseOrderListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.orders.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["order_number", "supplier_id"]
    ordering_fields = ["status", "order_date", "required_delivery_date"]
    ordering = ["-order_date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PurchaseOrderSerializer
        return PurchaseOrderListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return PurchaseOrderModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        order = PurchaseOrder(tenant_id=tenant_id, **serializer.validated_data)
        lines = [PurchaseOrderLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = PurchaseOrderService(order_repository=PurchaseOrderRepository(), line_repository=PurchaseOrderLineRepository())
        created = service.create(order, lines)
        return Response({"data": PurchaseOrderSerializer(created).data}, status=status.HTTP_201_CREATED)


PurchaseOrderListCreateView.create.required_permission = "purchasing.orders.create"


class PurchaseOrderDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.orders.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return PurchaseOrderSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return PurchaseOrderModel.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        existing = PurchaseOrderRepository().get_by_id(str(instance.id), tenant_id)
        if not existing:
            from django.http import Http404
            raise Http404
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)
        service = PurchaseOrderService(order_repository=PurchaseOrderRepository(), line_repository=PurchaseOrderLineRepository())
        updated = service.update(existing)
        return Response({"data": PurchaseOrderSerializer(updated).data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        reason = request.data.get("reason", "")
        service = PurchaseOrderService(order_repository=PurchaseOrderRepository(), line_repository=PurchaseOrderLineRepository())
        success = service.cancel(str(instance.id), tenant_id, reason)
        if not success:
            return _error_response("Order not found or cannot be cancelled.", code="ORDER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": {"cancelled": True}}, status=status.HTTP_200_OK)


PurchaseOrderDetailView.update.required_permission = "purchasing.orders.update"
PurchaseOrderDetailView.destroy.required_permission = "purchasing.orders.delete"


class PurchaseOrderApproveView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.orders.approve"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        approved_by = str(request.actor.id)
        service = PurchaseOrderService(order_repository=PurchaseOrderRepository(), line_repository=PurchaseOrderLineRepository())
        order = service.approve(str(pk), tenant_id, approved_by)
        if not order:
            return _error_response("Order not found or cannot be approved.", code="ORDER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseOrderSerializer(order).data}, status=status.HTTP_200_OK)


class PurchaseOrderSendView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.orders.send"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = PurchaseOrderService(order_repository=PurchaseOrderRepository(), line_repository=PurchaseOrderLineRepository())
        order = service.send_to_supplier(str(pk), tenant_id)
        if not order:
            return _error_response("Order not found or cannot be sent.", code="ORDER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseOrderSerializer(order).data}, status=status.HTTP_200_OK)


class PurchaseOrderAcknowledgeView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.orders.acknowledge"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = PurchaseOrderService(order_repository=PurchaseOrderRepository(), line_repository=PurchaseOrderLineRepository())
        order = service.acknowledge(str(pk), tenant_id)
        if not order:
            return _error_response("Order not found or cannot be acknowledged.", code="ORDER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseOrderSerializer(order).data}, status=status.HTTP_200_OK)


class PurchaseOrderCloseView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.orders.close"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = PurchaseOrderService(order_repository=PurchaseOrderRepository(), line_repository=PurchaseOrderLineRepository())
        order = service.close(str(pk), tenant_id)
        if not order:
            return _error_response("Order not found or cannot be closed.", code="ORDER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseOrderSerializer(order).data}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Goods Receipts
# ──────────────────────────────────────────────


class GoodsReceiptListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.goods_receipts.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["receipt_number", "purchase_order_id"]
    ordering_fields = ["status", "receipt_date", "created_at"]
    ordering = ["-receipt_date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return GoodsReceiptSerializer
        return GoodsReceiptListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return GoodsReceiptModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        receipt = GoodsReceipt(tenant_id=tenant_id, **serializer.validated_data)
        lines = [GoodsReceiptLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = GoodsReceiptService(receipt_repository=GoodsReceiptRepository(), line_repository=GoodsReceiptLineRepository())
        created = service.create(receipt, lines)
        return Response({"data": GoodsReceiptSerializer(created).data}, status=status.HTTP_201_CREATED)


GoodsReceiptListCreateView.create.required_permission = "purchasing.goods_receipts.create"


class GoodsReceiptDetailView(RetrieveAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.goods_receipts.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return GoodsReceiptSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return GoodsReceiptModel.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        existing = GoodsReceiptRepository().get_by_id(str(instance.id), tenant_id)
        if not existing:
            from django.http import Http404
            raise Http404
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)
        service = GoodsReceiptService(receipt_repository=GoodsReceiptRepository(), line_repository=GoodsReceiptLineRepository())
        updated = service.update(existing)
        return Response({"data": GoodsReceiptSerializer(updated).data}, status=status.HTTP_200_OK)


GoodsReceiptDetailView.update.required_permission = "purchasing.goods_receipts.update"


class GoodsReceiptReceiveView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.goods_receipts.receive"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        posted_by = str(request.actor.id)
        service = GoodsReceiptService(receipt_repository=GoodsReceiptRepository(), line_repository=GoodsReceiptLineRepository())
        receipt = service.receive(str(pk), tenant_id, posted_by)
        if not receipt:
            return _error_response("Receipt not found or cannot be posted.", code="RECEIPT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": GoodsReceiptSerializer(receipt).data}, status=status.HTTP_200_OK)


class GoodsReceiptCancelView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.goods_receipts.cancel"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        reason = request.data.get("reason", "")
        service = GoodsReceiptService(receipt_repository=GoodsReceiptRepository(), line_repository=GoodsReceiptLineRepository())
        receipt = service.cancel(str(pk), tenant_id, reason)
        if not receipt:
            return _error_response("Receipt not found or cannot be cancelled.", code="RECEIPT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": GoodsReceiptSerializer(receipt).data}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Purchase Returns
# ──────────────────────────────────────────────


class PurchaseReturnListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.returns.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["return_number", "supplier_id"]
    ordering_fields = ["status", "return_date", "created_at"]
    ordering = ["-return_date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PurchaseReturnSerializer
        return PurchaseReturnListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return PurchaseReturnModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        return_obj = PurchaseReturn(tenant_id=tenant_id, **serializer.validated_data)
        lines = [PurchaseReturnLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = PurchaseReturnService(return_repository=PurchaseReturnRepository(), line_repository=PurchaseReturnLineRepository())
        created = service.create(return_obj, lines)
        return Response({"data": PurchaseReturnSerializer(created).data}, status=status.HTTP_201_CREATED)


PurchaseReturnListCreateView.create.required_permission = "purchasing.returns.create"


class PurchaseReturnDetailView(RetrieveAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.returns.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return PurchaseReturnSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return PurchaseReturnModel.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        existing = PurchaseReturnRepository().get_by_id(str(instance.id), tenant_id)
        if not existing:
            from django.http import Http404
            raise Http404
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)
        service = PurchaseReturnService(return_repository=PurchaseReturnRepository(), line_repository=PurchaseReturnLineRepository())
        updated = service.update(existing)
        return Response({"data": PurchaseReturnSerializer(updated).data}, status=status.HTTP_200_OK)


PurchaseReturnDetailView.update.required_permission = "purchasing.returns.update"


class PurchaseReturnApproveView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.returns.approve"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        approved_by = str(request.actor.id)
        service = PurchaseReturnService(return_repository=PurchaseReturnRepository(), line_repository=PurchaseReturnLineRepository())
        return_obj = service.approve(str(pk), tenant_id, approved_by)
        if not return_obj:
            return _error_response("Return not found or cannot be approved.", code="RETURN_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseReturnSerializer(return_obj).data}, status=status.HTTP_200_OK)


class PurchaseReturnShipView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.returns.ship"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = PurchaseReturnService(return_repository=PurchaseReturnRepository(), line_repository=PurchaseReturnLineRepository())
        return_obj = service.ship(str(pk), tenant_id)
        if not return_obj:
            return _error_response("Return not found or cannot be shipped.", code="RETURN_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseReturnSerializer(return_obj).data}, status=status.HTTP_200_OK)


class PurchaseReturnCreditView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.returns.credit"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = PurchaseReturnService(return_repository=PurchaseReturnRepository(), line_repository=PurchaseReturnLineRepository())
        return_obj = service.receive_credit(str(pk), tenant_id)
        if not return_obj:
            return _error_response("Return not found or cannot be credited.", code="RETURN_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseReturnSerializer(return_obj).data}, status=status.HTTP_200_OK)


class PurchaseReturnCancelView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.returns.cancel"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = PurchaseReturnService(return_repository=PurchaseReturnRepository(), line_repository=PurchaseReturnLineRepository())
        return_obj = service.cancel(str(pk), tenant_id)
        if not return_obj:
            return _error_response("Return not found or cannot be cancelled.", code="RETURN_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": PurchaseReturnSerializer(return_obj).data}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Supplier Price Lists
# ──────────────────────────────────────────────


class SupplierPriceListListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.price_lists.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["supplier_id", "product_id"]
    ordering_fields = ["valid_from", "valid_to", "price"]
    ordering = ["-valid_from"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupplierPriceListSerializer
        return SupplierPriceListListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return SupplierPriceListModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        price_list = SupplierPriceList(tenant_id=tenant_id, **serializer.validated_data)
        service = SupplierPriceListService(price_list_repository=SupplierPriceListRepository())
        created = service.create(price_list)
        return Response({"data": SupplierPriceListSerializer(created).data}, status=status.HTTP_201_CREATED)


SupplierPriceListListCreateView.create.required_permission = "purchasing.price_lists.create"


class SupplierPriceListDetailView(RetrieveAPIView, UpdateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.price_lists.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return SupplierPriceListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return SupplierPriceListModel.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        existing = SupplierPriceListRepository().get_by_id(str(instance.id), tenant_id)
        if not existing:
            from django.http import Http404
            raise Http404
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)
        service = SupplierPriceListService(price_list_repository=SupplierPriceListRepository())
        updated = service.update(existing)
        return Response({"data": SupplierPriceListSerializer(updated).data}, status=status.HTTP_200_OK)


SupplierPriceListDetailView.update.required_permission = "purchasing.price_lists.update"


class SupplierPriceListActivateView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.price_lists.activate"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = SupplierPriceListService(price_list_repository=SupplierPriceListRepository())
        price_list = service.activate(str(pk), tenant_id)
        if not price_list:
            return _error_response("Price list not found or already active.", code="PRICE_LIST_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": SupplierPriceListSerializer(price_list).data}, status=status.HTTP_200_OK)


class SupplierPriceListDeactivateView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "purchasing.price_lists.deactivate"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = SupplierPriceListService(price_list_repository=SupplierPriceListRepository())
        price_list = service.deactivate(str(pk), tenant_id)
        if not price_list:
            return _error_response("Price list not found or already inactive.", code="PRICE_LIST_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": SupplierPriceListSerializer(price_list).data}, status=status.HTTP_200_OK)