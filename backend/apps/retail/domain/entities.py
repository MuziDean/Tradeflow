"""
Domain entities for the retail module.

Per ADR-004: Entities represent the core business concepts and invariants.
"""

from dataclasses import dataclass, field
from decimal import Decimal

from shared.ids.uuid import new_id_str
from shared.time.helpers import now


@dataclass
class UnitOfMeasure:
    """Unit of measure used for quantities and conversions."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    symbol: str = ""
    unit_type: str = ""
    conversion_factor: float | None = None
    is_active: bool = True
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class Brand:
    """Manufacturer or brand definition."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    description: str = ""
    website: str = ""
    logo_path: str = ""
    is_active: bool = True
    deleted_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class ProductCategory:
    """Hierarchical product category."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    description: str = ""
    parent_id: str | None = None
    image_path: str = ""
    sort_order: int = 0
    is_active: bool = True
    deleted_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class Product:
    """Core product catalog entity."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    sku: str = ""
    name: str = ""
    description: str = ""
    brand_id: str | None = None
    category_id: str | None = None
    unit_of_measure_id: str = ""
    barcode: str = ""
    status: str = ""
    is_trackable: bool = True
    is_serialized: bool = False
    is_batched: bool = False
    attributes: dict = field(default_factory=dict)
    is_active: bool = True
    deleted_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class ProductVariant:
    """Variant of a product such as color or size."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    product_id: str = ""
    sku: str = ""
    name: str = ""
    barcode: str = ""
    attributes: dict = field(default_factory=dict)
    is_active: bool = True
    deleted_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class ProductImage:
    """Media asset attached to a product or variant."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    product_id: str = ""
    variant_id: str | None = None
    storage_provider: str = ""
    storage_path: str = ""
    original_filename: str = ""
    mime_type: str = ""
    file_size: int = 0
    sort_order: int = 0
    is_primary: bool = False
    created_at: str = field(default_factory=now)


@dataclass
class ProductBarcode:
    """Barcode associated with a product, variant, or batch."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    entity_type: str = ""
    entity_id: str = ""
    barcode: str = ""
    barcode_type: str = ""
    created_at: str = field(default_factory=now)


@dataclass
class Supplier:
    """External supplier or vendor."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    code: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    tax_number: str = ""
    payment_terms_days: int = 0
    is_active: bool = True
    deleted_at: str | None = None
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)


@dataclass
class SupplierProduct:
    """Supplier relationship for a product."""

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    supplier_id: str = ""
    product_id: str = ""
    supplier_sku: str = ""
    lead_time_days: int = 0
    min_order_quantity: float = 0.0
    preferred: bool = False
    is_active: bool = True
    created_at: str = field(default_factory=now)
    updated_at: str = field(default_factory=now)
