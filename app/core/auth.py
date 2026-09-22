from __future__ import annotations

import ipaddress
import secrets

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.permissions import permission_codes_for_user
from app.models import User


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf_token")
    if not isinstance(token, str) or len(token) < 32:
        token = secrets.token_urlsafe(32)
        request.session["csrf_token"] = token
    return token


def csrf_is_valid(request: Request, token: str) -> bool:
    expected = request.session.get("csrf_token")
    return (
        isinstance(expected, str)
        and bool(token)
        and secrets.compare_digest(token, expected)
    )


def authenticated_user(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not isinstance(user_id, int):
        return None

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        request.session.clear()
        return None

    return user


def permission_or_redirect(
    request: Request,
    db: Session,
    *required_permissions: str,
) -> User | RedirectResponse:
    user = authenticated_user(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    granted = permission_codes_for_user(db, user)
    if not set(required_permissions).issubset(granted):
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return user


def superuser_or_redirect(request: Request, db: Session) -> User | RedirectResponse:
    user = authenticated_user(request, db)
    if user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    if not user.is_superuser:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
    return user


def user_display(user: User) -> tuple[str, str]:
    parts = [part for part in user.name.strip().split() if part]
    first_name = parts[0] if parts else user.username
    initials = "".join(part[0].upper() for part in parts[:2])
    if not initials:
        initials = user.username[:2].upper()
    return first_name, initials


def setup_request_is_allowed(request: Request, *, allow_remote: bool) -> bool:
    if allow_remote:
        return True

    if request.client is None:
        return False

    host = request.client.host.strip().split("%", 1)[0]
    if host.lower() == "localhost":
        return True

    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False
