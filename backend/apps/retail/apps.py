"""
TradeFlow Retail app configuration.

Per ADR-004: Retail module handles POS, sales, and invoices.
"""

from django.apps import AppConfig


class RetailConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.retail"
    verbose_name = "Retail & POS"