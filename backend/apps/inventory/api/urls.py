"""
URL routing for the Inventory module API.

Registered under the API root as:
    path("api/v1/inventory/", include("apps.inventory.api.urls"))
"""

from django.urls import path

from apps.inventory.api.views import (
    CycleCountCompleteView,
    CycleCountDetailView,
    CycleCountListCreateView,
    CycleCountRecordLineView,
    CycleCountStartView,
    InventoryItemDetailView,
    InventoryItemListCreateView,
    StockAdjustmentDetailView,
    StockAdjustmentListCreateView,
    StockAdjustmentPostView,
    StockBalanceGenerateView,
    StockBalanceListView,
    StockMovementCancelView,
    StockMovementDetailView,
    StockMovementListCreateView,
    StockMovementPostView,
    StockReservationAllocateView,
    StockReservationCancelView,
    StockReservationCompleteView,
    StockReservationDetailView,
    StockReservationListCreateView,
    StockReservationReleaseView,
    StockTransferCancelView,
    StockTransferDetailView,
    StockTransferListCreateView,
    StockTransferReceiveView,
    StockTransferShipView,
)

urlpatterns = [
    # Inventory Items
    path("items/", InventoryItemListCreateView.as_view(), name="inventory-item-list"),
    path("items/<str:pk>/", InventoryItemDetailView.as_view(), name="inventory-item-detail"),
    path("warehouse/<str:warehouse_id>/inventory/", InventoryItemListCreateView.as_view(), name="warehouse-inventory"),
    path("product/<str:product_id>/inventory/", InventoryItemListCreateView.as_view(), name="product-inventory"),
    # Stock Movements
    path("movements/", StockMovementListCreateView.as_view(), name="stock-movement-list"),
    path("movements/<str:pk>/", StockMovementDetailView.as_view(), name="stock-movement-detail"),
    path("movements/<str:pk>/post/", StockMovementPostView.as_view(), name="stock-movement-post"),
    path("movements/<str:pk>/cancel/", StockMovementCancelView.as_view(), name="stock-movement-cancel"),
    # Stock Adjustments
    path("adjustments/", StockAdjustmentListCreateView.as_view(), name="stock-adjustment-list"),
    path("adjustments/<str:pk>/", StockAdjustmentDetailView.as_view(), name="stock-adjustment-detail"),
    path("adjustments/<str:pk>/post/", StockAdjustmentPostView.as_view(), name="stock-adjustment-post"),
    # Stock Transfers
    path("transfers/", StockTransferListCreateView.as_view(), name="stock-transfer-list"),
    path("transfers/<str:pk>/", StockTransferDetailView.as_view(), name="stock-transfer-detail"),
    path("transfers/<str:pk>/ship/", StockTransferShipView.as_view(), name="stock-transfer-ship"),
    path("transfers/<str:pk>/receive/", StockTransferReceiveView.as_view(), name="stock-transfer-receive"),
    path("transfers/<str:pk>/cancel/", StockTransferCancelView.as_view(), name="stock-transfer-cancel"),
    # Reservations
    path("reservations/", StockReservationListCreateView.as_view(), name="stock-reservation-list"),
    path("reservations/<str:pk>/", StockReservationDetailView.as_view(), name="stock-reservation-detail"),
    path("reservations/<str:pk>/allocate/", StockReservationAllocateView.as_view(), name="stock-reservation-allocate"),
    path("reservations/<str:pk>/release/", StockReservationReleaseView.as_view(), name="stock-reservation-release"),
    path("reservations/<str:pk>/complete/", StockReservationCompleteView.as_view(), name="stock-reservation-complete"),
    path("reservations/<str:pk>/cancel/", StockReservationCancelView.as_view(), name="stock-reservation-cancel"),
    # Cycle Counts
    path("cycle-counts/", CycleCountListCreateView.as_view(), name="cycle-count-list"),
    path("cycle-counts/<str:pk>/", CycleCountDetailView.as_view(), name="cycle-count-detail"),
    path("cycle-counts/<str:pk>/start/", CycleCountStartView.as_view(), name="cycle-count-start"),
    path("cycle-counts/<str:pk>/complete/", CycleCountCompleteView.as_view(), name="cycle-count-complete"),
    path("cycle-counts/<str:pk>/record-line/", CycleCountRecordLineView.as_view(), name="cycle-count-record-line"),
    # Stock Balances
    path("balances/", StockBalanceListView.as_view(), name="stock-balance-list"),
    path("balances/generate/", StockBalanceGenerateView.as_view(), name="stock-balance-generate"),
]