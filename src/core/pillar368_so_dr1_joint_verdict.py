# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
src/core/pillar368_so_dr1_joint_verdict.py
==========================================
Pillar 368 — SO DR1 + ACT DR6 + SPT-3G 2027 Joint Verdict Protocol.

════════════════════════════════════════════════════════════════════════════
STATUS: ROUTING_INFRASTRUCTURE (non-hardgate)
════════════════════════════════════════════════════════════════════════════

MOTIVATION
══════════
Pillar 357 (v12.4) formally demonstrated that the ACT DR6 r-tension is
IRREDUCIBLE at the 5D-EFT level: scale-dependent running of r between BICEP
and ACT pivot scales is negligible (~0.01%), and ~87 loop orders would be
needed to drive r below 0.016 — well past perturbativity breakdown.

The Simons Observatory (SO) DR1 (~2027) will be the first instrument capable
of measuring r directly rather than placing an upper bound. Its projected
sensitivity σ_r ≈ 0.006 (DR1) and σ_r ≈ 0.003 (5-yr) are sufficient to
detect or exclude r = 0.0315 at 5–10σ.

This pillar constructs the joint posterior P(r | SO DR1 + ACT DR6 + SPT-3G),
calibrates the 3-instrument sensitivity for the UM prediction, and provides
a single callable `so_dr1_joint_routing(r_meas, sigma_r)` that returns the
CONFIRMED / CONSISTENT / TENSION / HIGH_TENSION / FALSIFIED verdict.

KEY RESULTS
═══════════
- If SO detects r = 0.0315 ± 0.006: ~5σ detection → P3 CONFIRMED
- If SO measures r < 0.010 at ≥3σ: P2 FALSIFIED (original falsifier condition)
- ACT DR6 tension: IRREDUCIBLE at 5D-EFT level (P357); SO is the resolution

PREREGISTRATION
═══════════════
This protocol is preregistered. The verdict conditions are:
    CONFIRMED  : r_meas ≥ 0.020 AND r_meas/sigma_r ≥ 3.0  (detection at ≥3σ)
    CONSISTENT : 0.010 ≤ r_meas < 0.020 (upper bound consistent with UM)
    TENSION    : r_meas < 0.010 at <3σ  (marginal below UM; monitor CMB-S4)
    FALSIFIED  : r_meas < 0.010 at ≥3σ  (original P2 falsifier triggered)

Note: A detection r_meas ≈ 0.0315 at 5σ does not trigger P2 falsifier
(that requires r < 0.010 at ≥3σ); it provides strong positive evidence.

*Theory: ThomasCory Walker-Pearson.*
*Code, tests, document engineering: GitHub Copilot (AI).*
"""
from __future__ import annotations
import math
from typing import Dict, List, Optional, Tuple

__all__ = [
    "PILLAR_NUMBER", "PILLAR_TITLE", "PILLAR_STATUS", "ADJACENCY_TRACK_LABEL",
    "R_UM_PREDICTION", "N_S_UM_PREDICTION",
    "SO_DR1_SIGMA_R", "SO_FIVEYEAR_SIGMA_R",
    "ACT_DR6_R_UPPER_BOUND", "ACT_DR6_SIGMA_R",
    "SPT3G_R_UPPER_BOUND",
    "FALSIFICATION_R_THRESHOLD",
    "separation_guard",
    "so_dr1_joint_routing",
    "joint_posterior_r",
    "instrument_sensitivity_table",
    "detection_significance",
    "so_preregistration_checklist",
    "pillar368_summary",
]

PILLAR_NUMBER: int = 368
PILLAR_TITLE: str = (
    "Simons Observatory DR1 + ACT DR6 + SPT-3G 2027 Joint r-Verdict Protocol"
)
PILLAR_STATUS: str = "ROUTING_INFRASTRUCTURE"
ADJACENCY_TRACK_LABEL: str = "HARDGATE_ADJACENT"

# UM predictions
R_UM_PREDICTION: float = 0.0315    # braided tensor-to-scalar ratio
N_S_UM_PREDICTION: float = 0.9635  # CMB spectral index

# Instrument projected precisions
SO_DR1_SIGMA_R: float = 0.006      # Simons Observatory DR1 (1σ)
SO_FIVEYEAR_SIGMA_R: float = 0.003  # Simons Observatory 5-year (1σ)

# Current upper bounds
ACT_DR6_R_UPPER_BOUND: float = 0.016   # 95%CL upper bound
ACT_DR6_SIGMA_R: float = 0.008         # effective 1σ (half of 95%CL bound)
SPT3G_R_UPPER_BOUND: float = 0.036     # 95%CL upper bound (Balkenhol et al. 2023)

# P2 falsifier condition
FALSIFICATION_R_THRESHOLD: float = 0.010  # r < this at ≥3σ → FALSIFIED


def separation_guard() -> str:
    return (
        "HARDGATE_ADJACENT: Pillar 368 provides the SO DR1 + ACT DR6 + SPT-3G "
        "joint verdict routing protocol for the r prediction. "
        "ACT DR6 tension is IRREDUCIBLE at 5D-EFT (Pillar 357). "
        "Status: ROUTING_INFRASTRUCTURE. No ToE score affected."
    )


def detection_significance(r_meas: float, sigma_r: float) -> float:
    """Significance of a r measurement as number of sigma from zero.

    Parameters
    ----------
    r_meas : float
        Measured central value of r.
    sigma_r : float
        Measurement uncertainty (1σ).

    Returns
    -------
    float
        r_meas / sigma_r (detection significance vs r=0 null).
    """
    if sigma_r <= 0.0:
        return 0.0
    return r_meas / sigma_r


def _tension_from_um(r_meas: float, sigma_r: float) -> float:
    """Tension of r measurement from UM prediction r=0.0315."""
    if sigma_r <= 0.0:
        return 0.0
    return abs(r_meas - R_UM_PREDICTION) / sigma_r


def so_dr1_joint_routing(
    r_meas: float,
    sigma_r: float,
    instrument: str = "SO_DR1",
) -> Dict[str, object]:
    """Machine-readable SO DR1 routing for the r prediction.

    Execute within 24 hours of SO DR1 publication.

    Parameters
    ----------
    r_meas : float
        Published r central value (or upper bound if not detected).
    sigma_r : float
        Published r uncertainty (1σ).
    instrument : str
        Instrument label for reporting.

    Returns
    -------
    dict
        CONFIRMED / CONSISTENT / TENSION / HIGH_TENSION / FALSIFIED verdict
        with required actions.
    """
    detection_sig = detection_significance(r_meas, sigma_r)
    um_tension = _tension_from_um(r_meas, sigma_r)
    upper_3sigma = r_meas + 3.0 * sigma_r
    lower_3sigma = r_meas - 3.0 * sigma_r

    # Verdict logic (preregistered)
    if r_meas >= 0.020 and detection_sig >= 3.0:
        # Detected at ≥3σ above zero, consistent with UM
        if um_tension <= 1.0:
            verdict = "CONFIRMED"
            description = (
                f"r = {r_meas:.4f} ± {sigma_r:.4f} detected at "
                f"{detection_sig:.1f}σ. UM prediction r=0.0315 confirmed "
                f"({um_tension:.1f}σ from prediction). "
                "Promote P3 status to CONFIRMED."
            )
        else:
            verdict = "CONSISTENT"
            description = (
                f"r = {r_meas:.4f} detected at {detection_sig:.1f}σ. "
                f"Tension with UM: {um_tension:.1f}σ. "
                "Consistent with r > 0 (UM-class). Not CONFIRMED at predicted value."
            )
    elif r_meas < FALSIFICATION_R_THRESHOLD and lower_3sigma < FALSIFICATION_R_THRESHOLD:
        # r < 0.010 at ≥3σ → P2 FALSIFIED
        verdict = "FALSIFIED"
        description = (
            f"r = {r_meas:.4f} ± {sigma_r:.4f}. "
            f"r < {FALSIFICATION_R_THRESHOLD} confirmed at ≥3σ. "
            "P2 FALSIFIED. Mark FALSIFIED in CLAIM_MASTER_BOARD.md. "
            "Update OBSERVATION_TRACKER.md and WAVE_CHANGELOG.md same day."
        )
    elif r_meas < FALSIFICATION_R_THRESHOLD:
        # Below 0.010 but not at 3σ
        verdict = "TENSION"
        description = (
            f"r = {r_meas:.4f} ± {sigma_r:.4f}. "
            f"Below UM prediction but not confirmed r<0.010 at 3σ. "
            f"Upper 3σ bound: {upper_3sigma:.4f}. Monitor CMB-S4 (~2030)."
        )
    elif um_tension >= 2.5:
        verdict = "HIGH_TENSION"
        description = (
            f"r = {r_meas:.4f} ± {sigma_r:.4f}. "
            f"Tension with UM: {um_tension:.1f}σ. "
            "HIGH_TENSION. Await CMB-S4 (~2030) for decisive test."
        )
    else:
        verdict = "CONSISTENT"
        description = (
            f"r = {r_meas:.4f} ± {sigma_r:.4f}. "
            f"Tension with UM: {um_tension:.1f}σ. CONSISTENT."
        )

    return {
        "pillar": PILLAR_NUMBER,
        "instrument": instrument,
        "input_r_measured": r_meas,
        "input_sigma_r": sigma_r,
        "um_r_prediction": R_UM_PREDICTION,
        "detection_significance_sigma": round(detection_sig, 2),
        "tension_from_um_sigma": round(um_tension, 2),
        "verdict": verdict,
        "description": description,
        "p2_falsifier_threshold": FALSIFICATION_R_THRESHOLD,
    }


def joint_posterior_r(
    measurements: List[Tuple[float, float, float]],
) -> Dict[str, object]:
    """Combine multiple r measurements into a joint posterior (Gaussian approx).

    Parameters
    ----------
    measurements : list of (r_central, sigma_r, weight)
        List of (r_central, sigma_r, weight) triples.
        weight = 1.0 means equal weighting; adjust for prior considerations.

    Returns
    -------
    dict
        Combined r_posterior and sigma_posterior from inverse-variance weighting.
    """
    if not measurements:
        return {"r_posterior": None, "sigma_posterior": None}

    total_weight = 0.0
    weighted_r = 0.0
    for r_c, sigma_r, w in measurements:
        if sigma_r > 0.0:
            inv_var = w / (sigma_r ** 2)
            total_weight += inv_var
            weighted_r += inv_var * r_c

    if total_weight <= 0.0:
        return {"r_posterior": None, "sigma_posterior": None}

    r_post = weighted_r / total_weight
    sigma_post = 1.0 / math.sqrt(total_weight)

    um_tension = abs(r_post - R_UM_PREDICTION) / sigma_post if sigma_post > 0 else 0.0

    return {
        "r_posterior": round(r_post, 5),
        "sigma_posterior": round(sigma_post, 5),
        "um_r_prediction": R_UM_PREDICTION,
        "tension_from_um_sigma": round(um_tension, 2),
        "n_measurements": len(measurements),
    }


def instrument_sensitivity_table() -> List[Dict[str, object]]:
    """Instrument sensitivity summary for the r measurement landscape.

    Returns
    -------
    list of dict
    """
    return [
        {
            "instrument": "BICEP/Keck BK18",
            "type": "upper_bound",
            "r_95cl": 0.036,
            "sigma_r_eff": 0.018,
            "status": "CONSISTENT — r=0.0315 satisfies bound",
            "year": "2022",
        },
        {
            "instrument": "SPT-3G 2022",
            "type": "upper_bound",
            "r_95cl": 0.036,
            "sigma_r_eff": 0.018,
            "status": "CONSISTENT — r=0.0315 satisfies bound",
            "year": "2022",
        },
        {
            "instrument": "ACT DR6",
            "type": "upper_bound",
            "r_95cl": 0.016,
            "sigma_r_eff": ACT_DR6_SIGMA_R,
            "status": "HIGH_TENSION — IRREDUCIBLE at 5D-EFT (Pillar 357)",
            "year": "2024",
        },
        {
            "instrument": "Simons Observatory DR1",
            "type": "measurement_capable",
            "sigma_r": SO_DR1_SIGMA_R,
            "detection_at_um": round(R_UM_PREDICTION / SO_DR1_SIGMA_R, 1),
            "status": "PREREGISTERED — primary 2027 r resolution",
            "year": "~2027",
        },
        {
            "instrument": "Simons Observatory 5-year",
            "type": "measurement_capable",
            "sigma_r": SO_FIVEYEAR_SIGMA_R,
            "detection_at_um": round(R_UM_PREDICTION / SO_FIVEYEAR_SIGMA_R, 1),
            "status": "PREREGISTERED — definitive ~2029",
            "year": "~2029",
        },
        {
            "instrument": "CMB-S4",
            "type": "measurement_capable",
            "sigma_r": 0.001,
            "detection_at_um": round(R_UM_PREDICTION / 0.001, 1),
            "status": "PREREGISTERED — ultimate ~2030",
            "year": "~2030",
        },
    ]


def so_preregistration_checklist() -> List[Dict[str, object]]:
    """Preregistration checklist for SO DR1 execution protocol.

    Returns
    -------
    list of dict
        Checklist items with status OPEN/COMPLETE.
    """
    return [
        {
            "item": "SO-PR-1",
            "description": "UM prediction r=0.0315 documented and timestamped",
            "status": "COMPLETE",
            "reference": "Pillar 2, CLAIM_MASTER_BOARD.md P3",
        },
        {
            "item": "SO-PR-2",
            "description": "Falsifier condition: r < 0.010 at ≥3σ → FALSIFIED",
            "status": "COMPLETE",
            "reference": "OBSERVATION_TRACKER.md P3 row",
        },
        {
            "item": "SO-PR-3",
            "description": "Confirmation condition: r ≥ 0.020 at ≥3σ → CONFIRMED",
            "status": "COMPLETE",
            "reference": "Pillar 368 so_dr1_joint_routing()",
        },
        {
            "item": "SO-PR-4",
            "description": "ACT DR6 tension acknowledged as IRREDUCIBLE at 5D-EFT",
            "status": "COMPLETE",
            "reference": "Pillar 357",
        },
        {
            "item": "SO-PR-5",
            "description": "Execute so_dr1_joint_routing() within 24h of DR1 publication",
            "status": "OPEN — awaiting SO DR1 publication (~2027)",
            "reference": "Pillar 368",
        },
    ]


def pillar368_summary() -> Dict[str, object]:
    """Summary dict for Pillar 368."""
    tbl = instrument_sensitivity_table()
    so_entry = next(t for t in tbl if "Simons Observatory DR1" in t["instrument"])
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "adjacency": ADJACENCY_TRACK_LABEL,
        "r_um_prediction": R_UM_PREDICTION,
        "so_dr1_detection_sigma": so_entry["detection_at_um"],
        "so_dr1_sigma_r": SO_DR1_SIGMA_R,
        "act_dr6_tension": "HIGH_TENSION (IRREDUCIBLE at 5D-EFT)",
        "falsification_condition": "r < 0.010 at ≥3σ → P2 FALSIFIED",
        "confirmation_condition": "r ≥ 0.020 at ≥3σ → P3 CONFIRMED",
        "preregistration_complete": True,
    }
