"""
Application service for SupplierProduct.
"""

import logging

from django.db import transaction

from apps.retail.domain.entities import SupplierProduct
from apps.retail.infrastructure.repositories import SupplierProductRepository, ProductRepository
from shared.events.retail_events import SupplierLinked, SupplierUnlinked, PreferredSupplierChanged

logger = logging.getLogger("tradeflow.retail")


class SupplierProductService:
    """Service for SupplierProduct."""

    def __init__(self, supplier_product_repository: SupplierProductRepository, product_repository: ProductRepository):
        self.supplier_product_repository = supplier_product_repository
        self.product_repository = product_repository

    def list_for_supplier(self, tenant_id: str, supplier_id: str) -> list[SupplierProduct]:
        return self.supplier_product_repository.list_for_supplier(tenant_id, supplier_id)

    def link_supplier_to_product(self, supplier_product: SupplierProduct) -> SupplierProduct:
        with transaction.atomic():
            created = self.supplier_product_repository.create(supplier_product)
            SupplierLinked(
                tenant_id=supplier_product.tenant_id,
                supplier_product_id=created.id,
                supplier_id=supplier_product.supplier_id,
                product_id=supplier_product.product_id,
            ).emit()
            logger.info(
                f"Supplier linked: supplier={supplier_product.supplier_id} product={supplier_product.product_id} tenant={supplier_product.tenant_id}"
            )
            return created

    def set_preferred(self, supplier_product_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            links = self.supplier_product_repository.list_for_supplier(
                tenant_id,
                self.supplier_product_repository.get_by_id(supplier_product_id, tenant_id).supplier_id,
            )
            for link in links:
                if link.id == supplier_product_id and link.preferred:
                    continue
                updated = self.supplier_product_repository.update(
                    SupplierProduct(
                        id=link.id,
                        tenant_id=link.tenant_id,
                        supplier_id=link.supplier_id,
                        product_id=link.product_id,
                        supplier_sku=link.supplier_sku,
                        lead_time_days=link.lead_time_days,
                        min_order_quantity=link.min_order_quantity,
                        preferred=(link.id == supplier_product_id),
                        is_active=link.is_active,
                    )
                )
            PreferredSupplierChanged(
                tenant_id=tenant_id,
                product_id=updated.product_id,
                supplier_id=updated.supplier_id,
            ).emit()
            logger.info(f"Preferred supplier changed: product={updated.product_id} supplier={updated.supplier_id} tenant={tenant_id}")
            return True

    def remove_link(self, supplier_product_id: str, tenant_id: str) -> bool:
        with transaction.atomic():
            success = self.supplier_product_repository.delete(supplier_product_id, tenant_id)
            if success:
                SupplierUnlinked(tenant_id=tenant_id, supplier_product_id=supplier_product_id).emit()
                logger.info(f"Supplier unlinked: {supplier_product_id} tenant={tenant_id}")
            return success