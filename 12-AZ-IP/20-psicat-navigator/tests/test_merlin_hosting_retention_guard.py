# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for the external-hosting retention guard / tokenpot canary (ADJACENT
TRACK / GOVERNANCE).

Covers: declared-terms loading from the existing base44 intake JSON,
declared-vs-observed posture evaluation, tokenpot marker embedding and
reappearance detection, and the synthetic detection-accuracy benchmark.
See ``PSICAT_EXTERNAL_HOSTING_PROTOCOL.md`` for the governance document this
module implements.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine import merlin_hosting_retention_guard as guard


# --- flag -----------------------------------------------------------------


def test_hosting_retention_guard_flag_default_off() -> None:
    assert guard.hosting_retention_guard_enabled() is False


def test_hosting_retention_guard_flag_honors_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(guard.HOSTING_RETENTION_GUARD_FLAG, "1")
    assert guard.hosting_retention_guard_enabled() is True


# --- declared terms ---------------------------------------------------------


def test_load_declared_terms_ok() -> None:
    loaded = guard.load_declared_terms()
    assert loaded["ok"] is True
    assert "sources" in loaded["document"]


def test_load_declared_terms_missing_file_fails_gracefully() -> None:
    loaded = guard.load_declared_terms(Path("/no/such/file.json"))
    assert loaded["ok"] is False
    assert "error" in loaded


def test_declared_clauses_match_source_file_count() -> None:
    clauses = guard.declared_clauses()
    assert len(clauses) == 8
    for clause in clauses:
        assert clause["clause_id"]
        assert clause["title"]
        assert clause["tier"]


# --- evaluate_retention_posture ---------------------------------------------


def test_evaluate_retention_posture_all_unverified_by_default() -> None:
    report = guard.evaluate_retention_posture()
    assert report["ok"] is True
    assert report["governance_label"] == "GOVERNANCE"
    assert report["counts"]["unverified"] == report["declared_clause_count"]
    assert report["counts"]["flagged"] == 0
    assert all(f["triage_status"] == "incomplete" for f in report["findings"])


def test_evaluate_retention_posture_consistent_signal() -> None:
    report = guard.evaluate_retention_posture([
        {"clause_id": "declared::0", "category": "consistent", "description": "matches stated behavior"},
    ])
    match = next(f for f in report["findings"] if f["clause_id"] == "declared::0")
    assert match["posture"] == "consistent"
    assert match["triage_status"] == "accepted"


def test_evaluate_retention_posture_contradicting_signal_is_flagged_not_asserted() -> None:
    report = guard.evaluate_retention_posture([
        {"clause_id": "declared::5", "category": "contradicts", "description": "observed training despite exclusion claim"},
    ])
    match = next(f for f in report["findings"] if f["clause_id"] == "declared::5")
    assert match["posture"] == "flagged"
    # A flag is never auto-accepted; it requires human review (pending).
    assert match["triage_status"] == "pending"


# --- tokenpot marker embed / detect -----------------------------------------


def test_embed_tokenpot_marker_is_deterministic_for_same_inputs() -> None:
    text_a, marker_a = guard.embed_tokenpot_marker("session body", "session-1", timestamp=1000.0)
    text_b, marker_b = guard.embed_tokenpot_marker("session body", "session-1", timestamp=1000.0)
    assert marker_a == marker_b
    assert text_a == text_b


def test_embed_tokenpot_marker_differs_per_session() -> None:
    _, marker_a = guard.embed_tokenpot_marker("session body", "session-1", timestamp=1000.0)
    _, marker_b = guard.embed_tokenpot_marker("session body", "session-2", timestamp=1000.0)
    assert marker_a != marker_b


def test_scan_for_tokenpot_reappearance_finds_verbatim_marker() -> None:
    marked_text, marker = guard.embed_tokenpot_marker("session body", "session-1")
    hits = guard.scan_for_tokenpot_reappearance(f"leaked elsewhere:\n{marked_text}", [marker])
    assert hits == [marker]


def test_scan_for_tokenpot_reappearance_misses_stripped_marker() -> None:
    marked_text, marker = guard.embed_tokenpot_marker("session body", "session-1")
    stripped = marked_text.split("<!--")[0]
    hits = guard.scan_for_tokenpot_reappearance(stripped, [marker])
    assert hits == []


def test_scan_for_tokenpot_reappearance_does_not_cross_match_other_sessions() -> None:
    _, marker_a = guard.embed_tokenpot_marker("session body", "session-1")
    marked_text_b, marker_b = guard.embed_tokenpot_marker("session body", "session-2")
    hits = guard.scan_for_tokenpot_reappearance(marked_text_b, [marker_a])
    assert hits == []
    hits_b = guard.scan_for_tokenpot_reappearance(marked_text_b, [marker_b])
    assert hits_b == [marker_b]


# --- evaluate_detection_accuracy --------------------------------------------


def test_evaluate_detection_accuracy_shape() -> None:
    report = guard.evaluate_detection_accuracy()
    assert report["ok"] is True
    assert report["governance_label"] == "GOVERNANCE"
    assert report["scenario_count"] == len(report["rows"])
    assert 0.0 <= report["precision"] <= 1.0
    assert 0.0 <= report["recall"] <= 1.0
    assert "caveat" in report and "Synthetic" in report["caveat"]


def test_evaluate_detection_accuracy_matches_expectations_per_row() -> None:
    report = guard.evaluate_detection_accuracy()
    for row in report["rows"]:
        assert row["detected"] == row["expected_detect"], row
