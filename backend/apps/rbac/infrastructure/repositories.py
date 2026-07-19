"""
Repository layer for RBAC.

Tenant-scoped queries for roles and user roles.
Permissions are global (not tenant-scoped).
"""

from uuid import UUID

from django.core.cache import cache
from django.db import transaction

from apps.rbac.domain.entities import Permission, Role, RolePermission, UserRole
from apps.rbac.infrastructure.models import (
    Permission as PermissionModel,
)
from apps.rbac.infrastructure.models import (
    Role as RoleModel,
)
from apps.rbac.infrastructure.models import (
    RolePermission as RolePermissionModel,
)
from apps.rbac.infrastructure.models import (
    UserRole as UserRoleModel,
)


class PermissionRepository:
    """Repository for global Permission records."""

    def get_by_name(self, name: str) -> Permission | None:
        try:
            model = PermissionModel.objects.get(name=name)
            return self._to_entity(model)
        except PermissionModel.DoesNotExist:
            return None

    def get_by_resource_action(self, resource: str, action: str) -> Permission | None:
        try:
            model = PermissionModel.objects.get(resource=resource, action=action)
            return self._to_entity(model)
        except PermissionModel.DoesNotExist:
            return None

    def list_global(self) -> list[Permission]:
        return [self._to_entity(m) for m in PermissionModel.objects.all()]

    def bulk_create(self, permissions: list[Permission]) -> None:
        models = [
            PermissionModel(
                id=p.id,
                name=p.name,
                resource=p.resource,
                action=p.action,
                description=p.description,
                is_wildcard=p.is_wildcard,
                is_system=p.is_system,
            )
            for p in permissions
        ]
        PermissionModel.objects.bulk_create(models, ignore_conflicts=True)

    def _to_entity(self, model: PermissionModel) -> Permission:
        return Permission(
            id=str(model.id),
            name=model.name,
            resource=model.resource,
            action=model.action,
            description=model.description or "",
            is_wildcard=model.is_wildcard,
            is_system=model.is_system,
            created_at=model.created_at,
        )


class RoleRepository:
    """Repository for tenant-scoped Role records."""

    def get_by_id(self, role_id: str, tenant_id: str) -> Role | None:
        try:
            model = RoleModel.objects.get(id=role_id, tenant_id=tenant_id)
            return self._to_entity(model)
        except RoleModel.DoesNotExist:
            return None

    def get_by_name(self, tenant_id: str, name: str) -> Role | None:
        try:
            model = RoleModel.objects.get(tenant_id=tenant_id, name=name)
            return self._to_entity(model)
        except RoleModel.DoesNotExist:
            return None

    def list_for_tenant(self, tenant_id: str) -> list[Role]:
        return [self._to_entity(m) for m in RoleModel.objects.filter(tenant_id=tenant_id)]

    def create(self, role: Role) -> Role:
        model = RoleModel(
            id=role.id,
            tenant_id=role.tenant_id,
            name=role.name,
            description=role.description,
            is_system=role.is_system,
            is_active=role.is_active,
            permission_version=role.permission_version,
        )
        model.save()
        return self._to_entity(model)

    def update(self, role: Role) -> Role:
        model = RoleModel.objects.get(id=role.id, tenant_id=role.tenant_id)
        model.name = role.name
        model.description = role.description
        model.is_active = role.is_active
        model.permission_version = role.permission_version
        model.save()
        return self._to_entity(model)

    def delete(self, role_id: str, tenant_id: str) -> bool:
        deleted, _ = RoleModel.objects.filter(id=role_id, tenant_id=tenant_id).delete()
        return deleted > 0

    def add_permission(self, role_id: str, permission_id: str) -> None:
        RolePermissionModel.objects.get_or_create(
            role_id=role_id, permission_id=permission_id
        )

    def remove_permission(self, role_id: str, permission_id: str) -> None:
        RolePermissionModel.objects.filter(
            role_id=role_id, permission_id=permission_id
        ).delete()

    def get_role_permissions(self, role_id: str) -> list[Permission]:
        rps = RolePermissionModel.objects.filter(role_id=role_id).select_related("permission")
        return [self._permission_to_entity(rp.permission) for rp in rps]

    def _to_entity(self, model: RoleModel) -> Role:
        return Role(
            id=str(model.id),
            tenant_id=str(model.tenant_id),
            name=model.name,
            description=model.description or "",
            is_system=model.is_system,
            is_active=model.is_active,
            permission_version=model.permission_version,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _permission_to_entity(self, model: PermissionModel) -> Permission:
        return Permission(
            id=str(model.id),
            name=model.name,
            resource=model.resource,
            action=model.action,
            description=model.description or "",
            is_wildcard=model.is_wildcard,
            is_system=model.is_system,
            created_at=model.created_at,
        )


class UserRoleRepository:
    """Repository for UserRole assignments."""

    def get_user_roles(self, tenant_id: str, user_id: str) -> list[UserRole]:
        qs = UserRoleModel.objects.filter(tenant_id=tenant_id, user_id=user_id).select_related("role")
        return [self._to_entity(ur) for ur in qs]

    def assign_role(
        self, user_id: str, role_id: str, tenant_id: str, branch_id: str | None, assigned_by: str
    ) -> UserRole:
        model, _ = UserRoleModel.objects.get_or_create(
            user_id=user_id,
            role_id=role_id,
            tenant_id=tenant_id,
            branch_id=branch_id,
            defaults={"assigned_by": UUID(assigned_by)},
        )
        return self._to_entity(model)

    def revoke_role(self, user_id: str, role_id: str, branch_id: str | None) -> bool:
        qs = UserRoleModel.objects.filter(user_id=user_id, role_id=role_id, branch_id=branch_id)
        deleted, _ = qs.delete()
        return deleted > 0

    def get_user_permissions(self, tenant_id: str, user_id: str) -> list[Permission]:
        user_roles = self.get_user_roles(tenant_id, user_id)
        role_ids = [ur.role_id for ur in user_roles]
        rps = RolePermissionModel.objects.filter(role_id__in=role_ids).select_related("permission")
        perms = {}
        for rp in rps:
            p = rp.permission
            if str(p.id) not in perms:
                perms[str(p.id)] = Permission(
                    id=str(p.id),
                    name=p.name,
                    resource=p.resource,
                    action=p.action,
                    description=p.description or "",
                    is_wildcard=p.is_wildcard,
                    is_system=p.is_system,
                    created_at=p.created_at,
                )
        return list(perms.values())

    def _to_entity(self, model: UserRoleModel) -> UserRole:
        return UserRole(
            id=str(model.id),
            user_id=str(model.user_id),
            role_id=str(model.role_id),
            tenant_id=str(model.tenant_id),
            branch_id=str(model.branch_id) if model.branch_id else None,
            assigned_by=str(model.assigned_by),
            assigned_at=model.assigned_at,
        )