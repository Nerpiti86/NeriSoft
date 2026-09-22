from __future__ import annotations

import os
import secrets
from dataclasses import dataclass, field
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _load_or_create_session_secret() -> str:
    env_secret = os.getenv("NERISOFT_SESSION_SECRET")
    if env_secret:
        if len(env_secret) < 32:
            raise ValueError("NERISOFT_SESSION_SECRET debe tener al menos 32 caracteres.")
        return env_secret

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    secret_path = DATA_DIR / "session.secret"

    if secret_path.exists():
        stored_secret = secret_path.read_text(encoding="utf-8").strip()
        if len(stored_secret) >= 32:
            return stored_secret

    new_secret = secrets.token_urlsafe(48)
    secret_path.write_text(new_secret, encoding="utf-8")
    try:
        os.chmod(secret_path, 0o600)
    except OSError:
        pass
    return new_secret


@dataclass(frozen=True, slots=True)
class Settings:
    app_name: str = "NERISOFT"
    app_version: str = "0.1.0"
    host: str = os.getenv("NERISOFT_HOST", "0.0.0.0")
    port: int = int(os.getenv("NERISOFT_PORT", "8000"))
    reload: bool = _env_bool("NERISOFT_RELOAD", False)
    database_url: str = os.getenv(
        "NERISOFT_DATABASE_URL",
        f"sqlite:///{(DATA_DIR / 'nerisoft.db').as_posix()}",
    )
    session_secret: str = field(default_factory=_load_or_create_session_secret)
    session_https_only: bool = _env_bool("NERISOFT_SESSION_HTTPS_ONLY", False)
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    templates_dir: Path = TEMPLATES_DIR
    static_dir: Path = STATIC_DIR


settings = Settings()
