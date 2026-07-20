"""
Application services for the retail module.

Each service handles one business capability in its own file.
"""

from apps.retail.application.brand_service import BrandService
from apps.retail.application.category_service import ProductCategoryService
from apps.retail.application.product_service import ProductService
from apps.retail.application.product_variant_service import ProductVariantService
from apps.retail.application.product_image_service import ProductImageService
from apps.retail.application.product_barcode_service import ProductBarcodeService
from apps.retail.application.supplier_service import SupplierService
from apps.retail.application.supplier_product_service import SupplierProductService
from apps.retail.application.unit_of_measure_service import UnitOfMeasureService

__all__ = [
    "UnitOfMeasureService",
    "BrandService",
    "ProductCategoryService",
    "ProductService",
    "ProductVariantService",
    "ProductImageService",
    "ProductBarcodeService",
    "SupplierService",
    "SupplierProductService",
]