"""
Application services for the audit module.

Per ADR-004: Application services orchestrate domain operations.
Per Security Architecture: All security-relevant actions must be audited.

Phase 0: Architectural scaffold only.
Phase 1: Implement business logic.
"""

from apps.audit.domain.entities import AuditLog


class AuditService:
    """
    Application service for audit logging.

    Records all security-relevant actions and data modifications.

    Phase 0: Scaffold only.
    """

    def __init__(self, audit_log_repository):
        self.audit_log_repository = audit_log_repository

    def log_action(
        self,
        tenant_id: str,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str,
        old_values: dict | None = None,
        new_values: dict | None = None,
        ip_address: str = "",
        user_agent: str = "",
        request_id: str = "",
    ) -> AuditLog:
        """Log an audit event. Phase 1: implement business logic."""
        pass