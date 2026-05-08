# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
desi_year3_monitor.py — DESI Year 3 / wₐ tension monitoring harness.

═══════════════════════════════════════════════════════════════════════════
PURPOSE
═══════════════════════════════════════════════════════════════════════════
The Pillar 155 module (kk_de_wa_cpl.py) documents the 2.1σ wₐ tension
between the UM prediction (wₐ = 0) and DESI DR2 (wₐ = −0.62 ± 0.30).

This monitoring harness:
  1. Stores the current observational state (DESI DR2 baseline).
  2. Provides a structured comparison framework for DESI Year 3 results
     (~2026) when they become available.
  3. Tracks the tension evolution as a function of the wₐ central value
     and uncertainty.
  4. Documents the UM falsification condition for the wₐ parameter.

═══════════════════════════════════════════════════════════════════════════
DESI YEAR 3 FALSIFICATION CONDITIONS
═══════════════════════════════════════════════════════════════════════════
The UM predicts wₐ = 0 exactly (frozen GW radion).

  • If DESI Year 3 gives wₐ = 0 consistent at < 1σ → UM consistent ✅
  • If DESI Year 3 gives wₐ ≠ 0 at > 3σ → UM predicts wₐ = 0 is excluded:
      Tension documented as HONEST_OPEN_PROBLEM.
      Resolution requires either:
        (a) A new geometric sector in the UM beyond the radion, or
        (b) Systematic effects in DESI (lensing, CMB cross-calibration).

CURRENT STATUS (DESI DR2, arXiv:2503.14738):
  w₀ = −0.838 ± 0.072  →  UM w₀ = −0.9302 at 1.3σ  ✅ CONSISTENT
  wₐ = −0.62 ± 0.30   →  UM wₐ = 0 at 2.1σ        ⚠️ OPEN TENSION

═══════════════════════════════════════════════════════════════════════════

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional

__all__ = [
    # Baseline data
    "DESI_DR2",
    "UM_PREDICTION",
    "MONITOR_INTEGRATION_TARGETS",
    # Functions
    "tension_from_measurement",
    "routing_decision",
    "update_with_new_data",
    "falsification_verdict",
    "monitoring_report",
    "desi_year3_placeholder",
]

# ---------------------------------------------------------------------------
# Baseline observational data (DESI DR2)
# ---------------------------------------------------------------------------

#: DESI DR2 CPL constraints (arXiv:2503.14738, 2025)
DESI_DR2: Dict = {
    "release": "DESI DR2",
    "year": 2025,
    "reference": "DESI Collaboration (2025), arXiv:2503.14738",
    "w0_central": -0.838,
    "w0_sigma": 0.072,
    "wa_central": -0.62,
    "wa_sigma": 0.30,
    "datasets": "BAO + CMB + SNe Ia",
    "status": "CURRENT_BASELINE",
}

MONITOR_INTEGRATION_TARGETS: List[str] = [
    "src/core/kk_de_wa_cpl.py",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "src/core/canonical_falsifier_evidence_feed.py",
]

#: UM predictions for w₀ and wₐ
UM_PREDICTION: Dict = {
    "w0": -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2,  # = W_KK ≈ −0.9302
    "wa": 0.0,
    "mechanism_w0": "w₀ = −1 + (2/3)c_s² with c_s = 12/37 (braided KK zero-mode)",
    "mechanism_wa": "wₐ = 0 (GW-stabilised radion frozen at m_r >> H₀)",
    "falsification_wa": "wₐ ≠ 0 at > 3σ would require new geometric sector",
    "module": "src/core/kk_de_wa_cpl.py (Pillar 155)",
}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def tension_from_measurement(
    w0_obs: float,
    w0_sigma: float,
    wa_obs: float,
    wa_sigma: float,
    release_name: str = "custom",
) -> Dict:
    """Compute UM tension vs an observed CPL measurement.

    Parameters
    ----------
    w0_obs : float   Observed w₀ central value.
    w0_sigma : float Observed w₀ uncertainty (1σ).
    wa_obs : float   Observed wₐ central value.
    wa_sigma : float Observed wₐ uncertainty (1σ).
    release_name : str  Name of the data release.

    Returns
    -------
    dict with tension analysis and consistency verdict.
    """
    w0_um = UM_PREDICTION["w0"]
    wa_um = UM_PREDICTION["wa"]

    tension_w0 = abs(w0_um - w0_obs) / w0_sigma if w0_sigma > 0 else float("inf")
    tension_wa = abs(wa_um - wa_obs) / wa_sigma if wa_sigma > 0 else float("inf")

    consistent_w0 = tension_w0 < 2.0
    consistent_wa = tension_wa < 2.0
    tension_combined = math.sqrt(tension_w0**2 + tension_wa**2)

    return {
        "release": release_name,
        "um_w0": w0_um,
        "obs_w0": w0_obs,
        "obs_w0_sigma": w0_sigma,
        "tension_w0_sigma": tension_w0,
        "consistent_w0": consistent_w0,
        "um_wa": wa_um,
        "obs_wa": wa_obs,
        "obs_wa_sigma": wa_sigma,
        "tension_wa_sigma": tension_wa,
        "consistent_wa": consistent_wa,
        "tension_combined_sigma": tension_combined,
        "overall_consistent": consistent_w0 and consistent_wa,
        "verdict": (
            "CONSISTENT ✅" if (consistent_w0 and consistent_wa)
            else f"PARTIAL_TENSION ⚠️ (w₀: {tension_w0:.1f}σ, wₐ: {tension_wa:.1f}σ)"
        ),
    }


def routing_decision(
    w0_tension_sigma: float,
    wa_tension_sigma: float,
    release_name: str,
    year: int,
) -> Dict[str, object]:
    """Route a new dark-energy release into PASS/TENSION/FALSIFIED buckets."""
    if wa_tension_sigma >= 3.0:
        route = "FALSIFIED"
        status = "❌ FALSIFIED"
        action = (
            "Update kk_de_wa_cpl.py, OBSERVATION_TRACKER.md, and the canonical "
            "falsifier feed immediately; record the ≥3σ Year-3 exclusion."
        )
    elif wa_tension_sigma >= 1.0 or w0_tension_sigma >= 2.0:
        route = "TENSION"
        status = "🟠 TENSION"
        action = (
            "Record the release as monitored tension; keep the gap open and do "
            "not claim any rescue without a new geometric sector."
        )
    else:
        route = "PASS"
        status = "🟢 PASS"
        action = (
            "Record the release as consistent in the tracker, sync the canonical "
            "feed, and preserve wₐ = 0 as unfalsified."
        )

    return {
        "route": route,
        "status": status,
        "release": release_name,
        "year": year,
        "integration_targets": list(MONITOR_INTEGRATION_TARGETS),
        "action": action,
    }


def update_with_new_data(
    release_name: str,
    year: int,
    w0_central: float,
    w0_sigma: float,
    wa_central: float,
    wa_sigma: float,
    reference: str = "",
    datasets: str = "",
) -> Dict:
    """Process new observational data and compare with UM prediction.

    This function is designed to be called when new DESI (or other)
    results become available.  It returns a full comparison report.

    Parameters
    ----------
    release_name : str  Name of the data release (e.g. "DESI Year 3").
    year : int          Year of the release.
    w0_central : float  Observed w₀ central value.
    w0_sigma : float    Observed w₀ uncertainty.
    wa_central : float  Observed wₐ central value.
    wa_sigma : float    Observed wₐ uncertainty.
    reference : str     Reference (arXiv or journal).
    datasets : str      Datasets used (e.g. "BAO + CMB + SNe Ia").

    Returns
    -------
    dict with full comparison vs DESI DR2 baseline and UM prediction.
    """
    new_tension = tension_from_measurement(
        w0_central, w0_sigma, wa_central, wa_sigma, release_name
    )
    dr2_tension = tension_from_measurement(
        DESI_DR2["w0_central"],
        DESI_DR2["w0_sigma"],
        DESI_DR2["wa_central"],
        DESI_DR2["wa_sigma"],
        "DESI DR2 baseline",
    )

    # Compute improvement vs DESI DR2 baseline
    wa_tension_dr2 = dr2_tension["tension_wa_sigma"]
    wa_tension_new = new_tension["tension_wa_sigma"]
    wa_improvement = wa_tension_dr2 - wa_tension_new
    routing = routing_decision(
        new_tension["tension_w0_sigma"],
        new_tension["tension_wa_sigma"],
        release_name,
        year,
    )

    return {
        "release": release_name,
        "year": year,
        "reference": reference,
        "datasets": datasets,
        "new_data": {
            "w0_central": w0_central,
            "w0_sigma": w0_sigma,
            "wa_central": wa_central,
            "wa_sigma": wa_sigma,
        },
        "um_tension": new_tension,
        "baseline_tension": dr2_tension,
        "routing": routing,
        "wa_tension_improvement_sigma": wa_improvement,
        "wording": (
            f"{release_name} ({year}): wₐ = {wa_central:.2f} ± {wa_sigma:.2f}. "
            f"UM tension: {wa_tension_new:.1f}σ (vs {wa_tension_dr2:.1f}σ at DESI DR2). "
            f"{'Tension reduced ✅' if wa_improvement > 0 else 'Tension increased ⚠️'}."
        ),
    }


def falsification_verdict(wa_obs: float, wa_sigma: float) -> Dict:
    """Return falsification verdict for the UM wₐ = 0 prediction.

    Parameters
    ----------
    wa_obs : float   Observed wₐ central value.
    wa_sigma : float Observed wₐ uncertainty (1σ).

    Returns
    -------
    dict with falsification assessment.
    """
    wa_um = 0.0
    tension = abs(wa_um - wa_obs) / wa_sigma if wa_sigma > 0 else float("inf")

    if tension < 1.0:
        verdict = "CONSISTENT — UM wₐ=0 within 1σ ✅"
        level = "CONSISTENT"
    elif tension < 2.0:
        verdict = f"MARGINAL — UM wₐ=0 at {tension:.1f}σ; monitoring required ⚠️"
        level = "MARGINAL"
    elif tension < 3.0:
        verdict = f"TENSION — UM wₐ=0 at {tension:.1f}σ; HONEST_OPEN_PROBLEM ⚠️"
        level = "TENSION"
    else:
        verdict = f"EXCLUDED — UM wₐ=0 at {tension:.1f}σ; requires new geometric sector 🔴"
        level = "EXCLUDED"

    return {
        "wa_um_prediction": wa_um,
        "wa_observed": wa_obs,
        "wa_sigma": wa_sigma,
        "tension_sigma": tension,
        "verdict": verdict,
        "level": level,
        "action_required": (
            "Document as HONEST_OPEN_PROBLEM in FALLIBILITY.md"
            if level in ("TENSION", "EXCLUDED")
            else "No action — within observational uncertainty"
        ),
    }


def monitoring_report() -> Dict:
    """Generate current monitoring report vs DESI DR2 baseline.

    Returns
    -------
    dict with full monitoring state.
    """
    dr2 = tension_from_measurement(
        DESI_DR2["w0_central"],
        DESI_DR2["w0_sigma"],
        DESI_DR2["wa_central"],
        DESI_DR2["wa_sigma"],
        "DESI DR2",
    )
    verdict = falsification_verdict(DESI_DR2["wa_central"], DESI_DR2["wa_sigma"])
    routing = routing_decision(
        dr2["tension_w0_sigma"],
        dr2["tension_wa_sigma"],
        DESI_DR2["release"],
        DESI_DR2["year"],
    )

    return {
        "version": "v10.26",
        "current_baseline": DESI_DR2,
        "um_prediction": UM_PREDICTION,
        "current_tension": dr2,
        "falsification_verdict": verdict,
        "routing": routing,
        "next_milestone": {
            "release": "DESI Year 3",
            "expected_year": 2026,
            "expected_wa_sigma": 0.20,
            "note": (
                "DESI Year 3 (~2026) is expected to reduce wₐ uncertainty "
                "to ~0.20. If wₐ remains at −0.62 with σ=0.20, tension rises "
                "to ~3.1σ — potential falsification of UM wₐ=0."
            ),
        },
        "update_instructions": (
            "When DESI Year 3 results are available, call:\n"
            "  update_with_new_data('DESI Year 3', 2026, w0_obs, w0_err, wa_obs, wa_err, ref, datasets)"
        ),
    }


def desi_year3_placeholder() -> Dict:
    """Placeholder for DESI Year 3 data (to be filled when available).

    Returns
    -------
    dict with placeholder status.
    """
    return {
        "release": "DESI Year 3",
        "year": 2026,
        "status": "PENDING — results not yet published",
        "expected_datasets": "BAO Year 3 + CMB (ACT DR6 / Planck PR4) + DESY5 SNe",
        "expected_improvement": "~2× improvement in wₐ precision (σ_wₐ ≈ 0.15–0.20)",
        "um_falsification_threshold": (
            "If wₐ ≠ 0 at > 3σ with Year 3 data → UM wₐ=0 excluded; "
            "requires new geometric sector (quintessence or bulk field)."
        ),
        "action_on_release": (
            "Update DESI_DR3 dict and call update_with_new_data() to refresh "
            "the tension analysis automatically."
        ),
        "integration_targets": list(MONITOR_INTEGRATION_TARGETS),
    }
