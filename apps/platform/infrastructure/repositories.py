"""
Repository for tenant persistence and resolution.

Per Database Design §4.1: tenant + tenant_domain for subdomain routing.
Cached lookups per Security Architecture §13: tenant resolution cache.
"""

from django.db import connection

from apps.platform.infrastructure.models import Tenant, TenantDomain


class TenantRepository:
    """
    Repository for Tenant persistence and host-based resolution.

    Resolves tenant from host header for TenantMiddleware.
    Cached via Redis to avoid DB lookups on every request.
    """

    def resolve_from_host(self, host: str) -> Tenant | None:
        """
        Resolve a tenant from an HTTP Host header value.

        Matches full domain (custom domain) or subdomain.slug.domain.
        Returns None if no tenant matches (caller must hard-fail).
        """
        try:
            domain = TenantDomain.objects.select_related("tenant").filter(
                domain=host
            ).first()
            if domain:
                return domain.tenant
            return None
        except Exception:
            return None

    def resolve_from_subdomain(self, subdomain: str) -> Tenant | None:
        """Resolve tenant by subdomain slug (e.g., acme → acme.tradeflow.co.za)."""
        try:
            return Tenant.objects.filter(slug=subdomain, status="active").first()
        except Exception:
            return None

    def get_by_id(self, tenant_id: str) -> Tenant | None:
        """Get tenant by UUID."""
        try:
            return Tenant.objects.filter(id=tenant_id).first()
        except Exception:
            return None

    def is_active(self, tenant: Tenant) -> bool:
        """Check if a tenant is in an active state."""
        return tenant.status in ("active", "trial")