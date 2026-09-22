from app.core.user_validation import normalized_user_values, validate_user_identity


def test_normalized_user_values_trim_and_lower_identity_fields() -> None:
    values = normalized_user_values("  Nicolás Nerpiti  ", " Admin.User ", " TEST@Example.COM ")
    assert values == {
        "name": "Nicolás Nerpiti",
        "username": "admin.user",
        "email": "test@example.com",
    }


def test_validate_user_identity_accepts_valid_values() -> None:
    values = normalized_user_values("Nicolás Nerpiti", "administrador", "nicolas@example.com")
    assert validate_user_identity(values) == {}


def test_validate_user_identity_rejects_invalid_username_and_email() -> None:
    values = {"name": "N", "username": "A B", "email": "correo-invalido"}
    errors = validate_user_identity(values)
    assert set(errors) == {"name", "username", "email"}
