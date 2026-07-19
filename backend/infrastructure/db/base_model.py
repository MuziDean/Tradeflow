"""
Base model classes for TradeFlow.

Per Database Design (Section 30, 38) and Security Architecture (Section 5.2):
All tenant-scoped models inherit from TenantModel which provides tenant_id
(NOT NULL, indexed first in access-path composites) + automatic query scoping.
PostgreSQL Row Level Security (RLS) provides defense-in-depth Layer 2, keyed
off the `app.tenant_id` session variable set by TenantMiddleware.

Tenant isolation rules (non-negotiable):
- tenant_id is NEVER accepted from request body/query params (Security §5.4).
- tenant_id is injected from the resolved request context (connection.tenant_id).
- Missing tenant context is a hard fail (Security §1.7, Backend §8.4).
"""

import logging
from uuid import uuid4

from django.db import connection, models
from django.utils import timezone

logger = logging.getLogger(__name__)


class TenantModel(models.Model):
    """
    Abstract base model for all tenant-scoped models.

    Provides:
    - UUID primary key (Database Design §8: UUID PK for all entities).
    - tenant_id (NOT NULL, indexed) injected from the request context.
    - Automatic tenant scoping via TenantAwareManager.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True, null=False, editable=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        default_permissions = ("add", "change", "delete", "view")

    def save(self, *args, **kwargs):
        # Tenant context is resolved by TenantMiddleware and stored on the
        # DB connection (connection.tenant_id). We never trust client-supplied
        # tenant identifiers (Security Architecture §5.4).
        if self.tenant_id is None:
            tenant_id = getattr(connection, "tenant_id", None)
            if tenant_id is None:
                # Hard fail: no tenant context means cross-tenant write risk.
                raise RuntimeError(
                    "Cannot save tenant-scoped model without tenant context. "
                    "TenantMiddleware must resolve tenant before writes."
                )
            self.tenant_id = tenant_id
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"


class TenantAwareManager(models.Manager):
    """
    Manager that automatically filters by the active request tenant.

    Uses connection.tenant_id (set by TenantMiddleware) so all reads are
    automatically scoped. When no tenant context is set (e.g. management
    commands, platform-level queries), returns the full queryset — callers
    must scope explicitly via .for_tenant().
    """

    def get_queryset(self):
        qs = super().get_queryset()
        tenant_id = getattr(connection, "tenant_id", None)
        if tenant_id is not None:
            return qs.filter(tenant_id=tenant_id)
        return qs

    def for_tenant(self, tenant_id):
        """Explicitly scope a queryset to a tenant (no context required)."""
        return self.get_queryset().filter(tenant_id=tenant_id)


class TenantQuerySet(models.QuerySet):
    """
    Custom QuerySet with tenant-aware filtering methods.
    """

    def for_tenant(self, tenant_id):
        """Filter queryset to a specific tenant."""
        return self.filter(tenant_id=tenant_id)
