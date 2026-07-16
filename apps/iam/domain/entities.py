"""
Domain entities for the IAM module.

Per ADR-004: Entities represent the core business concepts and invariants.
Per Security Architecture: MAX_FAILED_ATTEMPTS = 5, LOCKOUT_MINUTES = 30.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from shared.ids.uuid import new_id_str
from shared.time.helpers import now


@dataclass
class User:
    """
    User entity representing an authenticated individual.

    Security rules:
    - Failed login attempts locked after MAX_FAILED_ATTEMPTS
    - Lockout duration is LOCKOUT_MINUTES
    - Must have exactly one active session per device type
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    email: str = ""
    phone_number: str = ""
    first_name: str = ""
    last_name: str = ""
    status: str = "active"  # active, inactive, suspended, locked
    is_staff: bool = False
    is_superuser: bool = False
    failed_login_attempts: int = 0
    locked_until: Optional[datetime] = None
    last_login: Optional[datetime] = None
    mfa_enabled: bool = False
    mfa_secret: str = ""
    created_at: datetime = field(default_factory=now)
    updated_at: datetime = field(default_factory=now)

    @property
    def is_locked(self) -> bool:
        """Check if user is currently locked out."""
        if self.locked_until is None:
            return False
        return now() < self.locked_until


@dataclass
class Session:
    """
    User session entity.

    Tracks active sessions for security and audit purposes.
    One active session per device type per user.
    """

    id: str = field(default_factory=new_id_str)
    user_id: str = ""
    tenant_id: str = ""
    device_type: str = ""  # web, mobile, pos
    refresh_token_jti: str = ""  # JWT ID for revocation
    ip_address: str = ""
    user_agent: str = ""
    last_activity: datetime = field(default_factory=now)
    expires_at: datetime = field(default_factory=now)
    is_active: bool = True


@dataclass
class PasswordResetToken:
    """
    Password reset token entity.

    Single-use tokens with short expiry.
    """

    id: str = field(default_factory=new_id_str)
    user_id: str = ""
    token: str = ""
    expires_at: datetime = field(default_factory=now)
    used_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=now)

    @property
    def is_valid(self) -> bool:
        """Check if token is still valid and unused."""
        return self.used_at is None and now() < self.expires_at