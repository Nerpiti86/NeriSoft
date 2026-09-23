from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session

from app.core.permissions import ALL_PERMISSION_CODES
from app.models import Permission


def test_migrated_database_matches_permission_catalog(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    database_path = tmp_path / "migrated.db"
    database_url = f"sqlite:///{database_path.as_posix()}"

    env = os.environ.copy()
    env["NERISOFT_DATABASE_URL"] = database_url
    env["NERISOFT_SESSION_SECRET"] = "test-session-secret-for-migrations"

    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=project_root,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    engine = create_engine(database_url)
    inspector = inspect(engine)

    assert "companies" in inspector.get_table_names()

    with Session(engine) as db:
        migrated_codes = frozenset(db.scalars(select(Permission.code)).all())

    assert migrated_codes == ALL_PERMISSION_CODES
