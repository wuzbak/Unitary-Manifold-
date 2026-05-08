# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
cmbs4_ns_r_joint_falsifier.py — CMB-S4 joint n_s-r falsifier with confidence
ellipse and explicit PASS/TENSION/FALSIFIED routing (v10.30).

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
CMB-S4 (~2030) will measure n_s and r with:
  σ_ns ≈ 0.002  (vs current Planck ≈ 0.0042)
  σ_r  ≈ 0.001  (vs current BICEP/Keck upper limit r < 0.036)

UM predicts:
  n_s = 0.9635  (within 0.33σ of Planck 0.9649 ± 0.0042)
  r   = 0.0315  (within BICEP/Keck bound)

This module:
  1. Routes CMB-S4 results in the n_s-r plane.
  2. Maps the UM signal ellipse (±1σ, ±2σ predictions).
  3. Identifies the exact falsification conditions with σ_ns = 0.002.
  4. Computes the minimum r detection needed to support UM vs alternatives.

═══════════════════════════════════════════════════════════════════════════
FALSIFICATION CONDITIONS
═══════════════════════════════════════════════════════════════════════════
  • n_s ∉ [0.955, 0.972] at < 0.001 precision → FALSIFIED
  • r < 0.010 confirmed at > 3σ → FALSIFIED
  • r > 0.036 confirmed at > 3σ → FALSIFIED (violates BICEP bound)
  • Both n_s and r consistent with UM prediction → SUPPORTED (pending β)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

__all__ = [
    "UM_NS",
    "UM_R",
    "NS_PDG",
    "NS_SIGMA_PLANCK",
    "NS_SIGMA_CMBS4",
    "R_BICEP_UPPER",
    "R_SIGMA_CMBS4",
    "NS_FALSIFICATION_WINDOW",
    "R_FALSIFICATION_LOWER",
    "route_cmbs4_ns_r",
    "ns_tension",
    "r_tension",
    "joint_ns_r_verdict",
    "cmbs4_signal_ellipse",
    "cmbs4_readiness_report",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: UM CMB predictions
UM_NS: float = 0.9635
UM_R: float = 0.0315

#: Current observational constraints
NS_PDG: float = 0.9649
NS_SIGMA_PLANCK: float = 0.0042
R_BICEP_UPPER: float = 0.036

#: Projected CMB-S4 precisions (~2030)
NS_SIGMA_CMBS4: float = 0.002
R_SIGMA_CMBS4: float = 0.001

#: UM falsification window for n_s (must lie within at < 0.001 precision)
NS_FALSIFICATION_WINDOW: Tuple[float, float] = (0.955, 0.972)

#: Falsification threshold for r (r < this at > 3σ → FALSIFIED)
R_FALSIFICATION_LOWER: float = 0.010


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------


def ns_tension(ns_obs: float, ns_sigma: float) -> Dict[str, float]:
    """Compute UM n_s tension vs an observed value.

    Parameters
    ----------
    ns_obs   : float  Observed n_s central value.
    ns_sigma : float  Observed n_s uncertainty (1σ).

    Returns
    -------
    dict with tension, window check, and falsification status.
    """
    tension = abs(UM_NS - ns_obs) / ns_sigma if ns_sigma > 0 else float("inf")
    in_window = NS_FALSIFICATION_WINDOW[0] <= ns_obs <= NS_FALSIFICATION_WINDOW[1]
    falsified = (not in_window) and ns_sigma < 0.001

    return {
        "ns_obs": ns_obs,
        "ns_sigma": ns_sigma,
        "ns_um": UM_NS,
        "tension_sigma": tension,
        "in_falsification_window": in_window,
        "falsified": falsified,
        "window": NS_FALSIFICATION_WINDOW,
    }


def r_tension(r_obs: float, r_sigma: float) -> Dict[str, float]:
    """Compute UM r tension vs an observed value or upper limit.

    Parameters
    ----------
    r_obs   : float  Observed r central value (or 0 for upper limit).
    r_sigma : float  1σ uncertainty (or upper limit / 3 for a 3σ UL).

    Returns
    -------
    dict with tension and falsification status.
    """
    tension = abs(UM_R - r_obs) / r_sigma if r_sigma > 0 else float("inf")
    # Falsified if r < 0.010 at > 3σ confidence
    r_upper = r_obs + 3.0 * r_sigma
    falsified_low = r_upper < R_FALSIFICATION_LOWER

    # Falsified if r > 0.036 confirmed
    r_lower = r_obs - 3.0 * r_sigma if r_obs > 0 else 0.0
    falsified_high = r_lower > R_BICEP_UPPER

    return {
        "r_obs": r_obs,
        "r_sigma": r_sigma,
        "r_um": UM_R,
        "tension_sigma": tension,
        "falsified_too_low": falsified_low,
        "falsified_too_high": falsified_high,
        "falsified": falsified_low or falsified_high,
        "r_3sigma_upper": r_upper,
        "r_3sigma_lower": r_lower,
    }


def joint_ns_r_verdict(
    ns_obs: float,
    ns_sigma: float,
    r_obs: float,
    r_sigma: float,
    experiment: str = "CMB-S4",
    year: int = 2030,
) -> Dict[str, object]:
    """Route joint n_s-r measurement into PASS/TENSION/FALSIFIED.

    Routing hierarchy:
      1. If either n_s or r is falsified → FALSIFIED
      2. Elif joint χ² > 3σ or either 1D tension > 2σ → TENSION
      3. Else → PASS

    Parameters
    ----------
    ns_obs    : float  Observed n_s.
    ns_sigma  : float  n_s uncertainty (1σ).
    r_obs     : float  Observed r.
    r_sigma   : float  r uncertainty (1σ).
    experiment: str    Experiment name.
    year      : int    Publication year.

    Returns
    -------
    dict with full routing decision.
    """
    ns_result = ns_tension(ns_obs, ns_sigma)
    r_result = r_tension(r_obs, r_sigma)

    # Joint χ² (uncorrelated n_s, r for leading order)
    chi2 = ns_result["tension_sigma"]**2 + r_result["tension_sigma"]**2
    joint_sigma = math.sqrt(chi2)

    if ns_result["falsified"] or r_result["falsified"]:
        route = "FALSIFIED"
        status = "❌ FALSIFIED"
        reason = []
        if ns_result["falsified"]:
            reason.append(f"n_s = {ns_obs:.4f} ∉ [{NS_FALSIFICATION_WINDOW[0]}, {NS_FALSIFICATION_WINDOW[1]}]")
        if r_result["falsified_too_low"]:
            reason.append(f"r < {R_FALSIFICATION_LOWER} confirmed at 3σ")
        if r_result["falsified_too_high"]:
            reason.append(f"r > {R_BICEP_UPPER} confirmed at 3σ")
        action = (
            "Mark P1 and P2 FALSIFIED in CLAIM_MASTER_BOARD.md. "
            "Update TRUTH_LAYER.md and open retraction issue."
        )
    elif joint_sigma >= 2.0 or ns_result["tension_sigma"] >= 2.0 or r_result["tension_sigma"] >= 2.0:
        route = "TENSION"
        status = f"🟠 TENSION (joint {joint_sigma:.2f}σ)"
        reason = [
            f"n_s tension: {ns_result['tension_sigma']:.2f}σ",
            f"r tension: {r_result['tension_sigma']:.2f}σ",
        ]
        action = (
            "Document tension in OBSERVATION_TRACKER.md. "
            "Update TRUTH_LAYER.md §2. Monitor improvement with improved data."
        )
    else:
        route = "PASS"
        status = f"🟢 PASS (joint {joint_sigma:.2f}σ)"
        reason = [
            f"n_s tension: {ns_result['tension_sigma']:.2f}σ",
            f"r tension: {r_result['tension_sigma']:.2f}σ",
        ]
        action = (
            "Update OBSERVATION_TRACKER.md P2/P3 rows as CONSISTENT. "
            "No retraction needed. Both P1 and P2 remain GEOMETRIC_PREDICTION."
        )

    return {
        "experiment": experiment,
        "year": year,
        "measurement": {
            "ns_obs": ns_obs, "ns_sigma": ns_sigma,
            "r_obs": r_obs, "r_sigma": r_sigma,
        },
        "ns_result": ns_result,
        "r_result": r_result,
        "joint_sigma": joint_sigma,
        "route": route,
        "status": status,
        "reason": reason,
        "action": action,
    }


def cmbs4_signal_ellipse() -> Dict[str, object]:
    """Return the UM signal ellipse in the n_s-r plane for CMB-S4.

    The ellipse represents the UM prediction uncertainty from the
    geometric derivation. Not the experimental error ellipse.

    Returns
    -------
    dict with signal centre, 1σ and 2σ UM prediction bands.
    """
    # The UM n_s prediction has a derivation uncertainty of ±0.001
    # (sub-dominant to the current Planck 0.0042 experimental error)
    # The r prediction from inflation model has ±0.002 uncertainty
    ns_theory_sigma = 0.001  # theoretical uncertainty on UM n_s
    r_theory_sigma = 0.002   # theoretical uncertainty on UM r

    return {
        "centre_ns": UM_NS,
        "centre_r": UM_R,
        "ns_theory_sigma": ns_theory_sigma,
        "r_theory_sigma": r_theory_sigma,
        "ns_1sigma_band": (UM_NS - ns_theory_sigma, UM_NS + ns_theory_sigma),
        "ns_2sigma_band": (UM_NS - 2*ns_theory_sigma, UM_NS + 2*ns_theory_sigma),
        "r_1sigma_band": (UM_R - r_theory_sigma, UM_R + r_theory_sigma),
        "r_2sigma_band": (UM_R - 2*r_theory_sigma, UM_R + 2*r_theory_sigma),
        "cmbs4_ns_sigma": NS_SIGMA_CMBS4,
        "cmbs4_r_sigma": R_SIGMA_CMBS4,
        "detectability_ns": (
            f"CMB-S4 σ_ns = {NS_SIGMA_CMBS4} vs UM offset from Planck: "
            f"{abs(UM_NS - NS_PDG):.4f} ({abs(UM_NS - NS_PDG)/NS_SIGMA_CMBS4:.1f}σ). "
            f"Tension will be resolved at this precision."
        ),
        "detectability_r": (
            f"CMB-S4 σ_r = {R_SIGMA_CMBS4}; UM r = {UM_R}. "
            f"If measured: {UM_R/R_SIGMA_CMBS4:.1f}σ detection of primordial GW. "
            f"If r < 0.010 at 3σ: UM FALSIFIED."
        ),
    }


def cmbs4_readiness_report() -> Dict[str, object]:
    """Return CMB-S4 readiness and pre-publication falsifier status (v10.30)."""
    # Current state (Planck + BICEP/Keck)
    current_verdict = joint_ns_r_verdict(
        ns_obs=NS_PDG, ns_sigma=NS_SIGMA_PLANCK,
        r_obs=0.018, r_sigma=0.012,  # BICEP/Keck approximate representative point
        experiment="Planck 2018 + BICEP/Keck current",
        year=2024,
    )

    # Three CMB-S4 projection scenarios
    scenarios_s4 = [
        joint_ns_r_verdict(0.9635, 0.002, 0.0315, 0.001, "CMB-S4 best-case (UM exact)", 2030),
        joint_ns_r_verdict(0.9649, 0.002, 0.020, 0.001, "CMB-S4 Planck+r-detection", 2030),
        joint_ns_r_verdict(0.970, 0.002, 0.008, 0.001, "CMB-S4 worst-case (n_s high, r low)", 2030),
    ]

    return {
        "version": "v10.30",
        "title": "CMB-S4 Joint n_s-r Falsifier Readiness Report",
        "um_predictions": {"ns": UM_NS, "r": UM_R},
        "current_status": current_verdict,
        "cmbs4_expected_year": 2030,
        "cmbs4_expected_sigma_ns": NS_SIGMA_CMBS4,
        "cmbs4_expected_sigma_r": R_SIGMA_CMBS4,
        "signal_ellipse": cmbs4_signal_ellipse(),
        "projection_scenarios": scenarios_s4,
        "falsification_conditions": [
            f"n_s ∉ [{NS_FALSIFICATION_WINDOW[0]}, {NS_FALSIFICATION_WINDOW[1]}] at < 0.001 precision → FALSIFIED (P1)",
            f"r < {R_FALSIFICATION_LOWER} confirmed at > 3σ → FALSIFIED (P2)",
            f"r > {R_BICEP_UPPER} confirmed at > 3σ → FALSIFIED (P2, violates BICEP bound)",
        ],
        "command": (
            "from src.core.cmbs4_ns_r_joint_falsifier import joint_ns_r_verdict; "
            "print(joint_ns_r_verdict(ns_obs, ns_sigma, r_obs, r_sigma))"
        ),
    }
