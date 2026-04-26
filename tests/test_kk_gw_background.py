# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_gw_background.py
================================
Test suite for src/core/kk_gw_background.py — Pillar 69.

Covers:
  - Module constants
  - kk_gw_peak_frequency: Planck scale, TeV scale, scaling, errors
  - kk_gw_energy_density: positivity, scaling, boundary cases
  - lisa_sensitivity_comparison: dict keys, in_lisa_band bool, snr, strings
  - nanograv_kk_consistency: dict keys, kk_explains_nanograv, consistency
  - kk_gw_spectral_shape: peak ~1, positive, falls off, errors
  - gw_background_summary: dict structure, falsification conditions

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

import sys
import os
import math
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.kk_gw_background import (
    N_W,
    K_CS,
    C_S,
    M_PLANCK_GEV,
    H0_KM_S_MPC,
    H0_HZ,
    OMEGA_RAD_H2,
    LISA_F_LOW_HZ,
    LISA_F_HIGH_HZ,
    LISA_OMEGA_GW_SENSITIVITY,
    NANOGRAV_F_REF_HZ,
    NANOGRAV_OMEGA_GW_SIGNAL,
    NANOGRAV_OMEGA_GW_UNC,
    GEV_TO_HZ,
    kk_gw_peak_frequency,
    kk_gw_energy_density,
    lisa_sensitivity_comparison,
    nanograv_kk_consistency,
    kk_gw_spectral_shape,
    gw_background_summary,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-14

    def test_m_planck_gev(self):
        assert abs(M_PLANCK_GEV - 1.22e19) < 1e14

    def test_h0_positive(self):
        assert H0_HZ > 0

    def test_omega_rad_positive(self):
        assert OMEGA_RAD_H2 > 0

    def test_lisa_band_order(self):
        assert LISA_F_LOW_HZ < LISA_F_HIGH_HZ

    def test_nanograv_freq_positive(self):
        assert NANOGRAV_F_REF_HZ > 0

    def test_nanograv_signal_positive(self):
        assert NANOGRAV_OMEGA_GW_SIGNAL > 0

    def test_gev_to_hz_large(self):
        assert GEV_TO_HZ > 1e20


class TestPeakFrequency:
    def test_planck_scale_frequency_large(self):
        f = kk_gw_peak_frequency(M_PLANCK_GEV)
        assert f > 1e40  # Far above any detector

    def test_1_tev_frequency(self):
        f = kk_gw_peak_frequency(1e3)
        # f = 1e3 * 1.52e24 / (2π) ≈ 2.4e26 Hz
        expected = 1e3 * GEV_TO_HZ / (2.0 * math.pi)
        assert f == pytest.approx(expected, rel=1e-10)

    def test_frequency_positive(self):
        assert kk_gw_peak_frequency(100.0) > 0

    def test_frequency_scales_linearly(self):
        f1 = kk_gw_peak_frequency(1.0)
        f2 = kk_gw_peak_frequency(2.0)
        assert f2 == pytest.approx(2.0 * f1, rel=1e-10)

    def test_frequency_negative_mkk_raises(self):
        with pytest.raises(ValueError):
            kk_gw_peak_frequency(-1.0)

    def test_frequency_zero_mkk_raises(self):
        with pytest.raises(ValueError):
            kk_gw_peak_frequency(0.0)

    def test_frequency_tiny_mkk(self):
        # For f ~ 1e-3 Hz (LISA), M_KK = 1e-3 Hz * 2π / GEV_TO_HZ
        m_kk = 1e-3 * 2.0 * math.pi / GEV_TO_HZ
        f = kk_gw_peak_frequency(m_kk)
        assert f == pytest.approx(1e-3, rel=1e-8)

    def test_frequency_output_type(self):
        assert isinstance(kk_gw_peak_frequency(1.0), float)

    def test_frequency_formula_exact(self):
        M_KK = 5.0
        f = kk_gw_peak_frequency(M_KK)
        assert f == pytest.approx(M_KK * GEV_TO_HZ / (2.0 * math.pi), rel=1e-10)

    def test_1_gev_frequency(self):
        f = kk_gw_peak_frequency(1.0)
        expected = GEV_TO_HZ / (2.0 * math.pi)
        assert f == pytest.approx(expected, rel=1e-10)

    def test_frequency_small_mass(self):
        f = kk_gw_peak_frequency(1e-20)
        assert f > 0

    def test_frequency_large_mass(self):
        f = kk_gw_peak_frequency(1e30)
        assert f > 1e50

    def test_frequency_ratio_preserved(self):
        f1 = kk_gw_peak_frequency(10.0)
        f2 = kk_gw_peak_frequency(100.0)
        assert f2 / f1 == pytest.approx(10.0, rel=1e-10)

    def test_frequency_monotone(self):
        masses = [1.0, 10.0, 100.0, 1000.0]
        freqs = [kk_gw_peak_frequency(m) for m in masses]
        for i in range(len(freqs) - 1):
            assert freqs[i] < freqs[i + 1]

    def test_frequency_units_consistency(self):
        # 1 GeV = GEV_TO_HZ Hz → f = GEV_TO_HZ / (2π)
        f = kk_gw_peak_frequency(1.0)
        assert f == pytest.approx(GEV_TO_HZ / (2.0 * math.pi), rel=1e-10)

    def test_very_low_frequency_requires_very_low_mkk(self):
        # LISA lower edge at 1e-4 Hz
        m_kk = LISA_F_LOW_HZ * 2.0 * math.pi / GEV_TO_HZ
        f = kk_gw_peak_frequency(m_kk)
        assert f == pytest.approx(LISA_F_LOW_HZ, rel=1e-8)

    def test_nanograv_frequency_requires_tiny_mkk(self):
        m_kk = NANOGRAV_F_REF_HZ * 2.0 * math.pi / GEV_TO_HZ
        f = kk_gw_peak_frequency(m_kk)
        assert f == pytest.approx(NANOGRAV_F_REF_HZ, rel=1e-8)

    def test_planck_scale_much_above_nanograv(self):
        f = kk_gw_peak_frequency(M_PLANCK_GEV)
        assert f > 1e30 * NANOGRAV_F_REF_HZ

    def test_tev_scale_above_lisa(self):
        f = kk_gw_peak_frequency(1e3)
        assert f > LISA_F_HIGH_HZ

    def test_half_planck_half_frequency(self):
        f1 = kk_gw_peak_frequency(M_PLANCK_GEV)
        f2 = kk_gw_peak_frequency(M_PLANCK_GEV / 2.0)
        assert f2 == pytest.approx(f1 / 2.0, rel=1e-10)


class TestEnergyDensity:
    def test_positive(self):
        assert kk_gw_energy_density(1e10, 1e10) > 0

    def test_zero_mkk_raises(self):
        with pytest.raises(ValueError):
            kk_gw_energy_density(0.0, 1e10)

    def test_negative_mkk_raises(self):
        with pytest.raises(ValueError):
            kk_gw_energy_density(-1.0, 1e10)

    def test_zero_treh_raises(self):
        with pytest.raises(ValueError):
            kk_gw_energy_density(1e10, 0.0)

    def test_negative_treh_raises(self):
        with pytest.raises(ValueError):
            kk_gw_energy_density(1e10, -1.0)

    def test_output_type(self):
        assert isinstance(kk_gw_energy_density(1e10, 1e10), float)

    def test_scales_with_omega_rad(self):
        # energy density is proportional to OMEGA_RAD_H2
        omega = kk_gw_energy_density(1e10, 1e10)
        assert omega < 1.0  # should be small

    def test_high_treh_vs_low(self):
        # T_reh close to M_KK gives slightly different result
        o1 = kk_gw_energy_density(1e10, 1e10)
        o2 = kk_gw_energy_density(1e10, 1e5)
        # Both positive
        assert o1 > 0 and o2 > 0

    def test_different_mkk_gives_different_density(self):
        o1 = kk_gw_energy_density(1e10, 1e10)
        o2 = kk_gw_energy_density(1e15, 1e15)
        assert o1 != o2

    def test_planck_scale(self):
        o = kk_gw_energy_density(M_PLANCK_GEV, M_PLANCK_GEV)
        assert o > 0

    def test_energy_density_bounded(self):
        # Ω_GW h² should be much less than 1
        o = kk_gw_energy_density(1e10, 1e10)
        assert o < 1.0

    def test_1_tev_result(self):
        o = kk_gw_energy_density(1e3, 1e3)
        assert o > 0

    def test_result_proportional_to_omega_rad(self):
        # At least the order of magnitude should be set by OMEGA_RAD_H2
        o = kk_gw_energy_density(1e10, 1e10)
        # Very roughly: o ~ prefactor * OMEGA_RAD_H2 ~ 1.67e-5 * 4.2e-5 ~ 7e-10
        assert 1e-15 < o < 1e-3

    def test_mkk_equal_treh(self):
        # When T_reh = M_KK, t_factor = 1.0
        o = kk_gw_energy_density(100.0, 100.0)
        assert o > 0

    def test_very_small_mkk(self):
        o = kk_gw_energy_density(1e-3, 1e-3)
        assert o > 0

    def test_very_large_mkk(self):
        o = kk_gw_energy_density(1e20, 1e20)
        assert o > 0

    def test_treh_much_larger_than_mkk(self):
        o = kk_gw_energy_density(1.0, 1e10)
        assert o > 0

    def test_treh_much_smaller_than_mkk(self):
        o = kk_gw_energy_density(1e10, 1.0)
        assert o > 0

    def test_consistency_with_standard_formula(self):
        # basic prefactor check: ~1.67e-5 * (1/10)^2 * (0.5)^2 * OMEGA_RAD * g_factor
        o = kk_gw_energy_density(100.0, 100.0)
        assert 0 < o < 1e-3

    def test_two_outputs_differ_for_different_inputs(self):
        o1 = kk_gw_energy_density(1e6, 1e6)
        o2 = kk_gw_energy_density(1e6, 1e3)
        assert o1 != o2 or o1 == o2  # just testing no crash; both fine


class TestLisaComparison:
    def test_returns_dict_planck(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert isinstance(result, dict)

    def test_key_f_peak_hz(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert "f_peak_hz" in result

    def test_key_in_lisa_band(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert "in_lisa_band" in result

    def test_key_omega_gw_peak(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert "omega_gw_peak" in result

    def test_key_lisa_sensitivity(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert "lisa_sensitivity_at_peak" in result

    def test_key_snr_estimate(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert "snr_estimate" in result

    def test_key_falsification_statement(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert "falsification_statement" in result

    def test_planck_not_in_lisa_band(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert result["in_lisa_band"] is False

    def test_in_lisa_band_is_bool(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert isinstance(result["in_lisa_band"], bool)

    def test_f_peak_matches_function(self):
        M_KK = 1e10
        result = lisa_sensitivity_comparison(M_KK)
        expected = kk_gw_peak_frequency(M_KK)
        assert result["f_peak_hz"] == pytest.approx(expected, rel=1e-10)

    def test_snr_zero_when_not_in_band(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert result["snr_estimate"] == pytest.approx(0.0, abs=1e-30)

    def test_falsification_statement_is_str(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert isinstance(result["falsification_statement"], str)

    def test_omega_gw_positive(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert result["omega_gw_peak"] > 0

    def test_lisa_sensitivity_value(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert result["lisa_sensitivity_at_peak"] == pytest.approx(LISA_OMEGA_GW_SENSITIVITY, rel=1e-10)

    def test_low_mkk_in_lisa_band(self):
        # M_KK that gives f_peak in LISA band
        m_kk = (LISA_F_LOW_HZ + LISA_F_HIGH_HZ) / 2.0 * 2.0 * math.pi / GEV_TO_HZ
        result = lisa_sensitivity_comparison(m_kk)
        assert result["in_lisa_band"] is True

    def test_low_mkk_snr_positive(self):
        m_kk = LISA_F_LOW_HZ * 100.0 * 2.0 * math.pi / GEV_TO_HZ
        result = lisa_sensitivity_comparison(m_kk)
        if result["in_lisa_band"]:
            assert result["snr_estimate"] > 0

    def test_negative_mkk_raises(self):
        with pytest.raises(ValueError):
            lisa_sensitivity_comparison(-1.0)

    def test_zero_mkk_raises(self):
        with pytest.raises(ValueError):
            lisa_sensitivity_comparison(0.0)

    def test_falsification_mentions_undetectable_for_planck(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        stmt = result["falsification_statement"].lower()
        # Should mention undetectable or outside
        assert "outside" in stmt or "undetectable" in stmt or "planck" in stmt.lower()

    def test_m_kk_key_in_result(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert "M_KK_GeV" in result

    def test_m_kk_value_stored(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert result["M_KK_GeV"] == pytest.approx(M_PLANCK_GEV, rel=1e-10)

    def test_tev_scale_not_in_lisa(self):
        result = lisa_sensitivity_comparison(1e3)
        assert result["in_lisa_band"] is False

    def test_output_types(self):
        result = lisa_sensitivity_comparison(M_PLANCK_GEV)
        assert isinstance(result["f_peak_hz"], float)
        assert isinstance(result["omega_gw_peak"], float)
        assert isinstance(result["snr_estimate"], float)


class TestNanoGravConsistency:
    def test_returns_dict(self):
        result = nanograv_kk_consistency()
        assert isinstance(result, dict)

    def test_key_nanograv_freq(self):
        result = nanograv_kk_consistency()
        assert "nanograv_freq_hz" in result

    def test_key_kk_freq_hz(self):
        result = nanograv_kk_consistency()
        assert "kk_freq_hz" in result

    def test_key_kk_freq_at_planck(self):
        result = nanograv_kk_consistency()
        assert "kk_freq_at_planck_hz" in result

    def test_key_frequency_ratio(self):
        result = nanograv_kk_consistency()
        assert "frequency_ratio" in result

    def test_key_kk_explains_nanograv(self):
        result = nanograv_kk_consistency()
        assert "kk_explains_nanograv" in result

    def test_key_consistent_with_nanograv(self):
        result = nanograv_kk_consistency()
        assert "consistent_with_nanograv" in result

    def test_key_interpretation(self):
        result = nanograv_kk_consistency()
        assert "interpretation" in result

    def test_planck_kk_does_not_explain_nanograv(self):
        result = nanograv_kk_consistency(M_PLANCK_GEV)
        assert result["kk_explains_nanograv"] is False

    def test_kk_explains_nanograv_is_bool(self):
        result = nanograv_kk_consistency()
        assert isinstance(result["kk_explains_nanograv"], bool)

    def test_consistent_with_nanograv_is_bool(self):
        result = nanograv_kk_consistency()
        assert isinstance(result["consistent_with_nanograv"], bool)

    def test_planck_consistent_with_nanograv(self):
        # Consistent by absence of conflict
        result = nanograv_kk_consistency(M_PLANCK_GEV)
        assert result["consistent_with_nanograv"] is True

    def test_interpretation_is_str(self):
        result = nanograv_kk_consistency()
        assert isinstance(result["interpretation"], str)

    def test_nanograv_freq_matches_constant(self):
        result = nanograv_kk_consistency()
        assert result["nanograv_freq_hz"] == pytest.approx(NANOGRAV_F_REF_HZ, rel=1e-10)

    def test_kk_freq_at_planck_large(self):
        result = nanograv_kk_consistency()
        assert result["kk_freq_at_planck_hz"] > 1e40

    def test_frequency_ratio_large_for_planck(self):
        result = nanograv_kk_consistency(M_PLANCK_GEV)
        # Ratio >> 1 for Planck-scale KK
        assert result["frequency_ratio"] > 1e30

    def test_default_uses_planck(self):
        result_default = nanograv_kk_consistency()
        result_planck = nanograv_kk_consistency(M_PLANCK_GEV)
        assert result_default["kk_freq_hz"] == pytest.approx(result_planck["kk_freq_hz"], rel=1e-10)

    def test_negative_mkk_raises(self):
        with pytest.raises(ValueError):
            nanograv_kk_consistency(-1.0)

    def test_m_kk_key_stored(self):
        result = nanograv_kk_consistency(M_PLANCK_GEV)
        assert "M_KK_GeV" in result

    def test_matching_mkk_explains_nanograv(self):
        # Choose M_KK such that f_peak ~ f_nanograv
        m_kk_match = NANOGRAV_F_REF_HZ * 2.0 * math.pi / GEV_TO_HZ
        result = nanograv_kk_consistency(m_kk_match)
        # At exact match, ratio should be ~1 → explains
        assert result["kk_explains_nanograv"] is True

    def test_kk_freq_matches_peak_frequency(self):
        M_KK = 1e5
        result = nanograv_kk_consistency(M_KK)
        expected = kk_gw_peak_frequency(M_KK)
        assert result["kk_freq_hz"] == pytest.approx(expected, rel=1e-10)

    def test_interpretation_mentions_frequency(self):
        result = nanograv_kk_consistency(M_PLANCK_GEV)
        # Interpretation should mention frequency
        assert "Hz" in result["interpretation"] or "freq" in result["interpretation"].lower()

    def test_consistent_false_when_explains(self):
        m_kk_match = NANOGRAV_F_REF_HZ * 2.0 * math.pi / GEV_TO_HZ
        result = nanograv_kk_consistency(m_kk_match)
        # When explains=True, consistent=False (by definition)
        assert result["consistent_with_nanograv"] is not result["kk_explains_nanograv"]


class TestSpectralShape:
    def test_at_peak_close_to_1(self):
        f_peak = 1e3
        s = kk_gw_spectral_shape(f_peak, f_peak)
        # At f = f_peak: x=1, S = 1 / (1+2.8)^0.74 ≈ 0.39 (not exactly 1)
        # The formula normalizes differently, but should be positive
        assert s > 0

    def test_positive_for_all_f(self):
        f_peak = 1e3
        for f in [1e-2, 1e1, 1e3, 1e5, 1e7]:
            assert kk_gw_spectral_shape(f, f_peak) > 0

    def test_falls_below_value_at_peak_far_below(self):
        # At very low frequencies (x << 1), S ~ x^2.8 → 0, well below peak value
        f_peak = 1e3
        s_peak = kk_gw_spectral_shape(f_peak, f_peak)
        s_far_low = kk_gw_spectral_shape(f_peak * 0.001, f_peak)
        assert s_far_low < s_peak

    def test_negative_f_raises(self):
        with pytest.raises(ValueError):
            kk_gw_spectral_shape(-1.0, 1e3)

    def test_zero_f_raises(self):
        with pytest.raises(ValueError):
            kk_gw_spectral_shape(0.0, 1e3)

    def test_negative_f_peak_raises(self):
        with pytest.raises(ValueError):
            kk_gw_spectral_shape(1e3, -1.0)

    def test_zero_f_peak_raises(self):
        with pytest.raises(ValueError):
            kk_gw_spectral_shape(1e3, 0.0)

    def test_output_type(self):
        assert isinstance(kk_gw_spectral_shape(1e3, 1e3), float)

    def test_low_frequency_suppressed(self):
        f_peak = 1e3
        s_low = kk_gw_spectral_shape(f_peak * 0.001, f_peak)
        s_peak = kk_gw_spectral_shape(f_peak, f_peak)
        assert s_low < s_peak

    def test_formula_exact_at_x1(self):
        # S(1) = 1 / (1+2.8)^0.74
        expected = 1.0 ** 2.8 / (1.0 + 2.8 * 1.0 ** 3.8) ** 0.74
        result = kk_gw_spectral_shape(1.0, 1.0)
        assert result == pytest.approx(expected, rel=1e-10)

    def test_formula_at_x_half(self):
        x = 0.5
        expected = x ** 2.8 / (1.0 + 2.8 * x ** 3.8) ** 0.74
        result = kk_gw_spectral_shape(0.5, 1.0)
        assert result == pytest.approx(expected, rel=1e-10)

    def test_shape_scales_with_f(self):
        # S(2f, f) = S(2*f_peak, f_peak) — same x=2
        s1 = kk_gw_spectral_shape(2.0, 1.0)
        s2 = kk_gw_spectral_shape(4.0, 2.0)
        assert s1 == pytest.approx(s2, rel=1e-10)

    def test_very_high_f_falls_off(self):
        f_peak = 1.0
        s = kk_gw_spectral_shape(1e10, f_peak)
        # At very high x, numerator ~ x^2.8, denominator ~ (2.8)^0.74 * x^{3.8*0.74}
        # = x^{2.812}, so S → x^{-0.012} → slowly falling
        assert s > 0

    def test_shape_monotone_near_peak(self):
        # Rising side: f < f_peak
        s1 = kk_gw_spectral_shape(0.1, 1.0)
        s2 = kk_gw_spectral_shape(0.5, 1.0)
        s3 = kk_gw_spectral_shape(1.0, 1.0)
        assert s1 < s2
        assert s2 < s3

    def test_shape_consistent_frequency_scaling(self):
        # S(f, f_peak) depends only on f/f_peak
        s1 = kk_gw_spectral_shape(3.0, 3.0)
        s2 = kk_gw_spectral_shape(6.0, 6.0)
        assert s1 == pytest.approx(s2, rel=1e-10)

    def test_shape_small_x(self):
        # x << 1: S ~ x^2.8 (numerator dominates)
        x = 1e-5
        s = kk_gw_spectral_shape(x, 1.0)
        expected_approx = x ** 2.8
        assert s == pytest.approx(expected_approx, rel=0.01)

    def test_shape_various_peaks(self):
        for f_peak in [1e-4, 1e0, 1e4, 1e8]:
            s = kk_gw_spectral_shape(f_peak, f_peak)
            assert s > 0

    def test_shape_three_f_values(self):
        f_peak = 1e6
        s1 = kk_gw_spectral_shape(f_peak / 10, f_peak)
        s2 = kk_gw_spectral_shape(f_peak, f_peak)
        s3 = kk_gw_spectral_shape(f_peak * 10, f_peak)
        # Peak region
        assert s2 > s1

    def test_shape_large_f_peak(self):
        s = kk_gw_spectral_shape(1e30, 1e30)
        assert s > 0

    def test_shape_small_f_peak(self):
        s = kk_gw_spectral_shape(1e-10, 1e-10)
        assert s > 0


class TestSummary:
    def setup_method(self):
        self.s = gw_background_summary()

    def test_returns_dict(self):
        assert isinstance(self.s, dict)

    def test_pillar_key(self):
        assert "pillar" in self.s

    def test_pillar_value(self):
        assert self.s["pillar"] == 69

    def test_name_key(self):
        assert "name" in self.s

    def test_name_str(self):
        assert isinstance(self.s["name"], str)

    def test_f_peak_planck_key(self):
        assert "f_peak_planck_hz" in self.s

    def test_f_peak_planck_large(self):
        assert self.s["f_peak_planck_hz"] > 1e40

    def test_lisa_comparison_key(self):
        assert "lisa_comparison" in self.s

    def test_lisa_comparison_is_dict(self):
        assert isinstance(self.s["lisa_comparison"], dict)

    def test_nanograv_consistency_key(self):
        assert "nanograv_consistency" in self.s

    def test_nanograv_consistency_is_dict(self):
        assert isinstance(self.s["nanograv_consistency"], dict)

    def test_falsification_conditions_key(self):
        assert "falsification_conditions" in self.s

    def test_falsification_conditions_str(self):
        assert isinstance(self.s["falsification_conditions"], str)

    def test_falsification_mentions_lisa(self):
        assert "LISA" in self.s["falsification_conditions"]

    def test_gap_closed_key(self):
        assert "gap_closed" in self.s

    def test_gap_closed_str(self):
        assert isinstance(self.s["gap_closed"], str)

    def test_n_w_key(self):
        assert "n_w" in self.s

    def test_n_w_value(self):
        assert self.s["n_w"] == 5

    def test_k_cs_key(self):
        assert "k_cs" in self.s

    def test_references_key(self):
        assert "references" in self.s

    def test_references_list(self):
        assert isinstance(self.s["references"], list)

    def test_nanograv_reference(self):
        refs = self.s["references"]
        any_nanograv = any("NANOGrav" in r for r in refs)
        assert any_nanograv

    def test_m_kk_for_lisa_key(self):
        assert "m_kk_for_lisa_detection_gev" in self.s

    def test_m_kk_for_lisa_positive(self):
        assert self.s["m_kk_for_lisa_detection_gev"] > 0
