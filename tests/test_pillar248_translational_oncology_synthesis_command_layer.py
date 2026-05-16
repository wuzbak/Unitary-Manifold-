# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 248 — Translational Oncology Synthesis Command Layer.

Test plan scope:
- constants and provenance contract
- dataclass schema validation
- scoring math behavior and bounds
- intervention planning outputs
- uncertainty band determinism
- explicit non-hardgate/no-clinical separation guard

This suite intentionally provides 50+ assertion checks.
"""

from __future__ import annotations

import math

import pytest

from src.core.pillar248_translational_oncology_synthesis_command_layer import (
    ADJACENCY_TRACK_LABEL,
    C_S,
    INTERVENTION_ORDER,
    K_CS,
    N_W,
    PHI0,
    SCORE_WEIGHTS,
    TRANSLATIONAL_ONCOLOGY_TRACK_LABEL,
    TranslationalOncologyScenario,
    __provenance__,
    baseline_translational_oncology_scenario,
    bottleneck_synthesis_stack,
    control_profile,
    diagnostic_signal_stack,
    intervention_planning_stack,
    pillar248_translational_oncology_report,
    separation_guard,
    translational_oncology_synthesis_score,
    uncertainty_bands,
)


def _scenario() -> TranslationalOncologyScenario:
    return baseline_translational_oncology_scenario()


# ---------------------------------------------------------------------------
# Provenance + constants
# ---------------------------------------------------------------------------

def test_provenance_contract():
    assert __provenance__["pillar"] == 248
    assert __provenance__["title"] == "Translational Oncology Synthesis Command Layer"
    assert __provenance__["license_software"] == "AGPL-3.0-or-later"
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert "non-hardgate" in __provenance__["status"]


def test_framework_constants():
    assert N_W == 5
    assert K_CS == 74
    assert K_CS == 5**2 + 7**2
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12


def test_orders_and_weights_contracts():
    assert len(INTERVENTION_ORDER) == 4
    assert INTERVENTION_ORDER[0] == "enrollment_acceleration"
    assert INTERVENTION_ORDER[-1] == "resistance_prevention"
    assert set(SCORE_WEIGHTS.keys()) == {
        "diagnostic_signal",
        "execution_readiness",
        "control_tractability",
        "intervention_feasibility",
        "cross_pillar_alignment",
    }
    assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# Separation guard
# ---------------------------------------------------------------------------

def test_separation_guard_fields():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["track"] == TRANSLATIONAL_ONCOLOGY_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["toe_score_delta_allowed"] is False
    assert g["physics_claim_promotion_allowed"] is False
    assert g["clinical_claims_allowed"] is False
    assert g["patient_specific_recommendation_allowed"] is False
    assert "never clinical care directives" in g["message"]


# ---------------------------------------------------------------------------
# Dataclass schema
# ---------------------------------------------------------------------------

def test_baseline_schema_sanity():
    s = _scenario()
    assert isinstance(s, TranslationalOncologyScenario)
    assert 0.0 <= s.prevalence <= 1.0
    assert 0.0 <= s.sensitivity <= 1.0
    assert 0.0 <= s.specificity <= 1.0
    assert set(s.modality_probabilities.keys()) == set(s.modality_weights.keys())
    assert len(s.modality_probabilities) >= 3
    assert s.initial_tumor_size > 0
    assert s.mutation_rate > 0


@pytest.mark.parametrize(
    "field,value",
    [
        ("sensitivity", 1.2),
        ("participation_rate", 1.1),
        ("drug_holiday_fraction", -0.1),
    ],
)
def test_schema_invalid_unit_interval_raises(field: str, value: float):
    s = _scenario()
    with pytest.raises(ValueError):
        TranslationalOncologyScenario(**{**s.__dict__, field: value})


def test_schema_invalid_modalities_raises_on_missing_weights_key():
    s = _scenario()
    bad_weights = dict(s.modality_weights)
    bad_weights.pop("mri")
    with pytest.raises(ValueError):
        TranslationalOncologyScenario(**{**s.__dict__, "modality_weights": bad_weights})


def test_schema_invalid_empty_modality_probabilities_raises():
    s = _scenario()
    with pytest.raises(ValueError):
        TranslationalOncologyScenario(**{**s.__dict__, "modality_probabilities": {}})


def test_schema_invalid_non_positive_numeric_raises():
    s = _scenario()
    with pytest.raises(ValueError):
        TranslationalOncologyScenario(**{**s.__dict__, "eligible_patients": 0})
    with pytest.raises(ValueError):
        TranslationalOncologyScenario(**{**s.__dict__, "mutation_rate": 0.0})


# ---------------------------------------------------------------------------
# Control profile
# ---------------------------------------------------------------------------

def test_control_profile_keys_and_bounds():
    profile = control_profile(_scenario())
    assert set(profile.keys()) == {
        "heterogeneity_gap",
        "resistance_gap",
        "immune_escape_gap",
        "early_detection_gap",
        "targetability_gap",
        "access_gap",
    }
    for v in profile.values():
        assert 0.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# Diagnostic stack
# ---------------------------------------------------------------------------

def test_diagnostic_signal_stack_shape_and_ranges():
    r = diagnostic_signal_stack(_scenario())
    assert set(r.keys()) == {"bayes", "fusion", "triage", "alignment", "diagnostic_signal_score", "status"}
    assert 0.0 <= r["diagnostic_signal_score"] <= 1.0
    assert 0.0 <= r["bayes"]["ppv"] <= 1.0
    assert 0.0 <= r["bayes"]["npv"] <= 1.0
    assert 0.0 <= r["fusion"]["fused_probability"] <= 1.0
    assert 0.0 <= r["fusion"]["disagreement_index"] <= 1.0
    assert 0.0 <= r["alignment"]["alignment_score"] <= 1.0
    assert isinstance(r["triage"]["action"], str)


def test_diagnostic_signal_score_reduces_with_more_disagreement():
    s = _scenario()
    good = TranslationalOncologyScenario(
        **{
            **s.__dict__,
            "modality_probabilities": {"ultrasound": 0.68, "mri": 0.70, "liquid_biopsy": 0.69},
        }
    )
    bad = TranslationalOncologyScenario(
        **{
            **s.__dict__,
            "modality_probabilities": {"ultrasound": 0.20, "mri": 0.85, "liquid_biopsy": 0.95},
        }
    )
    assert diagnostic_signal_stack(good)["diagnostic_signal_score"] > diagnostic_signal_stack(bad)["diagnostic_signal_score"]


# ---------------------------------------------------------------------------
# Bottleneck synthesis
# ---------------------------------------------------------------------------

def test_bottleneck_stack_shape_and_ranges():
    r = bottleneck_synthesis_stack(_scenario())
    assert set(r.keys()) == {
        "enrollment",
        "access",
        "preclinical_paradox",
        "liquid_biopsy",
        "execution_readiness_score",
        "status",
    }
    assert 0.0 <= r["execution_readiness_score"] <= 1.0
    assert 0.0 <= r["enrollment"]["deficit_fraction"] <= 1.0
    assert 0.0 <= r["access"]["access_barrier_score"] <= 1.0
    assert 0.0 <= r["preclinical_paradox"]["expected_human_efficacy"] <= 1.0
    assert 0.0 <= r["liquid_biopsy"]["ppv"] <= 1.0
    assert 0.0 <= r["liquid_biopsy"]["npv"] <= 1.0


def test_bottleneck_execution_readiness_increases_with_trial_participation():
    s = _scenario()
    base = bottleneck_synthesis_stack(s)["execution_readiness_score"]
    better = TranslationalOncologyScenario(**{**s.__dict__, "participation_rate": 0.10})
    assert bottleneck_synthesis_stack(better)["execution_readiness_score"] > base


# ---------------------------------------------------------------------------
# Intervention planning
# ---------------------------------------------------------------------------

def test_intervention_planning_stack_shape_and_ranges():
    r = intervention_planning_stack(_scenario())
    assert r["intervention_order"] == INTERVENTION_ORDER
    assert "enrollment_plan" in r
    assert "detection_plan" in r
    assert "financial_plan" in r
    assert "resistance_plan" in r
    assert "prioritization" in r
    assert 0.0 <= r["intervention_feasibility_score"] <= 1.0
    assert len(r["prioritization"]) == 4


def test_intervention_prioritization_sorted_descending():
    rows = intervention_planning_stack(_scenario())["prioritization"]
    for i in range(len(rows) - 1):
        assert rows[i]["impact_score"] >= rows[i + 1]["impact_score"]


def test_intervention_prioritization_names_cover_full_order():
    rows = intervention_planning_stack(_scenario())["prioritization"]
    names = {r["name"] for r in rows}
    assert names == set(INTERVENTION_ORDER)


# ---------------------------------------------------------------------------
# Synthesis score
# ---------------------------------------------------------------------------

def test_synthesis_score_shape_and_ranges():
    r = translational_oncology_synthesis_score(_scenario())
    assert "diagnostic" in r
    assert "bottleneck" in r
    assert "planning" in r
    assert "control" in r
    assert "direction" in r
    assert "score_weights" in r
    assert "translational_synthesis_score" in r
    assert "readiness_band" in r
    assert 0.0 <= r["translational_synthesis_score"] <= 1.0
    assert r["readiness_band"] in {
        "high-synthesis-readiness",
        "intermediate-synthesis-readiness",
        "low-synthesis-readiness",
    }


def test_synthesis_score_responds_to_gap_severity():
    s = _scenario()
    better = TranslationalOncologyScenario(
        **{
            **s.__dict__,
            "heterogeneity_gap": 0.20,
            "resistance_gap": 0.20,
            "immune_escape_gap": 0.20,
            "early_detection_gap": 0.20,
            "targetability_gap": 0.20,
            "access_gap": 0.20,
        }
    )
    worse = TranslationalOncologyScenario(
        **{
            **s.__dict__,
            "heterogeneity_gap": 0.85,
            "resistance_gap": 0.85,
            "immune_escape_gap": 0.85,
            "early_detection_gap": 0.85,
            "targetability_gap": 0.85,
            "access_gap": 0.85,
        }
    )
    assert (
        translational_oncology_synthesis_score(better)["translational_synthesis_score"]
        > translational_oncology_synthesis_score(worse)["translational_synthesis_score"]
    )


# ---------------------------------------------------------------------------
# Uncertainty
# ---------------------------------------------------------------------------

def test_uncertainty_band_shape_and_ordering():
    u = uncertainty_bands(_scenario(), n_trials=120, seed=248)
    assert set(u.keys()) == {
        "mean_score",
        "p10_score",
        "p50_score",
        "p90_score",
        "uncertainty_spread",
        "uncertainty_band",
        "n_trials",
        "seed",
    }
    assert 0.0 <= u["mean_score"] <= 1.0
    assert 0.0 <= u["p10_score"] <= 1.0
    assert 0.0 <= u["p50_score"] <= 1.0
    assert 0.0 <= u["p90_score"] <= 1.0
    assert u["p10_score"] <= u["p50_score"] <= u["p90_score"]
    assert u["uncertainty_spread"] >= 0.0
    assert u["uncertainty_band"] in {"tight", "moderate", "wide"}


def test_uncertainty_reproducible_for_same_seed():
    u1 = uncertainty_bands(_scenario(), n_trials=60, seed=99)
    u2 = uncertainty_bands(_scenario(), n_trials=60, seed=99)
    assert u1 == u2


def test_uncertainty_invalid_trials_raises():
    with pytest.raises(ValueError):
        uncertainty_bands(_scenario(), n_trials=0)


# ---------------------------------------------------------------------------
# Integrated report
# ---------------------------------------------------------------------------

def test_integrated_report_shape_and_boundaries():
    report = pillar248_translational_oncology_report(n_trials=80, seed=248)
    assert report["pillar"] == 248
    assert "ADJACENT RESEARCH TRACK" in report["status"]
    assert "separation_guard" in report
    assert "scenario" in report
    assert "synthesis" in report
    assert "uncertainty" in report
    assert "falsification_condition" in report
    assert "epistemic_boundary" in report
    assert report["separation_guard"]["clinical_claims_allowed"] is False
    assert "No clinical efficacy claim is made" in report["epistemic_boundary"]


def test_integrated_report_deterministic_under_seed():
    r1 = pillar248_translational_oncology_report(n_trials=60, seed=11)
    r2 = pillar248_translational_oncology_report(n_trials=60, seed=11)
    assert r1["synthesis"]["translational_synthesis_score"] == r2["synthesis"]["translational_synthesis_score"]
    assert r1["uncertainty"] == r2["uncertainty"]


def test_integrated_report_accepts_custom_scenario():
    s = _scenario()
    report = pillar248_translational_oncology_report(scenario=s, n_trials=40, seed=248)
    assert report["scenario"] == s
    assert 0.0 <= report["synthesis"]["translational_synthesis_score"] <= 1.0
    assert report["uncertainty"]["n_trials"] == 40
