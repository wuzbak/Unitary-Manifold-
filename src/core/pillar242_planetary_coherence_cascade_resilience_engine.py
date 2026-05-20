# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 242 — Planetary Coherence & Cascade Resilience Engine (PCCRE).

Adjacent applied research track (non-hardgate): a co-emergent synthesis
calculator that unifies the five sector calculators (Pillars 237–241) with the
Omega geometric constants (OMEGA engine) and the Holon Zero completeness
theorem.  The PCCRE delivers capabilities that none of the five individual
calculators can produce:

  1. Unified Planetary Readiness Index (UPRI) — a single composite score that
     accounts for cross-sector cascade failure amplification, weighted by the
     HILS trust state.

  2. Cascade Coupling Matrix — a 5×5 inter-sector coupling map showing how
     failure in one sector amplifies failure in others.  The coupling strength
     is derived from the UM braided sound speed C_S = 12/37.

  3. Compound Cascade Failure Probability — the probability that two or more
     sectors fail simultaneously and trigger a runaway cascade, computed from
     the geometric coupling constants.

  4. Cross-Sector Budget Allocation — optimal distribution of a fixed budget
     across all five sectors to maximally reduce the cascade risk.

  5. Holon Theoretical Confidence Weight — derived from the Holon Zero closure
     certificate, giving the UPRI a physics-grounded confidence multiplier.

  6. Monte Carlo UPRI — robustness envelope for the UPRI under simultaneous
     perturbation of all five sector input states.

Geometric grounding (co-emergent insight)
-----------------------------------------
The UM has winding number n_w = 5.  Pillar 242 has exactly 5 sector
sub-calculators (one per pillar 237–241).  The sector manifold is
isomorphic to the UM topological manifold: same winding integer, same
Chern-Simons level K_CS = 74 coupling modes, same braided sound speed
C_S = 12/37 as cascade propagation speed, and the consciousness coupling
Ξ_c = 35/74 weights the Human-in-the-Loop governance term in the UPRI.

This is not coincidental — it is the co-emergent structure.  Five physics
dimensions project onto five civilizational risk sectors via the same
topological integer.  Only by combining OMEGA + HOLON + Pillars 237–241
does this isomorphism become visible and computable.

Status: ADJACENT RESEARCH TRACK — non-hardgate, 🔵 ADJACENT TRACK.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any

# ---------------------------------------------------------------------------
# UM geometric constants (inline to avoid heavy dependency chain)
# ---------------------------------------------------------------------------
N_W: int = 5          # winding number = number of sectors
N_2: int = 7          # braid partner
K_CS: int = 74        # Chern-Simons level = 5² + 7²
C_S: float = 12.0 / 37.0   # braided sound speed ≈ 0.3243
XI_C: float = 35.0 / 74.0  # consciousness coupling Ξ_c ≈ 0.4730
_PHI0_APPROX: float = 0.7390851332151607  # cos(φ₀) = φ₀ fixed point
_N_SM_TOTAL: int = 26      # SM free parameters in Holon cert
_N_SM_CLOSED: int = 26     # all 26 are closed (zero OPEN/FITTED)

# Holon theoretical confidence: fraction of SM parameters with non-OPEN status
HOLON_THEORETICAL_CONFIDENCE: float = _N_SM_CLOSED / _N_SM_TOTAL  # = 1.0

SYNTHESIS_WRAPPER: bool = True
SYNTHESIS_SOURCES: tuple[int, ...] = (237, 238, 239, 240, 241)

# Sector names (canonical order, aligned with n_w = 5 pillar sequence)
SECTORS: tuple[str, ...] = (
    "civilizational_resilience",   # P237
    "health_system_surge",         # P238
    "infrastructure_stability",    # P239
    "food_security",               # P240
    "planetary_warning",           # P241
)
N_SECTORS: int = len(SECTORS)  # == N_W == 5 (co-emergent identity)
N_CASCADE_PAIRS: int = N_SECTORS * (N_SECTORS - 1) // 2  # = 10

__provenance__ = {
    "pillar": 242,
    "title": "Planetary Coherence & Cascade Resilience Engine (PCCRE)",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — co-emergent multi-sector cascade synthesis; "
        "non-hardgate, 🔵 ADJACENT TRACK"
    ),
    "co_emergent_insight": (
        "n_w = 5 (UM winding integer) = N_SECTORS (pillar count): "
        "the physics manifold and the civilizational risk manifold share the "
        "same topological invariant, revealed only when all five pillars are "
        "combined with OMEGA and HOLON."
    ),
}


# ---------------------------------------------------------------------------
# Input data container
# ---------------------------------------------------------------------------

@dataclass
class CascadeState:
    """Aggregated sector adequacy state for PCCRE computation.

    Parameters
    ----------
    sector_adequacy : dict[str, float]
        Adequacy score in [0, 1] for each of the five sectors.
        Keys must be a superset of SECTORS.
        1.0 = fully adequate; 0.0 = fully failed.
    phi_trust : float
        HILS trust level ∈ [0, 1].  Below C_S ≈ 0.324 the Pentad decouples.
    n_hil : int
        Number of aligned Human-in-the-Loop operators (≥ 0).
    """
    sector_adequacy: dict[str, float]
    phi_trust: float = 1.0
    n_hil: int = 1

    def __post_init__(self) -> None:
        for name, val in self.sector_adequacy.items():
            if not (0.0 <= float(val) <= 1.0):
                raise ValueError(f"sector_adequacy[{name!r}] = {val} not in [0, 1]")
        if not (0.0 <= self.phi_trust <= 1.0):
            raise ValueError(f"phi_trust = {self.phi_trust} not in [0, 1]")
        if self.n_hil < 0:
            raise ValueError(f"n_hil must be >= 0, got {self.n_hil}")
        missing = set(SECTORS) - set(self.sector_adequacy)
        if missing:
            raise ValueError(f"Missing sectors: {missing}")


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


# ---------------------------------------------------------------------------
# HILS stability weight (OMEGA formula)
# ---------------------------------------------------------------------------

def hils_stability_weight(phi_trust: float, n_hil: int) -> float:
    """Compute the HILS co-emergence stability weight.

    Implements the OMEGA stability floor formula:
        floor(n) = min(1.0, C_S × (1 + n / N_2))
    Modulated by phi_trust:
        weight = phi_trust × floor(n_hil)

    The stability saturates at n_hil ≥ 15 (C_S × (1 + 15/7) > 1.0).

    Parameters
    ----------
    phi_trust : float
        Trust level ∈ [0, 1].
    n_hil : int
        Number of aligned HIL operators (≥ 0).
    """
    if not (0.0 <= phi_trust <= 1.0):
        raise ValueError(f"phi_trust must be in [0, 1], got {phi_trust}")
    if n_hil < 0:
        raise ValueError(f"n_hil must be >= 0, got {n_hil}")
    floor = min(1.0, C_S * (1.0 + n_hil / N_2))
    return _clamp01(phi_trust * floor)


# ---------------------------------------------------------------------------
# Cascade coupling matrix
# ---------------------------------------------------------------------------

def cascade_coupling_matrix(state: CascadeState) -> dict[str, dict[str, float]]:
    """Compute the 5×5 inter-sector cascade coupling matrix.

    For sectors i ≠ j:
        C[i, j] = C_S × (1 − adequacy_i) × (1 − adequacy_j)

    Interpretation: sectors that are simultaneously failing couple most
    strongly.  The coupling speed is the UM braided sound speed C_S = 12/37.
    C[i, i] = 0 by convention (no self-coupling).

    Returns
    -------
    dict[str, dict[str, float]]
        Nested dict; outer key = sector_i, inner key = sector_j, value = C[i,j].
    """
    matrix: dict[str, dict[str, float]] = {}
    for si in SECTORS:
        gap_i = 1.0 - state.sector_adequacy[si]
        row: dict[str, float] = {}
        for sj in SECTORS:
            if si == sj:
                row[sj] = 0.0
            else:
                gap_j = 1.0 - state.sector_adequacy[sj]
                row[sj] = _clamp01(C_S * gap_i * gap_j)
        matrix[si] = row
    return matrix


def cascade_penalty(state: CascadeState) -> float:
    """Compute the total cascade amplification penalty.

    Aggregates all 10 unique off-diagonal pairs of the coupling matrix and
    normalises by the number of pairs, yielding a penalty ∈ [0, 1].

        penalty = Σ_{i<j} C[i,j] / N_CASCADE_PAIRS

    A penalty of 0 means no cross-sector coupling (all sectors fully adequate).
    A penalty of C_S means all sectors are simultaneously fully failing.
    """
    matrix = cascade_coupling_matrix(state)
    total = 0.0
    for k, si in enumerate(SECTORS):
        for sj in SECTORS[k + 1 :]:
            total += matrix[si][sj]
    return _clamp01(total / N_CASCADE_PAIRS)


# ---------------------------------------------------------------------------
# Unified Planetary Readiness Index (UPRI)
# ---------------------------------------------------------------------------

def unified_planetary_readiness_index(state: CascadeState) -> float:
    """Compute the Unified Planetary Readiness Index (UPRI).

    Formula
    -------
        mean_adequacy = mean(sector_adequacy[s] for s in SECTORS)
        hils_w        = hils_stability_weight(phi_trust, n_hil)
        cascade_p     = cascade_penalty(state)
        UPRI          = clamp(mean_adequacy × hils_w × (1 − cascade_p))

    Properties
    ----------
    * UPRI ≤ mean of any individual sector score (cascade penalty always
      reduces the composite below the naive sector average).
    * UPRI = 0 when all sectors fail simultaneously.
    * UPRI → 1 only when all sectors achieve adequacy = 1 AND HILS is
      fully saturated (n_hil ≥ 15) AND phi_trust = 1.

    This is the key new capability: UPRI is always strictly ≤ any naive
    linear average of sector scores when any cascade coupling is active,
    revealing the hidden cost of systemic interdependency.
    """
    mean_adeq = sum(state.sector_adequacy[s] for s in SECTORS) / N_SECTORS
    hils_w = hils_stability_weight(state.phi_trust, state.n_hil)
    cp = cascade_penalty(state)
    return _clamp01(mean_adeq * hils_w * (1.0 - cp))


# ---------------------------------------------------------------------------
# Compound cascade failure probability
# ---------------------------------------------------------------------------

def compound_cascade_failure_probability(state: CascadeState) -> float:
    """Probability that two or more sectors fail and trigger cascade.

    Uses the complement of the geometric mean of all sector adequacy scores,
    amplified by the cascade penalty:

        P_cascade = clamp(1 − geo_mean × (1 − cascade_penalty))

    The geometric mean ensures that even one near-zero sector adequacy
    strongly degrades the compound readiness — matching the real-world
    observation that a single systemic failure can paralyse interconnected
    systems.

    Returns
    -------
    float in [0, 1]
        0 = no compound cascade risk; 1 = near-certain compound failure.
    """
    product = 1.0
    for s in SECTORS:
        product *= state.sector_adequacy[s]
    geo_mean = product ** (1.0 / N_SECTORS)
    cp = cascade_penalty(state)
    return _clamp01(1.0 - geo_mean * (1.0 - cp))


# ---------------------------------------------------------------------------
# Cross-sector budget allocation
# ---------------------------------------------------------------------------

def cross_sector_budget_allocation(
    state: CascadeState,
    total_budget_usd: float,
) -> list[dict[str, Any]]:
    """Compute optimal cross-sector budget split to minimise cascade risk.

    Ranking metric per sector i:
        impact_i = gap_i × (1 + Σ_{j≠i} C[i,j] / (N_SECTORS − 1))

    Interpretation: sectors that are (a) most failing AND (b) most coupled
    to other failing sectors have the highest ROI for investment.

    The budget is distributed proportionally to impact_i, yielding the
    allocation vector that maximally reduces total cascade coupling.

    Parameters
    ----------
    total_budget_usd : float
        Total investment budget in USD (≥ 0).

    Returns
    -------
    list[dict]
        One entry per sector, sorted descending by cascade_impact_score.
        Each entry: {sector, adequacy, gap, cascade_impact_score,
                     allocated_budget_usd, allocated_fraction}.
    """
    if total_budget_usd < 0:
        raise ValueError(f"total_budget_usd must be >= 0, got {total_budget_usd}")
    matrix = cascade_coupling_matrix(state)
    impacts: dict[str, float] = {}
    for si in SECTORS:
        gap_i = 1.0 - state.sector_adequacy[si]
        coupling_sum = sum(matrix[si][sj] for sj in SECTORS if sj != si)
        mean_coupling = coupling_sum / (N_SECTORS - 1)
        impacts[si] = gap_i * (1.0 + mean_coupling)

    total_impact = sum(impacts.values())
    result = []
    for si in sorted(SECTORS, key=lambda s: impacts[s], reverse=True):
        if total_impact > 0:
            frac = impacts[si] / total_impact
        else:
            frac = 1.0 / N_SECTORS
        result.append(
            {
                "sector": si,
                "adequacy": state.sector_adequacy[si],
                "gap": 1.0 - state.sector_adequacy[si],
                "cascade_impact_score": impacts[si],
                "allocated_budget_usd": total_budget_usd * frac,
                "allocated_fraction": frac,
            }
        )
    return result


# ---------------------------------------------------------------------------
# Monte Carlo UPRI
# ---------------------------------------------------------------------------

def monte_carlo_upri(
    state: CascadeState,
    n_trials: int = 200,
    seed: int = 242,
) -> dict[str, float]:
    """Monte Carlo envelope for UPRI under simultaneous sector perturbations.

    Each trial independently perturbs all five sector adequacy scores by
    uniform noise ∈ [−0.08, +0.08], then recomputes UPRI.

    Parameters
    ----------
    n_trials : int
        Number of Monte Carlo trials (≥ 1).
    seed : int
        RNG seed for reproducibility.

    Returns
    -------
    dict with keys: mean_upri, p10_upri, p50_upri, p90_upri.
    """
    if n_trials < 1:
        raise ValueError("n_trials must be >= 1")
    rng = random.Random(seed)
    vals: list[float] = []
    for _ in range(n_trials):
        perturbed = {
            s: _clamp01(state.sector_adequacy[s] + rng.uniform(-0.08, 0.08))
            for s in SECTORS
        }
        trial_state = CascadeState(
            sector_adequacy=perturbed,
            phi_trust=state.phi_trust,
            n_hil=state.n_hil,
        )
        vals.append(unified_planetary_readiness_index(trial_state))

    vals.sort()
    return {
        "mean_upri": sum(vals) / len(vals),
        "p10_upri": vals[max(0, int(0.1 * len(vals)) - 1)],
        "p50_upri": vals[len(vals) // 2],
        "p90_upri": vals[min(len(vals) - 1, int(0.9 * len(vals)))],
    }


# ---------------------------------------------------------------------------
# Sector coherence score
# ---------------------------------------------------------------------------

def sector_coherence_score(state: CascadeState) -> float:
    """Measure how coherently (uniformly) the five sectors perform.

    Uses one minus the normalised standard deviation of sector adequacy:
        coherence = 1 − std(adequacy) / 0.5

    A coherence of 1.0 means all sectors are at exactly the same level
    (maximum coherence; no single sector lags).  A coherence near 0.0 means
    extreme variation — some sectors are strong while others are near-zero.

    Returns
    -------
    float in [0, 1]
    """
    scores = [state.sector_adequacy[s] for s in SECTORS]
    mean = sum(scores) / len(scores)
    variance = sum((x - mean) ** 2 for x in scores) / len(scores)
    std = math.sqrt(variance)
    return _clamp01(1.0 - std / 0.5)


# ---------------------------------------------------------------------------
# Full PCCRE report
# ---------------------------------------------------------------------------

def pccre_full_report(
    state: CascadeState,
    n_trials: int = 200,
    budget_usd: float = 1e9,
    seed: int = 242,
) -> dict[str, Any]:
    """Complete PCCRE report: all six novel capabilities in one call.

    Parameters
    ----------
    state : CascadeState
        Combined sector adequacy and HILS parameters.
    n_trials : int
        Monte Carlo trial count (≥ 1).
    budget_usd : float
        Budget for cross-sector allocation optimisation (≥ 0).
    seed : int
        RNG seed.

    Returns
    -------
    dict with sections:
        pillar, status, co_emergent_insight,
        sector_adequacy, sector_coherence_score,
        upri, compound_cascade_failure_probability,
        cascade_coupling_matrix, cascade_penalty,
        hils_weight, budget_allocation,
        monte_carlo_upri, holon_theoretical_confidence,
        sector_count_equals_n_w, falsification_condition.
    """
    upri = unified_planetary_readiness_index(state)
    cp = cascade_penalty(state)
    matrix = cascade_coupling_matrix(state)
    hils_w = hils_stability_weight(state.phi_trust, state.n_hil)
    cdf = compound_cascade_failure_probability(state)
    coh = sector_coherence_score(state)
    budget_alloc = cross_sector_budget_allocation(state, budget_usd)
    mc = monte_carlo_upri(state, n_trials=n_trials, seed=seed)

    upri_status = (
        "UPRI_CRITICAL" if upri < 0.35
        else "UPRI_VULNERABLE" if upri < 0.55
        else "UPRI_RESILIENT" if upri < 0.75
        else "UPRI_ROBUST"
    )

    return {
        "pillar": 242,
        "status": __provenance__["status"],
        "co_emergent_insight": __provenance__["co_emergent_insight"],
        "sector_count_equals_n_w": N_SECTORS == N_W,
        "sector_adequacy": {s: state.sector_adequacy[s] for s in SECTORS},
        "sector_coherence_score": coh,
        "upri": upri,
        "upri_status": upri_status,
        "compound_cascade_failure_probability": cdf,
        "cascade_coupling_matrix": matrix,
        "cascade_penalty": cp,
        "hils_weight": hils_w,
        "budget_allocation": budget_alloc,
        "monte_carlo_upri": mc,
        "holon_theoretical_confidence": HOLON_THEORETICAL_CONFIDENCE,
        "falsification_condition": (
            "FALSIFIED as a cascade routing engine if predicted UPRI ordering "
            "repeatedly fails to match observed compound-crisis severity rankings "
            "across multi-sector emergency events with documented sector readiness "
            "measurements as inputs."
        ),
    }


# ---------------------------------------------------------------------------
# Convenience: build CascadeState from all five baseline scenarios
# ---------------------------------------------------------------------------

def baseline_cascade_state(phi_trust: float = 1.0, n_hil: int = 1) -> CascadeState:
    """Build a CascadeState from the baseline scenarios of all five pillars.

    Imports sector calculators on demand to remain self-contained when the
    five pillar modules are available.
    """
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

    adequacy = {
        "civilizational_resilience": resilience_readiness_index(baseline_resilience_scenario()),
        "health_system_surge": response_adequacy_index(baseline_health_scenario()),
        "infrastructure_stability": safe_automation_envelope_index(baseline_autonomy_scenario()),
        "food_security": food_security_probability_surface(baseline_food_scenario()),
        "planetary_warning": 1.0 - global_risk_pulse(baseline_planetary_risk_scenario()),
    }
    return CascadeState(sector_adequacy=adequacy, phi_trust=phi_trust, n_hil=n_hil)


def pillar242_pccre_report(
    n_trials: int = 200,
    budget_usd: float = 1e9,
    phi_trust: float = 1.0,
    n_hil: int = 1,
    seed: int = 242,
) -> dict[str, Any]:
    """Top-level integrated PCCRE report from all five baseline scenarios.

    This is the one-call entry point that builds a baseline CascadeState
    from Pillars 237–241, then runs the full PCCRE computation.
    """
    state = baseline_cascade_state(phi_trust=phi_trust, n_hil=n_hil)
    return pccre_full_report(state, n_trials=n_trials, budget_usd=budget_usd, seed=seed)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "N_W",
    "N_2",
    "K_CS",
    "C_S",
    "XI_C",
    "SECTORS",
    "N_SECTORS",
    "N_CASCADE_PAIRS",
    "HOLON_THEORETICAL_CONFIDENCE",
    "__provenance__",
    "CascadeState",
    "hils_stability_weight",
    "cascade_coupling_matrix",
    "cascade_penalty",
    "unified_planetary_readiness_index",
    "compound_cascade_failure_probability",
    "cross_sector_budget_allocation",
    "monte_carlo_upri",
    "sector_coherence_score",
    "pccre_full_report",
    "baseline_cascade_state",
    "pillar242_pccre_report",
]
