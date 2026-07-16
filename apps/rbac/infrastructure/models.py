"""
Django models for the RBAC module.

Per amendment: Permissions are global system records. Roles are tenant-scoped.
Permission grouping derived from naming conventions (resource.action).
Supports wildcard permissions (e.g., inventory.*, inventory.products.*).
"""

from uuid import uuid4

from django.db import models


class Permission(models.Model):
    """
    Global permission definition (not tenant-scoped).
    Permissions are system-wide and shared across all tenants.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)  # e.g., "inventory.products.edit"
    resource = models.CharField(max_length=100, db_index=True)  # e.g., "inventory.products"
    action = models.CharField(max_length=100, db_index=True)  # e.g., "edit"
    description = models.TextField(blank=True)
    is_wildcard = models.BooleanField(default=False, db_index=True)
    is_system = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "rbac_permissions"
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        indexes = [
            models.Index(fields=["resource", "action"]),
        ]

    def __str__(self) -> str:
        return self.name


class Role(models.Model):
    """
    Tenant-scoped role.
    Roles belong to a specific tenant and define a set of permissions.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tenant_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    permission_version = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "rbac_roles"
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        unique_together = ("tenant_id", "name")
        indexes = [
            models.Index(fields=["tenant_id", "name"]),
            models.Index(fields=["tenant_id", "is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.tenant_id})"


class RolePermission(models.Model):
    """
    Many-to-many relationship between Role and Permission.
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="role_permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="role_permissions")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rbac_role_permissions"
        verbose_name = "Role Permission"
        verbose_name_plural = "Role Permissions"
        unique_together = ("role", "permission")
        indexes = [
            models.Index(fields=["role", "permission"]),
        ]

    def __str__(self) -> str:
        return f"{self.role} -> {self.permission}"


class UserRole(models.Model):
    """
    User-Role assignment with optional branch scope.

    Branch scoping:
    - branch_id = null: user has role for all branches (Owner/Admin)
    - branch_id = specific: user has role only for that branch
    """

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")
    tenant_id = models.UUIDField(db_index=True)
    branch_id = models.UUIDField(null=True, blank=True, db_index=True)
    assigned_by = models.UUIDField()  # User ID who assigned this role
    assigned_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "rbac_user_roles"
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        unique_together = ("user_id", "role", "branch_id")
        indexes = [
            models.Index(fields=["tenant_id", "user_id"]),
            models.Index(fields=["tenant_id", "branch_id"]),
        ]

    def __str__(self) -> str:
        return f"User {self.user_id} -> Role {self.role}"