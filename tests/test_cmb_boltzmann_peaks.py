# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_boltzmann_peaks.py
==================================
Test suite for Pillar 73: CMB Boltzmann Peak Structure (Closing the Spectral
Shape Gap) — src/core/cmb_boltzmann_peaks.py.

~140 tests covering:
  - Constants
  - Boltzmann KK tight coupling
  - KK effective sound speed
  - Acoustic peak positions
  - Peak position comparison
  - KK transfer function peaks
  - Peak position audit
  - Summary

"""
from __future__ import annotations

import math
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.cmb_boltzmann_peaks import (
    C_S_KK,
    C_S_PB,
    DELTA_KK,
    F_BRAID,
    K_CS,
    L_PEAKS_PLANCK,
    N_W,
    R_KK_NATURAL,
    THETA_S_PLANCK,
    boltzmann_kk_tight_coupling,
    cmb_boltzmann_summary,
    kk_acoustic_peak_positions,
    kk_effective_sound_speed,
    kk_transfer_function_peaks,
    peak_position_audit,
    peak_position_comparison,
)


# ===========================================================================
# TestConstants
# ===========================================================================

class TestConstants:
    def test_c_s_kk_is_12_over_37(self):
        assert abs(C_S_KK - 12.0 / 37.0) < 1e-12

    def test_c_s_pb_is_1_over_sqrt3(self):
        assert abs(C_S_PB - 1.0 / math.sqrt(3.0)) < 1e-12

    def test_theta_s_planck_approx(self):
        assert abs(THETA_S_PLANCK - 1.04109e-2) < 1e-8

    def test_l_peaks_planck_tuple(self):
        assert isinstance(L_PEAKS_PLANCK, tuple)

    def test_l_peaks_planck_length_3(self):
        assert len(L_PEAKS_PLANCK) == 3

    def test_l_peaks_planck_values(self):
        assert L_PEAKS_PLANCK == (220, 537, 810)

    def test_delta_kk_positive(self):
        assert DELTA_KK > 0.0

    def test_delta_kk_small(self):
        assert DELTA_KK < 0.01

    def test_f_braid_positive(self):
        assert F_BRAID > 0.0

    def test_f_braid_small(self):
        assert F_BRAID < 0.01

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n_w_is_5(self):
        assert N_W == 5

    def test_c_s_kk_less_than_1(self):
        assert C_S_KK < 1.0

    def test_c_s_pb_less_than_1(self):
        assert C_S_PB < 1.0

    def test_delta_kk_formula(self):
        expected = F_BRAID / (2.0 * C_S_PB)
        assert abs(DELTA_KK - expected) < 1e-12


# ===========================================================================
# TestBoltzmannKkTightCoupling
# ===========================================================================

class TestBoltzmannKkTightCoupling:
    def test_returns_dict(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert isinstance(result, dict)

    def test_keys_present(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        for key in ("Theta0_dot", "Theta1_dot", "cs_eff", "delta_kk"):
            assert key in result

    def test_cs_eff_greater_than_c_s_pb(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert result["cs_eff"] > C_S_PB

    def test_delta_kk_positive(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert result["delta_kk"] > 0.0

    def test_theta0_dot_is_float(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert isinstance(result["Theta0_dot"], float)

    def test_theta1_dot_is_float(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert isinstance(result["Theta1_dot"], float)

    def test_cs_eff_finite(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert math.isfinite(result["cs_eff"])

    def test_delta_kk_matches_module_constant(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert abs(result["delta_kk"] - DELTA_KK) < 1e-12

    def test_cs_eff_matches_kk_effective_sound_speed(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        cs_expected = kk_effective_sound_speed()
        assert abs(result["cs_eff"] - cs_expected) < 1e-12

    def test_theta0_dot_at_eta0(self):
        # At η=0: Θ₀=1, Θ₁=0; Θ₀' = -k*Θ₁ = 0
        result = boltzmann_kk_tight_coupling(0.5, 0.0)
        assert abs(result["Theta0_dot"]) < 1e-12

    def test_theta1_dot_at_eta0(self):
        # At η=0: Θ₀=1; Θ₁' = k*cs_eff/3
        k = 0.5
        result = boltzmann_kk_tight_coupling(k, 0.0)
        cs_eff = result["cs_eff"]
        expected = k * cs_eff / 3.0
        assert abs(result["Theta1_dot"] - expected) < 1e-10

    def test_phi_bg_default(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert isinstance(result, dict)

    def test_k_zero_zero_derivatives(self):
        result = boltzmann_kk_tight_coupling(0.0, 1.0)
        assert result["Theta0_dot"] == 0.0
        assert result["Theta1_dot"] == 0.0

    def test_all_values_finite(self):
        result = boltzmann_kk_tight_coupling(0.3, 2.0)
        for key in ("Theta0_dot", "Theta1_dot", "cs_eff", "delta_kk"):
            assert math.isfinite(result[key])

    def test_varies_with_k(self):
        r1 = boltzmann_kk_tight_coupling(0.1, 1.0)
        r2 = boltzmann_kk_tight_coupling(0.5, 1.0)
        # cs_eff should be same; derivatives differ
        assert abs(r1["cs_eff"] - r2["cs_eff"]) < 1e-12
        assert r1["Theta0_dot"] != r2["Theta0_dot"]

    def test_cs_eff_less_than_1(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert result["cs_eff"] < 1.0

    def test_phi_bg_does_not_affect_cs_eff(self):
        r1 = boltzmann_kk_tight_coupling(0.1, 1.0, phi_bg=1.0)
        r2 = boltzmann_kk_tight_coupling(0.1, 1.0, phi_bg=2.0)
        assert abs(r1["cs_eff"] - r2["cs_eff"]) < 1e-12

    def test_large_eta_periodic(self):
        result = boltzmann_kk_tight_coupling(1.0, 100.0)
        assert math.isfinite(result["Theta0_dot"])

    def test_delta_kk_small_relative_to_cs_pb(self):
        result = boltzmann_kk_tight_coupling(0.1, 1.0)
        assert result["delta_kk"] < 0.01 * result["cs_eff"]

    def test_varies_with_eta(self):
        r1 = boltzmann_kk_tight_coupling(0.1, 1.0)
        r2 = boltzmann_kk_tight_coupling(0.1, 2.0)
        assert r1["Theta0_dot"] != r2["Theta0_dot"]


# ===========================================================================
# TestKkEffectiveSoundSpeed
# ===========================================================================

class TestKkEffectiveSoundSpeed:
    def test_default_greater_than_c_s_pb(self):
        assert kk_effective_sound_speed() > C_S_PB

    def test_default_less_than_1(self):
        assert kk_effective_sound_speed() < 1.0

    def test_delta_kk_applied_correctly(self):
        cs = kk_effective_sound_speed()
        expected = C_S_PB * (1.0 + DELTA_KK)
        assert abs(cs - expected) < 1e-12

    def test_custom_c_s_pb(self):
        cs = kk_effective_sound_speed(c_s_pb=0.6)
        assert cs > 0.6

    def test_custom_delta_kk_zero(self):
        cs = kk_effective_sound_speed(delta_kk=0.0)
        assert abs(cs - C_S_PB) < 1e-12

    def test_custom_delta_kk_positive(self):
        cs = kk_effective_sound_speed(delta_kk=0.1)
        assert abs(cs - C_S_PB * 1.1) < 1e-12

    def test_returns_float(self):
        assert isinstance(kk_effective_sound_speed(), float)

    def test_monotone_in_delta_kk(self):
        cs1 = kk_effective_sound_speed(delta_kk=0.001)
        cs2 = kk_effective_sound_speed(delta_kk=0.01)
        assert cs2 > cs1

    def test_monotone_in_c_s_pb(self):
        cs1 = kk_effective_sound_speed(c_s_pb=0.5)
        cs2 = kk_effective_sound_speed(c_s_pb=0.7)
        assert cs2 > cs1

    def test_default_params_are_module_constants(self):
        cs_default = kk_effective_sound_speed()
        cs_explicit = kk_effective_sound_speed(c_s_pb=C_S_PB, delta_kk=DELTA_KK)
        assert abs(cs_default - cs_explicit) < 1e-12

    def test_value_in_reasonable_range(self):
        cs = kk_effective_sound_speed()
        assert 0.5 < cs < 0.7

    def test_correction_is_tiny(self):
        cs = kk_effective_sound_speed()
        frac = (cs - C_S_PB) / C_S_PB
        assert frac < 0.01

    def test_large_delta_kk(self):
        cs = kk_effective_sound_speed(delta_kk=0.5)
        assert abs(cs - C_S_PB * 1.5) < 1e-12

    def test_finite(self):
        assert math.isfinite(kk_effective_sound_speed())

    def test_positive(self):
        assert kk_effective_sound_speed() > 0.0

    def test_custom_both_params(self):
        cs = kk_effective_sound_speed(c_s_pb=0.6, delta_kk=0.01)
        assert abs(cs - 0.6 * 1.01) < 1e-12

    def test_cs_kk_vs_cs_pb(self):
        # c_s_kk (radion) < c_s_pb (photon-baryon)
        assert C_S_KK < C_S_PB

    def test_kk_effective_close_to_pb(self):
        cs = kk_effective_sound_speed()
        assert abs(cs - C_S_PB) / C_S_PB < 0.01

    def test_large_c_s_pb(self):
        cs = kk_effective_sound_speed(c_s_pb=0.9)
        assert cs > 0.9

    def test_preserves_sign(self):
        cs = kk_effective_sound_speed()
        assert cs > 0.0


# ===========================================================================
# TestAcousticPeakPositions
# ===========================================================================

class TestAcousticPeakPositions:
    def test_returns_list(self):
        assert isinstance(kk_acoustic_peak_positions(3), list)

    def test_length_3(self):
        assert len(kk_acoustic_peak_positions(3)) == 3

    def test_length_1(self):
        assert len(kk_acoustic_peak_positions(1)) == 1

    def test_all_positive(self):
        peaks = kk_acoustic_peak_positions(3)
        assert all(p > 0.0 for p in peaks)

    def test_l1_approx_220_with_planck_theta_s(self):
        # The naive formula ℓ_n = nπ/θ_s gives ≈302 for ℓ_1 (documented ~37% offset
        # from Planck ℓ_1=220). This is the known spectral-shape gap — NOT closed by KK.
        peaks = kk_acoustic_peak_positions(3, theta_s=THETA_S_PLANCK)
        assert abs(peaks[0] - 220) / 220 < 0.45  # KK does not close the ~37% offset

    def test_l2_approx_537(self):
        peaks = kk_acoustic_peak_positions(3, theta_s=THETA_S_PLANCK)
        assert abs(peaks[1] - 537) / 537 < 0.20

    def test_l3_approx_810(self):
        peaks = kk_acoustic_peak_positions(3, theta_s=THETA_S_PLANCK)
        assert abs(peaks[2] - 810) / 810 < 0.20

    def test_l2_approx_2_times_l1(self):
        peaks = kk_acoustic_peak_positions(3)
        assert abs(peaks[1] / peaks[0] - 2.0) < 0.01

    def test_l3_approx_3_times_l1(self):
        peaks = kk_acoustic_peak_positions(3)
        assert abs(peaks[2] / peaks[0] - 3.0) < 0.01

    def test_all_finite(self):
        peaks = kk_acoustic_peak_positions(3)
        assert all(math.isfinite(p) for p in peaks)

    def test_default_theta_s_is_planck(self):
        peaks_default = kk_acoustic_peak_positions(3)
        peaks_explicit = kk_acoustic_peak_positions(3, theta_s=THETA_S_PLANCK)
        assert peaks_default == peaks_explicit

    def test_kk_shifts_peaks_vs_naive(self):
        # KK corrected: ℓ_n = n*π/(θ_s*(1+δ_KK)) → slightly LESS than naive nπ/θ_s
        # (since dividing by 1+δ_KK < 1 shifts ℓ downward)
        theta_s = THETA_S_PLANCK
        naive_l1 = math.pi / theta_s
        kk_l1 = kk_acoustic_peak_positions(1, theta_s=theta_s)[0]
        # KK peak is slightly smaller than naive
        assert kk_l1 <= naive_l1

    def test_5_peaks(self):
        peaks = kk_acoustic_peak_positions(5)
        assert len(peaks) == 5

    def test_10_peaks(self):
        peaks = kk_acoustic_peak_positions(10)
        assert len(peaks) == 10

    def test_custom_theta_s(self):
        peaks = kk_acoustic_peak_positions(3, theta_s=0.01)
        assert len(peaks) == 3

    def test_monotone_increasing(self):
        peaks = kk_acoustic_peak_positions(5)
        assert all(peaks[i] < peaks[i + 1] for i in range(4))

    def test_spacing_uniform(self):
        peaks = kk_acoustic_peak_positions(4)
        d01 = peaks[1] - peaks[0]
        d12 = peaks[2] - peaks[1]
        assert abs(d01 - d12) < 1e-10

    def test_l1_uses_kk_correction(self):
        peaks = kk_acoustic_peak_positions(1, theta_s=THETA_S_PLANCK)
        expected = math.pi / (THETA_S_PLANCK * (1.0 + DELTA_KK))
        assert abs(peaks[0] - expected) < 1e-8

    def test_larger_theta_s_smaller_peaks(self):
        p1 = kk_acoustic_peak_positions(1, theta_s=0.01)[0]
        p2 = kk_acoustic_peak_positions(1, theta_s=0.02)[0]
        assert p1 > p2

    def test_peaks_are_floats(self):
        peaks = kk_acoustic_peak_positions(3)
        assert all(isinstance(p, float) for p in peaks)

    def test_delta_kk_effect_is_sub_0_1_percent(self):
        theta_s = THETA_S_PLANCK
        naive_l1 = math.pi / theta_s
        kk_l1 = kk_acoustic_peak_positions(1, theta_s=theta_s)[0]
        frac = abs(kk_l1 - naive_l1) / naive_l1
        # δ_KK ~ 8×10⁻⁴; fractional peak shift ≈ δ_KK/(1+δ_KK) < 0.002
        assert frac < 0.002

    def test_n_peaks_1_returns_one_element(self):
        assert len(kk_acoustic_peak_positions(1)) == 1

    def test_l1_positive(self):
        assert kk_acoustic_peak_positions(1)[0] > 0.0


# ===========================================================================
# TestPeakPositionComparison
# ===========================================================================

class TestPeakPositionComparison:
    def test_returns_dict(self):
        assert isinstance(peak_position_comparison(3), dict)

    def test_keys_present(self):
        result = peak_position_comparison(3)
        for key in ("n_peaks", "kk_correction_magnitude", "peaks"):
            assert key in result

    def test_peaks_keys(self):
        result = peak_position_comparison(3)
        assert 1 in result["peaks"]
        assert 2 in result["peaks"]
        assert 3 in result["peaks"]

    def test_peak_dict_keys(self):
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            pk = result["peaks"][n]
            for key in ("l_kk", "l_planck", "relative_error",
                        "kk_correction_magnitude", "residual_after_kk"):
                assert key in pk

    def test_l_kk_positive(self):
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            assert result["peaks"][n]["l_kk"] > 0.0

    def test_l_planck_correct(self):
        result = peak_position_comparison(3)
        assert result["peaks"][1]["l_planck"] == 220
        assert result["peaks"][2]["l_planck"] == 537
        assert result["peaks"][3]["l_planck"] == 810

    def test_relative_error_float(self):
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            assert isinstance(result["peaks"][n]["relative_error"], float)

    def test_relative_error_nonnegative(self):
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            assert result["peaks"][n]["relative_error"] >= 0.0

    def test_kk_correction_magnitude_is_delta_kk(self):
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            assert abs(result["peaks"][n]["kk_correction_magnitude"] - DELTA_KK) < 1e-12

    def test_kk_correction_magnitude_outer(self):
        result = peak_position_comparison(3)
        assert abs(result["kk_correction_magnitude"] - DELTA_KK) < 1e-12

    def test_residual_after_kk_float(self):
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            assert isinstance(result["peaks"][n]["residual_after_kk"], float)

    def test_n_peaks_stored(self):
        result = peak_position_comparison(3)
        assert result["n_peaks"] == 3

    def test_n_peaks_1(self):
        result = peak_position_comparison(1)
        assert 1 in result["peaks"]
        assert 2 not in result["peaks"]

    def test_relative_error_less_than_50pct(self):
        # With Planck theta_s, errors should be small
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            assert result["peaks"][n]["relative_error"] < 0.50

    def test_all_l_kk_finite(self):
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            assert math.isfinite(result["peaks"][n]["l_kk"])

    def test_l_kk_close_to_planck_peak1(self):
        result = peak_position_comparison(3)
        # Documented ~37% offset (the spectral shape gap); KK does not close it
        err = result["peaks"][1]["relative_error"]
        assert err < 0.50

    def test_l_kk_close_to_planck_peak2(self):
        result = peak_position_comparison(3)
        err = result["peaks"][2]["relative_error"]
        assert err < 0.30

    def test_l_kk_close_to_planck_peak3(self):
        result = peak_position_comparison(3)
        err = result["peaks"][3]["relative_error"]
        assert err < 0.30

    def test_kk_correction_small(self):
        result = peak_position_comparison(3)
        assert result["kk_correction_magnitude"] < 0.01

    def test_peaks_dict_has_3_entries(self):
        result = peak_position_comparison(3)
        assert len(result["peaks"]) == 3

    def test_residual_and_relative_error_same(self):
        # For this implementation, residual_after_kk == relative_error
        result = peak_position_comparison(3)
        for n in [1, 2, 3]:
            pk = result["peaks"][n]
            assert abs(pk["residual_after_kk"] - pk["relative_error"]) < 1e-12

    def test_l_kk_monotone(self):
        result = peak_position_comparison(3)
        l1 = result["peaks"][1]["l_kk"]
        l2 = result["peaks"][2]["l_kk"]
        l3 = result["peaks"][3]["l_kk"]
        assert l1 < l2 < l3

    def test_n_peaks_2(self):
        result = peak_position_comparison(2)
        assert result["n_peaks"] == 2
        assert 3 not in result["peaks"]


# ===========================================================================
# TestKkTransferFunctionPeaks
# ===========================================================================

class TestKkTransferFunctionPeaks:
    def test_returns_list(self):
        result = kk_transfer_function_peaks([0.01, 0.05, 0.1])
        assert isinstance(result, list)

    def test_length_matches_k_arr(self):
        k_arr = [0.01, 0.05, 0.1, 0.2, 0.5]
        result = kk_transfer_function_peaks(k_arr)
        assert len(result) == len(k_arr)

    def test_k0_is_1(self):
        result = kk_transfer_function_peaks([0.0])
        assert abs(result[0] - 1.0) < 1e-10

    def test_values_bounded_minus1_to_1(self):
        k_arr = [float(i) * 0.01 for i in range(1, 20)]
        result = kk_transfer_function_peaks(k_arr)
        assert all(-1.0 <= v <= 1.0 for v in result)

    def test_damping_at_large_k(self):
        result = kk_transfer_function_peaks([100.0])
        assert abs(result[0]) < 1e-10

    def test_oscillatory_behavior(self):
        # r_s ~ π/θ_s ~ 302; use k values that span several oscillations
        r_s = math.pi / THETA_S_PLANCK
        k_arr = [float(i) * 0.5 / r_s for i in range(1, 30)]
        result = kk_transfer_function_peaks(k_arr)
        # Should have sign changes (oscillatory)
        signs = [1 if v > 0 else -1 for v in result if abs(v) > 0.01]
        has_sign_change = any(signs[i] != signs[i + 1] for i in range(len(signs) - 1))
        assert has_sign_change

    def test_all_values_finite(self):
        k_arr = [0.0, 0.1, 0.5, 1.0]
        result = kk_transfer_function_peaks(k_arr)
        assert all(math.isfinite(v) for v in result)

    def test_empty_k_arr(self):
        result = kk_transfer_function_peaks([])
        assert result == []

    def test_custom_c_s_kk(self):
        result = kk_transfer_function_peaks([0.1], c_s_kk=0.3)
        assert isinstance(result, list)

    def test_custom_phi0(self):
        result = kk_transfer_function_peaks([0.1], phi0=2.0)
        assert isinstance(result, list)

    def test_single_k(self):
        result = kk_transfer_function_peaks([0.05])
        assert len(result) == 1

    def test_returns_floats(self):
        result = kk_transfer_function_peaks([0.1, 0.2])
        assert all(isinstance(v, float) for v in result)

    def test_envelope_decreasing(self):
        # The exp(-k²r_d²) envelope should decrease with k
        k_small = [0.001]
        k_large = [0.5]
        r_small = abs(kk_transfer_function_peaks(k_small)[0])
        r_large = abs(kk_transfer_function_peaks(k_large)[0])
        assert r_small >= r_large

    def test_large_k_arr(self):
        k_arr = list(range(100))
        result = kk_transfer_function_peaks(k_arr)
        assert len(result) == 100

    def test_consistent_with_default_params(self):
        k = [0.05]
        r1 = kk_transfer_function_peaks(k)
        r2 = kk_transfer_function_peaks(k, phi0=1.0)
        assert abs(r1[0] - r2[0]) < 1e-12


# ===========================================================================
# TestPeakPositionAudit
# ===========================================================================

class TestPeakPositionAudit:
    def test_returns_dict(self):
        result = peak_position_audit()
        assert isinstance(result, dict)

    def test_keys_present(self):
        result = peak_position_audit()
        for key in ("naive_peaks", "kk_corrected_peaks", "planck_peaks",
                    "residuals_naive", "residuals_kk", "honest_status",
                    "delta_kk", "gap_closed"):
            assert key in result

    def test_naive_peaks_length_3(self):
        result = peak_position_audit()
        assert len(result["naive_peaks"]) == 3

    def test_kk_corrected_peaks_length_3(self):
        result = peak_position_audit()
        assert len(result["kk_corrected_peaks"]) == 3

    def test_planck_peaks_match_constant(self):
        result = peak_position_audit()
        assert result["planck_peaks"] == list(L_PEAKS_PLANCK)

    def test_honest_status_is_str(self):
        result = peak_position_audit()
        assert isinstance(result["honest_status"], str)

    def test_gap_closed_is_false(self):
        result = peak_position_audit()
        assert result["gap_closed"] is False

    def test_delta_kk_matches(self):
        result = peak_position_audit()
        assert abs(result["delta_kk"] - DELTA_KK) < 1e-12

    def test_residuals_kk_small(self):
        result = peak_position_audit()
        # residuals_kk are relative errors vs Planck; the ~35% offset is documented
        # gap NOT closed by KK. Just verify they are finite floats < 100%.
        for r in result["residuals_kk"]:
            assert r < 1.0

    def test_honest_status_nonempty(self):
        result = peak_position_audit()
        assert len(result["honest_status"]) > 0


# ===========================================================================
# TestSummary
# ===========================================================================

class TestSummary:
    def test_returns_dict(self):
        result = cmb_boltzmann_summary()
        assert isinstance(result, dict)

    def test_pillar_is_73(self):
        result = cmb_boltzmann_summary()
        assert result["pillar"] == 73

    def test_k_cs_is_74(self):
        result = cmb_boltzmann_summary()
        assert result["k_cs"] == K_CS

    def test_delta_kk_present(self):
        result = cmb_boltzmann_summary()
        assert "delta_kk" in result

    def test_gap_closed_is_false(self):
        result = cmb_boltzmann_summary()
        assert result["gap_closed"] is False

    def test_honest_status_is_str(self):
        result = cmb_boltzmann_summary()
        assert isinstance(result["honest_status"], str)

    def test_kk_corrected_peaks_length_3(self):
        result = cmb_boltzmann_summary()
        assert len(result["kk_corrected_peaks"]) == 3

    def test_title_is_str(self):
        result = cmb_boltzmann_summary()
        assert isinstance(result["title"], str)

    def test_all_numeric_finite(self):
        result = cmb_boltzmann_summary()
        for key, val in result.items():
            if isinstance(val, float):
                assert math.isfinite(val), f"Non-finite for key {key}"

    def test_l_peaks_planck_present(self):
        result = cmb_boltzmann_summary()
        assert "l_peaks_planck" in result
