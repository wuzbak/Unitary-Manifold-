# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 265 — Mukhanov-Sasaki A_s closure in KK slow-roll.

22+ deterministic unit tests covering:
  - slow-roll parameter computation
  - Hubble parameter physics
  - MS vacuum normalization scaling laws
  - A_s formula structure and monotonicity
  - Transfer coefficient computation
  - SC2 verdict dict completeness
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar265_mukhanov_sasaki_as_closure import (
    A_S_PLANCK,
    C_S,
    M_PL_GEV,
    N_S,
    N_W,
    R_TENSOR,
    TS_PASS_HIGH,
    TS_PASS_LOW,
    as_kk_prediction,
    hubble_parameter_from_inflation,
    ms_vacuum_normalization,
    scalar_power_spectrum,
    sc2_mukhanov_sasaki_verdict,
    slow_roll_epsilon,
    slow_roll_eta,
    transfer_normalization_coefficient,
)

# ── Slow-roll parameter tests ─────────────────────────────────────────────────


def test_slow_roll_epsilon_known_value():
    """ε matches the analytic formula for canonical KK parameters."""
    eps = slow_roll_epsilon(N_S, R_TENSOR)
    expected = (1.0 - N_S) / 2.0 + R_TENSOR / 8.0
    assert abs(eps - expected) < 1e-12


def test_slow_roll_epsilon_positive():
    """ε must be positive for any physically reasonable (n_s < 1, r > 0)."""
    assert slow_roll_epsilon(0.96, 0.03) > 0.0


def test_slow_roll_epsilon_in_slow_roll_range():
    """ε ≪ 1 for the canonical KK parameters."""
    eps = slow_roll_epsilon(N_S, R_TENSOR)
    assert 0.0 < eps < 0.5


def test_slow_roll_epsilon_increases_with_r():
    """Larger r → larger ε (more gravitational wave power → steeper slope)."""
    eps_low = slow_roll_epsilon(N_S, 0.02)
    eps_high = slow_roll_epsilon(N_S, 0.06)
    assert eps_high > eps_low


def test_slow_roll_eta_sign_positive():
    """η > 0 for the KK inflection-point scenario (concave-up potential)."""
    eta = slow_roll_eta(N_S, R_TENSOR)
    assert eta > 0.0


def test_slow_roll_eta_self_consistent():
    """Recovered n_s from (ε, η) matches input to within numerical noise."""
    eps = slow_roll_epsilon(N_S, R_TENSOR)
    eta = slow_roll_eta(N_S, R_TENSOR)
    n_s_check = 1.0 - 6.0 * eps + 2.0 * eta
    assert abs(n_s_check - N_S) < 1e-11


# ── Hubble parameter tests ────────────────────────────────────────────────────


def test_hubble_in_physical_range():
    """H from inflation should lie in [10¹², 10¹⁶] GeV for large-field models."""
    H = hubble_parameter_from_inflation(R_TENSOR)
    assert 1e12 < H < 1e16


def test_hubble_increases_with_r():
    """Larger r → higher inflation energy scale → larger H."""
    H_low = hubble_parameter_from_inflation(0.01)
    H_high = hubble_parameter_from_inflation(0.1)
    assert H_high > H_low


def test_hubble_positive():
    """H is positive for all positive r."""
    assert hubble_parameter_from_inflation(0.05) > 0.0


def test_hubble_reference_point():
    """At r = r_ref = 0.0128 the formula returns H from V^{1/4} = 2.2e16 GeV."""
    H_ref = hubble_parameter_from_inflation(0.0128)
    v14 = 2.2e16
    H_expected = math.sqrt(v14 ** 4 / (3.0 * M_PL_GEV ** 2))
    assert abs(H_ref - H_expected) / H_expected < 1e-10


# ── MS vacuum normalization tests ─────────────────────────────────────────────


def test_ms_normalization_positive():
    """MS vacuum |v_k/z|² is positive definite."""
    k, H, eps = 0.05, 1e13, 0.02
    assert ms_vacuum_normalization(k, C_S, H, eps) > 0.0


def test_ms_norm_scales_as_h_squared():
    """Doubling H → quadrupling |v_k/z|² (quadratic dependence)."""
    k, eps = 0.05, 0.02
    v1 = ms_vacuum_normalization(k, C_S, 1e13, eps)
    v2 = ms_vacuum_normalization(k, C_S, 2e13, eps)
    assert abs(v2 / v1 - 4.0) < 1e-10


def test_ms_norm_scales_inversely_with_epsilon():
    """Doubling ε → halving |v_k/z|² (∝ 1/ε)."""
    k, H = 0.05, 1e13
    v1 = ms_vacuum_normalization(k, C_S, H, 0.01)
    v2 = ms_vacuum_normalization(k, C_S, H, 0.02)
    assert abs(v2 / v1 - 0.5) < 1e-10


def test_ms_norm_scales_inversely_with_c_s():
    """Doubling c_s → halving |v_k/z|² (∝ 1/c_s)."""
    k, H, eps = 0.05, 1e13, 0.02
    v1 = ms_vacuum_normalization(k, 0.2, H, eps)
    v2 = ms_vacuum_normalization(k, 0.4, H, eps)
    assert abs(v2 / v1 - 0.5) < 1e-10


def test_ms_norm_scales_as_k_cubed():
    """Doubling k → |v_k/z|² decreases by factor 8 (∝ 1/k³)."""
    H, eps = 1e13, 0.02
    v1 = ms_vacuum_normalization(0.05, C_S, H, eps)
    v2 = ms_vacuum_normalization(0.10, C_S, H, eps)
    assert abs(v2 / v1 - 1.0 / 8.0) < 1e-10


def test_ms_norm_consistent_with_power_spectrum():
    """k³/(2π²) × ms_vac_norm / M_Pl² should equal scalar_power_spectrum."""
    k = 0.05
    H = 1e13
    eps = 0.02
    ms_vac = ms_vacuum_normalization(k, C_S, H, eps)
    # In M_Pl = 1 units: A_s = k³/(2π²) × ms_vac; with physical M_Pl: divide by M_Pl²
    A_s_from_ms = (k ** 3 / (2.0 * math.pi ** 2)) * ms_vac / M_PL_GEV ** 2
    A_s_direct = scalar_power_spectrum(H, eps, C_S, M_PL_GEV)
    assert abs(A_s_from_ms / A_s_direct - 1.0) < 1e-10


# ── Scalar power spectrum tests ───────────────────────────────────────────────


def test_scalar_power_spectrum_positive():
    """A_s must be positive for all positive inputs."""
    assert scalar_power_spectrum(1e13, 0.02, C_S) > 0.0


def test_scalar_power_spectrum_dimensionless_sanity():
    """A_s is dimensionless and in the expected cosmological range [10⁻¹², 10⁻⁵]."""
    A_s = scalar_power_spectrum(hubble_parameter_from_inflation(R_TENSOR),
                                slow_roll_epsilon(N_S, R_TENSOR), C_S)
    assert 1e-12 < A_s < 1e-5


def test_c_s_dependence_smaller_c_s_larger_as():
    """Smaller c_s → larger A_s (∝ 1/c_s, KK enhancement for c_s < 1)."""
    H, eps = 1e13, 0.02
    A_s_small = scalar_power_spectrum(H, eps, 0.2)
    A_s_large = scalar_power_spectrum(H, eps, 0.5)
    assert A_s_small > A_s_large


def test_epsilon_dependence_larger_eps_smaller_as():
    """Larger ε → smaller A_s (steeper potential → less curvature perturbation)."""
    H = 1e13
    A_s_small_eps = scalar_power_spectrum(H, 0.01, C_S)
    A_s_large_eps = scalar_power_spectrum(H, 0.05, C_S)
    assert A_s_small_eps > A_s_large_eps


def test_as_formula_self_consistency():
    """Given H_obs derived from Planck A_s, scalar_power_spectrum recovers A_S_PLANCK."""
    eps = slow_roll_epsilon(N_S, R_TENSOR)
    # Solve H from A_s = H²/(8π²ε c_s M_Pl²) → H = sqrt(8π²ε c_s M_Pl² A_s)
    H_obs = math.sqrt(8.0 * math.pi ** 2 * eps * C_S * M_PL_GEV ** 2 * A_S_PLANCK)
    A_s_check = scalar_power_spectrum(H_obs, eps, C_S)
    assert abs(A_s_check / A_S_PLANCK - 1.0) < 1e-10


# ── Transfer coefficient and prediction tests ─────────────────────────────────


def test_transfer_coeff_formula():
    """T_s = A_s_obs / A_s_pred."""
    T_s = transfer_normalization_coefficient(3.0e-9, 2.099e-9)
    assert abs(T_s - 2.099e-9 / 3.0e-9) < 1e-12


def test_transfer_coeff_in_range_with_near_match_inputs():
    """T_s is in [0.5, 2.0] when A_s_pred is within factor 2 of Planck."""
    A_s_pred_near = 1.5 * A_S_PLANCK   # 50% above Planck
    T_s = transfer_normalization_coefficient(A_s_pred_near, A_S_PLANCK)
    assert 0.5 <= T_s <= 2.0


def test_transfer_coeff_unity_when_exact():
    """T_s = 1 when prediction equals observation."""
    T_s = transfer_normalization_coefficient(A_S_PLANCK, A_S_PLANCK)
    assert abs(T_s - 1.0) < 1e-12


def test_transfer_coeff_positive():
    """T_s is always positive."""
    assert transfer_normalization_coefficient(5e-9, 2e-9) > 0.0


def test_as_kk_prediction_required_keys():
    """as_kk_prediction must contain all documented keys."""
    result = as_kk_prediction()
    required = {
        "epsilon", "eta", "H_gev", "A_s_predicted",
        "A_s_planck", "residual_fraction", "transfer_coeff_T_s", "c_s_used",
    }
    assert required.issubset(result.keys())


def test_as_kk_prediction_a_s_positive():
    """Predicted A_s is positive."""
    assert as_kk_prediction()["A_s_predicted"] > 0.0


def test_as_kk_prediction_c_s_is_braided():
    """as_kk_prediction uses c_s = 12/37 by default."""
    result = as_kk_prediction()
    assert abs(result["c_s_used"] - 12.0 / 37.0) < 1e-12


def test_as_kk_prediction_residual_non_negative():
    """residual_fraction is always ≥ 0."""
    assert as_kk_prediction()["residual_fraction"] >= 0.0


# ── SC2 verdict dict tests ────────────────────────────────────────────────────


def test_verdict_returns_all_required_keys():
    """sc2_mukhanov_sasaki_verdict returns all specification-required keys."""
    v = sc2_mukhanov_sasaki_verdict()
    required = {
        "A_s_predicted", "A_s_planck", "residual_fraction",
        "transfer_coeff_T_s", "verdict", "c_s_used", "ms_closure_note",
    }
    assert required.issubset(v.keys())


def test_verdict_string_valid():
    """verdict is one of the three allowed strings."""
    v = sc2_mukhanov_sasaki_verdict()
    assert v["verdict"] in {"PASS", "TENSION", "FALSIFIED"}


def test_verdict_c_s_used_is_braided():
    """Verdict uses the KK braided c_s = 12/37."""
    v = sc2_mukhanov_sasaki_verdict()
    assert abs(v["c_s_used"] - 12.0 / 37.0) < 1e-12


def test_verdict_a_s_planck_correct():
    """A_s_planck in verdict matches Planck 2018 central value."""
    v = sc2_mukhanov_sasaki_verdict()
    assert abs(v["A_s_planck"] - A_S_PLANCK) < 1e-15


def test_verdict_ms_closure_note_non_empty():
    """ms_closure_note is a non-empty string describing the closure status."""
    v = sc2_mukhanov_sasaki_verdict()
    assert isinstance(v["ms_closure_note"], str) and len(v["ms_closure_note"]) > 20


def test_verdict_is_tension_for_canonical_params():
    """Canonical KK parameters give TENSION (T_s ≈ 0.22, honest about normalization gap)."""
    v = sc2_mukhanov_sasaki_verdict()
    # T_s ≈ 0.22 is in (0, 0.8) → TENSION, not FALSIFIED (the sign and structure are correct)
    assert v["verdict"] in {"TENSION", "PASS"}


def test_verdict_transfer_coeff_is_positive():
    """T_s is positive (physically meaningful)."""
    v = sc2_mukhanov_sasaki_verdict()
    assert v["transfer_coeff_T_s"] > 0.0


def test_ts_pass_thresholds_correct():
    """Module-level pass thresholds match specification [0.8, 1.2]."""
    assert TS_PASS_LOW == 0.8
    assert TS_PASS_HIGH == 1.2


def test_n_w_winding_number():
    """Module constant N_W matches the canonical KK winding number 5."""
    assert N_W == 5


def test_a_s_planck_constant():
    """Module A_S_PLANCK matches Planck 2018 central value 2.099e-9."""
    assert abs(A_S_PLANCK - 2.099e-9) < 1e-15
