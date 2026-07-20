"""
Application service for SupplierPriceList.

Business rules:
- Price lists have validity periods (valid_from, valid_to)
- Only one active price per supplier-product combination at a time
- Deactivating a price list does not delete it
- Supports blanket/consignment pricing
- Full audit trail preserved
"""

import logging

from django.db import transaction

from apps.purchasing.domain.entities import SupplierPriceList
from apps.purchasing.infrastructure.repositories import SupplierPriceListRepository
from shared.events.purchasing_events import SupplierPriceListActivated, SupplierPriceListDeactivated
from shared.time.helpers import now

logger = logging.getLogger("tradeflow.purchasing")


class SupplierPriceListService:
    """Service for SupplierPriceList."""

    def __init__(self, price_list_repository: SupplierPriceListRepository):
        self.price_list_repository = price_list_repository

    def list_for_supplier(self, tenant_id: str, supplier_id: str) -> list[SupplierPriceList]:
        return self.price_list_repository.list_for_tenant(tenant_id, supplier_id)

    def get_active_for_supplier_product(self, tenant_id: str, supplier_id: str, product_id: str, variant_id: str = None) -> SupplierPriceList | None:
        return self.price_list_repository.get_active_for_supplier_product(tenant_id, supplier_id, product_id, variant_id)

    def create(self, price_list: SupplierPriceList) -> SupplierPriceList:
        with transaction.atomic():
            created = self.price_list_repository.create(price_list)
            if created.is_active:
                SupplierPriceListActivated(
                    tenant_id=price_list.tenant_id,
                    price_list_id=created.id,
                    supplier_id=created.supplier_id,
                    product_id=created.product_id,
                ).emit()
            logger.info(f"SupplierPriceList created: {created.id} tenant={price_list.tenant_id}")
            return created

    def update(self, price_list: SupplierPriceList) -> SupplierPriceList:
        with transaction.atomic():
            existing = self.price_list_repository.get_by_id(price_list.id, price_list.tenant_id)
            if not existing:
                raise ValueError("SupplierPriceList not found")
            updated = self.price_list_repository.update(price_list)
            if updated.is_active and not existing.is_active:
                SupplierPriceListActivated(
                    tenant_id=price_list.tenant_id,
                    price_list_id=updated.id,
                    supplier_id=updated.supplier_id,
                    product_id=updated.product_id,
                ).emit()
            elif not updated.is_active and existing.is_active:
                SupplierPriceListDeactivated(
                    tenant_id=price_list.tenant_id,
                    price_list_id=updated.id,
                    supplier_id=updated.supplier_id,
                    product_id=updated.product_id,
                ).emit()
            logger.info(f"SupplierPriceList updated: {updated.id} tenant={price_list.tenant_id}")
            return updated

    def activate(self, price_list_id: str, tenant_id: str) -> SupplierPriceList | None:
        with transaction.atomic():
            price_list = self.price_list_repository.get_by_id(price_list_id, tenant_id)
            if not price_list or price_list.is_active:
                return None
            updated = self.price_list_repository.update(
                SupplierPriceList(
                    id=price_list.id,
                    tenant_id=price_list.tenant_id,
                    supplier_id=price_list.supplier_id,
                    product_id=price_list.product_id,
                    variant_id=price_list.variant_id,
                    price=price_list.price,
                    discount_percent=price_list.discount_percent,
                    discount_amount=price_list.discount_amount,
                    effective_price=price_list.effective_price,
                    currency=price_list.currency,
                    valid_from=price_list.valid_from,
                    valid_to=price_list.valid_to,
                    minimum_order_quantity=price_list.minimum_order_quantity,
                    lead_time_days=price_list.lead_time_days,
                    is_active=True,
                )
            )
            SupplierPriceListActivated(
                tenant_id=tenant_id,
                price_list_id=price_list_id,
                supplier_id=price_list.supplier_id,
                product_id=price_list.product_id,
            ).emit()
            logger.info(f"SupplierPriceList activated: {price_list_id} tenant={tenant_id}")
            return updated

    def deactivate(self, price_list_id: str, tenant_id: str) -> SupplierPriceList | None:
        with transaction.atomic():
            price_list = self.price_list_repository.get_by_id(price_list_id, tenant_id)
            if not price_list or not price_list.is_active:
                return None
            updated = self.price_list_repository.update(
                SupplierPriceList(
                    id=price_list.id,
                    tenant_id=price_list.tenant_id,
                    supplier_id=price_list.supplier_id,
                    product_id=price_list.product_id,
                    variant_id=price_list.variant_id,
                    price=price_list.price,
                    discount_percent=price_list.discount_percent,
                    discount_amount=price_list.discount_amount,
                    effective_price=price_list.effective_price,
                    currency=price_list.currency,
                    valid_from=price_list.valid_from,
                    valid_to=price_list.valid_to,
                    minimum_order_quantity=price_list.minimum_order_quantity,
                    lead_time_days=price_list.lead_time_days,
                    is_active=False,
                )
            )
            SupplierPriceListDeactivated(
                tenant_id=tenant_id,
                price_list_id=price_list_id,
                supplier_id=price_list.supplier_id,
                product_id=price_list.product_id,
            ).emit()
            logger.info(f"SupplierPriceList deactivated: {price_list_id} tenant={tenant_id}")
            return updated