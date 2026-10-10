"""Tests for the post-pipeline interchange bridge (EDL / OTIO / CSV / Resolve)."""
from __future__ import annotations

import uuid

import pytest

from desktop.app.config import get_config
from desktop.app.db.schema import get_conn, init_db
from desktop.app.post_pipeline.service import PostPipelineBridge


@pytest.fixture
def db_path():
    cfg = get_config()
    init_db(cfg.db_path)
    return cfg.db_path


@pytest.fixture
def seeded_project(db_path):
    project_id = "proj-post-1"
    scene_id = str(uuid.uuid4())
    with get_conn(db_path) as conn:
        conn.execute(
            "INSERT INTO projects (id, title) VALUES (?, ?)", (project_id, "THE TEST REEL")
        )
        conn.execute(
            """INSERT INTO scenes (id, project_id, scene_number, int_ext, day_night, synopsis)
               VALUES (?, ?, ?, 'INT', 'DAY', 'Test scene')""",
            (scene_id, project_id, "1"),
        )
        for shot_number, coverage in enumerate(["WIDE", "CLOSE"], start=1):
            conn.execute(
                """INSERT INTO shot_lists (id, scene_id, shot_number, coverage_type, lens, movement)
                   VALUES (?, ?, ?, ?, '35mm', 'static')""",
                (str(uuid.uuid4()), scene_id, shot_number, coverage),
            )
    return project_id


def test_connect_resolve_offline_fallback():
    bridge = PostPipelineBridge(get_config().db_path)
    status = bridge.connect_resolve()
    assert status["connected"] is False
    assert status["mode"] == "offline"


def test_export_edl_contains_clips(db_path, seeded_project):
    bridge = PostPipelineBridge(db_path)
    edl = bridge.export_edl(seeded_project)
    assert "TITLE: THE TEST REEL" in edl
    assert "SC1_SH001" in edl
    assert "SC1_SH002" in edl


def test_export_edl_uses_storyboard_panel_durations(db_path, seeded_project):
    with get_conn(db_path) as conn:
        scene = conn.execute(
            "SELECT id FROM scenes WHERE project_id=?", (seeded_project,)
        ).fetchone()
        for panel_number, duration in enumerate([10.0, 2.0], start=1):
            conn.execute(
                """INSERT INTO storyboard_panels
                   (id, project_id, scene_id, panel_number, duration_sec)
                   VALUES (?, ?, ?, ?, ?)""",
                (str(uuid.uuid4()), seeded_project, scene["id"], panel_number, duration),
            )
    bridge = PostPipelineBridge(db_path)
    edl = bridge.export_edl(seeded_project)
    # 10s clip -> src_out at frame 240 (24fps); 2s clip rec_in starts at 00:00:10:00.
    assert "00:00:10:00" in edl
    assert "00:00:12:00" in edl


def test_export_shotlist_csv(db_path, seeded_project):
    bridge = PostPipelineBridge(db_path)
    csv_text = bridge.export_shotlist_csv(seeded_project)
    assert "scene_number,shot_number,coverage_type" in csv_text
    assert "WIDE" in csv_text and "CLOSE" in csv_text


def test_export_otio_json(db_path, seeded_project):
    bridge = PostPipelineBridge(db_path)
    timeline = bridge.export_otio_json(seeded_project)
    assert timeline["OTIO_SCHEMA"] == "Timeline.1"
    clips = timeline["tracks"]["children"][0]["children"]
    assert len(clips) == 2


def test_export_otio_json_uses_storyboard_panel_durations(db_path, seeded_project):
    with get_conn(db_path) as conn:
        scene = conn.execute(
            "SELECT id FROM scenes WHERE project_id=?", (seeded_project,)
        ).fetchone()
        conn.execute(
            """INSERT INTO storyboard_panels
               (id, project_id, scene_id, panel_number, duration_sec)
               VALUES (?, ?, ?, 1, 8.0)""",
            (str(uuid.uuid4()), seeded_project, scene["id"]),
        )
    bridge = PostPipelineBridge(db_path)
    timeline = bridge.export_otio_json(seeded_project)
    clips = timeline["tracks"]["children"][0]["children"]
    assert clips[0]["source_range"]["duration"]["value"] == 8.0 * 24
    # Second shot falls back to the default 5s clip since no panel covers it.
    assert clips[1]["source_range"]["duration"]["value"] == 5.0 * 24


def test_list_exports_records_history(db_path, seeded_project):
    bridge = PostPipelineBridge(db_path)
    bridge.export_edl(seeded_project)
    bridge.export_shotlist_csv(seeded_project)
    exports = bridge.list_exports(seeded_project)
    formats = {e["export_format"] for e in exports}
    assert formats == {"EDL", "CSV"}
