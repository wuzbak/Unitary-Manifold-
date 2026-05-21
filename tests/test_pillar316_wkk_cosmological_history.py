# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 316 — w_KK Cosmological History Derivation."""
import math
import pytest
from src.core.pillar316_wkk_cosmological_history import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    C_S_BRAIDED,
    M_KK_EV,
    H0_EV,
    M_KK_OVER_H0,
    W0_INFLATION_FORMULA,
    W0_FROZEN_RADION,
    W0_RESIDUAL_DEVIATION,
    w_kk_from_eos,
    w_kk_slow_roll_inflation,
    w_kk_post_inflation_frozen,
    w_kk_evolution_trajectory,
    planck_bao_tension_resolution,
    wkk_formula_validity_status,
    separation_guard,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 316


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_c_s_braided():
    assert abs(C_S_BRAIDED - 12.0 / 37.0) < 1e-12


def test_w0_inflation_formula_value():
    expected = -1.0 + (2.0 / 3.0) * (12.0 / 37.0)**2
    assert abs(W0_INFLATION_FORMULA - expected) < 1e-10


def test_w0_frozen_radion():
    assert W0_FROZEN_RADION == -1.0


def test_w0_residual_deviation_tiny():
    # |1+w₀| < (H₀/M_KK)² should be tiny
    assert W0_RESIDUAL_DEVIATION < 1e-30


def test_m_kk_over_h0_large():
    assert M_KK_OVER_H0 > 1.0e20   # ratio is astronomically large


# ── Core EoS ──────────────────────────────────────────────────────────────────

def test_w_kk_from_eos_frozen_radion():
    # phi_dot=0 → w = -V/V = -1
    w = w_kk_from_eos(phi_dot_sq=0.0, V=1.0)
    assert abs(w + 1.0) < 1e-12


def test_w_kk_from_eos_kinetic_dominated():
    # phi_dot^2/2 >> V → w → +1
    w = w_kk_from_eos(phi_dot_sq=2.0e6, V=1.0)
    assert w > 0.9


def test_w_kk_from_eos_range():
    w = w_kk_from_eos(phi_dot_sq=1.0, V=1.0)
    assert -1.0 <= w <= 1.0


def test_w_kk_from_eos_raises_negative_V():
    with pytest.raises(ValueError):
        w_kk_from_eos(phi_dot_sq=0.0, V=-1.0)


def test_w_kk_from_eos_equal_kinetic_potential():
    # phi_dot^2/2 = V → w = 0
    w = w_kk_from_eos(phi_dot_sq=2.0, V=1.0)
    assert abs(w) < 1e-10


# ── Slow-roll inflation ────────────────────────────────────────────────────────

def test_slow_roll_returns_dict():
    result = w_kk_slow_roll_inflation(epsilon_sr=0.5)
    assert isinstance(result, dict)


def test_slow_roll_w_kk_at_epsilon_half_matches_formula():
    result = w_kk_slow_roll_inflation(epsilon_sr=0.5, c_s=C_S_BRAIDED)
    # At ε=0.5, w_kk should match the formula approximately
    expected = W0_INFLATION_FORMULA
    assert abs(result["w_kk_formula"] - expected) < 1e-10


def test_slow_roll_formula_valid_at_epsilon_half():
    result = w_kk_slow_roll_inflation(epsilon_sr=0.5)
    assert result["formula_valid_at_this_epsilon"] is True


def test_slow_roll_formula_not_valid_at_epsilon_small():
    result = w_kk_slow_roll_inflation(epsilon_sr=0.01)
    assert result["formula_valid_at_this_epsilon"] is False


def test_slow_roll_w_kk_deep_slow_roll_close_to_minus1():
    # For small ε, kinetic energy is tiny → w_kk close to -1
    result = w_kk_slow_roll_inflation(epsilon_sr=0.001, c_s=C_S_BRAIDED)
    assert result["w_kk"] > -1.0
    assert result["w_kk"] < -0.99


# ── Post-inflation frozen radion ──────────────────────────────────────────────

def test_frozen_radion_returns_dict():
    result = w_kk_post_inflation_frozen(z=0.0)
    assert isinstance(result, dict)


def test_frozen_radion_z0_w_kk_close_to_minus1():
    result = w_kk_post_inflation_frozen(z=0.0)
    assert abs(result["w_kk"] + 1.0) < 1e-20


def test_frozen_radion_z_recombination_w_kk_minus1():
    result = w_kk_post_inflation_frozen(z=1100.0)
    assert abs(result["w_kk"] + 1.0) < 1e-5


def test_frozen_radion_z0_frozen_flag():
    result = w_kk_post_inflation_frozen(z=0.0)
    assert result["frozen_radion"] is True


def test_frozen_radion_regime_labels():
    z0 = w_kk_post_inflation_frozen(z=0.0)
    z_rec = w_kk_post_inflation_frozen(z=1100.0)
    assert "DARK_ENERGY" in z0["regime"]
    assert "RECOMBINATION" in z_rec["regime"]


def test_frozen_radion_deviation_from_minus1_tiny():
    result = w_kk_post_inflation_frozen(z=0.0)
    assert result["deviation_from_minus1"] < 1e-50


# ── Evolution trajectory ───────────────────────────────────────────────────────

def test_evolution_trajectory_returns_list():
    result = w_kk_evolution_trajectory()
    assert isinstance(result, list)


def test_evolution_trajectory_length():
    result = w_kk_evolution_trajectory([0.0, 1.0, 10.0])
    assert len(result) == 3


def test_evolution_trajectory_monotone_w_deviation():
    # Higher z → larger H → more kinetic → slightly larger deviation from -1
    z_low = w_kk_post_inflation_frozen(z=0.0)
    z_high = w_kk_post_inflation_frozen(z=100.0)
    assert z_high["deviation_from_minus1"] >= z_low["deviation_from_minus1"]


# ── Planck-BAO tension resolution ────────────────────────────────────────────

def test_planck_bao_tension_returns_dict():
    result = planck_bao_tension_resolution()
    assert isinstance(result, dict)


def test_planck_bao_gap_resolved():
    result = planck_bao_tension_resolution()
    assert result["gap_resolved"] is True


def test_planck_bao_new_tension_below_1p5sigma():
    result = planck_bao_tension_resolution()
    assert result["new_tension_planck_bao_sigma"] <= 1.5


def test_planck_bao_old_tension_above_2sigma():
    result = planck_bao_tension_resolution()
    assert result["old_tension_planck_bao_sigma"] > 2.0


def test_planck_bao_correct_prediction_minus1():
    result = planck_bao_tension_resolution()
    assert result["correct_prediction_w0"] == -1.0


def test_planck_bao_formula_valid_for_inflation():
    result = planck_bao_tension_resolution()
    assert "INFLATION" in result["formula_valid_for"]


def test_planck_bao_de_prediction_updated():
    result = planck_bao_tension_resolution()
    assert "w₀" in result["present_day_formula"] or "frozen radion" in result["explanation"]


# ── Formula validity status ───────────────────────────────────────────────────

def test_validity_status_returns_dict():
    status = wkk_formula_validity_status()
    assert isinstance(status, dict)


def test_validity_status_formula():
    status = wkk_formula_validity_status()
    assert "c_s" in status["formula"] or "w_KK" in status["formula"]


def test_validity_status_valid_regime():
    status = wkk_formula_validity_status()
    assert "INFLATION" in status["valid_regime"]


def test_validity_status_invalid_regime():
    status = wkk_formula_validity_status()
    assert "POST" in status["invalid_regime"]


def test_validity_status_gap_resolved():
    status = wkk_formula_validity_status()
    assert "RESOLVED" in status["gap_new_status"]


def test_validity_status_tension_resolved():
    # The tension should be significantly reduced (old was 3.3σ+, new should be ≤ 1.5σ)
    status = wkk_formula_validity_status()
    assert status["planck_bao_tension_new_sigma"] <= 1.5


def test_validity_status_de_prediction_updated():
    status = wkk_formula_validity_status()
    assert status["de_prediction_updated"] is True


def test_validity_status_label_upgrade_mentions_derived():
    status = wkk_formula_validity_status()
    assert "DERIVED" in status["label_upgrade"]


# ── Separation guard ───────────────────────────────────────────────────────────

def test_separation_guard():
    assert "SEPARATION_INTACT" in separation_guard()
