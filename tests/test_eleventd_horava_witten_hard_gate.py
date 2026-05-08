# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 11D Rung 6 hard-gate evidence: src/eleventd/horava_witten_hard_gate.py."""

from __future__ import annotations

from src.eleventd.horava_witten_hard_gate import (
    ANCHOR,
    DIM_E8,
    DIM_E8XE8,
    DIMENSION,
    EPISTEMIC_STATUS,
    HARD_GATE_CHECKS,
    KILL_SWITCH_PASS,
    MECHANISM,
    N_BOUNDARIES_S1Z2,
    N_SUPERCHARGES_11D,
    N_SUPERCHARGES_4D,
    RUNG_ID,
    STATUS,
    TARGET_PARAMETER,
    axiomzero_seed_purity_check,
    e8xe8_dimension_check,
    evaluate_candidate,
    hard_gate_check,
    kill_switch_check,
    rung6_gate_evidence,
    s1z2_boundary_count_check,
    scaffold_spec,
    sugra_supercharge_check,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

def test_constants():
    assert RUNG_ID == "R6"
    assert DIMENSION == "11D"
    assert "Horava_Witten" in ANCHOR
    assert "S1_Z2" in MECHANISM
    assert TARGET_PARAMETER == "M_theory_unification_bridge"


def test_supercharge_constants():
    assert N_SUPERCHARGES_11D == 32
    assert N_SUPERCHARGES_4D == 4
    assert N_SUPERCHARGES_11D // 8 == N_SUPERCHARGES_4D


def test_e8_dimension_constants():
    assert DIM_E8 == 248
    assert DIM_E8XE8 == 496
    assert DIM_E8 * 2 == DIM_E8XE8


def test_s1z2_boundary_constant():
    assert N_BOUNDARIES_S1Z2 == 2


def test_hard_gate_checks_tuple():
    assert len(HARD_GATE_CHECKS) == 4
    assert "sugra_supercharge_check" in HARD_GATE_CHECKS
    assert "e8xe8_dimension_check" in HARD_GATE_CHECKS
    assert "s1z2_boundary_count_check" in HARD_GATE_CHECKS
    assert "axiomzero_seed_purity_check" in HARD_GATE_CHECKS


# ---------------------------------------------------------------------------
# Gate 1: SUGRA supercharge reduction
# ---------------------------------------------------------------------------

def test_sugra_supercharge_gate_default_pass():
    r = sugra_supercharge_check()
    assert r["pass"] is True
    assert r["n_supercharges_4d_derived"] == 4
    assert r["n_supercharges_4d_expected"] == 4


def test_sugra_supercharge_gate_wrong_count():
    r = sugra_supercharge_check(n_supercharges_11d=16)
    assert r["pass"] is False


def test_sugra_supercharge_gate_wrong_cy3_factor():
    r = sugra_supercharge_check(cy3_reduction_factor=2)
    assert r["pass"] is False


def test_sugra_supercharge_evidence_string():
    r = sugra_supercharge_check()
    assert "CY₃" in r["evidence"] or "CY3" in r["evidence"] or "cy3" in r["evidence"].lower()
    assert "N=1" in r["evidence"] or "4" in r["evidence"]


# ---------------------------------------------------------------------------
# Gate 2: E₈×E₈ dimension
# ---------------------------------------------------------------------------

def test_e8xe8_dimension_gate_default_pass():
    r = e8xe8_dimension_check()
    assert r["pass"] is True
    assert r["dim_e8xe8_derived"] == 496
    assert r["dim_e8xe8_target"] == 496


def test_e8xe8_dimension_gate_wrong_dim_e8():
    r = e8xe8_dimension_check(dim_e8=240)
    assert r["pass"] is False


def test_e8xe8_dimension_gate_wrong_n_boundaries():
    r = e8xe8_dimension_check(n_boundaries=1)
    assert r["pass"] is False


def test_e8xe8_dimension_evidence_string():
    r = e8xe8_dimension_check()
    assert "496" in r["evidence"]
    assert "E₈" in r["evidence"] or "E8" in r["evidence"]


# ---------------------------------------------------------------------------
# Gate 3: S¹/Z₂ boundary count
# ---------------------------------------------------------------------------

def test_s1z2_boundary_count_gate_default_pass():
    r = s1z2_boundary_count_check()
    assert r["pass"] is True
    assert r["n_boundaries"] == 2


def test_s1z2_boundary_count_gate_wrong_count():
    r = s1z2_boundary_count_check(n_boundaries=1)
    assert r["pass"] is False


def test_s1z2_boundary_count_gate_excess():
    r = s1z2_boundary_count_check(n_boundaries=3)
    assert r["pass"] is False


def test_s1z2_boundary_evidence_string():
    r = s1z2_boundary_count_check()
    assert "UV" in r["evidence"] or "brane" in r["evidence"]


# ---------------------------------------------------------------------------
# Gate 4: AxiomZero seed purity
# ---------------------------------------------------------------------------

def test_axiomzero_seed_purity_gate_passes():
    r = axiomzero_seed_purity_check()
    assert r["pass"] is True


def test_axiomzero_seed_purity_allowed_contains_e8():
    r = axiomzero_seed_purity_check()
    assert any("E8" in s or "E₈" in s or "lie" in s.lower() for s in r["allowed_inputs"])


def test_axiomzero_seed_purity_forbidden_contains_pdg():
    r = axiomzero_seed_purity_check()
    assert any("pdg" in s.lower() for s in r["forbidden_inputs"])


# ---------------------------------------------------------------------------
# kill_switch_check and module-level status
# ---------------------------------------------------------------------------

def test_kill_switch_all_pass():
    ks = kill_switch_check()
    assert ks["all_pass"] is True
    assert ks["gate_count"] == 4
    assert ks["rung_id"] == "R6"
    assert ks["dimension"] == "11D"


def test_kill_switch_check_names():
    ks = kill_switch_check()
    names = [c["check"] for c in ks["checks"]]
    assert names == list(HARD_GATE_CHECKS)


def test_module_level_status():
    assert KILL_SWITCH_PASS is True
    assert STATUS == "RUNG_SOLID"
    assert "HARD_GATE_EVIDENCE_ATTACHED" in EPISTEMIC_STATUS


# ---------------------------------------------------------------------------
# hard_gate_check
# ---------------------------------------------------------------------------

def test_hard_gate_check_passes():
    hg = hard_gate_check()
    assert hg["all_required_checks_present"] is True
    assert hg["kill_switch_pass"] is True
    assert hg["hard_gate_pass"] is True
    assert hg["promotion_policy"] == "blocked_without_hard_gate_evidence"
    assert hg["rung_id"] == "R6"


# ---------------------------------------------------------------------------
# rung6_gate_evidence
# ---------------------------------------------------------------------------

def test_rung6_gate_evidence_shape():
    ev = rung6_gate_evidence()
    assert ev["kill_switch_pass"] is True
    assert ev["hard_gate_pass"] is True
    assert ev["gate_count"] == 4
    assert ev["status"] == "RUNG_SOLID"
    assert ev["promotion_policy"] == "blocked_without_hard_gate_evidence"
    assert ev["n_supercharges_4d"] == 4
    assert ev["dim_e8xe8"] == 496
    assert ev["n_boundaries_s1z2"] == 2
    assert ev["test_file"] == "tests/test_eleventd_horava_witten_hard_gate.py"


def test_rung6_gate_evidence_required_checks_present():
    ev = rung6_gate_evidence()
    assert set(ev["required_checks"]) == set(HARD_GATE_CHECKS)


# ---------------------------------------------------------------------------
# scaffold_spec
# ---------------------------------------------------------------------------

def test_scaffold_spec_marked_implemented():
    spec = scaffold_spec()
    assert spec["now_implemented"] is True
    assert spec["hard_gate_evidence_required"] is True
    assert spec["status"] == "RUNG_SOLID"
    assert spec["dimension"] == "11D"


# ---------------------------------------------------------------------------
# evaluate_candidate
# ---------------------------------------------------------------------------

def test_evaluate_candidate_pass():
    good = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "supercharge_pass": True,
        "e8xe8_dim_pass": True,
        "boundary_count_pass": True,
    }
    result = evaluate_candidate(good)
    assert result["gate_pass"] is True
    assert result["status_if_pass"] == "RUNG_SOLID"


def test_evaluate_candidate_fail_on_missing_supercharge():
    evidence = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "supercharge_pass": False,
        "e8xe8_dim_pass": True,
        "boundary_count_pass": True,
    }
    assert evaluate_candidate(evidence)["gate_pass"] is False


def test_evaluate_candidate_fail_on_missing_e8():
    evidence = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "supercharge_pass": True,
        "e8xe8_dim_pass": False,
        "boundary_count_pass": True,
    }
    assert evaluate_candidate(evidence)["gate_pass"] is False


def test_evaluate_candidate_fail_on_missing_boundary():
    evidence = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "supercharge_pass": True,
        "e8xe8_dim_pass": True,
        "boundary_count_pass": False,
    }
    assert evaluate_candidate(evidence)["gate_pass"] is False


def test_evaluate_candidate_internal_evidence_present():
    good = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "supercharge_pass": True,
        "e8xe8_dim_pass": True,
        "boundary_count_pass": True,
    }
    result = evaluate_candidate(good)
    assert "internal_evidence" in result
    assert result["internal_evidence"]["status"] == "RUNG_SOLID"
