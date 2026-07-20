"""
Repository implementations for the retail module.

These repositories contain persistence operations only. No business logic is
implemented here.
"""

from django.utils import timezone

from apps.retail.domain.entities import (
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
from apps.retail.infrastructure.models import (
    Brand as BrandModel,
    Product as ProductModel,
    ProductBarcode as ProductBarcodeModel,
    ProductCategory as ProductCategoryModel,
    ProductImage as ProductImageModel,
    ProductVariant as ProductVariantModel,
    Supplier as SupplierModel,
    SupplierProduct as SupplierProductModel,
    UnitOfMeasure as UnitOfMeasureModel,
)


class UnitOfMeasureRepository:
    """Repository for UnitOfMeasure."""

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[UnitOfMeasure]:
        qs = UnitOfMeasureModel.objects.filter(tenant_id=tenant_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_entity(model) for model in qs]

    def get_by_id(self, unit_id: str, tenant_id: str) -> UnitOfMeasure | None:
        try:
            return self._to_entity(UnitOfMeasureModel.objects.get(id=unit_id, tenant_id=tenant_id))
        except UnitOfMeasureModel.DoesNotExist:
            return None

    def get_by_symbol(self, symbol: str, tenant_id: str) -> UnitOfMeasure | None:
        try:
            return self._to_entity(UnitOfMeasureModel.objects.get(tenant_id=tenant_id, symbol=symbol))
        except UnitOfMeasureModel.DoesNotExist:
            return None

    def create(self, unit: UnitOfMeasure) -> UnitOfMeasure:
        model = UnitOfMeasureModel(
            id=unit.id,
            tenant_id=unit.tenant_id,
            name=unit.name,
            symbol=unit.symbol,
            unit_type=unit.unit_type,
            conversion_factor=unit.conversion_factor,
            is_active=unit.is_active,
        )
        model.save()
        return self._to_entity(model)

    def update(self, unit: UnitOfMeasure) -> UnitOfMeasure:
        model = UnitOfMeasureModel.objects.get(id=unit.id, tenant_id=unit.tenant_id)
        model.name = unit.name
        model.symbol = unit.symbol
        model.unit_type = unit.unit_type
        model.conversion_factor = unit.conversion_factor
        model.is_active = unit.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, unit_id: str, tenant_id: str) -> bool:
        updated = UnitOfMeasureModel.objects.filter(id=unit_id, tenant_id=tenant_id).update(is_active=False)
        return updated > 0

    def _to_entity(self, model: UnitOfMeasureModel) -> UnitOfMeasure:
        return UnitOfMeasure(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            symbol=model.symbol,
            unit_type=model.unit_type,
            conversion_factor=float(model.conversion_factor) if model.conversion_factor is not None else None,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class BrandRepository:
    """Repository for Brand."""

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[Brand]:
        qs = BrandModel.objects.filter(tenant_id=tenant_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_entity(model) for model in qs]

    def get_by_id(self, brand_id: str, tenant_id: str) -> Brand | None:
        try:
            return self._to_entity(BrandModel.objects.get(id=brand_id, tenant_id=tenant_id))
        except BrandModel.DoesNotExist:
            return None

    def create(self, brand: Brand) -> Brand:
        model = BrandModel(
            id=brand.id,
            tenant_id=brand.tenant_id,
            name=brand.name,
            description=brand.description,
            website=brand.website,
            logo_path=brand.logo_path,
            is_active=brand.is_active,
        )
        model.save()
        return self._to_entity(model)

    def update(self, brand: Brand) -> Brand:
        model = BrandModel.objects.get(id=brand.id, tenant_id=brand.tenant_id)
        model.name = brand.name
        model.description = brand.description
        model.website = brand.website
        model.logo_path = brand.logo_path
        model.is_active = brand.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, brand_id: str, tenant_id: str) -> bool:
        updated = BrandModel.objects.filter(id=brand_id, tenant_id=tenant_id).update(is_active=False, deleted_at=timezone.now())
        return updated > 0

    def _to_entity(self, model: BrandModel) -> Brand:
        return Brand(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            description=model.description or "",
            website=model.website or "",
            logo_path=model.logo_path or "",
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ProductCategoryRepository:
    """Repository for ProductCategory."""

    def list_for_tenant(self, tenant_id: str, parent_id: str | None = None) -> list[ProductCategory]:
        qs = ProductCategoryModel.objects.filter(tenant_id=tenant_id)
        if parent_id is not None:
            qs = qs.filter(parent_id=parent_id)
        else:
            qs = qs.filter(parent__isnull=True)
        return [self._to_entity(model) for model in qs]

    def get_by_id(self, category_id: str, tenant_id: str) -> ProductCategory | None:
        try:
            return self._to_entity(ProductCategoryModel.objects.get(id=category_id, tenant_id=tenant_id))
        except ProductCategoryModel.DoesNotExist:
            return None

    def create(self, category: ProductCategory) -> ProductCategory:
        model = ProductCategoryModel(
            id=category.id,
            tenant_id=category.tenant_id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            image_path=category.image_path,
            sort_order=category.sort_order,
            is_active=category.is_active,
        )
        model.save()
        return self._to_entity(model)

    def update(self, category: ProductCategory) -> ProductCategory:
        model = ProductCategoryModel.objects.get(id=category.id, tenant_id=category.tenant_id)
        model.name = category.name
        model.description = category.description
        model.parent_id = category.parent_id
        model.image_path = category.image_path
        model.sort_order = category.sort_order
        model.is_active = category.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, category_id: str, tenant_id: str) -> bool:
        updated = ProductCategoryModel.objects.filter(id=category_id, tenant_id=tenant_id).update(is_active=False, deleted_at=timezone.now())
        return updated > 0

    def _to_entity(self, model: ProductCategoryModel) -> ProductCategory:
        return ProductCategory(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            description=model.description or "",
            parent_id=str(model.parent_id) if model.parent_id else None,
            image_path=model.image_path or "",
            sort_order=model.sort_order,
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ProductRepository:
    """Repository for Product."""

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[Product]:
        qs = ProductModel.objects.filter(tenant_id=tenant_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_entity(model) for model in qs]

    def get_by_id(self, product_id: str, tenant_id: str) -> Product | None:
        try:
            return self._to_entity(ProductModel.objects.get(id=product_id, tenant_id=tenant_id))
        except ProductModel.DoesNotExist:
            return None

    def get_by_sku(self, sku: str, tenant_id: str) -> Product | None:
        try:
            return self._to_entity(ProductModel.objects.get(tenant_id=tenant_id, sku=sku))
        except ProductModel.DoesNotExist:
            return None

    def get_by_barcode(self, barcode: str, tenant_id: str) -> Product | None:
        try:
            return self._to_entity(ProductModel.objects.get(tenant_id=tenant_id, barcode=barcode))
        except ProductModel.DoesNotExist:
            return None

    def create(self, product: Product) -> Product:
        model = ProductModel(
            id=product.id,
            tenant_id=product.tenant_id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            brand_id=product.brand_id,
            category_id=product.category_id,
            unit_of_measure_id=product.unit_of_measure_id,
            barcode=product.barcode,
            status=product.status,
            is_trackable=product.is_trackable,
            is_serialized=product.is_serialized,
            is_batched=product.is_batched,
            attributes=product.attributes,
            is_active=product.is_active,
        )
        model.save()
        return self._to_entity(model)

    def update(self, product: Product) -> Product:
        model = ProductModel.objects.get(id=product.id, tenant_id=product.tenant_id)
        model.sku = product.sku
        model.name = product.name
        model.description = product.description
        model.brand_id = product.brand_id
        model.category_id = product.category_id
        model.unit_of_measure_id = product.unit_of_measure_id
        model.barcode = product.barcode
        model.status = product.status
        model.is_trackable = product.is_trackable
        model.is_serialized = product.is_serialized
        model.is_batched = product.is_batched
        model.attributes = product.attributes
        model.is_active = product.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, product_id: str, tenant_id: str) -> bool:
        updated = ProductModel.objects.filter(id=product_id, tenant_id=tenant_id).update(is_active=False, deleted_at=timezone.now())
        return updated > 0

    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            sku=model.sku,
            name=model.name,
            description=model.description or "",
            brand_id=str(model.brand_id) if model.brand_id else None,
            category_id=str(model.category_id) if model.category_id else None,
            unit_of_measure_id=str(model.unit_of_measure_id),
            barcode=model.barcode or "",
            status=model.status,
            is_trackable=model.is_trackable,
            is_serialized=model.is_serialized,
            is_batched=model.is_batched,
            attributes=model.attributes or {},
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ProductVariantRepository:
    """Repository for ProductVariant."""

    def list_for_product(self, tenant_id: str, product_id: str) -> list[ProductVariant]:
        return [self._to_entity(model) for model in ProductVariantModel.objects.filter(tenant_id=tenant_id, product_id=product_id)]

    def get_by_id(self, variant_id: str, tenant_id: str) -> ProductVariant | None:
        try:
            return self._to_entity(ProductVariantModel.objects.get(id=variant_id, tenant_id=tenant_id))
        except ProductVariantModel.DoesNotExist:
            return None

    def create(self, variant: ProductVariant) -> ProductVariant:
        model = ProductVariantModel(
            id=variant.id,
            tenant_id=variant.tenant_id,
            product_id=variant.product_id,
            sku=variant.sku,
            name=variant.name,
            barcode=variant.barcode,
            attributes=variant.attributes,
            is_active=variant.is_active,
        )
        model.save()
        return self._to_entity(model)

    def update(self, variant: ProductVariant) -> ProductVariant:
        model = ProductVariantModel.objects.get(id=variant.id, tenant_id=variant.tenant_id)
        model.product_id = variant.product_id
        model.sku = variant.sku
        model.name = variant.name
        model.barcode = variant.barcode
        model.attributes = variant.attributes
        model.is_active = variant.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, variant_id: str, tenant_id: str) -> bool:
        updated = ProductVariantModel.objects.filter(id=variant_id, tenant_id=tenant_id).update(is_active=False, deleted_at=timezone.now())
        return updated > 0

    def _to_entity(self, model: ProductVariantModel) -> ProductVariant:
        return ProductVariant(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            product_id=str(model.product_id),
            sku=model.sku,
            name=model.name,
            barcode=model.barcode or "",
            attributes=model.attributes or {},
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ProductImageRepository:
    """Repository for ProductImage."""

    def list_for_product(self, tenant_id: str, product_id: str) -> list[ProductImage]:
        return [self._to_entity(model) for model in ProductImageModel.objects.filter(tenant_id=tenant_id, product_id=product_id)]

    def create(self, image: ProductImage) -> ProductImage:
        model = ProductImageModel(
            id=image.id,
            tenant_id=image.tenant_id,
            product_id=image.product_id,
            variant_id=image.variant_id,
            storage_provider=image.storage_provider,
            storage_path=image.storage_path,
            original_filename=image.original_filename,
            mime_type=image.mime_type,
            file_size=image.file_size,
            sort_order=image.sort_order,
            is_primary=image.is_primary,
        )
        model.save()
        return self._to_entity(model)

    def update(self, image: ProductImage) -> ProductImage:
        model = ProductImageModel.objects.get(id=image.id, tenant_id=image.tenant_id)
        model.variant_id = image.variant_id
        model.storage_provider = image.storage_provider
        model.storage_path = image.storage_path
        model.original_filename = image.original_filename
        model.mime_type = image.mime_type
        model.file_size = image.file_size
        model.sort_order = image.sort_order
        model.is_primary = image.is_primary
        model.save()
        return self._to_entity(model)

    def unset_primary(self, image_id: str, tenant_id: str) -> bool:
        updated = ProductImageModel.objects.filter(id=image_id, tenant_id=tenant_id).update(is_primary=False)
        return updated > 0

    def delete(self, image_id: str, tenant_id: str) -> bool:
        deleted, _ = ProductImageModel.objects.filter(id=image_id, tenant_id=tenant_id).delete()
        return deleted > 0

    def _to_entity(self, model: ProductImageModel) -> ProductImage:
        return ProductImage(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            product_id=str(model.product_id),
            variant_id=str(model.variant_id) if model.variant_id else None,
            storage_provider=model.storage_provider,
            storage_path=model.storage_path,
            original_filename=model.original_filename,
            mime_type=model.mime_type,
            file_size=model.file_size,
            sort_order=model.sort_order,
            is_primary=model.is_primary,
            created_at=model.created_at,
        )


class ProductBarcodeRepository:
    """Repository for ProductBarcode."""

    def get_by_barcode(self, barcode: str, tenant_id: str) -> ProductBarcode | None:
        try:
            return self._to_entity(ProductBarcodeModel.objects.get(tenant_id=tenant_id, barcode=barcode))
        except ProductBarcodeModel.DoesNotExist:
            return None

    def create(self, barcode: ProductBarcode) -> ProductBarcode:
        model = ProductBarcodeModel(
            id=barcode.id,
            tenant_id=barcode.tenant_id,
            entity_type=barcode.entity_type,
            entity_id=barcode.entity_id,
            barcode=barcode.barcode,
            barcode_type=barcode.barcode_type,
        )
        model.save()
        return self._to_entity(model)

    def get_for_entity(self, tenant_id: str, entity_type: str, entity_id: str) -> list[ProductBarcode]:
        return [
            self._to_entity(model)
            for model in ProductBarcodeModel.objects.filter(
                tenant_id=tenant_id, entity_type=entity_type, entity_id=entity_id
            )
        ]

    def delete(self, barcode_id: str, tenant_id: str) -> bool:
        deleted, _ = ProductBarcodeModel.objects.filter(id=barcode_id, tenant_id=tenant_id).delete()
        return deleted > 0

    def _to_entity(self, model: ProductBarcodeModel) -> ProductBarcode:
        return ProductBarcode(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            entity_type=model.entity_type,
            entity_id=str(model.entity_id),
            barcode=model.barcode,
            barcode_type=model.barcode_type,
            created_at=model.created_at,
        )


class SupplierRepository:
    """Repository for Supplier."""

    def list_for_tenant(self, tenant_id: str, active_only: bool = True) -> list[Supplier]:
        qs = SupplierModel.objects.filter(tenant_id=tenant_id)
        if active_only:
            qs = qs.filter(is_active=True)
        return [self._to_entity(model) for model in qs]

    def get_by_id(self, supplier_id: str, tenant_id: str) -> Supplier | None:
        try:
            return self._to_entity(SupplierModel.objects.get(id=supplier_id, tenant_id=tenant_id))
        except SupplierModel.DoesNotExist:
            return None

    def create(self, supplier: Supplier) -> Supplier:
        model = SupplierModel(
            id=supplier.id,
            tenant_id=supplier.tenant_id,
            name=supplier.name,
            code=supplier.code,
            email=supplier.email,
            phone=supplier.phone,
            website=supplier.website,
            tax_number=supplier.tax_number,
            payment_terms_days=supplier.payment_terms_days,
            is_active=supplier.is_active,
        )
        model.save()
        return self._to_entity(model)

    def update(self, supplier: Supplier) -> Supplier:
        model = SupplierModel.objects.get(id=supplier.id, tenant_id=supplier.tenant_id)
        model.name = supplier.name
        model.code = supplier.code
        model.email = supplier.email
        model.phone = supplier.phone
        model.website = supplier.website
        model.tax_number = supplier.tax_number
        model.payment_terms_days = supplier.payment_terms_days
        model.is_active = supplier.is_active
        model.save()
        return self._to_entity(model)

    def soft_delete(self, supplier_id: str, tenant_id: str) -> bool:
        updated = SupplierModel.objects.filter(id=supplier_id, tenant_id=tenant_id).update(is_active=False, deleted_at=timezone.now())
        return updated > 0

    def _to_entity(self, model: SupplierModel) -> Supplier:
        return Supplier(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            code=model.code,
            email=model.email or "",
            phone=model.phone or "",
            website=model.website or "",
            tax_number=model.tax_number or "",
            payment_terms_days=model.payment_terms_days,
            is_active=model.is_active,
            deleted_at=model.deleted_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SupplierProductRepository:
    """Repository for SupplierProduct."""

    def list_for_supplier(self, tenant_id: str, supplier_id: str) -> list[SupplierProduct]:
        return [self._to_entity(model) for model in SupplierProductModel.objects.filter(tenant_id=tenant_id, supplier_id=supplier_id)]

    def create(self, supplier_product: SupplierProduct) -> SupplierProduct:
        model = SupplierProductModel(
            id=supplier_product.id,
            tenant_id=supplier_product.tenant_id,
            supplier_id=supplier_product.supplier_id,
            product_id=supplier_product.product_id,
            supplier_sku=supplier_product.supplier_sku,
            lead_time_days=supplier_product.lead_time_days,
            min_order_quantity=supplier_product.min_order_quantity,
            preferred=supplier_product.preferred,
            is_active=supplier_product.is_active,
        )
        model.save()
        return self._to_entity(model)

    def get_by_id(self, supplier_product_id: str, tenant_id: str) -> SupplierProduct | None:
        try:
            return self._to_entity(SupplierProductModel.objects.get(id=supplier_product_id, tenant_id=tenant_id))
        except SupplierProductModel.DoesNotExist:
            return None

    def update(self, supplier_product: SupplierProduct) -> SupplierProduct:
        model = SupplierProductModel.objects.get(id=supplier_product.id, tenant_id=supplier_product.tenant_id)
        model.supplier_id = supplier_product.supplier_id
        model.product_id = supplier_product.product_id
        model.supplier_sku = supplier_product.supplier_sku
        model.lead_time_days = supplier_product.lead_time_days
        model.min_order_quantity = supplier_product.min_order_quantity
        model.preferred = supplier_product.preferred
        model.is_active = supplier_product.is_active
        model.save()
        return self._to_entity(model)

    def delete(self, supplier_product_id: str, tenant_id: str) -> bool:
        deleted, _ = SupplierProductModel.objects.filter(id=supplier_product_id, tenant_id=tenant_id).delete()
        return deleted > 0

    def _to_entity(self, model: SupplierProductModel) -> SupplierProduct:
        return SupplierProduct(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            supplier_id=str(model.supplier_id),
            product_id=str(model.product_id),
            supplier_sku=model.supplier_sku,
            lead_time_days=model.lead_time_days,
            min_order_quantity=float(model.min_order_quantity),
            preferred=model.preferred,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
