from __future__ import annotations

import re
import secrets
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import database_is_ready, get_db
from app.core.security import hash_password
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

app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")


def _users_exist(db: Session) -> bool:
    user_count = db.scalar(select(func.count(User.id))) or 0
    return user_count > 0


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


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
        },
    )


@app.get("/login", response_class=HTMLResponse, include_in_schema=False)
def login(request: Request, db: Session = Depends(get_db)):
    if not _users_exist(db):
        return RedirectResponse(url="/setup", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
        },
    )


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
