from app.core.security import hash_password, verify_password


def test_password_hash_roundtrip() -> None:
    password = "una-clave-segura-2026"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash)
    assert not verify_password("otra-clave", password_hash)
