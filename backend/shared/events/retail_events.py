"""
Domain events for the retail module.

All events inherit from the shared DomainEvent base class and represent
immutable business facts that application services emit after successful
transaction commits.
"""

from shared.events.base import DomainEvent


class ProductCreated(DomainEvent):
    """Emitted when a new product is created."""

    def __init__(self, tenant_id: str, product_id: str, sku: str, name: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=product_id,
            aggregate_type="Product",
            event_data={"sku": sku, "name": name},
        )


class ProductUpdated(DomainEvent):
    """Emitted when a product is updated."""

    def __init__(self, tenant_id: str, product_id: str, sku: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=product_id,
            aggregate_type="Product",
            event_data={"sku": sku},
        )


class ProductArchived(DomainEvent):
    """Emitted when a product is archived."""

    def __init__(self, tenant_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=product_id,
            aggregate_type="Product",
            event_data={},
        )


class ProductActivated(DomainEvent):
    """Emitted when a product is activated."""

    def __init__(self, tenant_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=product_id,
            aggregate_type="Product",
            event_data={},
        )


class ProductDeactivated(DomainEvent):
    """Emitted when a product is deactivated."""

    def __init__(self, tenant_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=product_id,
            aggregate_type="Product",
            event_data={},
        )


class CategoryCreated(DomainEvent):
    """Emitted when a new category is created."""

    def __init__(self, tenant_id: str, category_id: str, name: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=category_id,
            aggregate_type="ProductCategory",
            event_data={"name": name},
        )


class CategoryUpdated(DomainEvent):
    """Emitted when a category is updated."""

    def __init__(self, tenant_id: str, category_id: str, name: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=category_id,
            aggregate_type="ProductCategory",
            event_data={"name": name},
        )


class CategoryArchived(DomainEvent):
    """Emitted when a category is archived."""

    def __init__(self, tenant_id: str, category_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=category_id,
            aggregate_type="ProductCategory",
            event_data={},
        )


class CategoryRestored(DomainEvent):
    """Emitted when a category is restored."""

    def __init__(self, tenant_id: str, category_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=category_id,
            aggregate_type="ProductCategory",
            event_data={},
        )


class BrandCreated(DomainEvent):
    """Emitted when a new brand is created."""

    def __init__(self, tenant_id: str, brand_id: str, name: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=brand_id,
            aggregate_type="Brand",
            event_data={"name": name},
        )


class BrandUpdated(DomainEvent):
    """Emitted when a brand is updated."""

    def __init__(self, tenant_id: str, brand_id: str, name: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=brand_id,
            aggregate_type="Brand",
            event_data={"name": name},
        )


class BrandArchived(DomainEvent):
    """Emitted when a brand is archived."""

    def __init__(self, tenant_id: str, brand_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=brand_id,
            aggregate_type="Brand",
            event_data={},
        )


class BrandRestored(DomainEvent):
    """Emitted when a brand is restored."""

    def __init__(self, tenant_id: str, brand_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=brand_id,
            aggregate_type="Brand",
            event_data={},
        )


class SupplierCreated(DomainEvent):
    """Emitted when a new supplier is created."""

    def __init__(self, tenant_id: str, supplier_id: str, name: str, code: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=supplier_id,
            aggregate_type="Supplier",
            event_data={"name": name, "code": code},
        )


class SupplierUpdated(DomainEvent):
    """Emitted when a supplier is updated."""

    def __init__(self, tenant_id: str, supplier_id: str, name: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=supplier_id,
            aggregate_type="Supplier",
            event_data={"name": name},
        )


class SupplierArchived(DomainEvent):
    """Emitted when a supplier is archived."""

    def __init__(self, tenant_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=supplier_id,
            aggregate_type="Supplier",
            event_data={},
        )


class SupplierRestored(DomainEvent):
    """Emitted when a supplier is restored."""

    def __init__(self, tenant_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=supplier_id,
            aggregate_type="Supplier",
            event_data={},
        )


class ProductVariantCreated(DomainEvent):
    """Emitted when a new product variant is created."""

    def __init__(self, tenant_id: str, variant_id: str, product_id: str, sku: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=variant_id,
            aggregate_type="ProductVariant",
            event_data={"product_id": product_id, "sku": sku},
        )


class ProductVariantUpdated(DomainEvent):
    """Emitted when a product variant is updated."""

    def __init__(self, tenant_id: str, variant_id: str, sku: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=variant_id,
            aggregate_type="ProductVariant",
            event_data={"sku": sku},
        )


class ProductVariantArchived(DomainEvent):
    """Emitted when a product variant is archived."""

    def __init__(self, tenant_id: str, variant_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=variant_id,
            aggregate_type="ProductVariant",
            event_data={},
        )


class BarcodeAssigned(DomainEvent):
    """Emitted when a barcode is assigned to a product or variant."""

    def __init__(self, tenant_id: str, barcode_id: str, entity_type: str, entity_id: str, barcode: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=barcode_id,
            aggregate_type="ProductBarcode",
            event_data={
                "entity_type": entity_type,
                "entity_id": entity_id,
                "barcode": barcode,
            },
        )


class BarcodeRemoved(DomainEvent):
    """Emitted when a barcode is removed."""

    def __init__(self, tenant_id: str, barcode_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=barcode_id,
            aggregate_type="ProductBarcode",
            event_data={},
        )


class UnitOfMeasureCreated(DomainEvent):
    """Emitted when a new unit of measure is created."""

    def __init__(self, tenant_id: str, unit_id: str, name: str, symbol: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=unit_id,
            aggregate_type="UnitOfMeasure",
            event_data={"name": name, "symbol": symbol},
        )


class UnitOfMeasureUpdated(DomainEvent):
    """Emitted when a unit of measure is updated."""

    def __init__(self, tenant_id: str, unit_id: str, name: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=unit_id,
            aggregate_type="UnitOfMeasure",
            event_data={"name": name},
        )


class UnitOfMeasureDeleted(DomainEvent):
    """Emitted when a unit of measure is deleted."""

    def __init__(self, tenant_id: str, unit_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=unit_id,
            aggregate_type="UnitOfMeasure",
            event_data={},
        )


class ImageAdded(DomainEvent):
    """Emitted when an image is added to a product."""

    def __init__(self, tenant_id: str, image_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=image_id,
            aggregate_type="ProductImage",
            event_data={"product_id": product_id},
        )


class ImageRemoved(DomainEvent):
    """Emitted when an image is removed."""

    def __init__(self, tenant_id: str, image_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=image_id,
            aggregate_type="ProductImage",
            event_data={},
        )


class PrimaryImageSet(DomainEvent):
    """Emitted when the primary image is changed."""

    def __init__(self, tenant_id: str, product_id: str, image_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=product_id,
            aggregate_type="ProductImage",
            event_data={"image_id": image_id},
        )


class SupplierLinked(DomainEvent):
    """Emitted when a supplier is linked to a product."""

    def __init__(self, tenant_id: str, supplier_product_id: str, supplier_id: str, product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=supplier_product_id,
            aggregate_type="SupplierProduct",
            event_data={"supplier_id": supplier_id, "product_id": product_id},
        )


class SupplierUnlinked(DomainEvent):
    """Emitted when a supplier is unlinked from a product."""

    def __init__(self, tenant_id: str, supplier_product_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=supplier_product_id,
            aggregate_type="SupplierProduct",
            event_data={},
        )


class PreferredSupplierChanged(DomainEvent):
    """Emitted when the preferred supplier for a product changes."""

    def __init__(self, tenant_id: str, product_id: str, supplier_id: str):
        super().__init__(
            tenant_id=tenant_id,
            aggregate_id=product_id,
            aggregate_type="SupplierProduct",
            event_data={"supplier_id": supplier_id},
        )