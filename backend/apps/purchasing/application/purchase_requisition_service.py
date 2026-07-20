"""
Application service for PurchaseRequisition.

Business rules:
- Draft requisition can be updated
- Submitted requisition goes to Pending Approval
- Approved requisition can be converted to Purchase Order
- Rejected requisition cannot be modified
- Cancelled requisition is archived
- Full audit trail preserved
"""

import logging
from datetime import datetime

from django.db import transaction

from apps.purchasing.domain.entities import PurchaseRequisition, PurchaseRequisitionLine
from apps.purchasing.infrastructure.repositories import PurchaseRequisitionLineRepository, PurchaseRequisitionRepository
from shared.events.purchasing_events import PurchaseRequisitionApproved, PurchaseRequisitionConverted, PurchaseRequisitionCreated, PurchaseRequisitionRejected
from shared.types.enums import PurchaseRequisitionStatus
from shared.time.helpers import now

logger = logging.getLogger("tradeflow.purchasing")


class PurchaseRequisitionService:
    """Service for PurchaseRequisition."""

    def __init__(self, requisition_repository: PurchaseRequisitionRepository,
                 line_repository: PurchaseRequisitionLineRepository):
        self.requisition_repository = requisition_repository
        self.line_repository = line_repository

    def list_for_tenant(self, tenant_id: str, status: str = "") -> list[PurchaseRequisition]:
        return self.requisition_repository.list_for_tenant(tenant_id, status)

    def get_by_id(self, requisition_id: str, tenant_id: str) -> PurchaseRequisition | None:
        return self.requisition_repository.get_by_id(requisition_id, tenant_id)

    def create(self, requisition: PurchaseRequisition, lines: list[PurchaseRequisitionLine]) -> PurchaseRequisition:
        with transaction.atomic():
            created = self.requisition_repository.create(requisition)
            for line in lines:
                line.requisition_id = created.id
                self.line_repository.create(line)
            PurchaseRequisitionCreated(
                tenant_id=requisition.tenant_id,
                requisition_id=created.id,
                warehouse_id=created.warehouse_id,
                requested_by=created.requested_by,
            ).emit()
            logger.info(f"PurchaseRequisition created: {created.id} tenant={requisition.tenant_id}")
            return created

    def update(self, requisition: PurchaseRequisition) -> PurchaseRequisition:
        with transaction.atomic():
            updated = self.requisition_repository.update(requisition)
            logger.info(f"PurchaseRequisition updated: {updated.id} tenant={updated.tenant_id}")
            return updated

    def submit_for_approval(self, requisition_id: str, tenant_id: str) -> PurchaseRequisition | None:
        with transaction.atomic():
            requisition = self.requisition_repository.get_by_id(requisition_id, tenant_id)
            if not requisition or requisition.status != PurchaseRequisitionStatus.DRAFT:
                return None
            updated = self.requisition_repository.update(
                PurchaseRequisition(
                    id=requisition.id,
                    tenant_id=requisition.tenant_id,
                    warehouse_id=requisition.warehouse_id,
                    requested_by=requisition.requested_by,
                    required_date=requisition.required_date,
                    justification=requisition.justification,
                    status=PurchaseRequisitionStatus.PENDING_APPROVAL,
                    approved_by=requisition.approved_by,
                    rejected_reason=requisition.rejected_reason,
                    total_estimated_amount=requisition.total_estimated_amount,
                    currency=requisition.currency,
                    notes=requisition.notes,
                )
            )
            logger.info(f"PurchaseRequisition submitted for approval: {requisition_id} tenant={tenant_id}")
            return updated

    def approve(self, requisition_id: str, tenant_id: str, approved_by: str) -> PurchaseRequisition | None:
        with transaction.atomic():
            requisition = self.requisition_repository.get_by_id(requisition_id, tenant_id)
            if not requisition or requisition.status != PurchaseRequisitionStatus.PENDING_APPROVAL:
                return None
            updated = self.requisition_repository.update(
                PurchaseRequisition(
                    id=requisition.id,
                    tenant_id=requisition.tenant_id,
                    warehouse_id=requisition.warehouse_id,
                    requested_by=requisition.requested_by,
                    required_date=requisition.required_date,
                    justification=requisition.justification,
                    status=PurchaseRequisitionStatus.APPROVED,
                    approved_by=approved_by,
                    rejected_reason=requisition.rejected_reason,
                    total_estimated_amount=requisition.total_estimated_amount,
                    currency=requisition.currency,
                    notes=requisition.notes,
                )
            )
            PurchaseRequisitionApproved(
                tenant_id=tenant_id,
                requisition_id=requisition_id,
                approved_by=approved_by,
            ).emit()
            logger.info(f"PurchaseRequisition approved: {requisition_id} tenant={tenant_id}")
            return updated

    def reject(self, requisition_id: str, tenant_id: str, rejected_by: str, reason: str) -> PurchaseRequisition | None:
        with transaction.atomic():
            requisition = self.requisition_repository.get_by_id(requisition_id, tenant_id)
            if not requisition or requisition.status != PurchaseRequisitionStatus.PENDING_APPROVAL:
                return None
            updated = self.requisition_repository.update(
                PurchaseRequisition(
                    id=requisition.id,
                    tenant_id=requisition.tenant_id,
                    warehouse_id=requisition.warehouse_id,
                    requested_by=requisition.requested_by,
                    required_date=requisition.required_date,
                    justification=requisition.justification,
                    status=PurchaseRequisitionStatus.REJECTED,
                    approved_by=requisition.approved_by,
                    rejected_reason=reason,
                    total_estimated_amount=requisition.total_estimated_amount,
                    currency=requisition.currency,
                    notes=requisition.notes,
                )
            )
            PurchaseRequisitionRejected(
                tenant_id=tenant_id,
                requisition_id=requisition_id,
                rejected_by=rejected_by,
                reason=reason,
            ).emit()
            logger.info(f"PurchaseRequisition rejected: {requisition_id} tenant={tenant_id}")
            return updated

    def cancel(self, requisition_id: str, tenant_id: str) -> PurchaseRequisition | None:
        with transaction.atomic():
            requisition = self.requisition_repository.get_by_id(requisition_id, tenant_id)
            if not requisition or requisition.status not in [PurchaseRequisitionStatus.DRAFT, PurchaseRequisitionStatus.PENDING_APPROVAL]:
                return None
            updated = self.requisition_repository.update(
                PurchaseRequisition(
                    id=requisition.id,
                    tenant_id=requisition.tenant_id,
                    warehouse_id=requisition.warehouse_id,
                    requested_by=requisition.requested_by,
                    required_date=requisition.required_date,
                    justification=requisition.justification,
                    status=PurchaseRequisitionStatus.CANCELLED,
                    approved_by=requisition.approved_by,
                    rejected_reason=requisition.rejected_reason,
                    total_estimated_amount=requisition.total_estimated_amount,
                    currency=requisition.currency,
                    notes=requisition.notes,
                )
            )
            logger.info(f"PurchaseRequisition cancelled: {requisition_id} tenant={tenant_id}")
            return updated

    def convert_to_purchase_order(self, requisition_id: str, tenant_id: str, purchase_order_id: str) -> PurchaseRequisition | None:
        with transaction.atomic():
            requisition = self.requisition_repository.get_by_id(requisition_id, tenant_id)
            if not requisition or requisition.status != PurchaseRequisitionStatus.APPROVED:
                return None
            updated = self.requisition_repository.update(
                PurchaseRequisition(
                    id=requisition.id,
                    tenant_id=requisition.tenant_id,
                    warehouse_id=requisition.warehouse_id,
                    requested_by=requisition.requested_by,
                    required_date=requisition.required_date,
                    justification=requisition.justification,
                    status=PurchaseRequisitionStatus.CONVERTED,
                    approved_by=requisition.approved_by,
                    rejected_reason=requisition.rejected_reason,
                    total_estimated_amount=requisition.total_estimated_amount,
                    currency=requisition.currency,
                    notes=requisition.notes,
                )
            )
            PurchaseRequisitionConverted(
                tenant_id=tenant_id,
                requisition_id=requisition_id,
                purchase_order_id=purchase_order_id,
            ).emit()
            logger.info(f"PurchaseRequisition converted to PO: {requisition_id} -> {purchase_order_id} tenant={tenant_id}")
            return updated