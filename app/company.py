from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import csrf_is_valid, csrf_token, permission_or_redirect, user_display
from app.core.company_validation import (
    TAX_CONDITIONS,
    normalized_company_values,
    validate_company_values,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.templates import templates
from app.models import Company, User


router = APIRouter(prefix="/configuracion/empresa", include_in_schema=False)


def _company_by_id(db: Session) -> Company | None:
    return db.get(Company, 1)


def _company_values(company: Company | None) -> dict[str, str]:
    if company is None:
        return {
            "legal_name": "",
            "trade_name": "",
            "tax_id": "",
            "tax_condition": "",
            "fiscal_address": "",
            "city": "",
            "province": "",
            "postal_code": "",
            "phone": "",
            "email": "",
        }
    return {
        "legal_name": company.legal_name,
        "trade_name": company.trade_name,
        "tax_id": company.tax_id,
        "tax_condition": company.tax_condition,
        "fiscal_address": company.fiscal_address,
        "city": company.city,
        "province": company.province,
        "postal_code": company.postal_code,
        "phone": company.phone,
        "email": company.email,
    }


def _company_response(
    request: Request,
    current_user: User,
    *,
    company: Company | None = None,
    errors: dict[str, str] | None = None,
    values: dict[str, str] | None = None,
    status_code: int = status.HTTP_200_OK,
):
    first_name, initials = user_display(current_user)
    return templates.TemplateResponse(
        request=request,
        name="company.html",
        context={
            "app_name": settings.app_name,
            "app_version": settings.app_version,
            "current_user": current_user,
            "current_user_first_name": first_name,
            "current_user_initials": initials,
            "csrf_token": csrf_token(request),
            "company": company,
            "values": values if values is not None else _company_values(company),
            "errors": errors or {},
            "tax_conditions": TAX_CONDITIONS,
            "notice_saved": request.query_params.get("notice") == "saved",
        },
        status_code=status_code,
    )


@router.get("", response_class=HTMLResponse)
def company_details(request: Request, db: Session = Depends(get_db)):
    current_user = permission_or_redirect(request, db, "system.company.manage")
    if isinstance(current_user, RedirectResponse):
        return current_user
    company = _company_by_id(db)
    return _company_response(request, current_user, company=company)


@router.post("", response_class=HTMLResponse)
def save_company(
    request: Request,
    legal_name: str = Form(""),
    trade_name: str = Form(""),
    tax_id: str = Form(""),
    tax_condition: str = Form(""),
    fiscal_address: str = Form(""),
    city: str = Form(""),
    province: str = Form(""),
    postal_code: str = Form(""),
    phone: str = Form(""),
    email: str = Form(""),
    csrf_token_value: str = Form("", alias="csrf_token"),
    db: Session = Depends(get_db),
):
    current_user = permission_or_redirect(request, db, "system.company.manage")
    if isinstance(current_user, RedirectResponse):
        return current_user

    values = normalized_company_values(
        legal_name,
        trade_name,
        tax_id,
        tax_condition,
        fiscal_address,
        city,
        province,
        postal_code,
        phone,
        email,
    )
    errors = validate_company_values(values)

    if not csrf_is_valid(request, csrf_token_value):
        errors["_form"] = (
            "La sesión del formulario venció. Recargá la página e intentá nuevamente."
        )

    company = _company_by_id(db)
    if errors:
        return _company_response(
            request,
            current_user,
            company=company,
            errors=errors,
            values=values,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if company is None:
        company = Company(id=1, **values)
        db.add(company)
    else:
        for field, value in values.items():
            setattr(company, field, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return _company_response(
            request,
            current_user,
            company=_company_by_id(db),
            errors={
                "_form": "No se pudieron guardar los datos de la empresa porque entraron en conflicto con otro registro."
            },
            values=values,
            status_code=status.HTTP_409_CONFLICT,
        )

    return RedirectResponse(
        url="/configuracion/empresa?notice=saved",
        status_code=status.HTTP_303_SEE_OTHER,
    )
