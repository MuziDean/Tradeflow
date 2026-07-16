"""
Domain entities for the platform module.

Per ADR-004: Entities represent the core business concepts and invariants.
"""

from dataclasses import dataclass, field
from typing import List

from shared.ids.uuid import new_id_str


@dataclass
class Tenant:
    """
    Tenant (company) entity.

    Represents a company/organization that uses TradeFlow.
    Each tenant is fully isolated from others.
    """

    id: str = field(default_factory=new_id_str)
    name: str = ""
    slug: str = ""  # Used for subdomain routing
    status: str = "active"
    subscription_plan: str = "basic"
    settings: dict = field(default_factory=dict)
    branding: dict = field(default_factory=dict)


@dataclass
class CompanyProfile:
    """
    Company profile entity.

    Extended profile information for a tenant.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    legal_name: str = ""
    registration_number: str = ""
    tax_id: str = ""
    address: dict = field(default_factory=dict)
    contact_email: str = ""
    contact_phone: str = ""
    logo_url: str = ""