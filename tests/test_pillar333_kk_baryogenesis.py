# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 333 — KK Phase Transition Baryogenesis."""
import math
import pytest

from src.core.pillar333_kk_baryogenesis import (
    N_W, K_CS, PI_KR,
    M_PL_GEV, M_KK_GEV,
    T_KK_GEV, T_EW_GEV, ALPHA_KK, V_W,
    DELTA_CP_LEPTONIC_RAD, JARLSKOG_INVARIANT,
    ETA_B_OBSERVED,
    separation_guard,
    sphaleron_rate_at_temperature,
    sphaleron_active_at_t_kk,
    cp_asymmetric_factor,
    kk_baryogenesis_naive_estimate,
    washout_factor_estimate,
    eta_b_with_washout,
    compare_to_observed,
    sakharov_conditions_check,
    kk_baryogenesis_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-9

    def test_m_kk_order(self):
        # M_KK ~ 1 TeV = 1000 GeV
        assert 100.0 < M_KK_GEV < 1e5

    def test_t_kk_equals_m_kk(self):
        assert abs(T_KK_GEV - M_KK_GEV) < 1e-6

    def test_t_ew(self):
        assert abs(T_EW_GEV - 100.0) < 1e-10

    def test_alpha_kk(self):
        assert abs(ALPHA_KK - PI_KR ** 2 / 100.0) < 1e-9

    def test_v_w(self):
        assert abs(V_W - 1.0) < 1e-10

    def test_delta_cp_range(self):
        assert 0 < DELTA_CP_LEPTONIC_RAD < math.pi

    def test_jarlskog_order(self):
        # J_CP ~ 3e-5
        assert 1e-6 < JARLSKOG_INVARIANT < 1e-3

    def test_eta_b_observed(self):
        assert abs(ETA_B_OBSERVED - 6.10e-10) < 1e-12


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()

    def test_mentions_pillar_323(self):
        guard = separation_guard()
        assert "323" in guard


class TestSphaleronRate:
    def test_active_above_ew(self):
        rate = sphaleron_rate_at_temperature(200.0)  # T > T_EW = 130 GeV
        assert rate > 0

    def test_suppressed_below_ew(self):
        rate_above = sphaleron_rate_at_temperature(200.0)
        rate_below = sphaleron_rate_at_temperature(10.0)  # T << T_EW
        assert rate_below < rate_above

    def test_rate_at_t_kk(self):
        rate = sphaleron_rate_at_temperature(T_KK_GEV)
        assert rate > 0

    def test_scales_with_t4(self):
        # Above T_EW: Γ ~ α_W^5 T^4 → T doubled gives 16× rate
        r1 = sphaleron_rate_at_temperature(200.0)
        r2 = sphaleron_rate_at_temperature(400.0)
        # Should be approximately 16× (some minor deviation from alpha_W running)
        ratio = r2 / r1
        assert 10.0 < ratio < 25.0


class TestSphaleronActive:
    def test_returns_dict(self):
        result = sphaleron_active_at_t_kk()
        assert isinstance(result, dict)

    def test_t_kk_sphalerons_active(self):
        result = sphaleron_active_at_t_kk()
        assert result["sphalerons_active"] is True

    def test_ratio_large_at_t_kk(self):
        result = sphaleron_active_at_t_kk()
        # Should be >> 1 (sphalerons much faster than Hubble)
        assert result["ratio_gamma_over_H"] > 1.0

    def test_has_conclusion(self):
        result = sphaleron_active_at_t_kk()
        assert "conclusion" in result
        assert "ACTIVE" in result["conclusion"]


class TestCPAsymmetricFactor:
    def test_returns_dict(self):
        result = cp_asymmetric_factor()
        assert isinstance(result, dict)

    def test_sin_delta_positive(self):
        result = cp_asymmetric_factor()
        assert result["sin_delta_cp"] > 0

    def test_sin_delta_range(self):
        result = cp_asymmetric_factor()
        assert 0 < result["sin_delta_cp"] < 1

    def test_mass_ratio_sq_positive(self):
        result = cp_asymmetric_factor()
        assert result["mass_ratio_sq"] > 0

    def test_cp_factor_positive(self):
        result = cp_asymmetric_factor()
        assert result["cp_factor"] > 0

    def test_cp_factor_less_than_one(self):
        # (m_t/T_KK)² < 1 since T_KK ~ M_t for UM
        result = cp_asymmetric_factor()
        assert result["cp_factor"] < 1.0


class TestNaiveEstimate:
    def test_returns_float(self):
        result = kk_baryogenesis_naive_estimate()
        assert isinstance(result, float)

    def test_positive(self):
        result = kk_baryogenesis_naive_estimate()
        assert result > 0

    def test_finite(self):
        result = kk_baryogenesis_naive_estimate()
        assert math.isfinite(result)

    def test_scales_with_cp(self):
        r1 = kk_baryogenesis_naive_estimate(delta_cp=0.1)
        r2 = kk_baryogenesis_naive_estimate(delta_cp=1.0)
        # Larger CP → larger asymmetry
        assert r2 > r1


class TestWashoutFactor:
    def test_returns_dict(self):
        result = washout_factor_estimate()
        assert isinstance(result, dict)

    def test_washout_range_valid(self):
        result = washout_factor_estimate()
        assert result["washout_range_low"] < result["washout_range_high"]

    def test_t_ratio_less_than_one(self):
        result = washout_factor_estimate()
        # T_EW / T_KK << 1
        assert result["t_ratio"] < 1.0

    def test_sphaleron_conversion(self):
        result = washout_factor_estimate()
        assert abs(result["sphaleron_l_to_b_conversion"] - 8.0 / 23.0) < 1e-10

    def test_net_washout_range(self):
        result = washout_factor_estimate()
        assert result["net_washout_factor_low"] < result["net_washout_factor_high"]


class TestEtaBWithWashout:
    def test_returns_dict(self):
        result = eta_b_with_washout()
        assert isinstance(result, dict)

    def test_all_eta_positive(self):
        result = eta_b_with_washout()
        assert result["eta_b_naive"] > 0
        assert result["eta_b_central"] > 0
        assert result["eta_b_low"] > 0
        assert result["eta_b_high"] > 0

    def test_low_lt_central_lt_high(self):
        result = eta_b_with_washout()
        assert result["eta_b_low"] < result["eta_b_central"]
        assert result["eta_b_central"] < result["eta_b_high"]

    def test_central_is_naive_times_washout(self):
        washout = 1e-3
        result = eta_b_with_washout(washout_central=washout)
        expected = result["eta_b_naive"] * washout * 8.0 / 23.0
        # Use relative tolerance for floating-point values at ~1e-12 scale
        assert abs(result["eta_b_central"] - expected) < 1e-20 * abs(expected) + 1e-25

    def test_has_observed_reference(self):
        result = eta_b_with_washout()
        assert abs(result["eta_b_observed"] - ETA_B_OBSERVED) < 1e-15


class TestCompareToObserved:
    def test_returns_dict(self):
        result = compare_to_observed()
        assert isinstance(result, dict)

    def test_has_verdict(self):
        result = compare_to_observed()
        assert "verdict" in result

    def test_has_eta_b_range(self):
        result = compare_to_observed()
        assert "eta_b_um_with_washout_range" in result
        lo, hi = result["eta_b_um_with_washout_range"]
        assert lo < hi

    def test_status_is_viable(self):
        result = compare_to_observed()
        assert "VIABLE" in result["status"] or "CONSISTENT" in result["status"]

    def test_dominant_uncertainty_mentioned(self):
        result = compare_to_observed()
        assert "dominant_uncertainty" in result


class TestSakharovConditions:
    def test_returns_dict(self):
        result = sakharov_conditions_check()
        assert isinstance(result, dict)

    def test_three_conditions(self):
        result = sakharov_conditions_check()
        assert "condition_1_baryon_violation" in result
        assert "condition_2_cp_violation" in result
        assert "condition_3_non_equilibrium" in result

    def test_all_three_satisfied(self):
        result = sakharov_conditions_check()
        assert result["condition_1_baryon_violation"]["status"] == "SATISFIED"
        assert result["condition_2_cp_violation"]["status"] == "SATISFIED"
        assert result["condition_3_non_equilibrium"]["status"] == "SATISFIED"

    def test_overall_verdict_present(self):
        result = sakharov_conditions_check()
        assert "overall_verdict" in result

    def test_cp_sin_matches(self):
        result = sakharov_conditions_check()
        sin_delta = result["condition_2_cp_violation"]["sin_delta_cp"]
        expected = math.sin(DELTA_CP_LEPTONIC_RAD)
        assert abs(sin_delta - expected) < 1e-10

    def test_non_eq_alpha_correct(self):
        result = sakharov_conditions_check()
        alpha = result["condition_3_non_equilibrium"]["alpha_strength"]
        assert abs(alpha - ALPHA_KK) < 1e-9


class TestFullReport:
    def test_returns_dict(self):
        r = kk_baryogenesis_full_report()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = kk_baryogenesis_full_report()
        assert r["pillar"] == 333

    def test_mechanism_description(self):
        r = kk_baryogenesis_full_report()
        assert "mechanism" in r
        assert "1 TeV" in r["mechanism"] or "TeV" in r["mechanism"]

    def test_all_sakharov_satisfied(self):
        r = kk_baryogenesis_full_report()
        sakh = r["sakharov_conditions"]
        assert sakh["condition_1_baryon_violation"]["status"] == "SATISFIED"
        assert sakh["condition_2_cp_violation"]["status"] == "SATISFIED"
        assert sakh["condition_3_non_equilibrium"]["status"] == "SATISFIED"

    def test_status_viable(self):
        r = kk_baryogenesis_full_report()
        assert "VIABLE" in r["status"]

    def test_has_open_calculations(self):
        r = kk_baryogenesis_full_report()
        assert "open_calculations" in r
        assert len(r["open_calculations"]) > 0

    def test_honest_assessment_present(self):
        r = kk_baryogenesis_full_report()
        assert "honest_assessment" in r

    def test_connection_to_pillar323(self):
        r = kk_baryogenesis_full_report()
        assert "connection_to_pillar323" in r
        assert "323" in r["connection_to_pillar323"]

    def test_adjacency_label(self):
        r = kk_baryogenesis_full_report()
        assert "ADJACENT" in r["adjacency"]
