from __future__ import annotations

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.company import company_details, save_company
from app.core.database import Base
from app.main import app
from app.models import Company, Permission, Role, User


CSRF_TOKEN = "company-test-csrf-token-000000000000"


def _request(
    path: str = "/configuracion/empresa",
    *,
    user_id: int | None = None,
    csrf_token: str | None = None,
    query_string: bytes = b"",
) -> Request:
    session: dict[str, object] = {}
    if user_id is not None:
        session["user_id"] = user_id
    if csrf_token is not None:
        session["csrf_token"] = csrf_token

    return Request(
        {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "GET",
            "scheme": "http",
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "root_path": "",
            "headers": [],
            "client": ("127.0.0.1", 12345),
            "server": ("127.0.0.1", 8000),
            "session": session,
            "app": app,
            "router": app.router,
        }
    )


def _user(username: str, *, is_superuser: bool = False) -> User:
    return User(
        name=username.title(),
        username=username,
        email=f"{username}@example.com",
        password_hash="hash",
        is_active=True,
        is_superuser=is_superuser,
    )


def _grant_company_permission(user: User) -> None:
    permission = Permission(
        code="system.company.manage",
        module="Empresa",
        name="Administrar datos de empresa",
        description="",
    )
    role = Role(
        name="Empresa",
        name_key="empresa",
        is_active=True,
        permissions=[permission],
    )
    user.roles = [role]


def _save(request: Request, db: Session, **overrides: str):
    values = {
        "legal_name": "Empresa de Prueba S.A.",
        "trade_name": "Empresa Prueba",
        "tax_id": "30-71234567-1",
        "tax_condition": "IVA RESPONSABLE INSCRITO",
        "fiscal_address": "Calle 123",
        "city": "Rosario",
        "province": "Santa Fe",
        "postal_code": "2000",
        "phone": "",
        "email": "empresa@example.com",
        "csrf_token_value": CSRF_TOKEN,
    }
    values.update(overrides)
    return save_company(request=request, db=db, **values)


def test_company_routes_are_registered_in_application() -> None:
    route_paths = {
        route.path
        for route in app.routes
        if getattr(route, "path", None)
    }
    assert "/configuracion/empresa" in route_paths


def test_company_routes_require_manage_permission() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = _user("operador")
        db.add(user)
        db.commit()

        read_response = company_details(_request(user_id=user.id), db=db)
        write_response = _save(
            _request(user_id=user.id, csrf_token=CSRF_TOKEN),
            db,
        )

        assert isinstance(read_response, RedirectResponse)
        assert read_response.headers["location"] == "/"
        assert isinstance(write_response, RedirectResponse)
        assert write_response.headers["location"] == "/"
        assert db.get(Company, 1) is None


def test_company_manage_permission_allows_reading_and_writing_company() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = _user("gestor")
        _grant_company_permission(user)
        db.add(user)
        db.commit()

        read_response = company_details(
            _request(user_id=user.id, csrf_token=CSRF_TOKEN),
            db=db,
        )
        assert read_response.status_code == 200

        write_response = _save(
            _request(user_id=user.id, csrf_token=CSRF_TOKEN),
            db,
        )
        assert isinstance(write_response, RedirectResponse)
        assert write_response.status_code == 303
        assert db.get(Company, 1) is not None


def test_superuser_can_create_and_update_single_company() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = _user("administrador", is_superuser=True)
        db.add(user)
        db.commit()

        first_response = _save(
            _request(user_id=user.id, csrf_token=CSRF_TOKEN),
            db,
        )
        assert isinstance(first_response, RedirectResponse)
        assert first_response.status_code == 303

        company = db.get(Company, 1)
        assert company is not None
        assert company.tax_id == "30712345671"
        assert company.email == "empresa@example.com"

        second_response = _save(
            _request(user_id=user.id, csrf_token=CSRF_TOKEN),
            db,
            legal_name="Empresa Actualizada S.A.",
            email="NUEVO@Example.COM",
        )
        assert isinstance(second_response, RedirectResponse)
        assert second_response.status_code == 303

        db.refresh(company)
        assert company.legal_name == "Empresa Actualizada S.A."
        assert company.email == "nuevo@example.com"
        assert db.scalar(select(func.count(Company.id))) == 1


def test_invalid_company_data_and_csrf_do_not_persist() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        user = _user("administrador", is_superuser=True)
        db.add(user)
        db.commit()

        response = _save(
            _request(user_id=user.id, csrf_token=CSRF_TOKEN),
            db,
            tax_id="30-71234567-2",
            email="correo-invalido",
            csrf_token_value="csrf-invalido",
        )

        assert response.status_code == 422
        assert db.get(Company, 1) is None
