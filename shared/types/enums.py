"""
Common enumerations and type definitions for TradeFlow.

Centralizes business-relevant enums to ensure consistency across modules.
"""

from enum import StrEnum


class UserStatus(StrEnum):
    """User account status."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    LOCKED = "locked"


class TenantStatus(StrEnum):
    """Tenant (company) subscription status."""

    ACTIVE = "active"
    TRIAL = "trial"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class EmploymentType(StrEnum):
    """Employee employment type."""

    PERMANENT = "permanent"
    CONTRACT = "contract"
    PART_TIME = "part_time"
    CASUAL = "casual"


class EmployeeStatus(StrEnum):
    """Employee lifecycle status."""

    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class PayrollRunStatus(StrEnum):
    """Payroll run state machine."""

    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    LOCKED = "locked"


class SaleStatus(StrEnum):
    """Sale transaction status."""

    COMPLETED = "completed"
    VOID = "void"
    REFUNDED = "refunded"


class StockMovementType(StrEnum):
    """Stock movement types."""

    SALE = "sale"
    GRN = "grn"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"
    ADJUSTMENT = "adjustment"
    RETURN = "return"
    STOCK_TAKE = "stock_take"


class PaymentMethod(StrEnum):
    """Payment methods."""

    CASH = "cash"
    CARD = "card"
    VOUCHER = "voucher"
    LAY_BY_DEPOSIT = "lay_by_deposit"
    CREDIT_NOTE = "credit_note"