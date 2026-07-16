"""
API views for the platform module.

Per Backend Engineering Standards §5.1: Thin views that only:
- Authenticate and authorize
- Parse request input
- Call exactly one use-case
- Format response

Phase 1: Read-only tenant info endpoint. No business logic.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.platform.api.serializers import (
    CompanyProfileSerializer,
    TenantSerializer,
)
from apps.platform.infrastructure.models import Tenant


class TenantInfoView(APIView):
    """
    Returns current tenant info.
    Tenant context is resolved by TenantMiddleware.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TenantSerializer

    def get(self, request):
        tenant_id = request.actor.tenant_id
        if not tenant_id:
            return Response(
                {"error": "Tenant context not available."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tenant = Tenant.objects.filter(id=tenant_id).first()
        if not tenant:
            return Response(
                {"error": "Tenant not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TenantSerializer(tenant)
        return Response({"data": serializer.data})