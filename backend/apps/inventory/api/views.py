"""
API views for the Inventory module.

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

from apps.inventory.api.serializers import (
    AdjustmentLineSerializer,
    CycleCountLineSerializer,
    CycleCountListSerializer,
    CycleCountSerializer,
    InventoryItemListSerializer,
    InventoryItemSerializer,
    MovementLineSerializer,
    StockAdjustmentListSerializer,
    StockAdjustmentSerializer,
    StockBalanceListSerializer,
    StockBalanceSerializer,
    StockMovementListSerializer,
    StockMovementSerializer,
    StockReservationListSerializer,
    StockReservationSerializer,
    StockTransferListSerializer,
    StockTransferSerializer,
    TransferLineSerializer,
)
from apps.inventory.application.inventory_item_service import InventoryItemService
from apps.inventory.application.stock_balance_service import StockBalanceService
from apps.inventory.application.stock_movement_service import StockMovementService
from apps.inventory.application.stock_adjustment_service import StockAdjustmentService
from apps.inventory.application.stock_transfer_service import StockTransferService
from apps.inventory.application.stock_reservation_service import StockReservationService
from apps.inventory.application.cycle_count_service import CycleCountService
from apps.inventory.domain.entities import (
    AdjustmentLine,
    CycleCount,
    CycleCountLine,
    InventoryItem,
    MovementLine,
    StockAdjustment,
    StockBalance,
    StockMovement,
    StockReservation,
    StockTransfer,
    TransferLine,
)
from apps.inventory.infrastructure.models import (
    AdjustmentLineModel,
    CycleCountLineModel,
    CycleCountModel,
    InventoryItemModel,
    MovementLineModel,
    StockAdjustmentModel,
    StockBalanceModel,
    StockMovementModel,
    StockReservationModel,
    StockTransferModel,
    TransferLineModel,
)
from apps.inventory.infrastructure.repositories import (
    AdjustmentLineRepository,
    CycleCountLineRepository,
    CycleCountRepository,
    InventoryItemRepository,
    MovementLineRepository,
    StockAdjustmentRepository,
    StockBalanceRepository,
    StockMovementRepository,
    StockReservationRepository,
    StockTransferRepository,
    TransferLineRepository,
)
from core.pagination import StandardPagination

logger = logging.getLogger("tradeflow.inventory")


def _error_response(message: str, code: str = "ERROR", status_code: int = status.HTTP_400_BAD_REQUEST) -> Response:
    return Response({"success": False, "error": {"code": code, "message": message}}, status=status_code)


# ──────────────────────────────────────────────
# Inventory Items
# ──────────────────────────────────────────────


class InventoryItemListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.items.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["warehouse_id", "product_id", "batch_number", "serial_number"]
    ordering_fields = ["warehouse_id", "product_id", "quantity_on_hand", "created_at"]
    ordering = ["warehouse_id"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return InventoryItemSerializer
        return InventoryItemListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return InventoryItemModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        item = InventoryItem(tenant_id=tenant_id, **serializer.validated_data)
        service = InventoryItemService(item_repository=InventoryItemRepository())
        created = service.create(item)
        return Response({"data": InventoryItemSerializer(created).data}, status=status.HTTP_201_CREATED)


InventoryItemListCreateView.create.required_permission = "inventory.items.create"


class InventoryItemDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.items.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return InventoryItemSerializer
        return InventoryItemSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return InventoryItemModel.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        existing = InventoryItemRepository().get_by_id(str(instance.id), tenant_id)
        if not existing:
            from django.http import Http404
            raise Http404
        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)
        service = InventoryItemService(item_repository=InventoryItemRepository())
        updated = service.update(existing)
        return Response({"data": InventoryItemSerializer(updated).data}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = InventoryItemService(item_repository=InventoryItemRepository())
        success = service.archive(str(instance.id), tenant_id)
        if not success:
            return _error_response("Inventory item not found.", code="ITEM_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": {"deleted": True}}, status=status.HTTP_200_OK)


InventoryItemDetailView.update.required_permission = "inventory.items.update"
InventoryItemDetailView.destroy.required_permission = "inventory.items.delete"


# ──────────────────────────────────────────────
# Stock Movements
# ──────────────────────────────────────────────


class StockMovementListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.movements.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reference_number", "description"]
    ordering_fields = ["movement_type", "status", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StockMovementSerializer
        return StockMovementListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockMovementModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        movement = StockMovement(tenant_id=tenant_id, **serializer.validated_data)
        lines = [MovementLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = StockMovementService(movement_repository=StockMovementRepository(), line_repository=MovementLineRepository(), item_repository=InventoryItemRepository())
        created = service.create(movement, lines)
        return Response({"data": StockMovementSerializer(created).data}, status=status.HTTP_201_CREATED)


StockMovementListCreateView.create.required_permission = "inventory.movements.create"


class StockMovementDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.movements.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return StockMovementSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockMovementModel.objects.filter(tenant_id=tenant_id)


class StockMovementPostView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.movements.post"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockMovementService(movement_repository=StockMovementRepository(), line_repository=MovementLineRepository(), item_repository=InventoryItemRepository())
        movement = service.post(str(pk), tenant_id)
        if not movement:
            return _error_response("Movement not found or cannot be posted.", code="MOVEMENT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockMovementSerializer(movement).data}, status=status.HTTP_200_OK)


class StockMovementCancelView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.movements.cancel"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockMovementService(movement_repository=StockMovementRepository(), line_repository=MovementLineRepository(), item_repository=InventoryItemRepository())
        success = service.cancel(str(pk), tenant_id)
        if not success:
            return _error_response("Movement not found or cannot be cancelled.", code="MOVEMENT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": {"cancelled": True}}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Stock Adjustments
# ──────────────────────────────────────────────


class StockAdjustmentListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.adjustments.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reason", "reference_number"]
    ordering_fields = ["adjustment_type", "status", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StockAdjustmentSerializer
        return StockAdjustmentListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockAdjustmentModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        adjustment = StockAdjustment(tenant_id=tenant_id, **serializer.validated_data)
        lines = [AdjustmentLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = StockAdjustmentService(adjustment_repository=StockAdjustmentRepository(), line_repository=AdjustmentLineRepository(), movement_repository=StockMovementRepository(), item_repository=InventoryItemRepository())
        created = service.create(adjustment, lines)
        return Response({"data": StockAdjustmentSerializer(created).data}, status=status.HTTP_201_CREATED)


StockAdjustmentListCreateView.create.required_permission = "inventory.adjustments.create"


class StockAdjustmentDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.adjustments.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return StockAdjustmentSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockAdjustmentModel.objects.filter(tenant_id=tenant_id)


class StockAdjustmentPostView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.adjustments.post"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        approved_by = str(request.actor.id)
        service = StockAdjustmentService(adjustment_repository=StockAdjustmentRepository(), line_repository=AdjustmentLineRepository(), movement_repository=StockMovementRepository(), item_repository=InventoryItemRepository())
        adjustment = service.post(str(pk), tenant_id, approved_by)
        if not adjustment:
            return _error_response("Adjustment not found or cannot be posted.", code="ADJUSTMENT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockAdjustmentSerializer(adjustment).data}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Stock Transfers
# ──────────────────────────────────────────────


class StockTransferListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.transfers.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reference_number", "description"]
    ordering_fields = ["status", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StockTransferSerializer
        return StockTransferListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockTransferModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        transfer = StockTransfer(tenant_id=tenant_id, **serializer.validated_data)
        lines = [TransferLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = StockTransferService(transfer_repository=StockTransferRepository(), line_repository=TransferLineRepository(), movement_repository=StockMovementRepository(), item_repository=InventoryItemRepository())
        created = service.create(transfer, lines)
        return Response({"data": StockTransferSerializer(created).data}, status=status.HTTP_201_CREATED)


StockTransferListCreateView.create.required_permission = "inventory.transfers.create"


class StockTransferDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.transfers.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return StockTransferSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockTransferModel.objects.filter(tenant_id=tenant_id)


class StockTransferShipView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.transfers.ship"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockTransferService(transfer_repository=StockTransferRepository(), line_repository=TransferLineRepository(), movement_repository=StockMovementRepository(), item_repository=InventoryItemRepository())
        transfer = service.ship(str(pk), tenant_id)
        if not transfer:
            return _error_response("Transfer not found or cannot be shipped.", code="TRANSFER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockTransferSerializer(transfer).data}, status=status.HTTP_200_OK)


class StockTransferReceiveView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.transfers.receive"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockTransferService(transfer_repository=StockTransferRepository(), line_repository=TransferLineRepository(), movement_repository=StockMovementRepository(), item_repository=InventoryItemRepository())
        transfer = service.receive(str(pk), tenant_id)
        if not transfer:
            return _error_response("Transfer not found or cannot be received.", code="TRANSFER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockTransferSerializer(transfer).data}, status=status.HTTP_200_OK)


class StockTransferCancelView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.transfers.cancel"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockTransferService(transfer_repository=StockTransferRepository(), line_repository=TransferLineRepository(), movement_repository=StockMovementRepository(), item_repository=InventoryItemRepository())
        success = service.cancel(str(pk), tenant_id)
        if not success:
            return _error_response("Transfer not found or cannot be cancelled.", code="TRANSFER_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": {"cancelled": True}}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Stock Reservations
# ──────────────────────────────────────────────


class StockReservationListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.reservations.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reference_type", "reference_id"]
    ordering_fields = ["status", "created_at"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StockReservationSerializer
        return StockReservationListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockReservationModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        reservation = StockReservation(tenant_id=tenant_id, **serializer.validated_data)
        service = StockReservationService(reservation_repository=StockReservationRepository(), item_repository=InventoryItemRepository())
        created = service.create(reservation)
        return Response({"data": StockReservationSerializer(created).data}, status=status.HTTP_201_CREATED)


StockReservationListCreateView.create.required_permission = "inventory.reservations.create"


class StockReservationDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.reservations.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return StockReservationSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockReservationModel.objects.filter(tenant_id=tenant_id)


class StockReservationAllocateView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.reservations.allocate"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        quantity_allocated = request.data.get("quantity_allocated")
        if quantity_allocated is None:
            return _error_response("quantity_allocated is required.", code="VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
        service = StockReservationService(reservation_repository=StockReservationRepository(), item_repository=InventoryItemRepository())
        reservation = service.allocate(str(pk), tenant_id, float(quantity_allocated))
        if not reservation:
            return _error_response("Reservation not found or cannot be allocated.", code="RESERVATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockReservationSerializer(reservation).data}, status=status.HTTP_200_OK)


class StockReservationReleaseView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.reservations.release"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockReservationService(reservation_repository=StockReservationRepository(), item_repository=InventoryItemRepository())
        reservation = service.release(str(pk), tenant_id)
        if not reservation:
            return _error_response("Reservation not found or cannot be released.", code="RESERVATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockReservationSerializer(reservation).data}, status=status.HTTP_200_OK)


class StockReservationCompleteView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.reservations.complete"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockReservationService(reservation_repository=StockReservationRepository(), item_repository=InventoryItemRepository())
        reservation = service.complete(str(pk), tenant_id)
        if not reservation:
            return _error_response("Reservation not found or cannot be completed.", code="RESERVATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockReservationSerializer(reservation).data}, status=status.HTTP_200_OK)


class StockReservationCancelView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.reservations.cancel"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = StockReservationService(reservation_repository=StockReservationRepository(), item_repository=InventoryItemRepository())
        reservation = service.cancel(str(pk), tenant_id)
        if not reservation:
            return _error_response("Reservation not found or cannot be cancelled.", code="RESERVATION_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": StockReservationSerializer(reservation).data}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Cycle Counts
# ──────────────────────────────────────────────


class CycleCountListCreateView(ListAPIView, CreateAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.cycle_counts.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["reference_number", "notes"]
    ordering_fields = ["scheduled_date", "status", "created_at"]
    ordering = ["-scheduled_date"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CycleCountSerializer
        return CycleCountListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return CycleCountModel.objects.filter(tenant_id=tenant_id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tenant_id = request.actor.tenant_id
        cycle_count = CycleCount(tenant_id=tenant_id, **serializer.validated_data)
        lines = [CycleCountLine(tenant_id=tenant_id, **line) for line in request.data.get("lines", [])]
        service = CycleCountService(cycle_count_repository=CycleCountRepository(), line_repository=CycleCountLineRepository(), adjustment_repository=StockAdjustmentRepository(), adjustment_line_repository=AdjustmentLineRepository(), item_repository=InventoryItemRepository())
        created = service.create(cycle_count, lines)
        return Response({"data": CycleCountSerializer(created).data}, status=status.HTTP_201_CREATED)


CycleCountListCreateView.create.required_permission = "inventory.cycle_counts.create"


class CycleCountDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.cycle_counts.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        return CycleCountSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return CycleCountModel.objects.filter(tenant_id=tenant_id)


class CycleCountStartView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.cycle_counts.start"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = CycleCountService(cycle_count_repository=CycleCountRepository(), line_repository=CycleCountLineRepository(), adjustment_repository=StockAdjustmentRepository(), adjustment_line_repository=AdjustmentLineRepository(), item_repository=InventoryItemRepository())
        cycle_count = service.start(str(pk), tenant_id)
        if not cycle_count:
            return _error_response("Cycle count not found or cannot be started.", code="CYCLE_COUNT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": CycleCountSerializer(cycle_count).data}, status=status.HTTP_200_OK)


class CycleCountCompleteView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.cycle_counts.complete"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        verified_by = str(request.actor.id)
        service = CycleCountService(cycle_count_repository=CycleCountRepository(), line_repository=CycleCountLineRepository(), adjustment_repository=StockAdjustmentRepository(), adjustment_line_repository=AdjustmentLineRepository(), item_repository=InventoryItemRepository())
        cycle_count = service.complete(str(pk), tenant_id, verified_by)
        if not cycle_count:
            return _error_response("Cycle count not found or cannot be completed.", code="CYCLE_COUNT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": CycleCountSerializer(cycle_count).data}, status=status.HTTP_200_OK)


class CycleCountRecordLineView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.cycle_counts.record_line"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        serializer = CycleCountLineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = CycleCountService(cycle_count_repository=CycleCountRepository(), line_repository=CycleCountLineRepository(), adjustment_repository=StockAdjustmentRepository(), adjustment_line_repository=AdjustmentLineRepository(), item_repository=InventoryItemRepository())
        line = service.record_line(str(pk), tenant_id, CycleCountLine(tenant_id=tenant_id, **serializer.validated_data))
        if not line:
            return _error_response("Cycle count not found or not in progress.", code="CYCLE_COUNT_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)
        return Response({"data": CycleCountLineSerializer(line).data}, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────────
# Stock Balances
# ──────────────────────────────────────────────


class StockBalanceListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.balances.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["product_id", "warehouse_id"]
    ordering_fields = ["snapshot_date", "quantity_on_hand"]
    ordering = ["-snapshot_date"]

    def get_serializer_class(self):
        return StockBalanceListSerializer

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return StockBalanceModel.objects.filter(tenant_id=tenant_id)


class StockBalanceGenerateView(APIView):
    permission_classes = [IsAuthenticated]
    required_permission = "inventory.balances.generate"

    def post(self, request):
        tenant_id = request.actor.tenant_id
        warehouse_id = request.data.get("warehouse_id")
        snapshot_date = request.data.get("snapshot_date", "")
        if not warehouse_id:
            return _error_response("warehouse_id is required.", code="VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
        service = StockBalanceService(balance_repository=StockBalanceRepository(), item_repository=InventoryItemRepository())
        snapshots = service.generate_daily_snapshot(tenant_id, warehouse_id, snapshot_date)
        return Response({"data": StockBalanceListSerializer(snapshots, many=True).data}, status=status.HTTP_201_CREATED)