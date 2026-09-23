from __future__ import annotations

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.auth import authenticated_user, csrf_token, user_display
from app.core.config import settings
from app.core.database import get_db
from app.core.permissions import permission_codes_for_user
from app.core.templates import templates


router = APIRouter(prefix="/configuracion", include_in_schema=False)


@router.get("", response_class=HTMLResponse)
def configuration_home(request: Request, db: Session = Depends(get_db)):
    current_user = authenticated_user(request, db)
    if current_user is None:
        return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    granted_codes = permission_codes_for_user(db, current_user)
    first_name, initials = user_display(current_user)

    return templates.TemplateResponse(
        request=request,
        name="configuration.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": current_user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": csrf_token(request),
            "can_manage_company": "system.company.manage" in granted_codes,
            "can_view_users": "system.users.view" in granted_codes,
            "can_view_roles": "system.roles.view" in granted_codes,
        },
    )
