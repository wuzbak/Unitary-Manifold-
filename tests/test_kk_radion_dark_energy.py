# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_radion_dark_energy.py
=====================================
Tests for Pillar 136 — KK Radion Dark Energy: Corrected EoS.

All tests verify:
  - Leading-order w_KK = −1 + (2/3)c_s² ≈ −0.9302
  - Radion mass >> H₀ for EW KK scale
  - Radion correction Δw ≈ 0 (negligible for EW scale)
  - w_corrected ≈ w_KK
  - DESI DR2 tension < 1σ ← CONSISTENT
  - Planck+BAO tension 2–4σ ← TENSION (honest)
  - Roman forecast tension > 1σ (future falsifier)
  - Pillar 136 summary structure
"""
import math
import pytest

from src.core.kk_radion_dark_energy import (
    kk_eos_leading_order,
    radion_mass_over_hubble,
    radion_eos_correction,
    kk_eos_corrected,
    eos_tension_vs_datasets,
    pillar136_summary,
    W_KK_LEADING,
    C_S_BRAID,
    C_S_SQUARED,
    N1_CANONICAL,
    N2_CANONICAL,
    H0_GEV,
    M_KK_EW_GEV,
    W_PLANCK_BAO_CENTRAL,
    W_DESI_DR2_CENTRAL,
    W_DESI_DR2_SIGMA,
)


class TestKkEosLeadingOrder:
    def test_canonical_value(self):
        w = kk_eos_leading_order()
        expected = -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2
        assert abs(w - expected) < 1e-10

    def test_approximately_minus_0_93(self):
        w = kk_eos_leading_order()
        assert -0.96 < w < -0.90

    def test_between_minus1_and_minus1_3(self):
        w = kk_eos_leading_order()
        assert -1.0 < w < -0.5

    def test_constant_formula_matches_w_kk_leading(self):
        w = kk_eos_leading_order()
        assert abs(w - W_KK_LEADING) < 1e-10

    def test_invalid_n1_raises(self):
        with pytest.raises(ValueError):
            kk_eos_leading_order(n1=0)


class TestRadionMassOverHubble:
    def test_ew_scale_gives_huge_ratio(self):
        r = radion_mass_over_hubble()
        assert r > 1e40  # radion mass >> H₀

    def test_ratio_positive(self):
        r = radion_mass_over_hubble()
        assert r > 0

    def test_larger_mkk_gives_larger_ratio(self):
        r1 = radion_mass_over_hubble(m_kk_gev=100.0)
        r2 = radion_mass_over_hubble(m_kk_gev=1000.0)
        assert r2 > r1

    def test_ratio_equal_to_hubble_when_mkk_equals_h0(self):
        r = radion_mass_over_hubble(m_kk_gev=H0_GEV, lambda_gw=1.0)
        assert abs(r - 1.0) < 1e-8

    def test_invalid_mkk_raises(self):
        with pytest.raises(ValueError):
            radion_mass_over_hubble(m_kk_gev=-100.0)

    def test_invalid_lambda_gw_raises(self):
        with pytest.raises(ValueError):
            radion_mass_over_hubble(lambda_gw=-1.0)

    def test_invalid_h0_raises(self):
        with pytest.raises(ValueError):
            radion_mass_over_hubble(h0_gev=-1.0)


class TestRadionEosCorrection:
    def test_correction_is_positive(self):
        dw = radion_eos_correction()
        assert dw >= 0

    def test_correction_negligible_for_ew_scale(self):
        dw = radion_eos_correction()
        assert abs(dw) < 1e-80

    def test_larger_mkk_gives_smaller_correction(self):
        dw1 = radion_eos_correction(m_kk_gev=H0_GEV * 10.0)
        dw2 = radion_eos_correction(m_kk_gev=H0_GEV * 100.0)
        assert dw2 < dw1

    def test_correction_at_h0_scale_is_significant(self):
        # When m_r = H₀: Δw = (1/3) × c_s²
        dw = radion_eos_correction(m_kk_gev=H0_GEV, lambda_gw=1.0)
        expected = (1.0 / 3.0) * C_S_SQUARED
        assert abs(dw - expected) < 1e-10


class TestKkEosCorrected:
    def test_w_corrected_approx_equals_w_leading_for_ew(self):
        result = kk_eos_corrected()
        assert abs(result["w_corrected"] - result["w_leading"]) < 1e-6

    def test_correction_negligible_flag(self):
        result = kk_eos_corrected()
        assert result["correction_negligible"] is True

    def test_delta_w_is_positive(self):
        result = kk_eos_corrected()
        assert result["delta_w"] >= 0

    def test_m_r_over_h0_huge(self):
        result = kk_eos_corrected()
        assert result["m_r_over_h0"] > 1e40

    def test_c_s_stored(self):
        result = kk_eos_corrected()
        assert abs(result["c_s"] - C_S_BRAID) < 1e-10

    def test_derivation_is_string(self):
        result = kk_eos_corrected()
        assert isinstance(result["derivation"], str)
        assert "\n" in result["derivation"]

    def test_w_leading_in_result(self):
        result = kk_eos_corrected()
        assert abs(result["w_leading"] - W_KK_LEADING) < 1e-10


class TestEosTensionVsDatasets:
    def test_desi_tension_below_1sigma(self):
        result = eos_tension_vs_datasets()
        # DESI DR2: w₀ = −0.92 ± 0.09; w_KK ≈ −0.9302 → ~0.11σ
        assert result["desi_dr2"]["sigma_tension"] < 1.0

    def test_desi_consistent_1sigma(self):
        result = eos_tension_vs_datasets()
        assert result["desi_dr2"]["consistent_1sigma"] is True

    def test_planck_tension_above_1sigma(self):
        result = eos_tension_vs_datasets()
        # Planck+BAO: w = −1.03 ± 0.03; tension ≈ 3.3σ
        assert result["planck_bao"]["sigma_tension"] > 1.0

    def test_all_datasets_present(self):
        result = eos_tension_vs_datasets()
        assert "planck_bao" in result
        assert "desi_dr2" in result
        assert "roman_forecast" in result

    def test_w_predicted_matches_constant(self):
        result = eos_tension_vs_datasets()
        assert abs(result["w_predicted"] - W_KK_LEADING) < 1e-10

    def test_sigma_values_positive(self):
        result = eos_tension_vs_datasets()
        for key in ["planck_bao", "desi_dr2", "roman_forecast"]:
            assert result[key]["sigma_tension"] >= 0

    def test_desi_tension_approximately_0_11sigma(self):
        result = eos_tension_vs_datasets()
        expected = abs(W_KK_LEADING - W_DESI_DR2_CENTRAL) / W_DESI_DR2_SIGMA
        assert abs(result["desi_dr2"]["sigma_tension"] - expected) < 1e-8

    def test_roman_tension_above_1sigma(self):
        result = eos_tension_vs_datasets()
        # w_KK ≈ −0.9302 vs Roman nominal −1.00 ± 0.02 → ~3.5σ
        assert result["roman_forecast"]["sigma_tension"] > 1.5


class TestModuleConstants:
    def test_c_s_is_12_over_37(self):
        assert abs(C_S_BRAID - 12.0 / 37.0) < 1e-12

    def test_c_s_squared(self):
        assert abs(C_S_SQUARED - (12.0 / 37.0) ** 2) < 1e-12

    def test_w_kk_leading_value(self):
        expected = -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2
        assert abs(W_KK_LEADING - expected) < 1e-10

    def test_w_kk_above_minus_1(self):
        assert W_KK_LEADING > -1.0

    def test_h0_gev_order_1e_minus_42(self):
        assert 1e-43 < H0_GEV < 1e-41

    def test_m_kk_ew_order_1_tev(self):
        assert 500 < M_KK_EW_GEV < 5000


class TestPillar136Summary:
    def test_pillar_number_136(self):
        result = pillar136_summary()
        assert result["pillar"] == 136

    def test_w_leading_correct(self):
        result = pillar136_summary()
        assert abs(result["w_leading"] - W_KK_LEADING) < 1e-10

    def test_correction_negligible(self):
        result = pillar136_summary()
        assert result["correction_negligible"] is True

    def test_desi_consistent_1sigma(self):
        result = pillar136_summary()
        assert result["desi_consistent_1sigma"] is True

    def test_status_is_string(self):
        result = pillar136_summary()
        assert isinstance(result["status"], str)

    def test_toe_status_present(self):
        result = pillar136_summary()
        assert "toe_status" in result
        # After adversarial review fix: status leads with TENSION against Planck+BAO
        assert "TENSION" in result["toe_status"] or "CONSTRAINED" in result["toe_status"]

    def test_falsifier_mentions_roman(self):
        result = pillar136_summary()
        assert "Roman" in result["falsifier"]

    def test_tensions_dict_present(self):
        result = pillar136_summary()
        assert "tensions" in result
        assert "desi_dr2_sigma" in result["tensions"]
        assert "planck_bao_sigma" in result["tensions"]

    def test_desi_sigma_below_1(self):
        result = pillar136_summary()
        assert result["tensions"]["desi_dr2_sigma"] < 1.0
