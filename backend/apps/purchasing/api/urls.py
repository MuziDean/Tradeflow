"""URL routing for the Purchasing API."""

from django.urls import path

from apps.purchasing.api.views import (
    GoodsReceiptCancelView,
    GoodsReceiptDetailView,
    GoodsReceiptListCreateView,
    GoodsReceiptReceiveView,
    PurchaseOrderAcknowledgeView,
    PurchaseOrderApproveView,
    PurchaseOrderCloseView,
    PurchaseOrderDetailView,
    PurchaseOrderListCreateView,
    PurchaseOrderSendView,
    PurchaseRequisitionApproveView,
    PurchaseRequisitionConvertView,
    PurchaseRequisitionDetailView,
    PurchaseRequisitionListCreateView,
    PurchaseRequisitionRejectView,
    PurchaseRequisitionSubmitView,
    PurchaseReturnApproveView,
    PurchaseReturnCancelView,
    PurchaseReturnCreditView,
    PurchaseReturnDetailView,
    PurchaseReturnListCreateView,
    PurchaseReturnShipView,
    SupplierPriceListActivateView,
    SupplierPriceListDeactivateView,
    SupplierPriceListDetailView,
    SupplierPriceListListCreateView,
    SupplierQuotationAcceptView,
    SupplierQuotationDetailView,
    SupplierQuotationListCreateView,
    SupplierQuotationRejectView,
    SupplierQuotationSubmitView,
)

urlpatterns = [
    # Purchase Requisitions
    path("requisitions/", PurchaseRequisitionListCreateView.as_view(), name="purchasing-requisition-list"),
    path("requisitions/<uuid:pk>/", PurchaseRequisitionDetailView.as_view(), name="purchasing-requisition-detail"),
    path("requisitions/<uuid:pk>/submit/", PurchaseRequisitionSubmitView.as_view(), name="purchasing-requisition-submit"),
    path("requisitions/<uuid:pk>/approve/", PurchaseRequisitionApproveView.as_view(), name="purchasing-requisition-approve"),
    path("requisitions/<uuid:pk>/reject/", PurchaseRequisitionRejectView.as_view(), name="purchasing-requisition-reject"),
    path("requisitions/<uuid:pk>/convert/", PurchaseRequisitionConvertView.as_view(), name="purchasing-requisition-convert"),
    # Supplier Quotations
    path("quotations/", SupplierQuotationListCreateView.as_view(), name="purchasing-quotation-list"),
    path("quotations/<uuid:pk>/", SupplierQuotationDetailView.as_view(), name="purchasing-quotation-detail"),
    path("quotations/<uuid:pk>/submit/", SupplierQuotationSubmitView.as_view(), name="purchasing-quotation-submit"),
    path("quotations/<uuid:pk>/accept/", SupplierQuotationAcceptView.as_view(), name="purchasing-quotation-accept"),
    path("quotations/<uuid:pk>/reject/", SupplierQuotationRejectView.as_view(), name="purchasing-quotation-reject"),
    # Purchase Orders
    path("orders/", PurchaseOrderListCreateView.as_view(), name="purchasing-order-list"),
    path("orders/<uuid:pk>/", PurchaseOrderDetailView.as_view(), name="purchasing-order-detail"),
    path("orders/<uuid:pk>/approve/", PurchaseOrderApproveView.as_view(), name="purchasing-order-approve"),
    path("orders/<uuid:pk>/send/", PurchaseOrderSendView.as_view(), name="purchasing-order-send"),
    path("orders/<uuid:pk>/acknowledge/", PurchaseOrderAcknowledgeView.as_view(), name="purchasing-order-acknowledge"),
    path("orders/<uuid:pk>/close/", PurchaseOrderCloseView.as_view(), name="purchasing-order-close"),
    # Goods Receipts
    path("goods-receipts/", GoodsReceiptListCreateView.as_view(), name="purchasing-goods-receipt-list"),
    path("goods-receipts/<uuid:pk>/", GoodsReceiptDetailView.as_view(), name="purchasing-goods-receipt-detail"),
    path("goods-receipts/<uuid:pk>/receive/", GoodsReceiptReceiveView.as_view(), name="purchasing-goods-receipt-receive"),
    path("goods-receipts/<uuid:pk>/cancel/", GoodsReceiptCancelView.as_view(), name="purchasing-goods-receipt-cancel"),
    # Purchase Returns
    path("returns/", PurchaseReturnListCreateView.as_view(), name="purchasing-return-list"),
    path("returns/<uuid:pk>/", PurchaseReturnDetailView.as_view(), name="purchasing-return-detail"),
    path("returns/<uuid:pk>/approve/", PurchaseReturnApproveView.as_view(), name="purchasing-return-approve"),
    path("returns/<uuid:pk>/ship/", PurchaseReturnShipView.as_view(), name="purchasing-return-ship"),
    path("returns/<uuid:pk>/credit/", PurchaseReturnCreditView.as_view(), name="purchasing-return-credit"),
    path("returns/<uuid:pk>/cancel/", PurchaseReturnCancelView.as_view(), name="purchasing-return-cancel"),
    # Supplier Price Lists
    path("price-lists/", SupplierPriceListListCreateView.as_view(), name="purchasing-price-list-list"),
    path("price-lists/<uuid:pk>/", SupplierPriceListDetailView.as_view(), name="purchasing-price-list-detail"),
    path("price-lists/<uuid:pk>/activate/", SupplierPriceListActivateView.as_view(), name="purchasing-price-list-activate"),
    path("price-lists/<uuid:pk>/deactivate/", SupplierPriceListDeactivateView.as_view(), name="purchasing-price-list-deactivate"),
]