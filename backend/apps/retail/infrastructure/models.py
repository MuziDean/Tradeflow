"""
Django ORM models for the retail module.

Product catalog foundation: units of measure, brands, categories, products,
variants, images, barcodes, suppliers, and supplier products.
"""

from django.db import models

from infrastructure.db.base_model import TenantModel
from shared.ids.uuid import new_id_str


class UnitOfMeasure(TenantModel):
    """Unit of measure definition."""

    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=20)
    unit_type = models.CharField(max_length=20, db_index=True)
    conversion_factor = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "retail_units_of_measure"
        verbose_name = "Unit of Measure"
        verbose_name_plural = "Units of Measure"
        unique_together = ("tenant_id", "symbol")
        indexes = [
            models.Index(fields=["tenant_id", "name"]),
            models.Index(fields=["tenant_id", "is_active"]),
        ]


class Brand(TenantModel):
    """Brand or manufacturer."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    logo_path = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "retail_brands"
        verbose_name = "Brand"
        verbose_name_plural = "Brands"
        unique_together = ("tenant_id", "name")
        indexes = [
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "deleted_at"]),
        ]


class ProductCategory(TenantModel):
    """Hierarchical product category."""

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    image_path = models.CharField(max_length=500, blank=True)
    sort_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "retail_product_categories"
        verbose_name = "Product Category"
        verbose_name_plural = "Product Categories"
        unique_together = ("tenant_id", "name")
        indexes = [
            models.Index(fields=["tenant_id", "parent"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "sort_order"]),
        ]


class Product(TenantModel):
    """Product catalog entry."""

    sku = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    brand = models.ForeignKey(Brand, null=True, blank=True, on_delete=models.SET_NULL, related_name="products")
    category = models.ForeignKey(ProductCategory, null=True, blank=True, on_delete=models.SET_NULL, related_name="products")
    unit_of_measure = models.ForeignKey(UnitOfMeasure, on_delete=models.PROTECT, related_name="products")
    barcode = models.CharField(max_length=100, blank=True, db_index=True)
    status = models.CharField(max_length=20, default="draft", db_index=True)
    is_trackable = models.BooleanField(default=True)
    is_serialized = models.BooleanField(default=False)
    is_batched = models.BooleanField(default=False)
    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "retail_products"
        verbose_name = "Product"
        verbose_name_plural = "Products"
        unique_together = ("tenant_id", "sku")
        indexes = [
            models.Index(fields=["tenant_id", "category"]),
            models.Index(fields=["tenant_id", "brand"]),
            models.Index(fields=["tenant_id", "status"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "deleted_at"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["barcode"]),
        ]


class ProductVariant(TenantModel):
    """Variant of a product."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    sku = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, blank=True, db_index=True)
    attributes = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "retail_product_variants"
        verbose_name = "Product Variant"
        verbose_name_plural = "Product Variants"
        unique_together = ("tenant_id", "sku")
        indexes = [
            models.Index(fields=["tenant_id", "product"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "deleted_at"]),
            models.Index(fields=["sku"]),
            models.Index(fields=["barcode"]),
        ]


class ProductImage(TenantModel):
    """Image asset for product or variant."""

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    variant = models.ForeignKey(ProductVariant, null=True, blank=True, on_delete=models.SET_NULL, related_name="images")
    storage_provider = models.CharField(max_length=20)
    storage_path = models.CharField(max_length=500)
    original_filename = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=100)
    file_size = models.BigIntegerField(default=0)
    sort_order = models.IntegerField(default=0)
    is_primary = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "retail_product_images"
        verbose_name = "Product Image"
        verbose_name_plural = "Product Images"
        indexes = [
            models.Index(fields=["tenant_id", "product"]),
            models.Index(fields=["tenant_id", "variant"]),
            models.Index(fields=["tenant_id", "is_primary"]),
        ]


class ProductBarcode(TenantModel):
    """Barcode reference for products or variants."""

    entity_type = models.CharField(max_length=30, db_index=True)
    entity_id = models.UUIDField(db_index=True)
    barcode = models.CharField(max_length=100, db_index=True)
    barcode_type = models.CharField(max_length=20, db_index=True)

    class Meta:
        db_table = "retail_product_barcodes"
        verbose_name = "Product Barcode"
        verbose_name_plural = "Product Barcodes"
        unique_together = ("tenant_id", "barcode")
        indexes = [
            models.Index(fields=["tenant_id", "entity_type", "entity_id"]),
            models.Index(fields=["tenant_id", "barcode_type"]),
        ]


class Supplier(TenantModel):
    """Supplier record."""

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, db_index=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    tax_number = models.CharField(max_length=100, blank=True)
    payment_terms_days = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = "retail_suppliers"
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"
        unique_together = ("tenant_id", "code")
        indexes = [
            models.Index(fields=["tenant_id", "name"]),
            models.Index(fields=["tenant_id", "is_active"]),
            models.Index(fields=["tenant_id", "deleted_at"]),
        ]


class SupplierProduct(TenantModel):
    """Supplier-submitted product mapping."""

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name="supplier_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="supplier_links")
    supplier_sku = models.CharField(max_length=100)
    lead_time_days = models.IntegerField(default=0)
    min_order_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    preferred = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "retail_supplier_products"
        verbose_name = "Supplier Product"
        verbose_name_plural = "Supplier Products"
        unique_together = ("tenant_id", "supplier", "product")
        indexes = [
            models.Index(fields=["tenant_id", "supplier"]),
            models.Index(fields=["tenant_id", "product"]),
            models.Index(fields=["tenant_id", "preferred"]),
            models.Index(fields=["tenant_id", "is_active"]),
        ]