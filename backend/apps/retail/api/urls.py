"""
API URL routing for the Retail module.

Per Software Architecture §5.1: Versioned from day one (/v1/).
Mounted at /api/v1/retail/ in config/api_urls.py.
"""

from django.urls import path

from apps.retail.api.views import (
    BrandDetailView,
    BrandListCreateView,
    CategoryDetailView,
    CategoryListCreateView,
    CategoryTreeView,
    ProductActivateView,
    ProductBarcodeDetailView,
    ProductBarcodeListCreateView,
    ProductByBarcodeView,
    ProductBySkuView,
    ProductDeactivateView,
    ProductDetailView,
    ProductImageDetailView,
    ProductImageListCreateView,
    ProductImageSetPrimaryView,
    ProductListCreateView,
    ProductVariantDetailView,
    ProductVariantListCreateView,
    SupplierDetailView,
    SupplierListCreateView,
    SupplierProductDetailView,
    SupplierProductListCreateView,
    SupplierProductSetPreferredView,
    UnitOfMeasureDetailView,
    UnitOfMeasureListCreateView,
)

urlpatterns = [
    # Units of Measure
    path("units/", UnitOfMeasureListCreateView.as_view(), name="unit-list-create"),
    path(
        "units/<uuid:pk>/",
        UnitOfMeasureDetailView.as_view(),
        name="unit-detail",
    ),
    # Brands
    path("brands/", BrandListCreateView.as_view(), name="brand-list-create"),
    path(
        "brands/<uuid:pk>/",
        BrandDetailView.as_view(),
        name="brand-detail",
    ),
    # Categories
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path(
        "categories/<uuid:pk>/",
        CategoryDetailView.as_view(),
        name="category-detail",
    ),
    path(
        "categories/tree/",
        CategoryTreeView.as_view(),
        name="category-tree",
    ),
    # Products
    path("products/", ProductListCreateView.as_view(), name="product-list-create"),
    path(
        "products/<uuid:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "products/<uuid:pk>/activate/",
        ProductActivateView.as_view(),
        name="product-activate",
    ),
    path(
        "products/<uuid:pk>/deactivate/",
        ProductDeactivateView.as_view(),
        name="product-deactivate",
    ),
    path(
        "products/sku/<str:sku>/",
        ProductBySkuView.as_view(),
        name="product-by-sku",
    ),
    path(
        "products/barcode/<str:barcode>/",
        ProductByBarcodeView.as_view(),
        name="product-by-barcode",
    ),
    # Product Variants (nested under products)
    path(
        "products/<uuid:product_id>/variants/",
        ProductVariantListCreateView.as_view(),
        name="product-variant-list-create",
    ),
    path(
        "products/<uuid:product_id>/variants/<uuid:pk>/",
        ProductVariantDetailView.as_view(),
        name="product-variant-detail",
    ),
    # Product Images (nested under products)
    path(
        "products/<uuid:product_id>/images/",
        ProductImageListCreateView.as_view(),
        name="product-image-list-create",
    ),
    path(
        "products/<uuid:product_id>/images/<uuid:pk>/",
        ProductImageDetailView.as_view(),
        name="product-image-detail",
    ),
    path(
        "products/<uuid:product_id>/images/<uuid:pk>/primary/",
        ProductImageSetPrimaryView.as_view(),
        name="product-image-set-primary",
    ),
    # Product Barcodes (nested under products)
    path(
        "products/<uuid:product_id>/barcodes/",
        ProductBarcodeListCreateView.as_view(),
        name="product-barcode-list-create",
    ),
    path(
        "products/<uuid:product_id>/barcodes/<uuid:pk>/",
        ProductBarcodeDetailView.as_view(),
        name="product-barcode-detail",
    ),
    # Suppliers
    path("suppliers/", SupplierListCreateView.as_view(), name="supplier-list-create"),
    path(
        "suppliers/<uuid:pk>/",
        SupplierDetailView.as_view(),
        name="supplier-detail",
    ),
    # Supplier Products (nested under suppliers)
    path(
        "suppliers/<uuid:supplier_id>/products/",
        SupplierProductListCreateView.as_view(),
        name="supplier-product-list-create",
    ),
    path(
        "suppliers/<uuid:supplier_id>/products/<uuid:pk>/",
        SupplierProductDetailView.as_view(),
        name="supplier-product-detail",
    ),
    path(
        "suppliers/<uuid:supplier_id>/products/<uuid:pk>/preferred/",
        SupplierProductSetPreferredView.as_view(),
        name="supplier-product-set-preferred",
    ),
]