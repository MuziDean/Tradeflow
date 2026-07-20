"""
API serializers for the Retail module.

Per Backend Engineering Standards §6.2: Serializers handle request parsing
and response formatting only. No business logic.
"""

from rest_framework import serializers

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


# ──────────────────────────────────────────────
# Unit of Measure
# ──────────────────────────────────────────────


class UnitOfMeasureSerializer(serializers.ModelSerializer):
    """Read/write serializer for unit of measure."""

    class Meta:
        model = UnitOfMeasure
        fields = [
            "id",
            "name",
            "symbol",
            "unit_type",
            "conversion_factor",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UnitOfMeasureListSerializer(serializers.ModelSerializer):
    """Compact serializer for unit list responses."""

    class Meta:
        model = UnitOfMeasure
        fields = [
            "id",
            "name",
            "symbol",
            "unit_type",
            "conversion_factor",
            "is_active",
        ]


# ──────────────────────────────────────────────
# Brand
# ──────────────────────────────────────────────


class BrandSerializer(serializers.ModelSerializer):
    """Read/write serializer for brand."""

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "description",
            "website",
            "logo_path",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class BrandListSerializer(serializers.ModelSerializer):
    """Compact serializer for brand list responses."""

    class Meta:
        model = Brand
        fields = [
            "id",
            "name",
            "website",
            "logo_path",
            "is_active",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Product Category
# ──────────────────────────────────────────────


class ProductCategorySerializer(serializers.ModelSerializer):
    """Read/write serializer for product category."""

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "description",
            "parent_id",
            "image_path",
            "sort_order",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class ProductCategoryListSerializer(serializers.ModelSerializer):
    """Compact serializer for category list responses."""

    class Meta:
        model = ProductCategory
        fields = [
            "id",
            "name",
            "parent_id",
            "sort_order",
            "is_active",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Product
# ──────────────────────────────────────────────


class ProductSerializer(serializers.ModelSerializer):
    """Read/write serializer for product."""

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "description",
            "brand_id",
            "category_id",
            "unit_of_measure_id",
            "barcode",
            "status",
            "is_trackable",
            "is_serialized",
            "is_batched",
            "attributes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class ProductListSerializer(serializers.ModelSerializer):
    """Compact serializer for product list responses."""

    class Meta:
        model = Product
        fields = [
            "id",
            "sku",
            "name",
            "brand_id",
            "category_id",
            "unit_of_measure_id",
            "barcode",
            "status",
            "is_trackable",
            "is_serialized",
            "is_batched",
            "is_active",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Product Variant
# ──────────────────────────────────────────────


class ProductVariantSerializer(serializers.ModelSerializer):
    """Read/write serializer for product variant."""

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product_id",
            "sku",
            "name",
            "attributes",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class ProductVariantListSerializer(serializers.ModelSerializer):
    """Compact serializer for variant list responses."""

    class Meta:
        model = ProductVariant
        fields = [
            "id",
            "product_id",
            "sku",
            "name",
            "attributes",
            "is_active",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Product Image
# ──────────────────────────────────────────────


class ProductImageSerializer(serializers.ModelSerializer):
    """Read/write serializer for product image."""

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "product_id",
            "variant_id",
            "storage_provider",
            "storage_path",
            "original_filename",
            "mime_type",
            "file_size",
            "sort_order",
            "is_primary",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ProductImageListSerializer(serializers.ModelSerializer):
    """Compact serializer for product image list responses."""

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "product_id",
            "variant_id",
            "storage_path",
            "original_filename",
            "mime_type",
            "file_size",
            "sort_order",
            "is_primary",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Product Barcode
# ──────────────────────────────────────────────


class ProductBarcodeSerializer(serializers.ModelSerializer):
    """Read/write serializer for product barcode."""

    class Meta:
        model = ProductBarcode
        fields = [
            "id",
            "entity_type",
            "entity_id",
            "barcode",
            "barcode_type",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class ProductBarcodeListSerializer(serializers.ModelSerializer):
    """Compact serializer for barcode list responses."""

    class Meta:
        model = ProductBarcode
        fields = [
            "id",
            "entity_type",
            "entity_id",
            "barcode",
            "barcode_type",
            "is_active",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Supplier
# ──────────────────────────────────────────────


class SupplierSerializer(serializers.ModelSerializer):
    """Read/write serializer for supplier."""

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "website",
            "tax_number",
            "payment_terms_days",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class SupplierListSerializer(serializers.ModelSerializer):
    """Compact serializer for supplier list responses."""

    class Meta:
        model = Supplier
        fields = [
            "id",
            "name",
            "code",
            "email",
            "phone",
            "website",
            "tax_number",
            "payment_terms_days",
            "is_active",
            "created_at",
        ]


# ──────────────────────────────────────────────
# Supplier Product
# ──────────────────────────────────────────────


class SupplierProductSerializer(serializers.ModelSerializer):
    """Read/write serializer for supplier product link."""

    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "supplier_id",
            "product_id",
            "supplier_sku",
            "lead_time_days",
            "min_order_quantity",
            "preferred",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]


class SupplierProductListSerializer(serializers.ModelSerializer):
    """Compact serializer for supplier product list responses."""

    class Meta:
        model = SupplierProduct
        fields = [
            "id",
            "supplier_id",
            "product_id",
            "supplier_sku",
            "lead_time_days",
            "min_order_quantity",
            "preferred",
            "is_active",
            "created_at",
        ]