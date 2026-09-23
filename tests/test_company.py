import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import Base
from app.models import Company


def _company(**overrides) -> Company:
    values = {
        "legal_name": "Empresa de Prueba S.A.",
        "trade_name": "Empresa Prueba",
        "tax_id": "30712345678",
        "tax_condition": "Responsable Inscripto",
        "fiscal_address": "Calle 123",
        "city": "Rosario",
        "province": "Santa Fe",
        "postal_code": "2000",
        "phone": "",
        "email": "",
    }
    values.update(overrides)
    return Company(**values)


def test_company_model_persists_approved_minimum_fields() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        company = _company()
        db.add(company)
        db.commit()
        db.refresh(company)

        assert company.id == 1
        assert company.legal_name == "Empresa de Prueba S.A."
        assert company.trade_name == "Empresa Prueba"
        assert company.tax_id == "30712345678"
        assert company.tax_condition == "Responsable Inscripto"
        assert company.fiscal_address == "Calle 123"
        assert company.city == "Rosario"
        assert company.province == "Santa Fe"
        assert company.postal_code == "2000"
        assert company.phone == ""
        assert company.email == ""


def test_company_table_rejects_a_second_company() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        db.add(_company())
        db.commit()

        db.add(_company(legal_name="Segunda Empresa S.A.", tax_id="30787654321"))
        with pytest.raises(IntegrityError):
            db.commit()
