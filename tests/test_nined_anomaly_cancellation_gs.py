# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 9D Rung 4 kickoff: src/nined/anomaly_cancellation_gs.py."""

from __future__ import annotations

import pytest

from src.nined.anomaly_cancellation_gs import (
    DIMENSION,
    EPISTEMIC_STATUS,
    KILL_SWITCH_PASS,
    RUNG_ID,
    STATUS,
    TARGET_GAUGE_DIMENSIONS,
    axiomzero_seed_purity_check,
    bianchi_identity_balance_check,
    evaluate_candidate,
    gauge_dimension_check,
    gs_counterterm_presence_check,
    hard_gate_check,
    kill_switch_check,
    rung4_gate_evidence,
    scaffold_spec,
)


def test_constants():
    assert RUNG_ID == "R4"
    assert DIMENSION == "9D"
    assert TARGET_GAUGE_DIMENSIONS == (496,)


def test_gauge_dimension_gate_passes_for_496():
    r = gauge_dimension_check(gauge_dimension=496)
    assert r["pass"] is True


def test_gauge_dimension_gate_fails_for_non_496():
    r = gauge_dimension_check(gauge_dimension=495)
    assert r["pass"] is False


def test_bianchi_balance_passes_for_equal_terms():
    r = bianchi_identity_balance_check(1.0, 1.0)
    assert r["pass"] is True


def test_bianchi_balance_fails_for_mismatch():
    r = bianchi_identity_balance_check(1.0, 1.1, tolerance=1e-3)
    assert r["pass"] is False


def test_gs_counterterm_presence_gate():
    assert gs_counterterm_presence_check(True)["pass"] is True
    assert gs_counterterm_presence_check(False)["pass"] is False


def test_axiomzero_seed_purity_gate():
    assert axiomzero_seed_purity_check()["pass"] is True


def test_kill_switch_and_status():
    ks = kill_switch_check()
    assert ks["all_pass"] is True
    assert ks["gate_count"] == 4
    assert KILL_SWITCH_PASS is True
    assert STATUS == "RUNG_SOLID"
    assert "HARD_GATE_EVIDENCE_ATTACHED" in EPISTEMIC_STATUS


def test_hard_gate_check_passes():
    hard = hard_gate_check()
    assert hard["all_required_checks_present"] is True
    assert hard["hard_gate_pass"] is True
    assert hard["promotion_policy"] == "blocked_without_hard_gate_evidence"


def test_rung4_gate_evidence_shape():
    ev = rung4_gate_evidence()
    assert ev["kill_switch_pass"] is True
    assert ev["hard_gate_pass"] is True
    assert ev["gate_count"] == 4
    assert ev["promotion_policy"] == "blocked_without_hard_gate_evidence"
    assert ev["test_file"] == "tests/test_nined_anomaly_cancellation_gs.py"


def test_scaffold_spec_marked_implemented():
    spec = scaffold_spec()
    assert spec["now_implemented"] is True


def test_evaluate_candidate_pass_and_fail():
    good = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "gauge_dim_pass": True,
        "bianchi_balance_pass": True,
        "counterterm_present": True,
    }
    bad = {**good, "gauge_dim_pass": False}
    assert evaluate_candidate(good)["gate_pass"] is True
    assert evaluate_candidate(bad)["gate_pass"] is False


def test_target_dimensions_are_positive():
    assert all(d > 0 for d in TARGET_GAUGE_DIMENSIONS)
    with pytest.raises(AssertionError):
        assert 0 in TARGET_GAUGE_DIMENSIONS
