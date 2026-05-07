# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 8D Rung 3: src/eightd/wilson_line_gauge.py"""

from __future__ import annotations

import math

import pytest

from src.eightd.wilson_line_gauge import (
    ANCHOR,
    DIMENSION,
    EPISTEMIC_STATUS,
    KILL_SWITCH_PASS,
    RUNG_ID,
    STATUS,
    TARGET_RANK,
    UNBROKEN_GROUP,
    WILSON_LINE_PHASES_RAD,
    axiomzero_seed_purity_check,
    evaluate_candidate,
    kill_switch_check,
    rank_conservation_check,
    rung3_gate_evidence,
    scaffold_spec,
    unbroken_group_validation_check,
    wilson_line_quantization_check,
)


def test_constants():
    assert RUNG_ID == "R3"
    assert DIMENSION == "8D"
    assert TARGET_RANK == 4
    assert ANCHOR


def test_wilson_line_default_phases_are_quantized():
    r = wilson_line_quantization_check()
    assert r["pass"] is True
    assert r["spacing_rad"] == pytest.approx(2.0 * math.pi / 3.0)


def test_rank_check_passes_for_rank_four():
    r = rank_conservation_check(vacuum_rank=4, target_rank=4)
    assert r["pass"] is True


def test_rank_check_fails_for_mismatch():
    r = rank_conservation_check(vacuum_rank=3, target_rank=4)
    assert r["pass"] is False


def test_group_validation_passes_for_sm_group():
    r = unbroken_group_validation_check(group_factors=UNBROKEN_GROUP)
    assert r["pass"] is True
    assert r["rank"] == 4


def test_group_validation_fails_for_wrong_group():
    r = unbroken_group_validation_check(group_factors=("SU(4)", "U(1)"))
    assert r["pass"] is False


def test_axiomzero_seed_purity_check():
    r = axiomzero_seed_purity_check()
    assert r["pass"] is True


def test_kill_switch_passes_and_status_promoted():
    ks = kill_switch_check()
    assert ks["all_pass"] is True
    assert KILL_SWITCH_PASS is True
    assert STATUS == "RUNG_SOLID"


def test_epistemic_status_updated_from_scaffold_label():
    assert "GEOMETRIC_DERIVATION_ATTEMPT" in EPISTEMIC_STATUS


def test_gate_evidence_has_test_file():
    ev = rung3_gate_evidence()
    assert ev["kill_switch_pass"] is True
    assert ev["test_file"] == "tests/test_eightd_wilson_line_gauge.py"


def test_scaffold_spec_now_implemented_true():
    spec = scaffold_spec()
    assert spec["now_implemented"] is True


def test_evaluate_candidate_pass_and_fail_paths():
    good = {
        "traceability_pass": True,
        "reproducibility_pass": True,
        "tests_pass": True,
        "epistemic_integrity_pass": True,
        "axiomzero_pass": True,
        "rank_check_pass": True,
        "group_structure_pass": True,
        "quantization_pass": True,
    }
    bad = {**good, "quantization_pass": False}
    assert evaluate_candidate(good)["gate_pass"] is True
    assert evaluate_candidate(bad)["gate_pass"] is False


def test_quantization_raises_for_invalid_denominator():
    with pytest.raises(ValueError):
        wilson_line_quantization_check(WILSON_LINE_PHASES_RAD, denominator=0)
