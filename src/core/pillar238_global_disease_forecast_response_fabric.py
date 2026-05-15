# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 238 — Global Health Systems Surge Readiness & Response Calculator.

Adjacent applied research track (non-hardgate): deterministic calculator
for public-health-system capacity gaps, transmission-rate estimation, and
coordinated response-adequacy routing.  All inputs are infrastructure and
logistics metrics; no claim of clinical advice or operational deployment.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Any

__provenance__ = {
    "pillar": 238,
    "title": "Global Health Systems Surge Readiness & Response Calculator",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — deterministic health-system surge readiness routing",
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

BOTTLENECK_ORDER: tuple[str, ...] = (
    "surveillance_latency_gap",
    "testing_capacity_gap",
    "hospital_capacity_gap",
    "therapeutic_access_gap",
    "vaccine_coverage_gap",
    "supply_logistics_gap",
    "workforce_protection_gap",
    "misinformation_gap",
    "cross_border_coordination_gap",
    "trial_activation_gap",
    "genomic_monitoring_gap",
    "equity_gap",
)


@dataclass(frozen=True)
class HealthSystemScenario:
    base_reproduction_number: float
    contact_reduction_fraction: float
    immunity_fraction: float

    surveillance_detection_delay_days: float
    target_detection_delay_days: float

    daily_tests_available: float
    daily_tests_required: float

    available_bed_capacity: float
    required_bed_capacity: float

    therapeutic_courses_available: float
    therapeutic_courses_required: float

    vaccine_coverage_fraction: float
    target_vaccine_coverage_fraction: float

    logistics_fill_rate: float

    ppe_coverage_fraction: float

    trusted_information_fraction: float

    cross_border_data_sharing_fraction: float

    trial_activation_days: float
    target_trial_activation_days: float

    sequenced_cases_fraction: float
    target_sequenced_cases_fraction: float

    vulnerable_population_coverage_fraction: float


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _ratio_deficit(actual: float, target: float) -> float:
    if actual < 0 or target <= 0:
        raise ValueError("invalid ratio inputs")
    return _clamp01(1.0 - actual / target)


def _ratio_excess(actual: float, target: float) -> float:
    if actual < 0 or target <= 0:
        raise ValueError("invalid ratio inputs")
    return _clamp01(actual / target - 1.0)


def effective_reproduction_number(s: HealthSystemScenario) -> float:
    if s.base_reproduction_number <= 0:
        raise ValueError("base_reproduction_number must be > 0")
    for name, val in (
        ("contact_reduction_fraction", s.contact_reduction_fraction),
        ("immunity_fraction", s.immunity_fraction),
    ):
        if not (0 <= val <= 1):
            raise ValueError(f"{name} must be in [0,1]")
    return s.base_reproduction_number * (1.0 - s.contact_reduction_fraction) * (1.0 - s.immunity_fraction)


def surge_risk_probability(s: HealthSystemScenario) -> float:
    rt = effective_reproduction_number(s)
    sigmoid = 1.0 / (1.0 + math.exp(-4.0 * (rt - 1.0)))
    return _clamp01(sigmoid)


def bottleneck_scores(s: HealthSystemScenario) -> dict[str, float]:
    for name, val in (
        ("vaccine_coverage_fraction", s.vaccine_coverage_fraction),
        ("logistics_fill_rate", s.logistics_fill_rate),
        ("ppe_coverage_fraction", s.ppe_coverage_fraction),
        ("trusted_information_fraction", s.trusted_information_fraction),
        ("cross_border_data_sharing_fraction", s.cross_border_data_sharing_fraction),
        ("sequenced_cases_fraction", s.sequenced_cases_fraction),
        ("vulnerable_population_coverage_fraction", s.vulnerable_population_coverage_fraction),
    ):
        if not (0 <= val <= 1):
            raise ValueError(f"{name} must be in [0,1]")

    return {
        "surveillance_latency_gap": _ratio_excess(s.surveillance_detection_delay_days, s.target_detection_delay_days),
        "testing_capacity_gap": _ratio_deficit(s.daily_tests_available, s.daily_tests_required),
        "hospital_capacity_gap": _ratio_deficit(s.available_bed_capacity, s.required_bed_capacity),
        "therapeutic_access_gap": _ratio_deficit(s.therapeutic_courses_available, s.therapeutic_courses_required),
        "vaccine_coverage_gap": _ratio_deficit(s.vaccine_coverage_fraction, s.target_vaccine_coverage_fraction),
        "supply_logistics_gap": 1.0 - s.logistics_fill_rate,
        "workforce_protection_gap": 1.0 - s.ppe_coverage_fraction,
        "misinformation_gap": 1.0 - s.trusted_information_fraction,
        "cross_border_coordination_gap": 1.0 - s.cross_border_data_sharing_fraction,
        "trial_activation_gap": _ratio_excess(s.trial_activation_days, s.target_trial_activation_days),
        "genomic_monitoring_gap": _ratio_deficit(s.sequenced_cases_fraction, s.target_sequenced_cases_fraction),
        "equity_gap": 1.0 - s.vulnerable_population_coverage_fraction,
    }


def response_adequacy_index(s: HealthSystemScenario) -> float:
    risk = surge_risk_probability(s)
    gaps = bottleneck_scores(s)
    system_penalty = sum(gaps.values()) / len(gaps)
    return _clamp01(1.0 - 0.55 * risk - 0.45 * system_penalty)


def response_report(s: HealthSystemScenario) -> dict[str, Any]:
    rt = effective_reproduction_number(s)
    risk = surge_risk_probability(s)
    gaps = bottleneck_scores(s)
    feasible = response_adequacy_index(s)
    top = sorted(gaps.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "R_effective": rt,
        "outbreak_risk_probability": risk,
        "containment_feasibility_index": feasible,
        "top_bottlenecks": [{"name": n, "gap": g} for n, g in top],
        "all_bottlenecks": gaps,
        "status": "CALCULATED health-system surge response-adequacy route map",
    }


def monte_carlo_response_adequacy(s: HealthSystemScenario, n_trials: int = 200, seed: int = 238) -> dict[str, float]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(n_trials):
        p = HealthSystemScenario(
            base_reproduction_number=max(0.1, s.base_reproduction_number * (1 + rng.uniform(-0.08, 0.08))),
            contact_reduction_fraction=_clamp01(s.contact_reduction_fraction + rng.uniform(-0.05, 0.05)),
            immunity_fraction=_clamp01(s.immunity_fraction + rng.uniform(-0.05, 0.05)),
            surveillance_detection_delay_days=max(0.1, s.surveillance_detection_delay_days * (1 + rng.uniform(-0.1, 0.1))),
            target_detection_delay_days=s.target_detection_delay_days,
            daily_tests_available=max(0.0, s.daily_tests_available * (1 + rng.uniform(-0.1, 0.1))),
            daily_tests_required=s.daily_tests_required,
            available_bed_capacity=max(0.0, s.available_bed_capacity * (1 + rng.uniform(-0.1, 0.1))),
            required_bed_capacity=s.required_bed_capacity,
            therapeutic_courses_available=max(0.0, s.therapeutic_courses_available * (1 + rng.uniform(-0.1, 0.1))),
            therapeutic_courses_required=s.therapeutic_courses_required,
            vaccine_coverage_fraction=_clamp01(s.vaccine_coverage_fraction + rng.uniform(-0.05, 0.05)),
            target_vaccine_coverage_fraction=s.target_vaccine_coverage_fraction,
            logistics_fill_rate=_clamp01(s.logistics_fill_rate + rng.uniform(-0.05, 0.05)),
            ppe_coverage_fraction=_clamp01(s.ppe_coverage_fraction + rng.uniform(-0.05, 0.05)),
            trusted_information_fraction=_clamp01(s.trusted_information_fraction + rng.uniform(-0.05, 0.05)),
            cross_border_data_sharing_fraction=_clamp01(s.cross_border_data_sharing_fraction + rng.uniform(-0.05, 0.05)),
            trial_activation_days=max(0.1, s.trial_activation_days * (1 + rng.uniform(-0.1, 0.1))),
            target_trial_activation_days=s.target_trial_activation_days,
            sequenced_cases_fraction=_clamp01(s.sequenced_cases_fraction + rng.uniform(-0.05, 0.05)),
            target_sequenced_cases_fraction=s.target_sequenced_cases_fraction,
            vulnerable_population_coverage_fraction=_clamp01(s.vulnerable_population_coverage_fraction + rng.uniform(-0.05, 0.05)),
        )
        vals.append(response_adequacy_index(p))

    vals.sort()
    return {
        "mean_feasibility": sum(vals) / len(vals),
        "p10_feasibility": vals[max(0, int(0.1 * len(vals)) - 1)],
        "p50_feasibility": vals[len(vals) // 2],
        "p90_feasibility": vals[min(len(vals) - 1, int(0.9 * len(vals)))],
    }


def baseline_health_scenario() -> HealthSystemScenario:
    return HealthSystemScenario(
        base_reproduction_number=2.1,
        contact_reduction_fraction=0.28,
        immunity_fraction=0.42,
        surveillance_detection_delay_days=8.0,
        target_detection_delay_days=3.0,
        daily_tests_available=2_500_000,
        daily_tests_required=4_000_000,
        available_bed_capacity=180_000,
        required_bed_capacity=260_000,
        therapeutic_courses_available=3_200_000,
        therapeutic_courses_required=5_000_000,
        vaccine_coverage_fraction=0.64,
        target_vaccine_coverage_fraction=0.85,
        logistics_fill_rate=0.72,
        ppe_coverage_fraction=0.78,
        trusted_information_fraction=0.58,
        cross_border_data_sharing_fraction=0.51,
        trial_activation_days=45,
        target_trial_activation_days=14,
        sequenced_cases_fraction=0.11,
        target_sequenced_cases_fraction=0.25,
        vulnerable_population_coverage_fraction=0.57,
    )


def pillar238_health_surge_readiness_report(
    n_trials: int = 200,
    seed: int = 238,
) -> dict[str, Any]:
    """Integrated report for Pillar 238."""
    scenario = baseline_health_scenario()
    return {
        "pillar": 238,
        "status": __provenance__["status"],
        "bottleneck_order": BOTTLENECK_ORDER,
        "baseline_report": response_report(scenario),
        "stability_simulation": monte_carlo_response_adequacy(scenario, n_trials=n_trials, seed=seed),
        "falsification_condition": (
            "FALSIFIED as an adjacent response-routing engine if predicted "
            "response-adequacy directionality is repeatedly contradicted by "
            "out-of-sample surge outcomes under comparable intervention profiles."
        ),
    }


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "BOTTLENECK_ORDER",
    "HealthSystemScenario",
    "__provenance__",
    "effective_reproduction_number",
    "surge_risk_probability",
    "bottleneck_scores",
    "response_adequacy_index",
    "response_report",
    "monte_carlo_response_adequacy",
    "baseline_health_scenario",
    "pillar238_health_surge_readiness_report",
]
