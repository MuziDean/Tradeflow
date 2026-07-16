"""
API URL routing for the IAM module.

Per Auth Spec §3: All endpoints under /api/v1/auth/.
"""

from django.urls import path

from apps.iam.api.views import (
    CurrentUserView,
    LoginView,
    LogoutView,
    RegisterView,
    TokenRefreshView,
)

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("me", CurrentUserView.as_view(), name="current-user"),
]
