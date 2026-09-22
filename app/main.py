from __future__ import annotations

import re
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import settings
from app.core.database import database_is_ready, get_db
from app.core.security import hash_password, verify_password
from app.models import User


templates = Jinja2Templates(directory=str(settings.templates_dir))
SETUP_TOKEN = secrets.token_urlsafe(32)
USERNAME_RE = re.compile(r"^[a-z0-9._-]+$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    settings.data_dir.mkdir(parents=True, exist_ok=True)
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


def _users_exist(db: Session) -> bool:
    user_count = db.scalar(select(func.count(User.id))) or 0
    return user_count > 0


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


def _user_display(user: User) -> tuple[str, str]:
    parts = [part for part in user.name.strip().split() if part]
    first_name = parts[0] if parts else user.username
    initials = "".join(part[0].upper() for part in parts[:2])
    if not initials:
        initials = user.username[:2].upper()
    return first_name, initials


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
            "csrf_token": _csrf_token(request),
            "login_error": error,
            "values": {"username": username},
        },
        status_code=status_code,
    )


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request, db: Session = Depends(get_db)):
    if not _users_exist(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

    user = _authenticated_user(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    first_name, initials = _user_display(user)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": _csrf_token(request),
        },
    )


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login(request: Request, db: Session = Depends(get_db)):
    if not _users_exist(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

    if _authenticated_user(request, db) is not None:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    return _login_response(request)


@app.post("/login", response_class=HTMLResponse, include_in_schema=False)
def authenticate(
    request: Request,
    username: str = Form(""),
    password: str = Form(""),
    csrf_token: str = Form(""),
    db: Session = Depends(get_db),
):
    if not _users_exist(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

    identity = username.strip().lower()

    if not _csrf_is_valid(request, csrf_token):
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
    csrf_token: str = Form(""),
):
    if not _csrf_is_valid(request, csrf_token):
        request.session.clear()
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    request.session.clear()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/setup", response_class=HTMLResponse, include_in_schema=False)
def setup(request: Request, db: Session = Depends(get_db)):
    if _users_exist(db):
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
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

    clean_name = name.strip()
    clean_username = username.strip().lower()
    clean_email = email.strip().lower()
    values = {
        "name": clean_name,
        "username": clean_username,
        "email": clean_email,
    }
    errors: dict[str, str] = {}

    if not secrets.compare_digest(setup_token, SETUP_TOKEN):
        errors["_form"] = "La sesión de configuración venció. Recargá la página e intentá nuevamente."

    if len(clean_name) < 2 or len(clean_name) > 120:
        errors["name"] = "Ingresá un nombre válido de hasta 120 caracteres."

    if not 3 <= len(clean_username) <= 64 or not USERNAME_RE.fullmatch(clean_username):
        errors["username"] = "Usá entre 3 y 64 caracteres: letras, números, punto, guion o guion bajo."

    if len(clean_email) > 254 or not EMAIL_RE.fullmatch(clean_email):
        errors["email"] = "Ingresá un correo electrónico válido."

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
        name=clean_name,
        username=clean_username,
        email=clean_email,
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
