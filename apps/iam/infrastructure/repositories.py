"""
Repository layer for IAM persistence.

Per Backend Engineering Standards §5.7: Repositories encapsulate persistence
operations per aggregate. Enforce tenant-aware access patterns.
"""

from datetime import timedelta
from uuid import uuid4

from django.utils import timezone

from apps.iam.infrastructure.models import (
    PasswordResetToken,
    SecurityEvent,
    UserAccount,
)


class UserRepository:
    """Repository for UserAccount persistence and queries."""

    def get_by_email(self, tenant_id: str, email: str) -> UserAccount | None:
        """Get user by tenant-scoped email. Returns None if not found."""
        try:
            return UserAccount.objects.filter(
                tenant_id=tenant_id, email=email
            ).first()
        except Exception:
            return None

    def get_by_id(self, user_id: str) -> UserAccount | None:
        """Get user by UUID."""
        try:
            return UserAccount.objects.filter(id=user_id).first()
        except Exception:
            return None

    def save(self, user: UserAccount) -> UserAccount:
        """Persist a user account."""
        user.save()
        return user

    def update_password(self, user: UserAccount, new_password: str) -> None:
        """Update user's password hash."""
        user.set_password(new_password)
        user.save(update_fields=["password_hash", "updated_at"])

    def increment_failed_attempts(self, user: UserAccount) -> bool:
        """
        Increment failed login counter. Returns True if account locked.
        Security §3.8: Account lockout and progressive delays.
        """
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= UserAccount.MAX_FAILED_ATTEMPTS:
            user.locked_until = timezone.now() + timedelta(
                minutes=UserAccount.LOCKOUT_MINUTES
            )
            user.save(update_fields=["failed_login_attempts", "locked_until", "updated_at"])
            return True
        user.save(update_fields=["failed_login_attempts", "updated_at"])
        return False

    def reset_failed_attempts(self, user: UserAccount) -> None:
        """Reset failed login counter on successful login."""
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = timezone.now()
        user.save(
            update_fields=[
                "failed_login_attempts", "locked_until",
                "last_login_at", "updated_at",
            ]
        )


class PasswordResetRepository:
    """Repository for password reset token persistence."""

    RESET_TOKEN_TTL_MINUTES = 15

    def create_token(self, user: UserAccount) -> tuple[PasswordResetToken, str]:
        """
        Create a single-use password reset token.

        Per Security §3.6: Single-use reset tokens with short TTL (15 minutes).
        Per Security §6.5: Tokens are hashed (not stored in plaintext).
        """
        from django.contrib.auth.hashers import make_password

        raw_token = str(uuid4())
        token = PasswordResetToken(
            user=user,
            tenant_id=user.tenant_id,
            token_hash=make_password(raw_token),
            expires_at=timezone.now()
            + timedelta(minutes=self.RESET_TOKEN_TTL_MINUTES),
        )
        token.save()
        # Return the raw token to the caller (for email). Only hash stored in DB.
        return token, raw_token

    def consume_token(self, token_id: str, raw_token: str) -> UserAccount | None:
        """
        Validate and consume a reset token.

        Returns the UserAccount if valid, None otherwise.
        Token is marked as used (single-use enforcement).
        """
        from django.contrib.auth.hashers import check_password

        try:
            token = PasswordResetToken.objects.select_related("user").get(
                id=token_id, used_at__isnull=True
            )
        except PasswordResetToken.DoesNotExist:
            return None

        # Verify token hash
        if not check_password(raw_token, token.token_hash):
            return None

        # Check expiry
        if timezone.now() > token.expires_at:
            return None

        # Mark as used (single-use)
        token.used_at = timezone.now()
        token.save(update_fields=["used_at"])

        return token.user


class SecurityEventRepository:
    """Repository for security event persistence."""

    def log_event(
        self,
        tenant_id: str,
        event_type: str,
        user_id: str | None = None,
        ip_address: str = "",
        user_agent: str = "",
        request_id: str = "",
        details: dict | None = None,
    ) -> SecurityEvent:
        """Record a security telemetry event."""
        event = SecurityEvent(
            tenant_id=tenant_id,
            user_id=user_id,
            event_type=event_type,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            details=details or {},
        )
        event.save()
        return event