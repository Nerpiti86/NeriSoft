from __future__ import annotations

import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.core.assets import ensure_vendor_assets_ready
from app.core.auth import (
    authenticated_user,
    csrf_is_valid,
    csrf_token,
    setup_request_is_allowed,
    user_display,
)
from app.core.config import settings
from app.core.database import database_is_ready, get_db
from app.core.security import hash_password, verify_password
from app.core.templates import templates
from app.core.user_validation import normalized_user_values, validate_user_identity
from app.models import User
from app.users import router as users_router


SETUP_TOKEN = secrets.token_urlsafe(32)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    ensure_vendor_assets_ready()
    database_is_ready()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/api/docs",
    redoc_url=None,
    lifespan=lifespan,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="nerisoft_session",
    max_age=8 * 60 * 60,
    same_site="lax",
    https_only=settings.session_https_only,
)

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")
app.include_router(users_router)


def _users_exist(db: Session) -> bool:
    user_count = db.scalar(select(func.count(User.id))) or 0
    return user_count > 0


def _require_setup_access(request: Request) -> None:
    if setup_request_is_allowed(request, allow_remote=settings.setup_allow_remote):
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "La configuración inicial debe realizarse desde el servidor de NERISOFT. "
            "Para habilitarla temporalmente desde la LAN usá NERISOFT_SETUP_ALLOW_REMOTE=true."
        ),
    )


def _setup_response(
    request: Request,
    *,
    errors: dict[str, str] | None = None,
    values: dict[str, str] | None = None,
    status_code: int = status.HTTP_200_OK,
):
    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "setup_token": SETUP_TOKEN,
            "errors": errors or {},
            "values": values or {},
        },
        status_code=status_code,
    )


def _login_response(
    request: Request,
    *,
    error: str | None = None,
    username: str = "",
    status_code: int = status.HTTP_200_OK,
):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "csrf_token": csrf_token(request),
            "login_error": error,
            "values": {"username": username},
        },
        status_code=status_code,
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request, db: Session = Depends(get_db)):
    if not _users_exist(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

    user = authenticated_user(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    first_name, initials = user_display(user)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": csrf_token(request),
        },
    )


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login(request: Request, db: Session = Depends(get_db)):
    if not _users_exist(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

    if authenticated_user(request, db) is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return _login_response(request)


@app.post("/login", response_class=HTMLResponse, include_in_schema=False)
def authenticate(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    if not _users_exist(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

    identity = username.strip().lower()

    if not csrf_is_valid(request, csrf_token_value):
        request.session.clear()
        return _login_response(
            request,
            error="La sesión de acceso venció. Recargá la página e intentá nuevamente.",
            username=identity,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if not identity or not password:
        return _login_response(
            request,
            error="Ingresá tu usuario o correo y contraseña.",
            username=identity,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    user = db.scalar(
        select(User).where(
            or_(
                User.username == identity,
                User.email == identity,
            )
        )
    )

    valid_credentials = (
        user is not None
        and user.is_active
        and verify_password(password, user.password_hash)
    )

    if not valid_credentials:
        return _login_response(
            request,
            error="Usuario o contraseña incorrectos.",
            username=identity,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session.clear()
    request.session["user_id"] = user.id
    request.session["csrf_token"] = secrets.token_urlsafe(32)

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/logout", include_in_schema=False)
def logout(
    request: Request,
    csrf_token_value: str = Form("", alias="csrf_token"),
):
    if not csrf_is_valid(request, csrf_token_value):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/setup", response_class=HTMLResponse, include_in_schema=False)
def setup(request: Request, db: Session = Depends(get_db)):
    if _users_exist(db):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    _require_setup_access(request)
    return _setup_response(request)


@app.post("/setup", response_class=HTMLResponse, include_in_schema=False)
def create_initial_admin(
    request: Request,
    name: str = Form(...),
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password_confirm: str = Form(...),
    setup_token: str = Form(...),
    db: Session = Depends(get_db),
):
    if _users_exist(db):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    _require_setup_access(request)

    values = normalized_user_values(name, username, email)
    errors = validate_user_identity(values)

    if not secrets.compare_digest(setup_token, SETUP_TOKEN):
        errors["_form"] = "La sesión de configuración venció. Recargá la página e intentá nuevamente."

    if not 10 <= len(password) <= 128:
        errors["password"] = "La contraseña debe tener entre 10 y 128 caracteres."

    if password != password_confirm:
        errors["password_confirm"] = "Las contraseñas no coinciden."

    if errors:
        return _setup_response(
            request,
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
        is_superuser=True,
    )
    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        if _users_exist(db):
            return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
        return _setup_response(
            request,
            errors={"_form": "No se pudo crear el administrador. Revisá los datos e intentá nuevamente."},
            values=values,
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    database_is_ready()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": "ok",
    }
