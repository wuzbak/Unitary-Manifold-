# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 227 — AI & Robotics Bottleneck Engine (2026).

Adjacent applied research track (non-hardgate): a deterministic calculator for
three strategic hurdles and twelve technical/operational bottlenecks that block
production-grade AI robotics deployment.

This module is designed to compute explicit gap scores from measurable inputs
(instead of narrative-only assessments), then aggregate those scores into a
reproducible deployment-readiness index and Monte Carlo scenario summary.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import random
from typing import Dict, Mapping, Tuple

__provenance__ = {
    "pillar": 227,
    "title": "AI & Robotics Bottleneck Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — operational readiness calculator, not a claim that deployment bottlenecks are solved",
}

# Framework constants
N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

STRATEGIC_HURDLES: Tuple[str, ...] = (
    "safety_liability_framework_gap",
    "infrastructure_grid_readiness_gap",
    "human_trust_perception_erosion",
)

BOTTLENECK_ORDER: Tuple[str, ...] = (
    "training_data_scarcity",
    "battery_endurance",
    "end_effector_dexterity",
    "compute_to_power_conflict",
    "memory_bandwidth_latency",
    "supply_chain_fragmentation",
    "weak_generalization",
    "cybersecurity_exposure",
    "process_instability",
    "global_talent_gap",
    "cost_of_prototyping",
    "software_to_hardware_gap",
)


@dataclass(frozen=True)
class DeploymentScenario:
    """Measured/assumed inputs for one deployment scenario."""

    # Strategic hurdle inputs
    safety_standard_coverage: float
    liability_clarity: float
    humanoid_mass_lbs: float

    grid_power_available_gw: float
    grid_power_required_gw: float
    utility_interconnection_years: float

    public_trust_percent: float
    bias_incidents_per_100_deployments: float
    uncanny_discomfort_percent: float

    # Bottleneck inputs
    real_world_training_hours: float
    target_training_hours: float

    battery_runtime_hours: float
    required_runtime_hours: float

    dexterity_success_rate: float
    required_dexterity_success_rate: float

    compute_watts: float
    motion_watts: float
    minimum_compute_share: float

    memory_bandwidth_tbps: float
    required_memory_bandwidth_tbps: float

    standardized_component_fraction: float

    novel_task_success_rate: float
    required_novel_task_success_rate: float

    critical_security_findings_per_quarter: float
    tolerable_security_findings_per_quarter: float

    documented_process_fraction: float

    cross_domain_engineers: float
    required_cross_domain_engineers: float

    prototype_unit_cost_usd: float
    target_unit_cost_usd: float

    software_hardware_lag_years: float
    target_software_hardware_lag_years: float


def _validate_fraction(name: str, value: float) -> None:
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {value}")


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be non-negative, got {value}")


def _clamp01(value: float) -> float:
    if value < 0.0:
        return 0.0
    if value > 1.0:
        return 1.0
    return value


def ratio_deficit(actual: float, target: float) -> float:
    """Return normalized shortfall max(0, 1 - actual/target)."""
    _validate_non_negative("actual", actual)
    if target <= 0:
        raise ValueError("target must be > 0")
    return _clamp01(1.0 - (actual / target))


def ratio_excess(actual: float, target: float) -> float:
    """Return normalized overshoot max(0, actual/target - 1)."""
    _validate_non_negative("actual", actual)
    if target <= 0:
        raise ValueError("target must be > 0")
    return _clamp01((actual / target) - 1.0)


def safety_liability_framework_gap(
    safety_standard_coverage: float,
    liability_clarity: float,
    humanoid_mass_lbs: float,
) -> float:
    """Gap score for fenceless-operation safety/liability readiness."""
    _validate_fraction("safety_standard_coverage", safety_standard_coverage)
    _validate_fraction("liability_clarity", liability_clarity)
    if humanoid_mass_lbs <= 0:
        raise ValueError("humanoid_mass_lbs must be > 0")

    # 150–200 lbs is the risk band highlighted in the problem statement.
    mass_factor = _clamp01((humanoid_mass_lbs - 150.0) / 50.0)

    return _clamp01(
        0.45 * (1.0 - safety_standard_coverage)
        + 0.45 * (1.0 - liability_clarity)
        + 0.10 * mass_factor
    )


def infrastructure_grid_readiness_gap(
    power_available_gw: float,
    power_required_gw: float,
    utility_interconnection_years: float,
    max_tolerable_interconnection_years: float = 2.0,
) -> float:
    """Gap score for AI/robotics energy infrastructure readiness."""
    _validate_non_negative("power_available_gw", power_available_gw)
    _validate_non_negative("power_required_gw", power_required_gw)
    _validate_non_negative("utility_interconnection_years", utility_interconnection_years)
    if power_required_gw <= 0:
        raise ValueError("power_required_gw must be > 0")
    if max_tolerable_interconnection_years <= 0:
        raise ValueError("max_tolerable_interconnection_years must be > 0")

    supply_gap = ratio_deficit(power_available_gw, power_required_gw)
    delay_gap = ratio_excess(utility_interconnection_years, max_tolerable_interconnection_years)
    return _clamp01(0.70 * supply_gap + 0.30 * delay_gap)


def human_trust_perception_erosion(
    public_trust_percent: float,
    bias_incidents_per_100_deployments: float,
    uncanny_discomfort_percent: float,
    target_trust_percent: float = 65.0,
    tolerable_bias_incidents_per_100: float = 5.0,
) -> float:
    """Gap score for social trust and acceptance barrier."""
    if not (0.0 <= public_trust_percent <= 100.0):
        raise ValueError("public_trust_percent must be in [0, 100]")
    _validate_non_negative("bias_incidents_per_100_deployments", bias_incidents_per_100_deployments)
    if not (0.0 <= uncanny_discomfort_percent <= 100.0):
        raise ValueError("uncanny_discomfort_percent must be in [0, 100]")
    if target_trust_percent <= 0:
        raise ValueError("target_trust_percent must be > 0")
    if tolerable_bias_incidents_per_100 <= 0:
        raise ValueError("tolerable_bias_incidents_per_100 must be > 0")

    trust_gap = ratio_deficit(public_trust_percent, target_trust_percent)
    bias_gap = ratio_excess(
        bias_incidents_per_100_deployments,
        tolerable_bias_incidents_per_100,
    )
    uncanny_gap = uncanny_discomfort_percent / 100.0

    return _clamp01(0.60 * trust_gap + 0.25 * bias_gap + 0.15 * uncanny_gap)


def bottleneck_scores(s: DeploymentScenario) -> Dict[str, float]:
    """Compute all 12 normalized bottleneck gap scores (0=no gap, 1=severe)."""
    _validate_fraction("minimum_compute_share", s.minimum_compute_share)
    _validate_fraction("standardized_component_fraction", s.standardized_component_fraction)
    _validate_fraction("documented_process_fraction", s.documented_process_fraction)
    _validate_fraction("dexterity_success_rate", s.dexterity_success_rate)
    _validate_fraction("required_dexterity_success_rate", s.required_dexterity_success_rate)
    _validate_fraction("novel_task_success_rate", s.novel_task_success_rate)
    _validate_fraction("required_novel_task_success_rate", s.required_novel_task_success_rate)

    total_power = s.compute_watts + s.motion_watts
    if total_power <= 0:
        raise ValueError("compute_watts + motion_watts must be > 0")

    compute_share = s.compute_watts / total_power

    return {
        "training_data_scarcity": ratio_deficit(
            s.real_world_training_hours,
            s.target_training_hours,
        ),
        "battery_endurance": ratio_deficit(
            s.battery_runtime_hours,
            s.required_runtime_hours,
        ),
        "end_effector_dexterity": ratio_deficit(
            s.dexterity_success_rate,
            s.required_dexterity_success_rate,
        ),
        "compute_to_power_conflict": ratio_deficit(
            compute_share,
            s.minimum_compute_share,
        ),
        "memory_bandwidth_latency": ratio_deficit(
            s.memory_bandwidth_tbps,
            s.required_memory_bandwidth_tbps,
        ),
        "supply_chain_fragmentation": 1.0 - s.standardized_component_fraction,
        "weak_generalization": ratio_deficit(
            s.novel_task_success_rate,
            s.required_novel_task_success_rate,
        ),
        "cybersecurity_exposure": ratio_excess(
            s.critical_security_findings_per_quarter,
            s.tolerable_security_findings_per_quarter,
        ),
        "process_instability": 1.0 - s.documented_process_fraction,
        "global_talent_gap": ratio_deficit(
            s.cross_domain_engineers,
            s.required_cross_domain_engineers,
        ),
        "cost_of_prototyping": ratio_excess(
            s.prototype_unit_cost_usd,
            s.target_unit_cost_usd,
        ),
        "software_to_hardware_gap": ratio_excess(
            s.software_hardware_lag_years,
            s.target_software_hardware_lag_years,
        ),
    }


def strategic_hurdle_scores(s: DeploymentScenario) -> Dict[str, float]:
    """Compute normalized scores for the 3 major strategic hurdles."""
    return {
        "safety_liability_framework_gap": safety_liability_framework_gap(
            s.safety_standard_coverage,
            s.liability_clarity,
            s.humanoid_mass_lbs,
        ),
        "infrastructure_grid_readiness_gap": infrastructure_grid_readiness_gap(
            s.grid_power_available_gw,
            s.grid_power_required_gw,
            s.utility_interconnection_years,
        ),
        "human_trust_perception_erosion": human_trust_perception_erosion(
            s.public_trust_percent,
            s.bias_incidents_per_100_deployments,
            s.uncanny_discomfort_percent,
        ),
    }


def deployment_readiness_report(
    s: DeploymentScenario,
    strategic_weight: float = 0.50,
) -> Dict[str, object]:
    """Aggregate 3+12 gaps into an overall readiness score in [0, 1]."""
    _validate_fraction("strategic_weight", strategic_weight)

    hurdles = strategic_hurdle_scores(s)
    bottlenecks = bottleneck_scores(s)

    hurdle_mean = sum(hurdles.values()) / len(hurdles)
    bottleneck_mean = sum(bottlenecks.values()) / len(bottlenecks)

    total_gap = strategic_weight * hurdle_mean + (1.0 - strategic_weight) * bottleneck_mean
    readiness = 1.0 - total_gap

    ranked = sorted(bottlenecks.items(), key=lambda kv: kv[1], reverse=True)

    return {
        "hurdle_scores": hurdles,
        "bottleneck_scores": bottlenecks,
        "strategic_gap_mean": hurdle_mean,
        "bottleneck_gap_mean": bottleneck_mean,
        "total_gap": total_gap,
        "readiness_index": readiness,
        "top_bottlenecks": ranked[:5],
    }


@dataclass(frozen=True)
class UniformRange:
    low: float
    high: float

    def sample(self, rng: random.Random) -> float:
        if self.high < self.low:
            raise ValueError("UniformRange requires high >= low")
        return rng.uniform(self.low, self.high)


def _percentile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        raise ValueError("sorted_values must be non-empty")
    if not (0.0 <= q <= 1.0):
        raise ValueError("q must be in [0, 1]")
    if len(sorted_values) == 1:
        return sorted_values[0]
    pos = q * (len(sorted_values) - 1)
    lo = int(pos)
    hi = min(lo + 1, len(sorted_values) - 1)
    w = pos - lo
    return (1.0 - w) * sorted_values[lo] + w * sorted_values[hi]


def monte_carlo_readiness(
    base_scenario: DeploymentScenario,
    uncertainty: Mapping[str, UniformRange],
    n_samples: int = 5000,
    seed: int = 227,
    strategic_weight: float = 0.50,
) -> Dict[str, float]:
    """Run Monte Carlo readiness simulation around a base scenario."""
    if n_samples <= 0:
        raise ValueError("n_samples must be > 0")

    rng = random.Random(seed)
    readiness_values: list[float] = []

    for _ in range(n_samples):
        updates = {field: interval.sample(rng) for field, interval in uncertainty.items()}
        scenario = replace(base_scenario, **updates)
        readiness_values.append(
            deployment_readiness_report(scenario, strategic_weight=strategic_weight)["readiness_index"]
        )

    readiness_values.sort()
    mean_readiness = sum(readiness_values) / len(readiness_values)

    return {
        "samples": float(n_samples),
        "mean_readiness": mean_readiness,
        "p10": _percentile(readiness_values, 0.10),
        "p50": _percentile(readiness_values, 0.50),
        "p90": _percentile(readiness_values, 0.90),
        "min": readiness_values[0],
        "max": readiness_values[-1],
    }


def baseline_2026_scenario() -> DeploymentScenario:
    """Return a transparent baseline scenario for 2026 deployment stress-testing.

    Values directly use the problem-statement ranges where provided (e.g. 150–200
    lbs, 90–120 minutes vs 8–20 hours, 3–5 year lag). Fields not numerically
    specified in the statement are explicit assumptions to enable calculation.
    """
    return DeploymentScenario(
        safety_standard_coverage=0.35,
        liability_clarity=0.25,
        humanoid_mass_lbs=175.0,
        grid_power_available_gw=1.2,
        grid_power_required_gw=3.0,
        utility_interconnection_years=5.0,
        public_trust_percent=46.0,
        bias_incidents_per_100_deployments=12.0,
        uncanny_discomfort_percent=58.0,
        real_world_training_hours=18000.0,
        target_training_hours=100000.0,
        battery_runtime_hours=1.75,
        required_runtime_hours=12.0,
        dexterity_success_rate=0.72,
        required_dexterity_success_rate=0.95,
        compute_watts=850.0,
        motion_watts=1500.0,
        minimum_compute_share=0.45,
        memory_bandwidth_tbps=2.0,
        required_memory_bandwidth_tbps=4.5,
        standardized_component_fraction=0.30,
        novel_task_success_rate=0.55,
        required_novel_task_success_rate=0.90,
        critical_security_findings_per_quarter=9.0,
        tolerable_security_findings_per_quarter=2.0,
        documented_process_fraction=0.50,
        cross_domain_engineers=18.0,
        required_cross_domain_engineers=45.0,
        prototype_unit_cost_usd=220000.0,
        target_unit_cost_usd=50000.0,
        software_hardware_lag_years=4.0,
        target_software_hardware_lag_years=1.5,
    )


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "STRATEGIC_HURDLES",
    "BOTTLENECK_ORDER",
    "DeploymentScenario",
    "UniformRange",
    "ratio_deficit",
    "ratio_excess",
    "safety_liability_framework_gap",
    "infrastructure_grid_readiness_gap",
    "human_trust_perception_erosion",
    "bottleneck_scores",
    "strategic_hurdle_scores",
    "deployment_readiness_report",
    "monte_carlo_readiness",
    "baseline_2026_scenario",
]
