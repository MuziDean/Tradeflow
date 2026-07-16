"""
Domain entities for the RBAC module.

Per amendment: Permissions are global system records. Roles are tenant-scoped.
Supports wildcard permissions (e.g., inventory.*, inventory.products.*).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from shared.ids.uuid import new_id_str
from shared.time.helpers import now


@dataclass
class Permission:
    """
    Global permission definition (not tenant-scoped).
    Permissions are system-wide and shared across all tenants.
    """

    id: str = field(default_factory=new_id_str)
    name: str = ""  # e.g., "inventory.products.edit"
    resource: str = ""  # e.g., "inventory.products"
    action: str = ""  # e.g., "edit"
    description: str = ""
    is_wildcard: bool = False
    is_system: bool = False
    created_at: datetime = field(default_factory=now)

    @property
    def full_name(self) -> str:
        return f"{self.resource}.{self.action}"


@dataclass
class Role:
    """
    Tenant-scoped role.
    Roles belong to a specific tenant and define a set of permissions.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    description: str = ""
    is_system: bool = False
    is_active: bool = True
    permission_version: int = 0  # For cache invalidation
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)


@dataclass
class RolePermission:
    """
    Many-to-many relationship between Role and Permission.
    """

    id: str = field(default_factory=new_id_str)
    role_id: str = ""
    permission_id: str = ""
    created_at: datetime = field(default_factory=now)


@dataclass
class UserRole:
    """
    User-Role assignment with optional branch scope.

    Branch scoping:
    - branch_id = null: user has role for all branches (Owner/Admin)
    - branch_id = specific: user has role only for that branch
    """

    id: str = field(default_factory=new_id_str)
    user_id: str = ""
    role_id: str = ""
    tenant_id: str = ""
    branch_id: Optional[str] = None  # None = all branches
    assigned_by: str = ""  # User ID who assigned this role
    assigned_at: datetime = field(default_factory=now)