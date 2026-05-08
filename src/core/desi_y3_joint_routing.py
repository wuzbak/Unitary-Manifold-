# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
desi_y3_joint_routing.py — DESI Year 3 joint w₀-wₐ routing with χ² ellipse
analysis and explicit PASS/TENSION/FALSIFIED verdicts (v10.30).

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
Extends desi_year3_monitor.py with:
  1. Joint w₀-wₐ confidence ellipse routing using a 2D χ² statistic.
  2. Scenario analysis across 9 realistic Y3 scenarios.
  3. 30-day integration protocol with explicit downstream update targets.
  4. Falsification probability forecast as a function of σ_wₐ improvement.

UM PREDICTIONS:
  w₀ = −1 + (2/3)(12/37)² = −0.9302   (braided KK zero-mode)
  wₐ = 0                               (frozen GW-stabilised radion)

DESI DR2 BASELINE (arXiv:2503.14738, 2025):
  w₀ = −0.838 ± 0.072  →  UM tension 1.28σ  ✅
  wₐ = −0.62 ± 0.30    →  UM tension 2.07σ  ⚠️ OPEN TENSION

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

from src.core.desi_year3_monitor import (
    DESI_DR2,
    UM_PREDICTION,
    route_desi_y3,
    routing_decision,
    tension_from_measurement,
)

__all__ = [
    "Y3_SCENARIOS",
    "DOWNSTREAM_UPDATE_TARGETS",
    "chi2_joint",
    "joint_routing_decision",
    "scenario_analysis",
    "falsification_probability_forecast",
    "thirty_day_integration_protocol",
    "y3_full_routing_report",
]

# ---------------------------------------------------------------------------
# Pre-defined DESI Y3 scenarios (not yet published; bracketing the space)
# ---------------------------------------------------------------------------

#: Nine realistic Y3 scenarios covering PASS / TENSION / FALSIFIED space.
Y3_SCENARIOS: List[Dict[str, object]] = [
    {
        "name": "Y3-S1: tension resolved",
        "w0": -0.93,
        "wa": -0.10,
        "sigma_w0": 0.060,
        "sigma_wa": 0.18,
        "description": "wₐ uncertainty shrinks; central value moves toward 0",
    },
    {
        "name": "Y3-S2: tension maintained",
        "w0": -0.84,
        "wa": -0.45,
        "sigma_w0": 0.060,
        "sigma_wa": 0.20,
        "description": "Central value ≈ Y1; precision improved → 2.25σ tension",
    },
    {
        "name": "Y3-S3: tension deepens (near falsification)",
        "w0": -0.82,
        "wa": -0.60,
        "sigma_w0": 0.055,
        "sigma_wa": 0.18,
        "description": "Y1 central value confirmed with tighter Y3 error bars → >3σ",
    },
    {
        "name": "Y3-S4: ΛCDM consistent",
        "w0": -0.98,
        "wa": 0.05,
        "sigma_w0": 0.060,
        "sigma_wa": 0.20,
        "description": "Y3 moves toward ΛCDM; UM wₐ=0 fully consistent",
    },
    {
        "name": "Y3-S5: w0 tension emerges",
        "w0": -0.78,
        "wa": -0.30,
        "sigma_w0": 0.050,
        "sigma_wa": 0.20,
        "description": "w₀ tension increases; wₐ remains marginal",
    },
    {
        "name": "Y3-S6: falsification (3.2σ wₐ)",
        "w0": -0.83,
        "wa": -0.64,
        "sigma_w0": 0.060,
        "sigma_wa": 0.20,
        "description": "Confirmed Y1 central value; 3.2σ — UM wₐ=0 excluded",
    },
    {
        "name": "Y3-S7: large statistical fluctuation resolved",
        "w0": -0.95,
        "wa": 0.00,
        "sigma_w0": 0.065,
        "sigma_wa": 0.22,
        "description": "wₐ = 0 exactly; Y1 was a fluctuation",
    },
    {
        "name": "Y3-S8: moderate tension (2.4σ)",
        "w0": -0.85,
        "wa": -0.48,
        "sigma_w0": 0.058,
        "sigma_wa": 0.20,
        "description": "Persistent tension just below falsification threshold",
    },
    {
        "name": "Y3-S9: worst case (4σ)",
        "w0": -0.82,
        "wa": -0.72,
        "sigma_w0": 0.055,
        "sigma_wa": 0.18,
        "description": "Strong Y3 evidence for wₐ ≠ 0 at 4σ — clear falsification",
    },
]

#: Targets that MUST be updated within 30 days of DESI Y3 publication.
DOWNSTREAM_UPDATE_TARGETS: List[Dict[str, str]] = [
    {
        "artifact": "src/core/desi_year3_monitor.py",
        "update": "Add DESI_Y3 dict; call update_with_new_data(); update monitoring_report()",
    },
    {
        "artifact": "3-FALSIFICATION/OBSERVATION_TRACKER.md",
        "update": "Update P4 row: status, sigma-level, date; update G3 gap row",
    },
    {
        "artifact": "docs/CLAIM_MASTER_BOARD.md",
        "update": "Update T1 tension row: routing verdict, σ-level, last_updated",
    },
    {
        "artifact": "docs/TRUTH_LAYER.md",
        "update": "Update Section 3 T1 with Y3 tension value and routing decision",
    },
    {
        "artifact": "docs/GATEKEEPER_SUMMARY.md",
        "update": "Update Part 5 TENSION table with Y3 routing",
    },
    {
        "artifact": "docs/WAVE_CHANGELOG.md",
        "update": "Add Y3 integration wave entry with routing verdict",
    },
    {
        "artifact": "src/core/canonical_falsifier_evidence_feed.py",
        "update": "Sync DESI tension level; update wₐ falsification status",
    },
]


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def chi2_joint(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
    rho: float = 0.0,
) -> Dict[str, float]:
    """Compute 2D χ² distance between UM prediction and observed CPL point.

    Assumes a 2D Gaussian likelihood (optionally with correlation ρ).

    χ² = (Δw₀/σ_{w₀})² + (Δwₐ/σ_{wₐ})² − 2ρ·(Δw₀/σ_{w₀})·(Δwₐ/σ_{wₐ})
         ─────────────────────────────────────────────────────────────────────
                                   1 − ρ²

    Parameters
    ----------
    w0_obs  : float  Observed w₀.
    w0_sigma: float  1σ uncertainty on w₀.
    wa_obs  : float  Observed wₐ.
    wa_sigma: float  1σ uncertainty on wₐ.
    rho     : float  Pearson correlation between w₀ and wₐ (default 0).

    Returns
    -------
    dict with chi2, degrees of freedom, p_value, and sigma-equivalent.
    """
    w0_um = UM_PREDICTION["w0"]
    wa_um = UM_PREDICTION["wa"]

    dw0 = (w0_um - w0_obs) / w0_sigma if w0_sigma > 0 else 0.0
    dwa = (wa_um - wa_obs) / wa_sigma if wa_sigma > 0 else 0.0

    denom = 1.0 - rho ** 2
    if denom <= 0:
        chi2 = float("inf")
    else:
        chi2 = (dw0**2 + dwa**2 - 2.0 * rho * dw0 * dwa) / denom

    # Convert χ²(2dof) to sigma-equivalent for 2D
    # P(χ²_2 < x) = 1 - exp(-x/2) → chi2_sigma = sqrt(-2 ln(p_outside))
    if chi2 >= 0:
        p_outside = math.exp(-chi2 / 2.0)
        # 1D sigma-equivalent: solve erfc(sigma/sqrt(2)) = p_outside
        # Approximation: sigma ≈ sqrt(chi2) for large chi2
        sigma_equiv = math.sqrt(chi2) if chi2 > 0 else 0.0
    else:
        sigma_equiv = 0.0
        p_outside = 1.0

    return {
        "chi2": chi2,
        "dof": 2,
        "sigma_equiv": sigma_equiv,
        "p_outside": p_outside,
        "dw0_sigma": dw0,
        "dwa_sigma": dwa,
    }


def joint_routing_decision(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
    release_name: str = "DESI Year 3",
    year: int = 2026,
    rho: float = 0.0,
) -> Dict[str, object]:
    """Route a CPL measurement using both 1D wₐ and 2D joint χ² tests.

    The 1D wₐ test is the primary falsification condition for UM (wₐ=0).
    The 2D joint test provides additional context on the combined tension.

    Routing hierarchy:
      1. If |wₐ/σ_wₐ| ≥ 3  →  FALSIFIED (wₐ=0 excluded at ≥3σ)
      2. Elif χ²_joint indicates >3σ joint exclusion  →  TENSION (document)
      3. Elif |wₐ/σ_wₐ| ≥ 1 or |w₀/σ_{w₀}| ≥ 2  →  TENSION
      4. Else  →  PASS

    Returns
    -------
    dict with routing verdicts (1D, 2D, combined), actions, and targets.
    """
    marginal_1d = tension_from_measurement(w0_obs, w0_sigma, wa_obs, wa_sigma, release_name)
    chi2_stat = chi2_joint(w0_obs, w0_sigma, wa_obs, wa_sigma, rho)

    wa_tension = marginal_1d["tension_wa_sigma"]
    w0_tension = marginal_1d["tension_w0_sigma"]

    route_1d = routing_decision(w0_tension, wa_tension, release_name, year)

    # 2D routing (more sensitive to joint constraint)
    if chi2_stat["sigma_equiv"] >= 3.5:
        route_2d = "FALSIFIED"
        route_2d_status = "❌ JOINT_FALSIFIED (χ²-2D ≥ 3.5σ)"
    elif chi2_stat["sigma_equiv"] >= 2.0:
        route_2d = "TENSION"
        route_2d_status = f"🟠 JOINT_TENSION (χ²-2D = {chi2_stat['sigma_equiv']:.2f}σ)"
    else:
        route_2d = "PASS"
        route_2d_status = f"🟢 JOINT_PASS (χ²-2D = {chi2_stat['sigma_equiv']:.2f}σ)"

    # Combined verdict: use the more severe routing
    severity = {"PASS": 0, "TENSION": 1, "FALSIFIED": 2}
    combined_route = (
        "FALSIFIED"
        if max(severity.get(route_1d["route"], 0), severity.get(route_2d, 0)) == 2
        else (
            "TENSION"
            if max(severity.get(route_1d["route"], 0), severity.get(route_2d, 0)) == 1
            else "PASS"
        )
    )

    return {
        "release": release_name,
        "year": year,
        "measurement": {
            "w0_obs": w0_obs, "w0_sigma": w0_sigma,
            "wa_obs": wa_obs, "wa_sigma": wa_sigma,
        },
        "1d_routing": route_1d,
        "chi2_joint": chi2_stat,
        "2d_routing": {"route": route_2d, "status": route_2d_status},
        "combined_route": combined_route,
        "combined_status": (
            "❌ FALSIFIED" if combined_route == "FALSIFIED"
            else "🟠 TENSION" if combined_route == "TENSION"
            else "🟢 PASS"
        ),
        "downstream_update_targets": DOWNSTREAM_UPDATE_TARGETS,
        "30_day_deadline_action": thirty_day_integration_protocol()["steps"][0],
    }


def scenario_analysis() -> List[Dict[str, object]]:
    """Run joint routing for all 9 pre-defined Y3 scenarios.

    Returns
    -------
    list of routing dicts, one per scenario.
    """
    results = []
    for sc in Y3_SCENARIOS:
        verdict = joint_routing_decision(
            w0_obs=sc["w0"],
            w0_sigma=sc["sigma_w0"],
            wa_obs=sc["wa"],
            wa_sigma=sc["sigma_wa"],
            release_name=sc["name"],
        )
        verdict["scenario_description"] = sc["description"]
        results.append(verdict)
    return results


def falsification_probability_forecast(
    wa_central: float = -0.62,
    sigma_range: Optional[List[float]] = None,
) -> List[Dict[str, object]]:
    """Forecast falsification tension as σ_wₐ tightens (precision improves).

    Holds w₀ and wₐ central values fixed at their Y1 values and sweeps
    σ_wₐ from Y1 precision down to a future tight measurement.

    Parameters
    ----------
    wa_central : float  wₐ central value (default: DESI Y1 = −0.62).
    sigma_range : list  σ_wₐ values to sweep (default: 0.30 → 0.10).

    Returns
    -------
    list of dicts with tension and routing at each precision level.
    """
    if sigma_range is None:
        sigma_range = [round(0.30 - i * 0.025, 3) for i in range(9)]  # 0.30 → 0.10

    results = []
    for sigma in sigma_range:
        tension = abs(wa_central - UM_PREDICTION["wa"]) / sigma if sigma > 0 else float("inf")
        w0_tension = abs(UM_PREDICTION["w0"] - DESI_DR2["w0_central"]) / DESI_DR2["w0_sigma"]
        route = routing_decision(w0_tension, tension, "forecast", 2026)
        results.append({
            "sigma_wa": sigma,
            "wa_central": wa_central,
            "wa_tension_sigma": tension,
            "route": route["route"],
            "status": route["status"],
        })
    return results


def thirty_day_integration_protocol() -> Dict[str, object]:
    """Return the 30-day integration protocol to execute on Y3 publication.

    Returns
    -------
    dict with ordered steps, artifact targets, and command references.
    """
    return {
        "trigger": "DESI Year 3 paper published (expected ~2026)",
        "deadline": "30 days from publication date",
        "steps": [
            {
                "step": 1,
                "action": "Extract w₀ and wₐ values with 1σ uncertainties from abstract/table",
                "required": True,
            },
            {
                "step": 2,
                "action": "Run: python -c \"from src.core.desi_y3_joint_routing import joint_routing_decision; print(joint_routing_decision(w0, s0, wa, swa))\"",
                "required": True,
            },
            {
                "step": 3,
                "action": "Run: route_desi_y3(wa, sigma) from src.core.desi_year3_monitor",
                "required": True,
            },
            {
                "step": 4,
                "action": "Update OBSERVATION_TRACKER.md P4 row with routing verdict, σ-level, date",
                "required": True,
            },
            {
                "step": 5,
                "action": "Update CLAIM_MASTER_BOARD.md T1 tension row",
                "required": True,
            },
            {
                "step": 6,
                "action": "Update TRUTH_LAYER.md §3 T1 section",
                "required": True,
            },
            {
                "step": 7,
                "action": "Update GATEKEEPER_SUMMARY.md Part 5",
                "required": True,
            },
            {
                "step": 8,
                "action": "Sync canonical_falsifier_evidence_feed.py DESI tension level",
                "required": True,
            },
            {
                "step": 9,
                "action": (
                    "If FALSIFIED: open retraction issue, mark T1 FALSIFIED in all docs, "
                    "add WAVE_CHANGELOG entry with full falsification record"
                ),
                "required": "conditional (only if FALSIFIED)",
            },
        ],
        "downstream_targets": DOWNSTREAM_UPDATE_TARGETS,
        "falsification_condition": "wₐ ≠ 0 at ≥ 3σ",
        "resolution_condition": "|wₐ| / σ_wₐ < 1.0 → T1 RESOLVED",
    }


def y3_full_routing_report() -> Dict[str, object]:
    """Return the full DESI Y3 routing readiness report (v10.30)."""
    return {
        "version": "v10.30",
        "title": "DESI Year 3 Joint w₀-wₐ Routing Infrastructure",
        "baseline": DESI_DR2,
        "um_prediction": UM_PREDICTION,
        "current_tension": tension_from_measurement(
            DESI_DR2["w0_central"], DESI_DR2["w0_sigma"],
            DESI_DR2["wa_central"], DESI_DR2["wa_sigma"],
            "DESI DR2 baseline",
        ),
        "current_chi2": chi2_joint(
            DESI_DR2["w0_central"], DESI_DR2["w0_sigma"],
            DESI_DR2["wa_central"], DESI_DR2["wa_sigma"],
        ),
        "y3_status": "PENDING — Y3 results not yet published",
        "scenarios_covered": len(Y3_SCENARIOS),
        "scenario_summary": [
            {
                "name": sc["name"],
                "route": joint_routing_decision(
                    sc["w0"], sc["sigma_w0"], sc["wa"], sc["sigma_wa"], sc["name"]
                )["combined_route"],
            }
            for sc in Y3_SCENARIOS
        ],
        "falsification_forecast": falsification_probability_forecast(),
        "integration_protocol": thirty_day_integration_protocol(),
    }
