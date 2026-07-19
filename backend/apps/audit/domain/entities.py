"""
Domain entities for the audit module.

Per Security Architecture: Audit logs must never be modified or deleted.
"""

from dataclasses import dataclass, field
from typing import Optional

from shared.ids.uuid import new_id_str


@dataclass
class AuditLog:
    """
    Audit log entity.

    Records all security-relevant actions and data modifications.
    Immutable once created.
    """

    id: str = field(default_factory=new_id_str)
    tenant_id: str = ""
    user_id: str = ""
    action: str = ""  # e.g., "user.login", "sale.create", "role.assign"
    resource_type: str = ""  # e.g., "user", "sale", "role"
    resource_id: str = ""
    old_values: Optional[dict] = None
    new_values: Optional[dict] = None
    ip_address: str = ""
    user_agent: str = ""
    request_id: str = ""
    timestamp: str = ""  # ISO format

    def to_dict(self) -> dict:
        """Serialize for storage."""
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "old_values": self.old_values,
            "new_values": self.new_values,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
        }