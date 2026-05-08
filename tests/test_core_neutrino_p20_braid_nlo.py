# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/neutrino_p20_braid_nlo.py."""
from __future__ import annotations

from src.core.neutrino_p20_braid_nlo import (
    N_W,
    N2,
    N_C,
    K_CS,
    PDG_SIN2_THETA13,
    ROBUSTNESS_DRIFT,
    GP_THRESHOLD_PCT,
    SIN2_THETA13_LO,
    SIN2_THETA13_NLO,
    RESIDUAL_LO_PCT,
    RESIDUAL_NLO_PCT,
    ROBUSTNESS_WORST_PCT,
    P20_STATUS,
    TOE_DELTA,
    p20_braid_nlo_prediction,
    p20_hardgate_certificate,
)


def test_geometric_constants():
    assert N_W == 5
    assert N2 == 7
    assert N_C == 3
    assert K_CS == 74
    assert N_W ** 2 + N2 ** 2 == K_CS


def test_lo_formula():
    expected = 3 / 144
    assert abs(SIN2_THETA13_LO - expected) < 1e-12


def test_nlo_formula():
    expected = 3 / 138
    assert abs(SIN2_THETA13_NLO - expected) < 1e-12
    # NLO should be closer to PDG than LO
    assert RESIDUAL_NLO_PCT < RESIDUAL_LO_PCT


def test_nlo_residual_within_5pct():
    assert RESIDUAL_NLO_PCT < GP_THRESHOLD_PCT, (
        f"P20 NLO residual {RESIDUAL_NLO_PCT:.3f}% exceeds 5% gate"
    )


def test_robustness_within_5pct():
    assert ROBUSTNESS_WORST_PCT < GP_THRESHOLD_PCT, (
        f"P20 robustness worst-case {ROBUSTNESS_WORST_PCT:.3f}% exceeds 5% gate"
    )


def test_robustness_exact_values():
    drift = ROBUSTNESS_DRIFT
    pred = SIN2_THETA13_NLO
    pdg = PDG_SIN2_THETA13
    minus_case = abs(pred - drift - pdg) / pdg * 100.0
    plus_case = abs(pred + drift - pdg) / pdg * 100.0
    assert minus_case < GP_THRESHOLD_PCT, f"pred−drift residual {minus_case:.3f}% >= 5%"
    assert plus_case < GP_THRESHOLD_PCT, f"pred+drift residual {plus_case:.3f}% >= 5%"


def test_p20_promotes_to_geometric_prediction():
    assert P20_STATUS == "GEOMETRIC_PREDICTION"


def test_toe_delta():
    assert abs(TOE_DELTA - 0.3) < 1e-12


def test_axiomzero_purity():
    # No PDG values used in derivation
    pred = p20_braid_nlo_prediction()
    assert pred["pdg_anchors_used"] == []
    assert "N_c" in pred["axiomzero_inputs"][0] or pred["n_c"] == 3


def test_prediction_structure():
    pred = p20_braid_nlo_prediction()
    assert pred["sin2_theta13_nlo"] == SIN2_THETA13_NLO
    assert pred["sin2_theta13_lo"] == SIN2_THETA13_LO
    assert pred["sin2_theta13_pdg"] == PDG_SIN2_THETA13
    assert pred["color_loop_correction"] == -6


def test_certificate_structure():
    cert = p20_hardgate_certificate()
    assert cert["parameter"] == "P20"
    assert cert["new_status"] == "GEOMETRIC_PREDICTION"
    assert cert["all_gates_pass"] is True
    assert cert["gates"]["nominal_residual_lt_5pct"] is True
    assert cert["gates"]["robustness_window_lt_5pct"] is True
    assert cert["gates"]["axiomzero_purity"] is True
    assert abs(cert["toe_delta"] - 0.3) < 1e-12


def test_nlo_is_improvement_over_lo():
    # The NLO formula should be closer to PDG than LO
    assert SIN2_THETA13_NLO > SIN2_THETA13_LO
    assert RESIDUAL_NLO_PCT < RESIDUAL_LO_PCT
