# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_cmb_peaks.py
========================
Test suite for Pillar 57 — CMB Acoustic Peak Resolution (src/core/cmb_peaks.py).

"""
from __future__ import annotations

import math

import pytest

from src.core.cmb_peaks import (
    C_S,
    ELL_KK,
    ELL_REF,
    K_CS,
    N_WINDING,
    PHI_SLS,
    PHI_TODAY,
    RESOLUTION_THRESHOLD,
    acoustic_peak_correction,
    closure_summary,
    peak_suppression_factor,
    phi_ratio_sls_to_today,
    radion_amplified_spectrum,
    silk_damping_scale,
    suppression_audit,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestModuleConstants:
    def test_n_winding_default(self):
        assert N_WINDING == 5

    def test_k_cs_default(self):
        assert K_CS == 74

    def test_c_s_value(self):
        assert abs(C_S - 12 / 37) < 1e-12

    def test_phi_sls(self):
        assert PHI_SLS == 1.0

    def test_phi_today(self):
        assert abs(PHI_TODAY - 5 * 2 * math.pi) < 1e-10

    def test_ell_kk_approximate(self):
        # ℓ_KK = 74 × π / (12/37) ≈ 717
        expected = 74 * math.pi / (12 / 37)
        assert abs(ELL_KK - expected) < 0.5

    def test_ell_ref(self):
        assert ELL_REF == 10.0

    def test_resolution_threshold(self):
        assert RESOLUTION_THRESHOLD == 2.0


# ===========================================================================
# phi_ratio_sls_to_today
# ===========================================================================

class TestPhiRatioSlsToToday:
    def test_default_n5(self):
        ratio = phi_ratio_sls_to_today(5)
        assert abs(ratio - 5 * 2 * math.pi) < 1e-10

    def test_n5_approx_31_416(self):
        ratio = phi_ratio_sls_to_today(5)
        assert abs(ratio - 31.416) < 0.001

    def test_n1(self):
        ratio = phi_ratio_sls_to_today(1)
        assert abs(ratio - 2 * math.pi) < 1e-10

    def test_n3(self):
        ratio = phi_ratio_sls_to_today(3)
        assert abs(ratio - 6 * math.pi) < 1e-10

    def test_n7(self):
        ratio = phi_ratio_sls_to_today(7)
        assert abs(ratio - 14 * math.pi) < 1e-10

    def test_n10(self):
        ratio = phi_ratio_sls_to_today(10)
        assert abs(ratio - 20 * math.pi) < 1e-10

    def test_positive(self):
        for n in [1, 2, 5, 10, 20]:
            assert phi_ratio_sls_to_today(n) > 0

    def test_scales_linearly_with_n(self):
        r1 = phi_ratio_sls_to_today(1)
        r5 = phi_ratio_sls_to_today(5)
        assert abs(r5 - 5 * r1) < 1e-10

    def test_greater_than_one(self):
        # Every physical winding number ≥ 1 gives ratio > 1
        for n in [1, 2, 5]:
            assert phi_ratio_sls_to_today(n) > 1.0

    def test_n5_larger_than_n3(self):
        assert phi_ratio_sls_to_today(5) > phi_ratio_sls_to_today(3)


# ===========================================================================
# acoustic_peak_correction
# ===========================================================================

class TestAcousticPeakCorrection:
    def test_positive_everywhere_low_ell(self):
        for ell in [1, 2, 5, 10, 50, 100]:
            assert acoustic_peak_correction(ell) > 0

    def test_positive_everywhere_acoustic_peaks(self):
        for ell in [220, 540, 810, 1150, 1450, 1800, 2100]:
            assert acoustic_peak_correction(ell) > 0

    def test_positive_very_high_ell(self):
        for ell in [3000, 5000, 10000]:
            assert acoustic_peak_correction(ell) > 0

    def test_decreases_with_ell(self):
        # T_KK decreases with ℓ, so correction decreases
        c10 = acoustic_peak_correction(10)
        c1000 = acoustic_peak_correction(1000)
        c2500 = acoustic_peak_correction(2500)
        assert c10 > c1000 > c2500

    def test_equals_phi_ratio_at_ell0(self):
        # At ℓ → 0, T_KK → 1, so C → phi_ratio
        c_near_zero = acoustic_peak_correction(0.001)
        phi_r = phi_ratio_sls_to_today(5)
        assert abs(c_near_zero - phi_r) < 0.01

    def test_n_winding_dependence(self):
        c_n3 = acoustic_peak_correction(100, n_winding=3)
        c_n5 = acoustic_peak_correction(100, n_winding=5)
        assert c_n5 > c_n3

    def test_k_cs_dependence(self):
        # Larger k_cs → larger ℓ_KK → less suppression at fixed ℓ
        c_k74 = acoustic_peak_correction(500, k_cs=74)
        c_k100 = acoustic_peak_correction(500, k_cs=100)
        assert c_k100 > c_k74

    def test_at_ell_ref(self):
        # At ELL_REF=10, T_KK ≈ 1, so correction ≈ phi_ratio
        c = acoustic_peak_correction(ELL_REF)
        phi_r = phi_ratio_sls_to_today(5)
        lkk = K_CS * math.pi / C_S
        t_kk_ref = 1.0 / (1.0 + (ELL_REF / lkk) ** 2)
        expected = phi_r * t_kk_ref
        assert abs(c - expected) < 1e-8

    def test_monotone_decrease(self):
        ells = [10, 100, 500, 1000, 2000]
        corrections = [acoustic_peak_correction(e) for e in ells]
        for i in range(len(corrections) - 1):
            assert corrections[i] > corrections[i + 1]


# ===========================================================================
# peak_suppression_factor
# ===========================================================================

class TestPeakSuppressionFactor:
    def test_equals_one_at_ell_ref(self):
        f = peak_suppression_factor(ELL_REF)
        assert abs(f - 1.0) < 1e-12

    def test_at_ell_10_equals_one(self):
        f = peak_suppression_factor(10.0)
        assert abs(f - 1.0) < 1e-12

    def test_less_than_one_at_ell_1000(self):
        f = peak_suppression_factor(1000.0)
        assert f < 1.0

    def test_less_than_one_at_ell_2500(self):
        f = peak_suppression_factor(2500.0)
        assert f < 1.0

    def test_decreasing_with_ell(self):
        f10 = peak_suppression_factor(10)
        f100 = peak_suppression_factor(100)
        f1000 = peak_suppression_factor(1000)
        assert f10 > f100 > f1000

    def test_positive_everywhere(self):
        for ell in [1, 10, 100, 500, 1000, 2500]:
            assert peak_suppression_factor(ell) > 0

    def test_n_winding_invariant(self):
        # phi_ratio cancels in normalisation — result is n_winding-independent
        f_n3 = peak_suppression_factor(500, n_winding=3)
        f_n5 = peak_suppression_factor(500, n_winding=5)
        assert abs(f_n3 - f_n5) < 1e-10

    def test_at_large_ell_approaches_zero(self):
        f = peak_suppression_factor(100_000)
        assert f < 0.01

    def test_between_zero_and_one(self):
        for ell in [10, 100, 500, 1000]:
            f = peak_suppression_factor(ell)
            assert 0.0 < f <= 1.0 + 1e-12


# ===========================================================================
# suppression_audit
# ===========================================================================

class TestSuppressionAudit:
    def test_returns_dict(self):
        result = suppression_audit()
        assert isinstance(result, dict)

    def test_required_keys(self):
        keys = {
            "ells",
            "raw_suppression",
            "corrected_suppression",
            "residual_suppression",
            "peak_deficit_raw",
            "peak_deficit_corrected",
            "gap_closed_fraction",
        }
        result = suppression_audit()
        assert keys.issubset(result.keys())

    def test_ells_length(self):
        result = suppression_audit()
        n = len(result["ells"])
        assert len(result["raw_suppression"]) == n
        assert len(result["corrected_suppression"]) == n
        assert len(result["residual_suppression"]) == n

    def test_raw_suppression_ge_one(self):
        result = suppression_audit()
        for s in result["raw_suppression"]:
            assert s >= 1.0

    def test_corrected_lt_raw(self):
        result = suppression_audit()
        for raw, corr in zip(result["raw_suppression"], result["corrected_suppression"]):
            assert corr < raw

    def test_peak_deficit_corrected_lt_raw(self):
        result = suppression_audit()
        assert result["peak_deficit_corrected"] < result["peak_deficit_raw"]

    def test_peak_deficit_corrected_lt_2(self):
        result = suppression_audit()
        assert result["peak_deficit_corrected"] < RESOLUTION_THRESHOLD

    def test_gap_closed_fraction_positive(self):
        result = suppression_audit()
        assert result["gap_closed_fraction"] > 0.0

    def test_gap_closed_fraction_le_one(self):
        result = suppression_audit()
        assert result["gap_closed_fraction"] <= 1.0

    def test_custom_ells(self):
        ells = [100.0, 500.0, 1000.0]
        result = suppression_audit(ells=ells)
        assert result["ells"] == ells
        assert len(result["raw_suppression"]) == 3

    def test_single_ell(self):
        result = suppression_audit(ells=[220.0])
        assert len(result["raw_suppression"]) == 1

    def test_residual_equals_corrected(self):
        result = suppression_audit()
        assert result["residual_suppression"] == result["corrected_suppression"]

    def test_increasing_raw_suppression_at_higher_ell(self):
        # Higher ℓ → more suppression (T_KK smaller)
        result = suppression_audit(ells=[220.0, 1000.0, 2100.0])
        raw = result["raw_suppression"]
        assert raw[0] < raw[1] < raw[2]

    def test_n_winding_reduces_corrected(self):
        # Higher n_winding → larger phi_ratio → smaller corrected suppression
        r5 = suppression_audit(n_winding=5)
        r3 = suppression_audit(n_winding=3)
        assert r5["peak_deficit_corrected"] < r3["peak_deficit_corrected"]

    def test_ell_1_raw_close_to_one(self):
        # At ℓ=1, T_KK ≈ 1, raw_suppression ≈ 1
        result = suppression_audit(ells=[1.0])
        assert result["raw_suppression"][0] < 1.001

    def test_very_large_ell_raw_suppression_large(self):
        result = suppression_audit(ells=[5000.0])
        assert result["raw_suppression"][0] > 10.0


# ===========================================================================
# silk_damping_scale
# ===========================================================================

class TestSilkDampingScale:
    def test_positive(self):
        ld = silk_damping_scale()
        assert ld > 0

    def test_default_value_reasonable(self):
        # Should be in multipole range [50, 500]
        ld = silk_damping_scale()
        assert 50 < ld < 500

    def test_decreases_with_n_winding(self):
        # ℓ_D ∝ 1/√n_winding — larger n gives smaller ℓ_D
        ld3 = silk_damping_scale(n_winding=3)
        ld5 = silk_damping_scale(n_winding=5)
        assert ld3 > ld5

    def test_increases_with_k_cs(self):
        ld74 = silk_damping_scale(k_cs=74)
        ld100 = silk_damping_scale(k_cs=100)
        assert ld100 > ld74

    def test_formula(self):
        n, k = 5, 74
        expected = k * math.sqrt(n) * math.pi / (C_S * 2.0 * n)
        assert abs(silk_damping_scale(n, k) - expected) < 1e-10

    def test_n1(self):
        ld = silk_damping_scale(n_winding=1)
        expected = 74 * math.pi / (C_S * 2.0)
        assert abs(ld - expected) < 1e-8


# ===========================================================================
# radion_amplified_spectrum
# ===========================================================================

class TestRadionAmplifiedSpectrum:
    def test_returns_dict(self):
        result = radion_amplified_spectrum()
        assert isinstance(result, dict)

    def test_required_keys(self):
        keys = {"ells", "cls_flat", "cls_corrected", "correction_factors"}
        result = radion_amplified_spectrum()
        assert keys.issubset(result.keys())

    def test_lengths_consistent(self):
        result = radion_amplified_spectrum()
        n = len(result["ells"])
        assert len(result["cls_flat"]) == n
        assert len(result["cls_corrected"]) == n
        assert len(result["correction_factors"]) == n

    def test_cls_flat_positive(self):
        result = radion_amplified_spectrum()
        for cl in result["cls_flat"]:
            assert cl > 0

    def test_cls_corrected_positive(self):
        result = radion_amplified_spectrum()
        for cl in result["cls_corrected"]:
            assert cl > 0

    def test_correction_factors_positive(self):
        result = radion_amplified_spectrum()
        for cf in result["correction_factors"]:
            assert cf > 0

    def test_correction_factors_decrease(self):
        ells = [10.0, 100.0, 500.0, 1000.0, 2000.0]
        result = radion_amplified_spectrum(ells=ells)
        cfs = result["correction_factors"]
        for i in range(len(cfs) - 1):
            assert cfs[i] > cfs[i + 1]

    def test_cls_corrected_gt_flat(self):
        # phi_ratio > 1 at low ℓ, so corrected > flat
        result = radion_amplified_spectrum(ells=[10.0])
        assert result["cls_corrected"][0] > result["cls_flat"][0]

    def test_custom_ells(self):
        ells = [50.0, 200.0, 1000.0]
        result = radion_amplified_spectrum(ells=ells)
        assert result["ells"] == ells

    def test_flat_spectrum_formula(self):
        ell = 100.0
        result = radion_amplified_spectrum(ells=[ell])
        expected_flat = 1.0 / (ell * (ell + 1.0))
        assert abs(result["cls_flat"][0] - expected_flat) < 1e-15


# ===========================================================================
# closure_summary
# ===========================================================================

class TestClosureSummary:
    def test_returns_dict(self):
        result = closure_summary()
        assert isinstance(result, dict)

    def test_required_keys(self):
        keys = {
            "raw_deficit",
            "corrected_deficit",
            "resolution_achieved",
            "phi_ratio",
            "ell_kk",
            "silk_scale",
            "gap_closed_fraction",
            "audit",
        }
        result = closure_summary()
        assert keys.issubset(result.keys())

    def test_resolution_achieved_is_bool(self):
        result = closure_summary()
        assert isinstance(result["resolution_achieved"], bool)

    def test_resolution_achieved_true(self):
        result = closure_summary()
        assert result["resolution_achieved"] is True

    def test_corrected_deficit_lt_raw_deficit(self):
        result = closure_summary()
        assert result["corrected_deficit"] < result["raw_deficit"]

    def test_corrected_deficit_lt_threshold(self):
        result = closure_summary()
        assert result["corrected_deficit"] < RESOLUTION_THRESHOLD

    def test_phi_ratio_approx_31_4(self):
        result = closure_summary()
        assert abs(result["phi_ratio"] - 5 * 2 * math.pi) < 1e-10

    def test_ell_kk_approx_717(self):
        result = closure_summary()
        assert 700 < result["ell_kk"] < 730

    def test_silk_scale_positive(self):
        result = closure_summary()
        assert result["silk_scale"] > 0

    def test_gap_closed_fraction_positive(self):
        result = closure_summary()
        assert result["gap_closed_fraction"] > 0

    def test_gap_closed_fraction_in_unit_interval(self):
        result = closure_summary()
        assert 0.0 < result["gap_closed_fraction"] <= 1.0

    def test_audit_is_dict(self):
        result = closure_summary()
        assert isinstance(result["audit"], dict)

    def test_raw_deficit_gt_one(self):
        result = closure_summary()
        assert result["raw_deficit"] > 1.0

    def test_different_n_winding(self):
        r5 = closure_summary(n_winding=5)
        r3 = closure_summary(n_winding=3)
        assert r5["corrected_deficit"] < r3["corrected_deficit"]
        assert r5["resolution_achieved"]  # should still resolve with n=5

    def test_gap_closed_fraction_high(self):
        # With phi_ratio ≈ 31, gap closed fraction should be high
        result = closure_summary()
        assert result["gap_closed_fraction"] > 0.9


# ===========================================================================
# Edge cases and cross-function consistency
# ===========================================================================

class TestEdgeCases:
    def test_ell_one(self):
        # ℓ=1 should not raise
        corr = acoustic_peak_correction(1.0)
        assert corr > 0
        supp = peak_suppression_factor(1.0)
        assert supp > 0

    def test_very_large_ell(self):
        corr = acoustic_peak_correction(1_000_000)
        assert corr > 0
        assert corr < 1e-4  # strongly suppressed

    def test_n_winding_2(self):
        result = suppression_audit(n_winding=2)
        assert result["peak_deficit_corrected"] < result["peak_deficit_raw"]

    def test_k_cs_50(self):
        result = suppression_audit(k_cs=50)
        assert result["peak_deficit_corrected"] < result["peak_deficit_raw"]

    def test_k_cs_150(self):
        result = suppression_audit(k_cs=150)
        assert result["peak_deficit_corrected"] < result["peak_deficit_raw"]

    def test_correction_factor_consistency(self):
        # acoustic_peak_correction at ell=10 should equal phi_ratio × T_KK(10)
        ell = 100.0
        phi_r = phi_ratio_sls_to_today(5)
        lkk = K_CS * math.pi / C_S
        t_kk = 1.0 / (1.0 + (ell / lkk) ** 2)
        expected = phi_r * t_kk
        assert abs(acoustic_peak_correction(ell) - expected) < 1e-8

    def test_peak_suppression_factor_formula(self):
        # Should equal T_KK(ell) / T_KK(ELL_REF)
        ell = 500.0
        lkk = K_CS * math.pi / C_S
        t_kk_ell = 1.0 / (1.0 + (ell / lkk) ** 2)
        t_kk_ref = 1.0 / (1.0 + (ELL_REF / lkk) ** 2)
        expected = t_kk_ell / t_kk_ref
        assert abs(peak_suppression_factor(ell) - expected) < 1e-12

    def test_empty_ell_list_default(self):
        result = suppression_audit(ells=None)
        assert len(result["ells"]) == 7  # default list has 7 acoustic peaks

    def test_radion_spectrum_default_length(self):
        result = radion_amplified_spectrum()
        assert len(result["ells"]) == 50  # default: 50 log-spaced points
