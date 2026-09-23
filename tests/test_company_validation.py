from app.core.company_validation import (
    TAX_CONDITIONS,
    cuit_is_valid,
    normalized_company_values,
    validate_company_values,
)


def _values(**overrides: str) -> dict[str, str]:
    values = normalized_company_values(
        " Empresa de Prueba S.A. ",
        " Empresa Prueba ",
        "30-71234567-1",
        "iva responsable inscripto",
        " Calle 123 ",
        " Rosario ",
        " Santa Fe ",
        " 2000 ",
        " +54 341 555-0000 ",
        " ADMIN@Example.COM ",
    )
    values.update(overrides)
    return values


def test_normalized_company_values_trim_identity_and_normalize_cuit() -> None:
    values = _values()

    assert values == {
        "legal_name": "Empresa de Prueba S.A.",
        "trade_name": "Empresa Prueba",
        "tax_id": "30712345671",
        "tax_condition": "IVA RESPONSABLE INSCRITO",
        "fiscal_address": "Calle 123",
        "city": "Rosario",
        "province": "Santa Fe",
        "postal_code": "2000",
        "phone": "+54 341 555-0000",
        "email": "admin@example.com",
    }


def test_cuit_checksum_accepts_valid_and_rejects_invalid_values() -> None:
    assert cuit_is_valid("30712345671")
    assert not cuit_is_valid("30712345672")
    assert not cuit_is_valid("30A12345671")
    assert not cuit_is_valid("3071234567")


def test_validate_company_values_accepts_approved_minimum() -> None:
    assert validate_company_values(_values()) == {}


def test_validate_company_values_rejects_required_invalid_and_unknown_fiscal_data() -> None:
    errors = validate_company_values(
        _values(
            legal_name="",
            tax_id="30712345672",
            tax_condition="CONSUMIDOR FINAL",
            fiscal_address="",
            city="",
            province="",
            email="correo-invalido",
        )
    )

    assert set(errors) == {
        "legal_name",
        "tax_id",
        "tax_condition",
        "fiscal_address",
        "city",
        "province",
        "email",
    }


def test_tax_conditions_are_limited_to_current_issuer_categories() -> None:
    assert TAX_CONDITIONS == (
        "IVA RESPONSABLE INSCRITO",
        "IVA EXENTO",
        "NO RESPONSABLE IVA",
        "RESPONSABLE MONOTRIBUTO",
        "MONOTRIBUTO TRABAJADOR INDEPENDIENTE PROMOVIDO",
        "MONOTRIBUTISTA SOCIAL",
    )
