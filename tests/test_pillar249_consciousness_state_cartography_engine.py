# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 249 — Consciousness State Cartography Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar249_consciousness_state_cartography_engine import (
    ADJACENCY_TRACK_LABEL,
    C_S,
    CONSCIOUSNESS_TRACK_LABEL,
    K_CS,
    N_W,
    PHI0,
    SCORE_WEIGHTS,
    STATE_ORDER,
    ConsciousnessStateScenario,
    __provenance__,
    baseline_consciousness_state_catalogue,
    classify_state,
    consciousness_access_score,
    geometry_alignment_stack,
    network_integration_stack,
    neuromodulator_stack,
    pillar249_consciousness_state_report,
    separation_guard,
    sleep_architecture_stack,
    state_landscape_report,
    transition_stack,
    uncertainty_bands,
)


def _catalogue() -> dict[str, ConsciousnessStateScenario]:
    return baseline_consciousness_state_catalogue()


# ---------------------------------------------------------------------------
# Provenance + constants
# ---------------------------------------------------------------------------

def test_provenance_contract():
    assert __provenance__["pillar"] == 249
    assert __provenance__["title"] == "Consciousness State Cartography Engine"
    assert __provenance__["version"] == "v11.1"
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert "non-clinical" in __provenance__["status"]



def test_framework_constants():
    assert N_W == 5
    assert K_CS == 74
    assert K_CS == 5**2 + 7**2
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
    assert abs(math.cos(PHI0) - PHI0) < 1e-12



def test_orders_and_weights_contracts():
    assert STATE_ORDER == (
        "wake",
        "rem",
        "nrem",
        "anesthesia",
        "coma",
        "near_death_transition",
    )
    assert set(SCORE_WEIGHTS.keys()) == {
        "neuromodulator_balance",
        "network_integration",
        "state_support",
        "metabolic_reversibility",
        "geometry_alignment",
    }
    assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-12


# ---------------------------------------------------------------------------
# Separation guard + catalogue
# ---------------------------------------------------------------------------

def test_separation_guard_fields():
    g = separation_guard()
    assert g["label"] == ADJACENCY_TRACK_LABEL
    assert g["track"] == CONSCIOUSNESS_TRACK_LABEL
    assert g["hardgate_isolation"] is True
    assert g["clinical_claims_allowed"] is False
    assert g["metaphysical_claims_allowed"] is False
    assert g["postmortem_survival_claims_allowed"] is False
    assert "irreversible brain death" in g["message"]



def test_baseline_catalogue_keys_match_state_order():
    cat = _catalogue()
    assert tuple(cat.keys()) == STATE_ORDER
    assert all(isinstance(cat[name], ConsciousnessStateScenario) for name in STATE_ORDER)



def test_schema_invalid_unit_interval_raises():
    s = _catalogue()["wake"]
    with pytest.raises(ValueError):
        ConsciousnessStateScenario(**{**s.__dict__, "acetylcholine": 1.1})
    with pytest.raises(ValueError):
        ConsciousnessStateScenario(**{**s.__dict__, "perfusion_fraction": -0.1})



def test_schema_empty_name_raises():
    s = _catalogue()["wake"]
    with pytest.raises(ValueError):
        ConsciousnessStateScenario(**{**s.__dict__, "name": ""})


# ---------------------------------------------------------------------------
# Neuromodulator stack
# ---------------------------------------------------------------------------

def test_neuromodulator_stack_shape_and_ranges():
    r = neuromodulator_stack(_catalogue()["wake"])
    assert set(r.keys()) == {
        "wake_drive",
        "monoamine_withdrawal",
        "dopaminergic_gain",
        "serotonergic_tone",
        "residual_excitation",
        "excitation_snr",
        "excitation_snr_norm",
        "neuromodulator_balance_score",
        "rem_bias",
        "status",
    }
    assert 0.0 <= r["wake_drive"] <= 1.0
    assert 0.0 <= r["monoamine_withdrawal"] <= 1.0
    assert r["dopaminergic_gain"] >= 1.0
    assert r["serotonergic_tone"] >= 0.0
    assert 0.0 <= r["residual_excitation"] <= 1.0
    assert r["excitation_snr"] >= 0.0
    assert 0.0 <= r["excitation_snr_norm"] <= 1.0
    assert 0.0 <= r["neuromodulator_balance_score"] <= 1.0
    assert 0.0 <= r["rem_bias"] <= 1.0



def test_wake_has_higher_wake_drive_than_nrem():
    cat = _catalogue()
    assert neuromodulator_stack(cat["wake"])["wake_drive"] > neuromodulator_stack(cat["nrem"])["wake_drive"]



def test_rem_has_higher_rem_bias_than_wake():
    cat = _catalogue()
    assert neuromodulator_stack(cat["rem"])["rem_bias"] > neuromodulator_stack(cat["wake"])["rem_bias"]


# ---------------------------------------------------------------------------
# Network integration
# ---------------------------------------------------------------------------

def test_network_stack_shape_and_ranges():
    r = network_integration_stack(_catalogue()["wake"])
    assert set(r.keys()) == {
        "integration_score",
        "perturbational_capacity",
        "collapse_risk",
        "status",
    }
    assert 0.0 <= r["integration_score"] <= 1.0
    assert 0.0 <= r["perturbational_capacity"] <= 1.0
    assert 0.0 <= r["collapse_risk"] <= 1.0



def test_wake_integration_exceeds_coma():
    cat = _catalogue()
    assert network_integration_stack(cat["wake"])["integration_score"] > network_integration_stack(cat["coma"])["integration_score"]



def test_coma_collapse_risk_exceeds_wake():
    cat = _catalogue()
    assert network_integration_stack(cat["coma"])["collapse_risk"] > network_integration_stack(cat["wake"])["collapse_risk"]


# ---------------------------------------------------------------------------
# Sleep architecture
# ---------------------------------------------------------------------------

def test_sleep_stack_shape_and_ranges():
    r = sleep_architecture_stack(_catalogue()["nrem"])
    assert set(r.keys()) == {
        "wake_pressure",
        "rem_drive",
        "slow_wave_drive",
        "dominant_rhythm",
        "status",
    }
    assert 0.0 <= r["wake_pressure"] <= 1.0
    assert 0.0 <= r["rem_drive"] <= 1.0
    assert 0.0 <= r["slow_wave_drive"] <= 1.0
    assert r["dominant_rhythm"] in {"wake", "rem", "slow_wave"}



def test_rem_and_nrem_dominant_rhythms_match_expectations():
    cat = _catalogue()
    assert sleep_architecture_stack(cat["rem"])["dominant_rhythm"] == "rem"
    assert sleep_architecture_stack(cat["nrem"])["dominant_rhythm"] == "slow_wave"


# ---------------------------------------------------------------------------
# Transition + geometry
# ---------------------------------------------------------------------------

def test_transition_stack_shape_and_ranges():
    r = transition_stack(_catalogue()["near_death_transition"])
    assert set(r.keys()) == {
        "reversibility_score",
        "near_death_signal",
        "boundary_zone",
        "status",
    }
    assert 0.0 <= r["reversibility_score"] <= 1.0
    assert 0.0 <= r["near_death_signal"] <= 1.0
    assert isinstance(r["boundary_zone"], bool)



def test_near_death_has_boundary_zone_and_stronger_signal_than_coma():
    cat = _catalogue()
    near = transition_stack(cat["near_death_transition"])
    coma = transition_stack(cat["coma"])
    assert near["boundary_zone"] is True
    assert near["near_death_signal"] > coma["near_death_signal"]



def test_geometry_stack_shape_and_ranges():
    r = geometry_alignment_stack(_catalogue()["wake"])
    assert set(r.keys()) == {
        "phi_eff",
        "beta",
        "resonance_quality",
        "entropy_coherence",
        "geometry_alignment_score",
        "status",
    }
    assert r["phi_eff"] > 0.0
    assert r["beta"] > 0.0
    assert 0.0 <= r["resonance_quality"] <= 1.0
    assert 0.0 <= r["entropy_coherence"] <= 1.0
    assert 0.0 <= r["geometry_alignment_score"] <= 1.0


# ---------------------------------------------------------------------------
# Classification + composite score
# ---------------------------------------------------------------------------

def test_baseline_scenarios_classify_as_themselves():
    cat = _catalogue()
    for name in STATE_ORDER:
        assert classify_state(cat[name])["predicted_state"] == name



def test_composite_score_shape_and_ranges():
    r = consciousness_access_score(_catalogue()["wake"])
    assert "neuromodulators" in r
    assert "network" in r
    assert "sleep" in r
    assert "transition" in r
    assert "geometry" in r
    assert "classification" in r
    assert "score_weights" in r
    assert "state_support_score" in r
    assert "consciousness_access_score" in r
    assert "access_band" in r
    assert 0.0 <= r["state_support_score"] <= 1.0
    assert 0.0 <= r["consciousness_access_score"] <= 1.0
    assert r["access_band"] in {
        "high-conscious-access",
        "intermediate-conscious-access",
        "low-conscious-access",
    }



def test_score_ordering_matches_expected_state_hierarchy():
    cat = _catalogue()
    scores = {
        name: consciousness_access_score(cat[name])["consciousness_access_score"]
        for name in STATE_ORDER
    }
    assert scores["wake"] > scores["rem"] > scores["nrem"]
    assert scores["nrem"] > scores["anesthesia"] > scores["coma"]
    assert scores["near_death_transition"] < scores["nrem"]



def test_access_bands_match_expected_extremes():
    cat = _catalogue()
    assert consciousness_access_score(cat["wake"])["access_band"] == "high-conscious-access"
    assert consciousness_access_score(cat["coma"])["access_band"] == "low-conscious-access"


# ---------------------------------------------------------------------------
# Uncertainty
# ---------------------------------------------------------------------------

def test_uncertainty_band_shape_and_ordering():
    u = uncertainty_bands(_catalogue()["wake"], n_trials=120, seed=249)
    assert set(u.keys()) == {
        "mean_score",
        "p10_score",
        "p50_score",
        "p90_score",
        "uncertainty_spread",
        "uncertainty_band",
        "dominant_state",
        "state_counts",
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
    assert u["dominant_state"] in STATE_ORDER
    assert set(u["state_counts"].keys()) == set(STATE_ORDER)



def test_uncertainty_reproducible_for_same_seed():
    s = _catalogue()["near_death_transition"]
    assert uncertainty_bands(s, n_trials=80, seed=77) == uncertainty_bands(s, n_trials=80, seed=77)



def test_uncertainty_invalid_trials_raises():
    with pytest.raises(ValueError):
        uncertainty_bands(_catalogue()["wake"], n_trials=0)


# ---------------------------------------------------------------------------
# Landscape + integrated report
# ---------------------------------------------------------------------------

def test_landscape_report_shape_and_ranking():
    report = state_landscape_report(n_trials=40, seed=249)
    assert set(report.keys()) == {
        "reports",
        "ranking",
        "highest_access_state",
        "lowest_access_state",
        "status",
    }
    assert tuple(report["reports"].keys()) == STATE_ORDER
    assert len(report["ranking"]) == len(STATE_ORDER)
    assert report["highest_access_state"] == "wake"
    assert report["lowest_access_state"] in {"coma", "near_death_transition"}
    for i in range(len(report["ranking"]) - 1):
        assert report["ranking"][i]["score"] >= report["ranking"][i + 1]["score"]



def test_integrated_report_shape_and_boundaries():
    report = pillar249_consciousness_state_report(n_trials=30, seed=249)
    assert report["pillar"] == 249
    assert "ADJACENT RESEARCH TRACK" in report["status"]
    assert report["separation_guard"]["clinical_claims_allowed"] is False
    assert report["separation_guard"]["metaphysical_claims_allowed"] is False
    assert "landscape" in report
    assert "falsification_condition" in report
    assert "epistemic_boundary" in report
    assert "irreversible brain death" in report["epistemic_boundary"]
