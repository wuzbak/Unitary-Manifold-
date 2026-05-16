# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 253 — AI Compute Sustainability & Access Engine.

Adjacent research track (non-hardgate): deterministic calculator for the coupled
problem of AI/cloud compute growth, electricity/carbon/water burden, and token-
cost affordability pressure.

Boundary statement (strict):
- This module is a planning and prioritization surface.
- It is not a hardgate physics claim and does not change ToE score.
- Outputs are policy/engineering guidance, not market-price guarantees.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.pillar220_energy_manifold import global_energy_manifold
from src.core.pillar227_ai_robotics_bottleneck_engine import (
    baseline_2026_scenario,
    deployment_readiness_report,
)
from src.core.pillar229_ai_robotics_solutions_engine import solve_for_target_readiness

__provenance__ = {
    "pillar": 253,
    "title": "AI Compute Sustainability & Access Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — AI/cloud sustainability and affordability "
        "calculator; non-hardgate, policy-planning only"
    ),
    "external_data_anchor": {
        "iea_data_center_twh_2024": [415.0, 460.0],
        "iea_data_center_twh_2026_high_case": 1050.0,
        "gpt3_training_mwh_reference": 1287.0,
        "bloom_training_mwh_reference": 433.0,
    },
}

N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

ADJACENCY_TRACK_LABEL = "ADJACENT RESEARCH TRACK"
AI_COMPUTE_TRACK_LABEL = "AI_COMPUTE_SUSTAINABILITY_ACCESS_TRACK"

IEA_DATA_CENTER_TWH_2024_LOW: float = 415.0
IEA_DATA_CENTER_TWH_2024_HIGH: float = 460.0
IEA_DATA_CENTER_TWH_2026_HIGH_CASE: float = 1050.0
TARGET_CLEAN_CARBON_INTENSITY_KG_PER_KWH: float = 0.05


@dataclass(frozen=True)
class AIComputeScenario:
    ai_compute_twh_year: float
    renewable_matched_fraction: float
    grid_carbon_intensity_kg_per_kwh: float
    water_liters_per_kwh: float
    pue: float
    hardware_utilization: float
    model_efficiency_gain_fraction: float
    annual_input_tokens_millions: float
    annual_output_tokens_millions: float
    input_price_usd_per_million_tokens: float
    output_price_usd_per_million_tokens: float
    inclusion_budget_usd_per_user_year: float
    annual_users: float
    embodied_emissions_mtco2e_year: float = 0.0

    def __post_init__(self) -> None:
        if self.ai_compute_twh_year < 0:
            raise ValueError("ai_compute_twh_year must be >= 0")
        _validate01("renewable_matched_fraction", self.renewable_matched_fraction)
        if self.grid_carbon_intensity_kg_per_kwh < 0:
            raise ValueError("grid_carbon_intensity_kg_per_kwh must be >= 0")
        if self.water_liters_per_kwh < 0:
            raise ValueError("water_liters_per_kwh must be >= 0")
        if self.pue < 1.0:
            raise ValueError("pue must be >= 1.0")
        _validate01("hardware_utilization", self.hardware_utilization)
        _validate01("model_efficiency_gain_fraction", self.model_efficiency_gain_fraction)
        if self.annual_input_tokens_millions < 0:
            raise ValueError("annual_input_tokens_millions must be >= 0")
        if self.annual_output_tokens_millions < 0:
            raise ValueError("annual_output_tokens_millions must be >= 0")
        if self.input_price_usd_per_million_tokens < 0:
            raise ValueError("input_price_usd_per_million_tokens must be >= 0")
        if self.output_price_usd_per_million_tokens < 0:
            raise ValueError("output_price_usd_per_million_tokens must be >= 0")
        if self.inclusion_budget_usd_per_user_year <= 0:
            raise ValueError("inclusion_budget_usd_per_user_year must be > 0")
        if self.annual_users <= 0:
            raise ValueError("annual_users must be > 0")
        if self.embodied_emissions_mtco2e_year < 0:
            raise ValueError("embodied_emissions_mtco2e_year must be >= 0")


def _validate01(name: str, value: float) -> None:
    if not 0.0 <= float(value) <= 1.0:
        raise ValueError(f"{name} must be in [0, 1]")


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _ratio_excess(actual: float, target: float) -> float:
    if target <= 0:
        raise ValueError("target must be > 0")
    return _clamp01(actual / target - 1.0)


def separation_guard() -> dict[str, Any]:
    return {
        "label": ADJACENCY_TRACK_LABEL,
        "track": AI_COMPUTE_TRACK_LABEL,
        "hardgate_isolation": True,
        "toe_score_delta_allowed": False,
        "physics_claim_promotion_allowed": False,
        "commercial_price_guarantee_allowed": False,
        "message": (
            "Pillar 253 is an adjacent sustainability/access planning layer. "
            "Outputs are deterministic calculators for prioritization, not claims "
            "of guaranteed market outcomes."
        ),
    }


def effective_ai_energy_twh(s: AIComputeScenario) -> float:
    utilization_effective = max(0.25, s.hardware_utilization)
    efficiency_factor = 1.0 - 0.5 * s.model_efficiency_gain_fraction
    return s.ai_compute_twh_year * s.pue * efficiency_factor / utilization_effective


def annual_token_cost_usd(s: AIComputeScenario) -> float:
    return (
        s.annual_input_tokens_millions * s.input_price_usd_per_million_tokens
        + s.annual_output_tokens_millions * s.output_price_usd_per_million_tokens
    )


def annual_cost_per_user_usd(s: AIComputeScenario) -> float:
    return annual_token_cost_usd(s) / s.annual_users


def operational_emissions_mtco2e(s: AIComputeScenario) -> float:
    effective_intensity = s.grid_carbon_intensity_kg_per_kwh * (1.0 - s.renewable_matched_fraction)
    energy_kwh = effective_ai_energy_twh(s) * 1_000_000_000.0
    emissions_kg = energy_kwh * effective_intensity
    return emissions_kg / 1_000_000_000.0


def total_emissions_mtco2e(s: AIComputeScenario) -> float:
    return operational_emissions_mtco2e(s) + s.embodied_emissions_mtco2e_year


def water_withdrawal_billion_liters(s: AIComputeScenario) -> float:
    energy_kwh = effective_ai_energy_twh(s) * 1_000_000_000.0
    liters = energy_kwh * s.water_liters_per_kwh
    return liters / 1_000_000_000.0


def burden_gap_scores(s: AIComputeScenario) -> dict[str, float]:
    energy_gap = _ratio_excess(effective_ai_energy_twh(s), IEA_DATA_CENTER_TWH_2026_HIGH_CASE)
    carbon_intensity = s.grid_carbon_intensity_kg_per_kwh * (1.0 - s.renewable_matched_fraction)
    emissions_gap = _ratio_excess(carbon_intensity, TARGET_CLEAN_CARBON_INTENSITY_KG_PER_KWH)
    affordability_gap = _ratio_excess(
        annual_cost_per_user_usd(s),
        s.inclusion_budget_usd_per_user_year,
    )

    baseline_readiness = float(
        deployment_readiness_report(baseline_2026_scenario())["readiness_index"]
    )
    automation_readiness_gap = _clamp01(1.0 - baseline_readiness)

    access_gap = _clamp01(0.65 * affordability_gap + 0.35 * automation_readiness_gap)

    return {
        "energy_pressure_gap": energy_gap,
        "emissions_intensity_gap": emissions_gap,
        "affordability_gap": affordability_gap,
        "access_gap": access_gap,
        "automation_readiness_gap": automation_readiness_gap,
    }


def burden_index(s: AIComputeScenario) -> float:
    g = burden_gap_scores(s)
    return _clamp01(
        0.26 * g["energy_pressure_gap"]
        + 0.30 * g["emissions_intensity_gap"]
        + 0.28 * g["affordability_gap"]
        + 0.16 * g["access_gap"]
    )


def intervention_blueprint(
    s: AIComputeScenario,
    budget_usd: float,
) -> list[dict[str, float | str]]:
    if budget_usd < 0:
        raise ValueError("budget_usd must be >= 0")

    g = burden_gap_scores(s)
    weights = {
        "efficiency_distillation_and_serving": 0.40 * g["energy_pressure_gap"] + 0.20 * g["affordability_gap"],
        "carbon_aware_scheduling_and_ppas": 0.75 * g["emissions_intensity_gap"] + 0.10 * g["energy_pressure_gap"],
        "cooling_water_retrofit": 0.20 * g["energy_pressure_gap"] + 0.25 * g["emissions_intensity_gap"],
        "open_model_public_inference_layer": 0.60 * g["affordability_gap"] + 0.20 * g["access_gap"],
        "public_compute_credits_and_shared_infra": 0.60 * g["access_gap"] + 0.20 * g["affordability_gap"],
    }

    total = sum(weights.values())
    rows: list[dict[str, float | str]] = []
    for lever, w in weights.items():
        frac = 0.0 if total <= 0 or budget_usd == 0 else w / total
        rows.append(
            {
                "lever": lever,
                "impact_weight": w,
                "allocated_fraction": frac,
                "allocated_budget_usd": budget_usd * frac,
            }
        )
    rows.sort(key=lambda x: float(x["impact_weight"]), reverse=True)
    return rows


def baseline_ai_compute_scenario() -> AIComputeScenario:
    energy = global_energy_manifold(year=2026)
    renewable = float(energy["renewable_fraction_current"])

    return AIComputeScenario(
        ai_compute_twh_year=460.0,
        renewable_matched_fraction=min(1.0, renewable + 0.10),
        grid_carbon_intensity_kg_per_kwh=0.38,
        water_liters_per_kwh=1.8,
        pue=1.30,
        hardware_utilization=0.58,
        model_efficiency_gain_fraction=0.22,
        annual_input_tokens_millions=9_000_000.0,
        annual_output_tokens_millions=3_000_000.0,
        input_price_usd_per_million_tokens=0.75,
        output_price_usd_per_million_tokens=4.50,
        inclusion_budget_usd_per_user_year=15.0,
        annual_users=120_000_000.0,
        embodied_emissions_mtco2e_year=12.0,
    )


def roadmap_blueprint(
    target_readiness: float = 0.75,
    max_interventions: int = 6,
) -> dict[str, Any]:
    return solve_for_target_readiness(
        base_scenario=baseline_2026_scenario(),
        target_readiness=target_readiness,
        max_interventions=max_interventions,
    )


def pillar253_ai_compute_sustainability_access_report(
    intervention_budget_usd: float = 180_000_000_000.0,
) -> dict[str, Any]:
    scenario = baseline_ai_compute_scenario()
    return {
        "provenance": __provenance__,
        "separation_guard": separation_guard(),
        "baseline_scenario": scenario,
        "effective_ai_energy_twh": effective_ai_energy_twh(scenario),
        "annual_token_cost_usd": annual_token_cost_usd(scenario),
        "annual_cost_per_user_usd": annual_cost_per_user_usd(scenario),
        "operational_emissions_mtco2e": operational_emissions_mtco2e(scenario),
        "total_emissions_mtco2e": total_emissions_mtco2e(scenario),
        "water_withdrawal_billion_liters": water_withdrawal_billion_liters(scenario),
        "burden_gap_scores": burden_gap_scores(scenario),
        "burden_index": burden_index(scenario),
        "intervention_blueprint": intervention_blueprint(scenario, intervention_budget_usd),
        "automation_roadmap_blueprint": roadmap_blueprint(),
        "falsification_condition": (
            "FALSIFIED if pre-registered deployments repeatedly fail to reduce "
            "all three burden dimensions (energy/carbon, affordability, access) "
            "against baseline over matched demand periods."
        ),
    }


__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "AI_COMPUTE_TRACK_LABEL",
    "AIComputeScenario",
    "C_S",
    "IEA_DATA_CENTER_TWH_2024_HIGH",
    "IEA_DATA_CENTER_TWH_2024_LOW",
    "IEA_DATA_CENTER_TWH_2026_HIGH_CASE",
    "K_CS",
    "N_W",
    "PHI0",
    "TARGET_CLEAN_CARBON_INTENSITY_KG_PER_KWH",
    "__provenance__",
    "annual_cost_per_user_usd",
    "annual_token_cost_usd",
    "baseline_ai_compute_scenario",
    "burden_gap_scores",
    "burden_index",
    "effective_ai_energy_twh",
    "intervention_blueprint",
    "operational_emissions_mtco2e",
    "pillar253_ai_compute_sustainability_access_report",
    "roadmap_blueprint",
    "separation_guard",
    "total_emissions_mtco2e",
    "water_withdrawal_billion_liters",
]
