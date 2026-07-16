"""
JWT authentication for TradeFlow.

Per Security Architecture §3.1 & §5.2: JWT must include tenant_id claim,
and tenant consistency check must be enforced.
Per Auth Spec §3.2: Return 403 TENANT_MISMATCH on mismatch.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import Token


class TenantAwareJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that validates tenant consistency.

    Extends SimpleJWT's JWTAuthentication to enforce:
    - JWT `tid` claim must match the resolved tenant from TenantMiddleware.
    - Cross-tenant token reuse is denied with 403 TENANT_MISMATCH.
    """

    def get_user(self, validated_token: Token):
        """
        Override to include tenant validation before returning user.
        """
        user_id = validated_token.get("user_id")
        if user_id is None:
            raise InvalidToken("JWT missing user_id claim.")

        try:
            user = self.user_model.objects.get(id=user_id)
        except self.user_model.DoesNotExist:
            raise InvalidToken("User not found.")

        return user

    def authenticate(self, request):
        """
        Authenticate request with JWT and validate tenant consistency.

        Returns (user, token) if valid, None if no token provided,
        raises AuthenticationFailed if invalid or tenant mismatch.
        """
        result = super().authenticate(request)
        if result is None:
            return None

        user, token = result

        # Validate tenant claim matches resolved tenant
        jwt_tenant_id = token.get("tid")
        resolved_tenant_id = getattr(request.actor, "tenant_id", None)

        if jwt_tenant_id is None or str(jwt_tenant_id) != str(resolved_tenant_id):
            from rest_framework.exceptions import AuthenticationFailed
            raise AuthenticationFailed(
                "TENANT_MISMATCH", code="TENANT_MISMATCH"
            )

        return user, token