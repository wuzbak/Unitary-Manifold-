# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 251 — Translational Oncology Adaptive Routing & Trial Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar251_translational_oncology_adaptive_routing_trial_engine import (
    ADJACENCY_TRACK_LABEL,
    C_S,
    K_CS,
    N_W,
    ONCOLOGY_ROUTING_TRACK_LABEL,
    PATHWAYS,
    PHI0,
    AdaptiveOncologyState,
    __provenance__,
    access_optimization,
    adaptive_trial_design_specification,
    baseline_adaptive_oncology_state,
    intervention_sequencing_plan,
    monte_carlo_operating_envelope,
    patient_state_routing_probabilities,
    pillar251_translational_oncology_operating_report,
    separation_guard,
    translational_operating_score,
    uncertainty_accounting,
)
from src.core.pillar248_translational_oncology_synthesis_command_layer import (
    baseline_translational_oncology_scenario,
)


def _state() -> AdaptiveOncologyState:
    return baseline_adaptive_oncology_state()


def test_provenance_contract():
    assert __provenance__["pillar"] == 251
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"


def test_framework_constants_contract():
    assert N_W == 5
    assert K_CS == 74
    assert K_CS == 5**2 + 7**2
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_separation_guard_contract():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["track"] == ONCOLOGY_ROUTING_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["clinical_claims_allowed"] is False


def test_state_schema_sanity():
    s = _state()
    assert isinstance(s, AdaptiveOncologyState)
    assert 0.0 <= s.stage_severity <= 1.0
    assert s.travel_distance_km >= 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("stage_severity", 1.1),
        ("biomarker_actionability", -0.1),
        ("travel_distance_km", -1.0),
    ],
)
def test_state_schema_validation_raises(field: str, value: float):
    s = _state()
    with pytest.raises(ValueError):
        AdaptiveOncologyState(**{**s.__dict__, field: value})


def test_routing_probability_shape_and_simplex():
    p = patient_state_routing_probabilities(_state())
    assert tuple(p.keys()) == PATHWAYS
    assert abs(sum(p.values()) - 1.0) < 1e-12
    for v in p.values():
        assert 0.0 <= v <= 1.0


def test_routing_prefers_biomarker_path_when_high_actionability():
    s = _state()
    high = AdaptiveOncologyState(
        **{
            **s.__dict__,
            "biomarker_actionability": 0.95,
            "ctdna_signal_strength": 0.20,
        }
    )
    p = patient_state_routing_probabilities(high)
    assert p["biomarker_adaptive"] > p["standard_of_care"]


def test_intervention_sequence_shape():
    seq = intervention_sequencing_plan(_state())
    assert len(seq) == 4
    assert [row["step"] for row in seq] == [1, 2, 3, 4]


def test_trial_design_specification_contract():
    d = adaptive_trial_design_specification(_state())
    assert d["design_type"] in {"platform_trial", "seamless_adaptive"}
    assert d["n_initial_arms"] >= 3
    assert d["max_arms"] > d["n_initial_arms"]
    assert d["allocation_strategy"] == "response_adaptive"


def test_access_optimization_ranges():
    a = access_optimization(_state())
    assert 0.0 <= a["distance_barrier"] <= 1.0
    assert 0.0 <= a["affordability_score"] <= 1.0
    assert 0.0 <= a["virtual_trial_eligibility"] <= 1.0
    assert 0.0 <= a["equity_access_score"] <= 1.0


def test_uncertainty_accounting_contract():
    u = uncertainty_accounting(_state())
    assert u["top_driver"] in u["elasticity_map"]
    assert u["recommendation"] in {"wait_for_more_signal", "commit_now"}


def test_translational_operating_score_range():
    score = translational_operating_score(_state(), baseline_translational_oncology_scenario())
    assert 0.0 <= score <= 1.0


def test_operating_score_changes_with_uncertainty_shift():
    s = _state()
    low = AdaptiveOncologyState(**{**s.__dict__, "response_uncertainty": 0.10})
    high = AdaptiveOncologyState(**{**s.__dict__, "response_uncertainty": 0.90})
    b = baseline_translational_oncology_scenario()
    assert translational_operating_score(low, b) > translational_operating_score(high, b)


def test_monte_carlo_contract_and_ordering():
    r = monte_carlo_operating_envelope(
        _state(), baseline_translational_oncology_scenario(), n_trials=40, seed=11
    )
    assert 0.0 <= float(r["p10"]) <= 1.0
    assert 0.0 <= float(r["p50"]) <= 1.0
    assert 0.0 <= float(r["p90"]) <= 1.0
    assert float(r["p10"]) <= float(r["p50"]) <= float(r["p90"])


def test_monte_carlo_seed_reproducible():
    a = monte_carlo_operating_envelope(
        _state(), baseline_translational_oncology_scenario(), n_trials=40, seed=5
    )
    b = monte_carlo_operating_envelope(
        _state(), baseline_translational_oncology_scenario(), n_trials=40, seed=5
    )
    assert a == b


def test_monte_carlo_invalid_inputs_raise():
    with pytest.raises(ValueError):
        monte_carlo_operating_envelope(
            _state(), baseline_translational_oncology_scenario(), n_trials=9
        )
    with pytest.raises(ValueError):
        monte_carlo_operating_envelope(
            _state(), baseline_translational_oncology_scenario(), sigma=-0.1
        )


def test_report_shape_and_falsification_clause():
    r = pillar251_translational_oncology_operating_report()
    assert r["provenance"]["pillar"] == 251
    assert abs(sum(r["routing_probabilities"].values()) - 1.0) < 1e-12
    assert len(r["intervention_sequence"]) == 4
    assert "FALSIFIED" in r["falsification_condition"]
