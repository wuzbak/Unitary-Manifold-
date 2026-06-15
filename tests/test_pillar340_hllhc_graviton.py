# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 340 — HL-LHC KK Graviton Search Routing Protocol."""
import math
import pytest

from src.core.pillar340_hllhc_kk_graviton import (
    N_W, K_CS, PI_KR,
    M_PL_GEV, M_5_GEV, T_KK_GEV,
    M_KK_CENTRAL_GEV, M_KK_LOW_GEV, M_KK_HIGH_GEV,
    SQRT_S_TEV, LUMINOSITY_INVFB,
    K_TILDE_CENTRAL, CURRENT_EXCLUSION_GEV,
    FALSIFICATION_THRESHOLD_SIGMA,
    separation_guard,
    mkk_prediction,
    kk_graviton_production_xs,
    signal_events,
    hllhc_exclusion_reach,
    route_lhc_result,
    pillar340_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < 1e-9

    def test_mkk_central_above_low(self):
        assert M_KK_CENTRAL_GEV > M_KK_LOW_GEV

    def test_mkk_high_above_central(self):
        assert M_KK_HIGH_GEV > M_KK_CENTRAL_GEV

    def test_mkk_low_above_ew_scale(self):
        assert M_KK_LOW_GEV > 500.0  # above EW scale

    def test_luminosity_positive(self):
        assert LUMINOSITY_INVFB > 0

    def test_sqrt_s_14_tev(self):
        assert abs(SQRT_S_TEV - 14.0) < 1e-9

    def test_k_tilde_o1(self):
        assert 0.01 <= K_TILDE_CENTRAL <= 0.5

    def test_falsification_threshold_3sigma(self):
        assert abs(FALSIFICATION_THRESHOLD_SIGMA - 3.0) < 1e-9

    def test_t_kk_consistent_with_mkk_range(self):
        # M_KK_LOW should be ≥ T_KK
        assert M_KK_LOW_GEV >= T_KK_GEV


class TestSeparationGuard:
    def test_returns_dict(self):
        assert isinstance(separation_guard(), dict)

    def test_pillar_340(self):
        assert separation_guard()["pillar"] == 340

    def test_no_hardgate_promotion(self):
        assert separation_guard()["hardgate_promotion"] is False

    def test_no_toe_delta(self):
        assert separation_guard()["toe_score_delta"] == 0

    def test_has_description(self):
        assert "description" in separation_guard()


class TestMKKPrediction:
    def test_returns_dict(self):
        assert isinstance(mkk_prediction(), dict)

    def test_epistemic_parameterized(self):
        result = mkk_prediction()
        assert "PARAMETERIZED" in result["epistemic_label"]

    def test_central_in_range(self):
        result = mkk_prediction()
        assert result["m_kk_low_gev"] <= result["m_kk_central_gev"] <= result["m_kk_high_gev"]

    def test_pi_kr_correct(self):
        result = mkk_prediction()
        assert abs(result["pi_kr"] - PI_KR) < 1e-9

    def test_x11_bessel_approx(self):
        result = mkk_prediction()
        # First zero of J_1 ≈ 3.83
        assert 3.8 < result["x_11_bessel"] < 3.9

    def test_note_present(self):
        result = mkk_prediction()
        assert "note" in result


class TestProductionCrossSection:
    def test_xs_positive(self):
        assert kk_graviton_production_xs(M_KK_CENTRAL_GEV) > 0

    def test_xs_decreases_with_mass(self):
        xs_low = kk_graviton_production_xs(M_KK_LOW_GEV)
        xs_high = kk_graviton_production_xs(M_KK_HIGH_GEV)
        assert xs_low > xs_high

    def test_xs_increases_with_k_tilde(self):
        xs_small = kk_graviton_production_xs(M_KK_CENTRAL_GEV, k_tilde=0.01)
        xs_large = kk_graviton_production_xs(M_KK_CENTRAL_GEV, k_tilde=0.1)
        assert xs_large > xs_small

    def test_xs_scales_as_k_tilde_squared(self):
        xs1 = kk_graviton_production_xs(M_KK_CENTRAL_GEV, k_tilde=0.05)
        xs2 = kk_graviton_production_xs(M_KK_CENTRAL_GEV, k_tilde=0.10)
        ratio = xs2 / xs1
        # Should be ~4 (scales as k̃²)
        assert 3.5 < ratio < 4.5


class TestSignalEvents:
    def test_signal_events_positive(self):
        assert signal_events(M_KK_CENTRAL_GEV) > 0

    def test_signal_events_scale_with_lumi(self):
        n1 = signal_events(M_KK_CENTRAL_GEV, lumi_invfb=1000.0)
        n2 = signal_events(M_KK_CENTRAL_GEV, lumi_invfb=3000.0)
        assert abs(n2 / n1 - 3.0) < 0.01

    def test_signal_events_decrease_with_mass(self):
        n_low = signal_events(M_KK_LOW_GEV)
        n_high = signal_events(M_KK_HIGH_GEV)
        assert n_low > n_high


class TestHLLHCReach:
    def test_reach_returns_dict(self):
        assert isinstance(hllhc_exclusion_reach(), dict)

    def test_projected_limit_above_current(self):
        result = hllhc_exclusion_reach()
        assert result["projected_hllhc_limit_gev"] >= result["current_exclusion_gev"]

    def test_um_range_consistency(self):
        result = hllhc_exclusion_reach()
        assert result["um_mkk_low_gev"] < result["um_mkk_high_gev"]

    def test_note_present(self):
        result = hllhc_exclusion_reach()
        assert "note" in result

    def test_k_tilde_returned(self):
        result = hllhc_exclusion_reach()
        assert result["k_tilde"] == K_TILDE_CENTRAL


class TestRoutingProtocol:
    def test_detection_in_range_gives_confirmed(self):
        result = route_lhc_result(
            m_kk_measured_or_limit_gev=M_KK_CENTRAL_GEV,
            sigma_level=5.0,
            is_detection=True,
        )
        assert result["verdict"] == "CONFIRMED"

    def test_detection_outside_range_gives_tension(self):
        result = route_lhc_result(
            m_kk_measured_or_limit_gev=500.0,  # below UM range
            sigma_level=5.0,
            is_detection=True,
        )
        assert result["verdict"] == "TENSION"

    def test_exclusion_above_high_gives_falsified(self):
        result = route_lhc_result(
            m_kk_measured_or_limit_gev=M_KK_HIGH_GEV + 1000.0,
            sigma_level=0.0,
            is_detection=False,
        )
        assert result["verdict"] == "FALSIFIED"

    def test_exclusion_below_central_gives_consistent(self):
        result = route_lhc_result(
            m_kk_measured_or_limit_gev=M_KK_CENTRAL_GEV - 500.0,
            sigma_level=0.0,
            is_detection=False,
        )
        assert result["verdict"] == "CONSISTENT"

    def test_exclusion_above_central_gives_high_tension(self):
        result = route_lhc_result(
            m_kk_measured_or_limit_gev=M_KK_CENTRAL_GEV + 500.0,
            sigma_level=0.0,
            is_detection=False,
        )
        assert result["verdict"] in ("HIGH_TENSION", "FALSIFIED")

    def test_result_type_detection(self):
        result = route_lhc_result(
            m_kk_measured_or_limit_gev=M_KK_CENTRAL_GEV,
            sigma_level=5.0,
            is_detection=True,
        )
        assert result["result_type"] == "DETECTION"

    def test_result_type_exclusion(self):
        result = route_lhc_result(
            m_kk_measured_or_limit_gev=5000.0,
            sigma_level=0.0,
            is_detection=False,
        )
        assert result["result_type"] == "EXCLUSION"

    def test_verdict_field_present(self):
        result = route_lhc_result(4000.0, 0.0, False)
        assert "verdict" in result

    def test_action_field_present(self):
        result = route_lhc_result(4000.0, 0.0, False)
        assert "action" in result


class TestFullReport:
    def test_report_returns_dict(self):
        assert isinstance(pillar340_full_report(), dict)

    def test_pillar_number(self):
        assert pillar340_full_report()["pillar"] == 340

    def test_has_falsification_condition(self):
        result = pillar340_full_report()
        assert "falsification_condition" in result

    def test_current_status_present(self):
        result = pillar340_full_report()
        assert "current_status" in result

    def test_xs_at_central_positive(self):
        result = pillar340_full_report()
        assert result["xs_at_central"] > 0

    def test_xs_at_low_above_central(self):
        result = pillar340_full_report()
        assert result["xs_at_low"] > result["xs_at_central"]

    def test_signal_events_central_positive(self):
        result = pillar340_full_report()
        assert result["signal_events_central"] > 0
