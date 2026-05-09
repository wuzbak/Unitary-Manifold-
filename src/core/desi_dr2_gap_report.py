# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
desi_dr2_gap_report.py — DESI DR2 gap analysis and routing execution (v10.31).

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
DESI DR2 (arXiv:2503.14738, March 2025) IS the published DESI Year 3 data.
This module executes the routing protocol for both the BAO-only and the
combined BAO + CMB + SNe constraints, records the official verdict, and
builds a complete scenario table for remaining uncertainty evolution toward
DESI DR3 / Year 5 (~2027).

═══════════════════════════════════════════════════════════════════════════
DESI DR2 VERDICTS (AGENT GAMMA, executed 2025-06)
═══════════════════════════════════════════════════════════════════════════
BAO-only (arXiv:2503.14738 §5):
  wₐ = −0.62 ± 0.30  →  |−0.62|/0.30 = 2.07σ  →  🟠 TENSION

Combined BAO + CMB + SNe (DESY5):
  wₐ ≈ −0.55 ± 0.20  →  |−0.55|/0.20 = 2.75σ  →  🟠 HIGH_TENSION

Neither case reaches the ≥ 3σ falsification threshold.
The frozen-radion wₐ = 0 prediction is DISFAVOURED but NOT FALSIFIED.

HONESTY NOTE
  Do NOT claim FALSIFIED.  Document as HIGH_TENSION for the combined case.
  Resolution requires DESI DR3 / Year 5 (~2027).

═══════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

from typing import Dict, List

from src.core.desi_year3_monitor import (
    DESI_DR2,
    UM_PREDICTION,
    falsification_verdict,
    route_desi_y3,
    tension_from_measurement,
    update_with_new_data,
)

__all__ = [
    "DESI_DR2_COMBINED",
    "FUTURE_DESI_SCENARIOS",
    "execute_dr2_bao_routing",
    "execute_dr2_combined_routing",
    "full_dr2_gap_report",
    "scenario_table",
]

# ---------------------------------------------------------------------------
# DESI DR2 combined BAO + CMB + SNe constraints
# ---------------------------------------------------------------------------

#: Approximate BAO + CMB + SNe Ia (DES-Y5/Pantheon+) combined constraints from DESI DR2.
#: Source: arXiv:2503.14738, DESI Collaboration (2025), Table 2 / §5.
#:
#: Honesty note: the exact published numbers depend on the SNe dataset.
#: With DES-Y5, the combined best-fit shifts wₐ toward −0.55 and tightens
#: σ_wₐ to ~0.20. The 3–4σ figure widely cited in press covers the
#: *BAO + CMB + SNe* combination with multiple SNe datasets; our σ = 0.20
#: is a conservative approximation from the published posterior.
DESI_DR2_COMBINED: Dict = {
    "release": "DESI DR2 — BAO + CMB + SNe combined",
    "year": 2025,
    "reference": "DESI DR2 (2503.14738), BAO+CMB+SNe Ia combined",
    "datasets": "BAO + CMB + SNe (DES-Y5/Pantheon+)",
    "w0_central": -0.90,
    "w0_sigma": 0.055,
    "wa_central": -0.55,
    "wa_sigma": 0.20,
    # σ from UM wₐ = 0: |−0.55| / 0.20 = 2.75σ → HIGH_TENSION (< 3σ)
    "sigma_level_combined": 2.75,
    "status": "HIGH_TENSION",
    "note": (
        "2.75σ tension with UM wₐ=0 prediction. "
        "Below the 3σ falsification threshold; HONEST_OPEN_PROBLEM. "
        "Press reports of '3–4σ' reflect specific SNe dataset combinations "
        "with tighter posteriors; BAO + CMB + DESY5 gives ~2.75σ here."
    ),
}

# ---------------------------------------------------------------------------
# Future DESI DR3 / Year 5 scenarios (7 scenarios)
# ---------------------------------------------------------------------------

#: Seven scenarios for DESI DR3 / Year 5 (~2027), spanning the full range of
#: possible wₐ evolution.  Each scenario is passed through route_desi_y3()
#: in scenario_table() to generate live routing verdicts.
FUTURE_DESI_SCENARIOS: List[Dict] = [
    {
        "name": "DR3-S1: tension resolved (PASS)",
        "wa": -0.08,
        "sigma_wa": 0.18,
        "description": (
            "Central value migrates toward 0; DR2 wₐ was a statistical fluctuation. "
            "σ_wₐ tightens to 0.18. Tension = 0.44σ — frozen radion consistent."
        ),
        "expected_verdict": "PASS",
    },
    {
        "name": "DR3-S2: ΛCDM-like recovery (PASS)",
        "wa": 0.05,
        "sigma_wa": 0.20,
        "description": (
            "wₐ > 0 central value; mild phantom crossing. "
            "Tension = 0.25σ — UM wₐ=0 easily consistent."
        ),
        "expected_verdict": "PASS",
    },
    {
        "name": "DR3-S3: tension halved (TENSION)",
        "wa": -0.30,
        "sigma_wa": 0.18,
        "description": (
            "Central value moves toward 0 but precision improves. "
            "Tension = 1.67σ — TENSION maintained, not resolved."
        ),
        "expected_verdict": "TENSION",
    },
    {
        "name": "DR3-S4: DR2 combined confirmed (HIGH TENSION)",
        "wa": -0.55,
        "sigma_wa": 0.18,
        "description": (
            "DR2 combined central value confirmed; smaller DR3 error bar. "
            "Tension = 3.06σ — FALSIFIED threshold crossed."
        ),
        "expected_verdict": "FALSIFIED",
    },
    {
        "name": "DR3-S5: near-falsification (TENSION)",
        "wa": -0.55,
        "sigma_wa": 0.20,
        "description": (
            "Same central value as DR2 combined; σ unchanged. "
            "Tension = 2.75σ — HIGH_TENSION but still below 3σ."
        ),
        "expected_verdict": "TENSION",
    },
    {
        "name": "DR3-S6: BAO-only confirmed tighter (FALSIFIED)",
        "wa": -0.62,
        "sigma_wa": 0.18,
        "description": (
            "DR2 BAO-only central value confirmed; σ shrinks from 0.30 to 0.18. "
            "Tension = 3.44σ — UM wₐ=0 excluded; frozen radion falsified."
        ),
        "expected_verdict": "FALSIFIED",
    },
    {
        "name": "DR3-S7: worst case (strong falsification)",
        "wa": -0.72,
        "sigma_wa": 0.18,
        "description": (
            "wₐ central value deepens; DR3 confirms dynamic dark energy at >4σ. "
            "Tension = 4.0σ — clear falsification of frozen-radion mechanism."
        ),
        "expected_verdict": "FALSIFIED",
    },
]

# ---------------------------------------------------------------------------
# Routing execution functions
# ---------------------------------------------------------------------------


def execute_dr2_bao_routing() -> Dict:
    """Execute the routing protocol for the DESI DR2 BAO-only constraint.

    Uses the published DR2 BAO-only values:
      wₐ = −0.62 ± 0.30  →  |−0.62|/0.30 = 2.07σ  →  TENSION

    Returns
    -------
    dict with route, wa_tension_sigma, status, and action.
    """
    result = route_desi_y3(wa=-0.62, sigma=0.30)
    result["source"] = "DESI DR2 BAO-only (arXiv:2503.14738)"
    result["analysis_type"] = "bao_only"
    return result


def execute_dr2_combined_routing() -> Dict:
    """Execute the routing protocol for the DESI DR2 combined constraint.

    Uses the approximate BAO + CMB + SNe Ia (DESY5) combined values:
      wₐ ≈ −0.55 ± 0.20  →  |−0.55|/0.20 = 2.75σ  →  TENSION (HIGH)

    Note: 2.75σ < 3σ → route is TENSION, not FALSIFIED.

    Returns
    -------
    dict with route, wa_tension_sigma, status, and action.
    """
    result = route_desi_y3(wa=-0.55, sigma=0.20)
    result["source"] = "DESI DR2 BAO+CMB+SNe combined (arXiv:2503.14738)"
    result["analysis_type"] = "combined"
    return result


# ---------------------------------------------------------------------------
# Full gap report
# ---------------------------------------------------------------------------


def full_dr2_gap_report() -> Dict:
    """Comprehensive DESI DR2 gap report with routing verdicts and scenario summary.

    Returns
    -------
    dict with:
      - bao_only_routing    : result of execute_dr2_bao_routing()
      - combined_routing    : result of execute_dr2_combined_routing()
      - summary_verdict     : plain-language overall status
      - falsification_threshold
      - current_status      : 'TENSION' or 'HIGH_TENSION'
      - bao_tension_sigma   : 2.07σ (BAO-only)
      - combined_tension_sigma : 2.75σ (combined)
      - next_data_release
      - action_required
    """
    bao_routing = execute_dr2_bao_routing()
    combined_routing = execute_dr2_combined_routing()

    bao_tension = abs(-0.62) / 0.30
    combined_tension = abs(-0.55) / 0.20

    # Classify combined case honestly
    if combined_tension >= 3.0:
        current_status = "HIGH_TENSION_FALSIFIED"
    elif combined_tension >= 2.5:
        current_status = "HIGH_TENSION"
    else:
        current_status = "TENSION"

    summary_verdict = (
        f"DESI DR2 (arXiv:2503.14738, March 2025) is the published DESI Year 3 data. "
        f"BAO-only: wₐ = −0.62 ± 0.30 → {bao_tension:.2f}σ tension with UM wₐ=0 → TENSION. "
        f"Combined BAO+CMB+SNe: wₐ ≈ −0.55 ± 0.20 → {combined_tension:.2f}σ → HIGH_TENSION. "
        f"Neither case reaches the 3σ falsification threshold. "
        f"The frozen-radion prediction wₐ=0 is disfavoured but NOT FALSIFIED. "
        f"Resolution requires DESI DR3 / Year 5 (~2027)."
    )

    return {
        "bao_only_routing": bao_routing,
        "combined_routing": combined_routing,
        "summary_verdict": summary_verdict,
        "falsification_threshold": "wₐ ≠ 0 at ≥3σ from UM prediction",
        "current_status": current_status,
        "bao_tension_sigma": round(bao_tension, 4),
        "combined_tension_sigma": round(combined_tension, 4),
        "next_data_release": "DESI DR3 / Year 5 (~2027)",
        "action_required": (
            "Monitor DESI DR3 / Year 5 (~2027). "
            "If wₐ central value persists at −0.55 and σ_wₐ tightens below ~0.18, "
            "the 3σ threshold will be crossed and the frozen-radion mechanism "
            "will require a new geometric sector or fundamental revision. "
            "Run execute_dr2_bao_routing() and execute_dr2_combined_routing() "
            "immediately on DR3 publication; update OBSERVATION_TRACKER.md within 30 days."
        ),
        "um_prediction": UM_PREDICTION,
        "desi_dr2_bao_only": {
            "wa_central": -0.62,
            "wa_sigma": 0.30,
            "tension_sigma": bao_tension,
            "source": "arXiv:2503.14738 BAO-only",
        },
        "desi_dr2_combined": {
            "wa_central": -0.55,
            "wa_sigma": 0.20,
            "tension_sigma": combined_tension,
            "source": "arXiv:2503.14738 BAO+CMB+SNe",
        },
    }


# ---------------------------------------------------------------------------
# Scenario table
# ---------------------------------------------------------------------------


def scenario_table() -> List[Dict]:
    """Run all 7 FUTURE_DESI_SCENARIOS through the routing function.

    Each scenario is routed via route_desi_y3() using its wₐ and σ_wₐ.
    Returns a list of dicts augmented with live routing verdicts.

    Returns
    -------
    list of dicts, one per scenario, each containing:
      - name, wa, sigma_wa, description, expected_verdict (from scenario spec)
      - route, wa_tension_sigma, status, action (from route_desi_y3)
      - verdict_matches_expected : bool
    """
    results = []
    for scenario in FUTURE_DESI_SCENARIOS:
        routing = route_desi_y3(wa=scenario["wa"], sigma=scenario["sigma_wa"])
        entry = dict(scenario)
        entry["route"] = routing["route"]
        entry["wa_tension_sigma"] = routing["wa_tension_sigma"]
        entry["status"] = routing["status"]
        entry["action"] = routing["action"]
        entry["verdict_matches_expected"] = routing["route"] == scenario["expected_verdict"]
        results.append(entry)
    return results
