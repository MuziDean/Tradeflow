"""
Tenant resolution middleware.

Per Security Architecture §5.1: Tenant is resolved from the request host
(subdomain/custom domain). Every request carries an immutable tenant context
throughout execution.

Layer 1 of defense-in-depth (Security §5.2):
- Application layer: automatic tenant scoping via TenantAwareManager.
- Database layer: RLS via app.tenant_id session variable.

Hard-fail on missing tenant context per Security §1.7 and Backend §8.4.
Public endpoints (health check, sign-up) must explicitly bypass tenant
resolution via the public_paths allowlist.
"""

import logging

from django.db import connection
from django.utils.deprecation import MiddlewareMixin

from apps.platform.infrastructure.repositories import TenantRepository
from core.context.actor import ActorContext

logger = logging.getLogger("tradeflow.middleware.tenant")

# Endpoints that do not require tenant context (health, sign-up, auth, docs)
PUBLIC_PATHS = (
    "/api/v1/health/",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/password/reset",
    "/api/schema/",
    "/api/docs/",
)


class TenantMiddleware(MiddlewareMixin):
    """
    Resolves tenant context from the request Host header.

    Process flow:
    1. Skip tenant resolution for PUBLIC_PATHS (set stub context).
    2. Extract subdomain from host (e.g. acme.tradeflow.co.za → acme).
    3. Look up TenantDomain or Tenant.slug in the DB.
    4. Set request.actor with tenant context.
    5. Set connection.tenant_id for TenantModel auto-scoping and RLS.
    6. Hard-fail (raise 403) if tenant cannot be resolved for protected paths.
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.tenant_repository = TenantRepository()

    def process_request(self, request):
        host = request.get_host().split(":")[0]  # Strip port
        path = request.path_info

        # Default: unauthenticated, no tenant context
        request.actor = ActorContext(
            tenant_id=None,
            user_id=None,
            branch_ids=[],
            role_ids=[],
            request_id=getattr(request, "request_id", None),
        )

        # Public endpoints bypass tenant resolution
        if path.startswith(PUBLIC_PATHS):
            return None

        # Resolve tenant from host
        tenant = self.tenant_repository.resolve_from_host(host)

        # Fallback: try subdomain (e.g. acme.tradeflow.co.za → slug "acme")
        if tenant is None:
            parts = host.split(".")
            if len(parts) >= 3 and parts[0] != "www":
                tenant = self.tenant_repository.resolve_from_subdomain(parts[0])

        if tenant is None:
            logger.warning(
                "Tenant not found for host=%s path=%s", host, path
            )
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden(
                "Tenant not found or inactive. Check your subdomain."
            )

        if not self.tenant_repository.is_active(tenant):
            logger.warning(
                "Inactive tenant access attempt: tenant=%s host=%s",
                tenant.id, host,
            )
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden(
                "This account is not active. Contact support."
            )

        # Set tenant context on the request
        request.actor.tenant_id = str(tenant.id)

        # Set database session variable for TenantModel auto-scoping
        connection.tenant_id = str(tenant.id)

        # Set PostgreSQL session variable for RLS enforcement (Layer 2)
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET app.tenant_id = %s", [str(tenant.id)]
                )
        except Exception:
            logger.exception("Failed to set app.tenant_id for RLS")

        logger.debug(
            "Tenant resolved: tenant=%s host=%s path=%s",
            tenant.id, host, path,
        )

        return None

    def process_response(self, request, response):
        # Clean up tenant context from the connection
        if hasattr(connection, "tenant_id"):
            connection.tenant_id = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SET app.tenant_id = ''")
        except Exception:
            pass
        return response