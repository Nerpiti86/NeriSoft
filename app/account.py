from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.auth import authenticated_user, csrf_token, user_display
from app.core.config import settings
from app.core.database import get_db
from app.core.permissions import permission_codes_for_user
from app.core.templates import templates
from app.models import User


router = APIRouter(include_in_schema=False)


@router.get("/mi-cuenta", response_class=HTMLResponse)
def my_account(request: Request, db: Session = Depends(get_db)):
    session_user = authenticated_user(request, db)
    if session_user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    current_user = db.scalar(
        select(User)
        .options(selectinload(User.roles))
        .where(User.id == session_user.id)
    ) or session_user

    granted_codes = permission_codes_for_user(db, current_user)
    first_name, initials = user_display(current_user)

    return templates.TemplateResponse(
        request=request,
        name="account.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": current_user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": csrf_token(request),
            "assigned_roles": tuple(sorted(current_user.roles, key=lambda role: role.name.lower())),
            "effective_permission_count": len(granted_codes),
        },
    )
