"""
API serializers for the platform module.

Phase 1: Read-only tenant info + health endpoints.
No business logic — request parsing only per Backend Standards §6.2.
"""

from rest_framework import serializers

from apps.platform.infrastructure.models import CompanyProfile, Tenant


class TenantSerializer(serializers.Serializer):
    """Read-only tenant info response serializer."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    status = serializers.CharField()
    subscription_plan = serializers.CharField()


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Company profile serializer."""

    class Meta:
        model = CompanyProfile
        fields = [
            "legal_name", "registration_number", "tax_id",
            "address", "contact_email", "contact_phone", "logo_url",
        ]
        read_only_fields = fields