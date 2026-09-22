from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import csrf_is_valid, csrf_token, superuser_or_redirect, user_display
from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password
from app.core.templates import templates
from app.core.user_validation import normalized_user_values, validate_user_identity
from app.models import User


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


def _users_response(
    request: Request,
    db: Session,
    current_user: User,
    *,
    form_mode: str | None = None,
    editing_user: User | None = None,
    errors: dict[str, str] | None = None,
    values: dict[str, str] | None = None,
    status_code: int = status.HTTP_200_OK,
    notice: str | None = None,
):
    search_value = request.query_params.get("q", "").strip()
    state_filter = request.query_params.get("estado", "todos").strip().lower()
    if state_filter not in {"todos", "activos", "inactivos"}:
        state_filter = "todos"

    statement = select(User)
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

    notice_key = notice or request.query_params.get("notice")
    notices = {
        "created": ("success", "Usuario creado correctamente."),
        "updated": ("success", "Usuario actualizado correctamente."),
        "activated": ("success", "Usuario activado correctamente."),
        "deactivated": ("success", "Usuario desactivado correctamente."),
        "self-status-blocked": ("warning", "No podés desactivar tu propia sesión administrativa."),
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
        },
        status_code=status_code,
    )


@router.get("", response_class=HTMLResponse)
def users_list(request: Request, db: Session = Depends(get_db)):
    current_user = superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    return _users_response(request, db, current_user)


@router.get("/nuevo", response_class=HTMLResponse)
def new_user(request: Request, db: Session = Depends(get_db)):
    current_user = superuser_or_redirect(request, db)
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
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    values = normalized_user_values(name, username, email)
    values["is_superuser"] = "1" if is_superuser == "1" else ""
    errors = validate_user_identity(values)

    if not csrf_is_valid(request, csrf_token_value):
        errors["_form"] = "La sesión del formulario venció. Recargá la página e intentá nuevamente."

    if not 10 <= len(password) <= 128:
        errors["password"] = "La contraseña debe tener entre 10 y 128 caracteres."

    if password != password_confirm:
        errors["password_confirm"] = "Las contraseñas no coinciden."

    errors.update(
        _duplicate_identity_errors(
            db,
            username=values["username"],
            email=values["email"],
        )
    )

    if errors:
        return _users_response(
            request,
            db,
            current_user,
            form_mode="create",
            errors=errors,
            values=values,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    user = User(
        name=values["name"],
        username=values["username"],
        email=values["email"],
        password_hash=hash_password(password),
        is_active=True,
        is_superuser=is_superuser == "1",
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
            errors={"_form": "No se pudo crear el usuario porque los datos entraron en conflicto con otro registro."},
            values=values,
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(
        url="/configuracion/usuarios?notice=created",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/{user_id}/editar", response_class=HTMLResponse)
def edit_user(user_id: int, request: Request, db: Session = Depends(get_db)):
    current_user = superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    target_user = db.get(User, user_id)
    if target_user is None:
        return RedirectResponse(
            url="/configuracion/usuarios?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

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
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    target_user = db.get(User, user_id)
    if target_user is None:
        return RedirectResponse(
            url="/configuracion/usuarios?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    values = normalized_user_values(name, username, email)
    values["is_superuser"] = "1" if is_superuser == "1" else ""
    errors = validate_user_identity(values)

    if not csrf_is_valid(request, csrf_token_value):
        errors["_form"] = "La sesión del formulario venció. Recargá la página e intentá nuevamente."

    errors.update(
        _duplicate_identity_errors(
            db,
            username=values["username"],
            email=values["email"],
            exclude_user_id=target_user.id,
        )
    )

    if errors:
        return _users_response(
            request,
            db,
            current_user,
            form_mode="edit",
            editing_user=target_user,
            errors=errors,
            values=values,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    target_user.name = values["name"]
    target_user.username = values["username"]
    target_user.email = values["email"]
    if target_user.id != current_user.id:
        target_user.is_superuser = is_superuser == "1"

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
            errors={"_form": "No se pudo actualizar el usuario porque los datos entraron en conflicto con otro registro."},
            values=values,
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
    current_user = superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not csrf_is_valid(request, csrf_token_value):
        return _users_response(
            request,
            db,
            current_user,
            errors={"_form": "La sesión del formulario venció. Recargá la página e intentá nuevamente."},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    target_user = db.get(User, user_id)
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

    target_user.is_active = not target_user.is_active
    db.commit()

    notice = "activated" if target_user.is_active else "deactivated"
    return RedirectResponse(
        url=f"/configuracion/usuarios?notice={notice}",
        status_code=status.HTTP_303_SEE_OTHER,
    )
