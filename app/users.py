from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.auth import csrf_is_valid, csrf_token, permission_or_redirect, user_display
from app.core.config import settings
from app.core.database import get_db
from app.core.permissions import (
    permission_codes_for_user,
    role_is_within_user_scope,
    user_is_within_user_scope,
)
from app.core.security import hash_password
from app.core.templates import templates
from app.core.user_validation import normalized_user_values, validate_user_identity
from app.models import Role, User


router = APIRouter(prefix="/configuracion/usuarios", include_in_schema=False)


def _duplicate_identity_errors(
    db: Session,
    *,
    username: str,
    email: str,
    exclude_user_id: int | None = None,
) -> dict[str, str]:
    statement = select(User).where(or_(User.username == username, User.email == email))
    if exclude_user_id is not None:
        statement = statement.where(User.id != exclude_user_id)

    errors: dict[str, str] = {}
    for existing in db.scalars(statement).all():
        if existing.username == username:
            errors["username"] = "Ese nombre de usuario ya está en uso."
        if existing.email == email:
            errors["email"] = "Ese correo electrónico ya está en uso."
    return errors


def _user_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )


def _roles_for_scope(db: Session, current_user: User) -> tuple[Role, ...]:
    roles = tuple(
        db.scalars(
            select(Role)
            .options(selectinload(Role.permissions))
            .order_by(func.lower(Role.name))
        ).all()
    )
    if current_user.is_superuser:
        return roles
    return tuple(role for role in roles if role_is_within_user_scope(db, role.id, current_user))


def _parse_role_ids(raw_role_ids: list[str]) -> tuple[frozenset[int], str | None]:
    parsed: set[int] = set()
    for raw_value in raw_role_ids:
        try:
            role_id = int(raw_value)
        except (TypeError, ValueError):
            return frozenset(), "La selección de roles contiene un valor inválido."
        if role_id <= 0:
            return frozenset(), "La selección de roles contiene un valor inválido."
        parsed.add(role_id)
    return frozenset(parsed), None


def _role_selection(
    db: Session,
    current_user: User,
    selected_ids: frozenset[int],
) -> tuple[list[Role], dict[str, str]]:
    allowed_roles = _roles_for_scope(db, current_user)
    allowed_by_id = {role.id: role for role in allowed_roles}
    if not selected_ids.issubset(allowed_by_id):
        return [], {
            "roles": "No podés asignar roles que estén fuera de tu propio alcance de permisos."
        }
    return [role for role in allowed_roles if role.id in selected_ids], {}


def _users_response(
    request: Request,
    db: Session,
    current_user: User,
    *,
    form_mode: str | None = None,
    editing_user: User | None = None,
    errors: dict[str, str] | None = None,
    values: dict[str, str] | None = None,
    selected_role_ids: frozenset[int] | None = None,
    status_code: int = status.HTTP_200_OK,
    notice: str | None = None,
):
    search_value = request.query_params.get("q", "").strip()
    state_filter = request.query_params.get("estado", "todos").strip().lower()
    if state_filter not in {"todos", "activos", "inactivos"}:
        state_filter = "todos"

    statement = select(User).options(
        selectinload(User.roles).selectinload(Role.permissions)
    )
    if search_value:
        pattern = f"%{search_value.lower()}%"
        statement = statement.where(
            or_(
                func.lower(User.name).like(pattern),
                func.lower(User.username).like(pattern),
                func.lower(User.email).like(pattern),
            )
        )

    if state_filter == "activos":
        statement = statement.where(User.is_active.is_(True))
    elif state_filter == "inactivos":
        statement = statement.where(User.is_active.is_(False))

    statement = statement.order_by(func.lower(User.name), func.lower(User.username))
    users = list(db.scalars(statement).all())

    total_users = db.scalar(select(func.count(User.id))) or 0
    active_users = db.scalar(
        select(func.count(User.id)).where(User.is_active.is_(True))
    ) or 0
    superusers = db.scalar(
        select(func.count(User.id)).where(User.is_superuser.is_(True))
    ) or 0

    granted_codes = permission_codes_for_user(db, current_user)
    can_create_users = "system.users.create" in granted_codes
    can_edit_users = "system.users.edit" in granted_codes
    can_change_user_status = "system.users.status" in granted_codes
    can_assign_roles = "system.users.assign_roles" in granted_codes

    user_manageable = {
        user.id: user_is_within_user_scope(db, user, current_user) for user in users
    }
    if editing_user is not None:
        editing_user_manageable = user_is_within_user_scope(db, editing_user, current_user)
        user_manageable[editing_user.id] = editing_user_manageable
    else:
        editing_user_manageable = False

    assignable_roles = _roles_for_scope(db, current_user) if can_assign_roles else tuple()
    assignable_role_ids = frozenset(role.id for role in assignable_roles)

    if selected_role_ids is None:
        if editing_user is not None:
            selected_role_ids = frozenset(
                role.id for role in editing_user.roles if role.id in assignable_role_ids
            )
        else:
            selected_role_ids = frozenset()

    can_edit_identity = form_mode == "create" or (
        form_mode == "edit" and can_edit_users and editing_user_manageable
    )
    can_assign_roles_to_form_user = can_assign_roles and (
        form_mode == "create"
        or (
            form_mode == "edit"
            and editing_user is not None
            and editing_user_manageable
            and editing_user.id != current_user.id
        )
    )

    hidden_assigned_roles = 0
    if editing_user is not None:
        hidden_assigned_roles = sum(
            1 for role in editing_user.roles if role.id not in assignable_role_ids
        )

    notice_key = notice or request.query_params.get("notice")
    notices = {
        "created": ("success", "Usuario creado correctamente."),
        "updated": ("success", "Usuario actualizado correctamente."),
        "activated": ("success", "Usuario activado correctamente."),
        "deactivated": ("success", "Usuario desactivado correctamente."),
        "self-status-blocked": (
            "warning",
            "No podés desactivar tu propia sesión administrativa.",
        ),
        "target-protected": (
            "warning",
            "Ese usuario tiene un nivel de acceso fuera de tu alcance y no puede ser modificado desde esta sesión.",
        ),
        "not-found": ("warning", "El usuario solicitado ya no existe."),
    }
    notice_payload = notices.get(notice_key or "")

    first_name, initials = user_display(current_user)
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": current_user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": csrf_token(request),
            "users": users,
            "total_users": total_users,
            "active_users": active_users,
            "superusers": superusers,
            "search_value": search_value,
            "state_filter": state_filter,
            "form_mode": form_mode,
            "editing_user": editing_user,
            "errors": errors or {},
            "values": values or {},
            "notice_kind": notice_payload[0] if notice_payload else None,
            "notice_message": notice_payload[1] if notice_payload else None,
            "can_create_users": can_create_users,
            "can_edit_users": can_edit_users,
            "can_change_user_status": can_change_user_status,
            "can_assign_roles": can_assign_roles,
            "can_edit_identity": can_edit_identity,
            "can_assign_roles_to_form_user": can_assign_roles_to_form_user,
            "assignable_roles": assignable_roles,
            "selected_role_ids": selected_role_ids,
            "hidden_assigned_roles": hidden_assigned_roles,
            "user_manageable": user_manageable,
        },
        status_code=status_code,
    )


def _mutation_permissions(db: Session, current_user: User) -> frozenset[str]:
    return permission_codes_for_user(db, current_user).intersection(
        {"system.users.edit", "system.users.assign_roles"}
    )


@router.get("", response_class=HTMLResponse)
def users_list(request: Request, db: Session = Depends(get_db)):
    current_user = permission_or_redirect(request, db, "system.users.view")
    if isinstance(current_user, RedirectResponse):
        return current_user
    return _users_response(request, db, current_user)


@router.get("/nuevo", response_class=HTMLResponse)
def new_user(request: Request, db: Session = Depends(get_db)):
    current_user = permission_or_redirect(
        request,
        db,
        "system.users.view",
        "system.users.create",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user
    return _users_response(request, db, current_user, form_mode="create")


@router.post("/nuevo", response_class=HTMLResponse)
def create_user(
    request: Request,
    name: str = Form(""),
    username: str = Form(""),
    email: str = Form(""),
    password: str = Form(""),
    password_confirm: str = Form(""),
    is_superuser: str = Form(""),
    roles: list[str] = Form(default=[]),
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = permission_or_redirect(
        request,
        db,
        "system.users.view",
        "system.users.create",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user

    granted_codes = permission_codes_for_user(db, current_user)
    can_assign_roles = "system.users.assign_roles" in granted_codes

    values = normalized_user_values(name, username, email)
    values["is_superuser"] = "1" if is_superuser == "1" else ""
    errors = validate_user_identity(values)

    if not csrf_is_valid(request, csrf_token_value):
        errors["_form"] = (
            "La sesión del formulario venció. Recargá la página e intentá nuevamente."
        )

    if not 10 <= len(password) <= 128:
        errors["password"] = "La contraseña debe tener entre 10 y 128 caracteres."

    if password != password_confirm:
        errors["password_confirm"] = "Las contraseñas no coinciden."

    if is_superuser == "1" and not current_user.is_superuser:
        errors["_form"] = "Solo un administrador del sistema puede crear otro administrador."

    errors.update(
        _duplicate_identity_errors(
            db,
            username=values["username"],
            email=values["email"],
        )
    )

    selected_role_ids, role_parse_error = _parse_role_ids(roles)
    role_records: list[Role] = []
    if role_parse_error:
        errors["roles"] = role_parse_error
    elif selected_role_ids and not can_assign_roles:
        errors["roles"] = "No tenés permiso para asignar roles a usuarios."
    elif can_assign_roles:
        role_records, role_errors = _role_selection(db, current_user, selected_role_ids)
        errors.update(role_errors)

    if errors:
        return _users_response(
            request,
            db,
            current_user,
            form_mode="create",
            errors=errors,
            values=values,
            selected_role_ids=selected_role_ids,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    user = User(
        name=values["name"],
        username=values["username"],
        email=values["email"],
        password_hash=hash_password(password),
        is_active=True,
        is_superuser=current_user.is_superuser and is_superuser == "1",
        roles=role_records,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _users_response(
            request,
            db,
            current_user,
            form_mode="create",
            errors={
                "_form": "No se pudo crear el usuario porque los datos entraron en conflicto con otro registro."
            },
            values=values,
            selected_role_ids=selected_role_ids,
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(
        url="/configuracion/usuarios?notice=created",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{user_id}/editar", response_class=HTMLResponse)
def edit_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = permission_or_redirect(request, db, "system.users.view")
    if isinstance(current_user, RedirectResponse):
        return current_user

    allowed_mutations = _mutation_permissions(db, current_user)
    if not allowed_mutations:
        return RedirectResponse(url="/configuracion/usuarios", status_code=status.HTTP_303_SEE_OTHER)

    target_user = _user_by_id(db, user_id)
    if target_user is None:
        return RedirectResponse(
            url="/configuracion/usuarios?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if not user_is_within_user_scope(db, target_user, current_user):
        return RedirectResponse(
            url="/configuracion/usuarios?notice=target-protected",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if target_user.id == current_user.id and "system.users.edit" not in allowed_mutations:
        return RedirectResponse(url="/configuracion/usuarios", status_code=status.HTTP_303_SEE_OTHER)

    values = {
        "name": target_user.name,
        "username": target_user.username,
        "email": target_user.email,
        "is_superuser": "1" if target_user.is_superuser else "",
    }
    return _users_response(
        request,
        db,
        current_user,
        form_mode="edit",
        editing_user=target_user,
        values=values,
    )


@router.post("/{user_id}/editar", response_class=HTMLResponse)
def update_user(
    user_id: int,
    request: Request,
    name: str = Form(""),
    username: str = Form(""),
    email: str = Form(""),
    is_superuser: str = Form(""),
    roles: list[str] = Form(default=[]),
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = permission_or_redirect(request, db, "system.users.view")
    if isinstance(current_user, RedirectResponse):
        return current_user

    allowed_mutations = _mutation_permissions(db, current_user)
    if not allowed_mutations:
        return RedirectResponse(url="/configuracion/usuarios", status_code=status.HTTP_303_SEE_OTHER)

    target_user = _user_by_id(db, user_id)
    if target_user is None:
        return RedirectResponse(
            url="/configuracion/usuarios?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if not user_is_within_user_scope(db, target_user, current_user):
        return RedirectResponse(
            url="/configuracion/usuarios?notice=target-protected",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    can_edit_identity = "system.users.edit" in allowed_mutations
    can_assign_roles = (
        "system.users.assign_roles" in allowed_mutations
        and target_user.id != current_user.id
    )

    if target_user.id == current_user.id and not can_edit_identity:
        return RedirectResponse(url="/configuracion/usuarios", status_code=status.HTTP_303_SEE_OTHER)

    if can_edit_identity:
        values = normalized_user_values(name, username, email)
        values["is_superuser"] = "1" if is_superuser == "1" else ""
        errors = validate_user_identity(values)
        errors.update(
            _duplicate_identity_errors(
                db,
                username=values["username"],
                email=values["email"],
                exclude_user_id=target_user.id,
            )
        )
    else:
        values = {
            "name": target_user.name,
            "username": target_user.username,
            "email": target_user.email,
            "is_superuser": "1" if target_user.is_superuser else "",
        }
        errors = {}

    if not csrf_is_valid(request, csrf_token_value):
        errors["_form"] = (
            "La sesión del formulario venció. Recargá la página e intentá nuevamente."
        )

    if is_superuser == "1" and not current_user.is_superuser and not target_user.is_superuser:
        errors["_form"] = "Solo un administrador del sistema puede otorgar acceso administrativo."

    selected_role_ids = frozenset(
        role.id for role in target_user.roles if role_is_within_user_scope(db, role.id, current_user)
    )
    role_records: list[Role] = []
    editable_role_ids: frozenset[int] = frozenset()

    if can_assign_roles:
        selected_role_ids, role_parse_error = _parse_role_ids(roles)
        if role_parse_error:
            errors["roles"] = role_parse_error
        else:
            role_records, role_errors = _role_selection(db, current_user, selected_role_ids)
            errors.update(role_errors)
            editable_role_ids = frozenset(role.id for role in _roles_for_scope(db, current_user))
    elif roles:
        errors["roles"] = "No tenés permiso para modificar los roles de este usuario."

    if errors:
        return _users_response(
            request,
            db,
            current_user,
            form_mode="edit",
            editing_user=target_user,
            errors=errors,
            values=values,
            selected_role_ids=selected_role_ids,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if can_edit_identity:
        target_user.name = values["name"]
        target_user.username = values["username"]
        target_user.email = values["email"]

    if current_user.is_superuser and target_user.id != current_user.id:
        target_user.is_superuser = is_superuser == "1"

    if can_assign_roles:
        preserved_roles = [
            role for role in target_user.roles if role.id not in editable_role_ids
        ]
        target_user.roles = preserved_roles + role_records

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _users_response(
            request,
            db,
            current_user,
            form_mode="edit",
            editing_user=target_user,
            errors={
                "_form": "No se pudo actualizar el usuario porque los datos entraron en conflicto con otro registro."
            },
            values=values,
            selected_role_ids=selected_role_ids,
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(
        url="/configuracion/usuarios?notice=updated",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.post("/{user_id}/estado", response_class=HTMLResponse)
def toggle_user_status(
    user_id: int,
    request: Request,
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = permission_or_redirect(
        request,
        db,
        "system.users.view",
        "system.users.status",
    )
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not csrf_is_valid(request, csrf_token_value):
        return _users_response(
            request,
            db,
            current_user,
            errors={
                "_form": "La sesión del formulario venció. Recargá la página e intentá nuevamente."
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    target_user = _user_by_id(db, user_id)
    if target_user is None:
        return RedirectResponse(
            url="/configuracion/usuarios?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if target_user.id == current_user.id:
        return RedirectResponse(
            url="/configuracion/usuarios?notice=self-status-blocked",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    if not user_is_within_user_scope(db, target_user, current_user):
        return RedirectResponse(
            url="/configuracion/usuarios?notice=target-protected",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    target_user.is_active = not target_user.is_active
    db.commit()

    notice = "activated" if target_user.is_active else "deactivated"
    return RedirectResponse(
        url=f"/configuracion/usuarios?notice={notice}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
