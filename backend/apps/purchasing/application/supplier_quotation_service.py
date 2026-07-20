"""
Application service for SupplierQuotation.

Business rules:
- Draft quotation can be updated
- Sent quotation is awaiting supplier response
- Accepted quotation can be converted to Purchase Order
- Rejected/Expired quotations are archived
- Full audit trail preserved
"""

import logging

from django.db import transaction

from apps.purchasing.domain.entities import SupplierQuotation, SupplierQuotationLine
from apps.purchasing.infrastructure.repositories import SupplierQuotationLineRepository, SupplierQuotationRepository
from shared.events.purchasing_events import SupplierQuotationAccepted, SupplierQuotationCreated, SupplierQuotationExpired, SupplierQuotationRejected, SupplierQuotationSubmitted
from shared.types.enums import QuotationStatus
from shared.time.helpers import now

logger = logging.getLogger("tradeflow.purchasing")


class SupplierQuotationService:
    """Service for SupplierQuotation."""

    def __init__(self, quotation_repository: SupplierQuotationRepository,
                 line_repository: SupplierQuotationLineRepository):
        self.quotation_repository = quotation_repository
        self.line_repository = line_repository

    def list_for_supplier(self, tenant_id: str, supplier_id: str, status: str = "") -> list[SupplierQuotation]:
        return self.quotation_repository.list_for_tenant(tenant_id, status)

    def get_by_id(self, quotation_id: str, tenant_id: str) -> SupplierQuotation | None:
        return self.quotation_repository.get_by_id(quotation_id, tenant_id)

    def create(self, quotation: SupplierQuotation, lines: list[SupplierQuotationLine]) -> SupplierQuotation:
        with transaction.atomic():
            created = self.quotation_repository.create(quotation)
            for line in lines:
                line.quotation_id = created.id
                self.line_repository.create(line)
            SupplierQuotationCreated(
                tenant_id=quotation.tenant_id,
                quotation_id=created.id,
                supplier_id=created.supplier_id,
                warehouse_id=created.warehouse_id,
            ).emit()
            logger.info(f"SupplierQuotation created: {created.id} tenant={quotation.tenant_id}")
            return created

    def update(self, quotation: SupplierQuotation) -> SupplierQuotation:
        with transaction.atomic():
            updated = self.quotation_repository.update(quotation)
            logger.info(f"SupplierQuotation updated: {updated.id} tenant={updated.tenant_id}")
            return updated

    def submit(self, quotation_id: str, tenant_id: str) -> SupplierQuotation | None:
        with transaction.atomic():
            quotation = self.quotation_repository.get_by_id(quotation_id, tenant_id)
            if not quotation or quotation.status != QuotationStatus.DRAFT:
                return None
            updated = self.quotation_repository.update(
                SupplierQuotation(
                    id=quotation.id,
                    tenant_id=quotation.tenant_id,
                    supplier_id=quotation.supplier_id,
                    warehouse_id=quotation.warehouse_id,
                    quotation_reference=quotation.quotation_reference,
                    quotation_date=quotation.quotation_date,
                    expiry_date=quotation.expiry_date,
                    validity_days=quotation.validity_days,
                    currency=quotation.currency,
                    payment_terms=quotation.payment_terms,
                    delivery_terms=quotation.delivery_terms,
                    status=QuotationStatus.SENT,
                    total_amount=quotation.total_amount,
                    notes=quotation.notes,
                )
            )
            SupplierQuotationSubmitted(
                tenant_id=tenant_id,
                quotation_id=quotation_id,
                supplier_id=quotation.supplier_id,
            ).emit()
            logger.info(f"SupplierQuotation submitted: {quotation_id} tenant={tenant_id}")
            return updated

    def accept(self, quotation_id: str, tenant_id: str) -> SupplierQuotation | None:
        with transaction.atomic():
            quotation = self.quotation_repository.get_by_id(quotation_id, tenant_id)
            if not quotation or quotation.status != QuotationStatus.SENT:
                return None
            updated = self.quotation_repository.update(
                SupplierQuotation(
                    id=quotation.id,
                    tenant_id=quotation.tenant_id,
                    supplier_id=quotation.supplier_id,
                    warehouse_id=quotation.warehouse_id,
                    quotation_reference=quotation.quotation_reference,
                    quotation_date=quotation.quotation_date,
                    expiry_date=quotation.expiry_date,
                    validity_days=quotation.validity_days,
                    currency=quotation.currency,
                    payment_terms=quotation.payment_terms,
                    delivery_terms=quotation.delivery_terms,
                    status=QuotationStatus.ACCEPTED,
                    total_amount=quotation.total_amount,
                    notes=quotation.notes,
                )
            )
            SupplierQuotationAccepted(
                tenant_id=tenant_id,
                quotation_id=quotation_id,
                supplier_id=quotation.supplier_id,
            ).emit()
            logger.info(f"SupplierQuotation accepted: {quotation_id} tenant={tenant_id}")
            return updated

    def reject(self, quotation_id: str, tenant_id: str, reason: str) -> SupplierQuotation | None:
        with transaction.atomic():
            quotation = self.quotation_repository.get_by_id(quotation_id, tenant_id)
            if not quotation or quotation.status != QuotationStatus.SENT:
                return None
            updated = self.quotation_repository.update(
                SupplierQuotation(
                    id=quotation.id,
                    tenant_id=quotation.tenant_id,
                    supplier_id=quotation.supplier_id,
                    warehouse_id=quotation.warehouse_id,
                    quotation_reference=quotation.quotation_reference,
                    quotation_date=quotation.quotation_date,
                    expiry_date=quotation.expiry_date,
                    validity_days=quotation.validity_days,
                    currency=quotation.currency,
                    payment_terms=quotation.payment_terms,
                    delivery_terms=quotation.delivery_terms,
                    status=QuotationStatus.REJECTED,
                    total_amount=quotation.total_amount,
                    notes=quotation.notes,
                )
            )
            SupplierQuotationRejected(
                tenant_id=tenant_id,
                quotation_id=quotation_id,
                supplier_id=quotation.supplier_id,
                reason=reason,
            ).emit()
            logger.info(f"SupplierQuotation rejected: {quotation_id} tenant={tenant_id}")
            return updated

    def expire(self, quotation_id: str, tenant_id: str) -> SupplierQuotation | None:
        with transaction.atomic():
            quotation = self.quotation_repository.get_by_id(quotation_id, tenant_id)
            if not quotation or quotation.status != QuotationStatus.SENT:
                return None
            updated = self.quotation_repository.update(
                SupplierQuotation(
                    id=quotation.id,
                    tenant_id=quotation.tenant_id,
                    supplier_id=quotation.supplier_id,
                    warehouse_id=quotation.warehouse_id,
                    quotation_reference=quotation.quotation_reference,
                    quotation_date=quotation.quotation_date,
                    expiry_date=quotation.expiry_date,
                    validity_days=quotation.validity_days,
                    currency=quotation.currency,
                    payment_terms=quotation.payment_terms,
                    delivery_terms=quotation.delivery_terms,
                    status=QuotationStatus.EXPIRED,
                    total_amount=quotation.total_amount,
                    notes=quotation.notes,
                )
            )
            SupplierQuotationExpired(
                tenant_id=tenant_id,
                quotation_id=quotation_id,
                supplier_id=quotation.supplier_id,
            ).emit()
            logger.info(f"SupplierQuotation expired: {quotation_id} tenant={tenant_id}")
            return updated