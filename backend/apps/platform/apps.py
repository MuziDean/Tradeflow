"""
TradeFlow Platform app configuration.

Per ADR-004: Platform module handles tenant lifecycle and company profiles.
"""

from django.apps import AppConfig


class PlatformConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.platform"
    verbose_name = "Platform"