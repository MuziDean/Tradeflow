"""
Actor context for TradeFlow.

Standardized context object attached to every authenticated request
containing user identity, tenant scope, branch scope, and role info.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ActorContext:
    """
    Represents the current authenticated actor for a request.

    Attached to request.actor by middleware and used throughout
    the application layer for tenant isolation, RBAC, and audit.

    Per documentation Section 8.3: Standardized actor context object.
    """

    tenant_id: Optional[str] = None
    """The tenant (company) this actor belongs to."""

    user_id: Optional[str] = None
    """The authenticated user's ID."""

    branch_ids: Optional[list[str]] = field(default_factory=list)
    """Branch scope for this actor. Empty = all branches (admin/owner)."""

    role_ids: Optional[list[str]] = field(default_factory=list)
    """Role assignments for permission evaluation."""

    request_id: Optional[str] = None
    """Correlation ID for tracing."""

    @property
    def is_authenticated(self) -> bool:
        """Whether the actor has been authenticated."""
        return self.user_id is not None

    @property
    def has_tenant_context(self) -> bool:
        """Whether tenant context has been resolved."""
        return self.tenant_id is not None