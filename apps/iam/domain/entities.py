"""
Domain entities for the IAM module.

Per ADR-004: Entities represent the core business concepts and invariants.
Per Security Architecture: MAX_FAILED_ATTEMPTS = 5, LOCKOUT_MINUTES = 30.
Per Database Design Section 4.2: user_account, security_event.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from shared.ids.uuid import new_id_str
from shared.time.helpers import now


@dataclass
class UserAccount:
    """
    User entity representing an authenticated individual within a tenant.

    Security rules:
    - Failed login attempts locked after MAX_FAILED_ATTEMPTS.
    - Lockout duration is LOCKOUT_MINUTES.
    - Password is stored hashed (bcrypt/Argon2id) per Security §6.5.
    """

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 30

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    email: str = ""
    password_hash: str = ""
    display_name: str = ""
    status: str = "active"  # active, inactive, suspended, locked
    is_staff: bool = False
    is_superuser: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    @property
    def is_locked(self) -> bool:
        """Check if user is currently locked out."""
        if self.locked_until is None:
            return False
        return now() < self.locked_until

    def increment_failed_attempts(self) -> bool:
        """
        Increment failed login counter. Returns True if account should be locked.
        Security §3.8: Account lockout and progressive delays.
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.locked_until = now().replace(
                hour=(now().hour + (now().minute + self.LOCKOUT_MINUTES) // 60) % 24,
                minute=(now().minute + self.LOCKOUT_MINUTES) % 60,
            )
            return True
        return False

    def reset_failed_attempts(self) -> None:
        """Reset failed login counter on successful login."""
        self.failed_login_attempts = 0
        self.locked_until = None


@dataclass
class SecurityEvent:
    """
    Security event entity for non-audit security telemetry.

    Per DB Design §4.2: security_event captures login failures, lockouts, etc.
    This is separate from the immutable audit log (Milestone 4).
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    user_id: str = ""
    event_type: str = ""
    ip_address: str = ""
    user_agent: str = ""
    request_id: str = ""
    details: Optional[dict] = None
    created_at: datetime = field(default_factory=now)


@dataclass
class PasswordResetToken:
    """
    Password reset token entity.

    Per Security §3.6: Single-use reset tokens with short TTL (15 minutes).
    Per Security §6.5: Backup codes/tokens are hashed.
    """

    id: str = field(default_factory=new_id_str)
    user_id: str = ""
    tenant_id: str = ""
    token_hash: str = ""
    expires_at: datetime = field(default_factory=now)
    used_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=now)

    @property
    def is_valid(self) -> bool:
        """Check if token is still valid and unused."""
        return self.used_at is None and now() < self.expires_at