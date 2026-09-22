from datetime import datetime, timezone

from app.core.formatting import format_datetime_ar


def test_format_datetime_ar_converts_naive_sqlite_utc_to_argentina() -> None:
    value = datetime(2026, 9, 22, 15, 30)
    assert format_datetime_ar(value) == "22/09/2026 12:30"


def test_format_datetime_ar_accepts_aware_datetime() -> None:
    value = datetime(2026, 9, 22, 15, 30, tzinfo=timezone.utc)
    assert format_datetime_ar(value) == "22/09/2026 12:30"


def test_format_datetime_ar_handles_none() -> None:
    assert format_datetime_ar(None) == "—"
