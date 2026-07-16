"""
Base permission classes for TradeFlow.

Provides tenant-aware and branch-scoped permission base classes
that all DRF views should use.
"""

from rest_framework.permissions import BasePermission, IsAuthenticated


class TenantAwarePermission(IsAuthenticated):
    """
    Base permission that ensures the request has a valid tenant context.

    All views in TradeFlow should inherit from this or a more specific
    permission class to ensure tenant isolation.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.actor is not None and request.actor.has_tenant_context


class IsSystemAdmin(BasePermission):
    """
    Permission for system-level operations (not tenant-scoped).
    Restricted to platform administrators.
    """

    def has_permission(self, request, view):
        return request.user is not None and request.user.is_staff