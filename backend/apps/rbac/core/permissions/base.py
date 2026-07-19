"""
RBAC permission classes for Django REST Framework.

Supports both decorator-based and DRF permission-class authorization.
"""

from rest_framework import permissions


class HasPermission(permissions.BasePermission):
    """
    DRF permission class that checks if the authenticated user
    has the required permission.

    Usage:
        class MyView(APIView):
            permission_classes = [HasPermission]
            required_permission = "inventory.products.edit"
    """

    message = "You do not have permission to perform this action."
    required_permission = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get required permission from view
        required = getattr(view, "required_permission", None)
        if not required:
            return True  # No permission required

        # Get tenant_id from request.actor (set by TenantMiddleware)
        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return False

        # Get user permissions from request.actor (populated by middleware)
        user_permissions = getattr(request.actor, "permissions", [])
        if not user_permissions:
            # Fallback: load from cache/DB if not in context
            from apps.rbac.application.services import AuthorizationService
            from apps.rbac.infrastructure.repositories import UserRoleRepository

            auth_service = AuthorizationService(user_role_repository=UserRoleRepository())
            user_permissions = auth_service.get_user_permissions(tenant_id, str(request.user.id))

        return self._check_permission(user_permissions, required)

    def _check_permission(self, user_permissions: list[str], required: str) -> bool:
        """Check if user has the required permission (supports wildcards)."""
        for perm in user_permissions:
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


class HasBranchAccess(permissions.BasePermission):
    """
    DRF permission class that checks if the user has access to the specified branch.

    Usage:
        class BranchView(APIView):
            permission_classes = [HasBranchAccess]
            branch_param = "branch_id"  # URL parameter name
    """

    message = "You do not have access to this branch."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Get branch_id from request
        branch_param = getattr(view, "branch_param", "branch_id")
        branch_id = request.query_params.get(branch_param) or request.data.get(branch_param)

        if not branch_id:
            return True  # No branch specified, allow

        # Get tenant_id from request.actor
        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return False

        # Check if user has access to this branch
        # User has access if they have a role with branch_id = null (all branches)
        # or branch_id = specific branch
        from apps.rbac.infrastructure.repositories import UserRoleRepository

        repo = UserRoleRepository()
        user_roles = repo.get_user_roles(tenant_id, str(request.user.id))

        for user_role in user_roles:
            if user_role.branch_id is None:
                return True  # Access to all branches
            if user_role.branch_id == branch_id:
                return True  # Access to this specific branch

        return False