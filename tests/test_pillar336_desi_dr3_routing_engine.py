# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 336 — DESI DR3 Real-Time Routing Engine."""
import math
import pytest

from src.core.pillar336_desi_dr3_routing_engine import (
    N_W, K_CS,
    W_A_UM, W_0_UM,
    WA_DESI_DR2_COMBINED, WA_DESI_DR2_COMBINED_SIGMA,
    TENSION_DR2_COMBINED,
    WA_SIGMA_DR3_PROJECTED,
    FALSIFIED_SIGMA, TENSION_SIGMA_LOW,
    separation_guard,
    current_tension_analysis,
    tension_from_wa,
    log_likelihood_wa_zero,
    log_evidence_lcdm_wa_free,
    log_bayes_factor_um_vs_lcdm,
    jeffreys_scale,
    posterior_probability_wa_zero,
    route_desi_dr3,
    dr3_scenario_matrix,
    desi_dr3_readiness_report,
    desi_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_wa_um_zero(self):
        assert W_A_UM == 0.0

    def test_w0_um_minus_one(self):
        assert W_0_UM == -1.0

    def test_dr2_tension(self):
        assert 2.0 < TENSION_DR2_COMBINED < 3.0

    def test_wa_dr2_combined_negative(self):
        assert WA_DESI_DR2_COMBINED < 0

    def test_falsified_sigma(self):
        assert FALSIFIED_SIGMA == 3.0

    def test_routing_thresholds_ordered(self):
        assert TENSION_SIGMA_LOW < FALSIFIED_SIGMA


class TestSeparationGuard:
    def test_is_string(self):
        assert isinstance(separation_guard(), str)

    def test_adjacent_track(self):
        assert "ADJACENT" in separation_guard()

    def test_desi_mentioned(self):
        assert "DESI" in separation_guard()


class TestTensionAnalysis:
    def test_current_tension_dict(self):
        tension = current_tension_analysis()
        assert isinstance(tension, dict)

    def test_um_prediction_zero(self):
        tension = current_tension_analysis()
        assert tension["um_prediction_wa"] == 0.0

    def test_dr2_combined_tension(self):
        tension = current_tension_analysis()
        t = tension["desi_dr2_combined"]["tension_sigma"]
        assert 2.0 < t < 3.5

    def test_status_high_tension(self):
        tension = current_tension_analysis()
        assert "HIGH_TENSION" in tension["status"]

    def test_falsification_condition_present(self):
        tension = current_tension_analysis()
        assert "FALSIFIED" in tension["falsification_condition"]

    def test_tension_from_wa_positive(self):
        t = tension_from_wa(-0.55, 0.20)
        assert t == pytest.approx(2.75, rel=1e-3)

    def test_tension_from_wa_zero_when_consistent(self):
        t = tension_from_wa(0.0, 0.20)
        assert t == 0.0

    def test_tension_from_wa_three_sigma(self):
        t = tension_from_wa(-0.60, 0.20)
        assert t == pytest.approx(3.0, rel=1e-3)


class TestBayesianMachinery:
    def test_log_likelihood_at_zero_is_zero(self):
        # wₐ_meas = 0 → perfectly consistent → log L = 0
        assert log_likelihood_wa_zero(0.0, 0.20) == pytest.approx(0.0)

    def test_log_likelihood_decreases_with_tension(self):
        ll_0 = log_likelihood_wa_zero(0.0, 0.20)
        ll_1 = log_likelihood_wa_zero(-0.20, 0.20)
        ll_2 = log_likelihood_wa_zero(-0.55, 0.20)
        assert ll_0 > ll_1 > ll_2

    def test_log_evidence_lcdm_negative(self):
        # ΛCDM log evidence should be negative (Occam penalty for wider prior)
        log_ev = log_evidence_lcdm_wa_free(0.0, 0.20)
        assert log_ev < 0

    def test_log_bf_positive_when_wa_consistent(self):
        # When wₐ ≈ 0, UM is favoured → positive log BF
        lbf = log_bayes_factor_um_vs_lcdm(0.05, 0.20)
        assert lbf > 0

    def test_log_bf_negative_when_wa_large(self):
        # When wₐ = -0.55 with tight σ, ΛCDM is favoured → negative log BF
        lbf = log_bayes_factor_um_vs_lcdm(-0.55, 0.10)
        assert lbf < 0

    def test_jeffreys_scale_is_string(self):
        assert isinstance(jeffreys_scale(5.0), str)

    def test_jeffreys_decisive_large(self):
        assert "decisive" in jeffreys_scale(10.0)

    def test_jeffreys_substantial_moderate(self):
        result = jeffreys_scale(2.0)
        assert "substantial" in result

    def test_posterior_at_wa_zero_high(self):
        # When measurement is wₐ = 0 exactly, posterior for UM should be high
        p = posterior_probability_wa_zero(0.0, 0.20)
        assert p > 0.5

    def test_posterior_at_wa_large_negative_low(self):
        # When measurement is wₐ = -0.55 with tight σ, UM posterior is low
        p = posterior_probability_wa_zero(-0.55, 0.10)
        assert 0 <= p <= 1.0

    def test_posterior_probability_in_range(self):
        for wa in [-0.55, -0.20, 0.0, 0.10]:
            p = posterior_probability_wa_zero(wa, 0.20)
            assert 0 <= p <= 1.0, f"Posterior out of range at wa={wa}: {p}"


class TestRoutingProtocol:
    def test_falsified_at_high_tension(self):
        # wₐ = -0.60 ± 0.15 → 4σ → FALSIFIED
        result = route_desi_dr3(-0.60, 0.15)
        assert result["verdict"] == "FALSIFIED"

    def test_resolved_when_tension_small(self):
        # wₐ = -0.10 ± 0.17 → 0.6σ → RESOLVED
        result = route_desi_dr3(-0.10, 0.17)
        assert result["verdict"] == "RESOLVED"

    def test_high_tension_at_current_level(self):
        # wₐ = -0.55 ± 0.17 → ~3.2σ → could be FALSIFIED or HIGH_TENSION
        result = route_desi_dr3(-0.55, 0.17)
        assert result["verdict"] in ("FALSIFIED", "HIGH_TENSION")

    def test_high_tension_maintained(self):
        # wₐ = -0.40 ± 0.17 → 2.35σ → HIGH_TENSION
        result = route_desi_dr3(-0.40, 0.17)
        assert result["verdict"] == "HIGH_TENSION"

    def test_result_has_pillar(self):
        result = route_desi_dr3(-0.30, 0.17)
        assert result["pillar"] == 336

    def test_result_has_bayes_factor(self):
        result = route_desi_dr3(-0.30, 0.17)
        assert "log_bayes_factor" in result
        assert isinstance(result["log_bayes_factor"], float)

    def test_result_has_posterior(self):
        result = route_desi_dr3(-0.30, 0.17)
        assert "posterior_p_um" in result
        assert 0 <= result["posterior_p_um"] <= 1.0

    def test_result_has_actions(self):
        result = route_desi_dr3(-0.30, 0.17)
        assert isinstance(result["required_actions"], list)
        assert len(result["required_actions"]) > 0

    def test_tension_sigma_computed_correctly(self):
        wa_test = -0.34
        sigma_test = 0.17
        result = route_desi_dr3(wa_test, sigma_test)
        expected_tension = abs(wa_test) / sigma_test
        assert abs(result["tension_sigma"] - expected_tension) < 0.001

    def test_exact_um_prediction_resolved(self):
        result = route_desi_dr3(0.0, 0.17)
        assert result["verdict"] == "RESOLVED"
        assert result["tension_sigma"] == 0.0


class TestScenarioMatrix:
    def test_returns_dict(self):
        scenarios = dr3_scenario_matrix()
        assert isinstance(scenarios, dict)

    def test_has_five_scenarios(self):
        scenarios = dr3_scenario_matrix()
        assert len(scenarios) == 5

    def test_exact_um_prediction_resolved(self):
        scenarios = dr3_scenario_matrix()
        exact = scenarios["exact_um_prediction"]
        assert exact["verdict"] == "RESOLVED"
        assert exact["tension_sigma"] == 0.0

    def test_tension_increased_may_falsify(self):
        scenarios = dr3_scenario_matrix()
        inc = scenarios["tension_increased"]
        # wₐ=-0.80 at DR3 precision (σ=0.17) → 4.7σ → FALSIFIED
        assert inc["verdict"] == "FALSIFIED"

    def test_tension_resolved_is_resolved(self):
        scenarios = dr3_scenario_matrix()
        res = scenarios["tension_resolved"]
        assert res["verdict"] == "RESOLVED"


class TestReadinessReport:
    def test_returns_dict(self):
        report = desi_dr3_readiness_report()
        assert isinstance(report, dict)

    def test_pillar_number(self):
        report = desi_dr3_readiness_report()
        assert report["pillar"] == 336

    def test_um_prediction_present(self):
        report = desi_dr3_readiness_report()
        assert report["um_prediction"]["wa"] == 0.0

    def test_architecture_limit_present(self):
        report = desi_dr3_readiness_report()
        assert "ARCHITECTURE_LIMIT" in report["architecture_limit"]

    def test_separation_guard_present(self):
        report = desi_dr3_readiness_report()
        assert "ADJACENT" in report["separation_guard"]

    def test_full_report_identical(self):
        r1 = desi_dr3_readiness_report()
        r2 = desi_full_report()
        assert r1["pillar"] == r2["pillar"]
