from __future__ import annotations

from pathlib import Path

from app.core.config import settings


REQUIRED_VENDOR_ASSETS = (
    "vendor/geist/Geist-Variable.woff2",
    "vendor/tabler/tabler-icons.min.css",
    "vendor/tabler/fonts/tabler-icons.woff2",
    "vendor/htmx/htmx.min.js",
)


def missing_vendor_assets() -> list[Path]:
    missing: list[Path] = []
    for relative_path in REQUIRED_VENDOR_ASSETS:
        path = settings.static_dir / relative_path
        if not path.is_file() or path.stat().st_size == 0:
            missing.append(path)
    return missing


def ensure_vendor_assets_ready() -> None:
    missing = missing_vendor_assets()
    if not missing:
        return

    relative = ", ".join(str(path.relative_to(settings.base_dir)) for path in missing)
    raise RuntimeError(
        "Faltan assets locales obligatorios de NERISOFT: "
        f"{relative}. Ejecutá scripts/vendor-assets.ps1 antes de iniciar la aplicación."
    )
