from __future__ import annotations

import re
import secrets

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import hash_password
from app.models import User


router = APIRouter(prefix="/configuracion/usuarios", include_in_schema=False)
templates = Jinja2Templates(directory=str(settings.templates_dir))
USERNAME_RE = re.compile(r"^[a-z0-9._-]+$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not isinstance(token, str) or len(token) < 32:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def _csrf_is_valid(request: Request, token: str) -> bool:
    expected = request.session.get("csrf_token")
    return (
        isinstance(expected, str)
        and bool(token)
        and secrets.compare_digest(token, expected)
    )


def _authenticated_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        return None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        request.session.clear()
        return None

    return user


def _superuser_or_redirect(request: Request, db: Session) -> User | RedirectResponse:
    user = _authenticated_user(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if not user.is_superuser:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return user


def _user_display(user: User) -> tuple[str, str]:
    parts = [part for part in user.name.strip().split() if part]
    first_name = parts[0] if parts else user.username
    initials = "".join(part[0].upper() for part in parts[:2])
    if not initials:
        initials = user.username[:2].upper()
    return first_name, initials


def _normalized_user_values(name: str, username: str, email: str) -> dict[str, str]:
    return {
        "name": name.strip(),
        "username": username.strip().lower(),
        "email": email.strip().lower(),
    }


def _validate_user_identity(values: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    clean_name = values["name"]
    clean_username = values["username"]
    clean_email = values["email"]

    if len(clean_name) < 2 or len(clean_name) > 120:
        errors["name"] = "Ingresá un nombre válido de hasta 120 caracteres."

    if not 3 <= len(clean_username) <= 64 or not USERNAME_RE.fullmatch(clean_username):
        errors["username"] = "Usá entre 3 y 64 caracteres: letras, números, punto, guion o guion bajo."

    if len(clean_email) > 254 or not EMAIL_RE.fullmatch(clean_email):
        errors["email"] = "Ingresá un correo electrónico válido."

    return errors


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

    first_name, initials = _user_display(current_user)
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": current_user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": _csrf_token(request),
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
    current_user = _superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user
    return _users_response(request, db, current_user)


@router.get("/nuevo", response_class=HTMLResponse)
def new_user(request: Request, db: Session = Depends(get_db)):
    current_user = _superuser_or_redirect(request, db)
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
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    current_user = _superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    values = _normalized_user_values(name, username, email)
    values["is_superuser"] = "1" if is_superuser == "1" else ""
    errors = _validate_user_identity(values)

    if not _csrf_is_valid(request, csrf_token):
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
    current_user = _superuser_or_redirect(request, db)
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
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    current_user = _superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    target_user = db.get(User, user_id)
    if target_user is None:
        return RedirectResponse(
            url="/configuracion/usuarios?notice=not-found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    values = _normalized_user_values(name, username, email)
    values["is_superuser"] = "1" if is_superuser == "1" else ""
    errors = _validate_user_identity(values)

    if not _csrf_is_valid(request, csrf_token):
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
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    current_user = _superuser_or_redirect(request, db)
    if isinstance(current_user, RedirectResponse):
        return current_user

    if not _csrf_is_valid(request, csrf_token):
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
