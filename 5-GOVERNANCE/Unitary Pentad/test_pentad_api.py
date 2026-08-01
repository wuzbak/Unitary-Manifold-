# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for the Pentad public API gateway."""

from __future__ import annotations

import os
import sys

import pytest

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from pentad_api import PentadAPI, generate_static_snapshot
from unitary_pentad import PENTAD_LABELS, PentadLabel


@pytest.fixture()
def api():
    return PentadAPI()


class TestRunScenario:
    @pytest.mark.parametrize("name", ["harmonic", "collapse", "wildcard"])
    def test_supported_scenarios(self, api, name):
        result = api.run_scenario(name)
        assert result["scenario"] == name

    def test_invalid_scenario_raises(self, api):
        with pytest.raises(ValueError):
            api.run_scenario("invalid")

    def test_harmonic_contains_metrics(self, api):
        assert "metrics" in api.run_scenario("harmonic")

    def test_collapse_contains_signature(self, api):
        assert "collapse" in api.run_scenario("collapse")

    def test_wildcard_contains_cost(self, api):
        assert "trust_maintenance_cost" in api.run_scenario("wildcard")


class TestStabilityScore:
    def test_rejects_wrong_length(self, api):
        with pytest.raises(ValueError):
            api.get_stability_score([1.0])

    @pytest.mark.parametrize(
        ("states", "lower_bound"),
        [
            ([1.0, 1.0, 1.0, 1.0, 1.0], 0.99),
            ([0.5, 0.5, 0.5, 0.5, 0.5], 0.99),
            ([0.0, 1.0, 0.0, 1.0, 0.5], 0.0),
            ([0.2, 0.3, 0.4, 0.5, 0.6], 0.0),
            ([0.1, 0.1, 0.9, 0.9, 0.9], 0.0),
        ],
    )
    def test_bounded_scores(self, api, states, lower_bound):
        score = api.get_stability_score(states)
        assert lower_bound <= score <= 1.0

    def test_uniform_states_outperform_spread_states(self, api):
        assert api.get_stability_score([0.8] * 5) > api.get_stability_score([0.0, 1.0, 0.0, 1.0, 0.5])


class TestTrustField:
    def test_labels_present(self, api):
        result = api.compute_trust_field({})
        assert result["labels"] == list(PENTAD_LABELS)

    def test_matrix_contains_all_bodies(self, api):
        matrix = api.compute_trust_field({})["matrix"]
        assert set(matrix.keys()) == set(PENTAD_LABELS)

    @pytest.mark.parametrize("label", list(PENTAD_LABELS))
    def test_diagonal_entries_exist(self, api, label):
        matrix = api.compute_trust_field({})["matrix"]
        assert label in matrix[label]

    @pytest.mark.parametrize(
        ("left", "right"),
        [
            (PentadLabel.UNIV, PentadLabel.BRAIN),
            (PentadLabel.UNIV, PentadLabel.HUMAN),
            (PentadLabel.UNIV, PentadLabel.AI),
            (PentadLabel.UNIV, PentadLabel.TRUST),
            (PentadLabel.BRAIN, PentadLabel.HUMAN),
            (PentadLabel.BRAIN, PentadLabel.AI),
            (PentadLabel.BRAIN, PentadLabel.TRUST),
            (PentadLabel.HUMAN, PentadLabel.AI),
            (PentadLabel.HUMAN, PentadLabel.TRUST),
            (PentadLabel.AI, PentadLabel.TRUST),
        ],
    )
    def test_matrix_is_symmetric(self, api, left, right):
        matrix = api.compute_trust_field({"trust": 0.8})["matrix"]
        assert matrix[left][right] == pytest.approx(matrix[right][left])

    def test_trust_scalar_is_bounded(self, api):
        result = api.compute_trust_field({"trust": 2.0})
        assert 0.0 <= result["trust_scalar"] <= 1.0


class TestSimulation:
    def test_negative_steps_rejected(self, api):
        with pytest.raises(ValueError):
            api.simulate_5body(-1, {})

    @pytest.mark.parametrize("steps", [0, 1, 2, 3, 4, 5])
    def test_trajectory_length(self, api, steps):
        trajectory = api.simulate_5body(steps, {})
        assert len(trajectory) == steps + 1

    @pytest.mark.parametrize("step_count", [1, 2, 3, 4, 5])
    def test_each_state_has_all_bodies(self, api, step_count):
        trajectory = api.simulate_5body(step_count, {})
        for state in trajectory:
            assert set(state.keys()) == set(PENTAD_LABELS)

    def test_state_values_are_clamped(self, api):
        trajectory = api.simulate_5body(2, {label: 2.0 for label in PENTAD_LABELS})
        for state in trajectory:
            assert all(0.0 <= value <= 1.0 for value in state.values())

    def test_relaxation_moves_toward_mean(self, api):
        trajectory = api.simulate_5body(1, {PentadLabel.UNIV: 1.0, PentadLabel.BRAIN: 0.0, PentadLabel.HUMAN: 0.0, PentadLabel.AI: 0.0, PentadLabel.TRUST: 0.0})
        assert trajectory[1][PentadLabel.UNIV] < trajectory[0][PentadLabel.UNIV]


class TestSummaryAndExport:
    def test_pillar_summary_contains_constants(self, api):
        summary = api.get_pillar_summary()
        assert summary["k_cs"] == 74

    @pytest.mark.parametrize(
        "key",
        [
            "winding_number",
            "braid_partner",
            "k_cs",
            "xi_c",
            "sentinel_capacity",
            "braided_sound_speed",
            "trust_floor",
            "pillars",
        ],
    )
    def test_summary_keys_present(self, api, key):
        assert key in api.get_pillar_summary()

    def test_export_static_json_contains_scenarios(self, api):
        export = api.export_static_json()
        assert set(export["scenarios"].keys()) == {"harmonic", "collapse", "wildcard"}

    def test_export_contains_trajectory(self, api):
        assert len(api.export_static_json()["sample_trajectory"]) == 4

    def test_snapshot_matches_export_shape(self):
        snapshot = generate_static_snapshot()
        assert "pillar_summary" in snapshot

    @pytest.mark.parametrize("key", ["api_version", "pillar_summary", "scenarios", "baseline_state", "baseline_trust", "baseline_defect", "sample_trajectory"])
    def test_export_keys_present(self, api, key):
        assert key in api.export_static_json()
