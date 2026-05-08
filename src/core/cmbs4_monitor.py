# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
cmbs4_monitor.py — CMB-S4 spectral-index / tensor-ratio monitoring harness.

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
CMB-S4 (~2030) will measure the scalar spectral index n_s and the
tensor-to-scalar ratio r with substantially improved precision over
Planck + BICEP/Keck.

UM predictions:
  n_s = 0.9635   (Planck 2018: 0.9649 ± 0.0042, currently 0.33σ — GEOMETRIC_PREDICTION)
  r   = 0.0315   (BICEP/Keck 95% UL < 0.036 — GEOMETRIC_PREDICTION)

CMB-S4 expected sensitivity:
  σ(n_s) ≈ 0.002  (factor ~2 improvement over Planck)
  σ(r)   ≈ 0.001  (or detection at ~30σ if r ≈ 0.03)

═══════════════════════════════════════════════════════════════════════════
FALSIFICATION CONDITIONS
═══════════════════════════════════════════════════════════════════════════
  • n_s: if measured n_s ∉ [0.955, 0.972] at σ < 0.001 → UM n_s challenged
  • r  : if r < 0.010 at > 3σ → UM braided-winding mechanism challenged
         (UM predicts r = 0.0315; detection below 0.010 would exclude it)

═══════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    # Constants
    "N_S_UM",
    "N_S_PDG",
    "N_S_PDG_SIGMA",
    "R_UM",
    "R_UPPER_LIMIT",
    "CMBS4_EXPECTED_NS_SIGMA",
    "CMBS4_EXPECTED_R_SIGMA",
    "CMBS4_LAUNCH_YEAR",
    "N_S_FALSIFICATION_WINDOW",
    "R_FALSIFICATION_THRESHOLD",
    # Baseline dicts
    "PLANCK_BASELINE",
    "UM_PREDICTION",
    # Functions
    "update_with_cmbs4_data",
    "falsification_verdict_ns",
    "falsification_verdict_r",
    "monitoring_report",
    "cmbs4_readiness_assessment",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N_S_UM: float = 0.9635          # UM prediction for scalar spectral index
N_S_PDG: float = 0.9649         # Planck 2018 central value
N_S_PDG_SIGMA: float = 0.0042   # Planck 2018 1σ uncertainty

R_UM: float = 0.0315            # UM prediction for tensor-to-scalar ratio
R_UPPER_LIMIT: float = 0.036    # BICEP/Keck 2021 95% upper limit

CMBS4_EXPECTED_NS_SIGMA: float = 0.002  # CMB-S4 forecast σ(n_s)
CMBS4_EXPECTED_R_SIGMA: float = 0.001   # CMB-S4 forecast σ(r)
CMBS4_LAUNCH_YEAR: int = 2030

N_S_FALSIFICATION_WINDOW: tuple = (0.955, 0.972)  # UM-predicted admissible n_s range
R_FALSIFICATION_THRESHOLD: float = 0.010           # r below this at >3σ challenges UM

# ---------------------------------------------------------------------------
# Baseline observational data
# ---------------------------------------------------------------------------

#: Planck 2018 + BICEP/Keck 2021 baseline
PLANCK_BASELINE: Dict = {
    "release": "Planck 2018 + BICEP/Keck 2021",
    "year": 2021,
    "reference": (
        "Planck Collaboration (2020), A&A 641 A10; "
        "BICEP/Keck Collaboration (2021), PRL 127, 151301"
    ),
    "n_s_central": N_S_PDG,
    "n_s_sigma": N_S_PDG_SIGMA,
    "r_central": None,          # only upper limit available
    "r_upper_limit_95": R_UPPER_LIMIT,
    "status": "CURRENT_BASELINE",
}

#: UM predictions for n_s and r
UM_PREDICTION: Dict = {
    "n_s": N_S_UM,
    "r": R_UM,
    "mechanism_ns": (
        "n_s = 1 − 2/(N_e) corrected by 5D Kaluza-Klein winding number n_w=5 "
        "and braided sound speed c_s=12/37"
    ),
    "mechanism_r": (
        "r = 16ε with ε suppressed by (5,7) braid resonance; "
        "r = 0.0315 from braided winding (Pillar 1)"
    ),
    "falsification_ns": (
        "n_s ∉ [0.955, 0.972] at σ(n_s) < 0.001 challenges UM spectral prediction"
    ),
    "falsification_r": (
        "r < 0.010 at > 3σ challenges UM braided-winding mechanism"
    ),
    "current_ns_tension_sigma": abs(N_S_UM - N_S_PDG) / N_S_PDG_SIGMA,
    "current_ns_status": "GEOMETRIC_PREDICTION (0.33σ from Planck central value)",
    "current_r_status": "GEOMETRIC_PREDICTION (consistent with < 0.036 upper limit)",
    "module": "src/core/ (Pillar 1 — braided KK geometry)",
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def _tension(predicted: float, observed: float, sigma: float) -> float:
    """Return tension in units of sigma; inf if sigma == 0."""
    return abs(predicted - observed) / sigma if sigma > 0 else float("inf")


def update_with_cmbs4_data(
    n_s_obs: float,
    n_s_sigma: float,
    r_obs: float,
    r_sigma: float,
    reference: str = "",
) -> Dict:
    """Process CMB-S4 data and compare with UM predictions.

    Parameters
    ----------
    n_s_obs : float   Observed n_s central value.
    n_s_sigma : float Observed n_s uncertainty (1σ).
    r_obs : float     Observed r central value.
    r_sigma : float   Observed r uncertainty (1σ).
    reference : str   Reference (arXiv or journal).

    Returns
    -------
    dict with tension analysis and consistency verdicts for both parameters.
    """
    t_ns = _tension(N_S_UM, n_s_obs, n_s_sigma)
    t_r = _tension(R_UM, r_obs, r_sigma)

    baseline_t_ns = _tension(N_S_UM, N_S_PDG, N_S_PDG_SIGMA)

    ns_verdict = falsification_verdict_ns(n_s_obs, n_s_sigma)
    r_verdict = falsification_verdict_r(r_obs, r_sigma)

    return {
        "reference": reference,
        "n_s_obs": n_s_obs,
        "n_s_sigma": n_s_sigma,
        "r_obs": r_obs,
        "r_sigma": r_sigma,
        "um_n_s": N_S_UM,
        "um_r": R_UM,
        "tension_ns_sigma": t_ns,
        "tension_r_sigma": t_r,
        "baseline_tension_ns_sigma": baseline_t_ns,
        "ns_verdict": ns_verdict,
        "r_verdict": r_verdict,
        "overall_consistent": (
            ns_verdict["level"] == "CONSISTENT"
            and r_verdict["level"] == "CONSISTENT"
        ),
        "wording": (
            f"CMB-S4 update: n_s = {n_s_obs:.4f} ± {n_s_sigma:.4f} "
            f"(UM: {N_S_UM:.4f}, tension {t_ns:.2f}σ); "
            f"r = {r_obs:.4f} ± {r_sigma:.4f} "
            f"(UM: {R_UM:.4f}, tension {t_r:.2f}σ)."
        ),
    }


def falsification_verdict_ns(n_s_obs: float, n_s_sigma: float) -> Dict:
    """Return falsification verdict for the UM n_s = 0.9635 prediction.

    Parameters
    ----------
    n_s_obs : float   Observed n_s central value.
    n_s_sigma : float Observed n_s uncertainty (1σ).

    Returns
    -------
    dict with falsification assessment.
    """
    tension = _tension(N_S_UM, n_s_obs, n_s_sigma)
    lo, hi = N_S_FALSIFICATION_WINDOW
    in_window = lo <= n_s_obs <= hi

    if tension < 1.0:
        level = "CONSISTENT"
        verdict = f"CONSISTENT — UM n_s={N_S_UM} within 1σ ✅"
    elif tension < 2.0:
        level = "CONSISTENT"
        verdict = f"CONSISTENT — UM n_s={N_S_UM} at {tension:.2f}σ ✅"
    elif tension < 3.0:
        level = "MARGINAL"
        verdict = f"MARGINAL — UM n_s={N_S_UM} at {tension:.2f}σ; monitoring required ⚠️"
    else:
        level = "EXCLUDED"
        verdict = f"EXCLUDED — UM n_s={N_S_UM} at {tension:.2f}σ 🔴"

    # Override to EXCLUDED if observed is outside falsification window at high precision
    if not in_window and n_s_sigma < 0.001 and level not in ("EXCLUDED",):
        level = "EXCLUDED"
        verdict = (
            f"EXCLUDED — n_s={n_s_obs:.4f} outside UM window "
            f"[{lo}, {hi}] at σ={n_s_sigma:.4f} 🔴"
        )

    return {
        "parameter": "n_s",
        "um_prediction": N_S_UM,
        "observed": n_s_obs,
        "sigma": n_s_sigma,
        "tension_sigma": tension,
        "in_falsification_window": in_window,
        "falsification_window": N_S_FALSIFICATION_WINDOW,
        "level": level,
        "verdict": verdict,
        "action_required": (
            "Document as HONEST_OPEN_PROBLEM in FALLIBILITY.md"
            if level in ("MARGINAL", "EXCLUDED")
            else "No action — within observational uncertainty"
        ),
    }


def falsification_verdict_r(r_obs: float, r_sigma: float) -> Dict:
    """Return falsification verdict for the UM r = 0.0315 prediction.

    Parameters
    ----------
    r_obs : float   Observed r central value.
    r_sigma : float Observed r uncertainty (1σ).

    Returns
    -------
    dict with falsification assessment.
    """
    tension = _tension(R_UM, r_obs, r_sigma)

    # Distinct falsification: if r < threshold detected at > 3σ
    threshold_tension = (R_FALSIFICATION_THRESHOLD - r_obs) / r_sigma if r_sigma > 0 else float("inf")
    falsified_by_threshold = (r_obs < R_FALSIFICATION_THRESHOLD) and (threshold_tension > 3.0)

    if falsified_by_threshold:
        level = "EXCLUDED"
        verdict = (
            f"EXCLUDED — r = {r_obs:.4f} < {R_FALSIFICATION_THRESHOLD} "
            f"at > 3σ; UM r={R_UM} challenged 🔴"
        )
    elif tension < 1.0:
        level = "CONSISTENT"
        verdict = f"CONSISTENT — UM r={R_UM} within 1σ ✅"
    elif tension < 2.0:
        level = "CONSISTENT"
        verdict = f"CONSISTENT — UM r={R_UM} at {tension:.2f}σ ✅"
    elif tension < 3.0:
        level = "MARGINAL"
        verdict = f"MARGINAL — UM r={R_UM} at {tension:.2f}σ ⚠️"
    else:
        level = "EXCLUDED"
        verdict = f"EXCLUDED — UM r={R_UM} at {tension:.2f}σ 🔴"

    return {
        "parameter": "r",
        "um_prediction": R_UM,
        "observed": r_obs,
        "sigma": r_sigma,
        "tension_sigma": tension,
        "falsification_threshold": R_FALSIFICATION_THRESHOLD,
        "falsified_by_threshold": falsified_by_threshold,
        "level": level,
        "verdict": verdict,
        "action_required": (
            "Document as HONEST_OPEN_PROBLEM in FALLIBILITY.md"
            if level in ("MARGINAL", "EXCLUDED")
            else "No action — within observational uncertainty"
        ),
    }


def monitoring_report() -> Dict:
    """Generate current monitoring report vs Planck baseline.

    Returns
    -------
    dict with full monitoring state.
    """
    ns_verdict = falsification_verdict_ns(N_S_PDG, N_S_PDG_SIGMA)
    # For r, Planck/BICEP only has an upper limit; use the upper limit as a proxy
    r_verdict = falsification_verdict_r(R_UPPER_LIMIT, R_UPPER_LIMIT * 0.5)

    return {
        "version": "v10.17",
        "current_baseline": PLANCK_BASELINE,
        "um_prediction": UM_PREDICTION,
        "current_ns_verdict": ns_verdict,
        "current_r_status": "GEOMETRIC_PREDICTION — r < 0.036 (95% UL, BICEP/Keck 2021)",
        "falsification_summary": {
            "n_s": f"UM: {N_S_UM} vs Planck: {N_S_PDG} ± {N_S_PDG_SIGMA} "
                   f"({ns_verdict['tension_sigma']:.2f}σ)",
            "r": f"UM: {R_UM} vs BICEP/Keck UL: < {R_UPPER_LIMIT} (consistent)",
        },
        "next_milestone": {
            "experiment": "CMB-S4",
            "expected_year": CMBS4_LAUNCH_YEAR,
            "expected_ns_sigma": CMBS4_EXPECTED_NS_SIGMA,
            "expected_r_sigma": CMBS4_EXPECTED_R_SIGMA,
            "note": (
                f"CMB-S4 (~{CMBS4_LAUNCH_YEAR}) will measure n_s to σ≈{CMBS4_EXPECTED_NS_SIGMA} "
                f"and r to σ≈{CMBS4_EXPECTED_R_SIGMA}, providing a decisive test of "
                f"UM n_s={N_S_UM} and r={R_UM}."
            ),
        },
        "update_instructions": (
            "When CMB-S4 results are available, call:\n"
            "  update_with_cmbs4_data(n_s_obs, n_s_sigma, r_obs, r_sigma, reference)"
        ),
    }


def cmbs4_readiness_assessment() -> Dict:
    """Explain what CMB-S4 will test and how UM fares.

    Returns
    -------
    dict describing UM readiness for CMB-S4 confrontation.
    """
    ns_room = min(
        abs(N_S_UM - N_S_FALSIFICATION_WINDOW[0]),
        abs(N_S_UM - N_S_FALSIFICATION_WINDOW[1]),
    )
    ns_survives = ns_room / CMBS4_EXPECTED_NS_SIGMA

    return {
        "experiment": "CMB-S4",
        "launch_year": CMBS4_LAUNCH_YEAR,
        "um_predictions": {"n_s": N_S_UM, "r": R_UM},
        "current_status": {
            "n_s": (
                f"UM n_s={N_S_UM} is {abs(N_S_UM - N_S_PDG) / N_S_PDG_SIGMA:.2f}σ "
                f"from Planck centre (GEOMETRIC_PREDICTION)"
            ),
            "r": (
                f"UM r={R_UM} is consistent with BICEP/Keck UL < {R_UPPER_LIMIT} "
                "(GEOMETRIC_PREDICTION)"
            ),
        },
        "cmbs4_sensitivity": {
            "sigma_ns": CMBS4_EXPECTED_NS_SIGMA,
            "sigma_r": CMBS4_EXPECTED_R_SIGMA,
        },
        "ns_margin_to_falsification_window_sigmas": ns_survives,
        "falsification_conditions": {
            "n_s": (
                f"n_s outside [{N_S_FALSIFICATION_WINDOW[0]}, {N_S_FALSIFICATION_WINDOW[1]}] "
                f"at σ < 0.001 → UM falsified"
            ),
            "r": (
                f"r < {R_FALSIFICATION_THRESHOLD} at > 3σ → UM braided-winding falsified"
            ),
        },
        "expected_outcome": (
            f"If UM is correct, CMB-S4 should measure "
            f"n_s ≈ {N_S_UM} (within ~{ns_room / CMBS4_EXPECTED_NS_SIGMA:.1f}σ of window edge) "
            f"and detect r ≈ {R_UM} at ~{R_UM / CMBS4_EXPECTED_R_SIGMA:.0f}σ significance."
        ),
        "status": "PENDING — CMB-S4 results expected ~2030",
    }
