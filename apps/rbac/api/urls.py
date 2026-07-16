"""
API URL routing for the RBAC module.

Per Software Architecture §5.1: Central API URL routing.
"""

from django.urls import path

from apps.rbac.api.views import (
    PermissionListView,
    RoleDetailView,
    RoleListView,
    RolePermissionAssignView,
    UserRoleAssignView,
    UserRoleListView,
)

urlpatterns = [
    path("permissions", PermissionListView.as_view(), name="permission-list"),
    path("roles", RoleListView.as_view(), name="role-list"),
    path("roles/<uuid:role_id>", RoleDetailView.as_view(), name="role-detail"),
    path("roles/<uuid:role_id>/permissions", RolePermissionAssignView.as_view(), name="role-permission-assign"),
    path("users/me/roles", UserRoleListView.as_view(), name="user-role-list"),
    path("users/<uuid:user_id>/roles", UserRoleAssignView.as_view(), name="user-role-assign"),
]