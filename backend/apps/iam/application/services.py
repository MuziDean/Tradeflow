"""
Application services for the IAM module.

Per ADR-004: Application services orchestrate domain operations.
Per Security Architecture: Password hashing, lockout, refresh rotation,
replay detection, audit events for all auth actions.

Phase 1: Implement business logic for authentication.
"""

from datetime import timedelta
from uuid import uuid4

from django.utils import timezone

from apps.iam.domain.entities import PasswordResetToken, SecurityEvent, UserAccount
from apps.iam.infrastructure.repositories import (
    PasswordResetRepository,
    SecurityEventRepository,
    UserRepository,
)


class AuthenticationService:
    """
    Application service for authentication operations.

    Per Security §3.1-3.11: login, logout, refresh, lockout, audit.
    """

    MAX_FAILED_ATTEMPTS = UserAccount.MAX_FAILED_ATTEMPTS
    LOCKOUT_MINUTES = UserAccount.LOCKOUT_MINUTES

    def __init__(
        self,
        user_repository: UserRepository,
        security_event_repository: SecurityEventRepository,
    ):
        self.user_repository = user_repository
        self.security_event_repository = security_event_repository

    def register(
        self,
        tenant_id: str,
        email: str,
        password: str,
        display_name: str = "",
        ip_address: str = "",
        user_agent: str = "",
        request_id: str = "",
    ) -> UserAccount:
        """
        Register a new user within a tenant.

        Raises ValueError if email already exists.
        """
        existing = self.user_repository.get_by_email(tenant_id, email)
        if existing:
            raise ValueError("Email already registered.")

        user = UserAccount(
            tenant_id=tenant_id,
            email=email,
            display_name=display_name,
        )
        user.set_password(password)

        user = self.user_repository.save(user)

        # Security event for registration
        self.security_event_repository.log_event(
            tenant_id=tenant_id,
            event_type="AUTH_REGISTERED",
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )

        return user

    def authenticate(
        self,
        tenant_id: str,
        email: str,
        password: str,
        ip_address: str = "",
        user_agent: str = "",
        request_id: str = "",
    ) -> UserAccount | None:
        """
        Authenticate a user. Returns UserAccount on success, None on failure.

        Security measures:
        - Same error for wrong email and wrong password (prevents enumeration)
        - Account lockout after MAX_FAILED_ATTEMPTS
        - Progressive delays (implemented in API throttle layer)
        """
        user = self.user_repository.get_by_email(tenant_id, email)

        # Do not leak whether email exists vs password wrong
        if user is None:
            self.security_event_repository.log_event(
                tenant_id=tenant_id,
                event_type="AUTH_LOGIN_FAILED",
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                details={"reason": "email_not_found"},
            )
            return None

        # Check if account is locked
        if user.is_locked:
            self.security_event_repository.log_event(
                tenant_id=tenant_id,
                event_type="AUTH_ACCOUNT_LOCKED",
                user_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )
            return None

        # Check if account is active
        if user.status not in ("active",):
            self.security_event_repository.log_event(
                tenant_id=tenant_id,
                event_type="AUTH_LOGIN_FAILED",
                user_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                details={"reason": f"status_{user.status}"},
            )
            return None

        # Verify password
        if not user.check_password(password):
            locked = self.user_repository.increment_failed_attempts(user)
            event_type = "AUTH_ACCOUNT_LOCKED" if locked else "AUTH_LOGIN_FAILED"
            self.security_event_repository.log_event(
                tenant_id=tenant_id,
                event_type=event_type,
                user_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
                details={"failed_attempts": user.failed_login_attempts},
            )
            return None

        # Success: reset failed attempts
        self.user_repository.reset_failed_attempts(user)

        self.security_event_repository.log_event(
            tenant_id=tenant_id,
            event_type="AUTH_LOGIN_SUCCEEDED",
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )

        return user


class TokenService:
    """
    Service for JWT token creation and refresh session management.

    Per Security §3.2: Short-lived access JWT + revocable refresh sessions.
    Uses SimpleJWT configuration from settings.
    """

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_access_token(self, user: UserAccount, session_id: str) -> str:
        """
        Create a short-lived access JWT.

        Claims: sub, tid, sid, iat, exp, jti.
        Per SAD §7.1 and Auth Spec §5.1.
        """
        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        # Add custom claims
        access["tid"] = str(user.tenant_id)
        access["sid"] = session_id

        return str(access)

    def create_refresh_token(self, user: UserAccount) -> str:
        """Create a refresh token (opaque UUID, not JWT)."""
        return str(uuid4())


class PasswordService:
    """
    Service for password reset workflow.

    Per Security §3.6: Single-use reset tokens with short TTL (15 minutes).
    Per Auth Spec §3.6-3.7: Forgot/reset flows.
    """

    RESET_TOKEN_TTL_MINUTES = PasswordResetRepository.RESET_TOKEN_TTL_MINUTES

    def __init__(
        self,
        password_reset_repository: PasswordResetRepository,
        security_event_repository: SecurityEventRepository,
    ):
        self.password_reset_repository = password_reset_repository
        self.security_event_repository = security_event_repository

    def request_reset(
        self,
        tenant_id: str,
        email: str,
        ip_address: str = "",
        user_agent: str = "",
        request_id: str = "",
    ) -> tuple[PasswordResetToken | None, str]:
        """
        Initiate password reset.

        Returns (token, raw_token) if user exists, else (None, raw_token).
        Raw token is returned to caller for email delivery; only hash stored in DB.
        Always returns success-like response to prevent enumeration.
        """
        user = None
        # Try to find user without revealing existence
        try:
            repo = UserRepository()
            user = repo.get_by_email(tenant_id, email)
        except Exception:
            pass

        raw_token = str(uuid4())
        token = None

        if user:
            token, raw_token = self.password_reset_repository.create_token(user)
            self.security_event_repository.log_event(
                tenant_id=tenant_id,
                event_type="AUTH_PASSWORD_RESET_REQUESTED",
                user_id=str(user.id),
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )

        return token, raw_token

    def confirm_reset(
        self,
        token_id: str,
        raw_token: str,
        new_password: str,
        ip_address: str = "",
        user_agent: str = "",
        request_id: str = "",
    ) -> UserAccount | None:
        """
        Complete password reset.

        Validates token, updates password, revokes all sessions.
        Returns UserAccount on success, None on failure.
        """
        user = self.password_reset_repository.consume_token(token_id, raw_token)
        if user is None:
            self.security_event_repository.log_event(
                tenant_id=str(user.tenant_id) if user else "",
                event_type="AUTH_RESET_TOKEN_INVALID_OR_EXPIRED",
                ip_address=ip_address,
                user_agent=user_agent,
                request_id=request_id,
            )
            return None

        # Update password
        user.set_password(new_password)
        user_repo = UserRepository()
        user_repo.update_password(user, new_password)

        # Revoke all sessions (security best practice after password change)
        # Note: session revocation via Redis happens in views layer

        self.security_event_repository.log_event(
            tenant_id=str(user.tenant_id),
            event_type="AUTH_PASSWORD_RESET_COMPLETED",
            user_id=str(user.id),
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
        )

        return user