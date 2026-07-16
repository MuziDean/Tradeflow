"""
Root URL configuration for TradeFlow.

API endpoints are versioned under /api/v1/.
Documentation is served at /docs/ and /redoc/.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from core.health.views import health

urlpatterns = [
    # Health check
    path("health/", health, name="health"),
    # API schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # Django admin
    path("admin/", admin.site.urls),
    # API v1 (app-specific routes will be registered in Phase 1+)
    path("api/v1/", include("config.api_urls")),
]