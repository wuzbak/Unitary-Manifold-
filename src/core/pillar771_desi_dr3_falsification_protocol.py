# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 771 — DESI DR3 / CMB-S4 / LiteBIRD Falsification Protocol
=================================================================

Sprint AH — Path B (Experimental Falsification)

STATUS: FALSIFICATION_PROTOCOL_ACTIVE

═══════════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════════

This pillar provides clean, pre-registered PASS/FAIL decision trees for the
three near-term experiments that can falsify or support the UM framework:

  1. DESI DR3 — dark energy equation of state (w₀, wₐ).
     UM prediction: w₀ = −1, wₐ = 0 (KK vacuum, FTUM fixed point).
     DESI Y1 tension: (w₀, wₐ) = (−0.727, −1.05) at 3.5σ from ΛCDM.

  2. CMB-S4 / Simons Observatory — tensor-to-scalar ratio r.
     UM prediction: r = 0.0315 (braided KK inflation, Pillar 58).

  3. LiteBIRD — CMB polarisation birefringence angle β.
     UM prediction: β ∈ {0.273°, 0.331°} (two sector branches).
     Falsifier gap: β ∈ (0.29°, 0.31°) would falsify the braided mechanism.

Each decision tree is:
  - Pre-registered (explicit thresholds, set before data release)
  - Binary routable (PASS / TENSION / FALSIFIED — no post-hoc reinterpretation)
  - Timestamped to this Sprint AH closure sprint (v22.4)

EPISTEMIC COMMITMENT
--------------------
Pre-registration is the scientific commitment that accompanies these protocols.
The thresholds below are FIXED. If the data land outside PASS, the framework
reports TENSION or FALSIFIED honestly. No post-hoc adjustment is permitted.

Theory: ThomasCory Walker-Pearson (2026)
Code: GitHub Copilot (AI)
"""
from __future__ import annotations

import math
from typing import Dict, Literal

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "REGISTRATION_VERSION",
    "DESI_DR3_PROTOCOL",
    "CMB_S4_PROTOCOL",
    "LITEBIRD_PROTOCOL",
    "desi_verdict",
    "cmb_s4_verdict",
    "litebird_verdict",
    "run_all_protocols",
    "pillar_report",
]

PILLAR_NUMBER: int = 771
PILLAR_STATUS: str = "FALSIFICATION_PROTOCOL_ACTIVE"
PILLAR_TITLE: str = "DESI DR3 / CMB-S4 / LiteBIRD Falsification Protocol"
VERSION: str = "v22.4"
REGISTRATION_VERSION: str = "Sprint_AH_v22.4_2026-08-19"

# ── UM Predictions (fixed; must not be changed after registration) ─────────
W0_KK: float = -1.0
WA_KK: float = 0.0
R_KK: float = 0.0315
BETA_BRANCH_LOW: float = 0.273    # degrees — (5,6) sector branch
BETA_BRANCH_HIGH: float = 0.331   # degrees — (5,7) sector branch
BETA_FALSIFIER_LOW: float = 0.290  # gap lower bound (falsifier if β lands here)
BETA_FALSIFIER_HIGH: float = 0.310  # gap upper bound

# ── Protocol thresholds ────────────────────────────────────────────────────
# DESI: PASS = KK prediction within 2σ of DR3 best-fit (w₀, wₐ)
DESI_PASS_SIGMA: float = 2.0
# DESI: TENSION = 2–5σ from KK prediction
# DESI: FALSIFIED = >5σ from KK prediction AND wₐ ≠ 0 at >5σ
DESI_FALSIFIED_SIGMA: float = 5.0

# CMB-S4: PASS = r within 2σ of R_KK (including both above and below)
CMBS4_PASS_SIGMA: float = 2.0
# CMB-S4: FALSIFIED = r > 0.036 (BICEP/Keck bound already eliminates this from above)
#         or r < 0.020 (below the braided lower limit)
CMBS4_R_UPPER_FALSIFIER: float = 0.036
CMBS4_R_LOWER_FALSIFIER: float = 0.020

# LiteBIRD: PASS = β within 0.5σ_LB of either branch (σ_LB ≈ 0.02°)
LITEBIRD_SIGMA: float = 0.02       # degrees per LiteBIRD sensitivity projection
LITEBIRD_PASS_TOLERANCE: float = 3.0 * LITEBIRD_SIGMA   # 3σ window around each branch

# ── Protocol definitions (pre-registered, immutable) ──────────────────────
DESI_DR3_PROTOCOL: Dict = {
    "experiment": "DESI DR3",
    "expected_release": "2026",
    "prediction": {"w0": W0_KK, "wa": WA_KK},
    "pass_threshold": f"KK w0/wa within {DESI_PASS_SIGMA}σ of DR3 best-fit",
    "tension_threshold": f"KK w0/wa at {DESI_PASS_SIGMA}–{DESI_FALSIFIED_SIGMA}σ from DR3",
    "falsified_threshold": f"wₐ ≠ 0 at >{DESI_FALSIFIED_SIGMA}σ AND w0 ≠ −1 at >{DESI_FALSIFIED_SIGMA}σ",
    "registration_version": REGISTRATION_VERSION,
    "note": (
        "DESI Y1 shows ~3.5σ tension with ΛCDM (w₀, wₐ) ≠ (−1, 0). "
        "The UM prediction is identical to ΛCDM at this level (wₐ = 0 exactly). "
        "DR3 will either confirm the Y1 tension (→ TENSION for UM) or revert "
        "toward ΛCDM (→ PASS for UM). No post-hoc rescaling permitted."
    ),
}

CMB_S4_PROTOCOL: Dict = {
    "experiment": "CMB-S4 / Simons Observatory",
    "expected_release": "2028-2030",
    "prediction": {"r": R_KK},
    "pass_threshold": f"r within {CMBS4_PASS_SIGMA}σ of R_KK = {R_KK}",
    "falsified_threshold": f"r > {CMBS4_R_UPPER_FALSIFIER} or r < {CMBS4_R_LOWER_FALSIFIER}",
    "registration_version": REGISTRATION_VERSION,
    "note": (
        "The UM predicts r = 0.0315, just below the current BICEP/Keck bound of 0.036. "
        "CMB-S4 can detect r ~ 0.003 (3σ), so r = 0.0315 is clearly testable. "
        "A non-detection at r < 0.020 would falsify the braided inflation mechanism."
    ),
}

LITEBIRD_PROTOCOL: Dict = {
    "experiment": "LiteBIRD",
    "expected_launch": "~2032",
    "prediction": {
        "beta_branch_1": BETA_BRANCH_LOW,
        "beta_branch_2": BETA_BRANCH_HIGH,
        "falsifier_gap": [BETA_FALSIFIER_LOW, BETA_FALSIFIER_HIGH],
    },
    "pass_threshold": (
        f"β within {LITEBIRD_PASS_TOLERANCE:.3f}° of {BETA_BRANCH_LOW}° OR {BETA_BRANCH_HIGH}°"
    ),
    "falsified_threshold": (
        f"β ∈ ({BETA_FALSIFIER_LOW}°, {BETA_FALSIFIER_HIGH}°) — the gap between branches"
    ),
    "registration_version": REGISTRATION_VERSION,
    "note": (
        "This is the sharpest falsifier. The two branches are separated by a 0.058° gap "
        "(2.9σ_LB). A measurement in the gap falsifies the braided winding mechanism. "
        "A measurement outside [0.22°, 0.38°] also falsifies."
    ),
}


# ── Verdict functions ──────────────────────────────────────────────────────

def desi_verdict(w0_measured: float, wa_measured: float,
                  sigma_w0: float, sigma_wa: float) -> Dict:
    """
    Compute UM verdict given DESI measured (w₀, wₐ) with uncertainties.

    Uses simple χ² distance from KK prediction (w₀=−1, wₐ=0).
    """
    delta_w0 = abs(w0_measured - W0_KK) / sigma_w0
    delta_wa = abs(wa_measured - WA_KK) / sigma_wa
    combined_sigma = math.sqrt(delta_w0**2 + delta_wa**2)

    if combined_sigma <= DESI_PASS_SIGMA:
        verdict: Literal["PASS", "TENSION", "FALSIFIED"] = "PASS"
    elif combined_sigma <= DESI_FALSIFIED_SIGMA:
        verdict = "TENSION"
    else:
        verdict = "FALSIFIED"

    return {
        "experiment": "DESI DR3",
        "input": {"w0": w0_measured, "wa": wa_measured, "sigma_w0": sigma_w0, "sigma_wa": sigma_wa},
        "kk_prediction": {"w0": W0_KK, "wa": WA_KK},
        "delta_w0_sigma": round(delta_w0, 3),
        "delta_wa_sigma": round(delta_wa, 3),
        "combined_sigma": round(combined_sigma, 3),
        "verdict": verdict,
        "protocol_version": REGISTRATION_VERSION,
    }


def cmb_s4_verdict(r_measured: float, sigma_r: float) -> Dict:
    """Compute UM verdict given CMB-S4 measured r with uncertainty."""
    delta_r_sigma = abs(r_measured - R_KK) / sigma_r

    if r_measured > CMBS4_R_UPPER_FALSIFIER or r_measured < CMBS4_R_LOWER_FALSIFIER:
        verdict: Literal["PASS", "TENSION", "FALSIFIED"] = "FALSIFIED"
    elif delta_r_sigma <= CMBS4_PASS_SIGMA:
        verdict = "PASS"
    else:
        verdict = "TENSION"

    return {
        "experiment": "CMB-S4/Simons",
        "input": {"r": r_measured, "sigma_r": sigma_r},
        "kk_prediction": {"r": R_KK},
        "delta_r_sigma": round(delta_r_sigma, 3),
        "verdict": verdict,
        "protocol_version": REGISTRATION_VERSION,
    }


def litebird_verdict(beta_measured: float, sigma_beta: float) -> Dict:
    """Compute UM verdict given LiteBIRD measured β (degrees) with uncertainty."""
    dist_branch1 = abs(beta_measured - BETA_BRANCH_LOW)
    dist_branch2 = abs(beta_measured - BETA_BRANCH_HIGH)
    min_dist = min(dist_branch1, dist_branch2)
    sigma_dist = min_dist / sigma_beta

    in_gap = BETA_FALSIFIER_LOW < beta_measured < BETA_FALSIFIER_HIGH
    outside_window = beta_measured < 0.22 or beta_measured > 0.38

    if in_gap or outside_window:
        verdict: Literal["PASS", "TENSION", "FALSIFIED"] = "FALSIFIED"
    elif sigma_dist <= 3.0:
        verdict = "PASS"
    else:
        verdict = "TENSION"

    return {
        "experiment": "LiteBIRD",
        "input": {"beta_deg": beta_measured, "sigma_beta_deg": sigma_beta},
        "kk_prediction": {
            "branch_1": BETA_BRANCH_LOW,
            "branch_2": BETA_BRANCH_HIGH,
            "falsifier_gap": [BETA_FALSIFIER_LOW, BETA_FALSIFIER_HIGH],
        },
        "dist_to_branch1_sigma": round(dist_branch1 / sigma_beta, 3),
        "dist_to_branch2_sigma": round(dist_branch2 / sigma_beta, 3),
        "in_gap": in_gap,
        "outside_window": outside_window,
        "verdict": verdict,
        "protocol_version": REGISTRATION_VERSION,
    }


def run_all_protocols(
    desi_inputs: Dict | None = None,
    cmbs4_inputs: Dict | None = None,
    litebird_inputs: Dict | None = None,
) -> Dict:
    """
    Run all falsification protocols with optional current data.

    Pass None for any experiment to return AWAITING_DATA.
    """
    results: Dict = {}

    if desi_inputs is not None:
        results["desi"] = desi_verdict(**desi_inputs)
    else:
        results["desi"] = {"verdict": "AWAITING_DATA", "experiment": "DESI DR3",
                           "expected": "2026"}

    if cmbs4_inputs is not None:
        results["cmb_s4"] = cmb_s4_verdict(**cmbs4_inputs)
    else:
        results["cmb_s4"] = {"verdict": "AWAITING_DATA", "experiment": "CMB-S4/Simons",
                              "expected": "2028-2030"}

    if litebird_inputs is not None:
        results["litebird"] = litebird_verdict(**litebird_inputs)
    else:
        results["litebird"] = {"verdict": "AWAITING_DATA", "experiment": "LiteBIRD",
                                "expected": "~2032"}

    verdicts = [v["verdict"] for v in results.values()]
    has_falsified = "FALSIFIED" in verdicts
    has_tension = "TENSION" in verdicts

    results["overall_status"] = (
        "FALSIFIED" if has_falsified
        else "TENSION" if has_tension
        else "PASS_OR_AWAITING"
    )
    results["protocol_version"] = REGISTRATION_VERSION
    return results


def pillar_report() -> Dict:
    """Top-level pillar report (no data yet — protocols registered)."""
    all_protocols = run_all_protocols()
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "protocols_registered": 3,
        "protocol_results": all_protocols,
        "current_overall": all_protocols["overall_status"],
    }
