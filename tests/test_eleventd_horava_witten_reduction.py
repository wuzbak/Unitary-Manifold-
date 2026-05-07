# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 11D Rung 6 kickoff: src/eleventd/horava_witten_reduction.py."""

from __future__ import annotations

from src.eleventd.horava_witten_reduction import (
    ANCHOR,
    BOUNDARY_ASSUMPTIONS,
    DIMENSION,
    EPISTEMIC_STATUS,
    FALSIFIER_CRITERIA,
    KILL_SWITCH_PASS,
    MECHANISM,
    RUNG_ID,
    STATUS,
    axiomzero_seed_purity_check,
    boundary_brane_structure_check,
    evaluate_candidate,
    kill_switch_check,
    orbifold_interval_check,
    rs1_reduction_consistency_check,
    rung6_kickoff_evidence,
    scaffold_spec,
)


def test_constants():
    assert RUNG_ID == "R6"
    assert DIMENSION == "11D"
    assert "Horava_Witten" in ANCHOR
    assert "S1_Z2" in MECHANISM


def test_boundary_brane_structure_gate():
    assert boundary_brane_structure_check()["pass"] is True
    assert boundary_brane_structure_check(uv_position=1.0, ir_position=0.0)["pass"] is False
    assert boundary_brane_structure_check(uv_has_e8=False)["pass"] is False


def test_orbifold_interval_gate():
    assert orbifold_interval_check()["pass"] is True
    assert orbifold_interval_check(is_s1_z2_interval=False)["pass"] is False


def test_rs1_reduction_consistency_gate():
    assert rs1_reduction_consistency_check(action_mismatch_fraction=0.15, tolerance=0.2)["pass"] is True
    assert rs1_reduction_consistency_check(action_mismatch_fraction=0.25, tolerance=0.2)["pass"] is False


def test_axiomzero_seed_purity_gate():
    assert axiomzero_seed_purity_check()["pass"] is True


def test_kill_switch_and_status():
    ks = kill_switch_check()
    assert ks["all_pass"] is True
    assert ks["gate_count"] == 4
    assert KILL_SWITCH_PASS is True
    assert STATUS == "KICKOFF_IMPLEMENTED"
    assert "ARCHITECTURE_KICKOFF" in EPISTEMIC_STATUS


def test_boundary_assumptions_and_falsifiers_present():
    assert len(BOUNDARY_ASSUMPTIONS) >= 3
    assert set(FALSIFIER_CRITERIA) == {"boundary_mismatch", "reduction_failure", "seed_impurity"}


def test_rung6_kickoff_evidence_shape():
    ev = rung6_kickoff_evidence()
    assert ev["kill_switch_pass"] is True
    assert ev["promotion_policy"] == "blocked_without_hard_gate_evidence"
    assert len(ev["boundary_assumptions"]) >= 3
    assert "boundary_mismatch" in ev["falsifier_criteria"]


def test_scaffold_spec_marked_implemented():
    spec = scaffold_spec()
    assert spec["now_implemented"] is True
    assert spec["boundary_assumptions_recorded"] is True
    assert spec["falsifier_criteria_recorded"] is True


def test_evaluate_candidate_pass_and_fail():
    good = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "boundary_structure_pass": True,
        "orbifold_interval_pass": True,
        "reduction_consistency_pass": True,
    }
    bad = {**good, "boundary_structure_pass": False}
    assert evaluate_candidate(good)["gate_pass"] is True
    assert evaluate_candidate(bad)["gate_pass"] is False
