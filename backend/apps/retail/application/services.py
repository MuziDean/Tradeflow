"""
Application services for the retail module.

Per ADR-004: Application services orchestrate domain operations.

Phase 0: Architectural scaffold only.
Phase 1: Implement business logic.
"""

from decimal import Decimal

from apps.retail.domain.entities import Sale, SaleItem


class RetailService:
    """
    Application service for retail operations.

    Provides use cases for sales, invoices, and POS transactions.

    Phase 0: Scaffold only.
    """

    def __init__(self, sale_repository, product_repository):
        self.sale_repository = sale_repository
        self.product_repository = product_repository

    def create_sale(
        self,
        tenant_id: str,
        branch_id: str,
        user_id: str,
        items: list,
        payment_method: str,
        customer_id: str = "",
    ) -> Sale:
        """Create a new sale. Phase 1: implement business logic."""
        pass

    def _generate_invoice_number(self, branch_id: str, last_sale) -> str:
        """Generate unique invoice number for a branch. Phase 1: implement business logic."""
        pass