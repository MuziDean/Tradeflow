"""
Application services for the IAM module.

Per ADR-004: Application services orchestrate domain operations.
Security rules:
- MAX_FAILED_ATTEMPTS = 5
- LOCKOUT_MINUTES = 30

Phase 0: Architectural scaffold only.
Phase 1: Implement business logic.
"""

from typing import Optional

from apps.iam.domain.entities import Session, User


class AuthenticationService:
    """
    Application service for authentication operations.

    Phase 0: Scaffold only.
    """

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_MINUTES = 30

    def __init__(self, user_repository, session_repository):
        self.user_repository = user_repository
        self.session_repository = session_repository

    def register_user(self, email: str, password: str, tenant_id: str) -> User:
        """Register a new user. Phase 1: implement business logic."""
        pass

    def authenticate(self, email: str, password: str, device_type: str = "web") -> Optional[User]:
        """Authenticate user. Phase 1: implement business logic."""
        pass