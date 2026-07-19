"""
Django models for the audit module.

Per Security Architecture: Audit logs must never be modified or deleted.
"""

from django.db import models

from infrastructure.db.base_model import TenantModel
from shared.ids.uuid import new_id_str


class AuditLog(models.Model):
    """
    Audit log model - append only, no updates or deletes allowed.
    """

    id = models.CharField(primary_key=True, max_length=36, default=new_id_str)
    tenant_id = models.CharField(max_length=36, db_index=True)
    user_id = models.CharField(max_length=36, db_index=True)
    action = models.CharField(max_length=100, db_index=True)
    resource_type = models.CharField(max_length=100, db_index=True)
    resource_id = models.CharField(max_length=36)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(blank=True)
    request_id = models.CharField(max_length=36)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "audit_logs"
        indexes = [
            models.Index(fields=["tenant_id", "created_at"]),
            models.Index(fields=["tenant_id", "user_id", "action"]),
            models.Index(fields=["resource_type", "resource_id"]),
        ]
        # Prevent modifications after creation
        default_permissions = ("add", "view")