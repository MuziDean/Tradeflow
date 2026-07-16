"""
API URL routing for the platform module.

Per Backend Engineering Standards §6.7: Versioned from day one (/v1/).
"""

from django.urls import path

from apps.platform.api.views import TenantInfoView

urlpatterns = [
    path("tenant/", TenantInfoView.as_view(), name="tenant-info"),
]