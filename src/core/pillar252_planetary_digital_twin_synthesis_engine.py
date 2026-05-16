# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 252 — Planetary Digital-Twin Synthesis Engine.

Adjacent research track (non-hardgate): constructs a time-evolving planetary
state twin coupling climate, food, disease, infrastructure, warning, and
governance response into scenario-grade trajectories.

Boundary statement (strict):
- This module is policy-simulation infrastructure for comparative planning.
- It is not a claim of deterministic planetary prediction.
- It does not modify hardgate physics status or ToE score.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Any

from src.core.pillar237_civilizational_resilience_os import (
    baseline_resilience_scenario,
    resilience_readiness_index,
)
from src.core.pillar238_global_disease_forecast_response_fabric import (
    baseline_health_scenario,
    response_adequacy_index,
)
from src.core.pillar239_autonomous_infrastructure_stability_engine import (
    baseline_autonomy_scenario,
    safe_automation_envelope_index,
)
from src.core.pillar240_precision_agriculture_food_security_command import (
    baseline_food_scenario,
    food_security_probability_surface,
)
from src.core.pillar241_planetary_early_warning_response_grid import (
    baseline_planetary_risk_scenario,
    global_risk_pulse,
)

__provenance__ = {
    "pillar": 252,
    "title": "Planetary Digital-Twin Synthesis Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — planetary digital twin; non-hardgate, "
        "scenario synthesis only"
    ),
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

ADJACENCY_TRACK_LABEL = "ADJACENT RESEARCH TRACK"
PLANETARY_TWIN_TRACK_LABEL = "PLANETARY_DIGITAL_TWIN_TRACK"

SECTORS: tuple[str, ...] = (
    "climate_resilience",
    "food_security",
    "disease_response",
    "infrastructure_stability",
    "warning_coverage",
    "governance_response",
)


@dataclass(frozen=True)
class PlanetaryTwinState:
    climate_resilience: float
    food_security: float
    disease_response: float
    infrastructure_stability: float
    warning_coverage: float
    governance_response: float
    phi_trust: float
    n_hil: int

    def __post_init__(self) -> None:
        for f in SECTORS + ("phi_trust",):
            _validate01(f, float(getattr(self, f)))
        if self.n_hil < 0:
            raise ValueError("n_hil must be >= 0")


def _validate01(name: str, value: float) -> None:
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def separation_guard() -> dict[str, Any]:
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": PLANETARY_TWIN_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "deterministic_forecast_claim_allowed": False,
        "message": (
            "Pillar 252 outputs are scenario-grade planning trajectories with "
            "explicit uncertainty, not deterministic planetary forecasts."
        ),
    }


def sector_adequacy(state: PlanetaryTwinState) -> dict[str, float]:
    return {k: float(getattr(state, k)) for k in SECTORS}


def coupling_matrix(state: PlanetaryTwinState) -> dict[str, dict[str, float]]:
    adequacy = sector_adequacy(state)
    matrix: dict[str, dict[str, float]] = {}
    for i in SECTORS:
        matrix[i] = {}
        for j in SECTORS:
            if i == j:
                matrix[i][j] = 0.0
            else:
                matrix[i][j] = C_S * (1.0 - adequacy[i]) * (1.0 - adequacy[j])
    return matrix


def twin_coherence_index(state: PlanetaryTwinState) -> float:
    adequacy = sector_adequacy(state)
    mean = sum(adequacy.values()) / len(adequacy)
    variance = sum((v - mean) ** 2 for v in adequacy.values()) / len(adequacy)
    cascade_penalty = sum(
        coupling_matrix(state)[i][j]
        for i in SECTORS
        for j in SECTORS
        if i != j
    ) / (len(SECTORS) * (len(SECTORS) - 1))

    hil_weight = _clamp01(state.phi_trust * min(1.0, C_S * (1.0 + state.n_hil / 15.0)))
    return _clamp01(mean * (1.0 - cascade_penalty) * (1.0 - 0.5 * variance) * hil_weight)


def step_planetary_twin(state: PlanetaryTwinState, years: float = 1.0) -> PlanetaryTwinState:
    if years <= 0:
        raise ValueError("years must be > 0")

    a = sector_adequacy(state)
    matrix = coupling_matrix(state)
    shock = {
        s: sum(matrix[s][o] for o in SECTORS if o != s) / (len(SECTORS) - 1)
        for s in SECTORS
    }

    update = {}
    for s in SECTORS:
        baseline_recovery = 0.06 * a[s] * (1.0 - a[s])
        governance_boost = 0.08 * state.governance_response * (1.0 - a[s])
        warning_boost = 0.05 * state.warning_coverage * (1.0 - a[s])
        decay = 0.20 * shock[s]
        update[s] = _clamp01(a[s] + years * (baseline_recovery + governance_boost + warning_boost - decay))

    return PlanetaryTwinState(
        climate_resilience=update["climate_resilience"],
        food_security=update["food_security"],
        disease_response=update["disease_response"],
        infrastructure_stability=update["infrastructure_stability"],
        warning_coverage=update["warning_coverage"],
        governance_response=update["governance_response"],
        phi_trust=state.phi_trust,
        n_hil=state.n_hil,
    )


def simulate_planetary_path(
    state: PlanetaryTwinState,
    horizon_years: int = 10,
) -> list[dict[str, Any]]:
    if horizon_years < 1:
        raise ValueError("horizon_years must be >= 1")

    out: list[dict[str, Any]] = []
    current = state
    for year in range(0, horizon_years + 1):
        out.append(
            {
                "year": year,
                "state": current,
                "coherence_index": twin_coherence_index(current),
                "sector_adequacy": sector_adequacy(current),
            }
        )
        if year < horizon_years:
            current = step_planetary_twin(current, years=1.0)
    return out


def intervention_allocator(state: PlanetaryTwinState, budget_usd: float) -> list[dict[str, float | str]]:
    if budget_usd < 0:
        raise ValueError("budget_usd must be >= 0")

    adequacy = sector_adequacy(state)
    matrix = coupling_matrix(state)
    impacts = {}
    for s in SECTORS:
        coupling_load = sum(matrix[s][o] for o in SECTORS if o != s) / (len(SECTORS) - 1)
        impacts[s] = (1.0 - adequacy[s]) * (1.0 + coupling_load)

    total = sum(impacts.values())
    rows = []
    for s in SECTORS:
        frac = 0.0 if total <= 0 or budget_usd == 0 else impacts[s] / total
        rows.append(
            {
                "sector": s,
                "adequacy": adequacy[s],
                "impact_score": impacts[s],
                "allocated_fraction": frac,
                "allocated_budget_usd": budget_usd * frac,
            }
        )
    rows.sort(key=lambda x: float(x["impact_score"]), reverse=True)
    return rows


def scenario_risk_envelope(
    state: PlanetaryTwinState,
    horizon_years: int = 10,
    n_trials: int = 252,
    sigma: float = 0.05,
    seed: int = 252,
) -> dict[str, float | str]:
    if n_trials < 10:
        raise ValueError("n_trials must be >= 10")
    if sigma < 0:
        raise ValueError("sigma must be >= 0")

    rng = random.Random(seed)
    terminal_scores: list[float] = []
    for _ in range(n_trials):
        noisy = PlanetaryTwinState(
            **{
                **state.__dict__,
                "climate_resilience": _clamp01(state.climate_resilience + rng.uniform(-sigma, sigma)),
                "food_security": _clamp01(state.food_security + rng.uniform(-sigma, sigma)),
                "disease_response": _clamp01(state.disease_response + rng.uniform(-sigma, sigma)),
                "infrastructure_stability": _clamp01(state.infrastructure_stability + rng.uniform(-sigma, sigma)),
                "warning_coverage": _clamp01(state.warning_coverage + rng.uniform(-sigma, sigma)),
                "governance_response": _clamp01(state.governance_response + rng.uniform(-sigma, sigma)),
            }
        )
        path = simulate_planetary_path(noisy, horizon_years=horizon_years)
        terminal_scores.append(float(path[-1]["coherence_index"]))

    terminal_scores.sort()
    i10 = int(0.10 * (n_trials - 1))
    i50 = int(0.50 * (n_trials - 1))
    i90 = int(0.90 * (n_trials - 1))
    return {
        "p10_terminal": terminal_scores[i10],
        "p50_terminal": terminal_scores[i50],
        "p90_terminal": terminal_scores[i90],
        "spread_terminal": terminal_scores[i90] - terminal_scores[i10],
        "status": "CALCULATED deterministic twin trajectory envelope",
    }


def baseline_planetary_twin_state(phi_trust: float = 0.88, n_hil: int = 6) -> PlanetaryTwinState:
    climate = _clamp01(float(resilience_readiness_index(baseline_resilience_scenario())))
    food = _clamp01(float(food_security_probability_surface(baseline_food_scenario())))
    disease = _clamp01(float(response_adequacy_index(baseline_health_scenario())))
    infra = _clamp01(float(safe_automation_envelope_index(baseline_autonomy_scenario())))
    warning = _clamp01(1.0 - float(global_risk_pulse(baseline_planetary_risk_scenario())))
    governance = _clamp01(0.60 * climate + 0.40 * warning)

    return PlanetaryTwinState(
        climate_resilience=climate,
        food_security=food,
        disease_response=disease,
        infrastructure_stability=infra,
        warning_coverage=warning,
        governance_response=governance,
        phi_trust=phi_trust,
        n_hil=n_hil,
    )


def pillar252_planetary_digital_twin_report(
    horizon_years: int = 10,
    budget_usd: float = 2_500_000_000_000.0,
) -> dict[str, Any]:
    state = baseline_planetary_twin_state()
    path = simulate_planetary_path(state, horizon_years=horizon_years)
    return {
        "provenance": __provenance__,
        "separation_guard": separation_guard(),
        "baseline_state": state,
        "baseline_coherence_index": twin_coherence_index(state),
        "coupling_matrix": coupling_matrix(state),
        "path": path,
        "allocation": intervention_allocator(state, budget_usd=budget_usd),
        "risk_envelope": scenario_risk_envelope(state, horizon_years=horizon_years),
        "falsification_condition": (
            "FALSIFIED if multi-year retrospective benchmarking shows trajectory "
            "ordering is consistently anti-correlated with independently observed "
            "cross-sector resilience outcomes under pre-registered datasets."
        ),
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "C_S",
    "K_CS",
    "N_W",
    "PHI0",
    "PLANETARY_TWIN_TRACK_LABEL",
    "PlanetaryTwinState",
    "SECTORS",
    "__provenance__",
    "baseline_planetary_twin_state",
    "coupling_matrix",
    "intervention_allocator",
    "pillar252_planetary_digital_twin_report",
    "scenario_risk_envelope",
    "sector_adequacy",
    "separation_guard",
    "simulate_planetary_path",
    "step_planetary_twin",
    "twin_coherence_index",
]
