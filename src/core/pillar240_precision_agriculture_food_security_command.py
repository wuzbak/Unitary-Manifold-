# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 240 — Precision Agriculture & Food Security Command Layer."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import random

__provenance__ = {
    "pillar": 240,
    "title": "Precision Agriculture & Food Security Command Layer",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK — food-system resilience and allocation engine",
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

BOTTLENECK_ORDER: tuple[str, ...] = (
    "crop_yield_gap",
    "soil_health_gap",
    "irrigation_gap",
    "fertilizer_affordability_gap",
    "storage_loss_gap",
    "transport_gap",
    "market_access_gap",
    "pest_pressure_gap",
    "fisheries_stability_gap",
    "climate_shock_gap",
    "nutrition_equity_gap",
    "strategic_reserve_gap",
)


@dataclass(frozen=True)
class FoodScenario:
    achieved_yield_tpha: float
    target_yield_tpha: float

    soil_organic_matter_fraction: float
    target_soil_organic_matter_fraction: float

    irrigated_area_fraction: float
    target_irrigated_area_fraction: float

    fertilizer_cost_index: float
    target_fertilizer_cost_index: float

    post_harvest_loss_fraction: float
    target_post_harvest_loss_fraction: float

    cold_chain_coverage_fraction: float

    farmer_market_access_fraction: float

    pest_loss_fraction: float
    target_pest_loss_fraction: float

    sustainable_fish_stock_fraction: float

    climate_extreme_days: float
    target_climate_extreme_days: float

    vulnerable_nutrition_coverage_fraction: float

    strategic_food_days: float
    target_strategic_food_days: float


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _ratio_deficit(actual: float, target: float) -> float:
    if actual < 0 or target <= 0:
        raise ValueError("invalid ratio inputs")
    return _clamp01(1 - actual / target)


def _ratio_excess(actual: float, target: float) -> float:
    if actual < 0 or target <= 0:
        raise ValueError("invalid ratio inputs")
    return _clamp01(actual / target - 1)


def bottleneck_scores(s: FoodScenario) -> dict[str, float]:
    for name, value in (
        ("soil_organic_matter_fraction", s.soil_organic_matter_fraction),
        ("target_soil_organic_matter_fraction", s.target_soil_organic_matter_fraction),
        ("irrigated_area_fraction", s.irrigated_area_fraction),
        ("target_irrigated_area_fraction", s.target_irrigated_area_fraction),
        ("post_harvest_loss_fraction", s.post_harvest_loss_fraction),
        ("target_post_harvest_loss_fraction", s.target_post_harvest_loss_fraction),
        ("cold_chain_coverage_fraction", s.cold_chain_coverage_fraction),
        ("farmer_market_access_fraction", s.farmer_market_access_fraction),
        ("pest_loss_fraction", s.pest_loss_fraction),
        ("target_pest_loss_fraction", s.target_pest_loss_fraction),
        ("sustainable_fish_stock_fraction", s.sustainable_fish_stock_fraction),
        ("vulnerable_nutrition_coverage_fraction", s.vulnerable_nutrition_coverage_fraction),
    ):
        if not (0 <= value <= 1):
            raise ValueError(f"{name} must be in [0,1]")

    return {
        "crop_yield_gap": _ratio_deficit(s.achieved_yield_tpha, s.target_yield_tpha),
        "soil_health_gap": _ratio_deficit(s.soil_organic_matter_fraction, s.target_soil_organic_matter_fraction),
        "irrigation_gap": _ratio_deficit(s.irrigated_area_fraction, s.target_irrigated_area_fraction),
        "fertilizer_affordability_gap": _ratio_excess(s.fertilizer_cost_index, s.target_fertilizer_cost_index),
        "storage_loss_gap": _ratio_excess(s.post_harvest_loss_fraction, s.target_post_harvest_loss_fraction),
        "transport_gap": 1.0 - s.cold_chain_coverage_fraction,
        "market_access_gap": 1.0 - s.farmer_market_access_fraction,
        "pest_pressure_gap": _ratio_excess(s.pest_loss_fraction, s.target_pest_loss_fraction),
        "fisheries_stability_gap": 1.0 - s.sustainable_fish_stock_fraction,
        "climate_shock_gap": _ratio_excess(s.climate_extreme_days, s.target_climate_extreme_days),
        "nutrition_equity_gap": 1.0 - s.vulnerable_nutrition_coverage_fraction,
        "strategic_reserve_gap": _ratio_deficit(s.strategic_food_days, s.target_strategic_food_days),
    }


def food_security_probability_surface(s: FoodScenario) -> float:
    gaps = bottleneck_scores(s)
    mean_gap = sum(gaps.values()) / len(gaps)
    return _clamp01(1.0 - mean_gap)


def food_security_report(s: FoodScenario) -> dict[str, Any]:
    gaps = bottleneck_scores(s)
    p = food_security_probability_surface(s)
    top = sorted(gaps.items(), key=lambda kv: kv[1], reverse=True)[:5]
    return {
        "food_security_probability": p,
        "bottlenecks": gaps,
        "top_constraints": [{"name": n, "gap": g} for n, g in top],
        "status": "CALCULATED food security command report",
    }


def intervention_priority(s: FoodScenario, budget_usd: float) -> list[dict[str, Any]]:
    if budget_usd < 0:
        raise ValueError("budget_usd must be non-negative")
    gaps = bottleneck_scores(s)
    costs = {name: 2_000_000 + i * 500_000 for i, name in enumerate(gaps.keys())}
    per = budget_usd / max(1, len(gaps)) if budget_usd > 0 else 0.0
    out = []
    for name, gap in gaps.items():
        frac = _clamp01(per / (gap * costs[name])) if (gap > 0 and per > 0) else 0.0
        closed = gap * frac
        roi = closed / per if per > 0 else 0.0
        out.append({"name": name, "gap": gap, "roi_per_dollar": roi, "closed": closed})
    out.sort(key=lambda d: d["roi_per_dollar"], reverse=True)
    return out


def monte_carlo_food_security(s: FoodScenario, n_trials: int = 200, seed: int = 240) -> dict[str, float]:
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(n_trials):
        p = FoodScenario(
            achieved_yield_tpha=max(0.0, s.achieved_yield_tpha * (1 + rng.uniform(-0.08, 0.08))),
            target_yield_tpha=s.target_yield_tpha,
            soil_organic_matter_fraction=_clamp01(s.soil_organic_matter_fraction + rng.uniform(-0.04, 0.04)),
            target_soil_organic_matter_fraction=s.target_soil_organic_matter_fraction,
            irrigated_area_fraction=_clamp01(s.irrigated_area_fraction + rng.uniform(-0.04, 0.04)),
            target_irrigated_area_fraction=s.target_irrigated_area_fraction,
            fertilizer_cost_index=max(0.01, s.fertilizer_cost_index * (1 + rng.uniform(-0.1, 0.1))),
            target_fertilizer_cost_index=s.target_fertilizer_cost_index,
            post_harvest_loss_fraction=_clamp01(s.post_harvest_loss_fraction + rng.uniform(-0.04, 0.04)),
            target_post_harvest_loss_fraction=s.target_post_harvest_loss_fraction,
            cold_chain_coverage_fraction=_clamp01(s.cold_chain_coverage_fraction + rng.uniform(-0.05, 0.05)),
            farmer_market_access_fraction=_clamp01(s.farmer_market_access_fraction + rng.uniform(-0.05, 0.05)),
            pest_loss_fraction=_clamp01(s.pest_loss_fraction + rng.uniform(-0.04, 0.04)),
            target_pest_loss_fraction=s.target_pest_loss_fraction,
            sustainable_fish_stock_fraction=_clamp01(s.sustainable_fish_stock_fraction + rng.uniform(-0.04, 0.04)),
            climate_extreme_days=max(0.0, s.climate_extreme_days * (1 + rng.uniform(-0.12, 0.12))),
            target_climate_extreme_days=s.target_climate_extreme_days,
            vulnerable_nutrition_coverage_fraction=_clamp01(s.vulnerable_nutrition_coverage_fraction + rng.uniform(-0.05, 0.05)),
            strategic_food_days=max(0.0, s.strategic_food_days * (1 + rng.uniform(-0.1, 0.1))),
            target_strategic_food_days=s.target_strategic_food_days,
        )
        vals.append(food_security_probability_surface(p))

    vals.sort()
    return {
        "mean_probability": sum(vals) / len(vals),
        "p10_probability": vals[max(0, int(0.1 * len(vals)) - 1)],
        "p50_probability": vals[len(vals) // 2],
        "p90_probability": vals[min(len(vals) - 1, int(0.9 * len(vals)))],
    }


def baseline_food_scenario() -> FoodScenario:
    return FoodScenario(
        achieved_yield_tpha=3.4,
        target_yield_tpha=4.5,
        soil_organic_matter_fraction=0.027,
        target_soil_organic_matter_fraction=0.045,
        irrigated_area_fraction=0.46,
        target_irrigated_area_fraction=0.62,
        fertilizer_cost_index=1.35,
        target_fertilizer_cost_index=1.00,
        post_harvest_loss_fraction=0.19,
        target_post_harvest_loss_fraction=0.10,
        cold_chain_coverage_fraction=0.52,
        farmer_market_access_fraction=0.57,
        pest_loss_fraction=0.16,
        target_pest_loss_fraction=0.08,
        sustainable_fish_stock_fraction=0.64,
        climate_extreme_days=19,
        target_climate_extreme_days=10,
        vulnerable_nutrition_coverage_fraction=0.61,
        strategic_food_days=40,
        target_strategic_food_days=90,
    )


def pillar240_food_security_report(
    budget_usd: float = 5_000_000_000.0,
    n_trials: int = 200,
    seed: int = 240,
) -> dict[str, Any]:
    """Integrated report for Pillar 240."""
    scenario = baseline_food_scenario()
    return {
        "pillar": 240,
        "status": __provenance__["status"],
        "bottleneck_order": BOTTLENECK_ORDER,
        "baseline_report": food_security_report(scenario),
        "intervention_ranking": intervention_priority(scenario, budget_usd=budget_usd),
        "stability_simulation": monte_carlo_food_security(scenario, n_trials=n_trials, seed=seed),
        "falsification_condition": (
            "FALSIFIED as an adjacent decision engine if food-security probability "
            "predictions are systematically anti-correlated with observed food-system "
            "outcomes under independent validation datasets."
        ),
    }


__all__ = [
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "BOTTLENECK_ORDER",
    "FoodScenario",
    "__provenance__",
    "bottleneck_scores",
    "food_security_probability_surface",
    "food_security_report",
    "intervention_priority",
    "monte_carlo_food_security",
    "baseline_food_scenario",
    "pillar240_food_security_report",
]
