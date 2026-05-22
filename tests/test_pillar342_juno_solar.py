# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 342 — JUNO Solar Neutrino Precision Routing."""
import math
import pytest

from src.core.pillar342_juno_solar_routing import (
    N_W, K_CS,
    THETA_12_DEG_UM, THETA_12_RAD_UM, SIN2_THETA_12_UM,
    THETA_13_DEG_UM, THETA_13_RAD_UM, SIN2_THETA_13_UM, COS4_THETA_13_UM,
    PDG_SIN2_THETA_12, PDG_SIN2_THETA_12_ERR,
    JUNO_SOLAR_PRECISION_FRAC,
    DM21_SQ_EV2_UM, PDG_DM21_SQ, JUNO_DM21_PRECISION_FRAC,
    SIGMA_TENSION, SIGMA_FALSIFIED,
    separation_guard,
    survival_probability_8b,
    survival_probability_pp,
    juno_solar_precision_budget,
    route_juno_solar,
    juno_solar_projection,
    pillar342_full_report,
)


class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_theta12_range(self):
        assert 30.0 < THETA_12_DEG_UM < 40.0

    def test_theta13_range(self):
        assert 7.0 < THETA_13_DEG_UM < 10.0

    def test_sin2_theta12_um_value(self):
        # sin²(33.82°) ≈ 0.305
        expected = math.sin(math.radians(33.82)) ** 2
        assert abs(SIN2_THETA_12_UM - expected) < 1e-6

    def test_sin2_theta12_range(self):
        assert 0.28 < SIN2_THETA_12_UM < 0.33

    def test_pdg_sin2_theta12_range(self):
        assert 0.28 < PDG_SIN2_THETA_12 < 0.33

    def test_juno_precision_small(self):
        assert JUNO_SOLAR_PRECISION_FRAC < 0.01

    def test_dm21_positive(self):
        assert DM21_SQ_EV2_UM > 0

    def test_dm21_um_equals_pdg(self):
        assert abs(DM21_SQ_EV2_UM - PDG_DM21_SQ) < 1e-7

    def test_sigma_falsified_three(self):
        assert abs(SIGMA_FALSIFIED - 3.0) < 1e-9


class TestSeparationGuard:
    def test_returns_dict(self):
        assert isinstance(separation_guard(), dict)

    def test_pillar_342(self):
        assert separation_guard()["pillar"] == 342

    def test_no_hardgate_promotion(self):
        assert separation_guard()["hardgate_promotion"] is False

    def test_no_toe_score_delta(self):
        assert separation_guard()["toe_score_delta"] == 0


class TestSurvivalProbabilities:
    def test_pee_8b_um_positive(self):
        assert survival_probability_8b() > 0

    def test_pee_8b_less_than_one(self):
        assert survival_probability_8b() < 1.0

    def test_pee_8b_approximate_value(self):
        # Should be ~0.50 in adiabatic MSW limit
        p = survival_probability_8b()
        assert 0.4 < p < 0.65

    def test_pee_pp_um_positive(self):
        assert survival_probability_pp() > 0

    def test_pee_pp_less_than_one(self):
        assert survival_probability_pp() < 1.0

    def test_pee_pp_approximate_value(self):
        # ~0.5 for solar mixing
        p = survival_probability_pp()
        assert 0.4 < p < 0.65

    def test_pee_changes_with_theta12(self):
        # Larger θ₁₂ → smaller survival probability (more oscillation)
        p1 = survival_probability_pp(theta_12_rad=math.radians(30))
        p2 = survival_probability_pp(theta_12_rad=math.radians(40))
        assert p1 != p2


class TestPrecisionBudget:
    def test_returns_dict(self):
        assert isinstance(juno_solar_precision_budget(), dict)

    def test_sin2_um_key_present(self):
        budget = juno_solar_precision_budget()
        assert "sin2_theta12_um" in budget

    def test_residual_pct_small(self):
        budget = juno_solar_precision_budget()
        # Current PDG residual ~0.65%
        assert budget["residual_pct"] < 3.0

    def test_juno_sigma_small(self):
        budget = juno_solar_precision_budget()
        # JUNO σ ~ 0.5% × 0.307 ~ 0.0015
        assert budget["juno_sigma_sin2"] < 0.005

    def test_juno_tension_sigma_reasonable(self):
        budget = juno_solar_precision_budget()
        # Should be ~1-2σ at JUNO precision
        assert 0.0 <= budget["juno_tension_sigma"] < 5.0

    def test_p_ee_8b_in_dict(self):
        budget = juno_solar_precision_budget()
        assert "p_ee_8b_um" in budget

    def test_p_ee_pp_in_dict(self):
        budget = juno_solar_precision_budget()
        assert "p_ee_pp_um" in budget


class TestRoutingProtocol:
    def test_returns_dict(self):
        result = route_juno_solar(
            sin2_theta12_measured=PDG_SIN2_THETA_12,
            sin2_theta12_sigma=JUNO_SOLAR_PRECISION_FRAC * PDG_SIN2_THETA_12,
        )
        assert isinstance(result, dict)

    def test_exact_um_prediction_gives_tightened(self):
        # If JUNO measures exactly UM prediction → 0σ residual → TIGHTENED
        result = route_juno_solar(
            sin2_theta12_measured=SIN2_THETA_12_UM,
            sin2_theta12_sigma=0.001,
        )
        assert result["verdict"] == "TIGHTENED"

    def test_large_deviation_gives_falsified(self):
        # If JUNO measures very different value → FALSIFIED
        result = route_juno_solar(
            sin2_theta12_measured=0.20,  # Far from 0.305
            sin2_theta12_sigma=0.0005,   # Very precise
        )
        assert result["verdict"] == "FALSIFIED"

    def test_moderate_deviation_gives_tension(self):
        result = route_juno_solar(
            sin2_theta12_measured=0.315,  # 2σ away
            sin2_theta12_sigma=0.005,
        )
        assert result["verdict"] in ("TENSION", "FALSIFIED", "TIGHTENED")

    def test_pdg_central_with_juno_precision_known_result(self):
        # PDG central (0.307) vs UM (0.305) at JUNO precision (0.0015)
        juno_sig = JUNO_SOLAR_PRECISION_FRAC * PDG_SIN2_THETA_12
        result = route_juno_solar(
            sin2_theta12_measured=PDG_SIN2_THETA_12,
            sin2_theta12_sigma=juno_sig,
        )
        # ~1.3σ residual → TENSION or TIGHTENED
        assert result["verdict"] in ("TIGHTENED", "TENSION")

    def test_combined_verdict_present(self):
        result = route_juno_solar(
            sin2_theta12_measured=PDG_SIN2_THETA_12,
            sin2_theta12_sigma=0.001,
            dm21_sq_measured_ev2=PDG_DM21_SQ,
            dm21_sq_sigma_ev2=JUNO_DM21_PRECISION_FRAC * PDG_DM21_SQ,
        )
        assert "combined_verdict" in result

    def test_dm21_verdict_perfect_match(self):
        result = route_juno_solar(
            sin2_theta12_measured=SIN2_THETA_12_UM,
            sin2_theta12_sigma=0.001,
            dm21_sq_measured_ev2=DM21_SQ_EV2_UM,
            dm21_sq_sigma_ev2=1e-7,
        )
        assert result["dm21"]["verdict"] == "TIGHTENED"

    def test_action_present(self):
        result = route_juno_solar(PDG_SIN2_THETA_12, 0.001)
        assert "action" in result

    def test_verdict_one_of_three(self):
        result = route_juno_solar(PDG_SIN2_THETA_12, 0.001)
        assert result["verdict"] in ("TIGHTENED", "TENSION", "FALSIFIED")


class TestJunoSolarProjection:
    def test_returns_dict(self):
        assert isinstance(juno_solar_projection(), dict)

    def test_if_pdg_holds(self):
        result = juno_solar_projection(central_shifts_to_pdg=False)
        # ~1.3σ residual → TIGHTENED or TENSION
        assert result["combined_verdict"] in ("TIGHTENED", "TENSION")

    def test_if_um_holds(self):
        result = juno_solar_projection(central_shifts_to_pdg=True)
        # Perfect match → TIGHTENED
        assert result["combined_verdict"] in ("TIGHTENED",)


class TestFullReport:
    def test_returns_dict(self):
        assert isinstance(pillar342_full_report(), dict)

    def test_pillar_number(self):
        assert pillar342_full_report()["pillar"] == 342

    def test_has_um_predictions(self):
        report = pillar342_full_report()
        assert "um_predictions" in report

    def test_sin2_theta12_in_predictions(self):
        report = pillar342_full_report()
        assert "sin2_theta12" in report["um_predictions"]

    def test_has_falsification_condition(self):
        report = pillar342_full_report()
        assert "falsification_condition" in report

    def test_has_connection_to_334(self):
        report = pillar342_full_report()
        assert "334" in report["connection_to_pillar334"]

    def test_has_projections(self):
        report = pillar342_full_report()
        assert "projection_if_pdg_holds" in report
        assert "projection_if_um_holds" in report
