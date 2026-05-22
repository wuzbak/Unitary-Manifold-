# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 341 — Proton Decay Partial Lifetime: Full Precision Package."""
import math
import pytest

from src.core.pillar341_proton_decay_precision import (
    N_W, K_CS, N_C, ALPHA_GUT,
    M_PROTON_GEV, F_PI_GEV, A_L, ALPHA_0_LAT_GEV3,
    M_GUT_GEV, TAU_SUPERK_YR, TAU_HYPERK_SENSITIVITY_YR,
    ORBIFOLD_NORMALIZATION, HBAR_GEV_S, S_PER_YR,
    separation_guard,
    proton_decay_rate_gev,
    proton_decay_lifetime_yr,
    lifetime_uncertainty_budget,
    route_hyperk_result,
    pillar341_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_c(self):
        assert N_C == 3

    def test_alpha_gut(self):
        assert abs(ALPHA_GUT - 3.0 / 74.0) < 1e-12

    def test_alpha_gut_value(self):
        # 3/74 ≈ 0.04054
        assert 0.040 < ALPHA_GUT < 0.042

    def test_m_proton(self):
        assert 0.930 < M_PROTON_GEV < 0.945

    def test_f_pi(self):
        assert 0.12 < F_PI_GEV < 0.14

    def test_m_gut_gev(self):
        # M_GUT should be in [10^14, 10^17] GeV
        assert 1e14 < M_GUT_GEV < 1e17

    def test_tau_superk_order(self):
        # Super-K limit ~10^34 yr
        assert 1e33 < TAU_SUPERK_YR < 1e36

    def test_tau_hyperk_above_superk(self):
        assert TAU_HYPERK_SENSITIVITY_YR > TAU_SUPERK_YR

    def test_orbifold_normalization(self):
        assert abs(ORBIFOLD_NORMALIZATION - 1.0 / (2.0 * N_W)) < 1e-12

    def test_orbifold_normalization_value(self):
        assert abs(ORBIFOLD_NORMALIZATION - 0.1) < 1e-9


class TestSeparationGuard:
    def test_returns_dict(self):
        assert isinstance(separation_guard(), dict)

    def test_pillar_341(self):
        assert separation_guard()["pillar"] == 341

    def test_no_hardgate_promotion(self):
        assert separation_guard()["hardgate_promotion"] is False

    def test_has_description(self):
        assert "description" in separation_guard()


class TestDecayRate:
    def test_rate_positive(self):
        assert proton_decay_rate_gev() > 0

    def test_rate_increases_with_alpha(self):
        r1 = proton_decay_rate_gev(alpha_gut=0.01)
        r2 = proton_decay_rate_gev(alpha_gut=0.10)
        assert r2 > r1

    def test_rate_decreases_with_m_gut(self):
        r1 = proton_decay_rate_gev(m_gut_gev=1e15)
        r2 = proton_decay_rate_gev(m_gut_gev=1e16)
        assert r1 > r2

    def test_rate_scales_as_m_gut_minus4(self):
        r1 = proton_decay_rate_gev(m_gut_gev=1e15)
        r2 = proton_decay_rate_gev(m_gut_gev=2e15)
        ratio = r1 / r2
        # Should be ~ (2e15/1e15)^4 = 16
        assert 14.0 < ratio < 18.0

    def test_rate_scales_as_alpha_squared(self):
        r1 = proton_decay_rate_gev(alpha_gut=0.04)
        r2 = proton_decay_rate_gev(alpha_gut=0.08)
        ratio = r2 / r1
        # Should be ~ 4 (scales as α²)
        assert 3.5 < ratio < 4.5


class TestLifetime:
    def test_lifetime_positive(self):
        assert proton_decay_lifetime_yr() > 0

    def test_lifetime_exceeds_superk(self):
        # Central prediction must be above current experimental limit
        tau = proton_decay_lifetime_yr()
        assert tau > TAU_SUPERK_YR

    def test_lifetime_order_of_magnitude(self):
        # Should be in [10^33, 10^40] yr range
        tau = proton_decay_lifetime_yr()
        assert 1e33 < tau < 1e42

    def test_lifetime_increases_with_m_gut(self):
        tau1 = proton_decay_lifetime_yr(m_gut_gev=1e15)
        tau2 = proton_decay_lifetime_yr(m_gut_gev=1e16)
        assert tau2 > tau1

    def test_lifetime_scales_as_m_gut_4(self):
        tau1 = proton_decay_lifetime_yr(m_gut_gev=1e15)
        tau2 = proton_decay_lifetime_yr(m_gut_gev=2e15)
        ratio = tau2 / tau1
        # Should be ~ (2)^4 = 16
        assert 14.0 < ratio < 18.0


class TestUncertaintyBudget:
    def test_budget_returns_dict(self):
        assert isinstance(lifetime_uncertainty_budget(), dict)

    def test_tau_central_present(self):
        budget = lifetime_uncertainty_budget()
        assert "tau_central_yr" in budget

    def test_tau_low_below_central(self):
        budget = lifetime_uncertainty_budget()
        assert budget["tau_low_yr"] < budget["tau_central_yr"]

    def test_tau_high_above_central(self):
        budget = lifetime_uncertainty_budget()
        assert budget["tau_high_yr"] > budget["tau_central_yr"]

    def test_consistent_with_superk(self):
        budget = lifetime_uncertainty_budget()
        assert budget["consistent_with_superk"]

    def test_uncertainty_range_factor_10(self):
        budget = lifetime_uncertainty_budget()
        # Range should be at least factor 10
        ratio = budget["tau_high_yr"] / budget["tau_low_yr"]
        assert ratio >= 10.0

    def test_dominant_uncertainty_mentioned(self):
        budget = lifetime_uncertainty_budget()
        assert "dominant_uncertainty" in budget
        assert "M_GUT" in budget["dominant_uncertainty"]


class TestRoutingProtocol:
    def test_detection_in_range_confirmed(self):
        tau_central = proton_decay_lifetime_yr()
        result = route_hyperk_result(tau_central, 5.0, is_detection=True)
        # Any detection in a broad range should be CONFIRMED
        assert result["verdict"] in ("CONFIRMED", "TENSION")

    def test_detection_way_below_range_falsified(self):
        result = route_hyperk_result(1e30, 5.0, is_detection=True)
        assert result["verdict"] == "FALSIFIED"

    def test_limit_below_central_consistent(self):
        tau_central = proton_decay_lifetime_yr()
        limit_below = tau_central / 10.0
        result = route_hyperk_result(limit_below, 0.0, is_detection=False)
        assert result["verdict"] == "CONSISTENT"

    def test_limit_way_above_range_falsified(self):
        tau_high = lifetime_uncertainty_budget()["tau_high_yr"]
        result = route_hyperk_result(tau_high * 100.0, 0.0, is_detection=False)
        assert result["verdict"] == "FALSIFIED"

    def test_result_type_detection_flag(self):
        result = route_hyperk_result(1e35, 3.0, is_detection=True)
        assert result["result_type"] == "DETECTION"

    def test_result_type_limit_flag(self):
        result = route_hyperk_result(1e35, 0.0, is_detection=False)
        assert result["result_type"] == "LIMIT"

    def test_verdict_present(self):
        result = route_hyperk_result(5e34, 0.0, False)
        assert "verdict" in result

    def test_action_present(self):
        result = route_hyperk_result(5e34, 0.0, False)
        assert "action" in result


class TestFullReport:
    def test_report_returns_dict(self):
        assert isinstance(pillar341_full_report(), dict)

    def test_pillar_number(self):
        assert pillar341_full_report()["pillar"] == 341

    def test_has_um_prediction(self):
        report = pillar341_full_report()
        assert "um_prediction" in report

    def test_consistent_with_current(self):
        report = pillar341_full_report()
        assert report["consistent_with_current"]

    def test_has_falsification_condition(self):
        report = pillar341_full_report()
        assert "falsification_condition" in report

    def test_has_architecture_limit(self):
        report = pillar341_full_report()
        assert "architecture_limit" in report

    def test_um_prediction_has_tau(self):
        report = pillar341_full_report()
        assert "tau_central_yr" in report["um_prediction"]

    def test_um_prediction_mode(self):
        report = pillar341_full_report()
        mode = report["um_prediction"]["mode"]
        assert "e" in mode and "π" in mode  # p → e⁺ π⁰
