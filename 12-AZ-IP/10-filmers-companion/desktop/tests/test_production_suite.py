"""Tests for the unified production-suite services."""
from pathlib import Path

import pytest


@pytest.fixture
def seeded_db(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.db.seed import seed_database

    db_path = tmp_path / "suite.db"
    init_db(db_path)
    seed_database(db_path, verbose=False)
    return db_path


def test_new_schema_tables_seeded(seeded_db):
    from desktop.app.db.schema import get_conn

    expected = {
        "projects",
        "scripts",
        "script_versions",
        "characters",
        "breakdown_elements",
        "storyboard_panels",
        "schedule_days",
        "schedule_strips",
        "crew_members",
        "tasks",
        "approvals",
        "assets",
        "reviews",
        "deliverables",
    }
    with get_conn(seeded_db) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        task_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE project_id='omega-001'").fetchone()[0]
        breakdown_count = conn.execute("SELECT COUNT(*) FROM breakdown_elements WHERE project_id='omega-001'").fetchone()[0]
    assert expected.issubset(tables)
    assert task_count >= 10
    assert breakdown_count >= 10


def test_producer_dashboard_contains_cross_domain_sections(seeded_db):
    from desktop.app.production_suite.service import FilmProductionSuiteService

    dashboard = FilmProductionSuiteService(seeded_db).producer_dashboard("omega-001")
    assert dashboard["project_id"] == "omega-001"
    for key in ["summary", "schedule", "script", "finance", "locations", "departments", "post", "alerts", "upm_brief"]:
        assert key in dashboard
    assert isinstance(dashboard["departments"], list)
    assert len(dashboard["departments"]) >= 10


def test_department_board_returns_tasks_and_readiness(seeded_db):
    from desktop.app.production_suite.service import FilmProductionSuiteService

    board = FilmProductionSuiteService(seeded_db).department_board("omega-001", "VFX")
    assert board["department"] == "VFX"
    assert board["readiness"] in {"READY", "WATCH", "AT_RISK"}
    assert board["pending_approval_count"] >= 1


def test_dood_report_has_cast_rows(seeded_db):
    from desktop.app.production_suite.service import FilmProductionSuiteService

    report = FilmProductionSuiteService(seeded_db).dood_report("omega-001")
    assert len(report["date_columns"]) >= 2
    assert any(row["name"] == "NOVA" for row in report["cast_rows"])


def test_post_overview_has_reviews_and_deliverables(seeded_db):
    from desktop.app.production_suite.service import FilmProductionSuiteService

    overview = FilmProductionSuiteService(seeded_db).post_overview("omega-001")
    assert overview["asset_count"] >= 3
    assert overview["deliverable_count"] >= 3
    assert overview["review_count"] >= 2


def test_import_script_text_generates_scenes_breakdowns_and_storyboards(tmp_path):
    from desktop.app.db.schema import init_db, get_conn
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "import.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    summary = service.import_script_text(
        project_id="import-001",
        title="Import Test",
        content=(
            "INT. APARTMENT - DAY\n"
            "NOVA packs the encrypted drive while MIRA waits by the door.\n\n"
            "EXT. GARAGE - NIGHT\n"
            "A CAR explodes as NOVA dives for cover."
        ),
        replace_existing=True,
    )
    with get_conn(db_path) as conn:
        scene_count = conn.execute("SELECT COUNT(*) FROM scenes WHERE project_id='import-001'").fetchone()[0]
        breakdown_count = conn.execute("SELECT COUNT(*) FROM breakdown_elements WHERE project_id='import-001'").fetchone()[0]
        panel_count = conn.execute("SELECT COUNT(*) FROM storyboard_panels WHERE project_id='import-001'").fetchone()[0]
    assert summary["scene_count"] == 2
    assert scene_count == 2
    assert breakdown_count >= 6
    assert panel_count == 4
