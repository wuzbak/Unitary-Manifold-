# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 239 — Autonomous Infrastructure Stability Engine (adjacent track)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import random

__provenance__ = {
    "pillar": 239,
    "title": "Autonomous Infrastructure Stability Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — safe autonomy deployment envelope calculator",
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

BOTTLENECK_ORDER: tuple[str, ...] = (
    "robotics_reliability_gap",
    "grid_power_gap",
    "edge_compute_gap",
    "cyber_hardening_gap",
    "safety_case_gap",
    "regulatory_latency_gap",
    "incident_response_gap",
    "human_oversight_gap",
    "supply_chain_gap",
    "interoperability_gap",
    "workforce_gap",
    "trust_acceptance_gap",
)


@dataclass(frozen=True)
class AutonomyScenario:
    robot_task_success_rate: float
    target_robot_task_success_rate: float

    available_power_gw: float
    required_power_gw: float

    available_edge_tops: float
    required_edge_tops: float

    critical_vulns_per_quarter: float
    tolerated_vulns_per_quarter: float

    certified_safety_cases_fraction: float

    regulatory_approval_months: float
    target_regulatory_approval_months: float

    mean_incident_response_minutes: float
    target_incident_response_minutes: float

    human_override_coverage_fraction: float

    critical_component_resilience_fraction: float

    open_standards_interoperability_fraction: float

    trained_operators: float
    required_trained_operators: float

    public_acceptance_fraction: float


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


def bottleneck_scores(s: AutonomyScenario) -> dict[str, float]:
    for name, val in (
        ("robot_task_success_rate", s.robot_task_success_rate),
        ("target_robot_task_success_rate", s.target_robot_task_success_rate),
        ("certified_safety_cases_fraction", s.certified_safety_cases_fraction),
        ("human_override_coverage_fraction", s.human_override_coverage_fraction),
        ("critical_component_resilience_fraction", s.critical_component_resilience_fraction),
        ("open_standards_interoperability_fraction", s.open_standards_interoperability_fraction),
        ("public_acceptance_fraction", s.public_acceptance_fraction),
    ):
        if not (0 <= val <= 1):
            raise ValueError(f"{name} must be in [0,1]")

    return {
        "robotics_reliability_gap": _ratio_deficit(s.robot_task_success_rate, s.target_robot_task_success_rate),
        "grid_power_gap": _ratio_deficit(s.available_power_gw, s.required_power_gw),
        "edge_compute_gap": _ratio_deficit(s.available_edge_tops, s.required_edge_tops),
        "cyber_hardening_gap": _ratio_excess(s.critical_vulns_per_quarter, s.tolerated_vulns_per_quarter),
        "safety_case_gap": 1.0 - s.certified_safety_cases_fraction,
        "regulatory_latency_gap": _ratio_excess(s.regulatory_approval_months, s.target_regulatory_approval_months),
        "incident_response_gap": _ratio_excess(s.mean_incident_response_minutes, s.target_incident_response_minutes),
        "human_oversight_gap": 1.0 - s.human_override_coverage_fraction,
        "supply_chain_gap": 1.0 - s.critical_component_resilience_fraction,
        "interoperability_gap": 1.0 - s.open_standards_interoperability_fraction,
        "workforce_gap": _ratio_deficit(s.trained_operators, s.required_trained_operators),
        "trust_acceptance_gap": 1.0 - s.public_acceptance_fraction,
    }


def safe_automation_envelope_index(s: AutonomyScenario) -> float:
    gaps = bottleneck_scores(s)
    mean_gap = sum(gaps.values()) / len(gaps)
    return _clamp01(1.0 - mean_gap)


def autonomy_readiness_report(s: AutonomyScenario) -> dict[str, Any]:
    gaps = bottleneck_scores(s)
    envelope = safe_automation_envelope_index(s)
    top = sorted(gaps.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "safe_automation_envelope_index": envelope,
        "bottlenecks": gaps,
        "top_constraints": [{"name": n, "gap": g} for n, g in top],
        "status": "CALCULATED autonomy infrastructure stability report",
    }


def intervention_rank(s: AutonomyScenario, budget_usd: float) -> list[dict[str, Any]]:
    if budget_usd < 0:
        raise ValueError("budget_usd must be non-negative")
    gaps = bottleneck_scores(s)
    costs = {name: 5_000_000 + i * 750_000 for i, name in enumerate(gaps.keys())}
    per = budget_usd / max(1, len(gaps)) if budget_usd > 0 else 0.0
    results = []
    for name, gap in gaps.items():
        frac = _clamp01(per / (gap * costs[name])) if (gap > 0 and per > 0) else 0.0
        closed = gap * frac
        roi = closed / per if per > 0 else 0.0
        results.append({"name": name, "gap": gap, "roi_per_dollar": roi, "closed": closed})
    results.sort(key=lambda d: d["roi_per_dollar"], reverse=True)
    return results


def monte_carlo_envelope(s: AutonomyScenario, n_trials: int = 200, seed: int = 239) -> dict[str, float]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(n_trials):
        p = AutonomyScenario(
            robot_task_success_rate=_clamp01(s.robot_task_success_rate + rng.uniform(-0.04, 0.04)),
            target_robot_task_success_rate=s.target_robot_task_success_rate,
            available_power_gw=max(0.0, s.available_power_gw * (1 + rng.uniform(-0.08, 0.08))),
            required_power_gw=s.required_power_gw,
            available_edge_tops=max(0.0, s.available_edge_tops * (1 + rng.uniform(-0.08, 0.08))),
            required_edge_tops=s.required_edge_tops,
            critical_vulns_per_quarter=max(0.0, s.critical_vulns_per_quarter * (1 + rng.uniform(-0.12, 0.12))),
            tolerated_vulns_per_quarter=s.tolerated_vulns_per_quarter,
            certified_safety_cases_fraction=_clamp01(s.certified_safety_cases_fraction + rng.uniform(-0.05, 0.05)),
            regulatory_approval_months=max(0.1, s.regulatory_approval_months * (1 + rng.uniform(-0.1, 0.1))),
            target_regulatory_approval_months=s.target_regulatory_approval_months,
            mean_incident_response_minutes=max(0.1, s.mean_incident_response_minutes * (1 + rng.uniform(-0.1, 0.1))),
            target_incident_response_minutes=s.target_incident_response_minutes,
            human_override_coverage_fraction=_clamp01(s.human_override_coverage_fraction + rng.uniform(-0.05, 0.05)),
            critical_component_resilience_fraction=_clamp01(s.critical_component_resilience_fraction + rng.uniform(-0.05, 0.05)),
            open_standards_interoperability_fraction=_clamp01(s.open_standards_interoperability_fraction + rng.uniform(-0.05, 0.05)),
            trained_operators=max(0.0, s.trained_operators * (1 + rng.uniform(-0.1, 0.1))),
            required_trained_operators=s.required_trained_operators,
            public_acceptance_fraction=_clamp01(s.public_acceptance_fraction + rng.uniform(-0.05, 0.05)),
        )
        vals.append(safe_automation_envelope_index(p))

    vals.sort()
    return {
        "mean_envelope": sum(vals) / len(vals),
        "p10_envelope": vals[max(0, int(0.1 * len(vals)) - 1)],
        "p50_envelope": vals[len(vals) // 2],
        "p90_envelope": vals[min(len(vals) - 1, int(0.9 * len(vals)))],
    }


def baseline_autonomy_scenario() -> AutonomyScenario:
    return AutonomyScenario(
        robot_task_success_rate=0.78,
        target_robot_task_success_rate=0.95,
        available_power_gw=5.5,
        required_power_gw=8.0,
        available_edge_tops=1300,
        required_edge_tops=2000,
        critical_vulns_per_quarter=14,
        tolerated_vulns_per_quarter=5,
        certified_safety_cases_fraction=0.46,
        regulatory_approval_months=18,
        target_regulatory_approval_months=9,
        mean_incident_response_minutes=42,
        target_incident_response_minutes=15,
        human_override_coverage_fraction=0.62,
        critical_component_resilience_fraction=0.57,
        open_standards_interoperability_fraction=0.54,
        trained_operators=120_000,
        required_trained_operators=220_000,
        public_acceptance_fraction=0.48,
    )
