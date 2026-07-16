"""
Django models for the IAM module.

Per Security Architecture: Users, sessions, and password reset tokens.
"""

from django.db import models

from shared.ids.uuid import new_id_str
from infrastructure.db.base_model import TenantModel


class User(TenantModel):
    """
    Django user model for TradeFlow.

    Extends TenantModel with authentication-specific fields.
    """

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20, blank=True)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, default="active")
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "iam_users"
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self) -> str:
        return self.email


class Session(models.Model):
    """
    User session model for tracking active sessions.
    """

    id = models.CharField(primary_key=True, max_length=36, default=new_id_str)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    tenant_id = models.CharField(max_length=36, db_index=True)
    device_type = models.CharField(max_length=20)  # web, mobile, pos
    refresh_token_jti = models.CharField(max_length=36, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    last_activity =models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "iam_sessions"
        indexes = [
            models.Index(fields=["user", "device_type", "is_active"]),
            models.Index(fields=["refresh_token_jti"]),
        ]


class PasswordResetToken(models.Model):
    """
    Password reset token model.
    """

    id = models.CharField(primary_key=True, max_length=36, default=new_id_str)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="password_reset_tokens")
    token = models.CharField(max_length=100, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "iam_password_reset_tokens"