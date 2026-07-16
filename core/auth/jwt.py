"""
JWT authentication backend for TradeFlow.

Configures the SimpleJWT authentication backend to extract tenant context
from JWT claims and populate the ActorContext.

Per documentation Section 7.1: JWT must include sub, tenant_id, branch_ids, iat, exp, jti.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication as BaseJWTAuthentication


class JWTAuthentication(BaseJWTAuthentication):
    """
    Custom JWT authentication that extracts tenant and branch context
    from token claims into the ActorContext.

    JWT payload includes:
    - sub: user_id
    - tenant_id: tenant UUID
    - branch_ids: list of branch UUIDs (optional)
    - role_ids: list of role IDs
    """

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            user, validated_token = result
            # Extract tenant context from token claims
            tenant_id = validated_token.get("tenant_id")
            branch_ids = validated_token.get("branch_ids", [])
            role_ids = validated_token.get("role_ids", [])

            # Update actor context on request
            if hasattr(request, "actor"):
                request.actor.tenant_id = tenant_id
                request.actor.user_id = str(user.id) if user else None
                request.actor.branch_ids = branch_ids
                request.actor.role_ids = role_ids
                request.actor.request_id = getattr(request, "request_id", None)

        return result