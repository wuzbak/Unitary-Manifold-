# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 281 — DESI DR3 Routing Drill."""
from __future__ import annotations

import pytest

from src.core.pillar281_desi_dr3_routing_drill import (
    ADJACENCY_TRACK_LABEL,
    DRILL_SIGMA_LEVELS,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    desi_dr3_drill_report,
    expected_verdict_for_sigma,
    idempotence_check,
    run_all_drills,
    run_single_drill,
    separation_guard,
    synthetic_dr3_inputs_for_sigma,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 281
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    g = separation_guard()
    assert g["drives_existing_runbook_only"] is True


def test_drill_sigma_levels_match_plan():
    assert DRILL_SIGMA_LEVELS == (3.2, 2.4, 1.8)


def test_synthetic_inputs_recover_target_sigma():
    for sigma in (1.5, 2.4, 3.0, 4.0):
        wa, sw = synthetic_dr3_inputs_for_sigma(sigma)
        # |wa − 0| / sw = sigma
        assert abs(abs(wa) / sw - sigma) < 1e-9


def test_synthetic_inputs_validation():
    with pytest.raises(ValueError):
        synthetic_dr3_inputs_for_sigma(-1.0)
    with pytest.raises(ValueError):
        synthetic_dr3_inputs_for_sigma(1.0, sigma_wa=0.0)


def test_expected_verdict_buckets():
    assert expected_verdict_for_sigma(3.2) == "FALSIFIED"
    assert expected_verdict_for_sigma(3.0) == "FALSIFIED"
    assert expected_verdict_for_sigma(2.5) == "HIGH_TENSION"
    assert expected_verdict_for_sigma(2.4) == "TENSION"
    assert expected_verdict_for_sigma(2.0) == "TENSION"
    assert expected_verdict_for_sigma(1.8) == "CONSISTENT"


def test_run_single_drill_3_2_falsified():
    r = run_single_drill(3.2)
    assert r["checklist_verdict"] == "FALSIFIED"
    assert r["verdict_matches_expected"] is True
    assert r["coverage_audit_pass"] is True
    assert r["same_day_sync_required"] is True
    assert r["deadline_hours"] <= 24


def test_run_single_drill_2_4_tension():
    r = run_single_drill(2.4)
    assert r["checklist_verdict"] == "TENSION"
    assert r["verdict_matches_expected"] is True


def test_run_single_drill_1_8_consistent():
    r = run_single_drill(1.8)
    assert r["checklist_verdict"] == "CONSISTENT"
    assert r["verdict_matches_expected"] is True
    # Consistent bucket is *not* same-day urgent
    assert r["same_day_sync_required"] is False


def test_run_all_drills_count():
    drills = run_all_drills()
    assert len(drills) == 3
    assert [d["target_sigma"] for d in drills] == list(DRILL_SIGMA_LEVELS)


def test_idempotence_per_sigma():
    for s in DRILL_SIGMA_LEVELS:
        i = idempotence_check(s)
        assert i["fully_idempotent"] is True
        assert i["idempotent_verdict"] is True
        assert i["idempotent_coverage"] is True
        assert i["idempotent_deadline"] is True


def test_drill_report_acceptance_and_receipts():
    r = desi_dr3_drill_report()
    assert r["acceptance_gate_passed"] is True
    assert r["all_drills_pass"] is True
    assert r["all_drills_idempotent"] is True
    receipts = r["receipts"]
    assert len(receipts) == 3
    for rec in receipts:
        assert rec["green_check"] is True


def test_drill_report_verdict_ordering():
    r = desi_dr3_drill_report()
    verdicts = [d["checklist_verdict"] for d in r["drills"]]
    assert verdicts == ["FALSIFIED", "TENSION", "CONSISTENT"]


def test_no_hardgate_drift():
    r = desi_dr3_drill_report()
    g = r["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
