# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 227 — AI & Robotics Bottleneck Engine."""
from __future__ import annotations

import pytest

from src.core.pillar227_ai_robotics_bottleneck_engine import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    STRATEGIC_HURDLES,
    BOTTLENECK_ORDER,
    DeploymentScenario,
    UniformRange,
    ratio_deficit,
    ratio_excess,
    safety_liability_framework_gap,
    infrastructure_grid_readiness_gap,
    human_trust_perception_erosion,
    bottleneck_scores,
    strategic_hurdle_scores,
    deployment_readiness_report,
    monte_carlo_readiness,
    baseline_2026_scenario,
)


class TestConstants:
    def test_framework_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert C_S == pytest.approx(12 / 37)
        assert PHI0 == pytest.approx(0.7390851332151607)

    def test_registry_sizes(self):
        assert len(STRATEGIC_HURDLES) == 3
        assert len(BOTTLENECK_ORDER) == 12


class TestRatioHelpers:
    def test_ratio_deficit_basic(self):
        assert ratio_deficit(1.75, 12.0) == pytest.approx(1.0 - 1.75 / 12.0)

    def test_ratio_deficit_clamped(self):
        assert ratio_deficit(12.0, 8.0) == 0.0

    def test_ratio_excess_basic(self):
        assert ratio_excess(4.0, 1.5) == 1.0  # clamps from >1

    def test_ratio_excess_zero_when_below_target(self):
        assert ratio_excess(1.0, 2.0) == 0.0

    def test_ratio_helpers_reject_bad_target(self):
        with pytest.raises(ValueError):
            ratio_deficit(1.0, 0.0)
        with pytest.raises(ValueError):
            ratio_excess(1.0, 0.0)


class TestStrategicHurdles:
    def test_safety_gap_in_range(self):
        gap = safety_liability_framework_gap(0.35, 0.25, 175.0)
        assert 0.0 <= gap <= 1.0

    def test_grid_gap_in_range(self):
        gap = infrastructure_grid_readiness_gap(1.2, 3.0, 5.0)
        assert 0.0 <= gap <= 1.0

    def test_trust_gap_in_range(self):
        gap = human_trust_perception_erosion(46.0, 12.0, 58.0)
        assert 0.0 <= gap <= 1.0

    def test_safety_gap_rejects_invalid_fraction(self):
        with pytest.raises(ValueError):
            safety_liability_framework_gap(1.5, 0.2, 170.0)

    def test_trust_gap_rejects_invalid_percent(self):
        with pytest.raises(ValueError):
            human_trust_perception_erosion(120.0, 1.0, 40.0)


class TestBottleneckScoring:
    def test_bottleneck_score_keys(self):
        s = baseline_2026_scenario()
        scores = bottleneck_scores(s)
        assert tuple(scores.keys()) == BOTTLENECK_ORDER

    def test_bottleneck_scores_all_in_range(self):
        s = baseline_2026_scenario()
        scores = bottleneck_scores(s)
        assert all(0.0 <= v <= 1.0 for v in scores.values())

    def test_cyber_and_cost_gaps_are_saturated_in_baseline(self):
        s = baseline_2026_scenario()
        scores = bottleneck_scores(s)
        assert scores["cybersecurity_exposure"] == 1.0
        assert scores["cost_of_prototyping"] == 1.0

    def test_compute_power_conflict_nonzero_baseline(self):
        s = baseline_2026_scenario()
        scores = bottleneck_scores(s)
        assert scores["compute_to_power_conflict"] > 0.0

    def test_invalid_power_budget_raises(self):
        s = baseline_2026_scenario()
        broken = DeploymentScenario(**{**s.__dict__, "compute_watts": 0.0, "motion_watts": 0.0})
        with pytest.raises(ValueError):
            bottleneck_scores(broken)


class TestReadinessReport:
    def test_report_shape(self):
        report = deployment_readiness_report(baseline_2026_scenario())
        assert "readiness_index" in report
        assert "hurdle_scores" in report
        assert "bottleneck_scores" in report
        assert len(report["top_bottlenecks"]) == 5

    def test_readiness_index_in_range(self):
        report = deployment_readiness_report(baseline_2026_scenario())
        assert 0.0 <= report["readiness_index"] <= 1.0

    def test_baseline_is_low_readiness(self):
        report = deployment_readiness_report(baseline_2026_scenario())
        assert report["readiness_index"] < 0.40

    def test_strategic_weight_validation(self):
        with pytest.raises(ValueError):
            deployment_readiness_report(baseline_2026_scenario(), strategic_weight=1.2)

    def test_hurdle_scores_match_registry(self):
        scores = strategic_hurdle_scores(baseline_2026_scenario())
        assert tuple(scores.keys()) == STRATEGIC_HURDLES


class TestMonteCarlo:
    def test_uniform_range_sampling(self):
        r = UniformRange(0.1, 0.2)
        value = r.sample(__import__("random").Random(1))
        assert 0.1 <= value <= 0.2

    def test_uniform_range_invalid(self):
        r = UniformRange(1.0, 0.0)
        with pytest.raises(ValueError):
            r.sample(__import__("random").Random(1))

    def test_monte_carlo_reproducible(self):
        base = baseline_2026_scenario()
        uncertainty = {
            "battery_runtime_hours": UniformRange(1.5, 2.0),
            "software_hardware_lag_years": UniformRange(3.0, 5.0),
            "public_trust_percent": UniformRange(40.0, 50.0),
        }
        a = monte_carlo_readiness(base, uncertainty, n_samples=500, seed=11)
        b = monte_carlo_readiness(base, uncertainty, n_samples=500, seed=11)
        assert a["mean_readiness"] == pytest.approx(b["mean_readiness"])
        assert a["p50"] == pytest.approx(b["p50"])

    def test_monte_carlo_percentile_ordering(self):
        base = baseline_2026_scenario()
        uncertainty = {
            "battery_runtime_hours": UniformRange(1.5, 2.0),
            "software_hardware_lag_years": UniformRange(3.0, 5.0),
            "public_trust_percent": UniformRange(40.0, 50.0),
        }
        summary = monte_carlo_readiness(base, uncertainty, n_samples=400, seed=227)
        assert summary["min"] <= summary["p10"] <= summary["p50"] <= summary["p90"] <= summary["max"]

    def test_monte_carlo_requires_positive_samples(self):
        with pytest.raises(ValueError):
            monte_carlo_readiness(baseline_2026_scenario(), {}, n_samples=0)
