from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.core.permissions import (
    ALL_PERMISSION_CODES,
    PERMISSION_DEFINITIONS,
    permission_selection_is_within_user_scope,
    role_is_assigned_to_user,
)
from app.core.role_validation import normalized_role_values, validate_role_values
from app.models import Permission, Role, User
from app.roles import _permission_sections


def _user(username: str, *, is_superuser: bool = False) -> User:
    return User(
        name=username.title(),
        username=username,
        email=f"{username}@example.com",
        password_hash="hash",
        is_active=True,
        is_superuser=is_superuser,
    )


def test_role_values_are_normalized_for_unique_identity() -> None:
    values = normalized_role_values("  Supervisor   de Ventas  ", "  Gestiona   el equipo.  ")

    assert values == {
        "name": "Supervisor de Ventas",
        "name_key": "supervisor de ventas",
        "description": "Gestiona el equipo.",
    }
    assert validate_role_values(values) == {}


def test_role_validation_rejects_invalid_lengths() -> None:
    values = {
        "name": "A",
        "name_key": "a",
        "description": "x" * 256,
    }

    errors = validate_role_values(values)
    assert "name" in errors
    assert "description" in errors


def test_current_permission_catalog_is_explicitly_system_scoped() -> None:
    assert {definition.area for definition in PERMISSION_DEFINITIONS} == {"Sistema"}
    assert all(definition.code.startswith("system.") for definition in PERMISSION_DEFINITIONS)

    sections = _permission_sections(ALL_PERMISSION_CODES)
    assert len(sections) == 1

    area_name, groups = sections[0]
    assert area_name == "Sistema"
    assert tuple(group_name for group_name, _ in groups) == (
        "Usuarios",
        "Roles y permisos",
    )
    assert sum(len(items) for _, items in groups) == len(PERMISSION_DEFINITIONS)


def test_permission_selection_and_self_assignment_are_detected() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        view_roles = Permission(
            code="system.roles.view",
            module="Roles",
            name="Ver roles",
            description="",
        )
        edit_roles = Permission(
            code="system.roles.edit",
            module="Roles",
            name="Editar roles",
            description="",
        )
        delegated_role = Role(
            name="Supervisor",
            name_key="supervisor",
            is_active=True,
            permissions=[view_roles],
        )
        user = _user("supervisor")
        user.roles = [delegated_role]
        db.add(user)
        db.add(edit_roles)
        db.commit()

        assert permission_selection_is_within_user_scope(
            db,
            user,
            {"system.roles.view"},
        )
        assert not permission_selection_is_within_user_scope(
            db,
            user,
            {"system.roles.view", "system.roles.edit"},
        )
        assert role_is_assigned_to_user(db, delegated_role.id, user.id)
