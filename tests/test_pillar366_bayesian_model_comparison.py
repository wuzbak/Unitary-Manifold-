# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar366_bayesian_model_comparison.py"""
from __future__ import annotations
import math
import pytest
from src.core.pillar366_bayesian_model_comparison import (
    PILLAR_NUMBER, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    OCCAM_FACTOR_NATS, PARAMETER_TABLE,
    separation_guard, gaussian_log_likelihood_ratio,
    compute_all_tensions, total_likelihood_penalty, net_bayesian_advantage,
    bayesian_model_comparison, pillar366_summary,
)


class TestConstants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 366
    def test_status(self): assert PILLAR_STATUS == "BAYESIAN_ANALYSIS_COMPLETE"
    def test_adjacency(self): assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"
    def test_occam_factor(self): assert abs(OCCAM_FACTOR_NATS - 136.0) < 1.0
    def test_parameter_table_nonempty(self): assert len(PARAMETER_TABLE) >= 5


class TestGaussianLogLikelihood:
    def test_perfect_fit(self):
        delta_ll = gaussian_log_likelihood_ratio(1.0, 1.0, 0.1)
        assert delta_ll == 0.0

    def test_one_sigma_tension(self):
        delta_ll = gaussian_log_likelihood_ratio(1.1, 1.0, 0.1)
        assert abs(delta_ll - (-0.5)) < 1e-10

    def test_two_sigma_penalty(self):
        delta_ll = gaussian_log_likelihood_ratio(1.2, 1.0, 0.1)
        assert abs(delta_ll - (-2.0)) < 1e-10

    def test_negative_for_tension(self):
        delta_ll = gaussian_log_likelihood_ratio(2.0, 1.0, 0.1)
        assert delta_ll < 0

    def test_zero_sigma_returns_zero(self):
        assert gaussian_log_likelihood_ratio(1.0, 2.0, 0.0) == 0.0


class TestComputeAllTensions:
    def test_returns_list(self): assert isinstance(compute_all_tensions(), list)
    def test_same_length_as_table(self):
        assert len(compute_all_tensions()) == len(PARAMETER_TABLE)
    def test_each_has_tension(self):
        for t in compute_all_tensions():
            assert "tension_sigma" in t
    def test_each_has_delta_ll(self):
        for t in compute_all_tensions():
            assert "delta_ln_L" in t
    def test_tensions_non_negative(self):
        for t in compute_all_tensions():
            assert t["tension_sigma"] >= 0


class TestLikelihoodPenalty:
    def test_negative(self):
        # Tensions always give negative delta_ln_L
        assert total_likelihood_penalty() <= 0

    def test_finite(self):
        assert math.isfinite(total_likelihood_penalty())


class TestNetBayesianAdvantage:
    def test_positive(self):
        # UM should have positive net advantage
        assert net_bayesian_advantage() > 0

    def test_less_than_occam(self):
        # Net advantage reduced by penalty
        assert net_bayesian_advantage() < OCCAM_FACTOR_NATS

    def test_substantial(self):
        # Should be >> 10 nats
        assert net_bayesian_advantage() > 50


class TestBayesianModelComparison:
    def test_returns_dict(self): assert isinstance(bayesian_model_comparison(), dict)
    def test_pillar_366(self): assert bayesian_model_comparison()["pillar"] == 366
    def test_um_preferred(self): assert bayesian_model_comparison()["um_preferred"] is True
    def test_n_parameters(self):
        result = bayesian_model_comparison()
        assert result["n_parameters"] == len(PARAMETER_TABLE)
    def test_verdict_present(self): assert "verdict" in bayesian_model_comparison()
    def test_honest_caveat(self): assert "honest_caveat" in bayesian_model_comparison()
    def test_high_tension_flagged(self):
        result = bayesian_model_comparison()
        assert result["n_high_tension"] >= 1


class TestSummary:
    def test_pillar_366(self): assert pillar366_summary()["pillar"] == 366
    def test_um_preferred(self): assert pillar366_summary()["um_preferred"] is True


class TestSeparationGuard:
    def test_returns_string(self): assert isinstance(separation_guard(), str)
    def test_hardgate_adjacent(self): assert "HARDGATE_ADJACENT" in separation_guard()
