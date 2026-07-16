"""
API serializers for the RBAC module.
"""

from rest_framework import serializers

from apps.rbac.domain.entities import Permission, Role, UserRole


class PermissionSerializer(serializers.Serializer):
    """Read-only permission output."""

    id = serializers.UUIDField()
    name = serializers.CharField()
    resource = serializers.CharField()
    action = serializers.CharField()
    description = serializers.CharField()
    is_wildcard = serializers.BooleanField()
    is_system = serializers.BooleanField()


class RoleSerializer(serializers.Serializer):
    """Role serializer with nested permissions."""

    id = serializers.UUIDField()
    tenant_id = serializers.UUIDField()
    name = serializers.CharField(max_length=100)
    description = serializers.CharField()
    is_system = serializers.BooleanField()
    is_active = serializers.BooleanField()
    permission_version = serializers.IntegerField()
    permissions = PermissionSerializer(many=True, read_only=True)


class RoleCreateSerializer(serializers.Serializer):
    """Role creation input."""

    name = serializers.CharField(max_length=100)
    description = serializers.CharField(required=False, default="")
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )


class UserRoleSerializer(serializers.Serializer):
    """User role assignment output."""

    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    role = RoleSerializer()
    branch_id = serializers.UUIDField(allow_null=True)
    assigned_by = serializers.UUIDField()
    assigned_at = serializers.DateTimeField()


class UserRoleAssignSerializer(serializers.Serializer):
    """User role assignment input."""

    role_id = serializers.UUIDField()
    branch_id = serializers.UUIDField(required=False, allow_null=True)