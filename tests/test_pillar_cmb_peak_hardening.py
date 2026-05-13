# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/pillar_cmb_peak_hardening.py."""

from __future__ import annotations

import pytest

from src.core.pillar_cmb_peak_hardening import (
    PEAK_ELL_VALUES,
    BASELINE_SUPPRESSION_FACTORS,
    N_W_CANONICAL,
    K_CS_CANONICAL,
    C_S_CANONICAL,
    CMB_PEAK_RESIDUAL_FACTOR,
    analytic_suppression_factor,
    numerical_suppression_factor,
    combined_p57_p63_peak_residual,
    combined_residual_report,
    sensitivity_scan_pm10pct,
)


class TestConstants:
    def test_peak_set(self):
        assert PEAK_ELL_VALUES == (220, 540, 820)

    def test_baseline_has_three_peaks(self):
        assert set(BASELINE_SUPPRESSION_FACTORS.keys()) == {220, 540, 820}

    def test_nw_kcs_canonical(self):
        assert N_W_CANONICAL == 5.0
        assert K_CS_CANONICAL == 74.0

    def test_sound_speed_range(self):
        assert 0.0 < C_S_CANONICAL < 1.0

    def test_named_residual_positive(self):
        assert CMB_PEAK_RESIDUAL_FACTOR > 0.0


class TestAnalyticNumericSuppression:
    @pytest.mark.parametrize("ell", [220, 540, 820])
    def test_analytic_positive(self, ell):
        assert analytic_suppression_factor(ell) > 1.0

    @pytest.mark.parametrize("ell", [220, 540, 820])
    def test_numeric_matches_analytic(self, ell):
        a = analytic_suppression_factor(ell)
        n = numerical_suppression_factor(ell)
        assert abs(a - n) < 1e-10

    def test_invalid_peak_raises(self):
        with pytest.raises(ValueError):
            analytic_suppression_factor(300)

    def test_small_sample_raises(self):
        with pytest.raises(ValueError):
            numerical_suppression_factor(220, n_samples=10)


class TestCombinedResiduals:
    @pytest.mark.parametrize("ell", [220, 540, 820])
    def test_combined_residual_positive(self, ell):
        assert combined_p57_p63_peak_residual(ell) > 0.0

    @pytest.mark.parametrize("ell", [220, 540, 820])
    def test_combined_reduces_baseline(self, ell):
        residual = combined_p57_p63_peak_residual(ell)
        assert residual < analytic_suppression_factor(ell)

    def test_report_structure(self):
        report = combined_residual_report()
        for key in ("n_w", "k_cs", "peaks", "max_combined_residual", "combined_reduces_below_x2"):
            assert key in report

    def test_report_has_three_peaks(self):
        report = combined_residual_report()
        assert len(report["peaks"]) == 3

    def test_each_peak_payload_keys(self):
        report = combined_residual_report()
        for row in report["peaks"]:
            for key in ("ell", "analytic_suppression", "numerical_suppression", "combined_residual"):
                assert key in row

    def test_named_constant_matches_report(self):
        report = combined_residual_report()
        assert abs(report["max_combined_residual"] - CMB_PEAK_RESIDUAL_FACTOR) < 1e-12

    def test_residual_below_x2_target(self):
        report = combined_residual_report()
        assert report["max_combined_residual"] < 2.0
        assert report["combined_reduces_below_x2"] is True

    def test_peak1_residual_bound(self):
        assert combined_p57_p63_peak_residual(220) < 1.6

    def test_peak2_residual_bound(self):
        assert combined_p57_p63_peak_residual(540) < 1.6

    def test_peak3_residual_bound(self):
        assert combined_p57_p63_peak_residual(820) < 1.7

    def test_invalid_ell_raises(self):
        with pytest.raises(ValueError):
            combined_p57_p63_peak_residual(0)


class TestSensitivity:
    def test_scan_structure(self):
        scan = sensitivity_scan_pm10pct()
        for key in ("variants", "baseline_max_residual", "delta_vs_baseline"):
            assert key in scan

    def test_all_variants_present(self):
        scan = sensitivity_scan_pm10pct()
        expected = {
            "baseline",
            "n_w_minus_10pct",
            "n_w_plus_10pct",
            "k_cs_minus_10pct",
            "k_cs_plus_10pct",
        }
        assert set(scan["variants"].keys()) == expected

    def test_variant_max_residuals_positive(self):
        scan = sensitivity_scan_pm10pct()
        for payload in scan["variants"].values():
            assert payload["max_combined_residual"] > 0

    def test_baseline_stays_below_x2(self):
        scan = sensitivity_scan_pm10pct()
        assert scan["baseline_max_residual"] < 2.0

    def test_all_variants_stay_below_x2(self):
        scan = sensitivity_scan_pm10pct()
        for payload in scan["variants"].values():
            assert payload["max_combined_residual"] < 2.0

    def test_nw_plus10_changes_residual(self):
        scan = sensitivity_scan_pm10pct()
        assert scan["delta_vs_baseline"]["n_w_plus_10pct"] != 0.0

    def test_nw_minus10_changes_residual(self):
        scan = sensitivity_scan_pm10pct()
        assert scan["delta_vs_baseline"]["n_w_minus_10pct"] != 0.0

    def test_kcs_plus10_changes_residual(self):
        scan = sensitivity_scan_pm10pct()
        assert scan["delta_vs_baseline"]["k_cs_plus_10pct"] != 0.0

    def test_kcs_minus10_changes_residual(self):
        scan = sensitivity_scan_pm10pct()
        assert scan["delta_vs_baseline"]["k_cs_minus_10pct"] != 0.0

    def test_nw_up_typically_worsens(self):
        scan = sensitivity_scan_pm10pct()
        assert scan["delta_vs_baseline"]["n_w_plus_10pct"] > 0.0

    def test_kcs_up_typically_improves(self):
        scan = sensitivity_scan_pm10pct()
        assert scan["delta_vs_baseline"]["k_cs_plus_10pct"] < 0.0
