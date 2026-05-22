# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 335 — Simons Observatory r=0.0315 Verification Protocol."""
import math
import pytest

from src.core.pillar335_simons_observatory_protocol import (
    N_W, K_CS, PI_KR,
    R_UM_CENTRAL, R_UM_THEORY_UNCERTAINTY, NS_UM,
    R_ACT_DR6_UPPER_95CL, R_BICEP_KECK_UPPER_95CL,
    SO_SIGMA_R_5YR, SO_SIGMA_R_2YR,
    R_FALSIFIED_UPPER, R_TENSION_UPPER, R_CONFIRMED_LOW,
    R_CONFIRMED_HIGH, R_ABOVE_UPPER,
    separation_guard,
    braided_sound_speed,
    sound_speed_correction_factor,
    wzw_nlo_loop_correction,
    r_bare_from_phi0,
    r_um_prediction,
    act_dr6_tension_analysis,
    so_detection_significance_if_correct,
    route_so_dr1,
    preregistration_manifest,
    so_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_r_um_physical(self):
        assert 0.01 < R_UM_CENTRAL < 0.10

    def test_r_um_matches_p3(self):
        assert abs(R_UM_CENTRAL - 0.0315) < 1e-4

    def test_ns_um(self):
        assert abs(NS_UM - 0.9635) < 1e-4

    def test_act_dr6_bound(self):
        assert abs(R_ACT_DR6_UPPER_95CL - 0.016) < 1e-4

    def test_bicep_bound(self):
        assert abs(R_BICEP_KECK_UPPER_95CL - 0.036) < 1e-4

    def test_so_sigma_physical(self):
        assert 0 < SO_SIGMA_R_5YR < SO_SIGMA_R_2YR

    def test_routing_thresholds_ordered(self):
        assert R_FALSIFIED_UPPER < R_TENSION_UPPER < R_CONFIRMED_LOW < R_CONFIRMED_HIGH < R_ABOVE_UPPER

    def test_r_um_above_falsified_threshold(self):
        # r_UM should be above the falsification threshold
        assert R_UM_CENTRAL > R_FALSIFIED_UPPER

    def test_r_um_in_consistent_range(self):
        # r_UM = 0.0315 is in the confirmed range [0.025, 0.040]
        assert R_CONFIRMED_LOW <= R_UM_CENTRAL <= R_CONFIRMED_HIGH


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()

    def test_mentions_so(self):
        assert "SO" in separation_guard() or "Observatory" in separation_guard()


class TestBraidedWindingChain:
    def test_braided_sound_speed(self):
        cs = braided_sound_speed()
        assert abs(cs - 12/37) < 1e-9

    def test_cs_range(self):
        cs = braided_sound_speed()
        assert 0 < cs < 1

    def test_sound_speed_correction(self):
        cs = braided_sound_speed()
        expected = 1 - cs**2 / 3
        assert abs(sound_speed_correction_factor() - expected) < 1e-10

    def test_correction_less_than_one(self):
        assert sound_speed_correction_factor() < 1.0
        assert sound_speed_correction_factor() > 0.9

    def test_wzw_nlo_small(self):
        nlo = wzw_nlo_loop_correction()
        assert 0 < nlo < 0.1  # sub-percent NLO correction

    def test_r_bare_physical(self):
        r_bare = r_bare_from_phi0()
        assert 0.01 < r_bare < 0.10

    def test_r_prediction_dict(self):
        r_pred = r_um_prediction()
        assert "r_central" in r_pred
        assert "c_s" in r_pred
        assert "r_braided" in r_pred
        assert "r_nlo" in r_pred
        assert r_pred["free_parameters"] == 0

    def test_r_prediction_matches_central(self):
        r_pred = r_um_prediction()
        assert abs(r_pred["r_central"] - R_UM_CENTRAL) < 1e-4


class TestTensionAnalysis:
    def test_returns_dict(self):
        tension = act_dr6_tension_analysis()
        assert isinstance(tension, dict)

    def test_tension_level(self):
        tension = act_dr6_tension_analysis()
        assert tension["tension_level"] == "HIGH_TENSION"

    def test_r_um_exceeds_bound(self):
        tension = act_dr6_tension_analysis()
        assert tension["r_um"] > tension["r_act_dr6_upper_95cl"]

    def test_excess_factor_approx_two(self):
        tension = act_dr6_tension_analysis()
        # r_UM/r_ACT = 0.0315/0.016 ≈ 2
        assert 1.5 < tension["excess_factor"] < 3.0

    def test_tension_estimate_sigma(self):
        tension = act_dr6_tension_analysis()
        # Tension should be ~2–4σ estimate
        assert 1.0 < tension["approximate_tension_sigma"] < 6.0

    def test_falsification_condition_present(self):
        tension = act_dr6_tension_analysis()
        assert "MEASURED" in tension["falsification_condition"]


class TestSODetection:
    def test_returns_dict(self):
        detect = so_detection_significance_if_correct()
        assert isinstance(detect, dict)

    def test_snr_5yr_high(self):
        detect = so_detection_significance_if_correct()
        # r_UM / sigma_SO_5yr = 0.0315 / 0.003 = 10.5 σ
        assert detect["detection_snr_5yr"] > 5.0

    def test_snr_2yr_less_than_5yr(self):
        detect = so_detection_significance_if_correct()
        assert detect["detection_snr_2yr"] < detect["detection_snr_5yr"]

    def test_detection_statement_present(self):
        detect = so_detection_significance_if_correct()
        assert isinstance(detect["detection_statement"], str)
        assert len(detect["detection_statement"]) > 10


class TestRoutingProtocol:
    def test_r_below_010_falsified(self):
        result = route_so_dr1(r_measured=0.005, r_sigma=0.003, is_measurement=True)
        assert result["verdict"] == "FALSIFIED"

    def test_r_at_um_prediction_confirmed(self):
        result = route_so_dr1(r_measured=0.0315, r_sigma=0.003, is_measurement=True)
        assert result["verdict"] == "CONFIRMED"

    def test_r_slightly_below_confirmed(self):
        result = route_so_dr1(r_measured=0.023, r_sigma=0.003, is_measurement=True)
        assert result["verdict"] in ("CONSISTENT", "HIGH_TENSION")

    def test_r_above_upper_high_tension(self):
        result = route_so_dr1(r_measured=0.060, r_sigma=0.003, is_measurement=True)
        assert result["verdict"] == "HIGH_TENSION_ABOVE"

    def test_result_has_pillar(self):
        result = route_so_dr1(r_measured=0.030, r_sigma=0.003)
        assert result["pillar"] == 335

    def test_result_has_actions(self):
        result = route_so_dr1(r_measured=0.030, r_sigma=0.003)
        assert isinstance(result["required_actions"], list)
        assert len(result["required_actions"]) > 0

    def test_result_has_n_sigma(self):
        result = route_so_dr1(r_measured=0.030, r_sigma=0.003)
        assert "n_sigma_from_um" in result
        assert result["n_sigma_from_um"] >= 0

    def test_r_um_confirmed_at_known_value(self):
        # At r=0.035, sigma=0.003: 0.5σ from r_UM → CONFIRMED
        result = route_so_dr1(r_measured=0.035, r_sigma=0.003, is_measurement=True)
        assert result["verdict"] in ("CONFIRMED", "CONSISTENT")


class TestPreregistration:
    def test_returns_dict(self):
        manifest = preregistration_manifest()
        assert isinstance(manifest, dict)

    def test_version(self):
        manifest = preregistration_manifest()
        assert "v11.18" in manifest["manifest_version"]

    def test_prediction_present(self):
        manifest = preregistration_manifest()
        assert manifest["prediction"]["r"] == R_UM_CENTRAL

    def test_routing_branches_present(self):
        manifest = preregistration_manifest()
        branches = manifest["routing_branches"]
        assert "FALSIFIED" in branches
        assert "CONFIRMED" in branches

    def test_free_parameters_zero(self):
        manifest = preregistration_manifest()
        assert manifest["prediction"]["free_parameters"] == 0


class TestFullReport:
    def test_returns_dict(self):
        report = so_full_report()
        assert isinstance(report, dict)

    def test_pillar_number(self):
        assert so_full_report()["pillar"] == 335

    def test_r_um_present(self):
        report = so_full_report()
        assert abs(report["r_um"] - R_UM_CENTRAL) < 1e-4

    def test_so_detection_snr(self):
        report = so_full_report()
        assert report["so_detection_snr"] > 5.0

    def test_falsification_condition(self):
        report = so_full_report()
        assert "MEASURED" in report["falsification_condition"]

    def test_separation_guard(self):
        report = so_full_report()
        assert "ADJACENT" in report["separation_guard"]
