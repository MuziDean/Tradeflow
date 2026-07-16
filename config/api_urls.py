"""
API URL routing for TradeFlow.

Per Software Architecture §5.1: Central API URL routing.
"""

from django.urls import include, path

urlpatterns = [
    path("api/v1/health/", include("core.health.urls")),
    path("api/v1/auth/", include("apps.iam.api.urls")),
    path("api/v1/rbac/", include("apps.rbac.api.urls")),
    path("api/v1/company/", include("apps.platform.api.urls")),
]
