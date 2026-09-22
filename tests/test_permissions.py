from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.core.permissions import (
    ALL_PERMISSION_CODES,
    has_permission,
    permission_codes_for_user,
    role_is_within_user_scope,
)
from app.models import Permission, Role, User


def _permission(code: str, name: str) -> Permission:
    return Permission(
        code=code,
        module="Sistema",
        name=name,
        description="",
    )


def _user(username: str, *, is_superuser: bool = False) -> User:
    return User(
        name=username.title(),
        username=username,
        email=f"{username}@example.com",
        password_hash="hash",
        is_active=True,
        is_superuser=is_superuser,
    )


def test_active_roles_grant_permissions_and_inactive_roles_do_not() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        view_users = _permission("system.users.view", "Ver usuarios")
        role = Role(
            name="Consulta",
            name_key="consulta",
            is_active=True,
            permissions=[view_users],
        )
        user = _user("operador")
        user.roles = [role]
        db.add(user)
        db.commit()

        assert permission_codes_for_user(db, user) == frozenset({"system.users.view"})
        assert has_permission(db, user, "system.users.view")

        role.is_active = False
        db.commit()
        assert permission_codes_for_user(db, user) == frozenset()
        assert not has_permission(db, user, "system.users.view")


def test_superuser_bypasses_role_assignments() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = _user("administrador", is_superuser=True)
        db.add(user)
        db.commit()

        assert permission_codes_for_user(db, user) == ALL_PERMISSION_CODES


def test_role_scope_cannot_exceed_delegated_user_permissions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        view_users = _permission("system.users.view", "Ver usuarios")
        edit_users = _permission("system.users.edit", "Editar usuarios")

        delegated_role = Role(
            name="Supervisor",
            name_key="supervisor",
            is_active=True,
            permissions=[view_users],
        )
        allowed_role = Role(
            name="Consulta",
            name_key="consulta",
            is_active=True,
            permissions=[view_users],
        )
        excessive_role = Role(
            name="Edición",
            name_key="edicion",
            is_active=True,
            permissions=[view_users, edit_users],
        )
        user = _user("supervisor")
        user.roles = [delegated_role]

        db.add_all([user, allowed_role, excessive_role])
        db.commit()

        assert role_is_within_user_scope(db, allowed_role.id, user)
        assert not role_is_within_user_scope(db, excessive_role.id, user)
