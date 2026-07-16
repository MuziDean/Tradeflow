"""
Application services for the RBAC module.

Per ADR-004: Application services orchestrate domain operations.
Per Security Architecture: RBAC authorization logic.

Phase 0: Architectural scaffold only.
Phase 1: Implement business logic.
"""

from typing import List

from apps.rbac.domain.entities import Role, Permission


class RBACService:
    """
    Application service for RBAC operations.

    Provides use cases for role management, permission checking,
    and branch access policy enforcement.

    Phase 0: Scaffold only.
    """

    def __init__(self, role_repository, permission_repository, policy_repository):
        self.role_repository = role_repository
        self.permission_repository = permission_repository
        self.policy_repository = policy_repository

    def create_role(self, tenant_id: str, name: str, description: str = "") -> Role:
        """Create a new role. Phase 1: implement business logic."""
        pass

    def assign_permissions(self, role_id: str, permission_codenames: List[str]) -> None:
        """Assign permissions to a role. Phase 1: implement business logic."""
        pass

    def check_permission(self, user_id: str, permission_codename: str) -> bool:
        """Check user permission. Phase 1: implement business logic."""
        pass