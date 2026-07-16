"""
Domain entities for the retail module.

Per ADR-004: Entities represent the core business concepts and invariants.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

from shared.ids.uuid import new_id_str
from shared.time.helpers import now


@dataclass
class Sale:
    """
    Sale entity representing a completed transaction.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    branch_id: str = ""
    user_id: str = ""
    customer_id: str = ""
    invoice_number: str = ""
    subtotal: Decimal = field(default=Decimal("0.00"))
    tax_amount: Decimal = field(default=Decimal("0.00"))
    discount_amount: Decimal = field(default=Decimal("0.00"))
    total: Decimal = field(default=Decimal("0.00"))
    payment_method: str = "cash"
    status: str = "completed"  # completed, void, refunded
    created_at: str = field(default_factory=now)


@dataclass
class SaleItem:
    """
    Sale item entity representing a line item in a sale.
    """

    id: str = field(default_factory=new_id_str)
    sale_id: str = ""
    product_id: str = ""
    quantity: Decimal = field(default=Decimal("1"))
    unit_price: Decimal = field(default=Decimal("0.00"))
    discount: Decimal = field(default=Decimal("0.00"))
    total: Decimal = field(default=Decimal("0.00"))