"""
API views for the RBAC module.

Provides endpoints for:
- Listing permissions (global)
- Managing tenant roles
- Assigning/revoking user roles
"""

from uuid import UUID

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.rbac.api.serializers import (
    PermissionSerializer,
    RoleCreateSerializer,
    RoleSerializer,
    UserRoleAssignSerializer,
    UserRoleSerializer,
)
from apps.rbac.application.services import (
    AuthorizationService,
    PermissionService,
    RoleService,
    UserRoleService,
)
from apps.rbac.infrastructure.repositories import (
    PermissionRepository,
    RoleRepository,
    UserRoleRepository,
)


class PermissionListView(APIView):
    """List all global permissions."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        service = PermissionService(permission_repository=PermissionRepository())
        permissions = service.list_all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response({"data": serializer.data})


class RoleListView(APIView):
    """List tenant roles."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return Response({"error": "Tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        repo = RoleRepository()
        roles = repo.list_for_tenant(tenant_id)
        serializer = RoleSerializer(roles, many=True)
        return Response({"data": serializer.data})

    def post(self, request):
        """Create a new role."""
        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return Response({"error": "Tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = RoleService(role_repository=RoleRepository())
        role = service.create_role(
            tenant_id=tenant_id,
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        # Assign permissions if provided
        permission_ids = serializer.validated_data.get("permission_ids", [])
        if permission_ids:
            service.assign_permissions(role.id, permission_ids)

        return Response({"data": RoleSerializer(role).data}, status=status.HTTP_201_CREATED)


class RoleDetailView(APIView):
    """Get, update, delete a specific role."""

    permission_classes = [IsAuthenticated]

    def get(self, request, role_id):
        tenant_id = getattr(request.actor, "tenant_id", None)
        repo = RoleRepository()
        role = repo.get_by_id(role_id, tenant_id)
        if not role:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"data": RoleSerializer(role).data})

    def patch(self, request, role_id):
        tenant_id = getattr(request.actor, "tenant_id", None)
        repo = RoleRepository()
        role = repo.get_by_id(role_id, tenant_id)
        if not role:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        if role.is_system:
            return Response({"error": "Cannot modify system role."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RoleCreateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if "name" in serializer.validated_data:
            role.name = serializer.validated_data["name"]
        if "description" in serializer.validated_data:
            role.description = serializer.validated_data["description"]
        role.updated_at = timezone.now()

        updated_role = repo.update(role)

        # Update permissions if provided
        if "permission_ids" in serializer.validated_data:
            service = RoleService(role_repository=repo)
            # Clear existing and assign new
            existing = repo.get_role_permissions(role_id)
            for perm in existing:
                repo.remove_permission(role_id, perm.id)
            service.assign_permissions(role_id, serializer.validated_data["permission_ids"])

        return Response({"data": RoleSerializer(updated_role).data})

    def delete(self, request, role_id):
        tenant_id = getattr(request.actor, "tenant_id", None)
        repo = RoleRepository()
        role = repo.get_by_id(role_id, tenant_id)
        if not role:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        if role.is_system:
            return Response({"error": "Cannot delete system role."}, status=status.HTTP_400_BAD_REQUEST)

        deleted = repo.delete(role_id, tenant_id)
        if not deleted:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)


class RolePermissionAssignView(APIView):
    """Assign or remove permissions from a role."""

    permission_classes = [IsAuthenticated]

    def post(self, request, role_id):
        tenant_id = getattr(request.actor, "tenant_id", None)
        repo = RoleRepository()
        role = repo.get_by_id(role_id, tenant_id)
        if not role:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        if role.is_system:
            return Response({"error": "Cannot modify system role."}, status=status.HTTP_400_BAD_REQUEST)

        permission_id = request.data.get("permission_id")
        if not permission_id:
            return Response({"error": "permission_id required."}, status=status.HTTP_400_BAD_REQUEST)

        repo.add_permission(role_id, permission_id)
        return Response({"data": {"assigned": True}})

    def delete(self, request, role_id):
        tenant_id = getattr(request.actor, "tenant_id", None)
        repo = RoleRepository()
        role = repo.get_by_id(role_id, tenant_id)
        if not role:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)

        if role.is_system:
            return Response({"error": "Cannot modify system role."}, status=status.HTTP_400_BAD_REQUEST)

        permission_id = request.data.get("permission_id")
        if not permission_id:
            return Response({"error": "permission_id required."}, status=status.HTTP_400_BAD_REQUEST)

        repo.remove_permission(role_id, permission_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserRoleListView(APIView):
    """List roles for current user."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tenant_id = getattr(request.actor, "tenant_id", None)
        user_id = str(request.user.id)
        service = UserRoleService(user_role_repository=UserRoleRepository())
        roles = service.list_user_roles(tenant_id, user_id)
        serializer = UserRoleSerializer(roles, many=True)
        return Response({"data": serializer.data})


class UserRoleAssignView(APIView):
    """Assign or revoke roles for a user."""

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        tenant_id = getattr(request.actor, "tenant_id", None)
        if not tenant_id:
            return Response({"error": "Tenant context required."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserRoleAssignSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        role_id = str(serializer.validated_data["role_id"])
        branch_id = serializer.validated_data.get("branch_id")
        assigned_by = str(request.user.id)

        service = UserRoleService(user_role_repository=UserRoleRepository())
        user_role = service.assign_role(
            user_id=user_id,
            role_id=role_id,
            tenant_id=tenant_id,
            branch_id=branch_id,
            assigned_by=assigned_by,
        )

        return Response({"data": UserRoleSerializer(user_role).data}, status=status.HTTP_201_CREATED)

    def delete(self, request, user_id, role_id):
        tenant_id = getattr(request.actor, "tenant_id", None)
        branch_id = request.data.get("branch_id")

        service = UserRoleService(user_role_repository=UserRoleRepository())
        revoked = service.revoke_role(user_id, role_id, branch_id)
        if not revoked:
            return Response({"error": "Assignment not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)