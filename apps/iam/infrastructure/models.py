"""
Django models for the IAM module.

Per Database Design Section 4.2: user_account, security_event, password_reset_token.
Per Security Architecture: Users are tenant-scoped, passwords hashed, lockout enforced.
Per Backend Engineering Standards §2.4: models in infrastructure/ layer.
"""

from uuid import uuid4

from django.contrib.auth.hashers import make_password
from django.db import models

from infrastructure.db.base_model import TenantModel


class UserAccount(TenantModel):
    """
    Tenant-scoped user account model.

    Per DB Design §4.2: user_account (tenant-scoped; unique email per tenant).
    Per Security §3.1: User identities are tenant-scoped.
    Per Security §6.5: Passwords hashed via bcrypt/Argon2id.
    Per Security §3.8: Account lockout and progressive delays.
    """

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 30

    email = models.EmailField(db_index=True)
    password_hash = models.CharField(max_length=255)
    display_name = models.CharField(max_length=150, blank=True)
    status = models.CharField(
        max_length=20,
        default="active",
        choices=[
            ("active", "Active"),
            ("inactive", "Inactive"),
            ("suspended", "Suspended"),
            ("locked", "Locked"),
        ],
    )
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "iam_user_accounts"
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"
        unique_together = ("tenant_id", "email")
        indexes = [
            models.Index(fields=["tenant_id", "email"]),
            models.Index(fields=["tenant_id", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.email} ({self.tenant_id})"

    def set_password(self, raw_password: str) -> None:
        """Hash and set password using Django's hasher (bcrypt default)."""
        self.password_hash = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verify password against stored hash."""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.password_hash)


class SecurityEvent(models.Model):
    """
    Security telemetry event (non-audit, for detection/alerting).

    Per DB Design §4.2: security_event captures login failures, lockouts, etc.
    Per Security §11.3: Separate security telemetry from audit.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    user_id = models.UUIDField(null=True, blank=True)
    event_type = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=36, blank=True)
    details = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "iam_security_events"
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
        indexes = [
            models.Index(fields=["tenant_id", "created_at"]),
            models.Index(fields=["event_type", "created_at"]),
        ]


class PasswordResetToken(models.Model):
    """
    Single-use password reset token.

    Per Security §3.6: Single-use reset tokens with short TTL (15 minutes).
    Per Security §6.5: Tokens are hashed (not stored in plaintext).
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user = models.ForeignKey(
        UserAccount, on_delete=models.CASCADE, related_name="password_reset_tokens"
    )
    tenant_id = models.UUIDField(db_index=True)
    token_hash = models.CharField(max_length=255, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "iam_password_reset_tokens"
        verbose_name = "Password Reset Token"
        verbose_name_plural = "Password Reset Tokens"
        indexes = [
            models.Index(fields=["token_hash"]),
            models.Index(fields=["user", "used_at"]),
        ]