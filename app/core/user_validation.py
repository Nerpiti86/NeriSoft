from __future__ import annotations

import re


USERNAME_RE = re.compile(r"^[a-z0-9._-]+$")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalized_user_values(name: str, username: str, email: str) -> dict[str, str]:
    return {
        "name": name.strip(),
        "username": username.strip().lower(),
        "email": email.strip().lower(),
    }


def validate_user_identity(values: dict[str, str]) -> dict[str, str]:
    errors: dict[str, str] = {}
    clean_name = values["name"]
    clean_username = values["username"]
    clean_email = values["email"]

    if len(clean_name) < 2 or len(clean_name) > 120:
        errors["name"] = "Ingresá un nombre válido de hasta 120 caracteres."

    if not 3 <= len(clean_username) <= 64 or not USERNAME_RE.fullmatch(clean_username):
        errors["username"] = "Usá entre 3 y 64 caracteres: letras, números, punto, guion o guion bajo."

    if len(clean_email) > 254 or not EMAIL_RE.fullmatch(clean_email):
        errors["email"] = "Ingresá un correo electrónico válido."

    return errors
