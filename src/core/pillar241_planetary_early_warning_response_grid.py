# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 241 — Planetary Early Warning & Coordinated Response Grid.

Adjacent research track (non-hardgate): compound-risk warning and response prioritization.
Applies Unitary Manifold (5,7)-braid geometry as a coordination framework for
planetary early warning, cascading-risk detection, and response grid orchestration.
Physical claims are speculative extrapolations; not a 5D-derived hardgate prediction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import random

__provenance__ = {
    "pillar": 241,
    "title": "Planetary Early Warning & Coordinated Response Grid",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — compound-risk warning and response prioritization",
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

HAZARD_ORDER: tuple[str, ...] = (
    "climate_extreme",
    "seismic_tsunami",
    "health_system_surge",
    "cyber_systemic",
    "grid_cascade",
    "space_weather",
)


@dataclass(frozen=True)
class PlanetaryRiskScenario:
    hazard_probability: dict[str, float]
    exposure_index: dict[str, float]
    vulnerability_index: dict[str, float]

    average_warning_lead_hours: float
    target_warning_lead_hours: float

    response_mobilization_hours: float
    target_response_mobilization_hours: float

    cross_border_operability_fraction: float
    data_fusion_coverage_fraction: float


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _validate_hazard_map(name: str, m: dict[str, float]) -> None:
    if set(m.keys()) != set(HAZARD_ORDER):
        raise ValueError(f"{name} must have exactly hazards {HAZARD_ORDER}")
    for h, v in m.items():
        if not (0 <= v <= 1):
            raise ValueError(f"{name}[{h}] must be in [0,1]")


def hazard_risk_scores(s: PlanetaryRiskScenario) -> dict[str, float]:
    _validate_hazard_map("hazard_probability", s.hazard_probability)
    _validate_hazard_map("exposure_index", s.exposure_index)
    _validate_hazard_map("vulnerability_index", s.vulnerability_index)
    return {
        h: _clamp01(s.hazard_probability[h] * s.exposure_index[h] * s.vulnerability_index[h])
        for h in HAZARD_ORDER
    }


def warning_latency_gap(s: PlanetaryRiskScenario) -> float:
    if s.target_warning_lead_hours <= 0 or s.average_warning_lead_hours < 0:
        raise ValueError("invalid warning inputs")
    return _clamp01(1.0 - s.average_warning_lead_hours / s.target_warning_lead_hours)


def response_latency_gap(s: PlanetaryRiskScenario) -> float:
    if s.target_response_mobilization_hours <= 0 or s.response_mobilization_hours < 0:
        raise ValueError("invalid response inputs")
    return _clamp01(s.response_mobilization_hours / s.target_response_mobilization_hours - 1.0)


def global_risk_pulse(s: PlanetaryRiskScenario) -> float:
    hazard = hazard_risk_scores(s)
    h_mean = sum(hazard.values()) / len(hazard)
    wl = warning_latency_gap(s)
    rl = response_latency_gap(s)
    if not (0 <= s.cross_border_operability_fraction <= 1):
        raise ValueError("cross_border_operability_fraction must be in [0,1]")
    if not (0 <= s.data_fusion_coverage_fraction <= 1):
        raise ValueError("data_fusion_coverage_fraction must be in [0,1]")

    coordination_gap = 1.0 - s.cross_border_operability_fraction
    fusion_gap = 1.0 - s.data_fusion_coverage_fraction

    return _clamp01(0.45 * h_mean + 0.20 * wl + 0.20 * rl + 0.10 * coordination_gap + 0.05 * fusion_gap)


def coordinated_response_priority_queue(s: PlanetaryRiskScenario) -> list[dict[str, float | str]]:
    hazard = hazard_risk_scores(s)
    queue = [{"hazard": h, "risk": hazard[h]} for h in HAZARD_ORDER]
    queue.sort(key=lambda x: x["risk"], reverse=True)
    return queue


def warning_grid_report(s: PlanetaryRiskScenario) -> dict[str, Any]:
    hazard = hazard_risk_scores(s)
    pulse = global_risk_pulse(s)
    queue = coordinated_response_priority_queue(s)
    return {
        "global_risk_pulse": pulse,
        "hazard_risk_scores": hazard,
        "warning_latency_gap": warning_latency_gap(s),
        "response_latency_gap": response_latency_gap(s),
        "priority_queue": queue,
        "status": "CALCULATED planetary warning-response report",
    }


def monte_carlo_global_risk(s: PlanetaryRiskScenario, n_trials: int = 200, seed: int = 241) -> dict[str, float]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(n_trials):
        hp = {h: _clamp01(s.hazard_probability[h] + rng.uniform(-0.05, 0.05)) for h in HAZARD_ORDER}
        ex = {h: _clamp01(s.exposure_index[h] + rng.uniform(-0.05, 0.05)) for h in HAZARD_ORDER}
        vu = {h: _clamp01(s.vulnerability_index[h] + rng.uniform(-0.05, 0.05)) for h in HAZARD_ORDER}
        p = PlanetaryRiskScenario(
            hazard_probability=hp,
            exposure_index=ex,
            vulnerability_index=vu,
            average_warning_lead_hours=max(0.0, s.average_warning_lead_hours * (1 + rng.uniform(-0.1, 0.1))),
            target_warning_lead_hours=s.target_warning_lead_hours,
            response_mobilization_hours=max(0.0, s.response_mobilization_hours * (1 + rng.uniform(-0.1, 0.1))),
            target_response_mobilization_hours=s.target_response_mobilization_hours,
            cross_border_operability_fraction=_clamp01(s.cross_border_operability_fraction + rng.uniform(-0.05, 0.05)),
            data_fusion_coverage_fraction=_clamp01(s.data_fusion_coverage_fraction + rng.uniform(-0.05, 0.05)),
        )
        vals.append(global_risk_pulse(p))

    vals.sort()
    return {
        "mean_pulse": sum(vals) / len(vals),
        "p10_pulse": vals[max(0, int(0.1 * len(vals)) - 1)],
        "p50_pulse": vals[len(vals) // 2],
        "p90_pulse": vals[min(len(vals) - 1, int(0.9 * len(vals)))],
    }


def baseline_planetary_risk_scenario() -> PlanetaryRiskScenario:
    return PlanetaryRiskScenario(
        hazard_probability={
            "climate_extreme": 0.72,
            "seismic_tsunami": 0.28,
            "health_system_surge": 0.41,
            "cyber_systemic": 0.63,
            "grid_cascade": 0.47,
            "space_weather": 0.24,
        },
        exposure_index={
            "climate_extreme": 0.81,
            "seismic_tsunami": 0.44,
            "health_system_surge": 0.77,
            "cyber_systemic": 0.79,
            "grid_cascade": 0.69,
            "space_weather": 0.57,
        },
        vulnerability_index={
            "climate_extreme": 0.62,
            "seismic_tsunami": 0.55,
            "health_system_surge": 0.58,
            "cyber_systemic": 0.64,
            "grid_cascade": 0.61,
            "space_weather": 0.49,
        },
        average_warning_lead_hours=18,
        target_warning_lead_hours=36,
        response_mobilization_hours=22,
        target_response_mobilization_hours=8,
        cross_border_operability_fraction=0.53,
        data_fusion_coverage_fraction=0.59,
    )


def pillar241_planetary_warning_report(
    n_trials: int = 200,
    seed: int = 241,
) -> dict[str, Any]:
    """Integrated report for Pillar 241."""
    scenario = baseline_planetary_risk_scenario()
    return {
        "pillar": 241,
        "status": __provenance__["status"],
        "hazard_order": HAZARD_ORDER,
        "baseline_report": warning_grid_report(scenario),
        "stability_simulation": monte_carlo_global_risk(scenario, n_trials=n_trials, seed=seed),
        "falsification_condition": (
            "FALSIFIED as an adjacent decision engine if global-risk-pulse predictions "
            "are systematically anti-correlated with observed compound-hazard outcomes "
            "under independent validation datasets."
        ),
    }


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "HAZARD_ORDER",
    "PlanetaryRiskScenario",
    "__provenance__",
    "hazard_risk_scores",
    "warning_latency_gap",
    "response_latency_gap",
    "global_risk_pulse",
    "coordinated_response_priority_queue",
    "warning_grid_report",
    "monte_carlo_global_risk",
    "baseline_planetary_risk_scenario",
    "pillar241_planetary_warning_report",
]
