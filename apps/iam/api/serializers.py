"""
API serializers for the IAM module.

Per Auth Spec §3: Validation, response envelopes, error codes.
Per Backend Engineering Standards §6.2: Serializer responsibilities.
"""

from rest_framework import serializers

from apps.iam.domain.entities import UserAccount


class LoginSerializer(serializers.Serializer):
    """Request serializer for POST /auth/login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    remember_me = serializers.BooleanField(default=False, required=False)


class RegisterSerializer(serializers.Serializer):
    """Request serializer for POST /auth/register."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=12)
    display_name = serializers.CharField(max_length=150, required=False, default="")


class UserSerializer(serializers.Serializer):
    """Read-only user profile output."""

    id = serializers.UUIDField()
    email = serializers.EmailField()
    display_name = serializers.CharField()
    status = serializers.CharField()
    last_login_at = serializers.DateTimeField(allow_null=True)


class TokenRefreshSerializer(serializers.Serializer):
    """Request serializer for POST /auth/token/refresh."""

    refresh_token = serializers.CharField(required=False)


class PasswordResetRequestSerializer(serializers.Serializer):
    """Request serializer for POST /auth/password/reset."""

    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Request serializer for POST /auth/password/reset/confirm."""

    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=12)