"""add roles and permissions

Revision ID: 0003_roles_permissions
Revises: 0002_user_superuser
Create Date: 2026-09-22
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_roles_permissions"
down_revision: Union[str, None] = "0002_user_superuser"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERMISSIONS = (
    ("system.users.view", "Usuarios", "Ver usuarios", "Consultar el listado, estados y roles asignados a las cuentas de acceso."),
    ("system.users.create", "Usuarios", "Crear usuarios", "Dar de alta nuevas cuentas de acceso no administrativas."),
    ("system.users.edit", "Usuarios", "Editar usuarios", "Modificar nombre, usuario y correo de cuentas permitidas."),
    ("system.users.status", "Usuarios", "Activar o desactivar usuarios", "Cambiar el estado de cuentas permitidas, excepto la propia sesión."),
    ("system.users.assign_roles", "Usuarios", "Asignar roles", "Asignar a otros usuarios roles cuyo alcance no supere el propio."),
    ("system.roles.view", "Roles", "Ver roles y permisos", "Consultar roles, permisos incluidos y cantidad de usuarios asignados."),
    ("system.roles.create", "Roles", "Crear roles", "Crear roles con permisos dentro del alcance propio."),
    ("system.roles.edit", "Roles", "Editar roles y permisos", "Modificar nombre, descripción y permisos dentro del alcance propio."),
    ("system.roles.status", "Roles", "Activar o desactivar roles", "Cambiar el estado de roles que estén dentro del alcance propio."),
)


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=80), nullable=False),
        sa.Column("name_key", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=255), server_default="", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name_key"),
    )

    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=100), nullable=False),
        sa.Column("module", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), server_default="", nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )

    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    permissions_table = sa.table(
        "permissions",
        sa.column("code", sa.String),
        sa.column("module", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.String),
    )
    op.bulk_insert(
        permissions_table,
        [
            {"code": code, "module": module, "name": name, "description": description}
            for code, module, name, description in PERMISSIONS
        ],
    )


def downgrade() -> None:
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
