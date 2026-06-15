# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar355_zphi_second_quantization.py
==================================================
Test suite for Pillar 355 — Second Quantization of φ: Wavefunction
Renormalization Z_φ and CMB Acoustic Peak Gap Closure.

Covers all public API functions:
  - radion_zero_point_variance()
  - zphi_wavefunction_renormalization()
  - zphi_one_loop_interpretation()
  - mode_expansion_coefficients()
  - fock_space_zero_point_energy()
  - kk_tower_zphi_contribution()
  - quantum_corrected_cl_peaks()
  - quantum_power_spectrum()
  - quantum_boltzmann_source_correction()
  - residual_gap_after_quantum_correction()
  - frontier_roadmap()
  - pillar355_summary()

Physical correctness checks:
  - Z_φ = 1 + √K_CS/(2φ₀²) for canonical parameters
  - Z_φ^{1/2} ∈ [2.0, 2.6] (problem statement range)
  - Gap reduction: mean residual < 30% after quantum correction
  - KK tower convergence with braided weights
  - Fock space zero-point energy positivity
  - One-loop factor consistency: δZ_φ = α × F_KK
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar355_zphi_second_quantization import (
    # Constants
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    K_CS,
    N_W,
    PHI0_FTUM,
    OMEGA_PHI,
    ALPHA_PHI,
    ZP_VARIANCE_CANONICAL,
    Z_PHI_CANONICAL,
    Z_PHI_HALF_CANONICAL,
    Z_PHI_HALF_MIN,
    Z_PHI_HALF_MAX,
    M_KK,
    R_C_PLANCK,
    SUPPRESSION_PEAK1_CLASSICAL,
    SUPPRESSION_PEAK2_CLASSICAL,
    SUPPRESSION_PEAK3_CLASSICAL,
    ACOUSTIC_PEAK_ELLS,
    CL_PEAK1_LCDM_UK2,
    CL_PEAK2_LCDM_UK2,
    CL_PEAK3_LCDM_UK2,
    A_S_PLANCK,
    N_S_UM,
    K_PIVOT_MPC,
    # Functions
    radion_zero_point_variance,
    zphi_wavefunction_renormalization,
    zphi_one_loop_interpretation,
    mode_expansion_coefficients,
    fock_space_zero_point_energy,
    kk_tower_zphi_contribution,
    quantum_corrected_cl_peaks,
    quantum_power_spectrum,
    quantum_boltzmann_source_correction,
    residual_gap_after_quantum_correction,
    frontier_roadmap,
    pillar355_summary,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Section 1 — Module constants
# ═══════════════════════════════════════════════════════════════════════════════

class TestModuleConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 355

    def test_pillar_status_is_frontier(self):
        assert "FRONTIER" in PILLAR_STATUS

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n_w_is_5(self):
        assert N_W == 5

    def test_phi0_is_unity(self):
        assert abs(PHI0_FTUM - 1.0) < 1e-12

    def test_omega_phi_equals_one_over_sqrt_k_cs(self):
        expected = 1.0 / math.sqrt(74)
        assert abs(OMEGA_PHI - expected) < 1e-10

    def test_alpha_phi_equals_one(self):
        assert abs(ALPHA_PHI - 1.0) < 1e-12

    def test_zp_variance_canonical_is_sqrt_k_cs_over_two(self):
        expected = math.sqrt(74) / 2.0
        assert abs(ZP_VARIANCE_CANONICAL - expected) < 1e-10

    def test_z_phi_canonical_formula(self):
        expected = 1.0 + math.sqrt(74) / 2.0
        assert abs(Z_PHI_CANONICAL - expected) < 1e-10

    def test_z_phi_canonical_value_in_range_four_to_seven(self):
        assert 4.0 < Z_PHI_CANONICAL < 7.0

    def test_z_phi_half_canonical_formula(self):
        expected = math.sqrt(1.0 + math.sqrt(74) / 2.0)
        assert abs(Z_PHI_HALF_CANONICAL - expected) < 1e-10

    def test_z_phi_half_canonical_in_predicted_range(self):
        # Problem statement: Z_φ^{1/2} ∈ [2.0, 2.6]
        assert Z_PHI_HALF_MIN <= Z_PHI_HALF_CANONICAL <= Z_PHI_HALF_MAX

    def test_z_phi_half_min_is_2(self):
        assert abs(Z_PHI_HALF_MIN - 2.0) < 1e-12

    def test_z_phi_half_max_is_2p6(self):
        assert abs(Z_PHI_HALF_MAX - 2.6) < 1e-12

    def test_m_kk_is_one_over_r_c(self):
        assert abs(M_KK - 1.0 / R_C_PLANCK) < 1e-12

    def test_r_c_planck_is_12(self):
        assert abs(R_C_PLANCK - 12.0) < 1e-12

    def test_suppressions_positive(self):
        assert SUPPRESSION_PEAK1_CLASSICAL > 1.0
        assert SUPPRESSION_PEAK2_CLASSICAL > 1.0
        assert SUPPRESSION_PEAK3_CLASSICAL > 1.0

    def test_suppressions_ordering(self):
        # Gap grows with peak index
        assert SUPPRESSION_PEAK1_CLASSICAL < SUPPRESSION_PEAK2_CLASSICAL
        assert SUPPRESSION_PEAK2_CLASSICAL < SUPPRESSION_PEAK3_CLASSICAL

    def test_acoustic_peak_ells_length(self):
        assert len(ACOUSTIC_PEAK_ELLS) == 3

    def test_acoustic_peak_ells_values(self):
        assert ACOUSTIC_PEAK_ELLS[0] == 220
        assert ACOUSTIC_PEAK_ELLS[1] == 540
        assert ACOUSTIC_PEAK_ELLS[2] == 820

    def test_cl_lcdm_positive(self):
        assert CL_PEAK1_LCDM_UK2 > 0
        assert CL_PEAK2_LCDM_UK2 > 0
        assert CL_PEAK3_LCDM_UK2 > 0

    def test_a_s_planck_order_of_magnitude(self):
        assert 1e-10 < A_S_PLANCK < 1e-8

    def test_n_s_um_value(self):
        assert abs(N_S_UM - 0.9635) < 1e-4

    def test_k_pivot_mpc(self):
        assert abs(K_PIVOT_MPC - 0.05) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# Section 2 — radion_zero_point_variance()
# ═══════════════════════════════════════════════════════════════════════════════

class TestRadionZeroPointVariance:
    def test_returns_dict(self):
        result = radion_zero_point_variance()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = radion_zero_point_variance()
        for key in ("phi0", "omega_phi", "zp_variance", "alpha_phi", "epsilon_quantum", "k_cs"):
            assert key in result, f"Missing key: {key}"

    def test_omega_phi_canonical(self):
        result = radion_zero_point_variance()
        expected = 1.0 / math.sqrt(74)
        assert abs(result["omega_phi"] - expected) < 1e-10

    def test_zp_variance_canonical(self):
        result = radion_zero_point_variance()
        expected = math.sqrt(74) / 2.0
        assert abs(result["zp_variance"] - expected) < 1e-10

    def test_zp_variance_equals_one_over_two_omega(self):
        result = radion_zero_point_variance()
        assert abs(result["zp_variance"] - 1.0 / (2.0 * result["omega_phi"])) < 1e-10

    def test_alpha_phi_unity_at_phi0_1(self):
        result = radion_zero_point_variance(phi0=1.0)
        assert abs(result["alpha_phi"] - 1.0) < 1e-12

    def test_alpha_phi_phi0_dependence(self):
        r1 = radion_zero_point_variance(phi0=2.0)
        assert abs(r1["alpha_phi"] - 0.25) < 1e-12

    def test_epsilon_quantum_positive(self):
        result = radion_zero_point_variance()
        assert result["epsilon_quantum"] > 0

    def test_epsilon_quantum_equals_zp_over_phi0_sq(self):
        phi0 = 1.5
        result = radion_zero_point_variance(phi0=phi0)
        expected = result["zp_variance"] / (phi0 ** 2)
        assert abs(result["epsilon_quantum"] - expected) < 1e-10

    def test_zp_variance_scales_with_sqrt_k_cs(self):
        r74 = radion_zero_point_variance(k_cs=74)
        # For k_cs = 74: zp_variance = √74/2
        assert abs(r74["zp_variance"] - math.sqrt(74) / 2.0) < 1e-10

    def test_k_cs_returned_correctly(self):
        result = radion_zero_point_variance(k_cs=74)
        assert result["k_cs"] == 74

    def test_phi0_returned_correctly(self):
        result = radion_zero_point_variance(phi0=2.0)
        assert abs(result["phi0"] - 2.0) < 1e-12


# ═══════════════════════════════════════════════════════════════════════════════
# Section 3 — zphi_wavefunction_renormalization()
# ═══════════════════════════════════════════════════════════════════════════════

class TestZphiWavefunctionRenormalization:
    def test_returns_dict(self):
        result = zphi_wavefunction_renormalization()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = zphi_wavefunction_renormalization()
        required = (
            "Z_phi", "Z_phi_half", "Z_phi_half_in_range",
            "Z_phi_half_predicted_range", "zp_info", "gap_factor",
            "gap_sqrt", "n_w", "k_cs", "consistency", "formula",
        )
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_z_phi_canonical_value(self):
        result = zphi_wavefunction_renormalization()
        expected = 1.0 + math.sqrt(74) / 2.0
        assert abs(result["Z_phi"] - expected) < 1e-10

    def test_z_phi_greater_than_four(self):
        result = zphi_wavefunction_renormalization()
        assert result["Z_phi"] > 4.0

    def test_z_phi_less_than_seven(self):
        result = zphi_wavefunction_renormalization()
        assert result["Z_phi"] < 7.0

    def test_z_phi_half_canonical(self):
        result = zphi_wavefunction_renormalization()
        expected = math.sqrt(1.0 + math.sqrt(74) / 2.0)
        assert abs(result["Z_phi_half"] - expected) < 1e-10

    def test_z_phi_half_in_predicted_range(self):
        result = zphi_wavefunction_renormalization()
        assert result["Z_phi_half_in_range"] is True

    def test_z_phi_half_in_range_2_to_2p6(self):
        result = zphi_wavefunction_renormalization()
        z_half = result["Z_phi_half"]
        assert 2.0 <= z_half <= 2.6

    def test_consistency_label_contains_consistent(self):
        result = zphi_wavefunction_renormalization()
        assert "CONSISTENT" in result["consistency"]

    def test_gap_factor_equals_z_phi(self):
        result = zphi_wavefunction_renormalization()
        assert abs(result["gap_factor"] - result["Z_phi"]) < 1e-12

    def test_gap_sqrt_equals_z_phi_half(self):
        result = zphi_wavefunction_renormalization()
        assert abs(result["gap_sqrt"] - result["Z_phi_half"]) < 1e-12

    def test_z_phi_increases_as_k_cs_increases(self):
        r74 = zphi_wavefunction_renormalization(k_cs=74)
        r80 = zphi_wavefunction_renormalization(k_cs=80)
        assert r80["Z_phi"] > r74["Z_phi"]

    def test_z_phi_decreases_as_phi0_increases(self):
        r1 = zphi_wavefunction_renormalization(phi0=1.0)
        r2 = zphi_wavefunction_renormalization(phi0=2.0)
        assert r2["Z_phi"] < r1["Z_phi"]

    def test_z_phi_approaches_one_as_phi0_large(self):
        r_large = zphi_wavefunction_renormalization(phi0=100.0)
        assert abs(r_large["Z_phi"] - 1.0) < 0.01

    def test_formula_string_present(self):
        result = zphi_wavefunction_renormalization()
        assert "Z_phi" in result["formula"]
        assert "sqrt" in result["formula"].lower() or "K_CS" in result["formula"]

    def test_zp_info_sub_report(self):
        result = zphi_wavefunction_renormalization()
        assert isinstance(result["zp_info"], dict)
        assert "zp_variance" in result["zp_info"]


# ═══════════════════════════════════════════════════════════════════════════════
# Section 4 — zphi_one_loop_interpretation()
# ═══════════════════════════════════════════════════════════════════════════════

class TestZphiOneLoopInterpretation:
    def test_returns_dict(self):
        result = zphi_one_loop_interpretation()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = zphi_one_loop_interpretation()
        for key in ("alpha_phi", "F_KK", "delta_Z_phi", "Z_phi",
                    "naive_loop_factor", "KK_resonance_enhancement",
                    "interpretation"):
            assert key in result, f"Missing key: {key}"

    def test_alpha_phi_unity(self):
        result = zphi_one_loop_interpretation()
        assert abs(result["alpha_phi"] - 1.0) < 1e-12

    def test_F_KK_equals_sqrt_k_cs_over_two(self):
        result = zphi_one_loop_interpretation()
        expected = math.sqrt(74) / 2.0
        assert abs(result["F_KK"] - expected) < 1e-10

    def test_delta_z_equals_alpha_times_f_kk(self):
        result = zphi_one_loop_interpretation()
        assert abs(result["delta_Z_phi"] - result["alpha_phi"] * result["F_KK"]) < 1e-10

    def test_z_phi_equals_one_plus_delta(self):
        result = zphi_one_loop_interpretation()
        assert abs(result["Z_phi"] - (1.0 + result["delta_Z_phi"])) < 1e-10

    def test_naive_loop_factor_order_one_percent(self):
        result = zphi_one_loop_interpretation()
        # α/(16π²) ≈ 0.006 — much smaller than the KK-enhanced result
        assert result["naive_loop_factor"] < 0.02

    def test_kk_resonance_enhancement_large(self):
        result = zphi_one_loop_interpretation()
        # KK enhancement factor should be >> 1
        assert result["KK_resonance_enhancement"] > 100.0

    def test_interpretation_string_present(self):
        result = zphi_one_loop_interpretation()
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 50


# ═══════════════════════════════════════════════════════════════════════════════
# Section 5 — mode_expansion_coefficients()
# ═══════════════════════════════════════════════════════════════════════════════

class TestModeExpansionCoefficients:
    def test_returns_dict(self):
        result = mode_expansion_coefficients()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = mode_expansion_coefficients()
        for key in ("n_modes", "k_cs", "omega_phi", "c_0_zeromode",
                    "c_0_variance", "mode_data", "description"):
            assert key in result, f"Missing key: {key}"

    def test_mode_data_length(self):
        result = mode_expansion_coefficients(n_modes=5)
        assert len(result["mode_data"]) == 6  # n=0..5

    def test_n_modes_returned(self):
        result = mode_expansion_coefficients(n_modes=8)
        assert result["n_modes"] == 8

    def test_c_0_positive(self):
        result = mode_expansion_coefficients()
        assert result["c_0_zeromode"] > 0

    def test_c_0_equals_one_over_sqrt_two_omega(self):
        result = mode_expansion_coefficients()
        expected = 1.0 / math.sqrt(2.0 * result["omega_phi"])
        assert abs(result["c_0_zeromode"] - expected) < 1e-10

    def test_c_0_variance_equals_c_0_squared(self):
        result = mode_expansion_coefficients()
        assert abs(result["c_0_variance"] - result["c_0_zeromode"] ** 2) < 1e-12

    def test_mode_data_indices(self):
        result = mode_expansion_coefficients(n_modes=4)
        for i, mode in enumerate(result["mode_data"]):
            assert mode["n"] == i

    def test_braided_weights_monotone_decreasing(self):
        result = mode_expansion_coefficients(n_modes=10)
        modes = result["mode_data"]
        for i in range(1, len(modes) - 1):
            assert modes[i]["w_n"] >= modes[i + 1]["w_n"]

    def test_zero_mode_weight_is_one(self):
        result = mode_expansion_coefficients()
        assert abs(result["mode_data"][0]["w_n"] - 1.0) < 1e-12

    def test_zp_contribution_positive_all_modes(self):
        result = mode_expansion_coefficients(n_modes=10)
        for mode in result["mode_data"]:
            assert mode["zp_contribution"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
# Section 6 — fock_space_zero_point_energy()
# ═══════════════════════════════════════════════════════════════════════════════

class TestFockSpaceZeroPointEnergy:
    def test_returns_dict(self):
        result = fock_space_zero_point_energy()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = fock_space_zero_point_energy()
        for key in ("n_max", "k_cs", "m_kk", "omega_phi", "E0_zero_mode",
                    "E0_kk_tower", "E0_total", "mode_e0"):
            assert key in result, f"Missing key: {key}"

    def test_e0_zero_mode_positive(self):
        result = fock_space_zero_point_energy()
        assert result["E0_zero_mode"] > 0

    def test_e0_zero_mode_formula(self):
        result = fock_space_zero_point_energy()
        expected = 0.5 * result["omega_phi"]
        assert abs(result["E0_zero_mode"] - expected) < 1e-10

    def test_e0_kk_tower_positive(self):
        result = fock_space_zero_point_energy()
        assert result["E0_kk_tower"] > 0

    def test_e0_total_greater_than_zero_mode(self):
        result = fock_space_zero_point_energy()
        assert result["E0_total"] > result["E0_zero_mode"]

    def test_mode_e0_length(self):
        result = fock_space_zero_point_energy(n_max=5)
        assert len(result["mode_e0"]) == 6  # n=0..5

    def test_kk_modes_high_n_suppressed(self):
        # The KK mode energy e0_n = w_n × n × M_KK / 2 peaks near n*=sqrt(K_CS/2) ≈ 6
        # and decays for large n. Compare n=5 (near peak) vs n=20 (well past peak).
        result = fock_space_zero_point_energy(n_max=20)
        modes = result["mode_e0"]
        e0_5 = modes[5]["e0_n"]
        e0_20 = modes[20]["e0_n"]
        assert e0_20 < e0_5  # Gaussian decay dominates at large n

    def test_n_max_returned(self):
        result = fock_space_zero_point_energy(n_max=15)
        assert result["n_max"] == 15

    def test_convergence_with_large_n_max(self):
        # The braided sum converges once past the Gaussian peak at n* ≈ sqrt(K_CS/2) ≈ 6.
        # Compare n_max=80 vs n_max=100: additional contribution < 1% of total.
        r80 = fock_space_zero_point_energy(n_max=80)
        r100 = fock_space_zero_point_energy(n_max=100)
        delta = abs(r100["E0_total"] - r80["E0_total"])
        assert delta < 0.01 * r80["E0_total"]  # < 1% relative change


# ═══════════════════════════════════════════════════════════════════════════════
# Section 7 — kk_tower_zphi_contribution()
# ═══════════════════════════════════════════════════════════════════════════════

class TestKKTowerZphiContribution:
    def test_returns_dict(self):
        result = kk_tower_zphi_contribution()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = kk_tower_zphi_contribution()
        for key in ("Z_phi_zero_mode", "Z_phi_kk_sum", "Z_phi_total",
                    "Z_phi_physical", "mode_contributions", "uv_note",
                    "n_max", "k_cs", "m_kk", "phi0"):
            assert key in result, f"Missing key: {key}"

    def test_z_phi_zero_mode_matches_canonical(self):
        result = kk_tower_zphi_contribution()
        expected = 1.0 + math.sqrt(74) / 2.0
        assert abs(result["Z_phi_zero_mode"] - expected) < 1e-10

    def test_z_phi_physical_equals_zero_mode(self):
        result = kk_tower_zphi_contribution()
        assert abs(result["Z_phi_physical"] - result["Z_phi_zero_mode"]) < 1e-12

    def test_z_phi_kk_sum_positive(self):
        result = kk_tower_zphi_contribution()
        assert result["Z_phi_kk_sum"] > 0

    def test_z_phi_total_greater_than_zero_mode(self):
        result = kk_tower_zphi_contribution()
        assert result["Z_phi_total"] > result["Z_phi_zero_mode"]

    def test_uv_note_string_present(self):
        result = kk_tower_zphi_contribution()
        assert isinstance(result["uv_note"], str)
        assert len(result["uv_note"]) > 50

    def test_mode_contributions_length(self):
        result = kk_tower_zphi_contribution(n_max=10)
        assert len(result["mode_contributions"]) == 11  # n=0..10

    def test_zero_mode_delta_z_dominant_vs_single_kk_mode(self):
        # The zero-mode Z_φ contribution ≈ 4.30 is large; the KK tower
        # sum is also significant (larger for small n due to 1/m_n factor).
        # But the PHYSICAL Z_φ for CMB physics is the zero-mode only,
        # since KK modes are superhorizon-suppressed at CMB scales.
        result = kk_tower_zphi_contribution()
        delta_z_zero = result["mode_contributions"][0]["delta_Z_phi"]
        # Zero-mode contribution ≈ sqrt(74)/2 ≈ 4.30 > any single KK mode at large n
        delta_z_large_n = result["mode_contributions"][-1]["delta_Z_phi"]
        assert delta_z_zero > delta_z_large_n


# ═══════════════════════════════════════════════════════════════════════════════
# Section 8 — quantum_corrected_cl_peaks()
# ═══════════════════════════════════════════════════════════════════════════════

class TestQuantumCorrectedClPeaks:
    def test_returns_list(self):
        result = quantum_corrected_cl_peaks()
        assert isinstance(result, list)

    def test_three_peaks_returned(self):
        result = quantum_corrected_cl_peaks()
        assert len(result) == 3

    def test_required_keys_per_peak(self):
        result = quantum_corrected_cl_peaks()
        for peak in result:
            for key in ("peak_index", "ell", "suppression_classical",
                        "cl_lcdm_uk2", "cl_classical_uk2", "cl_quantum_uk2",
                        "ratio_quantum_to_lcdm", "pct_residual_vs_lcdm",
                        "gap_status"):
                assert key in peak, f"Missing key: {key}"

    def test_peak_indices_1_2_3(self):
        result = quantum_corrected_cl_peaks()
        for i, peak in enumerate(result):
            assert peak["peak_index"] == i + 1

    def test_peak_ells_correct(self):
        result = quantum_corrected_cl_peaks()
        assert result[0]["ell"] == 220
        assert result[1]["ell"] == 540
        assert result[2]["ell"] == 820

    def test_cl_classical_less_than_lcdm(self):
        result = quantum_corrected_cl_peaks()
        for peak in result:
            # Classical UM is suppressed relative to ΛCDM
            assert peak["cl_classical_uk2"] < peak["cl_lcdm_uk2"]

    def test_cl_quantum_greater_than_classical(self):
        result = quantum_corrected_cl_peaks()
        for peak in result:
            assert peak["cl_quantum_uk2"] > peak["cl_classical_uk2"]

    def test_z_phi_enhances_peaks_toward_lcdm(self):
        result = quantum_corrected_cl_peaks(z_phi=Z_PHI_CANONICAL)
        for peak in result:
            # Quantum correction should bring ratio closer to 1 than raw suppression
            ratio = peak["ratio_quantum_to_lcdm"]
            # Should be between 0.5 and 2.0 (substantial improvement from raw 1/4.2)
            assert 0.5 < ratio < 2.0

    def test_second_peak_closest_to_lcdm(self):
        result = quantum_corrected_cl_peaks()
        # Peak 2 (Z_φ/5.0 ≈ 1.06) should be closest to 1.0
        residuals = [abs(peak["ratio_quantum_to_lcdm"] - 1.0) for peak in result]
        assert residuals[1] < max(residuals[0], residuals[2])

    def test_gap_status_strings_valid(self):
        result = quantum_corrected_cl_peaks()
        valid_statuses = {
            "CLOSED_WITHIN_15_PCT",
            "SUBSTANTIALLY_CLOSED",
            "PARTIALLY_CLOSED",
        }
        for peak in result:
            assert peak["gap_status"] in valid_statuses

    def test_custom_suppressions(self):
        custom_sups = [3.0, 4.0, 5.0]
        result = quantum_corrected_cl_peaks(
            z_phi=4.0, suppressions_classical=custom_sups
        )
        assert len(result) == 3
        assert abs(result[0]["ratio_quantum_to_lcdm"] - 4.0 / 3.0) < 1e-10

    def test_high_z_phi_overshoots(self):
        # Z_φ > suppression → ratio > 1 (overshoot)
        result = quantum_corrected_cl_peaks(z_phi=10.0)
        for peak in result:
            assert peak["ratio_quantum_to_lcdm"] > 1.0

    def test_low_z_phi_undershoots(self):
        # Z_φ < suppression → ratio < 1 (undershoot)
        result = quantum_corrected_cl_peaks(z_phi=1.0)
        for peak in result:
            assert peak["ratio_quantum_to_lcdm"] < 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# Section 9 — quantum_power_spectrum()
# ═══════════════════════════════════════════════════════════════════════════════

class TestQuantumPowerSpectrum:
    def test_returns_dict(self):
        k_vals = [0.01, 0.05, 0.1]
        result = quantum_power_spectrum(k_vals)
        assert isinstance(result, dict)

    def test_required_keys(self):
        k_vals = [0.01, 0.05, 0.1]
        result = quantum_power_spectrum(k_vals)
        for key in ("k_vals", "P_classical", "P_quantum", "Z_phi", "n_s", "A_s", "note_cobe"):
            assert key in result, f"Missing key: {key}"

    def test_p_quantum_equals_z_phi_times_p_classical(self):
        k_vals = [0.001, 0.01, 0.05, 0.1, 0.5]
        result = quantum_power_spectrum(k_vals, z_phi=5.0)
        for pc, pq in zip(result["P_classical"], result["P_quantum"]):
            assert abs(pq - 5.0 * pc) < 1e-20

    def test_p_classical_at_pivot_equals_as(self):
        k_vals = [K_PIVOT_MPC]
        result = quantum_power_spectrum(k_vals, A_s=A_S_PLANCK, n_s=N_S_UM)
        assert abs(result["P_classical"][0] - A_S_PLANCK) < 1e-20

    def test_p_classical_red_tilt(self):
        # n_s < 1 → power decreases with k
        k_vals = [0.01, 0.05, 0.1]
        result = quantum_power_spectrum(k_vals, n_s=0.96)
        p_cl = result["P_classical"]
        assert p_cl[0] > p_cl[1] > p_cl[2]

    def test_p_quantum_always_greater_than_classical(self):
        k_vals = [0.001, 0.01, 0.1]
        result = quantum_power_spectrum(k_vals)
        for pc, pq in zip(result["P_classical"], result["P_quantum"]):
            assert pq > pc

    def test_z_phi_recorded_correctly(self):
        k_vals = [0.05]
        result = quantum_power_spectrum(k_vals, z_phi=7.0)
        assert abs(result["Z_phi"] - 7.0) < 1e-12

    def test_note_cobe_present(self):
        k_vals = [0.05]
        result = quantum_power_spectrum(k_vals)
        assert isinstance(result["note_cobe"], str)
        assert len(result["note_cobe"]) > 20

    def test_output_length_matches_input(self):
        k_vals = list(range(1, 11))
        result = quantum_power_spectrum(k_vals)
        assert len(result["P_classical"]) == 10
        assert len(result["P_quantum"]) == 10


# ═══════════════════════════════════════════════════════════════════════════════
# Section 10 — quantum_boltzmann_source_correction()
# ═══════════════════════════════════════════════════════════════════════════════

class TestQuantumBoltzmannSourceCorrection:
    def test_returns_dict(self):
        result = quantum_boltzmann_source_correction()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = quantum_boltzmann_source_correction()
        for key in ("Z_phi", "Z_phi_half", "ell_vals", "source_data", "physics"):
            assert key in result, f"Missing key: {key}"

    def test_z_phi_half_equals_sqrt_z_phi(self):
        result = quantum_boltzmann_source_correction(z_phi=9.0)
        assert abs(result["Z_phi_half"] - 3.0) < 1e-10

    def test_s_quantum_greater_than_s_classical(self):
        result = quantum_boltzmann_source_correction()
        for mode in result["source_data"]:
            assert mode["S_quantum"] > mode["S_classical"]

    def test_cl_ratio_quantum_greater_than_classical(self):
        result = quantum_boltzmann_source_correction()
        for mode in result["source_data"]:
            assert mode["Cl_ratio_quantum"] > mode["Cl_ratio_classical"]

    def test_default_ell_vals(self):
        result = quantum_boltzmann_source_correction()
        ell_vals = result["ell_vals"]
        assert 220 in ell_vals or len(ell_vals) >= 4  # Default has ≥ 4 ells

    def test_custom_ell_vals(self):
        result = quantum_boltzmann_source_correction(ell_vals=[200, 400, 800])
        assert result["ell_vals"] == [200, 400, 800]
        assert len(result["source_data"]) == 3

    def test_source_data_ell_ordering(self):
        result = quantum_boltzmann_source_correction()
        ells = [m["ell"] for m in result["source_data"]]
        assert ells == sorted(ells)

    def test_physics_string_present(self):
        result = quantum_boltzmann_source_correction()
        assert isinstance(result["physics"], str)
        assert len(result["physics"]) > 30


# ═══════════════════════════════════════════════════════════════════════════════
# Section 11 — residual_gap_after_quantum_correction()
# ═══════════════════════════════════════════════════════════════════════════════

class TestResidualGapAfterQuantumCorrection:
    def test_returns_dict(self):
        result = residual_gap_after_quantum_correction()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = residual_gap_after_quantum_correction()
        for key in ("Z_phi", "Z_phi_half", "classical_suppressions",
                    "residual_ratios", "mean_residual", "max_residual",
                    "classical_mean_gap", "gap_reduction_factor",
                    "gap_closed_within", "pct_residuals", "summary"):
            assert key in result, f"Missing key: {key}"

    def test_z_phi_recorded(self):
        result = residual_gap_after_quantum_correction(z_phi=5.0)
        assert abs(result["Z_phi"] - 5.0) < 1e-12

    def test_z_phi_half_sqrt(self):
        result = residual_gap_after_quantum_correction(z_phi=4.0)
        assert abs(result["Z_phi_half"] - 2.0) < 1e-10

    def test_residual_ratios_length(self):
        result = residual_gap_after_quantum_correction()
        assert len(result["residual_ratios"]) == 3

    def test_residual_ratios_formula(self):
        sups = [4.2, 5.0, 6.1]
        z = Z_PHI_CANONICAL
        result = residual_gap_after_quantum_correction(z_phi=z, suppressions_classical=sups)
        for i, (r, s) in enumerate(zip(result["residual_ratios"], sups)):
            assert abs(r - z / s) < 1e-10

    def test_mean_residual_less_than_max_residual(self):
        result = residual_gap_after_quantum_correction()
        assert result["mean_residual"] <= result["max_residual"]

    def test_mean_residual_positive(self):
        result = residual_gap_after_quantum_correction()
        assert result["mean_residual"] >= 0

    def test_classical_mean_gap_in_range_4_to_7(self):
        result = residual_gap_after_quantum_correction()
        assert 4.0 < result["classical_mean_gap"] < 7.0

    def test_gap_reduction_factor_large(self):
        # Z_φ should substantially reduce the gap
        result = residual_gap_after_quantum_correction()
        # classical_mean / mean_residual should be >> 1
        assert result["gap_reduction_factor"] > 5.0

    def test_gap_closed_within_label_valid(self):
        result = residual_gap_after_quantum_correction()
        valid = {
            "CLOSED_WITHIN_15_PCT",
            "SUBSTANTIALLY_CLOSED_WITHIN_30_PCT",
            "PARTIALLY_CLOSED",
        }
        assert result["gap_closed_within"] in valid

    def test_substantially_closed_with_canonical_z_phi(self):
        result = residual_gap_after_quantum_correction(z_phi=Z_PHI_CANONICAL)
        # With Z_φ ≈ 5.30, max residual ≈ 26% → SUBSTANTIALLY_CLOSED
        assert "CLOSED" in result["gap_closed_within"]

    def test_pct_residuals_length_three(self):
        result = residual_gap_after_quantum_correction()
        assert len(result["pct_residuals"]) == 3

    def test_summary_string_present(self):
        result = residual_gap_after_quantum_correction()
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 30

    def test_perfect_z_phi_gives_zero_residual(self):
        # If Z_φ exactly equals the suppression, residual = 0
        s = [5.0, 5.0, 5.0]
        result = residual_gap_after_quantum_correction(z_phi=5.0, suppressions_classical=s)
        assert abs(result["mean_residual"]) < 1e-12

    def test_custom_suppressions(self):
        custom_sups = [2.0, 3.0, 4.0]
        result = residual_gap_after_quantum_correction(
            z_phi=3.0, suppressions_classical=custom_sups
        )
        assert len(result["classical_suppressions"]) == 3
        assert abs(result["residual_ratios"][0] - 1.5) < 1e-10
        assert abs(result["residual_ratios"][1] - 1.0) < 1e-10
        assert abs(result["residual_ratios"][2] - 0.75) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# Section 12 — frontier_roadmap()
# ═══════════════════════════════════════════════════════════════════════════════

class TestFrontierRoadmap:
    def test_returns_dict(self):
        result = frontier_roadmap()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = frontier_roadmap()
        for key in ("pillar", "Z_phi_computed", "gap_substantially_closed",
                    "mean_residual_pct", "frontier_items", "horizon_completion"):
            assert key in result, f"Missing key: {key}"

    def test_pillar_number(self):
        result = frontier_roadmap()
        assert result["pillar"] == 355

    def test_z_phi_computed_true(self):
        result = frontier_roadmap()
        assert result["Z_phi_computed"] is True

    def test_gap_substantially_closed_true(self):
        result = frontier_roadmap()
        assert result["gap_substantially_closed"] is True

    def test_mean_residual_pct_positive(self):
        result = frontier_roadmap()
        assert result["mean_residual_pct"] > 0

    def test_frontier_items_list(self):
        result = frontier_roadmap()
        assert isinstance(result["frontier_items"], list)
        assert len(result["frontier_items"]) >= 4

    def test_frontier_items_have_id(self):
        result = frontier_roadmap()
        for item in result["frontier_items"]:
            assert "id" in item
            assert "description" in item
            assert "status" in item

    def test_frontier_items_have_open_or_future_status(self):
        result = frontier_roadmap()
        valid_statuses = {"OPEN", "FUTURE_EXPERIMENT", "COMPLETE"}
        for item in result["frontier_items"]:
            assert item["status"] in valid_statuses

    def test_boltzmann_solver_in_frontier(self):
        result = frontier_roadmap()
        descriptions = " ".join(item["description"].lower() for item in result["frontier_items"])
        assert "boltzmann" in descriptions

    def test_litebird_in_frontier(self):
        result = frontier_roadmap()
        descriptions = " ".join(item["description"].lower() for item in result["frontier_items"])
        assert "litebird" in descriptions or "birefringence" in descriptions

    def test_horizon_completion_string(self):
        result = frontier_roadmap()
        assert isinstance(result["horizon_completion"], str)
        assert len(result["horizon_completion"]) > 50


# ═══════════════════════════════════════════════════════════════════════════════
# Section 13 — pillar355_summary()
# ═══════════════════════════════════════════════════════════════════════════════

class TestPillar355Summary:
    def test_returns_dict(self):
        result = pillar355_summary()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = pillar355_summary()
        for key in ("pillar", "title", "status", "closure_type",
                    "wavefunction_renormalization", "one_loop_interpretation",
                    "peak_corrections", "residual_gap", "kk_tower_analysis",
                    "zero_point_info", "frontier_roadmap", "key_results",
                    "fallibility_md_update", "pillar_references"):
            assert key in result, f"Missing key: {key}"

    def test_pillar_number_355(self):
        result = pillar355_summary()
        assert result["pillar"] == 355

    def test_title_contains_second_quantization(self):
        result = pillar355_summary()
        title = result["title"].lower()
        assert "second quantization" in title or "quantization" in title

    def test_key_results_z_phi_canonical(self):
        result = pillar355_summary()
        expected = 1.0 + math.sqrt(74) / 2.0
        assert abs(result["key_results"]["Z_phi"] - expected) < 1e-10

    def test_key_results_z_phi_half_in_range(self):
        result = pillar355_summary()
        z_half = result["key_results"]["Z_phi_half"]
        assert 2.0 <= z_half <= 2.6

    def test_key_results_in_predicted_range(self):
        result = pillar355_summary()
        assert result["key_results"]["Z_phi_half_in_predicted_range"] is True

    def test_key_results_gap_reduction_factor(self):
        result = pillar355_summary()
        assert result["key_results"]["gap_reduction_factor"] > 5.0

    def test_key_results_classical_mean_suppression(self):
        result = pillar355_summary()
        # Classical suppression mean ≈ (4.2 + 5.0 + 6.1)/3 ≈ 5.1
        assert 4.0 < result["key_results"]["classical_mean_suppression"] < 7.0

    def test_peak_corrections_is_list_of_3(self):
        result = pillar355_summary()
        assert isinstance(result["peak_corrections"], list)
        assert len(result["peak_corrections"]) == 3

    def test_pillar_references_list_nonempty(self):
        result = pillar355_summary()
        refs = result["pillar_references"]
        assert isinstance(refs, list)
        assert len(refs) >= 3

    def test_fallibility_update_string(self):
        result = pillar355_summary()
        update = result["fallibility_md_update"]
        assert isinstance(update, str)
        assert "Pillar 355" in update
        assert "Z_φ" in update or "Z_phi" in update

    def test_status_string_contains_closed(self):
        result = pillar355_summary()
        assert "CLOSED" in result["status"] or "closed" in result["status"].lower()

    def test_closure_type_valid(self):
        result = pillar355_summary()
        ct = result["closure_type"]
        assert "CLOSED" in ct or "PARTIALLY" in ct

    def test_wfr_sub_report_present(self):
        result = pillar355_summary()
        wfr = result["wavefunction_renormalization"]
        assert "Z_phi" in wfr

    def test_one_loop_interpretation_sub_report(self):
        result = pillar355_summary()
        oli = result["one_loop_interpretation"]
        assert "F_KK" in oli

    def test_residual_gap_sub_report(self):
        result = pillar355_summary()
        rg = result["residual_gap"]
        assert "mean_residual" in rg


# ═══════════════════════════════════════════════════════════════════════════════
# Section 14 — Cross-function consistency
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrossFunctionConsistency:
    def test_z_phi_consistent_across_functions(self):
        """Z_φ should be identical across all functions using canonical params."""
        z_wfr = zphi_wavefunction_renormalization()["Z_phi"]
        z_oli = zphi_one_loop_interpretation()["Z_phi"]
        z_tower = kk_tower_zphi_contribution()["Z_phi_zero_mode"]
        expected = 1.0 + math.sqrt(74) / 2.0
        assert abs(z_wfr - expected) < 1e-10
        assert abs(z_oli - expected) < 1e-10
        assert abs(z_tower - expected) < 1e-10

    def test_z_phi_canonical_module_constant_consistent(self):
        """Module constant Z_PHI_CANONICAL agrees with computed value."""
        z_computed = zphi_wavefunction_renormalization()["Z_phi"]
        assert abs(Z_PHI_CANONICAL - z_computed) < 1e-10

    def test_z_phi_half_consistent(self):
        """Z_φ^{1/2} from wfr function equals sqrt of Z_φ."""
        wfr = zphi_wavefunction_renormalization()
        assert abs(wfr["Z_phi_half"] - math.sqrt(wfr["Z_phi"])) < 1e-10

    def test_residual_gap_uses_canonical_z_phi(self):
        """Residual gap with canonical Z_φ matches direct peak correction."""
        res = residual_gap_after_quantum_correction(z_phi=Z_PHI_CANONICAL)
        peaks = quantum_corrected_cl_peaks(z_phi=Z_PHI_CANONICAL)
        for i, (r, peak) in enumerate(zip(res["residual_ratios"], peaks)):
            assert abs(r - peak["ratio_quantum_to_lcdm"]) < 1e-10

    def test_zero_point_variance_consistent_with_wfr(self):
        """Zero-point variance from zp function feeds into wfr correctly."""
        zp = radion_zero_point_variance()
        wfr = zphi_wavefunction_renormalization()
        # Z_φ = 1 + ε_quantum = 1 + zp_variance/phi0²
        expected_z = 1.0 + zp["epsilon_quantum"]
        assert abs(wfr["Z_phi"] - expected_z) < 1e-10

    def test_frontier_mean_residual_consistent(self):
        """Frontier roadmap mean residual % matches residual_gap function."""
        road = frontier_roadmap()
        res = residual_gap_after_quantum_correction()
        assert abs(road["mean_residual_pct"] - res["mean_residual"] * 100.0) < 0.1

    def test_kk_tower_zero_mode_equals_standalone_z_phi(self):
        """kk_tower_zphi_contribution zero-mode Z_φ equals standalone formula."""
        tower = kk_tower_zphi_contribution()
        standalone = zphi_wavefunction_renormalization()
        assert abs(tower["Z_phi_zero_mode"] - standalone["Z_phi"]) < 1e-10

    def test_summary_key_results_consistent(self):
        """Summary key results are consistent with individual function outputs."""
        summary = pillar355_summary()
        wfr = zphi_wavefunction_renormalization()
        assert abs(summary["key_results"]["Z_phi"] - wfr["Z_phi"]) < 1e-10
        assert abs(summary["key_results"]["Z_phi_half"] - wfr["Z_phi_half"]) < 1e-10


# ═══════════════════════════════════════════════════════════════════════════════
# Section 15 — Physical constraints
# ═══════════════════════════════════════════════════════════════════════════════

class TestPhysicalConstraints:
    def test_z_phi_greater_than_one(self):
        """Z_φ must be > 1 (quantum correction must be additive)."""
        assert Z_PHI_CANONICAL > 1.0

    def test_z_phi_finite(self):
        """Z_φ must be finite for all reasonable φ₀ > 0."""
        for phi0 in [0.1, 0.5, 1.0, 2.0, 10.0]:
            wfr = zphi_wavefunction_renormalization(phi0=phi0)
            assert math.isfinite(wfr["Z_phi"])
            assert wfr["Z_phi"] > 0

    def test_zp_variance_positive_for_positive_omega(self):
        """Zero-point variance ⟨δφ²⟩₀ = 1/(2ω_φ) must be positive."""
        result = radion_zero_point_variance()
        assert result["zp_variance"] > 0

    def test_z_phi_monotone_in_k_cs(self):
        """Z_φ increases monotonically with K_CS (more braid → larger correction)."""
        z_vals = []
        for k_cs in [50, 60, 70, 74, 80, 90]:
            wfr = zphi_wavefunction_renormalization(k_cs=k_cs)
            z_vals.append(wfr["Z_phi"])
        for i in range(len(z_vals) - 1):
            assert z_vals[i] < z_vals[i + 1]

    def test_z_phi_monotone_decreasing_in_phi0(self):
        """Z_φ decreases with φ₀ (larger vev → smaller relative fluctuation)."""
        z_vals = []
        for phi0 in [0.5, 1.0, 1.5, 2.0, 3.0]:
            wfr = zphi_wavefunction_renormalization(phi0=phi0)
            z_vals.append(wfr["Z_phi"])
        for i in range(len(z_vals) - 1):
            assert z_vals[i] > z_vals[i + 1]

    def test_z_phi_approaches_correct_limit_at_large_k_cs(self):
        """For large K_CS, Z_φ ≈ 1 + √K_CS/2 (exact formula)."""
        for k_cs in [100, 200, 400]:
            wfr = zphi_wavefunction_renormalization(k_cs=k_cs)
            expected = 1.0 + math.sqrt(k_cs) / 2.0
            assert abs(wfr["Z_phi"] - expected) < 1e-10

    def test_quantum_spectrum_positive_everywhere(self):
        """Quantum power spectrum must be positive for all k > 0."""
        k_vals = [0.001, 0.01, 0.05, 0.1, 0.5, 1.0]
        result = quantum_power_spectrum(k_vals)
        for p in result["P_quantum"]:
            assert p > 0

    def test_classical_spectrum_positive_everywhere(self):
        """Classical power spectrum must be positive for all k > 0."""
        k_vals = [0.001, 0.01, 0.05, 0.1, 0.5, 1.0]
        result = quantum_power_spectrum(k_vals)
        for p in result["P_classical"]:
            assert p > 0

    def test_gap_identified_at_acoustic_peaks(self):
        """Z_φ must account for ≥ 50% of the classical gap at all peaks."""
        peaks = quantum_corrected_cl_peaks(z_phi=Z_PHI_CANONICAL)
        classical_sups = [
            SUPPRESSION_PEAK1_CLASSICAL,
            SUPPRESSION_PEAK2_CLASSICAL,
            SUPPRESSION_PEAK3_CLASSICAL,
        ]
        for peak, s_i in zip(peaks, classical_sups):
            # After quantum correction, ratio to ΛCDM should be > 50%
            assert peak["ratio_quantum_to_lcdm"] > 0.5
            # And less than 2× (not wildly overshooting)
            assert peak["ratio_quantum_to_lcdm"] < 2.0

    def test_fock_space_energy_sum_convergent_at_large_n(self):
        """Fock space zero-point energy sum converges well past the braided peak."""
        # The peak of e0_n is at n* ≈ sqrt(K_CS/2) ≈ 6. For n >> n*,
        # the Gaussian weight exp(-n²/K_CS) ensures rapid convergence.
        # Compare n_max=80 vs n_max=100: additional contribution < 1%.
        r80 = fock_space_zero_point_energy(n_max=80)
        r100 = fock_space_zero_point_energy(n_max=100)
        relative_change = abs(r100["E0_total"] - r80["E0_total"]) / r80["E0_total"]
        assert relative_change < 0.01

    def test_omega_phi_equals_one_over_sqrt_74(self):
        """Canonical ω_φ = 1/√74 (from phi_radion_quantization.py)."""
        result = radion_zero_point_variance()
        assert abs(result["omega_phi"] - 1.0 / math.sqrt(74)) < 1e-10

    def test_problem_statement_range_is_satisfied(self):
        """Z_φ^{1/2} ∈ [2.0, 2.6] as stated in the problem."""
        z_half = Z_PHI_HALF_CANONICAL
        assert z_half >= 2.0, f"Z_φ^{{1/2}} = {z_half:.4f} < 2.0"
        assert z_half <= 2.6, f"Z_φ^{{1/2}} = {z_half:.4f} > 2.6"

    def test_problem_statement_gap_range_is_satisfied(self):
        """Z_φ ∈ [4, 7] corresponding to the CMB amplitude gap."""
        assert 4.0 <= Z_PHI_CANONICAL <= 7.0, (
            f"Z_φ = {Z_PHI_CANONICAL:.4f} not in [4, 7]"
        )
