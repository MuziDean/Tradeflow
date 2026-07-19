"""
TradeFlow RBAC app configuration.

Per ADR-004: RBAC module handles roles, permissions, and access control.
"""

from django.apps import AppConfig


class RBACConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.rbac"
    verbose_name = "Role-Based Access Control"