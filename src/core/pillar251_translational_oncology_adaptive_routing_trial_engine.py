# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 251 — Translational Oncology Adaptive Routing & Trial Engine.

Adjacent research track (non-hardgate): operational synthesis layer that extends
Pillar 248 into patient-state routing, intervention sequencing, adaptive trial
design, access optimization, and uncertainty accounting.

Boundary statement (strict):
- Research planning and systems simulation only.
- Not a medical device, not treatment advice, not patient-specific care output.
- No hardgate physics promotion.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from src.core.pillar248_translational_oncology_synthesis_command_layer import (
    TranslationalOncologyScenario,
    baseline_translational_oncology_scenario,
    translational_oncology_synthesis_score,
)

__provenance__ = {
    "pillar": 251,
    "title": "Translational Oncology Adaptive Routing & Trial Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — translational oncology operating-system "
        "extension; non-hardgate, non-clinical"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

ADJACENCY_TRACK_LABEL = "ADJACENT RESEARCH TRACK"
ONCOLOGY_ROUTING_TRACK_LABEL = "TRANSLATIONAL_ONCOLOGY_ADAPTIVE_ROUTING_TRACK"

PATHWAYS: tuple[str, ...] = (
    "standard_of_care",
    "biomarker_adaptive",
    "ctdna_response_adaptive",
    "triplet_combo_escalation",
)


@dataclass(frozen=True)
class AdaptiveOncologyState:
    stage_severity: float
    biomarker_actionability: float
    ctdna_signal_strength: float
    ecog_function: float
    prior_line_burden: float
    travel_distance_km: float
    insurance_coverage_fraction: float
    copay_pressure_fraction: float
    trial_site_density: float
    digital_access_fraction: float
    toxicity_risk_fraction: float
    response_uncertainty: float

    def __post_init__(self) -> None:
        for f in (
            "stage_severity",
            "biomarker_actionability",
            "ctdna_signal_strength",
            "ecog_function",
            "prior_line_burden",
            "insurance_coverage_fraction",
            "copay_pressure_fraction",
            "trial_site_density",
            "digital_access_fraction",
            "toxicity_risk_fraction",
            "response_uncertainty",
        ):
            _validate01(f, float(getattr(self, f)))
        if self.travel_distance_km < 0:
            raise ValueError("travel_distance_km must be >= 0")


def _validate01(name: str, value: float) -> None:
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def separation_guard() -> dict[str, Any]:
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": ONCOLOGY_ROUTING_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "clinical_claims_allowed": False,
        "patient_specific_recommendation_allowed": False,
        "message": (
            "Pillar 251 outputs are trial and access planning artifacts only; "
            "never clinical directives for individual patients."
        ),
    }


def patient_state_routing_probabilities(s: AdaptiveOncologyState) -> dict[str, float]:
    standard = _clamp01(
        0.45 * (1.0 - s.biomarker_actionability)
        + 0.35 * (1.0 - s.ctdna_signal_strength)
        + 0.20 * s.prior_line_burden
    )
    biomarker = _clamp01(
        0.50 * s.biomarker_actionability
        + 0.20 * (1.0 - s.toxicity_risk_fraction)
        + 0.30 * s.ecog_function
    )
    ctdna = _clamp01(
        0.55 * s.ctdna_signal_strength
        + 0.20 * s.response_uncertainty
        + 0.25 * s.digital_access_fraction
    )
    triplet = _clamp01(
        0.35 * s.stage_severity
        + 0.35 * s.prior_line_burden
        + 0.20 * s.biomarker_actionability
        + 0.10 * (1.0 - s.toxicity_risk_fraction)
    )

    raw = {
        "standard_of_care": standard,
        "biomarker_adaptive": biomarker,
        "ctdna_response_adaptive": ctdna,
        "triplet_combo_escalation": triplet,
    }
    z = sum(raw.values())
    if z <= 0:
        return {k: 1.0 / len(PATHWAYS) for k in PATHWAYS}
    return {k: raw[k] / z for k in PATHWAYS}


def intervention_sequencing_plan(s: AdaptiveOncologyState) -> list[dict[str, Any]]:
    seq = [
        {
            "step": 1,
            "name": "state_staging_and_biomarker_refresh",
            "go_threshold": _clamp01(0.60 - 0.15 * s.stage_severity),
            "fallback": "expedite_multimodal_imaging",
        },
        {
            "step": 2,
            "name": "adaptive_trial_allocation",
            "go_threshold": _clamp01(0.52 + 0.20 * s.biomarker_actionability),
            "fallback": "bridge_soc_with_ctdna_monitoring",
        },
        {
            "step": 3,
            "name": "access_equity_activation",
            "go_threshold": _clamp01(0.45 + 0.25 * (1.0 - s.copay_pressure_fraction)),
            "fallback": "navigator_plus_remote_enrollment",
        },
        {
            "step": 4,
            "name": "resistance_prevention_feedback",
            "go_threshold": _clamp01(0.40 + 0.30 * (1.0 - s.response_uncertainty)),
            "fallback": "schedule_early_interim_pivot",
        },
    ]
    return seq


def adaptive_trial_design_specification(s: AdaptiveOncologyState) -> dict[str, Any]:
    design_type = (
        "platform_trial"
        if s.biomarker_actionability >= 0.55 and s.ctdna_signal_strength >= 0.45
        else "seamless_adaptive"
    )
    n_initial_arms = 4 if s.stage_severity >= 0.5 else 3
    max_arms = n_initial_arms + 2
    interim_every = 60 if s.response_uncertainty >= 0.45 else 90
    return {
        "design_type": design_type,
        "n_initial_arms": n_initial_arms,
        "max_arms": max_arms,
        "interim_analysis_every_patients": interim_every,
        "allocation_strategy": "response_adaptive",
        "target_conditional_power": _clamp01(0.75 + 0.15 * s.biomarker_actionability),
        "sample_size_reallocation_cap": _clamp01(0.20 + 0.20 * s.response_uncertainty),
    }


def access_optimization(s: AdaptiveOncologyState) -> dict[str, Any]:
    distance_barrier = _clamp01(s.travel_distance_km / 800.0)
    affordability = _clamp01(
        0.60 * s.insurance_coverage_fraction + 0.40 * (1.0 - s.copay_pressure_fraction)
    )
    virtual_eligibility = _clamp01(
        0.65 * s.digital_access_fraction + 0.35 * s.ecog_function
    )
    site_fit = _clamp01(0.55 * s.trial_site_density + 0.45 * (1.0 - distance_barrier))
    equity_score = _clamp01(0.35 * affordability + 0.30 * virtual_eligibility + 0.35 * site_fit)
    return {
        "distance_barrier": distance_barrier,
        "affordability_score": affordability,
        "virtual_trial_eligibility": virtual_eligibility,
        "site_fit_score": site_fit,
        "equity_access_score": equity_score,
    }


def uncertainty_accounting(s: AdaptiveOncologyState) -> dict[str, Any]:
    elasticities = {
        "response_uncertainty": 0.36,
        "biomarker_actionability": 0.24,
        "ctdna_signal_strength": 0.20,
        "copay_pressure_fraction": 0.12,
        "trial_site_density": 0.08,
    }
    top_driver = max(elasticities, key=elasticities.get)
    option_value_wait = _clamp01(0.45 + 0.45 * s.response_uncertainty)
    option_value_commit = _clamp01(0.62 - 0.25 * s.response_uncertainty)
    return {
        "elasticity_map": elasticities,
        "top_driver": top_driver,
        "option_value_wait": option_value_wait,
        "option_value_commit": option_value_commit,
        "recommendation": "wait_for_more_signal" if option_value_wait > option_value_commit else "commit_now",
    }


def translational_operating_score(
    state: AdaptiveOncologyState,
    base: TranslationalOncologyScenario,
) -> float:
    base_score = float(
        translational_oncology_synthesis_score(base)["translational_synthesis_score"]
    )
    routes = patient_state_routing_probabilities(state)
    access = access_optimization(state)
    uncertainty = uncertainty_accounting(state)

    route_focus = max(routes.values())
    uncertainty_penalty = 1.0 - 0.25 * float(state.response_uncertainty)
    score = _clamp01(
        (0.45 * base_score + 0.20 * route_focus + 0.20 * access["equity_access_score"] + 0.15 * uncertainty["option_value_commit"])
        * uncertainty_penalty
    )
    return score


def monte_carlo_operating_envelope(
    state: AdaptiveOncologyState,
    base: TranslationalOncologyScenario,
    n_trials: int = 251,
    sigma: float = 0.06,
    seed: int = 251,
) -> dict[str, float | str]:
    if n_trials < 10:
        raise ValueError("n_trials must be >= 10")
    if sigma < 0:
        raise ValueError("sigma must be >= 0")

    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(n_trials):
        s = AdaptiveOncologyState(
            **{
                **state.__dict__,
                "biomarker_actionability": _clamp01(state.biomarker_actionability + rng.uniform(-sigma, sigma)),
                "ctdna_signal_strength": _clamp01(state.ctdna_signal_strength + rng.uniform(-sigma, sigma)),
                "copay_pressure_fraction": _clamp01(state.copay_pressure_fraction + rng.uniform(-sigma, sigma)),
                "response_uncertainty": _clamp01(state.response_uncertainty + rng.uniform(-sigma, sigma)),
                "trial_site_density": _clamp01(state.trial_site_density + rng.uniform(-sigma, sigma)),
            }
        )
        values.append(translational_operating_score(s, base))

    values.sort()
    i10 = int(0.10 * (n_trials - 1))
    i50 = int(0.50 * (n_trials - 1))
    i90 = int(0.90 * (n_trials - 1))
    return {
        "p10": values[i10],
        "p50": values[i50],
        "p90": values[i90],
        "spread": values[i90] - values[i10],
        "status": "CALCULATED deterministic operating envelope",
    }


def baseline_adaptive_oncology_state() -> AdaptiveOncologyState:
    return AdaptiveOncologyState(
        stage_severity=0.58,
        biomarker_actionability=0.54,
        ctdna_signal_strength=0.61,
        ecog_function=0.74,
        prior_line_burden=0.40,
        travel_distance_km=86.0,
        insurance_coverage_fraction=0.63,
        copay_pressure_fraction=0.46,
        trial_site_density=0.58,
        digital_access_fraction=0.69,
        toxicity_risk_fraction=0.34,
        response_uncertainty=0.49,
    )


def pillar251_translational_oncology_operating_report() -> dict[str, Any]:
    base = baseline_translational_oncology_scenario()
    state = baseline_adaptive_oncology_state()
    score = translational_operating_score(state, base)
    return {
        "provenance": __provenance__,
        "separation_guard": separation_guard(),
        "baseline_state": state,
        "routing_probabilities": patient_state_routing_probabilities(state),
        "intervention_sequence": intervention_sequencing_plan(state),
        "trial_design": adaptive_trial_design_specification(state),
        "access_plan": access_optimization(state),
        "uncertainty": uncertainty_accounting(state),
        "operating_score": score,
        "status_band": "HIGH" if score >= 0.75 else "INTERMEDIATE" if score >= 0.50 else "LOW",
        "operating_envelope": monte_carlo_operating_envelope(state, base),
        "falsification_condition": (
            "FALSIFIED if pre-registered multicenter evaluations show no "
            "predictive linkage between routing/sequence outputs and observed "
            "trial throughput, access equity, or adaptation efficiency outcomes."
        ),
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "C_S",
    "K_CS",
    "N_W",
    "ONCOLOGY_ROUTING_TRACK_LABEL",
    "PATHWAYS",
    "PHI0",
    "AdaptiveOncologyState",
    "__provenance__",
    "access_optimization",
    "adaptive_trial_design_specification",
    "baseline_adaptive_oncology_state",
    "intervention_sequencing_plan",
    "monte_carlo_operating_envelope",
    "patient_state_routing_probabilities",
    "pillar251_translational_oncology_operating_report",
    "separation_guard",
    "translational_operating_score",
    "uncertainty_accounting",
]
