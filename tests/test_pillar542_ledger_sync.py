# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 542 — v18.5 Ledger Sync Certificate."""
from __future__ import annotations

import pytest
from src.core.pillar542_ledger_sync_certificate import (
    CANONICAL_TRUTH_SURFACES,
    LEDGER_SYNC_DELTAS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    REGRESSION_SNAPSHOT,
    TOE_SCORE,
    VERSION,
    ledger_drift_certificate,
    ledger_sync_audit,
    pillar_report,
    regression_snapshot_report,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 542


def test_pillar_status():
    assert PILLAR_STATUS == "LEDGER_SYNC_CERTIFICATE_V185"


def test_version():
    assert VERSION == "v19.0"


def test_pillar_title_non_empty():
    assert len(PILLAR_TITLE) > 0


# ─── Canonical truth surfaces ────────────────────────────────────────────────

def test_canonical_truth_surfaces_count():
    # At least 5 surfaces listed
    assert len(CANONICAL_TRUTH_SURFACES) >= 5


def test_status_md_in_surfaces():
    assert "STATUS.md" in CANONICAL_TRUTH_SURFACES


def test_claim_master_board_in_surfaces():
    assert "docs/CLAIM_MASTER_BOARD.md" in CANONICAL_TRUTH_SURFACES


def test_all_surfaces_at_v185():
    for surface, ver in CANONICAL_TRUTH_SURFACES.items():
        assert ver == "v18.5", f"{surface} not at v18.5 (got {ver!r})"


# ─── Regression snapshot ─────────────────────────────────────────────────────

def test_regression_zero_failures():
    assert REGRESSION_SNAPSHOT["failed"] == 0


def test_regression_passed_count():
    assert REGRESSION_SNAPSHOT["passed"] == 47_245


def test_regression_version():
    assert REGRESSION_SNAPSHOT["version"] == "v18.5"


def test_regression_pillar_count():
    assert REGRESSION_SNAPSHOT["pillar_count_at_sync"] == 541


# ─── Ledger sync deltas ──────────────────────────────────────────────────────

def test_sync_deltas_count():
    # We have 4 documents that needed updating
    assert len(LEDGER_SYNC_DELTAS) == 4


def test_gatekeeper_summary_corrected():
    docs = {d["document"]: d for d in LEDGER_SYNC_DELTAS}
    assert "docs/GATEKEEPER_SUMMARY.md" in docs
    delta = docs["docs/GATEKEEPER_SUMMARY.md"]
    assert delta["was_at"] == "v15.8"
    assert delta["now_at"] == "v18.5"


def test_truth_layer_corrected():
    docs = {d["document"]: d for d in LEDGER_SYNC_DELTAS}
    assert "docs/TRUTH_LAYER.md" in docs
    delta = docs["docs/TRUTH_LAYER.md"]
    assert delta["was_at"] == "v15.7"
    assert delta["now_at"] == "v18.5"


def test_observation_tracker_corrected():
    docs = {d["document"]: d for d in LEDGER_SYNC_DELTAS}
    assert "3-FALSIFICATION/OBSERVATION_TRACKER.md" in docs
    delta = docs["3-FALSIFICATION/OBSERVATION_TRACKER.md"]
    assert delta["was_at"] == "v15.3"
    assert delta["now_at"] == "v18.5"


def test_claim_master_board_corrected():
    docs = {d["document"]: d for d in LEDGER_SYNC_DELTAS}
    assert "docs/CLAIM_MASTER_BOARD.md" in docs
    delta = docs["docs/CLAIM_MASTER_BOARD.md"]
    assert delta["was_at"] == "v18.4"
    assert delta["now_at"] == "v18.5"


def test_all_deltas_now_at_v185():
    for d in LEDGER_SYNC_DELTAS:
        assert d["now_at"] == "v18.5", f"{d['document']} not synced to v18.5"


# ─── ToE score ───────────────────────────────────────────────────────────────

def test_toe_score_unchanged():
    assert TOE_SCORE["score"] == "28.0/28"


def test_toe_score_percentage():
    assert TOE_SCORE["percentage"] == 100.0


def test_toe_hardgate_changes_zero():
    assert TOE_SCORE["hardgate_changes"] == 0


# ─── Functions ───────────────────────────────────────────────────────────────

def test_ledger_sync_audit_returns_dict():
    audit = ledger_sync_audit()
    assert isinstance(audit, dict)
    assert audit["status"] == "LEDGER_SYNC_CERTIFICATE_V185"
    assert audit["hardgate_score_delta"] == 0.0


def test_ledger_sync_audit_no_new_admissions():
    audit = ledger_sync_audit()
    assert audit["new_admissions"] == []
    assert audit["closed_admissions"] == []


def test_regression_snapshot_report():
    report = regression_snapshot_report()
    assert report["assertion"] is True
    assert report["regression"]["failed"] == 0


def test_ledger_drift_certificate():
    cert = ledger_drift_certificate()
    assert cert["drift_acknowledged"] is True
    assert cert["physics_impact"] == "NONE — bookkeeping only"
    assert cert["documents_corrected"] == 4


def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 542
    assert report["new_physics"] is False
    assert report["adjacent_track"] is False
    assert report["toe_score_delta"] == 0.0


def test_pillar_report_complete_fields():
    report = pillar_report()
    required = [
        "pillar", "title", "status", "version",
        "ledger_sync_audit", "regression_snapshot",
        "drift_certificate", "toe_score_delta", "hardgate_score_delta",
    ]
    for field in required:
        assert field in report, f"Missing field: {field}"
