from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.auth import csrf_is_valid, csrf_token, permission_or_redirect, user_display
from app.core.config import settings
from app.core.database import get_db
from app.core.permissions import (
    ALL_PERMISSION_CODES,
    PERMISSION_DEFINITIONS,
    permission_codes_for_user,
    permission_selection_is_within_user_scope,
    role_is_assigned_to_user,
    role_is_within_user_scope,
)
from app.core.role_validation import normalized_role_values, validate_role_values
from app.core.templates import templates
from app.models import Permission, Role, User
from app.models.access import user_roles


router = APIRouter(prefix="/configuracion/roles", include_in_schema=False)


def _permission_groups(allowed_codes: frozenset[str]):
    grouped: dict[str, list] = defaultdict(list)
    for definition in PERMISSION_DEFINITIONS:
        if definition.code in allowed_codes:
            grouped[definition.group].append(definition)
    return tuple((group, tuple(items)) for group, items in grouped.items())


def _role_by_id(db: Session, role_id: int) -> Role | None:
    return db.scalar(
        select(Role)
        .options(selectinload(Role.permissions), selectinload(Role.users))
        .where(Role.id == role_id)
    )


def _permission_records(
    db: Session,
    selected_codes: frozenset[str],
) -> list[Permission] | None:
    if not selected_codes:
        return []

    permissions = list(
        db.scalars(
            select(Permission)
            .where(Permission.code.in_(selected_codes))
            .order_by(Permission.module, Permission.name)
        ).all()
    )
    if len(permissions) != len(selected_codes):
        return None
    return permissions


def _utc_now_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _role_response(
    request: Request,
    db: Session,
    current_user: User,
    *,
    form_mode: str | None = None,
    editing_role: Role | None = None,
    errors: dict[str, str] | None = None,
    values: dict[str, str] | None = None,
    selected_permission_codes: frozenset[str] | None = None,
    status_code: int = status.HTTP_200_OK,
    notice: str | None = None,
):
    roles = list(
        db.scalars(
            select(Role)
            .options(selectinload(Role.permissions), selectinload(Role.users))
            .order_by(func.lower(Role.name))
        ).all()
    )

    granted_codes = permission_codes_for_user(db, current_user)
    can_create_role = "system.roles.create" in granted_codes
    can_edit_role = "system.roles.edit" in granted_codes
    can_change_role_status = "system.roles.status" in granted_codes

    manageable_roles: dict[int, bool] = {}
    role_permission_modules: dict[int, tuple[str, ...]] = {}
    for role in roles:
        role_codes = frozenset(permission.code for permission in role.permissions)
        within_scope = current_user.is_superuser or role_codes.issubset(granted_codes)
        self_assigned = any(user.id == current_user.id for user in role.users)
        manageable_roles[role.id] = within_scope and (
            current_user.is_superuser or not self_assigned
        )
        role_permission_modules[role.id] = tuple(
            sorted({permission.module for permission in role.permissions})
        )

    total_roles = len(roles)
    active_roles = sum(1 for role in roles if role.is_active)
    users_with_roles = db.scalar(
        select(func.count(func.distinct(user_roles.c.user_id)))
    ) or 0

    notice_key = notice or request.query_params.get("notice")
    notices = {
        "created": ("success", "Rol creado correctamente."),
        "updated": ("success", "Rol actualizado correctamente."),
        "activated": ("success", "Rol activado correctamente."),
        "deactivated": ("success", "Rol desactivado correctamente."),
        "not-found": ("warning", "El rol solicitado ya no existe."),
        "scope-blocked": (
            "warning",
            "Ese rol contiene permisos fuera de tu alcance y no puede ser modificado desde esta sesión.",
        ),
        "self-role-blocked": (
            "warning",
            "No podés modificar ni desactivar un rol asignado a tu propia cuenta.",
        ),
    }
    notice_payload = notices.get(notice_key or "")

    first_name, initials = user_display(current_user)
    return templates.TemplateResponse(
        request=request,
        name="roles.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": current_user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": csrf_token(request),
            "roles": roles,
            "total_roles": total_roles,
            "active_roles": active_roles,
            "users_with_roles": users_with_roles,
            "manageable_roles": manageable_roles,
            "role_permission_modules": role_permission_modules,
            "can_create_role": can_create_role,
            "can_edit_role": can_edit_role,
            "can_change_role_status": can_change_role_status,
            "permission_groups": _permission_groups(granted_codes),
            "form_mode": form_mode,
            "editing_role": editing_role,
            "errors": errors or {},
            "values": values or {},
            "selected_permission_codes": selected_permission_codes or frozenset(),
            "notice_kind": notice_payload[0] if notice_payload else None,
            "notice_message": notice_payload[1] if notice_payload else None,
        },
        status_code=status_code,
    )


def _existing_role_name(
    db: Session,
    name_key: str,
    *,
    exclude_role_id: int | None = None,
) -> bool:
    statement = select(Role.id).where(Role.name_key == name_key)
    if exclude_role_id is not None:
        statement = statement.where(Role.id != exclude_role_id)
    return db.scalar(statement.limit(1)) is not None


def _selection_errors(
    db: Session,
    current_user: User,
    selected_codes: frozenset[str],
) -> dict[str, str]:
    errors: dict[str, str] = {}
    unknown_codes = selected_codes.difference(ALL_PERMISSION_CODES)
    if unknown_codes:
        errors["permissions"] = (
            "La selección contiene permisos que no pertenecen al catálogo vigente."
        )
        return errors

    if not permission_selection_is_within_user_scope(db, current_user, selected_codes):
        errors["permissions"] = (
            "No podés otorgar permisos que no estén incluidos en tu propio alcance."
        )
    return errors


def _role_change_blocked(db: Session, role: Role, current_user: User) -> str | None:
    if not role_is_within_user_scope(db, role.id, current_user):
        return "scope-blocked"
    if (
        not current_user.is_superuser
        and role_is_assigned_to_user(db, role.id, current_user.id)
    ):
        return "self-role-blocked"
    return None


@router.get("", response_class=HTMLResponse)
def roles_list(request: Request, db: Session = Depends(get_db)):
    current_user = permission_or_redirect(request, db, "system.roles.view")
    if isinstance(current_user, RedirectResponse):
        return current_user
    return _role_response(request, db, current_user)


@router.get("/nuevo", response_class=HTMLResponse)
def new_role(request: Request, db: Session = Depends(get_db)):
    current_user = permission_or_redirect(
        request,
        db,
        "system.roles.view",
        "system.roles.create",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user

    return _role_response(
        request,
        db,
        current_user,
        form_mode="create",
        values={"name": "", "description": ""},
    )


@router.post("/nuevo", response_class=HTMLResponse)
def create_role(
    request: Request,
    name: str = Form(""),
    description: str = Form(""),
    permissions: list[str] = Form(default=[]),
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = permission_or_redirect(
        request,
        db,
        "system.roles.view",
        "system.roles.create",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user

    values = normalized_role_values(name, description)
    selected_codes = frozenset(code.strip() for code in permissions if code.strip())
    errors = validate_role_values(values)
    errors.update(_selection_errors(db, current_user, selected_codes))

    if not csrf_is_valid(request, csrf_token_value):
        errors["_form"] = (
            "La sesión del formulario venció. Recargá la página e intentá nuevamente."
        )

    if values["name_key"] and _existing_role_name(db, values["name_key"]):
        errors["name"] = "Ya existe un rol con ese nombre."

    permission_records = None
    if not errors:
        permission_records = _permission_records(db, selected_codes)
        if permission_records is None:
            errors["_form"] = (
                "El catálogo de permisos de la base no coincide con la versión de la aplicación."
            )

    if errors:
        return _role_response(
            request,
            db,
            current_user,
            form_mode="create",
            errors=errors,
            values=values,
            selected_permission_codes=selected_codes,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    role = Role(
        name=values["name"],
        name_key=values["name_key"],
        description=values["description"],
        is_active=True,
    )
    role.permissions = permission_records or []
    db.add(role)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _role_response(
            request,
            db,
            current_user,
            form_mode="create",
            errors={
                "_form": "No se pudo crear el rol porque sus datos entraron en conflicto con otro registro."
            },
            values=values,
            selected_permission_codes=selected_codes,
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(
        url="/configuracion/roles?notice=created",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{role_id}/editar", response_class=HTMLResponse)
def edit_role(role_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = permission_or_redirect(
        request,
        db,
        "system.roles.view",
        "system.roles.edit",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user

    role = _role_by_id(db, role_id)
    if role is None:
        return RedirectResponse(
            url="/configuracion/roles?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    blocked_notice = _role_change_blocked(db, role, current_user)
    if blocked_notice:
        return RedirectResponse(
            url=f"/configuracion/roles?notice={blocked_notice}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    return _role_response(
        request,
        db,
        current_user,
        form_mode="edit",
        editing_role=role,
        values={
            "name": role.name,
            "description": role.description,
            "name_key": role.name_key,
        },
        selected_permission_codes=frozenset(
            permission.code for permission in role.permissions
        ),
    )


@router.post("/{role_id}/editar", response_class=HTMLResponse)
def update_role(
    role_id: int,
    request: Request,
    name: str = Form(""),
    description: str = Form(""),
    permissions: list[str] = Form(default=[]),
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = permission_or_redirect(
        request,
        db,
        "system.roles.view",
        "system.roles.edit",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user

    role = _role_by_id(db, role_id)
    if role is None:
        return RedirectResponse(
            url="/configuracion/roles?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    blocked_notice = _role_change_blocked(db, role, current_user)
    if blocked_notice:
        return RedirectResponse(
            url=f"/configuracion/roles?notice={blocked_notice}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    values = normalized_role_values(name, description)
    selected_codes = frozenset(code.strip() for code in permissions if code.strip())
    errors = validate_role_values(values)
    errors.update(_selection_errors(db, current_user, selected_codes))

    if not csrf_is_valid(request, csrf_token_value):
        errors["_form"] = (
            "La sesión del formulario venció. Recargá la página e intentá nuevamente."
        )

    if (
        values["name_key"]
        and _existing_role_name(
            db,
            values["name_key"],
            exclude_role_id=role.id,
        )
    ):
        errors["name"] = "Ya existe un rol con ese nombre."

    permission_records = None
    if not errors:
        permission_records = _permission_records(db, selected_codes)
        if permission_records is None:
            errors["_form"] = (
                "El catálogo de permisos de la base no coincide con la versión de la aplicación."
            )

    if errors:
        return _role_response(
            request,
            db,
            current_user,
            form_mode="edit",
            editing_role=role,
            errors=errors,
            values=values,
            selected_permission_codes=selected_codes,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    role.name = values["name"]
    role.name_key = values["name_key"]
    role.description = values["description"]
    role.permissions = permission_records or []
    role.updated_at = _utc_now_naive()

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _role_response(
            request,
            db,
            current_user,
            form_mode="edit",
            editing_role=role,
            errors={
                "_form": "No se pudo actualizar el rol porque sus datos entraron en conflicto con otro registro."
            },
            values=values,
            selected_permission_codes=selected_codes,
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(
        url="/configuracion/roles?notice=updated",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{role_id}/estado", response_class=HTMLResponse)
def toggle_role_status(
    role_id: int,
    request: Request,
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = permission_or_redirect(
        request,
        db,
        "system.roles.view",
        "system.roles.status",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not csrf_is_valid(request, csrf_token_value):
        return _role_response(
            request,
            db,
            current_user,
            errors={
                "_form": "La sesión del formulario venció. Recargá la página e intentá nuevamente."
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    role = _role_by_id(db, role_id)
    if role is None:
        return RedirectResponse(
            url="/configuracion/roles?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    blocked_notice = _role_change_blocked(db, role, current_user)
    if blocked_notice:
        return RedirectResponse(
            url=f"/configuracion/roles?notice={blocked_notice}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    role.is_active = not role.is_active
    role.updated_at = _utc_now_naive()
    db.commit()

    notice = "activated" if role.is_active else "deactivated"
    return RedirectResponse(
        url=f"/configuracion/roles?notice={notice}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
