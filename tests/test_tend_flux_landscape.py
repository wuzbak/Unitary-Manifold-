# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 10D Rung 5 scaffold: src/tend/flux_landscape.py."""

from __future__ import annotations

import pytest

from src.tend.flux_landscape import (
    ARCHITECTURE_LIMIT,
    DIMENSION,
    EPISTEMIC_STATUS,
    KILL_SWITCH_PASS,
    K_CS,
    LAMBDA_OBS,
    N_FLUX,
    RUNG_ID,
    STATUS,
    architecture_limit_alignment_check,
    axiomzero_seed_purity_check,
    discrete_vacua_count,
    evaluate_candidate,
    flux_count_consistency_check,
    kill_switch_check,
    landscape_resolution_check,
    rung5_gate_evidence,
    scaffold_spec,
)


def test_constants():
    assert RUNG_ID == "R5"
    assert DIMENSION == "10D"
    assert K_CS == 74
    assert N_FLUX == 37


def test_discrete_vacua_count_uses_flux_scaling():
    r = discrete_vacua_count()
    assert r["vacua_order_of_magnitude"] == 74
    assert r["vacua_count_estimate"] == 10**74


def test_discrete_vacua_count_raises_for_invalid_flux():
    with pytest.raises(ValueError):
        discrete_vacua_count(0)


def test_flux_count_consistency_gate():
    assert flux_count_consistency_check()["pass"] is True
    assert flux_count_consistency_check(k_cs=74, n_flux=36)["pass"] is False


def test_landscape_resolution_gate():
    r = landscape_resolution_check()
    assert r["pass"] is True
    assert r["spacing_log10_per_flux_pair"] < 0.0


def test_landscape_resolution_raises_for_invalid_inputs():
    with pytest.raises(ValueError):
        landscape_resolution_check(n_flux=0)
    with pytest.raises(ValueError):
        landscape_resolution_check(lambda_obs=0.0)


def test_architecture_limit_alignment_gate():
    assert architecture_limit_alignment_check(True)["pass"] is True
    assert architecture_limit_alignment_check(False)["pass"] is False


def test_axiomzero_seed_purity_gate():
    assert axiomzero_seed_purity_check()["pass"] is True


def test_kill_switch_and_status():
    ks = kill_switch_check()
    assert ks["all_pass"] is True
    assert KILL_SWITCH_PASS is True
    assert STATUS == "SCAFFOLD_IMPLEMENTED"
    assert ARCHITECTURE_LIMIT is True
    assert "ARCHITECTURE_LIMIT_SCAFFOLD" in EPISTEMIC_STATUS


def test_rung5_gate_evidence_shape():
    ev = rung5_gate_evidence()
    assert ev["kill_switch_pass"] is True
    assert ev["architecture_limit"] is True
    assert ev["test_file"] == "tests/test_tend_flux_landscape.py"


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
        "flux_count_pass": True,
        "resolution_pass": True,
        "architecture_limit_pass": True,
    }
    bad = {**good, "resolution_pass": False}
    assert evaluate_candidate(good)["gate_pass"] is True
    assert evaluate_candidate(bad)["gate_pass"] is False


def test_lambda_constant_positive():
    assert LAMBDA_OBS > 0.0

