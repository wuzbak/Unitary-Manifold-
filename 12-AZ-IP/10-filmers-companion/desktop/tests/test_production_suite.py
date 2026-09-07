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


def test_import_script_fountain_and_export_round_trip(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "fountain.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    fountain = (
        "Title: UPGRADE TEST\n"
        "Author: AXIOMZERO\n\n"
        "INT. LAB - DAY\n"
        "NOVA\n"
        "We are going full integration.\n\n"
        "EXT. STREET - NIGHT\n"
        "MIRA\n"
        "No partial steps."
    )
    summary = service.import_script_fountain(
        project_id="fountain-001",
        title="Fountain Upgrade",
        content=fountain,
        replace_existing=True,
    )
    exported = service.export_script_fountain("fountain-001")
    assert summary["import_format"] == "fountain"
    assert summary["scene_count"] == 2
    assert "INT. LAB - DAY" in exported["content"]
    assert "EXT. STREET - NIGHT" in exported["content"]


def test_import_script_fountain_strips_lowercase_title_page_fields(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "fountain_titlecase.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    summary = service.import_script_fountain(
        project_id="fountain-002",
        title="Lower Title",
        content="title: lower\nauthor: az\n\nINT. ROOM - DAY\nNOVA\nLine.",
        replace_existing=True,
    )
    exported = service.export_script_fountain("fountain-002")
    assert summary["scene_count"] == 1
    assert "title: lower" not in exported["content"].lower()


def test_import_script_fdx_and_export_fdx(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "fdx.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    fdx = """<?xml version="1.0" encoding="UTF-8"?>
<FinalDraft DocumentType="Script"><Content>
<Paragraph Type="Scene Heading"><Text>INT. HUB - DAY</Text></Paragraph>
<Paragraph Type="Character"><Text>NOVA</Text></Paragraph>
<Paragraph Type="Dialogue"><Text>We launch now.</Text></Paragraph>
<Paragraph Type="Scene Heading"><Text>EXT. LOT - NIGHT</Text></Paragraph>
<Paragraph Type="Character"><Text>MIRA</Text></Paragraph>
<Paragraph Type="Dialogue"><Text>Confirmed.</Text></Paragraph>
</Content></FinalDraft>"""
    summary = service.import_script_fdx(
        project_id="fdx-001",
        title="FDX Upgrade",
        content=fdx,
        replace_existing=True,
    )
    exported = service.export_script_fdx("fdx-001")
    assert summary["import_format"] == "fdx"
    assert summary["scene_count"] == 2
    assert "<FinalDraft" in exported["content"]
    assert "Scene Heading" in exported["content"]


def test_import_script_fdx_namespaced_xml(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "fdx_ns.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    fdx = """<?xml version="1.0" encoding="UTF-8"?>
<fd:FinalDraft xmlns:fd="urn:finaldraft" DocumentType="Script"><fd:Content>
<fd:Paragraph Type="Scene Heading"><fd:Text>INT. STAGE - DAY</fd:Text></fd:Paragraph>
<fd:Paragraph Type="Character"><fd:Text>NOVA</fd:Text></fd:Paragraph>
<fd:Paragraph Type="Dialogue"><fd:Text>Namespace-safe import.</fd:Text></fd:Paragraph>
</fd:Content></fd:FinalDraft>"""
    summary = service.import_script_fdx(
        project_id="fdx-ns-001",
        title="FDX Namespace",
        content=fdx,
        replace_existing=True,
    )
    diagnostics = service.script_diagnostics("fdx-ns-001")
    assert summary["scene_count"] == 1
    assert diagnostics["dialogue_character_count"] >= 1


def test_script_revision_diagnostics_and_reports(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "revision.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    service.import_script_text(
        project_id="rev-001",
        title="Revision Test",
        content=(
            "INT. OFFICE - DAY\n"
            "NOVA\n"
            "The baseline is stable.\n\n"
            "EXT. ROOF - NIGHT\n"
            "MIRA\n"
            "Proceed with the upgrade."
        ),
        replace_existing=True,
    )
    revision = service.create_script_revision(
        project_id="rev-001",
        revision_name="Blue Draft",
        revision_color="Blue",
        change_summary="Integrated fountain/fdx workflow.",
        content=(
            "INT. OFFICE - DAY\n"
            "NOVA\n"
            "The baseline is stable and verified.\n\n"
            "EXT. ROOF - NIGHT\n"
            "MIRA\n"
            "Proceed with the upgrade now."
        ),
    )
    diagnostics = service.script_diagnostics("rev-001")
    reports = service.screenplay_reports("rev-001")
    plan = service.merlin_screenwriting_master_plan("rev-001")
    assert revision["status"] == "created"
    assert diagnostics["scene_count"] == 2
    assert diagnostics["dialogue_character_count"] >= 2
    assert reports["script_report"]["total_scenes"] == 2
    assert any(str(row["character"]).lower() == "nova" for row in reports["character_report"])
    assert plan["service_capabilities"]["fdx_import"] is True
    assert plan["service_capabilities"]["fountain_export"] is True


def test_import_script_fdx_invalid_xml_raises_clear_error(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "fdx_invalid.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    with pytest.raises(ValueError, match="Invalid FDX payload"):
        service.import_script_fdx(
            project_id="fdx-invalid",
            title="Invalid FDX",
            content="<FinalDraft><Content><Paragraph>",
            replace_existing=True,
        )


def test_master_plan_marks_project_not_ready_without_script(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "empty_plan.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    plan = service.merlin_screenwriting_master_plan("empty-project")
    assert plan["project_state"]["has_script"] is False
    assert plan["project_state"]["ready_for_upgrade_workflow"] is False


def test_revision_rebuild_preserves_enriched_character_records(tmp_path):
    from desktop.app.db.schema import get_conn, init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "character_preserve.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    service.import_script_text(
        project_id="char-001",
        title="Character Preserve",
        content="INT. LAB - DAY\nNOVA\nInitial line.",
        replace_existing=True,
    )
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO characters (id, project_id, name, performer, notes) VALUES (?, ?, ?, ?, ?)",
            ("manual-1", "char-001", "Astra Mentor", "Performer X", "Custom cast assignment"),
        )
    service.create_script_revision(
        project_id="char-001",
        revision_name="Blue Draft",
        revision_color="Blue",
        change_summary="Shift scene cast.",
        content="INT. LAB - DAY\nMIRA\nRevised line.",
    )
    reports = service.screenplay_reports("char-001")
    names = {str(row["character"]).lower() for row in reports["character_report"]}
    with get_conn(db_path) as conn:
        manual = conn.execute(
            "SELECT performer, notes FROM characters WHERE project_id=? AND name=?",
            ("char-001", "Astra Mentor"),
        ).fetchone()
    assert "mira" in names
    assert manual is not None
    assert manual["performer"] == "Performer X"


def test_revision_rebuild_normalizes_character_case_identity(tmp_path):
    from desktop.app.db.schema import get_conn, init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "character_case.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    service.import_script_text(
        project_id="case-001",
        title="Case Identity",
        content="INT. LAB - DAY\nNOVA\nLine one.",
        replace_existing=True,
    )
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO characters (id, project_id, name, performer, notes) VALUES (?, ?, ?, ?, ?)",
            ("auto-dup", "case-001", "NOVA", "", "Detected from screenplay import"),
        )
    service.create_script_revision(
        project_id="case-001",
        revision_name="Blue Draft",
        revision_color="Blue",
        change_summary="Case variant import.",
        content="INT. LAB - DAY\nNOVA\nLine two.",
    )
    with get_conn(db_path) as conn:
        rows = conn.execute("SELECT name FROM characters WHERE project_id=?", ("case-001",)).fetchall()
    assert len([row["name"] for row in rows if row["name"].lower() == "nova"]) == 1


def test_export_fdx_preserves_parenthetical_type(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "parenthetical.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    service.import_script_text(
        project_id="paren-001",
        title="Parenthetical",
        content="INT. STUDIO - NIGHT\nNOVA\n(whispering)\nWe move at dawn.",
        replace_existing=True,
    )
    exported = service.export_script_fdx("paren-001")
    assert 'Type="Parenthetical"' in exported["content"]


def test_dialogue_stats_exclude_parenthetical_lines(tmp_path):
    from desktop.app.db.schema import init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "paren_stats.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    service.import_script_text(
        project_id="paren-stats-001",
        title="Parenthetical Stats",
        content="INT. STUDIO - NIGHT\nNOVA\n(whispering)\nWe move at dawn.",
        replace_existing=True,
    )
    reports = service.screenplay_reports("paren-stats-001")
    nova = next(row for row in reports["character_report"] if str(row["character"]).lower() == "nova")
    assert nova["dialogue_lines"] == 1
    assert nova["dialogue_words"] == 4


def test_revision_with_no_character_cues_clears_auto_characters(tmp_path):
    from desktop.app.db.schema import get_conn, init_db
    from desktop.app.production_suite.service import FilmProductionSuiteService

    db_path = tmp_path / "clear_chars.db"
    init_db(db_path)
    service = FilmProductionSuiteService(db_path)
    service.import_script_text(
        project_id="clear-001",
        title="Clear Auto Characters",
        content="INT. BASE - DAY\nNOVA\nInitial line.",
        replace_existing=True,
    )
    service.create_script_revision(
        project_id="clear-001",
        revision_name="No Dialogue Cues",
        revision_color="Blue",
        change_summary="Remove character cues.",
        content="INT. BASE - DAY\nAction only line.",
    )
    with get_conn(db_path) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM characters WHERE project_id='clear-001' AND notes='Detected from screenplay import'"
        ).fetchone()[0]
    assert count == 0
