from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo


ARGENTINA_TZ = ZoneInfo("America/Argentina/Cordoba")


def format_datetime_ar(value: datetime | None) -> str:
    if value is None:
        return "—"

    normalized = value
    if normalized.tzinfo is None:
        normalized = normalized.replace(tzinfo=timezone.utc)

    return normalized.astimezone(ARGENTINA_TZ).strftime("%d/%m/%Y %H:%M")


def current_year() -> int:
    return datetime.now(ARGENTINA_TZ).year
