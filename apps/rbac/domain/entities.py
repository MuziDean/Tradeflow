"""
Domain entities for the RBAC module.

Per Security Architecture: Roles, permissions, and access policies.
"""

from dataclasses import dataclass, field
from typing import List, Optional

from shared.ids.uuid import new_id_str


@dataclass
class Role:
    """
    Role entity representing a collection of permissions.

    Roles are assigned to users within a tenant scope.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    name: str = ""
    description: str = ""
    permissions: List[str] = field(default_factory=list)
    is_system_role: bool = False  # System roles cannot be deleted
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Permission:
    """
    Permission entity representing a specific action on a resource.

    Format: "module:action" (e.g., "sales:create", "payroll:approve")
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    codename: str = ""  # Unique permission identifier
    name: str = ""  # Human-readable name
    module: str = ""  # Module this permission belongs to
    action: str = ""  # Action allowed (create, read, update, delete, approve)
    description: str = ""


@dataclass
class BranchAccessPolicy:
    """
    Branch access policy for a role.

    Defines which branches a role can access.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    role_id: str = ""
    branch_ids: List[str] = field(default_factory=list)
    access_type: str = "allowed"  # allowed or denied