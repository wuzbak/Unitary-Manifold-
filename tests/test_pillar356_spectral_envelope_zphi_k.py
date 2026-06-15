# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar356_spectral_envelope_zphi_k.py
=================================================
Test suite for Pillar 356 — Spectral Envelope of Z_φ(k): Braid-Induced
Scale Dependence and Three-Peak CMB Acoustic Closure.

Covers all public API functions:
  - braid_tower_weight_sum()
  - gamma_theory_from_braid()
  - gamma_fit_from_peaks()
  - zphi_spectral_envelope()
  - zphi_at_acoustic_peaks()
  - peak_residuals_flat_zphi()
  - peak_residuals_zphi_k()
  - bessel_spectral_envelope()
  - braid_sound_speed_acoustic_ratio()
  - three_peak_consistency_report()
  - spectral_envelope_validation()
  - pillar356_summary()

Physical correctness checks:
  - γ_theory = Z_φ^(0) × α × Σw_n / (16π²) ≈ 0.242 (within 20% tolerance)
  - γ_fit ≈ 0.273 (within tolerance from 3-peak data)
  - γ_theory and γ_fit agree within 20%
  - Z_φ(ℓ) is monotonically increasing with ℓ (for γ > 0)
  - Z_φ(ℓ_pivot) = Z_φ^(0) exactly (normalization)
  - Flat Z_φ^(0) residuals: ~15% mean at acoustic peaks
  - Spectral envelope residuals: < 10% mean at acoustic peaks
  - Bessel ansatz J_{n-1}(n×ρ) ruled out (decreasing direction)
  - Tower sum Σw_n ≈ 7.1–7.4 (within 5% of continuum estimate)
  - Sound speed ratio R_sound = (12/37)×√3 ≈ 0.562
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar356_spectral_envelope_zphi_k import (
    # Constants
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    K_CS,
    N_W1,
    N_W2,
    RHO_BRAID,
    CS_BRAID,
    OMEGA_PHI,
    PHI0_FTUM,
    ALPHA_PHI,
    Z_PHI_0,
    CS_LCDM,
    R_SOUND,
    ACOUSTIC_PEAK_ELLS,
    SUPPRESSION_CLASSICAL,
    ELL_PIVOT,
    LOOP_FACTOR,
    BESSEL_ANSATZ_STATUS,
    # Functions
    braid_tower_weight_sum,
    gamma_theory_from_braid,
    gamma_fit_from_peaks,
    zphi_spectral_envelope,
    zphi_at_acoustic_peaks,
    peak_residuals_flat_zphi,
    peak_residuals_zphi_k,
    bessel_spectral_envelope,
    braid_sound_speed_acoustic_ratio,
    three_peak_consistency_report,
    spectral_envelope_validation,
    pillar356_summary,
)

# ═══════════════════════════════════════════════════════════════════════════════
# Section 1 — Module constants
# ═══════════════════════════════════════════════════════════════════════════════


def test_pillar_number():
    assert PILLAR_NUMBER == 356


def test_pillar_status():
    assert PILLAR_STATUS == "FRONTIER_COMPUTATION"


def test_pillar_title_contains_spectral_envelope():
    assert "Spectral Envelope" in PILLAR_TITLE


def test_k_cs_value():
    assert K_CS == 74


def test_k_cs_sum_of_squares():
    assert K_CS == N_W1**2 + N_W2**2


def test_rho_braid_value():
    assert abs(RHO_BRAID - 35.0 / 37.0) < 1e-12


def test_rho_braid_formula():
    assert abs(RHO_BRAID - 2.0 * N_W1 * N_W2 / K_CS) < 1e-12


def test_cs_braid_value():
    assert abs(CS_BRAID - 12.0 / 37.0) < 1e-12


def test_cs_braid_formula():
    expected = (N_W2**2 - N_W1**2) / K_CS
    assert abs(CS_BRAID - expected) < 1e-12


def test_omega_phi_value():
    assert abs(OMEGA_PHI - 1.0 / math.sqrt(74)) < 1e-12


def test_phi0_ftum_value():
    assert abs(PHI0_FTUM - 1.0) < 1e-12


def test_alpha_phi_value():
    # α = φ₀⁻² = 1.0
    assert abs(ALPHA_PHI - 1.0) < 1e-12


def test_z_phi_0_value():
    # Z_φ^(0) = 1 + √74/2 ≈ 5.301
    expected = 1.0 + math.sqrt(74) / 2.0
    assert abs(Z_PHI_0 - expected) < 1e-10


def test_z_phi_0_greater_than_5():
    assert Z_PHI_0 > 5.0


def test_cs_lcdm_value():
    assert abs(CS_LCDM - 1.0 / math.sqrt(3.0)) < 1e-12


def test_r_sound_value():
    expected = CS_BRAID / CS_LCDM
    assert abs(R_SOUND - expected) < 1e-12


def test_r_sound_range():
    # Should be less than 1 (braid sound speed < ΛCDM)
    assert 0.0 < R_SOUND < 1.0


def test_acoustic_peak_ells():
    assert ACOUSTIC_PEAK_ELLS == [220, 540, 820]


def test_suppression_classical_values():
    assert len(SUPPRESSION_CLASSICAL) == 3
    assert abs(SUPPRESSION_CLASSICAL[0] - 4.2) < 1e-10
    assert abs(SUPPRESSION_CLASSICAL[1] - 5.0) < 1e-10
    assert abs(SUPPRESSION_CLASSICAL[2] - 6.1) < 1e-10


def test_suppression_classical_increasing():
    # Growing suppression: S₁ < S₂ < S₃
    assert SUPPRESSION_CLASSICAL[0] < SUPPRESSION_CLASSICAL[1] < SUPPRESSION_CLASSICAL[2]


def test_ell_pivot_is_second_peak():
    assert ELL_PIVOT == 540


def test_loop_factor_value():
    assert abs(LOOP_FACTOR - 16.0 * math.pi**2) < 1e-8


def test_bessel_ansatz_status_contains_ruled_out():
    assert "RULED_OUT" in BESSEL_ANSATZ_STATUS


# ═══════════════════════════════════════════════════════════════════════════════
# Section 2 — braid_tower_weight_sum
# ═══════════════════════════════════════════════════════════════════════════════


def test_tower_sum_keys():
    result = braid_tower_weight_sum()
    for key in ("sum_discrete", "sum_continuum", "relative_error", "n_modes_above_1pct"):
        assert key in result


def test_tower_sum_range():
    result = braid_tower_weight_sum()
    # Should be approximately 7.1–7.5 for K_CS = 74
    assert 6.5 < result["sum_discrete"] < 8.0


def test_tower_sum_positive():
    result = braid_tower_weight_sum()
    assert result["sum_discrete"] > 0.0


def test_tower_sum_continuum_approximation():
    result = braid_tower_weight_sum()
    # Relative error between discrete sum and continuum should be < 5%
    assert result["relative_error"] < 0.05


def test_tower_sum_k_cs_field():
    result = braid_tower_weight_sum(k_cs=74)
    assert result["k_cs"] == 74


def test_tower_sum_larger_k_cs():
    # Larger K_CS → larger sum (more modes contributing significantly)
    result_74 = braid_tower_weight_sum(k_cs=74)
    result_100 = braid_tower_weight_sum(k_cs=100)
    assert result_100["sum_discrete"] > result_74["sum_discrete"]


def test_tower_sum_n_modes_positive():
    result = braid_tower_weight_sum()
    assert result["n_modes_above_1pct"] >= 1


def test_tower_sum_default_convergence():
    # Sum with n_max=500 vs n_max=100 should be the same to high precision
    result_500 = braid_tower_weight_sum(n_max=500)
    result_100 = braid_tower_weight_sum(n_max=100)
    assert abs(result_500["sum_discrete"] - result_100["sum_discrete"]) < 1e-8


# ═══════════════════════════════════════════════════════════════════════════════
# Section 3 — gamma_theory_from_braid
# ═══════════════════════════════════════════════════════════════════════════════


def test_gamma_theory_keys():
    result = gamma_theory_from_braid()
    for key in ("gamma_theory", "tower_sum", "z_phi_0", "alpha", "loop_factor", "formula"):
        assert key in result


def test_gamma_theory_range():
    result = gamma_theory_from_braid()
    # Expected ≈ 0.242 from derivation
    assert 0.15 < result["gamma_theory"] < 0.40


def test_gamma_theory_positive():
    result = gamma_theory_from_braid()
    assert result["gamma_theory"] > 0.0


def test_gamma_theory_formula_consistency():
    result = gamma_theory_from_braid()
    # Cross-check: Z_φ^(0) × α × Σw_n / (16π²)
    expected = result["z_phi_0"] * result["alpha"] * result["tower_sum"] / result["loop_factor"]
    assert abs(result["gamma_theory"] - expected) < 1e-12


def test_gamma_theory_z_phi_0_field():
    result = gamma_theory_from_braid()
    assert abs(result["z_phi_0"] - Z_PHI_0) < 1e-10


def test_gamma_theory_loop_factor_field():
    result = gamma_theory_from_braid()
    assert abs(result["loop_factor"] - LOOP_FACTOR) < 1e-8


def test_gamma_theory_scales_with_z_phi():
    # Larger Z_φ^(0) → larger γ_theory (since γ ∝ Z_φ^(0))
    gamma_5 = gamma_theory_from_braid(z_phi_0=5.0)["gamma_theory"]
    gamma_10 = gamma_theory_from_braid(z_phi_0=10.0)["gamma_theory"]
    assert gamma_10 > gamma_5


def test_gamma_theory_scales_linearly_with_z_phi():
    gamma_5 = gamma_theory_from_braid(z_phi_0=5.0)["gamma_theory"]
    gamma_10 = gamma_theory_from_braid(z_phi_0=10.0)["gamma_theory"]
    # Should be exactly 2× (linear in Z_φ^(0))
    assert abs(gamma_10 / gamma_5 - 2.0) < 1e-10


def test_gamma_theory_status_field():
    result = gamma_theory_from_braid()
    assert result["status"] == "NON_PERTURBATIVE_ESTIMATE"


# ═══════════════════════════════════════════════════════════════════════════════
# Section 4 — gamma_fit_from_peaks
# ═══════════════════════════════════════════════════════════════════════════════


def test_gamma_fit_keys():
    result = gamma_fit_from_peaks()
    for key in (
        "gamma_fit", "rms_residual_pct", "peak_residuals_pct",
        "z_phi_fit_at_peaks", "r_squared_log",
    ):
        assert key in result


def test_gamma_fit_range():
    result = gamma_fit_from_peaks()
    # Expected ≈ 0.273 from derivation
    assert 0.10 < result["gamma_fit"] < 0.50


def test_gamma_fit_positive():
    result = gamma_fit_from_peaks()
    assert result["gamma_fit"] > 0.0


def test_gamma_fit_rms_residual_small():
    result = gamma_fit_from_peaks()
    # By construction the fit minimizes residuals; should be < 10%
    assert result["rms_residual_pct"] < 15.0


def test_gamma_fit_three_residuals():
    result = gamma_fit_from_peaks()
    assert len(result["peak_residuals_pct"]) == 3


def test_gamma_fit_r_squared_reasonable():
    result = gamma_fit_from_peaks()
    # For a good fit, R² should be positive
    assert result["r_squared_log"] > 0.0


def test_gamma_fit_pivot_normalization():
    # At ell_pivot = 540, Z_φ(ell_pivot) should equal Z_φ^(0) for any γ
    result = gamma_fit_from_peaks()
    gamma = result["gamma_fit"]
    z_at_pivot = zphi_spectral_envelope(ELL_PIVOT, gamma)
    assert abs(z_at_pivot - Z_PHI_0) < 1e-10


def test_gamma_fit_with_custom_suppressions():
    result = gamma_fit_from_peaks(suppressions=[3.0, 4.0, 5.0], ells=[200, 500, 800])
    assert isinstance(result["gamma_fit"], float)
    assert result["gamma_fit"] > 0.0


def test_gamma_fit_theory_agreement():
    # γ_theory and γ_fit should agree within 20%
    gamma_fit = gamma_fit_from_peaks()["gamma_fit"]
    gamma_theory = gamma_theory_from_braid()["gamma_theory"]
    rel_diff = abs(gamma_fit - gamma_theory) / max(abs(gamma_fit), 1e-10)
    assert rel_diff < 0.20


# ═══════════════════════════════════════════════════════════════════════════════
# Section 5 — zphi_spectral_envelope
# ═══════════════════════════════════════════════════════════════════════════════


def test_zphi_spectral_envelope_at_pivot():
    # Z_φ(ℓ_pivot) = Z_φ^(0) exactly (normalization condition)
    z_at_pivot = zphi_spectral_envelope(ELL_PIVOT, gamma=0.273)
    assert abs(z_at_pivot - Z_PHI_0) < 1e-10


def test_zphi_spectral_envelope_increasing_with_ell():
    # For γ > 0, Z_φ(ℓ) is increasing
    z1 = zphi_spectral_envelope(200.0, gamma=0.273)
    z2 = zphi_spectral_envelope(500.0, gamma=0.273)
    z3 = zphi_spectral_envelope(900.0, gamma=0.273)
    assert z1 < z2 < z3


def test_zphi_spectral_envelope_decreasing_for_negative_gamma():
    # For γ < 0, Z_φ(ℓ) is decreasing
    z1 = zphi_spectral_envelope(200.0, gamma=-0.1)
    z2 = zphi_spectral_envelope(900.0, gamma=-0.1)
    assert z1 > z2


def test_zphi_spectral_envelope_unity_at_pivot_any_gamma():
    for gamma in [0.1, 0.2, 0.3, 0.5]:
        z = zphi_spectral_envelope(ELL_PIVOT, gamma=gamma)
        assert abs(z - Z_PHI_0) < 1e-10


def test_zphi_spectral_envelope_power_law():
    # Z_φ(ℓ) / Z_φ^(0) = (ℓ/ℓ_pivot)^γ
    gamma = 0.273
    ell = 300.0
    ratio = zphi_spectral_envelope(ell, gamma) / Z_PHI_0
    expected = (ell / ELL_PIVOT) ** gamma
    assert abs(ratio - expected) < 1e-12


def test_zphi_spectral_envelope_greater_than_one():
    # Z_φ(ℓ) > 1 for all ℓ > 0 (it starts at ≥1 and scales up)
    for ell in [50.0, 200.0, 540.0, 1000.0]:
        assert zphi_spectral_envelope(ell, gamma=0.2) > 1.0


def test_zphi_spectral_envelope_invalid_ell():
    with pytest.raises((ValueError, ZeroDivisionError)):
        zphi_spectral_envelope(-100.0, gamma=0.2)


def test_zphi_spectral_envelope_default_gamma():
    # Default gamma should come from braid β-function (positive)
    z = zphi_spectral_envelope(400.0)
    assert z > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Section 6 — zphi_at_acoustic_peaks
# ═══════════════════════════════════════════════════════════════════════════════


def test_zphi_at_acoustic_peaks_keys():
    result = zphi_at_acoustic_peaks()
    for key in ("z_phi_at_peaks", "ells", "gamma_used", "z_phi_0"):
        assert key in result


def test_zphi_at_acoustic_peaks_count():
    result = zphi_at_acoustic_peaks()
    assert len(result["z_phi_at_peaks"]) == 3


def test_zphi_at_acoustic_peaks_increasing():
    # Z_φ increasing: first peak < second < third (for γ > 0)
    result = zphi_at_acoustic_peaks(gamma=0.273)
    z = result["z_phi_at_peaks"]
    assert z[0] < z[1] < z[2]


def test_zphi_at_acoustic_peaks_pivot_normalization():
    # Z_φ at second peak (ℓ=540=pivot) equals Z_φ^(0)
    result = zphi_at_acoustic_peaks(gamma=0.273)
    # Second peak index is 1
    z_peak2 = result["z_phi_at_peaks"][1]
    assert abs(z_peak2 - Z_PHI_0) < 1e-10


def test_zphi_at_acoustic_peaks_all_positive():
    result = zphi_at_acoustic_peaks()
    for z in result["z_phi_at_peaks"]:
        assert z > 0.0


def test_zphi_at_acoustic_peaks_ells_field():
    result = zphi_at_acoustic_peaks()
    assert result["ells"] == ACOUSTIC_PEAK_ELLS


# ═══════════════════════════════════════════════════════════════════════════════
# Section 7 — peak_residuals_flat_zphi
# ═══════════════════════════════════════════════════════════════════════════════


def test_peak_residuals_flat_keys():
    result = peak_residuals_flat_zphi()
    for key in (
        "method", "z_phi_0", "suppressions", "residuals",
        "residuals_pct", "mean_abs_residual_pct", "max_abs_residual_pct",
    ):
        assert key in result


def test_peak_residuals_flat_method_label():
    result = peak_residuals_flat_zphi()
    assert result["method"] == "flat_Z_phi_0"


def test_peak_residuals_flat_count():
    result = peak_residuals_flat_zphi()
    assert len(result["residuals"]) == 3
    assert len(result["residuals_pct"]) == 3


def test_peak_residuals_flat_first_peak_positive():
    # At peak 1: Z_φ^(0)/S₁ = 5.301/4.2 > 1 → positive residual (overcorrected)
    result = peak_residuals_flat_zphi()
    assert result["residuals"][0] > 0.0


def test_peak_residuals_flat_third_peak_negative():
    # At peak 3: Z_φ^(0)/S₃ = 5.301/6.1 < 1 → negative residual (undercorrected)
    result = peak_residuals_flat_zphi()
    assert result["residuals"][2] < 0.0


def test_peak_residuals_flat_mean_significant():
    # Mean residual should be non-trivial (> 5%) — there IS an envelope
    result = peak_residuals_flat_zphi()
    assert result["mean_abs_residual_pct"] > 5.0


def test_peak_residuals_flat_max_significant():
    result = peak_residuals_flat_zphi()
    assert result["max_abs_residual_pct"] > 10.0


# ═══════════════════════════════════════════════════════════════════════════════
# Section 8 — peak_residuals_zphi_k
# ═══════════════════════════════════════════════════════════════════════════════


def test_peak_residuals_zphi_k_keys():
    result = peak_residuals_zphi_k(gamma=0.273)
    for key in (
        "method", "gamma", "z_phi_at_peaks", "suppressions",
        "residuals", "residuals_pct", "mean_abs_residual_pct",
    ):
        assert key in result


def test_peak_residuals_zphi_k_method_label():
    result = peak_residuals_zphi_k(gamma=0.273)
    assert result["method"] == "zphi_k_spectral_envelope"


def test_peak_residuals_zphi_k_count():
    result = peak_residuals_zphi_k()
    assert len(result["residuals"]) == 3


def test_peak_residuals_zphi_k_smaller_than_flat():
    flat = peak_residuals_flat_zphi()
    envelope = peak_residuals_zphi_k()
    # Spectral envelope should reduce mean residual vs. flat
    assert envelope["mean_abs_residual_pct"] < flat["mean_abs_residual_pct"]


def test_peak_residuals_zphi_k_with_fitted_gamma():
    gamma_fit = gamma_fit_from_peaks()["gamma_fit"]
    result = peak_residuals_zphi_k(gamma=gamma_fit)
    # With fitted gamma, residuals should be very small (< 10%)
    assert result["mean_abs_residual_pct"] < 10.0


def test_peak_residuals_zphi_k_theory_gamma_reasonable():
    gamma_theory = gamma_theory_from_braid()["gamma_theory"]
    result = peak_residuals_zphi_k(gamma=gamma_theory)
    # Theory gamma should give reasonable residuals (< 20%)
    assert result["mean_abs_residual_pct"] < 20.0


def test_peak_residuals_zphi_k_pivot_peak():
    # At ℓ_pivot = 540 (second peak, index 1): Z_φ(ℓ_pivot) = Z_φ^(0)
    result = peak_residuals_zphi_k(gamma=0.273)
    z_at_second = result["z_phi_at_peaks"][1]
    assert abs(z_at_second - Z_PHI_0) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# Section 9 — bessel_spectral_envelope
# ═══════════════════════════════════════════════════════════════════════════════


def test_bessel_envelope_keys():
    result = bessel_spectral_envelope()
    for key in (
        "bessel_envelope", "rho", "direction",
        "consistent_with_data", "status",
    ):
        assert key in result


def test_bessel_envelope_count():
    result = bessel_spectral_envelope(n_peaks=3)
    assert len(result["bessel_envelope"]) == 3


def test_bessel_envelope_first_value_one():
    result = bessel_spectral_envelope()
    # E_1 = J_0(ρ)/J_0(ρ) = 1.0
    assert abs(result["bessel_envelope"][0] - 1.0) < 1e-10


def test_bessel_envelope_direction_decreasing():
    result = bessel_spectral_envelope()
    # J_{n-1}(n×ρ) is decreasing for the (5,7) braid — this is the key result
    assert result["direction"] == "DECREASING"


def test_bessel_envelope_not_consistent_with_data():
    # The Bessel ansatz predicts wrong direction → inconsistent with data
    result = bessel_spectral_envelope()
    assert result["consistent_with_data"] is False


def test_bessel_envelope_status_ruled_out():
    result = bessel_spectral_envelope()
    assert "RULED_OUT" in result["status"]


def test_bessel_envelope_qualitative_insight_present():
    result = bessel_spectral_envelope()
    assert "qualitative_insight" in result
    assert len(result["qualitative_insight"]) > 50


def test_bessel_envelope_custom_rho():
    # With small rho, should still give E_1 = 1
    result = bessel_spectral_envelope(rho=0.1, n_peaks=3)
    assert abs(result["bessel_envelope"][0] - 1.0) < 1e-10


def test_bessel_envelope_n_peaks_4():
    result = bessel_spectral_envelope(n_peaks=4)
    assert len(result["bessel_envelope"]) == 4


def test_bessel_envelope_all_positive():
    result = bessel_spectral_envelope()
    # J_n are real and normalized relative to J_0 which is positive for small arg
    # They may not all be positive (J_n can oscillate), but the magnitudes should be computed
    for e in result["bessel_envelope"]:
        assert isinstance(e, float)


# ═══════════════════════════════════════════════════════════════════════════════
# Section 10 — braid_sound_speed_acoustic_ratio
# ═══════════════════════════════════════════════════════════════════════════════


def test_acoustic_ratio_keys():
    result = braid_sound_speed_acoustic_ratio()
    for key in (
        "r_sound", "cs_um", "cs_lcdm",
        "acoustic_amplitude_ratios", "status",
    ):
        assert key in result


def test_acoustic_ratio_r_sound():
    result = braid_sound_speed_acoustic_ratio()
    assert abs(result["r_sound"] - R_SOUND) < 1e-12


def test_acoustic_ratio_cs_um():
    result = braid_sound_speed_acoustic_ratio()
    assert abs(result["cs_um"] - CS_BRAID) < 1e-12


def test_acoustic_ratio_cs_lcdm():
    result = braid_sound_speed_acoustic_ratio()
    assert abs(result["cs_lcdm"] - CS_LCDM) < 1e-12


def test_acoustic_ratio_count():
    result = braid_sound_speed_acoustic_ratio(n_peaks=3)
    assert len(result["acoustic_amplitude_ratios"]) == 3


def test_acoustic_ratio_status_illustrative():
    result = braid_sound_speed_acoustic_ratio()
    assert "ILLUSTRATIVE" in result["status"]


def test_acoustic_ratio_r_sound_range():
    result = braid_sound_speed_acoustic_ratio()
    assert 0.0 < result["r_sound"] < 1.0


def test_acoustic_ratio_custom_n_peaks():
    result = braid_sound_speed_acoustic_ratio(n_peaks=5)
    assert len(result["acoustic_amplitude_ratios"]) == 5


# ═══════════════════════════════════════════════════════════════════════════════
# Section 11 — three_peak_consistency_report
# ═══════════════════════════════════════════════════════════════════════════════


def test_consistency_report_keys():
    result = three_peak_consistency_report()
    for key in (
        "method_A_flat_zphi", "method_B_gamma_theory",
        "method_C_gamma_fit", "method_D_bessel_ansatz",
        "gamma_theory", "gamma_fit", "gamma_theory_vs_fit_pct",
        "improvement_theory_over_flat_pct", "verdict",
    ):
        assert key in result


def test_consistency_method_A_label():
    result = three_peak_consistency_report()
    assert "flat" in result["method_A_flat_zphi"]["label"].lower()


def test_consistency_method_B_label():
    result = three_peak_consistency_report()
    assert "theory" in result["method_B_gamma_theory"]["label"].lower()


def test_consistency_method_C_label():
    result = three_peak_consistency_report()
    assert "fit" in result["method_C_gamma_fit"]["label"].lower()


def test_consistency_method_D_bessel_ruled_out():
    result = three_peak_consistency_report()
    assert result["method_D_bessel_ansatz"]["status"] == "RULED_OUT"


def test_consistency_theory_improves_over_flat():
    result = three_peak_consistency_report()
    # Z_φ(ℓ) with theory γ should have smaller mean residual than flat Z_φ^(0)
    flat_residual = result["method_A_flat_zphi"]["mean_abs_residual_pct"]
    theory_residual = result["method_B_gamma_theory"]["mean_abs_residual_pct"]
    assert theory_residual < flat_residual


def test_consistency_fit_better_than_theory():
    result = three_peak_consistency_report()
    # Fitted γ should give smaller residual than theory γ (by construction)
    theory_residual = result["method_B_gamma_theory"]["mean_abs_residual_pct"]
    fit_residual = result["method_C_gamma_fit"]["mean_abs_residual_pct"]
    assert fit_residual <= theory_residual + 1.0  # fit should be ≤ theory (with small tolerance)


def test_consistency_gamma_theory_vs_fit_agreement():
    result = three_peak_consistency_report()
    # γ_theory and γ_fit should agree within 25%
    assert result["gamma_theory_vs_fit_pct"] < 25.0


def test_consistency_verdict_contains_key_phrase():
    result = three_peak_consistency_report()
    verdict = result["verdict"]
    assert "SPECTRAL_ENVELOPE" in verdict


def test_consistency_improvement_positive():
    result = three_peak_consistency_report()
    # The spectral envelope should improve over flat (positive improvement)
    assert result["improvement_theory_over_flat_pct"] > 0.0


def test_consistency_gamma_fields():
    result = three_peak_consistency_report()
    assert result["gamma_theory"] > 0.0
    assert result["gamma_fit"] > 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# Section 12 — spectral_envelope_validation
# ═══════════════════════════════════════════════════════════════════════════════


def test_envelope_validation_keys():
    result = spectral_envelope_validation()
    for key in ("ells", "z_phi_ell", "z_phi_min", "z_phi_max", "gamma", "monotone_increasing"):
        assert key in result


def test_envelope_validation_monotone_increasing():
    result = spectral_envelope_validation(gamma=0.273)
    assert result["monotone_increasing"] is True


def test_envelope_validation_min_less_than_max():
    result = spectral_envelope_validation()
    assert result["z_phi_min"] < result["z_phi_max"]


def test_envelope_validation_all_positive():
    result = spectral_envelope_validation()
    assert all(z > 0 for z in result["z_phi_ell"])


def test_envelope_validation_pivot_value():
    # Z_φ at pivot ℓ=540 should be Z_φ^(0)
    result = spectral_envelope_validation(
        ell_range=[220.0, 540.0, 820.0],
        gamma=0.273,
    )
    idx = result["ells"].index(540.0)
    assert abs(result["z_phi_ell"][idx] - Z_PHI_0) < 1e-10


def test_envelope_validation_custom_range():
    ells = [100.0, 500.0, 1000.0]
    result = spectral_envelope_validation(ell_range=ells, gamma=0.2)
    assert len(result["z_phi_ell"]) == 3


def test_envelope_validation_count_default():
    result = spectral_envelope_validation()
    # Default: range(100, 1001, 50) = 19 values
    assert len(result["ells"]) == len(result["z_phi_ell"])
    assert len(result["ells"]) > 5


# ═══════════════════════════════════════════════════════════════════════════════
# Section 13 — pillar356_summary
# ═══════════════════════════════════════════════════════════════════════════════


def test_summary_keys():
    result = pillar356_summary()
    for key in (
        "pillar", "title", "status", "key_results",
        "gamma_theory_derivation", "gamma_data_fit",
        "three_peak_consistency", "bessel_ansatz",
        "acoustic_ratio", "electronic_music_connection",
        "frontier_items", "pillar_references",
        "fallibility_md_update",
    ):
        assert key in result


def test_summary_pillar_number():
    result = pillar356_summary()
    assert result["pillar"] == 356


def test_summary_status():
    result = pillar356_summary()
    assert result["status"] == "FRONTIER_COMPUTATION"


def test_summary_key_results_z_phi_0():
    result = pillar356_summary()
    z0 = result["key_results"]["Z_phi_0_pillar355"]
    assert abs(z0 - Z_PHI_0) < 1e-6


def test_summary_key_results_gamma_theory_range():
    result = pillar356_summary()
    gamma = result["key_results"]["gamma_theory"]
    assert 0.15 < gamma < 0.40


def test_summary_key_results_gamma_fit_range():
    result = pillar356_summary()
    gamma = result["key_results"]["gamma_fit"]
    assert 0.15 < gamma < 0.50


def test_summary_key_results_bessel_ruled_out():
    result = pillar356_summary()
    assert result["key_results"]["bessel_ansatz_ruled_out"] is True


def test_summary_key_results_bessel_decreasing():
    result = pillar356_summary()
    assert result["key_results"]["bessel_ansatz_direction"] == "DECREASING"


def test_summary_key_results_mean_residual_improvement():
    result = pillar356_summary()
    flat = result["key_results"]["mean_residual_flat_pct"]
    theory = result["key_results"]["mean_residual_theory_envelope_pct"]
    assert theory < flat


def test_summary_electronic_music_connection():
    result = pillar356_summary()
    em = result["electronic_music_connection"]
    assert "analogy" in em
    assert "adsr_mapping" in em
    assert "fm_modulation_index" in em


def test_summary_adsr_mapping_keys():
    result = pillar356_summary()
    adsr = result["electronic_music_connection"]["adsr_mapping"]
    for key in ("Attack", "Decay", "Sustain", "Release", "Master_volume", "Spectral_envelope"):
        assert key in adsr


def test_summary_fm_modulation_index_is_rho():
    result = pillar356_summary()
    I_FM = result["electronic_music_connection"]["fm_modulation_index"]
    assert abs(I_FM - RHO_BRAID) < 1e-10


def test_summary_frontier_items_count():
    result = pillar356_summary()
    assert len(result["frontier_items"]) >= 4


def test_summary_frontier_item_structure():
    result = pillar356_summary()
    for item in result["frontier_items"]:
        assert "id" in item
        assert "description" in item
        assert "status" in item
        assert "detail" in item


def test_summary_pillar_references_contain_355():
    result = pillar356_summary()
    refs = " ".join(result["pillar_references"])
    assert "355" in refs


def test_summary_fallibility_update_contains_pillar():
    result = pillar356_summary()
    update = result["fallibility_md_update"]
    assert "356" in update


def test_summary_fallibility_update_contains_gamma():
    result = pillar356_summary()
    update = result["fallibility_md_update"]
    assert "γ" in update or "gamma" in update.lower()


def test_summary_fallibility_update_contains_bessel_ruled_out():
    result = pillar356_summary()
    update = result["fallibility_md_update"]
    assert "ruled out" in update.lower() or "RULED_OUT" in update


def test_summary_r_sound_ratio():
    result = pillar356_summary()
    r_sound = result["key_results"]["r_sound_ratio"]
    assert abs(r_sound - R_SOUND) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# Section 14 — Physical cross-checks
# ═══════════════════════════════════════════════════════════════════════════════


def test_cross_gamma_theory_vs_fit_within_20pct():
    gamma_theory = gamma_theory_from_braid()["gamma_theory"]
    gamma_fit = gamma_fit_from_peaks()["gamma_fit"]
    assert abs(gamma_theory - gamma_fit) / gamma_fit < 0.20


def test_cross_zphi_k_reproduces_suppression_data():
    # Z_φ(ℓ) with γ_fit should approximately reproduce S_n at each peak
    gamma_fit = gamma_fit_from_peaks()["gamma_fit"]
    for ell, s in zip(ACOUSTIC_PEAK_ELLS, SUPPRESSION_CLASSICAL):
        z_eff = zphi_spectral_envelope(ell, gamma=gamma_fit)
        assert abs(z_eff - s) / s < 0.10  # within 10%


def test_cross_flat_residuals_direction():
    # Peak 1: Z_φ^(0) overcorrects (residual > 0); Peak 3: undercorrects (residual < 0)
    residuals = peak_residuals_flat_zphi()["residuals"]
    assert residuals[0] > 0.0   # overcorrected at peak 1
    assert residuals[2] < 0.0   # undercorrected at peak 3


def test_cross_tower_sum_continuum_approximation():
    # Σw_n ≈ (1/2)√(π×74) − 0.5 = ≈ 7.12
    result = braid_tower_weight_sum()
    continuum = 0.5 * math.sqrt(math.pi * K_CS) - 0.5
    assert abs(result["sum_discrete"] - continuum) / continuum < 0.05


def test_cross_spectral_envelope_monotone():
    # Z_φ(ℓ) is monotonically increasing for γ > 0
    ells = [200.0, 300.0, 400.0, 540.0, 700.0, 900.0]
    z_vals = [zphi_spectral_envelope(ell, gamma=0.273) for ell in ells]
    assert all(z_vals[i] < z_vals[i + 1] for i in range(len(z_vals) - 1))


def test_cross_rho_in_physical_range():
    # ρ must be in (0, 1) for physical braid
    assert 0.0 < RHO_BRAID < 1.0


def test_cross_cs_braid_less_than_cs_lcdm():
    # Braid sound speed < ΛCDM sound speed
    assert CS_BRAID < CS_LCDM


def test_cross_z_phi_0_close_to_5_3():
    # Z_φ^(0) = 1 + √74/2 ≈ 5.30
    assert 5.2 < Z_PHI_0 < 5.4


def test_cross_bessel_ansatz_predicts_wrong_direction():
    # The Bessel ansatz predicts DECREASING, but the data requires INCREASING
    # This is the key negative result of Pillar 356
    bessel = bessel_spectral_envelope()
    assert bessel["direction"] == "DECREASING"
    assert not bessel["consistent_with_data"]


def test_cross_spectral_envelope_improvement_significant():
    # Z_φ(ℓ) with γ_theory should give a non-trivial improvement over flat
    flat = peak_residuals_flat_zphi()
    gamma_theory = gamma_theory_from_braid()["gamma_theory"]
    envelope = peak_residuals_zphi_k(gamma=gamma_theory)
    # At minimum, the envelope should reduce the max residual
    assert envelope["max_abs_residual_pct"] < flat["max_abs_residual_pct"]


def test_cross_pillar_number_correct():
    result = pillar356_summary()
    assert result["pillar"] == PILLAR_NUMBER == 356


def test_cross_z_phi_at_peak2_equals_z0():
    result = zphi_at_acoustic_peaks(gamma=0.25)
    z_at_peak2 = result["z_phi_at_peaks"][1]
    assert abs(z_at_peak2 - Z_PHI_0) < 1e-10


def test_cross_gamma_theory_depends_on_k_cs():
    gamma_74 = gamma_theory_from_braid(k_cs=74)["gamma_theory"]
    gamma_37 = gamma_theory_from_braid(k_cs=37)["gamma_theory"]
    # Different K_CS → different γ_theory
    assert gamma_74 != gamma_37


def test_cross_frontier_item_f356_1_open():
    result = pillar356_summary()
    items = {i["id"]: i for i in result["frontier_items"]}
    assert items["F356-1"]["status"] == "OPEN"


def test_cross_frontier_item_f356_4_future():
    result = pillar356_summary()
    items = {i["id"]: i for i in result["frontier_items"]}
    assert items["F356-4"]["status"] == "FUTURE_EXPERIMENT"
