"""
Unit tests for AuthorizationService.

Tests permission evaluation, wildcard matching, and caching.
"""

from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.rbac.application.services import AuthorizationService
from apps.rbac.domain.entities import Permission, Role, UserRole
from apps.rbac.infrastructure.repositories import UserRoleRepository


class AuthorizationServiceUnitTests(TestCase):
    """Unit tests for AuthorizationService."""

    def setUp(self):
        self.user_role_repo = MagicMock(spec=UserRoleRepository)
        self.service = AuthorizationService(user_role_repository=self.user_role_repo)
        self.tenant_id = "11111111-1111-1111-1111-111111111111"
        self.user_id = "22222222-2222-2222-2222-222222222222"

    def test_has_permission_exact_match(self):
        """Test exact permission match."""
        self.user_role_repo.get_user_roles.return_value = []
        self.user_role_repo.get_user_permissions.return_value = []

        result = self.service.has_permission(self.tenant_id, self.user_id, "inventory.products.edit")
        self.assertFalse(result)

    def test_has_permission_wildcard_match(self):
        """Test wildcard permission matching."""
        permissions = [
            "inventory.*",
            "sales.transactions.view",
        ]
        self.user_role_repo.get_user_roles.return_value = []
        with patch.object(self.service, 'get_user_permissions', return_value=permissions):
            result = self.service.has_permission(self.tenant_id, self.user_id, "inventory.products.edit")
            self.assertTrue(result)

    def test_has_permission_no_match(self):
        """Test permission denial when no match."""
        permissions = ["sales.transactions.view"]
        self.user_role_repo.get_user_roles.return_value = []
        with patch.object(self.service, 'get_user_permissions', return_value=permissions):
            result = self.service.has_permission(self.tenant_id, self.user_id, "inventory.products.edit")
            self.assertFalse(result)

    def test_wildcard_match_partial(self):
        """Test wildcard matching for partial prefixes."""
        self.assertTrue(self.service._wildcard_match("inventory.*", "inventory.products.edit"))
        self.assertTrue(self.service._wildcard_match("inventory.products.*", "inventory.products.edit"))
        self.assertFalse(self.service._wildcard_match("inventory.*", "sales.transactions.view"))
        self.assertFalse(self.service._wildcard_match("inventory.products.*", "inventory.edit"))