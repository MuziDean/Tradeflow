"""
API views for the Retail module.

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

from apps.retail.api.serializers import (
    BrandListSerializer,
    BrandSerializer,
    CategoryListSerializer,
    CategorySerializer,
    ProductBarcodeListSerializer,
    ProductBarcodeSerializer,
    ProductImageListSerializer,
    ProductImageSerializer,
    ProductListSerializer,
    ProductSerializer,
    ProductVariantListSerializer,
    ProductVariantSerializer,
    SupplierListSerializer,
    SupplierProductListSerializer,
    SupplierProductSerializer,
    SupplierSerializer,
    UnitOfMeasureListSerializer,
    UnitOfMeasureSerializer,
)
from apps.retail.application.brand_service import BrandService
from apps.retail.application.category_service import ProductCategoryService
from apps.retail.application.product_barcode_service import ProductBarcodeService
from apps.retail.application.product_image_service import ProductImageService
from apps.retail.application.product_service import ProductService
from apps.retail.application.product_variant_service import ProductVariantService
from apps.retail.application.supplier_product_service import SupplierProductService
from apps.retail.application.supplier_service import SupplierService
from apps.retail.application.unit_of_measure_service import UnitOfMeasureService
from apps.retail.domain.entities import (
    Brand as BrandEntity,
    ProductCategory as CategoryEntity,
    Product as ProductEntity,
    ProductVariant as ProductVariantEntity,
    ProductImage as ProductImageEntity,
    ProductBarcode as ProductBarcodeEntity,
    Supplier as SupplierEntity,
    SupplierProduct as SupplierProductEntity,
    UnitOfMeasure as UnitOfMeasureEntity,
)
from apps.retail.infrastructure.models import (
    Brand,
    Product,
    ProductBarcode,
    ProductCategory,
    ProductImage,
    ProductVariant,
    Supplier,
    SupplierProduct,
    UnitOfMeasure,
)
from apps.retail.infrastructure.repositories import (
    BrandRepository,
    ProductBarcodeRepository,
    ProductCategoryRepository,
    ProductImageRepository,
    ProductRepository,
    ProductVariantRepository,
    SupplierProductRepository,
    SupplierRepository,
    UnitOfMeasureRepository,
)
from core.pagination import StandardPagination

logger = logging.getLogger("tradeflow.retail")


def _error_response(
    message: str,
    code: str = "ERROR",
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    """Standard error response using the API envelope format."""
    return Response(
        {"success": False, "error": {"code": code, "message": message}},
        status=status_code,
    )


# ──────────────────────────────────────────────
# Unit of Measure
# ──────────────────────────────────────────────


class UnitOfMeasureListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of units of measure.

    post: Creates a new unit of measure.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.units.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "symbol", "unit_type"]
    ordering_fields = ["name", "symbol", "unit_type", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UnitOfMeasureSerializer
        return UnitOfMeasureListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return UnitOfMeasure.objects.filter(tenant_id=tenant_id).order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        unit = UnitOfMeasureEntity(
            tenant_id=tenant_id,
            **serializer.validated_data,
        )

        service = UnitOfMeasureService(unit_of_measure_repository=UnitOfMeasureRepository())
        created = service.create(unit)

        return Response(
            {"data": UnitOfMeasureSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


UnitOfMeasureListCreateView.create.required_permission = "retail.units.create"


class UnitOfMeasureDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific unit of measure.

    put: Updates a specific unit of measure.

    delete: Deletes a specific unit of measure.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.units.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return UnitOfMeasureSerializer
        return UnitOfMeasureSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return UnitOfMeasure.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        unit_id = str(instance.id)
        existing = UnitOfMeasureRepository().get_by_id(unit_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        service = UnitOfMeasureService(unit_of_measure_repository=UnitOfMeasureRepository())
        updated = service.update(existing)

        return Response(
            {"data": UnitOfMeasureSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = UnitOfMeasureService(unit_of_measure_repository=UnitOfMeasureRepository())
        service.soft_delete(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


UnitOfMeasureDetailView.update.required_permission = "retail.units.update"
UnitOfMeasureDetailView.destroy.required_permission = "retail.units.delete"


# ──────────────────────────────────────────────
# Brands
# ──────────────────────────────────────────────


class BrandListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of brands.

    post: Creates a new brand.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.brands.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "website"]
    ordering_fields = ["name", "created_at", "is_active"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return BrandSerializer
        return BrandListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return Brand.objects.filter(tenant_id=tenant_id).order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        brand = BrandEntity(
            tenant_id=tenant_id,
            **serializer.validated_data,
        )

        service = BrandService(brand_repository=BrandRepository())
        created = service.create(brand)

        return Response(
            {"data": BrandSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


BrandListCreateView.create.required_permission = "retail.brands.create"


class BrandDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific brand.

    put: Updates a specific brand.

    delete: Soft-deletes a specific brand.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.brands.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return BrandSerializer
        return BrandSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return Brand.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        brand_id = str(instance.id)
        existing = BrandRepository().get_by_id(brand_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        service = BrandService(brand_repository=BrandRepository())
        updated = service.update(existing)

        return Response(
            {"data": BrandSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = BrandService(brand_repository=BrandRepository())
        service.archive(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


BrandDetailView.update.required_permission = "retail.brands.update"
BrandDetailView.destroy.required_permission = "retail.brands.delete"


# ──────────────────────────────────────────────
# Categories
# ──────────────────────────────────────────────


class CategoryListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of categories.

    post: Creates a new category.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.categories.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "sort_order", "created_at"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CategorySerializer
        return CategoryListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return ProductCategory.objects.filter(tenant_id=tenant_id).order_by("sort_order")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        category = CategoryEntity(
            tenant_id=tenant_id,
            **serializer.validated_data,
        )

        service = ProductCategoryService(category_repository=ProductCategoryRepository())
        created = service.create(category)

        return Response(
            {"data": CategorySerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


CategoryListCreateView.create.required_permission = "retail.categories.create"


class CategoryDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific category.

    put: Updates a specific category.

    delete: Soft-deletes a specific category.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.categories.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return CategorySerializer
        return CategorySerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return ProductCategory.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        category_id = str(instance.id)
        existing = ProductCategoryRepository().get_by_id(category_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        service = ProductCategoryService(category_repository=ProductCategoryRepository())
        updated = service.update(existing)

        return Response(
            {"data": CategorySerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = ProductCategoryService(category_repository=ProductCategoryRepository())
        service.archive(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


CategoryDetailView.update.required_permission = "retail.categories.update"
CategoryDetailView.destroy.required_permission = "retail.categories.delete"


class CategoryTreeView(APIView):
    """
    get: Returns the full category tree.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.categories.read"

    def get(self, request):
        tenant_id = request.actor.tenant_id
        categories = ProductCategory.objects.filter(tenant_id=tenant_id).order_by("sort_order")
        serializer = CategoryListSerializer(categories, many=True)
        return Response({"data": serializer.data})


# ──────────────────────────────────────────────
# Products
# ──────────────────────────────────────────────


class ProductListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of products.

    post: Creates a new product.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "sku", "barcode"]
    ordering_fields = ["name", "sku", "created_at", "is_active"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductSerializer
        return ProductListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return Product.objects.filter(tenant_id=tenant_id).order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        product = ProductEntity(
            tenant_id=tenant_id,
            **serializer.validated_data,
        )

        service = ProductService(product_repository=ProductRepository())
        created = service.create(product)

        return Response(
            {"data": ProductSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


ProductListCreateView.create.required_permission = "retail.products.create"


class ProductDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific product.

    put: Updates a specific product.

    delete: Soft-deletes a specific product.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return ProductSerializer
        return ProductSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return Product.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        product_id = str(instance.id)
        existing = ProductRepository().get_by_id(product_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        service = ProductService(product_repository=ProductRepository())
        updated = service.update(existing)

        return Response(
            {"data": ProductSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = ProductService(product_repository=ProductRepository())
        service.archive(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


ProductDetailView.update.required_permission = "retail.products.update"
ProductDetailView.destroy.required_permission = "retail.products.delete"


class ProductActivateView(APIView):
    """
    post: Activates a product.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.update"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = ProductService(product_repository=ProductRepository())
        activated = service.activate(pk, tenant_id)
        if not activated:
            return _error_response(
                "Product not found.",
                code="PRODUCT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"data": ProductSerializer(activated).data},
            status=status.HTTP_200_OK,
        )


class ProductDeactivateView(APIView):
    """
    post: Deactivates a product.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.update"

    def post(self, request, pk=None):
        tenant_id = request.actor.tenant_id
        service = ProductService(product_repository=ProductRepository())
        deactivated = service.deactivate(pk, tenant_id)
        if not deactivated:
            return _error_response(
                "Product not found.",
                code="PRODUCT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response(
            {"data": ProductSerializer(deactivated).data},
            status=status.HTTP_200_OK,
        )


class ProductBySkuView(APIView):
    """
    get: Returns product by SKU.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"

    def get(self, request, sku=None):
        tenant_id = request.actor.tenant_id
        service = ProductService(product_repository=ProductRepository())
        product = service.get_by_sku(sku, tenant_id)
        if not product:
            return _error_response(
                "Product not found.",
                code="PRODUCT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": ProductSerializer(product).data})


class ProductByBarcodeView(APIView):
    """
    get: Returns product by barcode.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"

    def get(self, request, barcode=None):
        tenant_id = request.actor.tenant_id
        service = ProductService(product_repository=ProductRepository())
        product = service.get_by_barcode(barcode, tenant_id)
        if not product:
            return _error_response(
                "Product not found.",
                code="PRODUCT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": ProductSerializer(product).data})


# ──────────────────────────────────────────────
# Product Variants
# ──────────────────────────────────────────────


class ProductVariantListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of variants for a product.

    post: Creates a new variant for a product.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["sku", "name"]
    ordering_fields = ["sku", "name", "created_at"]
    ordering = ["sku"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductVariantSerializer
        return ProductVariantListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        return ProductVariant.objects.filter(tenant_id=tenant_id, product_id=product_id).order_by("sku")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        variant = ProductVariantEntity(
            tenant_id=tenant_id,
            product_id=product_id,
            **serializer.validated_data,
        )

        service = ProductVariantService(variant_repository=ProductVariantRepository())
        created = service.create(variant)

        return Response(
            {"data": ProductVariantSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


ProductVariantListCreateView.create.required_permission = "retail.products.create"


class ProductVariantDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific variant.

    put: Updates a specific variant.

    delete: Soft-deletes a specific variant.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return ProductVariantSerializer
        return ProductVariantSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        return ProductVariant.objects.filter(tenant_id=tenant_id, product_id=product_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        variant_id = str(instance.id)
        existing = ProductVariantRepository().get_by_id(variant_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        service = ProductVariantService(variant_repository=ProductVariantRepository())
        updated = service.update(existing)

        return Response(
            {"data": ProductVariantSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = ProductVariantService(variant_repository=ProductVariantRepository())
        service.archive(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


ProductVariantDetailView.update.required_permission = "retail.products.update"
ProductVariantDetailView.destroy.required_permission = "retail.products.delete"


# ──────────────────────────────────────────────
# Product Images
# ──────────────────────────────────────────────


class ProductImageListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of images for a product.

    post: Adds a new image to a product.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["original_filename", "mime_type"]
    ordering_fields = ["sort_order", "created_at", "is_primary"]
    ordering = ["sort_order"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductImageSerializer
        return ProductImageListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        return ProductImage.objects.filter(tenant_id=tenant_id, product_id=product_id).order_by("sort_order")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        image = ProductImageEntity(
            tenant_id=tenant_id,
            product_id=product_id,
            **serializer.validated_data,
        )

        service = ProductImageService(image_repository=ProductImageRepository())
        created = service.add_image(image)

        return Response(
            {"data": ProductImageSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


ProductImageListCreateView.create.required_permission = "retail.products.create"


class ProductImageDetailView(DestroyAPIView):
    """
    delete: Removes a product image.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.delete"
    lookup_field = "pk"

    def get_serializer_class(self):
        return ProductImageSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        return ProductImage.objects.filter(tenant_id=tenant_id, product_id=product_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = ProductImageService(image_repository=ProductImageRepository())
        service.remove_image(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


class ProductImageSetPrimaryView(APIView):
    """
    post: Sets a product image as primary.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.update"

    def post(self, request, product_id=None, pk=None):
        tenant_id = request.actor.tenant_id
        service = ProductImageService(image_repository=ProductImageRepository())
        success = service.set_primary(pk, tenant_id, product_id)
        if not success:
            return _error_response(
                "Image not found.",
                code="IMAGE_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": {"primary_set": True}}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────────
# Product Barcodes
# ──────────────────────────────────────────────


class ProductBarcodeListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of barcodes for a product.

    post: Assigns a new barcode to a product.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["barcode", "barcode_type"]
    ordering_fields = ["barcode", "barcode_type", "created_at"]
    ordering = ["barcode"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ProductBarcodeSerializer
        return ProductBarcodeListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        return ProductBarcode.objects.filter(tenant_id=tenant_id, entity_id=product_id).order_by("barcode")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        barcode = ProductBarcodeEntity(
            tenant_id=tenant_id,
            entity_type="product",
            entity_id=product_id,
            **serializer.validated_data,
        )

        service = ProductBarcodeService(
            barcode_repository=ProductBarcodeRepository(),
            product_repository=ProductRepository(),
        )
        created = service.assign_barcode(barcode)

        return Response(
            {"data": ProductBarcodeSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


ProductBarcodeListCreateView.create.required_permission = "retail.products.create"


class ProductBarcodeDetailView(DestroyAPIView):
    """
    delete: Removes a product barcode.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.products.delete"
    lookup_field = "pk"

    def get_serializer_class(self):
        return ProductBarcodeSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        product_id = self.kwargs.get("product_id")
        return ProductBarcode.objects.filter(tenant_id=tenant_id, entity_id=product_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = ProductBarcodeService(
            barcode_repository=ProductBarcodeRepository(),
            product_repository=ProductRepository(),
        )
        service.remove_barcode(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


# ──────────────────────────────────────────────
# Suppliers
# ──────────────────────────────────────────────


class SupplierListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of suppliers.

    post: Creates a new supplier.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.suppliers.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "code", "email", "phone"]
    ordering_fields = ["name", "code", "created_at", "is_active"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupplierSerializer
        return SupplierListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return Supplier.objects.filter(tenant_id=tenant_id).order_by("name")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        supplier = SupplierEntity(
            tenant_id=tenant_id,
            **serializer.validated_data,
        )

        service = SupplierService(supplier_repository=SupplierRepository())
        created = service.create(supplier)

        return Response(
            {"data": SupplierSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


SupplierListCreateView.create.required_permission = "retail.suppliers.create"


class SupplierDetailView(RetrieveAPIView, UpdateAPIView, DestroyAPIView):
    """
    get: Returns detailed information about a specific supplier.

    put: Updates a specific supplier.

    delete: Soft-deletes a specific supplier.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.suppliers.read"
    lookup_field = "pk"

    def get_serializer_class(self):
        if self.request.method == "PUT":
            return SupplierSerializer
        return SupplierSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        return Supplier.objects.filter(tenant_id=tenant_id)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        supplier_id = str(instance.id)
        existing = SupplierRepository().get_by_id(supplier_id, tenant_id)
        if not existing:
            from django.http import Http404

            raise Http404

        for attr, value in serializer.validated_data.items():
            setattr(existing, attr, value)

        service = SupplierService(supplier_repository=SupplierRepository())
        updated = service.update(existing)

        return Response(
            {"data": SupplierSerializer(updated).data},
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = SupplierService(supplier_repository=SupplierRepository())
        service.archive(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


SupplierDetailView.update.required_permission = "retail.suppliers.update"
SupplierDetailView.destroy.required_permission = "retail.suppliers.delete"


# ──────────────────────────────────────────────
# Supplier Products
# ──────────────────────────────────────────────


class SupplierProductListCreateView(ListAPIView, CreateAPIView):
    """
    get: Returns a paginated list of products linked to a supplier.

    post: Links a product to a supplier.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.suppliers.read"
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["supplier_sku"]
    ordering_fields = ["supplier_sku", "lead_time_days", "created_at"]
    ordering = ["supplier_sku"]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return SupplierProductSerializer
        return SupplierProductListSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        supplier_id = self.kwargs.get("supplier_id")
        return SupplierProduct.objects.filter(tenant_id=tenant_id, supplier_id=supplier_id).order_by("supplier_sku")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tenant_id = request.actor.tenant_id
        supplier_id = self.kwargs.get("supplier_id")
        link = SupplierProductEntity(
            tenant_id=tenant_id,
            supplier_id=supplier_id,
            **serializer.validated_data,
        )

        service = SupplierProductService(
            supplier_product_repository=SupplierProductRepository(),
            product_repository=ProductRepository(),
        )
        created = service.link_supplier_to_product(link)

        return Response(
            {"data": SupplierProductSerializer(created).data},
            status=status.HTTP_201_CREATED,
        )


SupplierProductListCreateView.create.required_permission = "retail.suppliers.create"


class SupplierProductDetailView(DestroyAPIView):
    """
    delete: Unlinks a product from a supplier.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.suppliers.delete"
    lookup_field = "pk"

    def get_serializer_class(self):
        return SupplierProductSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_queryset(self):
        tenant_id = self.request.actor.tenant_id
        supplier_id = self.kwargs.get("supplier_id")
        return SupplierProduct.objects.filter(tenant_id=tenant_id, supplier_id=supplier_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        tenant_id = request.actor.tenant_id
        service = SupplierProductService(
            supplier_product_repository=SupplierProductRepository(),
            product_repository=ProductRepository(),
        )
        service.remove_link(str(instance.id), tenant_id)
        return Response(
            {"data": {"deleted": True}},
            status=status.HTTP_200_OK,
        )


class SupplierProductSetPreferredView(APIView):
    """
    post: Sets a supplier product link as preferred.
    """

    permission_classes = [IsAuthenticated]
    required_permission = "retail.suppliers.update"

    def post(self, request, supplier_id=None, pk=None):
        tenant_id = request.actor.tenant_id
        service = SupplierProductService(
            supplier_product_repository=SupplierProductRepository(),
            product_repository=ProductRepository(),
        )
        success = service.set_preferred(pk, tenant_id)
        if not success:
            return _error_response(
                "Supplier product link not found.",
                code="SUPPLIER_PRODUCT_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return Response({"data": {"preferred_set": True}}, status=status.HTTP_200_OK)