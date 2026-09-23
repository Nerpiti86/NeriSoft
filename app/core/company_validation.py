from __future__ import annotations

import re


EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
CUIT_SEPARATORS_RE = re.compile(r"[\s-]+")

TAX_CONDITIONS = (
    "IVA RESPONSABLE INSCRITO",
    "IVA EXENTO",
    "NO RESPONSABLE IVA",
    "RESPONSABLE MONOTRIBUTO",
    "MONOTRIBUTO TRABAJADOR INDEPENDIENTE PROMOVIDO",
    "MONOTRIBUTISTA SOCIAL",
)


def _clean_text(value: str) -> str:
    return " ".join(value.strip().split())


def normalize_tax_id(value: str) -> str:
    return CUIT_SEPARATORS_RE.sub("", value.strip())


def normalized_company_values(
    legal_name: str,
    trade_name: str,
    tax_id: str,
    tax_condition: str,
    fiscal_address: str,
    city: str,
    province: str,
    postal_code: str,
    phone: str,
    email: str,
) -> dict[str, str]:
    return {
        "legal_name": _clean_text(legal_name),
        "trade_name": _clean_text(trade_name),
        "tax_id": normalize_tax_id(tax_id),
        "tax_condition": _clean_text(tax_condition).upper(),
        "fiscal_address": _clean_text(fiscal_address),
        "city": _clean_text(city),
        "province": _clean_text(province),
        "postal_code": _clean_text(postal_code),
        "phone": _clean_text(phone),
        "email": email.strip().lower(),
    }


def cuit_is_valid(value: str) -> bool:
    if len(value) != 11 or not value.isdigit():
        return False

    weights = (5, 4, 3, 2, 7, 6, 5, 4, 3, 2)
    total = sum(int(digit) * weight for digit, weight in zip(value[:10], weights))
    verifier = 11 - (total % 11)
    if verifier == 11:
        verifier = 0
    elif verifier == 10:
        verifier = 9
    return verifier == int(value[-1])


def validate_company_values(values: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}

    if not values["legal_name"] or len(values["legal_name"]) > 160:
        errors["legal_name"] = "Ingresá la razón social (máximo 160 caracteres)."

    if len(values["trade_name"]) > 160:
        errors["trade_name"] = "El nombre comercial no puede superar los 160 caracteres."

    if not cuit_is_valid(values["tax_id"]):
        errors["tax_id"] = "Ingresá un CUIT válido de 11 dígitos."

    if values["tax_condition"] not in TAX_CONDITIONS:
        errors["tax_condition"] = "Seleccioná una condición fiscal válida."

    if not values["fiscal_address"] or len(values["fiscal_address"]) > 255:
        errors["fiscal_address"] = "Ingresá el domicilio fiscal (máximo 255 caracteres)."

    if not values["city"] or len(values["city"]) > 120:
        errors["city"] = "Ingresá la localidad (máximo 120 caracteres)."

    if not values["province"] or len(values["province"]) > 120:
        errors["province"] = "Ingresá la provincia (máximo 120 caracteres)."

    if len(values["postal_code"]) > 20:
        errors["postal_code"] = "El código postal no puede superar los 20 caracteres."

    if len(values["phone"]) > 50:
        errors["phone"] = "El teléfono no puede superar los 50 caracteres."

    email = values["email"]
    if len(email) > 254 or (email and not EMAIL_RE.fullmatch(email)):
        errors["email"] = "Ingresá un correo electrónico válido."

    return errors
