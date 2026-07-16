"""
API v1 URL routing.

App-specific routes will be included here as each module is implemented.
For Phase 0, this provides a placeholder that can be extended.
"""

from django.urls import include, path

urlpatterns = [
    # Platform (tenant info)
    path("company/", include("apps.platform.api.urls")),
    # Phase 1+ will add more app routes here
    # path("auth/", include("apps.iam.api.urls")),
    # path("users/", include("apps.iam.api.urls")),
    # path("roles/", include("apps.rbac.api.urls")),
    # path("audit/", include("apps.audit.api.urls")),
]
