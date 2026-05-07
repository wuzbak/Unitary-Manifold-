# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for GW Strain Architecture Limit (Pillar 222, Track A Session 5)."""

import math
import pytest

from src.core.gw_architecture_limit import (
    N_W, K_CS,
    M_PL_GEV, PI_KR, M_KK_GEV,
    R_BRAIDED, H_INF_GEV,
    H_STRAIN_LIGO_BAND,
    LIGO_SENSITIVITY,
    LIGO_STRAIN_GAP_LOG10,
    OMEGA_GW_STOCHASTIC,
    LISA_SENSITIVITY_OMEGA,
    ARCHITECTURE_LIMIT_LIGO,
    STOCHASTIC_TESTABLE,
    kk_characteristic_strain,
    stochastic_gw_background,
    ligo_gap_analysis,
    lisa_testability_analysis,
    gw_architecture_limit_audit,
    pillar222_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_r_braided_value(self):
        assert R_BRAIDED == pytest.approx(0.0315)

    def test_r_braided_below_bicep_limit(self):
        assert R_BRAIDED < 0.036

    def test_h_inf_gev_positive(self):
        assert H_INF_GEV > 0

    def test_h_inf_gev_is_gut_scale(self):
        # GUT-scale inflation: H_inf ~ 10^{13-14} GeV
        assert 1e12 < H_INF_GEV < 1e16

    def test_h_strain_ligo_tiny(self):
        # KK-graviton strain must be MUCH smaller than LIGO sensitivity
        assert H_STRAIN_LIGO_BAND < LIGO_SENSITIVITY

    def test_ligo_sensitivity_value(self):
        # LIGO O4: ~3e-24 at 100 Hz
        assert 1e-25 < LIGO_SENSITIVITY < 1e-22

    def test_ligo_gap_is_significant(self):
        # KK-graviton strain is significantly below LIGO sensitivity
        assert LIGO_STRAIN_GAP_LOG10 > 8

    def test_omega_gw_positive(self):
        assert OMEGA_GW_STOCHASTIC > 0

    def test_architecture_limit_ligo_true(self):
        assert ARCHITECTURE_LIMIT_LIGO is True

    def test_stochastic_testable_is_bool(self):
        assert isinstance(STOCHASTIC_TESTABLE, bool)


class TestKKCharacteristicStrain:
    def test_returns_dict(self):
        result = kk_characteristic_strain()
        assert isinstance(result, dict)

    def test_h_c_positive(self):
        result = kk_characteristic_strain()
        assert result["h_c"] > 0

    def test_gap_is_significant(self):
        result = kk_characteristic_strain()
        assert result["gap_orders_of_magnitude"] > 8

    def test_architecture_limit_at_100hz(self):
        result = kk_characteristic_strain(f_hz=100.0)
        assert result["architecture_limit"] is True

    def test_different_frequencies_give_different_strain(self):
        r100 = kk_characteristic_strain(f_hz=100.0)
        r10 = kk_characteristic_strain(f_hz=10.0)
        assert r100["h_c"] != r10["h_c"]


class TestStochasticGWBackground:
    def test_returns_dict(self):
        result = stochastic_gw_background()
        assert isinstance(result, dict)

    def test_omega_gw_positive(self):
        result = stochastic_gw_background()
        assert result["omega_gw"] > 0

    def test_n_t_small_and_negative(self):
        result = stochastic_gw_background()
        assert -0.01 < result["n_T"] < 0  # small negative tensor tilt

    def test_has_testable_flag(self):
        result = stochastic_gw_background()
        assert "testable_at_lisa" in result

    def test_different_r_changes_spectrum(self):
        r1 = stochastic_gw_background(r=0.0315)
        r2 = stochastic_gw_background(r=0.01)
        assert r1["omega_gw"] != r2["omega_gw"]


class TestLIGOGapAnalysis:
    def test_returns_dict(self):
        result = ligo_gap_analysis()
        assert isinstance(result, dict)

    def test_architecture_limit_true(self):
        result = ligo_gap_analysis()
        assert result["architecture_limit"] is True

    def test_gap_log10_large(self):
        result = ligo_gap_analysis()
        assert result["gap_log10"] > 8

    def test_limit_type_technology(self):
        result = ligo_gap_analysis()
        assert "TECHNOLOGY" in result["limit_type"]

    def test_requires_dimension_none(self):
        result = ligo_gap_analysis()
        assert result["requires_dimension"] is None

    def test_honest_statement_present(self):
        result = ligo_gap_analysis()
        assert len(result["honest_statement"]) > 50


class TestLISATestabilityAnalysis:
    def test_returns_dict(self):
        result = lisa_testability_analysis()
        assert isinstance(result, dict)

    def test_omega_gw_positive(self):
        result = lisa_testability_analysis()
        assert result["omega_gw_predicted"] > 0

    def test_has_timeline(self):
        result = lisa_testability_analysis()
        assert "2035" in result["timeline"] or "LISA" in result["timeline"]

    def test_falsification_condition_present(self):
        result = lisa_testability_analysis()
        assert len(result["falsification_condition"]) > 20


class TestGWArchitectureLimitAudit:
    def test_returns_dict(self):
        result = gw_architecture_limit_audit()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = gw_architecture_limit_audit()
        assert result["pillar"] == 222

    def test_has_ligo_and_lisa(self):
        result = gw_architecture_limit_audit()
        assert "ligo_gap" in result
        assert "lisa_testability" in result

    def test_verdict_present(self):
        result = gw_architecture_limit_audit()
        assert len(result["verdict"]) > 50


class TestPillar222Summary:
    def test_returns_dict(self):
        s = pillar222_summary()
        assert isinstance(s, dict)

    def test_pillar_number(self):
        s = pillar222_summary()
        assert s["pillar"] == 222

    def test_architecture_limit_ligo_true(self):
        s = pillar222_summary()
        assert s["architecture_limit_ligo"] is True

    def test_ligo_gap_large(self):
        s = pillar222_summary()
        assert s["ligo_gap_log10"] > 8
