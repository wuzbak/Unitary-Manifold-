# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 412 — Non-Perturbative Braid Condensate γ Contribution."""
import math
import pytest

from src.core.pillar412_braid_condensate_gamma import (
    PILLAR_STATUS,
    L2_STATUS,
    K_CS,
    PHI0,
    PHI0_FULL,
    GAMMA_THEORY,
    GAMMA_FIT,
    GAMMA_GAP,
    condensate_fluctuation,
    zero_mode_gamma_contribution,
    kk_mode_suppression,
    inflation_scenario_contribution,
    c1_budget,
    l2_condensate_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == "L2_CONDENSATE_ZERO_MODE_VIABLE"

    def test_l2_status(self):
        assert L2_STATUS == "L2_CONDENSATE_ZERO_MODE_VIABLE"

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0_approx_pi(self):
        assert abs(PHI0 - math.pi) < 1e-10

    def test_phi0_full(self):
        assert abs(PHI0_FULL - 31.416) < 0.001

    def test_gamma_gap(self):
        assert abs(GAMMA_GAP - (GAMMA_FIT - GAMMA_THEORY)) < 1e-10

    def test_gamma_gap_positive(self):
        assert GAMMA_GAP > 0

    def test_gamma_gap_value(self):
        assert abs(GAMMA_GAP - 0.031) < 0.001


class TestCondensateFluctuation:
    def test_returns_dict(self):
        data = condensate_fluctuation()
        assert isinstance(data, dict)

    def test_fluctuation_positive(self):
        data = condensate_fluctuation()
        assert data["fluctuation_abs"] > 0

    def test_relative_fluctuation_positive(self):
        data = condensate_fluctuation()
        assert data["fluctuation_relative"] > 0

    def test_formula(self):
        phi0 = PHI0_FULL
        K_cs = K_CS
        expected = phi0 ** 2 / (2.0 * K_cs) * math.pi
        data = condensate_fluctuation(K_cs, phi0)
        assert abs(data["fluctuation_abs"] - expected) < 1e-10

    def test_smaller_for_larger_K_cs(self):
        d1 = condensate_fluctuation(K_cs=74)
        d2 = condensate_fluctuation(K_cs=148)
        assert d2["fluctuation_abs"] < d1["fluctuation_abs"]


class TestZeroModeGammaContribution:
    def test_returns_dict(self):
        data = zero_mode_gamma_contribution()
        assert isinstance(data, dict)

    def test_delta_gamma_positive(self):
        data = zero_mode_gamma_contribution()
        assert data["delta_gamma_zero_mode"] > 0

    def test_g_braid_scaling(self):
        d1 = zero_mode_gamma_contribution(g_braid=1.0)
        d2 = zero_mode_gamma_contribution(g_braid=2.0)
        assert abs(d2["delta_gamma_zero_mode"] - 2 * d1["delta_gamma_zero_mode"]) < 1e-4

    def test_gamma_gap_fraction_positive(self):
        data = zero_mode_gamma_contribution()
        assert data["gamma_gap_fraction"] > 0

    def test_gamma_gap_fraction_less_than_2(self):
        # Even g_braid = 1 should not overshoot the gap by a large factor
        data = zero_mode_gamma_contribution(g_braid=1.0)
        assert data["gamma_gap_fraction"] < 2.0

    def test_c1_positive(self):
        data = zero_mode_gamma_contribution()
        assert data["c1_zm_estimate"] > 0

    def test_scenario_label(self):
        data = zero_mode_gamma_contribution()
        assert "B" in data["scenario"]


class TestKKModeSuppression:
    def test_returns_dict(self):
        data = kk_mode_suppression()
        assert isinstance(data, dict)

    def test_ratio_very_small(self):
        # k_CMB / M_KK should be tiny (CMB scale << KK scale)
        data = kk_mode_suppression()
        assert data["k_ratio"] < 1e-40

    def test_verdict_suppressed(self):
        data = kk_mode_suppression()
        assert "SUPPRESSED" in data["verdict"]

    def test_log10_suppression_negative(self):
        data = kk_mode_suppression()
        assert data["log10_suppression_n1"] < -40


class TestInflationScenario:
    def test_returns_dict(self):
        data = inflation_scenario_contribution()
        assert isinstance(data, dict)

    def test_delta_gamma_negligible(self):
        data = inflation_scenario_contribution()
        # Should be tiny
        assert data["delta_gamma_inf"] < 1e-4

    def test_verdict_negligible(self):
        data = inflation_scenario_contribution()
        assert "NEGLIGIBLE" in data["verdict"]

    def test_h_inf_positive(self):
        data = inflation_scenario_contribution()
        assert data["H_inf_GeV"] > 0

    def test_scenario_label(self):
        data = inflation_scenario_contribution()
        assert "C" in data["scenario"]


class TestC1Budget:
    def test_returns_dict(self):
        data = c1_budget()
        assert isinstance(data, dict)

    def test_c1_km_stored(self):
        data = c1_budget()
        assert abs(data["c1_km"] - 3.02) < 0.01

    def test_c1_zm_range_positive(self):
        data = c1_budget()
        lo, hi = data["c1_zm_estimate_range"]
        assert lo > 0
        assert hi > lo

    def test_fractions_between_0_and_1(self):
        data = c1_budget()
        assert 0 < data["fraction_km"] < 1
        assert 0 < data["fraction_zm_lo"] < 1

    def test_budget_summary_present(self):
        data = c1_budget()
        assert "budget_summary" in data
        assert len(data["budget_summary"]) > 20


class TestL2CondensateVerdict:
    def test_status(self):
        verdict = l2_condensate_verdict()
        assert verdict["status"] == "L2_CONDENSATE_ZERO_MODE_VIABLE"

    def test_status_upgrade(self):
        verdict = l2_condensate_verdict()
        assert verdict["previous_status"] == "L2_KACMOODY_CONSTRAINED"
        assert verdict["new_status"] == "L2_CONDENSATE_ZERO_MODE_VIABLE"

    def test_gamma_values(self):
        verdict = l2_condensate_verdict()
        assert abs(verdict["gamma_theory"] - GAMMA_THEORY) < 1e-10
        assert abs(verdict["gamma_fit"] - GAMMA_FIT) < 1e-10
        assert abs(verdict["gamma_gap"] - GAMMA_GAP) < 1e-10

    def test_viable_mechanism(self):
        verdict = l2_condensate_verdict()
        assert "Scenario B" in verdict["viable_mechanism"]

    def test_all_scenarios_present(self):
        verdict = l2_condensate_verdict()
        assert "scenario_A_kk" in verdict
        assert "scenario_B_zero_mode" in verdict
        assert "scenario_C_inflation" in verdict

    def test_verdict_contains_upgraded(self):
        verdict = l2_condensate_verdict()
        assert "L2_CONDENSATE_ZERO_MODE_VIABLE" in verdict["verdict"]
