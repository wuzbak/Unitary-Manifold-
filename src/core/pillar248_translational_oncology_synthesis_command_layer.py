# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 248 — Translational Oncology Synthesis Command Layer.

Adjacent applied research track (non-hardgate): this module synthesizes outputs
from existing adjacent oncology modules (Pillars 223, 228, 230, 232) into a
single research-planning command surface.

Boundary statement (strict):
- This module is for research prioritization and scenario analysis only.
- It is not a clinical decision system, not a treatment recommendation engine,
  and not a diagnostic device.
- No output should be interpreted as patient-specific medical advice.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any, Mapping

from src.core.pillar223_medical_imaging_diagnosis import (
    bayes_ppv_npv,
    cross_pillar_alignment_score,
    diagnostic_triage,
    fused_diagnostic_probability,
)
from src.core.pillar228_cancer_bottleneck_calculator import (
    access_barrier_fraction,
    enrollment_deficit,
    liquid_biopsy_ppv_npv,
    preclinical_paradox_score,
)
from src.core.pillar230_cancer_solutions_engine import (
    detection_improvement_pathway,
    enrollment_intervention_model,
    financial_access_intervention,
    resistance_prevention_model,
)
from src.core.pillar232_universal_cancer_control_framework import (
    missing_key_direction,
    precision_weighted_control_probability,
)

__provenance__ = {
    "pillar": 248,
    "title": "Translational Oncology Synthesis Command Layer",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — translational oncology synthesis command "
        "layer; non-hardgate, no clinical claims"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

ADJACENCY_TRACK_LABEL = "ADJACENT RESEARCH TRACK"
TRANSLATIONAL_ONCOLOGY_TRACK_LABEL = "TRANSLATIONAL_ONCOLOGY_SYNTHESIS_TRACK"

INTERVENTION_ORDER: tuple[str, ...] = (
    "enrollment_acceleration",
    "detection_calibration",
    "financial_toxicity_reduction",
    "resistance_prevention",
)

SCORE_WEIGHTS: Mapping[str, float] = {
    "diagnostic_signal": 0.30,
    "execution_readiness": 0.20,
    "control_tractability": 0.25,
    "intervention_feasibility": 0.15,
    "cross_pillar_alignment": 0.10,
}


@dataclass(frozen=True)
class TranslationalOncologyScenario:
    prevalence: float
    sensitivity: float
    specificity: float

    modality_probabilities: Mapping[str, float]
    modality_weights: Mapping[str, float]
    critical_symptom_score: float
    ultrasound_mechanical_index: float
    nanosensor_snr_db: float

    eligible_patients: float
    participation_rate: float

    annual_drug_cost_usd: float
    median_annual_income_usd: float
    insurance_coverage_fraction: float
    proposed_oop_cap_usd: float

    preclinical_animal_efficacy: float

    heterogeneity_gap: float
    resistance_gap: float
    immune_escape_gap: float
    early_detection_gap: float
    targetability_gap: float
    access_gap: float

    decentralized_trial_adoption: float
    navigator_program_coverage: float
    financial_assistance_coverage: float

    initial_tumor_size: int
    mutation_rate: float
    n_drugs_in_combination: int
    adaptive_therapy_cycles: int
    drug_holiday_fraction: float

    def __post_init__(self) -> None:
        for name in (
            "prevalence",
            "sensitivity",
            "specificity",
            "critical_symptom_score",
            "participation_rate",
            "insurance_coverage_fraction",
            "preclinical_animal_efficacy",
            "heterogeneity_gap",
            "resistance_gap",
            "immune_escape_gap",
            "early_detection_gap",
            "targetability_gap",
            "access_gap",
            "decentralized_trial_adoption",
            "navigator_program_coverage",
            "financial_assistance_coverage",
            "drug_holiday_fraction",
        ):
            _validate01(name, float(getattr(self, name)))

        if self.ultrasound_mechanical_index < 0:
            raise ValueError("ultrasound_mechanical_index must be non-negative")
        if self.eligible_patients <= 0:
            raise ValueError("eligible_patients must be > 0")
        if self.participation_rate <= 0:
            raise ValueError("participation_rate must be > 0")
        if self.annual_drug_cost_usd <= 0:
            raise ValueError("annual_drug_cost_usd must be > 0")
        if self.median_annual_income_usd <= 0:
            raise ValueError("median_annual_income_usd must be > 0")
        if self.proposed_oop_cap_usd < 0:
            raise ValueError("proposed_oop_cap_usd must be >= 0")
        if self.initial_tumor_size <= 0:
            raise ValueError("initial_tumor_size must be > 0")
        if self.mutation_rate <= 0:
            raise ValueError("mutation_rate must be > 0")
        if self.n_drugs_in_combination < 1:
            raise ValueError("n_drugs_in_combination must be >= 1")
        if self.adaptive_therapy_cycles < 0:
            raise ValueError("adaptive_therapy_cycles must be >= 0")

        if not self.modality_probabilities:
            raise ValueError("modality_probabilities must be non-empty")
        if set(self.modality_probabilities) != set(self.modality_weights):
            raise ValueError("modality_weights keys must match modality_probabilities")
        for k, v in self.modality_probabilities.items():
            _validate01(f"modality_probabilities[{k}]", float(v))
        for k, v in self.modality_weights.items():
            if float(v) < 0:
                raise ValueError(f"modality_weights[{k}] must be non-negative")
        if sum(float(v) for v in self.modality_weights.values()) <= 0:
            raise ValueError("sum(modality_weights) must be > 0")


def _validate01(name: str, value: float) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def separation_guard() -> dict[str, Any]:
    """Return explicit non-hardgate and no-clinical-claim boundary metadata."""
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": TRANSLATIONAL_ONCOLOGY_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "clinical_claims_allowed": False,
        "patient_specific_recommendation_allowed": False,
        "message": (
            "Pillar 248 is a non-hardgate translational research synthesis layer. "
            "Outputs are hypothesis and planning artifacts only, never clinical "
            "care directives."
        ),
    }


def control_profile(s: TranslationalOncologyScenario) -> dict[str, float]:
    return {
        "heterogeneity_gap": s.heterogeneity_gap,
        "resistance_gap": s.resistance_gap,
        "immune_escape_gap": s.immune_escape_gap,
        "early_detection_gap": s.early_detection_gap,
        "targetability_gap": s.targetability_gap,
        "access_gap": s.access_gap,
    }


def diagnostic_signal_stack(s: TranslationalOncologyScenario) -> dict[str, Any]:
    bayes = bayes_ppv_npv(s.prevalence, s.sensitivity, s.specificity)
    fused = fused_diagnostic_probability(
        probabilities=dict(s.modality_probabilities),
        weights=dict(s.modality_weights),
    )
    triage = diagnostic_triage(
        fused_probability=float(fused["fused_probability"]),
        npv=float(bayes["npv"]),
        critical_symptom_score=s.critical_symptom_score,
    )
    alignment = cross_pillar_alignment_score(
        ultrasound_mechanical_index=s.ultrasound_mechanical_index,
        nanosensor_snr_db=s.nanosensor_snr_db,
        fused_probability=float(fused["fused_probability"]),
    )

    confidence = _clamp01(
        0.40 * float(bayes["ppv"])
        + 0.30 * float(bayes["npv"])
        + 0.20 * (1.0 - float(fused["disagreement_index"]))
        + 0.10 * float(fused["fused_probability"])
    )
    return {
        "bayes": bayes,
        "fusion": fused,
        "triage": triage,
        "alignment": alignment,
        "diagnostic_signal_score": confidence,
        "status": "CALCULATED (cross-pillar diagnostic synthesis)",
    }


def bottleneck_synthesis_stack(s: TranslationalOncologyScenario) -> dict[str, Any]:
    enrollment = enrollment_deficit(
        eligible_patients=s.eligible_patients,
        participation_rate=s.participation_rate,
    )
    access = access_barrier_fraction(
        annual_drug_cost_usd=s.annual_drug_cost_usd,
        median_annual_income_usd=s.median_annual_income_usd,
        insurance_coverage_fraction=s.insurance_coverage_fraction,
    )
    paradox = preclinical_paradox_score(animal_efficacy=s.preclinical_animal_efficacy)
    liquid_biopsy = liquid_biopsy_ppv_npv(
        sensitivity=s.sensitivity,
        specificity=s.specificity,
        prevalence=max(1e-6, s.prevalence),
    )

    execution_readiness = _clamp01(
        1.0
        - (
            0.45 * float(enrollment["deficit_fraction"])
            + 0.35 * float(access["access_barrier_score"])
            + 0.20 * (1.0 - float(paradox["expected_human_efficacy"]))
        )
    )

    return {
        "enrollment": enrollment,
        "access": access,
        "preclinical_paradox": paradox,
        "liquid_biopsy": liquid_biopsy,
        "execution_readiness_score": execution_readiness,
        "status": "CALCULATED + EMPIRICAL synthesis (execution bottleneck surface)",
    }


def intervention_planning_stack(s: TranslationalOncologyScenario) -> dict[str, Any]:
    enrollment_plan = enrollment_intervention_model(
        current_participation_rate=s.participation_rate,
        decentralized_trial_adoption=s.decentralized_trial_adoption,
        navigator_program_coverage=s.navigator_program_coverage,
        financial_assistance_coverage=s.financial_assistance_coverage,
    )
    detection_plan = detection_improvement_pathway(
        current_sensitivity=s.sensitivity,
        current_specificity=s.specificity,
        prevalence=s.prevalence,
        target_ppv=0.80,
    )
    finance_plan = financial_access_intervention(
        drug_annual_cost_usd=s.annual_drug_cost_usd,
        insurance_coverage_fraction=s.insurance_coverage_fraction,
        income_usd=s.median_annual_income_usd,
        proposed_oop_cap_usd=s.proposed_oop_cap_usd,
    )
    resistance_plan = resistance_prevention_model(
        initial_tumor_size=s.initial_tumor_size,
        mutation_rate=s.mutation_rate,
        n_drugs_in_combination=s.n_drugs_in_combination,
        adaptive_therapy_cycles=s.adaptive_therapy_cycles,
        drug_holiday_fraction=s.drug_holiday_fraction,
    )

    feasibility = _clamp01(
        0.35 * float(enrollment_plan["enrollment_gap_closed"])
        + 0.20 * (1.0 - float(detection_plan["required_specificity_for_target_ppv"]))
        + 0.20 * (1.0 - float(finance_plan["toxicity_score_after"]))
        + 0.25 * (1.0 - float(resistance_plan["final_resistance_probability"]))
    )

    prioritization = [
        {
            "name": "enrollment_acceleration",
            "impact_score": float(enrollment_plan["enrollment_gap_closed"]),
            "primary_metric": "enrollment_gap_closed",
        },
        {
            "name": "detection_calibration",
            "impact_score": _clamp01(1.0 - float(detection_plan["current_ppv"])),
            "primary_metric": "ppv_gap",
        },
        {
            "name": "financial_toxicity_reduction",
            "impact_score": _clamp01(float(finance_plan["toxicity_score_before"]) - float(finance_plan["toxicity_score_after"])),
            "primary_metric": "toxicity_score_delta",
        },
        {
            "name": "resistance_prevention",
            "impact_score": _clamp01(float(resistance_plan["base_resistance_probability"]) - float(resistance_plan["final_resistance_probability"])),
            "primary_metric": "resistance_probability_delta",
        },
    ]
    prioritization.sort(key=lambda x: x["impact_score"], reverse=True)

    return {
        "intervention_order": INTERVENTION_ORDER,
        "enrollment_plan": enrollment_plan,
        "detection_plan": detection_plan,
        "financial_plan": finance_plan,
        "resistance_plan": resistance_plan,
        "prioritization": prioritization,
        "intervention_feasibility_score": feasibility,
        "status": "CALCULATED + EMPIRICAL planning stack (non-clinical)",
    }


def translational_oncology_synthesis_score(s: TranslationalOncologyScenario) -> dict[str, Any]:
    diagnostic = diagnostic_signal_stack(s)
    bottleneck = bottleneck_synthesis_stack(s)
    planning = intervention_planning_stack(s)

    control = precision_weighted_control_probability(
        profile=control_profile(s),
        precision_bits=256,
        use_jax=True,
    )
    direction = missing_key_direction("translational_portfolio", control_profile(s))

    score = _clamp01(
        float(SCORE_WEIGHTS["diagnostic_signal"]) * float(diagnostic["diagnostic_signal_score"])
        + float(SCORE_WEIGHTS["execution_readiness"]) * float(bottleneck["execution_readiness_score"])
        + float(SCORE_WEIGHTS["control_tractability"]) * float(control["control_probability"])
        + float(SCORE_WEIGHTS["intervention_feasibility"]) * float(planning["intervention_feasibility_score"])
        + float(SCORE_WEIGHTS["cross_pillar_alignment"]) * float(diagnostic["alignment"]["alignment_score"])
    )

    if score >= 0.70:
        band = "high-synthesis-readiness"
    elif score >= 0.45:
        band = "intermediate-synthesis-readiness"
    else:
        band = "low-synthesis-readiness"

    return {
        "diagnostic": diagnostic,
        "bottleneck": bottleneck,
        "planning": planning,
        "control": control,
        "direction": direction,
        "score_weights": dict(SCORE_WEIGHTS),
        "translational_synthesis_score": score,
        "readiness_band": band,
        "status": "CALCULATED synthesis score (adjacent research routing only)",
    }


def uncertainty_bands(
    s: TranslationalOncologyScenario,
    n_trials: int = 248,
    seed: int = 248,
) -> dict[str, Any]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")

    rng = random.Random(seed)
    vals: list[float] = []

    for _ in range(n_trials):
        p = TranslationalOncologyScenario(
            prevalence=_clamp01(s.prevalence + rng.uniform(-0.015, 0.015)),
            sensitivity=_clamp01(s.sensitivity + rng.uniform(-0.04, 0.04)),
            specificity=_clamp01(s.specificity + rng.uniform(-0.01, 0.01)),
            modality_probabilities={
                k: _clamp01(float(v) + rng.uniform(-0.05, 0.05))
                for k, v in s.modality_probabilities.items()
            },
            modality_weights=dict(s.modality_weights),
            critical_symptom_score=_clamp01(s.critical_symptom_score + rng.uniform(-0.05, 0.05)),
            ultrasound_mechanical_index=max(0.0, s.ultrasound_mechanical_index * (1 + rng.uniform(-0.08, 0.08))),
            nanosensor_snr_db=s.nanosensor_snr_db + rng.uniform(-2.5, 2.5),
            eligible_patients=max(1.0, s.eligible_patients * (1 + rng.uniform(-0.08, 0.08))),
            participation_rate=_clamp01(s.participation_rate + rng.uniform(-0.01, 0.01)),
            annual_drug_cost_usd=max(1.0, s.annual_drug_cost_usd * (1 + rng.uniform(-0.12, 0.12))),
            median_annual_income_usd=max(1.0, s.median_annual_income_usd * (1 + rng.uniform(-0.08, 0.08))),
            insurance_coverage_fraction=_clamp01(s.insurance_coverage_fraction + rng.uniform(-0.03, 0.03)),
            proposed_oop_cap_usd=max(0.0, s.proposed_oop_cap_usd * (1 + rng.uniform(-0.12, 0.12))),
            preclinical_animal_efficacy=_clamp01(s.preclinical_animal_efficacy + rng.uniform(-0.06, 0.06)),
            heterogeneity_gap=_clamp01(s.heterogeneity_gap + rng.uniform(-0.05, 0.05)),
            resistance_gap=_clamp01(s.resistance_gap + rng.uniform(-0.05, 0.05)),
            immune_escape_gap=_clamp01(s.immune_escape_gap + rng.uniform(-0.05, 0.05)),
            early_detection_gap=_clamp01(s.early_detection_gap + rng.uniform(-0.05, 0.05)),
            targetability_gap=_clamp01(s.targetability_gap + rng.uniform(-0.05, 0.05)),
            access_gap=_clamp01(s.access_gap + rng.uniform(-0.05, 0.05)),
            decentralized_trial_adoption=_clamp01(s.decentralized_trial_adoption + rng.uniform(-0.04, 0.04)),
            navigator_program_coverage=_clamp01(s.navigator_program_coverage + rng.uniform(-0.04, 0.04)),
            financial_assistance_coverage=_clamp01(s.financial_assistance_coverage + rng.uniform(-0.04, 0.04)),
            initial_tumor_size=max(1, int(s.initial_tumor_size * (1 + rng.uniform(-0.12, 0.12)))),
            mutation_rate=max(1e-12, s.mutation_rate * (1 + rng.uniform(-0.15, 0.15))),
            n_drugs_in_combination=s.n_drugs_in_combination,
            adaptive_therapy_cycles=max(0, int(round(s.adaptive_therapy_cycles + rng.uniform(-1.0, 1.0)))),
            drug_holiday_fraction=_clamp01(s.drug_holiday_fraction + rng.uniform(-0.04, 0.04)),
        )
        vals.append(float(translational_oncology_synthesis_score(p)["translational_synthesis_score"]))

    vals.sort()
    p10 = vals[max(0, int(0.10 * len(vals)) - 1)]
    p50 = vals[len(vals) // 2]
    p90 = vals[min(len(vals) - 1, int(0.90 * len(vals)))]

    spread = p90 - p10
    if spread <= 0.10:
        confidence = "tight"
    elif spread <= 0.20:
        confidence = "moderate"
    else:
        confidence = "wide"

    return {
        "mean_score": sum(vals) / len(vals),
        "p10_score": p10,
        "p50_score": p50,
        "p90_score": p90,
        "uncertainty_spread": spread,
        "uncertainty_band": confidence,
        "n_trials": n_trials,
        "seed": seed,
    }


def baseline_translational_oncology_scenario() -> TranslationalOncologyScenario:
    return TranslationalOncologyScenario(
        prevalence=0.035,
        sensitivity=0.86,
        specificity=0.93,
        modality_probabilities={"ultrasound": 0.56, "mri": 0.74, "liquid_biopsy": 0.61},
        modality_weights={"ultrasound": 0.9, "mri": 1.2, "liquid_biopsy": 1.0},
        critical_symptom_score=0.42,
        ultrasound_mechanical_index=0.8,
        nanosensor_snr_db=31.0,
        eligible_patients=1_900_000,
        participation_rate=0.045,
        annual_drug_cost_usd=180_000,
        median_annual_income_usd=82_000,
        insurance_coverage_fraction=0.82,
        proposed_oop_cap_usd=9_500,
        preclinical_animal_efficacy=0.78,
        heterogeneity_gap=0.58,
        resistance_gap=0.54,
        immune_escape_gap=0.49,
        early_detection_gap=0.43,
        targetability_gap=0.41,
        access_gap=0.46,
        decentralized_trial_adoption=0.55,
        navigator_program_coverage=0.42,
        financial_assistance_coverage=0.36,
        initial_tumor_size=900_000_000,
        mutation_rate=2.2e-7,
        n_drugs_in_combination=3,
        adaptive_therapy_cycles=5,
        drug_holiday_fraction=0.22,
    )


def pillar248_translational_oncology_report(
    scenario: TranslationalOncologyScenario | None = None,
    n_trials: int = 248,
    seed: int = 248,
) -> dict[str, Any]:
    """Integrated Pillar 248 adjacent-track report (non-clinical research routing)."""
    s = baseline_translational_oncology_scenario() if scenario is None else scenario
    synthesis = translational_oncology_synthesis_score(s)
    uncertainty = uncertainty_bands(s, n_trials=n_trials, seed=seed)
    return {
        "pillar": 248,
        "status": __provenance__["status"],
        "separation_guard": separation_guard(),
        "scenario": s,
        "synthesis": synthesis,
        "uncertainty": uncertainty,
        "falsification_condition": (
            "FALSIFIED as an adjacent translational synthesis layer if its "
            "composite score fails to correlate with independent, out-of-sample "
            "program-level improvement trends under pre-registered evaluation."
        ),
        "epistemic_boundary": (
            "No clinical efficacy claim is made. No treatment recommendation is "
            "produced. Outputs are exploratory planning artifacts only."
        ),
    }


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "ADJACENCY_TRACK_LABEL",
    "TRANSLATIONAL_ONCOLOGY_TRACK_LABEL",
    "INTERVENTION_ORDER",
    "SCORE_WEIGHTS",
    "TranslationalOncologyScenario",
    "__provenance__",
    "separation_guard",
    "control_profile",
    "diagnostic_signal_stack",
    "bottleneck_synthesis_stack",
    "intervention_planning_stack",
    "translational_oncology_synthesis_score",
    "uncertainty_bands",
    "baseline_translational_oncology_scenario",
    "pillar248_translational_oncology_report",
]
