# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Track 4: 10D CY₃ KK threshold corrections to α_s(M_Z)."""
from __future__ import annotations

import math
import pytest

from src.tend.cy3_kk_thresholds_alpha_s import (
    ALPHA_S_MZ_PDG,
    ALPHA_S_MZ_DIRECT_CHAIN,
    WARP_FACTOR_5D,
    H11_QUINTIC,
    H21_QUINTIC,
    N_KK_MODES_EFF,
    FLUX_LATTICE_ENHANCEMENT_WEIGHT,
    M_KK_CY3_GEV,
    M_PLANCK_GEV,
    M_Z_GEV,
    cy3_beta_function_coefficient,
    flux_lattice_enhancement,
    kk_threshold_correction,
    alpha_s_with_cy3_thresholds,
    warp_factor_residual_cy3,
    cy3_architecture_gate,
    cy3_kk_thresholds_summary,
)


class TestConstants:
    def test_alpha_s_pdg_value(self):
        assert ALPHA_S_MZ_PDG == pytest.approx(0.1179, rel=1e-3)

    def test_alpha_s_direct_chain_positive(self):
        assert ALPHA_S_MZ_DIRECT_CHAIN > 0.0

    def test_alpha_s_direct_chain_below_pdg(self):
        assert ALPHA_S_MZ_DIRECT_CHAIN < ALPHA_S_MZ_PDG

    def test_warp_factor_5d_value(self):
        assert WARP_FACTOR_5D == pytest.approx(2.5, rel=1e-3)

    def test_hodge_numbers_quintic(self):
        assert H11_QUINTIC == 1
        assert H21_QUINTIC == 101

    def test_n_kk_modes(self):
        assert N_KK_MODES_EFF == 37

    def test_flux_lattice_enhancement_weight(self):
        assert FLUX_LATTICE_ENHANCEMENT_WEIGHT == pytest.approx(0.15, rel=1e-9)

    def test_m_kk_above_mz(self):
        assert M_KK_CY3_GEV > M_Z_GEV * 1e10

    def test_m_planck_above_m_kk(self):
        assert M_PLANCK_GEV > M_KK_CY3_GEV

    def test_m_z_value(self):
        assert M_Z_GEV == pytest.approx(91.188, rel=1e-3)


class TestBetaFunctionCoefficient:
    def test_quintic_b_kk_negative(self):
        b = cy3_beta_function_coefficient(H11_QUINTIC, H21_QUINTIC)
        assert b < 0, "Chiral-dominated CY₃ should give negative b_kk"

    def test_quintic_b_kk_magnitude(self):
        b = cy3_beta_function_coefficient(H11_QUINTIC, H21_QUINTIC)
        assert abs(b) < 2.0, "Per-level b_kk should be O(1)"
        assert abs(b) > 0.1

    def test_vector_dominated_positive(self):
        # h11 >> h21: vector-dominated → positive b_kk
        b = cy3_beta_function_coefficient(100, 1)
        assert b > 0

    def test_chiral_dominated_negative(self):
        b = cy3_beta_function_coefficient(1, 100)
        assert b < 0

    def test_dependence_on_h11(self):
        b1 = cy3_beta_function_coefficient(1, H21_QUINTIC)
        b2 = cy3_beta_function_coefficient(10, H21_QUINTIC)
        assert b2 > b1

    def test_dependence_on_h21(self):
        b1 = cy3_beta_function_coefficient(H11_QUINTIC, 10)
        b2 = cy3_beta_function_coefficient(H11_QUINTIC, 200)
        assert b2 < b1

    def test_quintic_b_kk_formula(self):
        expected = (2.0 * 1 - 101.0 / 3.0) / 37
        b = cy3_beta_function_coefficient(1, 101)
        assert b == pytest.approx(expected, rel=1e-6)


class TestKKThresholdCorrection:
    def test_positive_correction(self):
        b = cy3_beta_function_coefficient(H11_QUINTIC, H21_QUINTIC)
        delta = kk_threshold_correction(b)
        assert delta > 0, "CY₃ threshold correction should be positive"

    def test_correction_magnitude(self):
        b = cy3_beta_function_coefficient(H11_QUINTIC, H21_QUINTIC)
        delta = kk_threshold_correction(b)
        assert 0.001 < delta < 0.5

    def test_larger_b_kk_gives_larger_correction(self):
        b_small = cy3_beta_function_coefficient(1, 10)
        b_large = cy3_beta_function_coefficient(1, 200)
        d_small = kk_threshold_correction(b_small)
        d_large = kk_threshold_correction(b_large)
        assert d_large > d_small

    def test_larger_m_kk_gives_larger_correction(self):
        b = cy3_beta_function_coefficient(H11_QUINTIC, H21_QUINTIC)
        d1 = kk_threshold_correction(b, m_kk=1e15)
        d2 = kk_threshold_correction(b, m_kk=1e17)
        assert d2 > d1

    def test_log_ratio_positive(self):
        assert math.log(M_KK_CY3_GEV / M_Z_GEV) > 0


class TestFluxLatticeEnhancement:
    def test_enhancement_above_unity(self):
        assert flux_lattice_enhancement() > 1.0

    def test_more_modes_more_enhancement(self):
        assert flux_lattice_enhancement(100) > flux_lattice_enhancement(10)


class TestAlphaSWithCY3:
    def test_cy3_alpha_s_above_direct_chain(self):
        a_cy3 = alpha_s_with_cy3_thresholds()
        assert a_cy3 > ALPHA_S_MZ_DIRECT_CHAIN

    def test_cy3_alpha_s_still_below_pdg(self):
        a_cy3 = alpha_s_with_cy3_thresholds()
        assert a_cy3 < ALPHA_S_MZ_PDG, "10D CY₃ limit — should not reach PDG"

    def test_cy3_alpha_s_in_reasonable_range(self):
        a_cy3 = alpha_s_with_cy3_thresholds()
        # Lower bound reflects strengthened CY3+flux pathway in this track.
        assert 0.08 < a_cy3 < 0.12

    def test_custom_b_kk(self):
        b = cy3_beta_function_coefficient(H11_QUINTIC, H21_QUINTIC)
        a1 = alpha_s_with_cy3_thresholds(b_kk=b)
        a2 = alpha_s_with_cy3_thresholds()
        assert a1 == pytest.approx(a2, rel=1e-6)

    def test_improvement_increases_with_h21(self):
        a_small = alpha_s_with_cy3_thresholds(
            b_kk=cy3_beta_function_coefficient(1, 50)
        )
        a_large = alpha_s_with_cy3_thresholds(
            b_kk=cy3_beta_function_coefficient(1, 200)
        )
        assert a_large > a_small


class TestWarpFactorResidual:
    def test_gap_factor_finite(self):
        a_cy3 = alpha_s_with_cy3_thresholds()
        gap = warp_factor_residual_cy3(a_cy3)
        assert math.isfinite(gap)

    def test_gap_factor_above_one(self):
        a_cy3 = alpha_s_with_cy3_thresholds()
        gap = warp_factor_residual_cy3(a_cy3)
        assert gap > 1.0, "Architecture limit — gap should remain > 1"

    def test_gap_factor_below_5d_baseline(self):
        a_cy3 = alpha_s_with_cy3_thresholds()
        gap = warp_factor_residual_cy3(a_cy3)
        assert gap < WARP_FACTOR_5D, "CY₃ must improve over 5D baseline"

    def test_gap_factor_direct_chain_matches_pdg_ratio(self):
        gap = warp_factor_residual_cy3(ALPHA_S_MZ_DIRECT_CHAIN)
        expected = ALPHA_S_MZ_PDG / ALPHA_S_MZ_DIRECT_CHAIN
        assert gap == pytest.approx(expected, rel=1e-6)

    def test_gap_factor_zero_alpha_returns_inf(self):
        gap = warp_factor_residual_cy3(0.0)
        assert math.isinf(gap)


class TestArchitectureGate:
    def test_gate_pass(self):
        g = cy3_architecture_gate()
        assert g["gate_pass"] is True

    def test_correction_positive(self):
        g = cy3_architecture_gate()
        assert g["correction_positive"] is True

    def test_gap_improved(self):
        g = cy3_architecture_gate()
        assert g["gap_improved"] is True

    def test_still_architecture_limited(self):
        g = cy3_architecture_gate()
        assert g["still_architecture_limited"] is True

    def test_residual_improved(self):
        g = cy3_architecture_gate()
        assert g["residual_pct_after"] < g["residual_pct_before"]
        assert g["residual_pct_after"] < 25.0

    def test_gap_factor_decreased(self):
        g = cy3_architecture_gate()
        assert g["gap_factor_cy3"] < g["gap_factor_5d_baseline"]

    def test_status_contains_certified(self):
        g = cy3_architecture_gate()
        assert "ARCHITECTURE_LIMIT_CERTIFIED" in g["status"]

    def test_gate_has_expected_keys(self):
        g = cy3_architecture_gate()
        for key in [
            "b_kk", "delta_alpha_s", "alpha_s_direct_chain",
            "alpha_s_cy3_corrected", "alpha_s_pdg",
            "gap_factor_5d_baseline", "gap_factor_cy3",
            "residual_pct_before", "residual_pct_after",
            "delta_alpha_s_raw", "flux_lattice_enhancement_factor",
            "correction_positive", "gap_improved",
            "still_architecture_limited", "gate_pass", "status",
        ]:
            assert key in g

    def test_alpha_s_direct_chain_in_gate(self):
        g = cy3_architecture_gate()
        assert g["alpha_s_direct_chain"] == pytest.approx(ALPHA_S_MZ_DIRECT_CHAIN, rel=1e-6)

    def test_alpha_s_pdg_in_gate(self):
        g = cy3_architecture_gate()
        assert g["alpha_s_pdg"] == pytest.approx(ALPHA_S_MZ_PDG, rel=1e-6)


class TestSummary:
    def test_summary_keys(self):
        s = cy3_kk_thresholds_summary()
        for key in [
            "h11_quintic", "h21_quintic", "n_kk_modes_eff",
            "flux_lattice_enhancement_factor",
            "m_kk_cy3_gev", "b_kk", "delta_alpha_s",
            "alpha_s_direct_chain", "alpha_s_cy3_corrected", "alpha_s_pdg",
            "gap_factor_5d", "gap_factor_cy3",
            "residual_pct_before", "residual_pct_after",
            "gate", "overall_status", "note",
        ]:
            assert key in s

    def test_overall_status(self):
        s = cy3_kk_thresholds_summary()
        assert s["overall_status"] == "ARCHITECTURE_LIMIT_CERTIFIED(10D)"

    def test_hodge_numbers_in_summary(self):
        s = cy3_kk_thresholds_summary()
        assert s["h11_quintic"] == H11_QUINTIC
        assert s["h21_quintic"] == H21_QUINTIC

    def test_note_nonempty(self):
        s = cy3_kk_thresholds_summary()
        assert len(s["note"]) > 50

    def test_gap_factor_cy3_in_summary(self):
        s = cy3_kk_thresholds_summary()
        assert 1.0 < s["gap_factor_cy3"] < WARP_FACTOR_5D
