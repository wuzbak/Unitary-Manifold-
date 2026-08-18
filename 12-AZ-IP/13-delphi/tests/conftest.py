"""
DelPhi — Test Fixtures (conftest.py)
"""
from __future__ import annotations

import pytest

from delphi.app.db.schema import init_db
from delphi.app.db.seed import seed_database


@pytest.fixture(scope="session")
def tmp_db(tmp_path_factory):
    """Session-scoped temporary SQLite database, fully seeded."""
    db_dir = tmp_path_factory.mktemp("delphi_db")
    db_path = str(db_dir / "test_delphi.db")
    init_db(db_path)
    seed_database(db_path)
    return db_path


@pytest.fixture(scope="session")
def today() -> str:
    from datetime import date
    return date.today().isoformat()
