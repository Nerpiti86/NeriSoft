from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.access import Permission, Role, role_permissions, user_roles
from app.models.user import User


@dataclass(frozen=True, slots=True)
class PermissionDefinition:
    code: str
    group: str
    name: str
    description: str


PERMISSION_DEFINITIONS = (
    PermissionDefinition(
        "system.users.view",
        "Usuarios",
        "Ver usuarios",
        "Consultar el listado, estados y roles asignados a las cuentas de acceso.",
    ),
    PermissionDefinition(
        "system.users.create",
        "Usuarios",
        "Crear usuarios",
        "Dar de alta nuevas cuentas de acceso no administrativas.",
    ),
    PermissionDefinition(
        "system.users.edit",
        "Usuarios",
        "Editar usuarios",
        "Modificar nombre, usuario y correo de cuentas permitidas.",
    ),
    PermissionDefinition(
        "system.users.status",
        "Usuarios",
        "Activar o desactivar usuarios",
        "Cambiar el estado de cuentas permitidas, excepto la propia sesión.",
    ),
    PermissionDefinition(
        "system.users.assign_roles",
        "Usuarios",
        "Asignar roles",
        "Asignar a otros usuarios roles cuyo alcance no supere el propio.",
    ),
    PermissionDefinition(
        "system.roles.view",
        "Roles",
        "Ver roles y permisos",
        "Consultar roles, permisos incluidos y cantidad de usuarios asignados.",
    ),
    PermissionDefinition(
        "system.roles.create",
        "Roles",
        "Crear roles",
        "Crear roles con permisos dentro del alcance propio.",
    ),
    PermissionDefinition(
        "system.roles.edit",
        "Roles",
        "Editar roles y permisos",
        "Modificar nombre, descripción y permisos dentro del alcance propio.",
    ),
    PermissionDefinition(
        "system.roles.status",
        "Roles",
        "Activar o desactivar roles",
        "Cambiar el estado de roles que estén dentro del alcance propio.",
    ),
)

PERMISSION_BY_CODE = {item.code: item for item in PERMISSION_DEFINITIONS}
ALL_PERMISSION_CODES = frozenset(PERMISSION_BY_CODE)


def permission_codes_for_user(db: Session, user: User) -> frozenset[str]:
    if user.is_superuser:
        return ALL_PERMISSION_CODES

    statement = (
        select(Permission.code)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .join(Role, Role.id == role_permissions.c.role_id)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(
            user_roles.c.user_id == user.id,
            Role.is_active.is_(True),
        )
        .distinct()
    )
    return frozenset(db.scalars(statement).all())


def has_permission(db: Session, user: User, code: str) -> bool:
    return code in permission_codes_for_user(db, user)


def role_permission_codes(db: Session, role_id: int) -> frozenset[str]:
    statement = (
        select(Permission.code)
        .join(role_permissions, role_permissions.c.permission_id == Permission.id)
        .where(role_permissions.c.role_id == role_id)
    )
    return frozenset(db.scalars(statement).all())


def role_is_within_user_scope(db: Session, role_id: int, user: User) -> bool:
    if user.is_superuser:
        return True
    return role_permission_codes(db, role_id).issubset(permission_codes_for_user(db, user))
