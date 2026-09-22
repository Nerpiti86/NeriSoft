from __future__ import annotations

import os
from dataclasses import dataclass
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
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    templates_dir: Path = TEMPLATES_DIR
    static_dir: Path = STATIC_DIR


settings = Settings()
