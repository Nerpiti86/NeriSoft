from __future__ import annotations

import re


WHITESPACE_RE = re.compile(r"\s+")


def normalized_role_values(name: str, description: str) -> dict[str, str]:
    normalized_name = WHITESPACE_RE.sub(" ", name.strip())
    normalized_description = WHITESPACE_RE.sub(" ", description.strip())
    return {
        "name": normalized_name,
        "name_key": normalized_name.casefold(),
        "description": normalized_description,
    }


def validate_role_values(values: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    name = values.get("name", "")
    description = values.get("description", "")

    if len(name) < 2:
        errors["name"] = "El nombre del rol debe tener al menos 2 caracteres."
    elif len(name) > 80:
        errors["name"] = "El nombre del rol no puede superar los 80 caracteres."

    if len(description) > 255:
        errors["description"] = "La descripción no puede superar los 255 caracteres."

    return errors
