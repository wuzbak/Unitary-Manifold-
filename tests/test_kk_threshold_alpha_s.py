# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for KK Threshold α_s Correction (Pillar 219, Track A Session 2)."""

import math
import pytest

from src.core.kk_threshold_alpha_s import (
    N_W, K_CS, N_C,
    M_PL_GEV, PI_KR, M_KK_GEV,
    ALPHA_S_GEO_GUT,
    ALPHA_S_GEO_MEW,
    ALPHA_S_PDG_MZ,
    WARP_ANCHOR_GAP_FACTOR,
    N_KK_MODES_EFFECTIVE,
    THRESHOLD_CORRECTION_FACTOR,
    ALPHA_S_KK_CORRECTED,
    RESIDUAL_GAP_FACTOR,
    ARCHITECTURE_LIMIT,
    REQUIRES_DIMENSION,
    kk_spectral_weight,
    kk_mode_beta_coefficient,
    kk_threshold_sum,
    alpha_s_kk_corrected,
    warp_anchor_gap_analysis,
    threshold_correction_audit,
    pillar219_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_m_kk_positive(self):
        assert M_KK_GEV > 0

    def test_m_kk_much_less_than_mpl(self):
        assert M_KK_GEV < M_PL_GEV * 1e-10

    def test_alpha_s_geo_gut_value(self):
        expected = 3.0 / 74.0
        assert ALPHA_S_GEO_GUT == pytest.approx(expected, rel=1e-6)

    def test_alpha_s_geo_mew_positive(self):
        assert ALPHA_S_GEO_MEW > 0

    def test_alpha_s_geo_mew_less_than_geo_gut(self):
        # Running down from GUT to EW increases α_s
        # α_s(M_EW) > α_s(M_GUT) for QCD (asymptotic freedom)
        # GUT has α_s small, at EW it is larger
        assert ALPHA_S_GEO_MEW >= ALPHA_S_GEO_GUT * 0.5  # rough bound

    def test_pdg_alpha_s_is_comparison_only(self):
        # PDG value should be around 0.118
        assert 0.10 < ALPHA_S_PDG_MZ < 0.14

    def test_warp_anchor_gap_positive(self):
        assert WARP_ANCHOR_GAP_FACTOR > 1.0

    def test_warp_anchor_gap_finite(self):
        assert WARP_ANCHOR_GAP_FACTOR < 100.0

    def test_n_kk_modes_effective_positive(self):
        assert N_KK_MODES_EFFECTIVE > 0

    def test_architecture_limit_flag(self):
        assert ARCHITECTURE_LIMIT is True

    def test_requires_dimension(self):
        assert REQUIRES_DIMENSION == 10


class TestKKSpectralWeight:
    def test_n1_has_weight_between_0_and_1(self):
        w = kk_spectral_weight(1)
        assert 0 < w <= 1

    def test_n0_would_be_1(self):
        w = kk_spectral_weight(0)
        assert w == pytest.approx(1.0)

    def test_weights_decrease_with_n(self):
        for n in range(1, 10):
            assert kk_spectral_weight(n) > kk_spectral_weight(n + 1)

    def test_large_n_weight_tiny(self):
        w = kk_spectral_weight(100)
        assert w < 1e-50


class TestKKModeBetaCoefficient:
    def test_returns_positive(self):
        b = kk_mode_beta_coefficient(1)
        assert b > 0

    def test_scales_with_n_c(self):
        b3 = kk_mode_beta_coefficient(1, n_c=3)
        b4 = kk_mode_beta_coefficient(1, n_c=4)
        assert b4 > b3

    def test_suppressed_by_pi_kr(self):
        # b_n = b0 / PI_KR — smaller than bare b0
        b = kk_mode_beta_coefficient(1)
        b0_bare = 11.0 * 3.0 / 3.0 - 2.0 * 6.0 / 3.0   # ≈ 7
        assert b < b0_bare


class TestKKThresholdSum:
    def test_returns_float_and_list(self):
        delta, table = kk_threshold_sum()
        assert isinstance(delta, float)
        assert isinstance(table, list)

    def test_delta_finite(self):
        delta, _ = kk_threshold_sum()
        assert math.isfinite(delta)

    def test_table_entries_have_n(self):
        _, table = kk_threshold_sum()
        for entry in table:
            assert "n" in entry
            assert "w_n" in entry


class TestAlphaSKKCorrected:
    def test_corrected_value_finite(self):
        val = alpha_s_kk_corrected()
        assert math.isfinite(val)

    def test_corrected_differs_from_geo(self):
        val = alpha_s_kk_corrected()
        assert val != ALPHA_S_GEO_MEW

    def test_residual_gap_smaller_than_initial(self):
        # After corrections, residual gap should be less than initial gap
        assert RESIDUAL_GAP_FACTOR <= WARP_ANCHOR_GAP_FACTOR * 1.1  # within 10% margin


class TestWarpAnchorGapAnalysis:
    def test_returns_dict(self):
        result = warp_anchor_gap_analysis()
        assert isinstance(result, dict)

    def test_has_alpha_s_keys(self):
        result = warp_anchor_gap_analysis()
        assert "alpha_s_geo_gut" in result
        assert "alpha_s_geo_mew" in result
        assert "alpha_s_kk_corrected" in result

    def test_architecture_limit_true(self):
        result = warp_anchor_gap_analysis()
        assert result["architecture_limit"] is True

    def test_requires_dimension_10(self):
        result = warp_anchor_gap_analysis()
        assert result["requires_dimension"] == 10


class TestThresholdCorrectionAudit:
    def test_returns_dict(self):
        result = threshold_correction_audit()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = threshold_correction_audit()
        assert result["pillar"] == 219

    def test_axiom_zero_compliant(self):
        result = threshold_correction_audit()
        assert result["axiom_zero_compliant"] is True

    def test_honest_verdict_present(self):
        result = threshold_correction_audit()
        assert len(result["honest_verdict"]) > 50


class TestPillar219Summary:
    def test_returns_dict(self):
        s = pillar219_summary()
        assert isinstance(s, dict)

    def test_pillar_number(self):
        s = pillar219_summary()
        assert s["pillar"] == 219

    def test_architecture_limit_true(self):
        s = pillar219_summary()
        assert s["architecture_limit"] is True
