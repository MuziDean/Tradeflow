"""
Application services for RBAC.

Handles permission evaluation, role management, user role assignments.
Supports wildcard permissions (e.g., inventory.*, inventory.products.*).
"""

from uuid import UUID

from django.core.cache import cache
from django.utils import timezone

from apps.rbac.domain.entities import Permission, Role, RolePermission, UserRole
from apps.rbac.infrastructure.repositories import (
    PermissionRepository,
    RoleRepository,
    UserRoleRepository,
)


class AuthorizationService:
    """
    Core authorization service for permission evaluation.
    """

    def __init__(self, user_role_repository: UserRoleRepository):
        self.user_role_repository = user_role_repository

    def has_permission(self, tenant_id: str, user_id: str, required_permission: str) -> bool:
        """
        Check if user has the required permission.

        Supports wildcard matching:
        - If user has 'inventory.*', they can access 'inventory.products.edit'
        - If user has 'inventory.products.*', they can access 'inventory.products.edit'
        """
        permissions = self.get_user_permissions(tenant_id, user_id)
        return self._matches_any(permissions, required_permission)

    def get_user_permissions(self, tenant_id: str, user_id: str) -> list[str]:
        """
        Get list of permission names for user.
        Uses cache with version invalidation.
        """
        # Get permission version for cache invalidation
        role_repo = RoleRepository()
        user_roles = self.user_role_repository.get_user_roles(tenant_id, user_id)
        if not user_roles:
            return []

        # Use the highest permission_version among user's roles
        version = max(r.role.permission_version for r in user_roles)

        # Cache key includes permission_version for invalidation
        cache_key = f"permissions:{tenant_id}:{user_id}:{version}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Load permissions from DB
        perms = self.user_role_repository.get_user_permissions(tenant_id, user_id)
        perm_names = sorted([p.name for p in perms])

        # Cache for 15 minutes
        cache.set(cache_key, perm_names, 15 * 60)
        return perm_names

    def _matches_any(self, permissions: list[str], required: str) -> bool:
        """Check if required permission matches any of the user's permissions via wildcard."""
        for perm in permissions:
            if perm == required:
                return True
            if self._wildcard_match(perm, required):
                return True
        return False

    def _wildcard_match(self, pattern: str, candidate: str) -> bool:
        """Match permission pattern against candidate (supports * wildcard)."""
        if not pattern.endswith(".*"):
            return False

        prefix = pattern[:-1]  # Remove trailing '*'
        return candidate.startswith(prefix)


class PermissionService:
    """
    Service for managing permissions.
    Permissions are global system records.
    """

    def __init__(self, permission_repository: PermissionRepository):
        self.permission_repository = permission_repository

    def seed_system_permissions(self, permissions: list[dict]) -> None:
        """
        Seed system permissions into the database.
        Called during migration/initialization.
        """
        entities = []
        for p in permissions:
            entity = Permission(
                name=p["name"],
                resource=p["resource"],
                action=p["action"],
                description=p.get("description", ""),
                is_wildcard=p.get("is_wildcard", False),
                is_system=True,
            )
            entities.append(entity)
        self.permission_repository.bulk_create(entities)

    def list_all(self) -> list[Permission]:
        return self.permission_repository.list_global()


class RoleService:
    """
    Service for managing tenant-scoped roles.
    """

    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def create_role(self, tenant_id: str, name: str, description: str = "") -> Role:
        role = Role(tenant_id=tenant_id, name=name, description=description)
        return self.role_repository.create(role)

    def assign_permissions(self, role_id: str, permission_ids: list[str]) -> None:
        for pid in permission_ids:
            self.role_repository.add_permission(role_id, pid)

    def get_role_permissions(self, role_id: str) -> list[Permission]:
        return self.role_repository.get_role_permissions(role_id)


class UserRoleService:
    """
    Service for managing user-role assignments.
    """

    def __init__(self, user_role_repository: UserRoleRepository):
        self.user_role_repository = user_role_repository

    def assign_role(
        self, user_id: str, role_id: str, tenant_id: str, branch_id: str | None, assigned_by: str
    ) -> UserRole:
        return self.user_role_repository.assign_role(
            user_id=user_id,
            role_id=role_id,
            tenant_id=tenant_id,
            branch_id=branch_id,
            assigned_by=assigned_by,
        )

    def revoke_role(self, user_id: str, role_id: str, branch_id: str | None) -> bool:
        return self.user_role_repository.revoke_role(user_id, role_id, branch_id)

    def list_user_roles(self, tenant_id: str, user_id: str) -> list[UserRole]:
        return self.user_role_repository.get_user_roles(tenant_id, user_id)