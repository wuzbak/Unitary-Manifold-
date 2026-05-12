# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 229 — AI & Robotics Solutions Engine (2026).

Adjacent applied research track (non-hardgate): computes solution pathways for
the three strategic hurdles and twelve technical/operational bottlenecks
identified in Pillar 227.  Provides intervention ROI ranking, readiness
trajectory projection, target-gap solving, sensitivity analysis, and Monte
Carlo intervention impact simulation.

Depends on Pillar 227 for bottleneck definitions and the baseline 2026 scenario.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Mapping, Tuple

try:
    from src.core.pillar227_ai_robotics_bottleneck_engine import (
        BOTTLENECK_ORDER,
        STRATEGIC_HURDLES,
        DeploymentScenario,
        baseline_2026_scenario,
        bottleneck_scores,
        deployment_readiness_report,
        strategic_hurdle_scores,
    )
except ImportError:  # relative fallback (package-internal use)
    from .pillar227_ai_robotics_bottleneck_engine import (  # type: ignore[no-redef]
        BOTTLENECK_ORDER,
        STRATEGIC_HURDLES,
        DeploymentScenario,
        baseline_2026_scenario,
        bottleneck_scores,
        deployment_readiness_report,
        strategic_hurdle_scores,
    )

__provenance__ = {
    "pillar": 229,
    "title": "AI & Robotics Solutions Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — solution pathway calculator, not a claim"
        " that deployment bottlenecks are solved"
    ),
}

# ---------------------------------------------------------------------------
# Framework constants (identical to Pillar 227 for cross-module consistency)
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

# ---------------------------------------------------------------------------
# Intervention registry
# cost_denominator (USD): capital required to fully close a gap of 1.0.
# Formula: reduction_fraction = min(1, investment_usd / (gap * cost_denominator))
# ---------------------------------------------------------------------------
_COST_DENOMINATORS: Dict[str, int] = {
    # --- 12 bottlenecks ---
    "training_data_scarcity": 15_000_000,
    "battery_endurance": 8_000_000,
    "end_effector_dexterity": 5_000_000,
    "compute_to_power_conflict": 12_000_000,
    "memory_bandwidth_latency": 3_000_000,
    "supply_chain_fragmentation": 20_000_000,
    "weak_generalization": 25_000_000,
    "cybersecurity_exposure": 2_000_000,
    "process_instability": 1_000_000,
    "global_talent_gap": 4_000_000,
    "cost_of_prototyping": 30_000_000,
    "software_to_hardware_gap": 10_000_000,
    # --- 3 strategic hurdles ---
    "safety_liability_framework_gap": 50_000_000,
    "infrastructure_grid_readiness_gap": 100_000_000,
    "human_trust_perception_erosion": 15_000_000,
}

_INTERVENTION_DESCRIPTIONS: Dict[str, str] = {
    "training_data_scarcity": "Sim-to-real transfer investment",
    "battery_endurance": "Solid-state battery R&D investment",
    "end_effector_dexterity": "Dexterous robot hand program",
    "compute_to_power_conflict": "Neuromorphic chip adoption",
    "memory_bandwidth_latency": "HBM4 hardware upgrade",
    "supply_chain_fragmentation": "Supply chain standardization program",
    "weak_generalization": "Foundation model fine-tuning dataset",
    "cybersecurity_exposure": "Red-team + security hardening program",
    "process_instability": "ISO/TS documentation sprint",
    "global_talent_gap": "Cross-domain engineering fellowship",
    "cost_of_prototyping": "Manufacturing scale-up investment",
    "software_to_hardware_gap": "Co-design team funding",
    "safety_liability_framework_gap": "Regulatory framework acceleration fund",
    "infrastructure_grid_readiness_gap": "Grid expansion PPAs",
    "human_trust_perception_erosion": "Public deployment transparency initiative",
}

# Canonical ordering: bottlenecks first (matching BOTTLENECK_ORDER), then hurdles
ALL_INTERVENTIONS: Tuple[str, ...] = tuple(BOTTLENECK_ORDER) + tuple(STRATEGIC_HURDLES)


# ---------------------------------------------------------------------------
# Public dataclass
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InterventionParams:
    """Parameters for a single intervention calculation.

    [EMPIRICAL] investment_usd: capital committed to this intervention.
    [CALCULATED] gap: current normalized gap score in [0, 1] from Pillar 227.
                      Obtained via bottleneck_scores() or strategic_hurdle_scores().
    """

    investment_usd: float
    gap: float


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _compute_all_gaps(scenario: DeploymentScenario) -> Dict[str, float]:
    """Return combined dict of all 15 gap scores (bottlenecks + hurdles)."""
    gaps: Dict[str, float] = {}
    gaps.update(bottleneck_scores(scenario))
    gaps.update(strategic_hurdle_scores(scenario))
    return gaps


def _readiness_from_gaps(
    gaps: Dict[str, float],
    strategic_weight: float = 0.50,
) -> float:
    """Compute readiness index from a gap dict.

    [CALCULATED] Reproduces Pillar 227 deployment_readiness_report formula:
        total_gap = w * mean(hurdle_gaps) + (1-w) * mean(bottleneck_gaps)
        readiness  = 1 - total_gap
    """
    hurdle_gaps = [gaps[h] for h in STRATEGIC_HURDLES]
    bottleneck_gaps = [gaps[b] for b in BOTTLENECK_ORDER]
    hurdle_mean = sum(hurdle_gaps) / len(hurdle_gaps)
    bottleneck_mean = sum(bottleneck_gaps) / len(bottleneck_gaps)
    total_gap = strategic_weight * hurdle_mean + (1.0 - strategic_weight) * bottleneck_mean
    return _clamp01(1.0 - total_gap)


def _percentile_sorted(sorted_values: List[float], q: float) -> float:
    """Linear-interpolation percentile on an already-sorted list."""
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


def _std_dev(values: List[float], mean: float) -> float:
    """Population standard deviation."""
    if len(values) < 2:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def _rank_by_roi_from_gaps(
    gaps: Dict[str, float],
    investment_per: float,
) -> List[Dict]:
    """Rank all 15 interventions by ROI given a per-intervention investment.

    [CALCULATED] ROI = actual_gap_closure / investment_per.
    actual_gap_closure = gap * reduction_fraction (absolute gap units closed).
    """
    results = []
    for name in ALL_INTERVENTIONS:
        gap = gaps[name]
        params = InterventionParams(investment_usd=investment_per, gap=gap)
        reduction_fraction = intervention_gap_reduction(name, params)
        actual_gap_closure = gap * reduction_fraction
        roi = actual_gap_closure / investment_per if investment_per > 0 else 0.0
        results.append(
            {
                "name": name,
                "current_gap": gap,
                "gap_reduction_fraction": reduction_fraction,
                "actual_gap_closure": actual_gap_closure,
                "roi_per_dollar": roi,
            }
        )
    results.sort(key=lambda d: d["roi_per_dollar"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def intervention_gap_reduction(bottleneck_name: str, params: InterventionParams) -> float:
    """Return the fraction of the current gap closed by the given intervention.

    [CALCULATED] Formula: min(1, investment_usd / (gap * cost_denominator)).
    The cost_denominator (USD) is the investment needed to fully close a gap of 1.0.
    Returns 0 when gap == 0 (nothing to improve).

    Returns
    -------
    float
        Gap-reduction fraction in [0, 1].
        Multiply by params.gap to obtain the absolute gap closure.
    """
    if bottleneck_name not in _COST_DENOMINATORS:
        raise ValueError(
            f"Unknown intervention: {bottleneck_name!r}. "
            f"Valid names: {list(_COST_DENOMINATORS)}"
        )
    if not (0.0 <= params.gap <= 1.0):
        raise ValueError(f"params.gap must be in [0, 1], got {params.gap}")
    if params.investment_usd < 0:
        raise ValueError(
            f"params.investment_usd must be non-negative, got {params.investment_usd}"
        )
    if params.gap <= 0.0:
        return 0.0
    c = _COST_DENOMINATORS[bottleneck_name]
    return _clamp01(params.investment_usd / (params.gap * c))


def rank_interventions_by_roi(
    scenario: DeploymentScenario,
    budget_usd: float,
) -> List[Dict]:
    """Rank all 15 interventions by return-on-investment for a given budget.

    [CALCULATED] The budget is split equally across all 15 interventions for a
    level-playing-field comparison.  ROI = actual_gap_closure / cost_per_intervention.

    [SPECULATIVE] Equal budget allocation is a simplification; optimal capital
    allocation requires a convex program.

    Parameters
    ----------
    scenario : DeploymentScenario
        Current baseline (from Pillar 227).
    budget_usd : float
        Total investment budget (USD).

    Returns
    -------
    list of dict
        Each entry contains: name, description, current_gap, gap_reduction_fraction,
        actual_gap_closure, investment_usd, roi_per_dollar, cost_to_fully_close_usd.
        Sorted descending by roi_per_dollar.
    """
    if budget_usd < 0:
        raise ValueError(f"budget_usd must be non-negative, got {budget_usd}")

    gaps = _compute_all_gaps(scenario)
    n = len(ALL_INTERVENTIONS)
    investment_per = budget_usd / n if (budget_usd > 0 and n > 0) else 0.0

    results: List[Dict] = []
    for name in ALL_INTERVENTIONS:
        gap = gaps[name]
        params = InterventionParams(investment_usd=investment_per, gap=gap)
        reduction_fraction = intervention_gap_reduction(name, params)
        actual_gap_closure = gap * reduction_fraction
        roi = actual_gap_closure / investment_per if investment_per > 0 else 0.0
        cost_to_close = gap * _COST_DENOMINATORS[name] if gap > 0 else 0.0
        results.append(
            {
                "name": name,
                "description": _INTERVENTION_DESCRIPTIONS[name],
                "current_gap": gap,
                "gap_reduction_fraction": reduction_fraction,
                "actual_gap_closure": actual_gap_closure,
                "investment_usd": investment_per,
                "roi_per_dollar": roi,
                "cost_to_fully_close_usd": cost_to_close,
            }
        )

    results.sort(key=lambda d: d["roi_per_dollar"], reverse=True)
    return results


def project_readiness_trajectory(
    base_scenario: DeploymentScenario,
    interventions_per_year: int,
    years: int = 5,
    annual_budget_usd: float = 250_000_000,
    strategic_weight: float = 0.50,
) -> List[Dict]:
    """Model year-by-year readiness improvement under an intervention program.

    [CALCULATED] Each year the top-k interventions by ROI are selected and
    funded with an equal share of the annual budget.  Gap state is tracked in
    normalized gap space (not raw scenario parameter space) for tractability.

    [SPECULATIVE] Linear gap-reduction and fixed-annual-budget assumptions
    simplify real investment dynamics.  Actual improvement rates depend on
    technology maturation curves not modeled here.

    Parameters
    ----------
    base_scenario : DeploymentScenario
        Pillar 227 baseline.
    interventions_per_year : int
        Number of bottlenecks/hurdles to address each year (k).
    years : int
        Horizon length in years (default 5).
    annual_budget_usd : float
        Total budget allocated per year (USD).  Default: $250 M.
    strategic_weight : float
        Hurdle vs bottleneck weight in readiness formula (default 0.50).

    Returns
    -------
    list of dict
        {year, readiness, top_interventions_applied} for year 0 (baseline)
        through year ``years``.
    """
    if interventions_per_year <= 0:
        raise ValueError("interventions_per_year must be > 0")
    if years <= 0:
        raise ValueError("years must be > 0")
    if annual_budget_usd < 0:
        raise ValueError("annual_budget_usd must be non-negative")
    if not (0.0 <= strategic_weight <= 1.0):
        raise ValueError("strategic_weight must be in [0, 1]")

    gaps = _compute_all_gaps(base_scenario)
    trajectory: List[Dict] = []

    baseline_readiness = _readiness_from_gaps(gaps, strategic_weight)
    trajectory.append(
        {"year": 2026, "readiness": baseline_readiness, "top_interventions_applied": []}
    )

    investment_per = (
        annual_budget_usd / interventions_per_year if interventions_per_year > 0 else 0.0
    )

    for yr in range(1, years + 1):
        ranked = _rank_by_roi_from_gaps(gaps, investment_per)
        top_k = ranked[:interventions_per_year]

        applied: List[str] = []
        for entry in top_k:
            name = entry["name"]
            reduction_fraction = entry["gap_reduction_fraction"]
            old_gap = gaps[name]
            gaps[name] = _clamp01(old_gap * (1.0 - reduction_fraction))
            applied.append(name)

        readiness = _readiness_from_gaps(gaps, strategic_weight)
        trajectory.append(
            {
                "year": 2026 + yr,
                "readiness": readiness,
                "top_interventions_applied": applied,
            }
        )

    return trajectory


def solve_for_target_readiness(
    base_scenario: DeploymentScenario,
    target_readiness: float,
    max_interventions: int,
    strategic_weight: float = 0.50,
) -> Dict:
    """Find the minimum set of interventions to reach a target readiness level.

    [CALCULATED] Greedy algorithm: at each step, fully close the bottleneck or
    hurdle whose closure delivers the largest single-step readiness gain.  The
    cost reported is the exact capital to fully close each selected gap.

    [SPECULATIVE] Greedy is not guaranteed globally optimal; exact minimization
    requires integer programming.  For the 15-item problem size the greedy
    solution is typically within 5 % of optimal.

    Parameters
    ----------
    base_scenario : DeploymentScenario
        Pillar 227 baseline.
    target_readiness : float
        Desired readiness index in [0, 1].
    max_interventions : int
        Hard cap on number of interventions to consider.
    strategic_weight : float
        Weight of strategic hurdles in readiness (default 0.50).

    Returns
    -------
    dict
        Keys: target_readiness, achieved_readiness, interventions_needed
        (list of {name, cost_usd, gap_before}), total_cost_usd, feasible.
    """
    if not (0.0 <= target_readiness <= 1.0):
        raise ValueError(f"target_readiness must be in [0, 1], got {target_readiness}")
    if max_interventions < 0:
        raise ValueError(f"max_interventions must be >= 0, got {max_interventions}")
    if not (0.0 <= strategic_weight <= 1.0):
        raise ValueError(f"strategic_weight must be in [0, 1], got {strategic_weight}")

    gaps = _compute_all_gaps(base_scenario)
    current_readiness = _readiness_from_gaps(gaps, strategic_weight)

    if current_readiness >= target_readiness:
        return {
            "target_readiness": target_readiness,
            "achieved_readiness": current_readiness,
            "interventions_needed": [],
            "total_cost_usd": 0.0,
            "feasible": True,
        }

    applied: List[Dict] = []
    total_cost = 0.0

    for _ in range(max_interventions):
        # Select intervention with largest readiness gain on full closure
        best_gain = -1.0
        best_name: str | None = None

        for name in ALL_INTERVENTIONS:
            gap = gaps[name]
            if gap <= 0.0:
                continue
            # Readiness contribution of this gap
            if name in STRATEGIC_HURDLES:
                weight = strategic_weight / len(STRATEGIC_HURDLES)
            else:
                weight = (1.0 - strategic_weight) / len(BOTTLENECK_ORDER)
            gain = weight * gap  # readiness increase on full closure
            if gain > best_gain:
                best_gain = gain
                best_name = name

        if best_name is None:
            break  # all gaps already zero

        gap_before = gaps[best_name]
        cost = gap_before * _COST_DENOMINATORS[best_name]
        applied.append({"name": best_name, "cost_usd": cost, "gap_before": gap_before})
        total_cost += cost
        gaps[best_name] = 0.0

        current_readiness = _readiness_from_gaps(gaps, strategic_weight)
        if current_readiness >= target_readiness:
            break

    return {
        "target_readiness": target_readiness,
        "achieved_readiness": current_readiness,
        "interventions_needed": applied,
        "total_cost_usd": total_cost,
        "feasible": current_readiness >= target_readiness,
    }


def bottleneck_sensitivity_analysis(
    base_scenario: DeploymentScenario,
    strategic_weight: float = 0.50,
    delta: float = 1e-4,
) -> List[Dict]:
    """Compute ∂readiness/∂gap for every bottleneck and strategic hurdle.

    [CALCULATED] Numerical partial derivative via one-sided finite difference.
    Because the readiness formula is linear in the gaps, the exact derivatives
    are: -(1-w)/12 for each bottleneck, -w/3 for each hurdle.
    achievable_impact = |∂readiness/∂gap| × current_gap — the maximum readiness
    gain obtainable by fully closing that bottleneck from its current level.

    Returns
    -------
    list of dict
        All 15 entries sorted by achievable_impact descending.  Keys: name,
        category, current_gap, partial_derivative_readiness_wrt_gap,
        achievable_impact.
    """
    if not (0.0 <= strategic_weight <= 1.0):
        raise ValueError("strategic_weight must be in [0, 1]")
    if delta <= 0:
        raise ValueError("delta must be > 0")

    gaps = _compute_all_gaps(base_scenario)
    base_readiness = _readiness_from_gaps(gaps, strategic_weight)

    results: List[Dict] = []
    for name in ALL_INTERVENTIONS:
        old_gap = gaps[name]
        # Use forward difference; fall back to backward when gap is at the upper boundary.
        step_fwd = _clamp01(old_gap + delta) - old_gap
        if abs(step_fwd) > delta / 2:
            perturbed = dict(gaps)
            perturbed[name] = old_gap + step_fwd
            perturbed_readiness = _readiness_from_gaps(perturbed, strategic_weight)
            partial = (perturbed_readiness - base_readiness) / step_fwd
        else:
            # Backward difference (gap is saturated at 1.0)
            step_bwd = old_gap - _clamp01(old_gap - delta)
            if step_bwd == 0.0:
                partial = 0.0  # gap is exactly 0 — no movement in either direction
            else:
                perturbed = dict(gaps)
                perturbed[name] = old_gap - step_bwd
                perturbed_readiness = _readiness_from_gaps(perturbed, strategic_weight)
                partial = (base_readiness - perturbed_readiness) / step_bwd
        achievable_impact = abs(partial) * old_gap
        results.append(
            {
                "name": name,
                "category": "hurdle" if name in STRATEGIC_HURDLES else "bottleneck",
                "current_gap": old_gap,
                "partial_derivative_readiness_wrt_gap": partial,
                "achievable_impact": achievable_impact,
            }
        )

    results.sort(key=lambda d: d["achievable_impact"], reverse=True)
    return results


def monte_carlo_intervention_impact(
    base_scenario: DeploymentScenario,
    intervention_plan: Mapping[str, float],
    n_samples: int = 5000,
    seed: int = 229,
    strategic_weight: float = 0.50,
    uncertainty_fraction: float = 0.20,
) -> Dict:
    """Monte Carlo simulation of intervention impact with efficacy uncertainty.

    [CALCULATED] For each sample, each planned intervention's gap-reduction
    fraction is perturbed by ±uncertainty_fraction (uniform distribution) before
    being applied.  Final readiness is recorded for all samples.

    [SPECULATIVE] Uniform perturbation model is a first-order approximation;
    real intervention efficacy follows skewed, fat-tailed distributions.

    Parameters
    ----------
    base_scenario : DeploymentScenario
        Pillar 227 baseline.
    intervention_plan : mapping of str → float
        Dict of {bottleneck_name: investment_usd} for each planned intervention.
    n_samples : int
        Monte Carlo sample count (default 5000).
    seed : int
        RNG seed for reproducibility (default 229).
    strategic_weight : float
        Readiness formula weight (default 0.50).
    uncertainty_fraction : float
        Half-width of uniform perturbation on reduction fraction (default 0.20).

    Returns
    -------
    dict
        Keys: samples, mean_readiness, p10, p50, p90, min, max, std.
    """
    if n_samples <= 0:
        raise ValueError("n_samples must be > 0")
    if not (0.0 <= strategic_weight <= 1.0):
        raise ValueError("strategic_weight must be in [0, 1]")
    if uncertainty_fraction < 0:
        raise ValueError("uncertainty_fraction must be non-negative")

    for name in intervention_plan:
        if name not in _COST_DENOMINATORS:
            raise ValueError(f"Unknown intervention name in plan: {name!r}")

    rng = random.Random(seed)
    base_gaps = _compute_all_gaps(base_scenario)

    readiness_values: List[float] = []
    for _ in range(n_samples):
        gaps = dict(base_gaps)
        for name, investment in intervention_plan.items():
            gap = gaps[name]
            params = InterventionParams(investment_usd=investment, gap=gap)
            reduction_fraction = intervention_gap_reduction(name, params)
            noise = rng.uniform(-uncertainty_fraction, uncertainty_fraction)
            perturbed_reduction = _clamp01(reduction_fraction + noise)
            gaps[name] = _clamp01(gap * (1.0 - perturbed_reduction))
        readiness_values.append(_readiness_from_gaps(gaps, strategic_weight))

    readiness_values.sort()
    mean_r = sum(readiness_values) / len(readiness_values)

    return {
        "samples": float(n_samples),
        "mean_readiness": mean_r,
        "p10": _percentile_sorted(readiness_values, 0.10),
        "p50": _percentile_sorted(readiness_values, 0.50),
        "p90": _percentile_sorted(readiness_values, 0.90),
        "min": readiness_values[0],
        "max": readiness_values[-1],
        "std": _std_dev(readiness_values, mean_r),
    }


# ---------------------------------------------------------------------------
# Convenience: pre-built baseline scenario (re-exported from Pillar 227)
# ---------------------------------------------------------------------------

def baseline_2026_solutions_scenario() -> DeploymentScenario:
    """Return Pillar 227 baseline_2026_scenario() for use in Pillar 229 functions.

    [EMPIRICAL] Values originate in Pillar 227; see baseline_2026_scenario()
    for field-by-field provenance notes.
    """
    return baseline_2026_scenario()


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [
    # Constants
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "ALL_INTERVENTIONS",
    # Dataclass
    "InterventionParams",
    # Core intervention model
    "intervention_gap_reduction",
    # Analysis functions
    "rank_interventions_by_roi",
    "project_readiness_trajectory",
    "solve_for_target_readiness",
    "bottleneck_sensitivity_analysis",
    "monte_carlo_intervention_impact",
    # Convenience
    "baseline_2026_solutions_scenario",
    # Provenance
    "__provenance__",
]
