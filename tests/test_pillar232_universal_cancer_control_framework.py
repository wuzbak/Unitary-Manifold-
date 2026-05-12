# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar232_universal_cancer_control_framework.py
===========================================================
Tests for Pillar 232: Universal Cancer Control Framework.
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar232_universal_cancer_control_framework import (
    N_W,
    K_CS,
    C_S,
    PHI0,
    JAX_AVAILABLE,
    DEFAULT_AXIS_WEIGHTS,
    __provenance__,
    precision_digits_for_bits,
    precision_weighted_control_probability,
    universal_prediction_engine,
    missing_key_direction,
    cancer_type_solution_directions,
    multi_agent_cancer_workforce_plan,
    pillar232_universal_control_hypothesis,
)


def _demo_profiles():
    return {
        "lung": {
            "heterogeneity_gap": 0.70,
            "resistance_gap": 0.62,
            "immune_escape_gap": 0.58,
            "early_detection_gap": 0.52,
            "targetability_gap": 0.46,
            "access_gap": 0.40,
        },
        "breast": {
            "heterogeneity_gap": 0.48,
            "resistance_gap": 0.44,
            "immune_escape_gap": 0.35,
            "early_detection_gap": 0.25,
            "targetability_gap": 0.30,
            "access_gap": 0.28,
        },
        "pancreatic": {
            "heterogeneity_gap": 0.82,
            "resistance_gap": 0.79,
            "immune_escape_gap": 0.76,
            "early_detection_gap": 0.85,
            "targetability_gap": 0.71,
            "access_gap": 0.52,
        },
    }


class TestPublicMetadata:
    def test_provenance_pillar(self):
        assert __provenance__["pillar"] == 232

    def test_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert abs(C_S - 12.0 / 37.0) < 1e-15
        assert abs(math.cos(PHI0) - PHI0) < 1e-12

    def test_default_weights_sum_to_one(self):
        assert abs(sum(DEFAULT_AXIS_WEIGHTS.values()) - 1.0) < 1e-12


class TestPrecisionDigits:
    @pytest.mark.parametrize(
        "bits,minimum",
        [
            (64, 20),
            (128, 40),
            (256, 80),
            (512, 150),
        ],
    )
    def test_digits_reasonable(self, bits, minimum):
        assert precision_digits_for_bits(bits) >= minimum

    def test_invalid_bits_raises(self):
        with pytest.raises(ValueError):
            precision_digits_for_bits(80)


class TestPrecisionWeightedControlProbability:
    def test_returns_required_keys(self):
        profile = _demo_profiles()["breast"]
        r = precision_weighted_control_probability(profile, precision_bits=256, use_jax=False)
        for key in [
            "control_probability",
            "control_probability_jax",
            "precision_bits",
            "decimal_digits",
            "limiting_axis",
            "treatability_band",
            "status",
            "notes",
        ]:
            assert key in r

    def test_probability_in_unit_interval(self):
        profile = _demo_profiles()["breast"]
        r = precision_weighted_control_probability(profile, precision_bits=256, use_jax=False)
        assert 0.0 <= r["control_probability"] <= 1.0

    def test_limiting_axis_is_max_gap(self):
        profile = _demo_profiles()["pancreatic"]
        r = precision_weighted_control_probability(profile, precision_bits=256, use_jax=False)
        assert r["limiting_axis"] == "early_detection_gap"

    def test_worse_profile_reduces_control_probability(self):
        p_good = _demo_profiles()["breast"]
        p_bad = _demo_profiles()["pancreatic"]
        r_good = precision_weighted_control_probability(p_good, precision_bits=256, use_jax=False)
        r_bad = precision_weighted_control_probability(p_bad, precision_bits=256, use_jax=False)
        assert r_bad["control_probability"] < r_good["control_probability"]

    def test_512bit_and_256bit_close(self):
        profile = _demo_profiles()["lung"]
        r256 = precision_weighted_control_probability(profile, precision_bits=256, use_jax=False)
        r512 = precision_weighted_control_probability(profile, precision_bits=512, use_jax=False)
        assert abs(r256["control_probability"] - r512["control_probability"]) < 1e-10

    def test_invalid_profile_missing_axis_raises(self):
        with pytest.raises(ValueError):
            precision_weighted_control_probability({"heterogeneity_gap": 0.5}, use_jax=False)

    def test_invalid_profile_range_raises(self):
        bad = dict(_demo_profiles()["lung"])
        bad["access_gap"] = 1.2
        with pytest.raises(ValueError):
            precision_weighted_control_probability(bad, use_jax=False)

    def test_invalid_weight_sum_raises(self):
        with pytest.raises(ValueError):
            precision_weighted_control_probability(
                _demo_profiles()["lung"],
                axis_weights={k: 0.0 for k in DEFAULT_AXIS_WEIGHTS},
                use_jax=False,
            )

    def test_invalid_weight_negative_raises(self):
        bad_w = dict(DEFAULT_AXIS_WEIGHTS)
        bad_w["access_gap"] = -0.1
        with pytest.raises(ValueError):
            precision_weighted_control_probability(_demo_profiles()["lung"], axis_weights=bad_w)

    def test_jax_crosscheck_available_or_none(self):
        r = precision_weighted_control_probability(_demo_profiles()["lung"], precision_bits=256, use_jax=True)
        if JAX_AVAILABLE:
            assert r["control_probability_jax"] is not None
            assert abs(r["control_probability"] - r["control_probability_jax"]) < 1e-9
        else:
            assert r["control_probability_jax"] is None


class TestUniversalPredictionEngine:
    def test_non_empty_required(self):
        with pytest.raises(ValueError):
            universal_prediction_engine({})

    def test_returns_required_keys(self):
        r = universal_prediction_engine(_demo_profiles(), precision_bits=256, use_jax=False)
        for key in [
            "n_cancer_types",
            "per_type",
            "portfolio_mean_control_probability",
            "portfolio_median_control_probability",
            "status",
            "notes",
        ]:
            assert key in r

    def test_count_matches(self):
        profiles = _demo_profiles()
        r = universal_prediction_engine(profiles, precision_bits=256, use_jax=False)
        assert r["n_cancer_types"] == len(profiles)
        assert len(r["per_type"]) == len(profiles)

    def test_mean_in_unit_interval(self):
        r = universal_prediction_engine(_demo_profiles(), precision_bits=256, use_jax=False)
        assert 0.0 <= r["portfolio_mean_control_probability"] <= 1.0

    def test_median_in_unit_interval(self):
        r = universal_prediction_engine(_demo_profiles(), precision_bits=256, use_jax=False)
        assert 0.0 <= r["portfolio_median_control_probability"] <= 1.0


class TestMissingKeyDirection:
    def test_missing_key_axis(self):
        profile = _demo_profiles()["lung"]
        r = missing_key_direction("lung", profile)
        assert r["missing_key_axis"] == "heterogeneity_gap"
        assert r["gap_value"] == profile["heterogeneity_gap"]

    def test_direction_non_empty(self):
        r = missing_key_direction("breast", _demo_profiles()["breast"])
        assert isinstance(r["direction"], str)
        assert len(r["direction"]) > 10


class TestCancerTypeSolutionDirections:
    def test_count_matches_profiles(self):
        profiles = _demo_profiles()
        rows = cancer_type_solution_directions(profiles)
        assert len(rows) == len(profiles)

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            cancer_type_solution_directions({})


class TestMultiAgentWorkforcePlan:
    def test_empty_raises(self):
        with pytest.raises(ValueError):
            multi_agent_cancer_workforce_plan({})

    def test_returns_required_keys(self):
        r = multi_agent_cancer_workforce_plan(_demo_profiles())
        for key in [
            "lead_axis",
            "axis_distribution",
            "coherence_score",
            "agents",
            "status",
            "notes",
        ]:
            assert key in r

    def test_coherence_in_unit_interval(self):
        r = multi_agent_cancer_workforce_plan(_demo_profiles())
        assert 0.0 <= r["coherence_score"] <= 1.0

    def test_eight_agents_defined(self):
        r = multi_agent_cancer_workforce_plan(_demo_profiles())
        assert len(r["agents"]) == 8
        assert any(a["agent"] == "A8-synthesis-lead" for a in r["agents"])


class TestIntegratedHypothesisPipeline:
    def test_returns_required_keys(self):
        r = pillar232_universal_control_hypothesis(_demo_profiles(), precision_bits=512, use_jax=False)
        for key in [
            "prediction",
            "directions",
            "workforce",
            "universal_method_viability",
            "status",
            "falsification_condition",
        ]:
            assert key in r

    def test_prediction_direction_alignment(self):
        r = pillar232_universal_control_hypothesis(_demo_profiles(), precision_bits=256, use_jax=False)
        assert len(r["directions"]) == r["prediction"]["n_cancer_types"]

    def test_viability_value_set(self):
        r = pillar232_universal_control_hypothesis(_demo_profiles(), precision_bits=256, use_jax=False)
        assert r["universal_method_viability"] in {
            "plausible-universal-method",
            "insufficient-current-tractability",
        }
