"""
TradeFlow Audit app configuration.

Per Security Architecture: Audit logging for all security-relevant actions.
"""

from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = "Audit Logging"