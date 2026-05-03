# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_higgs_mass_closure.py
==================================
Tests for Pillar 134 — Higgs Mass Closure from FTUM Quartic + One-Loop RGE.

All tests verify:
  - FTUM tree-level quartic λ_H = n_w²/(2k_CS) = 25/148 ≈ 0.1689
  - Tree-level mass ≈ 143 GeV (pre-loop)
  - M_KK from RS warp factor
  - Top Yukawa at M_KK ≈ 0.87-0.95
  - RGE correction Δλ < 0 (reduces quartic when running down)
  - Effective m_H within 5 % of PDG 125.25 GeV
  - Conservative interval [m_min, m_max] contains PDG 125.25 GeV
  - pillar134_summary structure and closure status
"""
import math
import pytest

from src.core.higgs_mass_closure import (
    ftum_tree_quartic,
    kk_scale_gev,
    top_yukawa_at_kk,
    rge_quartic_correction,
    higgs_mass_closure,
    higgs_mass_interval,
    pillar134_summary,
    N_W_CANONICAL,
    K_CS_CANONICAL,
    PI_KR_CANONICAL,
    M_PLANCK_GEV,
    HIGGS_VEV_GEV,
    HIGGS_MASS_PDG_GEV,
    LAMBDA_H_TREE,
    M_KK_GEV,
)


class TestFtumTreeQuartic:
    def test_canonical_quartic_value(self):
        result = ftum_tree_quartic()
        expected = 25.0 / (2 * 74)
        assert abs(result["lambda_H_tree"] - expected) < 1e-10

    def test_quartic_is_25_over_148(self):
        result = ftum_tree_quartic()
        assert abs(result["lambda_H_tree"] - 25 / 148) < 1e-10

    def test_tree_mass_is_approximately_143(self):
        result = ftum_tree_quartic()
        # m_H^tree = 246 × √(2 × 25/148) ≈ 143 GeV
        assert 138.0 < result["m_H_tree_gev"] < 148.0

    def test_n_w_stored(self):
        result = ftum_tree_quartic(n_w=5)
        assert result["n_w"] == 5

    def test_k_cs_stored(self):
        result = ftum_tree_quartic(k_cs=74)
        assert result["k_cs"] == 74

    def test_invalid_n_w_raises(self):
        with pytest.raises(ValueError):
            ftum_tree_quartic(n_w=0)

    def test_invalid_k_cs_raises(self):
        with pytest.raises(ValueError):
            ftum_tree_quartic(k_cs=-1)

    def test_quartic_scales_as_n_w_squared(self):
        r1 = ftum_tree_quartic(n_w=3)
        r2 = ftum_tree_quartic(n_w=6)
        # λ ∝ n_w² → ratio = 4
        ratio = r2["lambda_H_tree"] / r1["lambda_H_tree"]
        assert abs(ratio - 4.0) < 1e-8

    def test_derivation_is_string(self):
        result = ftum_tree_quartic()
        assert isinstance(result["derivation"], str)


class TestKkScaleGev:
    def test_canonical_kk_scale(self):
        m_kk = kk_scale_gev()
        # M_KK = M_Pl × exp(-37) ≈ 1000-1100 GeV
        assert 800 < m_kk < 1500

    def test_larger_pikr_gives_smaller_mkk(self):
        m1 = kk_scale_gev(pi_kr=35.0)
        m2 = kk_scale_gev(pi_kr=39.0)
        assert m2 < m1

    def test_zero_pikr_gives_planck_mass(self):
        # Note: pi_kr > 0 is required; small pi_kr → M_KK near Planck scale
        m_kk = kk_scale_gev(pi_kr=1e-6)
        # For tiny πkR, M_KK ≈ M_Pl
        assert m_kk > M_PLANCK_GEV * 0.999

    def test_invalid_pikr_raises(self):
        with pytest.raises(ValueError):
            kk_scale_gev(pi_kr=-1.0)

    def test_m_kk_constant_consistent(self):
        assert abs(M_KK_GEV - kk_scale_gev()) < 1e-3


class TestTopYukawaAtKk:
    def test_at_top_mass_returns_y_t0(self):
        # When m_kk = m_top, running is zero
        m_top = 172.76
        y_t = top_yukawa_at_kk(m_top_gev=m_top, m_kk_gev=m_top)
        y_t0 = math.sqrt(2) * m_top / HIGGS_VEV_GEV
        assert abs(y_t - y_t0) < 1e-8

    def test_y_t_decreases_at_higher_scale(self):
        y_t_mt = top_yukawa_at_kk(m_top_gev=172.76, m_kk_gev=172.76)
        y_t_kk = top_yukawa_at_kk(m_top_gev=172.76, m_kk_gev=1040.0)
        # QCD asymptotic freedom: y_t decreases slightly at higher scales
        assert y_t_kk <= y_t_mt

    def test_y_t_kk_is_positive(self):
        y_t = top_yukawa_at_kk()
        assert y_t > 0

    def test_y_t_kk_in_physical_range(self):
        y_t = top_yukawa_at_kk()
        assert 0.5 < y_t < 1.2

    def test_canonical_y_t_approximately_0_9(self):
        y_t = top_yukawa_at_kk()
        assert 0.85 < y_t < 1.0

    def test_invalid_m_top_raises(self):
        with pytest.raises(ValueError):
            top_yukawa_at_kk(m_top_gev=-1.0)

    def test_invalid_m_kk_raises(self):
        with pytest.raises(ValueError):
            top_yukawa_at_kk(m_kk_gev=-100.0)


class TestRgeQuarticCorrection:
    def test_correction_is_negative(self):
        y_t = 0.92
        m_kk = kk_scale_gev()
        delta = rge_quartic_correction(y_t, m_kk)
        assert delta < 0

    def test_larger_y_t_gives_larger_correction(self):
        m_kk = kk_scale_gev()
        d1 = rge_quartic_correction(0.8, m_kk)
        d2 = rge_quartic_correction(0.95, m_kk)
        assert abs(d2) > abs(d1)

    def test_mkk_below_v_gives_zero(self):
        delta = rge_quartic_correction(0.92, m_kk_gev=100.0)
        assert delta == 0.0

    def test_larger_mkk_gives_larger_correction(self):
        d1 = rge_quartic_correction(0.92, m_kk_gev=500.0)
        d2 = rge_quartic_correction(0.92, m_kk_gev=2000.0)
        assert abs(d2) > abs(d1)

    def test_magnitude_in_reasonable_range(self):
        y_t = 0.92
        m_kk = kk_scale_gev()
        delta = rge_quartic_correction(y_t, m_kk)
        # Expected ~0.04 magnitude
        assert 0.02 < abs(delta) < 0.10


class TestHiggsMassClosure:
    def test_effective_mass_within_5pct_of_pdg(self):
        result = higgs_mass_closure()
        assert result["m_H_pct_err"] < 5.0, (
            f"m_H eff = {result['m_H_eff_gev']:.2f} GeV, "
            f"PDG = {HIGGS_MASS_PDG_GEV} GeV, err = {result['m_H_pct_err']:.2f}%"
        )

    def test_effective_mass_in_range_115_135(self):
        result = higgs_mass_closure()
        assert 115.0 < result["m_H_eff_gev"] < 135.0

    def test_tree_mass_approximately_143(self):
        result = higgs_mass_closure()
        assert 135.0 < result["m_H_tree_gev"] < 150.0

    def test_loop_correction_reduces_mass(self):
        result = higgs_mass_closure()
        assert result["m_H_eff_gev"] < result["m_H_tree_gev"]

    def test_delta_lambda_is_negative(self):
        result = higgs_mass_closure()
        assert result["delta_lambda"] < 0

    def test_lambda_eff_less_than_tree(self):
        result = higgs_mass_closure()
        assert result["lambda_H_eff"] < result["lambda_H_tree"]

    def test_lambda_eff_positive(self):
        result = higgs_mass_closure()
        assert result["lambda_H_eff"] > 0

    def test_status_contains_derived(self):
        result = higgs_mass_closure()
        assert "DERIVED" in result["status"] or "CONSTRAINED" in result["status"]

    def test_m_kk_in_result(self):
        result = higgs_mass_closure()
        assert 800 < result["m_kk_gev"] < 1500

    def test_y_t_kk_in_result(self):
        result = higgs_mass_closure()
        assert 0.5 < result["y_t_kk"] < 1.2

    def test_pdg_stored(self):
        result = higgs_mass_closure()
        assert abs(result["m_H_pdg_gev"] - HIGGS_MASS_PDG_GEV) < 1e-8

    def test_derivation_is_multiline(self):
        result = higgs_mass_closure()
        assert "\n" in result["derivation"]

    def test_different_pi_kr_changes_result(self):
        r1 = higgs_mass_closure(pi_kr=35.0)
        r2 = higgs_mass_closure(pi_kr=39.0)
        assert abs(r1["m_H_eff_gev"] - r2["m_H_eff_gev"]) > 0.5

    def test_lambda_h_tree_constant(self):
        result = higgs_mass_closure()
        assert abs(result["lambda_H_tree"] - LAMBDA_H_TREE) < 1e-10


class TestHiggsMassInterval:
    def test_pdg_in_interval(self):
        result = higgs_mass_interval()
        assert result["pdg_in_interval"] is True, (
            f"PDG {HIGGS_MASS_PDG_GEV} not in [{result['m_H_min_gev']:.1f}, "
            f"{result['m_H_max_gev']:.1f}] GeV"
        )

    def test_min_less_than_max(self):
        result = higgs_mass_interval()
        assert result["m_H_min_gev"] < result["m_H_max_gev"]

    def test_central_within_interval(self):
        result = higgs_mass_interval()
        assert result["m_H_min_gev"] <= result["m_H_central_gev"] <= result["m_H_max_gev"]

    def test_status_is_string(self):
        result = higgs_mass_interval()
        assert isinstance(result["status"], str)

    def test_min_below_pdg(self):
        result = higgs_mass_interval()
        assert result["m_H_min_gev"] < HIGGS_MASS_PDG_GEV

    def test_max_above_pdg(self):
        result = higgs_mass_interval()
        assert result["m_H_max_gev"] > HIGGS_MASS_PDG_GEV


class TestPillar134Summary:
    def test_pillar_number_134(self):
        result = pillar134_summary()
        assert result["pillar"] == 134

    def test_m_H_predicted_in_result(self):
        result = pillar134_summary()
        assert 115.0 < result["m_H_predicted_gev"] < 135.0

    def test_pct_accuracy_below_5(self):
        result = pillar134_summary()
        assert result["pct_accuracy"] < 5.0

    def test_status_is_derived(self):
        result = pillar134_summary()
        assert "DERIVED" in result["status"] or "CONSTRAINED" in result["status"]

    def test_pdg_in_interval(self):
        result = pillar134_summary()
        assert result["pdg_in_interval"] is True

    def test_key_formula_present(self):
        result = pillar134_summary()
        assert "key_formula" in result
        assert "λ" in result["key_formula"] or "lambda" in result["key_formula"].lower()

    def test_lambda_h_tree_consistent(self):
        result = pillar134_summary()
        assert abs(result["lambda_H_tree"] - 25 / 148) < 1e-8

    def test_delta_lambda_negative(self):
        result = pillar134_summary()
        assert result["delta_lambda"] < 0

    def test_interval_contains_pdg(self):
        result = pillar134_summary()
        lo, hi = result["interval_gev"]
        assert lo < HIGGS_MASS_PDG_GEV < hi
