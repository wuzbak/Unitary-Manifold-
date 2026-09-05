# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import json

import src.core.pillar1059_sprint_cc_status_coherence_certificate as p1059

from src.core.pillar1059_sprint_cc_status_coherence_certificate import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    REQUIRED_SPRINT_MARKERS,
    STATUS_SURFACES,
    pillar1059_summary,
    status_surface_audit,
    sprint_cc_status_coherence_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1059
    assert PILLAR_GATE == "SPRINT_CC_STATUS_COHERENCE_CERTIFICATE"
    assert PILLAR_STATUS == "SPRINT_CC_STATUS_COHERENCE_CERTIFICATE_COMPLETE"
    assert isinstance(PILLAR_VALID, bool)


def test_surface_registry() -> None:
    assert len(STATUS_SURFACES) == 8
    assert REQUIRED_SPRINT_MARKERS == ["v35.9", "1058-1059", "1060"]


def test_certificate_shape() -> None:
    report = sprint_cc_status_coherence_certificate()
    assert report["surface_audit"]["all_exist"] is True
    assert "open_labels_pass" in report["surface_audit"]
    assert "sprint_markers_pass" in report["surface_audit"]
    assert "tests_ok" in report["live_status_audit"]
    assert "version_ok" in report["live_status_audit"]
    assert "next_slot_ok" in report["live_status_audit"]
    assert "pillar1058" in report["dependency_chain"]


def test_summary() -> None:
    summary = pillar1059_summary()
    assert summary["status"] == PILLAR_STATUS


def test_marker_drift_detected_when_surface_loses_required_marker(
    monkeypatch, tmp_path
) -> None:
    original_path = STATUS_SURFACES["status"]
    text = original_path.read_text(encoding="utf-8").replace("v35.9", "v35x")
    drifted = tmp_path / "status_drifted.md"
    drifted.write_text(text, encoding="utf-8")
    monkeypatch.setitem(STATUS_SURFACES, "status", drifted)

    audit = status_surface_audit()
    assert audit["sprint_markers_pass"] is False


def test_live_status_missing_file_fails_closed(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(p1059, "LIVE_STATUS_PATH", tmp_path / "missing.json")
    audit = p1059._live_status_audit()
    assert audit["exists"] is False
    assert audit["parse_ok"] is False
    assert audit["version_ok"] is False


def test_live_status_invalid_json_fails_closed(monkeypatch, tmp_path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{not-json", encoding="utf-8")
    monkeypatch.setattr(p1059, "LIVE_STATUS_PATH", bad)
    audit = p1059._live_status_audit()
    assert audit["exists"] is True
    assert audit["parse_ok"] is False
    assert audit["next_slot_ok"] is False


def test_live_status_slot_mismatch_fails(monkeypatch, tmp_path) -> None:
    expected = p1059._expected_slot_targets()
    payload = {
        "meta": {"version": "35.9"},
        "pillars": {
            "next_slot": expected["next_slot"] + 1,
            "total_slots": expected["total_slots"],
        },
        "lean4": {"theorem_count": 4000},
        "tests": {"passed": 63764},
    }
    path = tmp_path / "live.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(p1059, "LIVE_STATUS_PATH", path)
    audit = p1059._live_status_audit()
    assert audit["parse_ok"] is True
    assert audit["version_ok"] is True
    assert audit["next_slot_ok"] is False
