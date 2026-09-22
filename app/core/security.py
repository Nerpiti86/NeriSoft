from __future__ import annotations

from pwdlib import PasswordHash


password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """Return a secure password hash. Plaintext passwords must never be persisted."""
    if not password:
        raise ValueError("La contraseña no puede estar vacía.")
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against its stored hash."""
    if not password or not password_hash:
        return False
    return password_hasher.verify(password, password_hash)
