# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar220_energy_manifold.py
======================================
Pillar 220 — Manifold Applied to Energy: Consumer to Civilization Scale.

Applies the Unitary Manifold φ-debt entropy accounting framework to energy
systems across scales — from individual households to the global civilization.

Key insight: energy waste is entropic debt (analogous to φ-debt in recycling/),
and the KK compactification geometry suggests a hierarchical scaling law for
efficiency gaps.  PHI0 ≈ 73.9% emerges as a natural thermodynamic efficiency
ceiling.  The hierarchy home → company → city → country → world follows a
self-similar KK tower with ratio N_W = 5.

**Epistemic status**: adjacent applied research track.  The φ-debt framing is
a geometric analogy; carbon and energy numbers are derived from IEA / EIA
public data and are genuine empirical constraints.
"""
from __future__ import annotations

import math
from typing import Any

__provenance__ = {
    "pillar": 220,
    "title": "Manifold Applied to Energy: Consumer to Civilization Scale",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": "ADJACENT RESEARCH TRACK (non-hardgate)",
    "data_sources": ["IEA World Energy Outlook 2023", "EIA 2023", "Energy Institute 2024"],
}

__all__ = [
    "N_W",
    "K_CS",
    "PHI0",
    "BRAIDED_SOUND_SPEED",
    "KWH_PER_JOULE",
    "WORLD_PRIMARY_ENERGY_EJ_2023",
    "US_HOUSEHOLD_KWH_YEAR",
    "GLOBAL_POPULATION_2026",
    "CO2_KG_PER_KWH_COAL",
    "CO2_KG_PER_KWH_GAS",
    "CO2_KG_PER_KWH_SOLAR",
    "CARNOT_LIMIT",
    "RENEWABLE_FRACTION_2023",
    "SCALE_NAMES",
    "household_phi_efficiency",
    "kk_efficiency_scaling",
    "energy_phi_debt",
    "city_energy_audit",
    "global_energy_manifold",
    "phi_pathway_to_sustainability",
    "appliance_phi_audit",
    "pillar220_summary",
]

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
PHI0: float = 0.739085                     # radion attractor / φ₀ efficiency ceiling
BRAIDED_SOUND_SPEED: float = 12 / 37      # c_s from (5,7) braid resonance

KWH_PER_JOULE: float = 1 / 3.6e6          # 1 kWh = 3.6 MJ
WORLD_PRIMARY_ENERGY_EJ_2023: float = 620.0  # EJ/year (IEA / Energy Institute 2023)
US_HOUSEHOLD_KWH_YEAR: float = 10_500.0   # US avg household electricity (EIA 2023)
GLOBAL_POPULATION_2026: float = 8.1e9
CO2_KG_PER_KWH_COAL: float = 0.82         # kg CO₂ per kWh — coal generation
CO2_KG_PER_KWH_GAS: float = 0.49          # kg CO₂ per kWh — natural gas
CO2_KG_PER_KWH_SOLAR: float = 0.041       # kg CO₂ per kWh — utility solar (LCA)
CARNOT_LIMIT: float = 1.0                  # theoretical maximum efficiency
RENEWABLE_FRACTION_2023: float = 0.154    # ~15.4 % incl. hydro (Energy Institute 2024)

# KK tower scale names (level 0 → 4)
SCALE_NAMES: dict[int, str] = {
    0: "household",
    1: "company",
    2: "city",
    3: "country",
    4: "world",
}

# Baseline useful-energy fractions by home type (empirical estimates)
_HOME_USEFUL_FRACTION: dict[str, float] = {
    "average_us": 0.55,        # ~55 % ends as useful work; rest is waste heat
    "efficient": 0.72,         # near-passive-house standard
    "inefficient": 0.38,       # older stock, poor insulation
    "passive_house": 0.82,     # exceeds PHI0 ceiling — anomalous
}

# Approximate CO₂ intensity of US grid (kg per kWh, 2023 mixed grid)
_US_GRID_CO2_KG_KWH: float = 0.386


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def household_phi_efficiency(
    annual_kwh: float,
    home_type: str = "average_us",
) -> dict[str, Any]:
    """Compute the φ-efficiency of a household.

    Compares the fraction of energy that becomes useful work against the PHI0
    ceiling (≈ 73.9 %).  Energy above the waste floor is φ-debt.

    Parameters
    ----------
    annual_kwh : float
        Total electricity consumed in kWh per year.
    home_type : str
        One of 'average_us', 'efficient', 'inefficient', 'passive_house'.

    Returns
    -------
    dict with keys:
        total_kwh            float
        useful_fraction_estimate float
        phi_debt_kwh         float   — waste above PHI0 floor
        phi_debt_fraction    float   — phi_debt / total
        co2_kg               float   — annual CO₂ from grid electricity
        recommendations      list[str]
    """
    if annual_kwh < 0:
        raise ValueError("annual_kwh must be non-negative")

    useful_frac = _HOME_USEFUL_FRACTION.get(home_type, _HOME_USEFUL_FRACTION["average_us"])
    waste_frac = 1.0 - useful_frac

    # φ-debt = energy consumed beyond what PHI0 efficiency would waste
    phi_floor_waste_frac = 1.0 - PHI0          # ≈ 0.261
    phi_debt_frac = max(0.0, waste_frac - phi_floor_waste_frac)
    phi_debt_kwh = annual_kwh * phi_debt_frac
    co2_kg = annual_kwh * _US_GRID_CO2_KG_KWH

    recs: list[str] = []
    if useful_frac < PHI0:
        recs.append("Insulation upgrades could close the φ-debt gap by 15–30 %.")
    if annual_kwh > US_HOUSEHOLD_KWH_YEAR * 1.2:
        recs.append("Usage is 20 %+ above US average — audit high-draw appliances.")
    if home_type == "inefficient":
        recs.append("Heat-pump retrofit would raise useful fraction toward PHI0 ceiling.")
    if home_type == "passive_house":
        recs.append("Already exceeds PHI0 ceiling — φ-debt is negligible.")
    if not recs:
        recs.append("Performance is near the PHI0 ceiling — focus on renewable sourcing.")

    return {
        "total_kwh": annual_kwh,
        "useful_fraction_estimate": useful_frac,
        "phi_debt_kwh": phi_debt_kwh,
        "phi_debt_fraction": phi_debt_frac,
        "co2_kg": co2_kg,
        "recommendations": recs,
    }


def kk_efficiency_scaling(scale_level: int) -> dict[str, Any]:
    """KK tower efficiency model.

    At scale level n, the efficiency ceiling is PHI0^(1 + 1/n) for n ≥ 1,
    and PHI0 at level 0 (individual household).  The exponent reflects the
    additional coordination overhead that appears in a KK tower.

    Parameters
    ----------
    scale_level : int
        0 = household, 1 = company, 2 = city, 3 = country, 4 = world.

    Returns
    -------
    dict with keys:
        scale_name          str
        efficiency_ceiling  float   — value in (0, 1]
        phi_debt_fraction   float   — 1 - efficiency_ceiling
    """
    if scale_level not in SCALE_NAMES:
        raise ValueError(f"scale_level must be 0–4, got {scale_level}")

    # Each additional scale level multiplies efficiency by PHI0 (self-similar KK tower).
    eff = PHI0 ** (scale_level + 1)

    return {
        "scale_name": SCALE_NAMES[scale_level],
        "efficiency_ceiling": eff,
        "phi_debt_fraction": 1.0 - eff,
    }


def energy_phi_debt(consumed_joules: float, useful_joules: float) -> dict[str, Any]:
    """Compute φ-debt (entropy) from energy waste.

    Parameters
    ----------
    consumed_joules : float
        Total energy consumed (J).
    useful_joules : float
        Energy that became useful work (J).  Must be ≤ consumed_joules.

    Returns
    -------
    dict with keys:
        phi_debt_joules     float
        phi_debt_fraction   float
        co2_equivalent_kg   float   — rough CO₂ at average grid intensity
    """
    if consumed_joules < 0:
        raise ValueError("consumed_joules must be non-negative")
    if useful_joules < 0:
        raise ValueError("useful_joules must be non-negative")
    if useful_joules > consumed_joules:
        raise ValueError("useful_joules cannot exceed consumed_joules")

    waste_j = consumed_joules - useful_joules
    fraction = waste_j / consumed_joules if consumed_joules > 0 else 0.0

    # CO₂ estimate using average grid intensity (0.386 kg/kWh)
    waste_kwh = waste_j * KWH_PER_JOULE
    co2_kg = waste_kwh * _US_GRID_CO2_KG_KWH

    return {
        "phi_debt_joules": waste_j,
        "phi_debt_fraction": fraction,
        "co2_equivalent_kg": co2_kg,
    }


def city_energy_audit(
    population: float,
    kwh_per_capita_year: float = 6_000.0,
) -> dict[str, Any]:
    """City-scale energy audit.

    Parameters
    ----------
    population : float
        City population.
    kwh_per_capita_year : float
        Annual electricity consumption per person (kWh).  Default 6 000 kWh
        (global urban average; US cities ~12 000).

    Returns
    -------
    dict with keys:
        total_kwh_year        float
        total_ej_year         float
        phi_debt_ej           float
        renewable_target_fraction float
        kk_tower_level        int
    """
    total_kwh = population * kwh_per_capita_year
    total_j = total_kwh / KWH_PER_JOULE
    total_ej = total_j / 1e18

    city_eff = kk_efficiency_scaling(2)["efficiency_ceiling"]
    phi_debt_ej = total_ej * (1.0 - city_eff)

    # Renewable target: close the φ-debt gap by 2050 (linear schedule)
    renewable_target = min(1.0, RENEWABLE_FRACTION_2023 + (1.0 - city_eff) * 0.5)

    return {
        "total_kwh_year": total_kwh,
        "total_ej_year": total_ej,
        "phi_debt_ej": phi_debt_ej,
        "renewable_target_fraction": renewable_target,
        "kk_tower_level": 2,
    }


def global_energy_manifold(year: int = 2026) -> dict[str, Any]:
    """Global energy analysis using IEA / Energy Institute data.

    Parameters
    ----------
    year : int
        Reference year (default 2026; data anchored to 2023 IEA values with
        linear extrapolation at +1.5 % per year).

    Returns
    -------
    dict with keys:
        world_primary_ej          float
        renewable_fraction_current float
        phi_ceiling_ej            float
        phi_debt_ej               float
        gap_to_phi_ceiling_ej     float
        co2_gt_year               float
        recommendations           list[str]
    """
    # Linear growth from 2023 baseline
    years_ahead = max(0, year - 2023)
    world_ej = WORLD_PRIMARY_ENERGY_EJ_2023 * (1.015 ** years_ahead)

    # Renewable fraction grows ~0.7 pp/year (Energy Institute trend 2018-2023)
    renew_frac = min(1.0, RENEWABLE_FRACTION_2023 + 0.007 * years_ahead)

    # φ-ceiling: world-scale KK tower level = 4
    world_level = kk_efficiency_scaling(4)
    phi_ceiling_eff = world_level["efficiency_ceiling"]
    phi_ceiling_ej = world_ej * phi_ceiling_eff
    phi_debt_ej = world_ej * (1.0 - phi_ceiling_eff)

    gap_ej = max(0.0, phi_debt_ej - (world_ej * (1.0 - renew_frac) * 0.3))

    # CO₂: fossil fraction × 80 kg/GJ average intensity → Gt/year
    fossil_frac = 1.0 - renew_frac
    co2_gt = world_ej * 1e18 * fossil_frac * 70e-12   # 70 kg CO₂/GJ fossil avg

    recs = [
        "Scale renewable capacity at ≥ 0.7 pp/year to track PHI0 pathway.",
        "Industrial electrification closes the largest single φ-debt sector.",
        "Building retrofit programs target the household KK level (level 0).",
        "Green hydrogen bridges the gap where direct electrification is hard.",
    ]

    return {
        "world_primary_ej": world_ej,
        "renewable_fraction_current": renew_frac,
        "phi_ceiling_ej": phi_ceiling_ej,
        "phi_debt_ej": phi_debt_ej,
        "gap_to_phi_ceiling_ej": gap_ej,
        "co2_gt_year": co2_gt,
        "recommendations": recs,
    }


def phi_pathway_to_sustainability(target_year: int = 2050) -> dict[str, Any]:
    """Compute the φ-debt reduction trajectory needed to reach PHI0 by target_year.

    Starting from 2026 baseline, computes the required annual fractional
    reduction in φ-debt to arrive at or below the PHI0 efficiency ceiling.

    Parameters
    ----------
    target_year : int
        Year by which global energy efficiency should reach the PHI0 ceiling.

    Returns
    -------
    dict with keys:
        start_year              int
        target_year             int
        years_available         int
        yearly_reduction_fraction float
        technology_mix          dict[str, float]
        feasibility_score       float   — 0 (impossible) to 1 (easily achieved)
    """
    start_year = 2026
    if target_year <= start_year:
        target_year = start_year + 1

    years = target_year - start_year
    baseline = global_energy_manifold(start_year)
    current_phi_debt_frac = baseline["phi_debt_ej"] / baseline["world_primary_ej"]

    # Target: reduce phi_debt_frac to the world-level KK floor
    target_frac = kk_efficiency_scaling(4)["phi_debt_fraction"]
    gap = max(0.0, current_phi_debt_frac - target_frac)

    # Required annual exponential reduction
    if gap > 0 and years > 0:
        yearly_reduction = 1.0 - ((target_frac / current_phi_debt_frac) ** (1.0 / years))
    else:
        yearly_reduction = 0.0

    tech_mix = {
        "solar_wind": 0.45,
        "efficiency_buildings": 0.20,
        "industrial_electrification": 0.18,
        "green_hydrogen": 0.10,
        "nuclear": 0.07,
    }

    # Feasibility heuristic: 2 % annual reduction is historically achievable (~0.5),
    # 1 % is easy (0.8), 4 %+ is hard (0.1)
    if yearly_reduction <= 0:
        feasibility = 1.0
    elif yearly_reduction <= 0.01:
        feasibility = 0.90
    elif yearly_reduction <= 0.02:
        feasibility = 0.70
    elif yearly_reduction <= 0.03:
        feasibility = 0.50
    elif yearly_reduction <= 0.04:
        feasibility = 0.30
    else:
        feasibility = max(0.05, 0.30 - (yearly_reduction - 0.04) * 5)

    return {
        "start_year": start_year,
        "target_year": target_year,
        "years_available": years,
        "yearly_reduction_fraction": yearly_reduction,
        "technology_mix": tech_mix,
        "feasibility_score": feasibility,
    }


def appliance_phi_audit(appliance_list: list[dict]) -> dict[str, Any]:
    """Audit appliances by their φ-debt (wasted energy).

    Parameters
    ----------
    appliance_list : list[dict]
        Each dict must have:
            name             str
            watts            float   — rated power
            hours_per_day    float
            efficiency_percent float  — 0–100

    Returns
    -------
    dict with keys:
        total_phi_debt_kwh_year float
        appliance_rankings      list[dict]   — sorted by phi_debt_kwh_year desc
        summary                 str
    """
    if not appliance_list:
        return {
            "total_phi_debt_kwh_year": 0.0,
            "appliance_rankings": [],
            "summary": "No appliances provided.",
        }

    ranked = []
    for item in appliance_list:
        watts = float(item.get("watts", 0))
        hours = float(item.get("hours_per_day", 0))
        eff = float(item.get("efficiency_percent", 100)) / 100.0
        eff = max(0.0, min(1.0, eff))

        kwh_year = watts * hours * 365 / 1_000
        waste_kwh = kwh_year * (1.0 - eff)

        ranked.append({
            "name": item.get("name", "unknown"),
            "total_kwh_year": kwh_year,
            "phi_debt_kwh_year": waste_kwh,
            "efficiency_fraction": eff,
        })

    ranked.sort(key=lambda x: x["phi_debt_kwh_year"], reverse=True)
    total = sum(a["phi_debt_kwh_year"] for a in ranked)

    return {
        "total_phi_debt_kwh_year": total,
        "appliance_rankings": ranked,
        "summary": (
            f"{len(ranked)} appliances audited; "
            f"total φ-debt = {total:.1f} kWh/year. "
            f"Top offender: {ranked[0]['name']} "
            f"({ranked[0]['phi_debt_kwh_year']:.1f} kWh/year wasted)."
        ),
    }


def pillar220_summary() -> dict[str, Any]:
    """Return key findings and status for Pillar 220."""
    global_data = global_energy_manifold(2026)
    pathway = phi_pathway_to_sustainability(2050)

    return {
        "pillar": 220,
        "title": "Manifold Applied to Energy: Consumer to Civilization Scale",
        "status": "ADJACENT RESEARCH TRACK (non-hardgate)",
        "phi_ceiling": PHI0,
        "phi_ceiling_percent": f"{PHI0 * 100:.2f}%",
        "world_primary_energy_ej_2023": WORLD_PRIMARY_ENERGY_EJ_2023,
        "world_primary_energy_ej_2026": round(global_data["world_primary_ej"], 1),
        "renewable_fraction_2026": round(global_data["renewable_fraction_current"], 3),
        "phi_debt_ej_2026": round(global_data["phi_debt_ej"], 1),
        "co2_gt_2026": round(global_data["co2_gt_year"], 2),
        "feasibility_2050": pathway["feasibility_score"],
        "kk_tower_levels": {k: kk_efficiency_scaling(k) for k in range(5)},
        "epistemic_note": (
            "PHI0 as an efficiency ceiling is a geometric analogy from the "
            "KK compactification, not a derived thermodynamic theorem. "
            "Carbon and energy numbers are IEA/EIA empirical data."
        ),
    }
