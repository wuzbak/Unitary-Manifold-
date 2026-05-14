# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 237 — Civilizational Resilience Operating System (CROS).

Adjacent applied research track (non-hardgate): deterministic multi-sector
resilience scoring for integrated civilizational continuity planning.

This module computes sector bottlenecks independently, in parallel portfolio
mode, and in coordinated unison mode with intervention ranking.
"""
from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

__provenance__ = {
    "pillar": 237,
    "title": "Civilizational Resilience Operating System",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — deterministic resilience orchestration; "
        "not a claim of solved global continuity"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

STRATEGIC_HURDLES: tuple[str, ...] = (
    "coordination_fragmentation",
    "critical_infrastructure_fragility",
    "trust_governance_erosion",
)

BOTTLENECK_ORDER: tuple[str, ...] = (
    "grid_stability_gap",
    "hospital_surge_gap",
    "supply_chain_gap",
    "water_security_gap",
    "food_reserve_gap",
    "cyber_resilience_gap",
    "mobility_logistics_gap",
    "disaster_response_gap",
    "information_integrity_gap",
    "equity_access_gap",
    "workforce_readiness_gap",
    "fiscal_buffer_gap",
)


@dataclass(frozen=True)
class ResilienceScenario:
    # strategic
    interagency_coordination_score: float
    infrastructure_redundancy_score: float
    public_institution_trust_score: float

    # technical/operational
    grid_uptime_fraction: float
    target_grid_uptime_fraction: float

    available_hospital_surge_beds: float
    required_hospital_surge_beds: float

    days_of_critical_supply: float
    target_days_of_critical_supply: float

    secure_water_days: float
    target_secure_water_days: float

    strategic_food_days: float
    target_strategic_food_days: float

    cyber_mttd_hours: float
    target_cyber_mttd_hours: float

    logistics_coverage_fraction: float

    disaster_response_hours: float
    target_disaster_response_hours: float

    verified_information_fraction: float

    essential_service_equity_fraction: float

    trained_response_workforce: float
    required_response_workforce: float

    fiscal_reserve_months: float
    target_fiscal_reserve_months: float


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _validate_fraction(name: str, value: float) -> None:
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{name} must be in [0,1], got {value}")


def _ratio_deficit(actual: float, target: float) -> float:
    if target <= 0:
        raise ValueError("target must be > 0")
    if actual < 0:
        raise ValueError("actual must be non-negative")
    return _clamp01(1.0 - actual / target)


def _ratio_excess(actual: float, target: float) -> float:
    if target <= 0:
        raise ValueError("target must be > 0")
    if actual < 0:
        raise ValueError("actual must be non-negative")
    return _clamp01(actual / target - 1.0)


def strategic_hurdle_scores(s: ResilienceScenario) -> dict[str, float]:
    _validate_fraction("interagency_coordination_score", s.interagency_coordination_score)
    _validate_fraction("infrastructure_redundancy_score", s.infrastructure_redundancy_score)
    _validate_fraction("public_institution_trust_score", s.public_institution_trust_score)

    return {
        "coordination_fragmentation": 1.0 - s.interagency_coordination_score,
        "critical_infrastructure_fragility": 1.0 - s.infrastructure_redundancy_score,
        "trust_governance_erosion": 1.0 - s.public_institution_trust_score,
    }


def bottleneck_scores(s: ResilienceScenario) -> dict[str, float]:
    _validate_fraction("logistics_coverage_fraction", s.logistics_coverage_fraction)
    _validate_fraction("verified_information_fraction", s.verified_information_fraction)
    _validate_fraction("essential_service_equity_fraction", s.essential_service_equity_fraction)

    return {
        "grid_stability_gap": _ratio_deficit(s.grid_uptime_fraction, s.target_grid_uptime_fraction),
        "hospital_surge_gap": _ratio_deficit(s.available_hospital_surge_beds, s.required_hospital_surge_beds),
        "supply_chain_gap": _ratio_deficit(s.days_of_critical_supply, s.target_days_of_critical_supply),
        "water_security_gap": _ratio_deficit(s.secure_water_days, s.target_secure_water_days),
        "food_reserve_gap": _ratio_deficit(s.strategic_food_days, s.target_strategic_food_days),
        "cyber_resilience_gap": _ratio_excess(s.cyber_mttd_hours, s.target_cyber_mttd_hours),
        "mobility_logistics_gap": 1.0 - s.logistics_coverage_fraction,
        "disaster_response_gap": _ratio_excess(s.disaster_response_hours, s.target_disaster_response_hours),
        "information_integrity_gap": 1.0 - s.verified_information_fraction,
        "equity_access_gap": 1.0 - s.essential_service_equity_fraction,
        "workforce_readiness_gap": _ratio_deficit(s.trained_response_workforce, s.required_response_workforce),
        "fiscal_buffer_gap": _ratio_deficit(s.fiscal_reserve_months, s.target_fiscal_reserve_months),
    }


def resilience_readiness_index(s: ResilienceScenario, strategic_weight: float = 0.5) -> float:
    if not (0.0 <= strategic_weight <= 1.0):
        raise ValueError("strategic_weight must be in [0,1]")
    hurdles = strategic_hurdle_scores(s)
    bottlenecks = bottleneck_scores(s)
    h_mean = sum(hurdles.values()) / len(hurdles)
    b_mean = sum(bottlenecks.values()) / len(bottlenecks)
    total_gap = strategic_weight * h_mean + (1.0 - strategic_weight) * b_mean
    return _clamp01(1.0 - total_gap)


def resilience_report(s: ResilienceScenario, strategic_weight: float = 0.5) -> dict[str, Any]:
    hurdles = strategic_hurdle_scores(s)
    bottlenecks = bottleneck_scores(s)
    readiness = resilience_readiness_index(s, strategic_weight=strategic_weight)
    all_gaps = {**bottlenecks, **hurdles}
    top5 = sorted(all_gaps.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "readiness_index": readiness,
        "strategic_hurdles": hurdles,
        "bottlenecks": bottlenecks,
        "largest_gaps": [{"name": k, "gap": v} for k, v in top5],
        "status": "CALCULATED deterministic resilience report",
    }


def rank_interventions_by_roi(s: ResilienceScenario, budget_usd: float) -> list[dict[str, Any]]:
    if budget_usd < 0:
        raise ValueError("budget_usd must be non-negative")
    gaps = {**bottleneck_scores(s), **strategic_hurdle_scores(s)}
    cost_denominator = {
        name: (6_000_000 + 500_000 * idx) for idx, name in enumerate(gaps.keys())
    }
    per = budget_usd / max(1, len(gaps)) if budget_usd > 0 else 0.0
    out: list[dict[str, Any]] = []
    for name, gap in gaps.items():
        if gap <= 0 or per <= 0:
            reduction = 0.0
        else:
            reduction = _clamp01(per / (gap * cost_denominator[name]))
        closed = gap * reduction
        roi = closed / per if per > 0 else 0.0
        out.append({
            "name": name,
            "gap": gap,
            "investment_usd": per,
            "gap_reduction_fraction": reduction,
            "absolute_gap_closed": closed,
            "roi_per_dollar": roi,
        })
    out.sort(key=lambda d: d["roi_per_dollar"], reverse=True)
    return out


def monte_carlo_resilience(s: ResilienceScenario, n_trials: int = 200, seed: int = 237) -> dict[str, float]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(n_trials):
        perturbed = ResilienceScenario(
            interagency_coordination_score=_clamp01(s.interagency_coordination_score + rng.uniform(-0.05, 0.05)),
            infrastructure_redundancy_score=_clamp01(s.infrastructure_redundancy_score + rng.uniform(-0.05, 0.05)),
            public_institution_trust_score=_clamp01(s.public_institution_trust_score + rng.uniform(-0.05, 0.05)),
            grid_uptime_fraction=max(0.0, s.grid_uptime_fraction + rng.uniform(-0.01, 0.01)),
            target_grid_uptime_fraction=s.target_grid_uptime_fraction,
            available_hospital_surge_beds=max(0.0, s.available_hospital_surge_beds * (1.0 + rng.uniform(-0.08, 0.08))),
            required_hospital_surge_beds=s.required_hospital_surge_beds,
            days_of_critical_supply=max(0.0, s.days_of_critical_supply * (1.0 + rng.uniform(-0.08, 0.08))),
            target_days_of_critical_supply=s.target_days_of_critical_supply,
            secure_water_days=max(0.0, s.secure_water_days * (1.0 + rng.uniform(-0.08, 0.08))),
            target_secure_water_days=s.target_secure_water_days,
            strategic_food_days=max(0.0, s.strategic_food_days * (1.0 + rng.uniform(-0.08, 0.08))),
            target_strategic_food_days=s.target_strategic_food_days,
            cyber_mttd_hours=max(0.01, s.cyber_mttd_hours * (1.0 + rng.uniform(-0.10, 0.10))),
            target_cyber_mttd_hours=s.target_cyber_mttd_hours,
            logistics_coverage_fraction=_clamp01(s.logistics_coverage_fraction + rng.uniform(-0.05, 0.05)),
            disaster_response_hours=max(0.01, s.disaster_response_hours * (1.0 + rng.uniform(-0.10, 0.10))),
            target_disaster_response_hours=s.target_disaster_response_hours,
            verified_information_fraction=_clamp01(s.verified_information_fraction + rng.uniform(-0.05, 0.05)),
            essential_service_equity_fraction=_clamp01(s.essential_service_equity_fraction + rng.uniform(-0.05, 0.05)),
            trained_response_workforce=max(0.0, s.trained_response_workforce * (1.0 + rng.uniform(-0.10, 0.10))),
            required_response_workforce=s.required_response_workforce,
            fiscal_reserve_months=max(0.0, s.fiscal_reserve_months * (1.0 + rng.uniform(-0.10, 0.10))),
            target_fiscal_reserve_months=s.target_fiscal_reserve_months,
        )
        vals.append(resilience_readiness_index(perturbed))

    vals_sorted = sorted(vals)
    mid = len(vals_sorted) // 2
    return {
        "mean_readiness": sum(vals_sorted) / len(vals_sorted),
        "median_readiness": vals_sorted[mid],
        "p10_readiness": vals_sorted[max(0, int(0.1 * len(vals_sorted)) - 1)],
        "p90_readiness": vals_sorted[min(len(vals_sorted) - 1, int(0.9 * len(vals_sorted)))],
    }


def baseline_resilience_scenario() -> ResilienceScenario:
    return ResilienceScenario(
        interagency_coordination_score=0.56,
        infrastructure_redundancy_score=0.48,
        public_institution_trust_score=0.44,
        grid_uptime_fraction=0.975,
        target_grid_uptime_fraction=0.995,
        available_hospital_surge_beds=65_000,
        required_hospital_surge_beds=100_000,
        days_of_critical_supply=18,
        target_days_of_critical_supply=45,
        secure_water_days=22,
        target_secure_water_days=60,
        strategic_food_days=35,
        target_strategic_food_days=90,
        cyber_mttd_hours=72,
        target_cyber_mttd_hours=24,
        logistics_coverage_fraction=0.68,
        disaster_response_hours=30,
        target_disaster_response_hours=12,
        verified_information_fraction=0.62,
        essential_service_equity_fraction=0.58,
        trained_response_workforce=420_000,
        required_response_workforce=700_000,
        fiscal_reserve_months=3.0,
        target_fiscal_reserve_months=9.0,
    )


def pillar237_civilizational_resilience_report(
    budget_usd: float = 12_000_000_000.0,
    n_trials: int = 200,
    seed: int = 237,
) -> dict[str, Any]:
    """Integrated report for Pillar 237."""
    scenario = baseline_resilience_scenario()
    return {
        "pillar": 237,
        "status": __provenance__["status"],
        "strategic_hurdles": STRATEGIC_HURDLES,
        "bottleneck_order": BOTTLENECK_ORDER,
        "baseline_report": resilience_report(scenario),
        "intervention_ranking": rank_interventions_by_roi(scenario, budget_usd=budget_usd),
        "stability_simulation": monte_carlo_resilience(scenario, n_trials=n_trials, seed=seed),
        "falsification_condition": (
            "FALSIFIED as an adjacent decision engine if intervention rankings and "
            "reported bottleneck reductions are systematically anti-correlated with "
            "observed continuity outcomes under independent validation datasets."
        ),
    }


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "STRATEGIC_HURDLES",
    "BOTTLENECK_ORDER",
    "ResilienceScenario",
    "__provenance__",
    "strategic_hurdle_scores",
    "bottleneck_scores",
    "resilience_readiness_index",
    "resilience_report",
    "rank_interventions_by_roi",
    "monte_carlo_resilience",
    "baseline_resilience_scenario",
    "pillar237_civilizational_resilience_report",
]
