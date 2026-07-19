"""
Unit tests for AuthenticationService.

Per Auth Spec §3: Lockout, brute-force protection, same error for enumeration.
"""

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.utils import timezone

from apps.iam.application.services import AuthenticationService
from apps.iam.domain.entities import UserAccount
from apps.iam.infrastructure.repositories import SecurityEventRepository, UserRepository


class AuthenticationServiceUnitTests(TestCase):
    """Unit tests for AuthenticationService."""

    def setUp(self):
        self.user_repo = MagicMock(spec=UserRepository)
        self.security_repo = MagicMock(spec=SecurityEventRepository)
        self.service = AuthenticationService(
            user_repository=self.user_repo,
            security_event_repository=self.security_repo,
        )
        self.tenant_id = "11111111-1111-1111-1111-111111111111"
        self.email = "test@example.com"

    def test_authenticate_success(self):
        """Test successful authentication resets failed attempts."""
        user = UserAccount(
            tenant_id=self.tenant_id,
            email=self.email,
            status="active",
            failed_login_attempts=2,
        )
        user.set_password("correct_password")
        self.user_repo.get_by_email.return_value = user

        result = self.service.authenticate(
            tenant_id=self.tenant_id,
            email=self.email,
            password="correct_password",
        )

        self.assertIsNotNone(result)
        self.assertEqual(result.failed_login_attempts, 0)
        self.user_repo.reset_failed_attempts.assert_called_once_with(user)

    def test_authenticate_wrong_password(self):
        """Test wrong password increments failed attempts."""
        user = UserAccount(
            tenant_id=self.tenant_id,
            email=self.email,
            status="active",
            failed_login_attempts=0,
        )
        user.set_password("correct_password")
        self.user_repo.get_by_email.return_value = user

        result = self.service.authenticate(
            tenant_id=self.tenant_id,
            email=self.email,
            password="wrong_password",
        )

        self.assertIsNone(result)
        self.user_repo.increment_failed_attempts.assert_called_once_with(user)

    def test_authenticate_locked_account(self):
        """Test locked account returns None."""
        user = UserAccount(
            tenant_id=self.tenant_id,
            email=self.email,
            status="active",
            locked_until=timezone.now() + timedelta(minutes=30),
        )
        self.user_repo.get_by_email.return_value = user

        result = self.service.authenticate(
            tenant_id=self.tenant_id,
            email=self.email,
            password="password",
        )

        self.assertIsNone(result)
        self.security_repo.log_event.assert_called()

    def test_authenticate_inactive_account(self):
        """Test inactive account returns None."""
        user = UserAccount(
            tenant_id=self.tenant_id,
            email=self.email,
            status="inactive",
        )
        self.user_repo.get_by_email.return_value = user

        result = self.service.authenticate(
            tenant_id=self.tenant_id,
            email=self.email,
            password="password",
        )

        self.assertIsNone(result)