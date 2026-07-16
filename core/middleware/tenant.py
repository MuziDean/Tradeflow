"""
Tenant middleware for multi-tenant isolation.

Resolves tenant from request host and sets:
- connection.tenant_id (for TenantModel)
- request.actor.tenant_id
- request.actor.permissions (RBAC)
"""

from uuid import UUID

from django.db import connection
from django.utils.deprecation import MiddlewareMixin

from apps.rbac.application.services import AuthorizationService
from apps.rbac.infrastructure.repositories import UserRoleRepository


class TenantMiddleware(MiddlewareMixin):
    """
    Resolve tenant from request host header.
    Sets connection.tenant_id for TenantModel auto-filtering.
    """

    def process_request(self, request):
        host = request.get_host()
        tenant_id = self._extract_tenant_id(host)

        if not tenant_id:
            # Allow health check and auth endpoints without tenant
            if request.path.startswith("/api/v1/health") or request.path.startswith("/api/v1/auth"):
                return None
            return None  # Or return 400/404 depending on strategy

        # Set connection tenant for TenantModel
        connection.tenant_id = tenant_id

        # Set actor context
        class Actor:
            tenant_id = tenant_id
            permissions = []

        request.actor = Actor()

        # If user is authenticated, load their permissions
        if request.user and request.user.is_authenticated:
            self._load_user_permissions(request, tenant_id)

        return None

    def _extract_tenant_id(self, host: str) -> str | None:
        """
        Extract tenant_id from host.
        Supports:
        - Subdomain: tenant1.example.com
        - Header: X-Tenant-ID (fallback)
        """
        # Subdomain extraction
        parts = host.split(".")
        if len(parts) >= 3:
            subdomain = parts[0]
            if subdomain not in ("www", "api"):
                return subdomain

        return None

    def _load_user_permissions(self, request, tenant_id: str):
        """Load user permissions into request.actor."""
        try:
            auth_service = AuthorizationService(user_role_repository=UserRoleRepository())
            permissions = auth_service.get_user_permissions(tenant_id, str(request.user.id))
            request.actor.permissions = permissions
        except Exception:
            request.actor.permissions = []