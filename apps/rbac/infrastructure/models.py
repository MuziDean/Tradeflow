"""
Django models for the RBAC module.

Per Security Architecture: Roles, permissions, and branch access policies.
"""

from django.db import models

from infrastructure.db.base_model import TenantModel
from shared.ids.uuid import new_id_str


class Role(TenantModel):
    """
    Django model for roles.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)

    class Meta:
        db_table = "rbac_roles"
        unique_together = ("tenant_id", "name")


class Permission(models.Model):
    """
    Django model for permissions.
    """

    id = models.CharField(primary_key=True, max_length=36, default=new_id_str)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    codename = models.CharField(max_length=100, db_index=True)
    name = models.CharField(max_length=255)
    module = models.CharField(max_length=50, db_index=True)
    action = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        db_table = "rbac_permissions"
        unique_together = ("role", "codename")


class BranchAccessPolicy(models.Model):
    """
    Branch access policy for a role.
    """

    id = models.CharField(primary_key=True, max_length=36, default=new_id_str)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="branch_policies")
    tenant_id = models.CharField(max_length=36, db_index=True)
    branch_ids = models.JSONField(default=list)
    access_type = models.CharField(max_length=20, default="allowed")

    class Meta:
        db_table = "rbac_branch_access_policies"