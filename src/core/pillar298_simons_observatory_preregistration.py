# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 298 — Simons Observatory CMB Preregistration Package.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

The Simons Observatory (SO) Large Aperture Telescope (LAT) is currently
operating at the Atacama site in Chile, having commenced commissioning in
late 2023 / early 2024.  Unlike previous CMB experiments that only set upper
limits on r, SO is projected to make a direct *measurement* of the tensor-
to-scalar ratio (or a firm upper limit below the P2 falsifier threshold) well
before CMB-S4 (~2030).  This module formally preregisters the Unitary
Manifold's routing rules for SO, modelled on the JUNO DR1 preregistration
package and the ACT DR6 / SPT-3G routing (Pillars 288, 292, 297).

Simons Observatory science goals
---------------------------------
Reference: The Simons Observatory Science Goals and Forecasts
  (SO Collaboration, arXiv:1808.07445, 2019)

  LAT configuration (5-year baseline):
    - r sensitivity:     σ_r ~ 0.003  (95% CL limit: r < 0.006 if null)
    - n_s sensitivity:   σ_{n_s} ~ 0.002
    - Sky coverage:      f_sky ~ 0.40

  DR1 estimate (1–2 year baseline, early science):
    - r sensitivity:     σ_r ~ 0.005–0.008  (conservative estimate)
    - Expected year:     2026–2027

SO vs. ACT DR6 vs. SPT-3G comparison
---------------------------------------
  ACT DR6 (2024):   r < 0.016 (95% CL upper limit)
  SPT-3G (2022):    r < 0.036 (95% CL upper limit)
  SO DR1 (est.):    σ_r ~ 0.005 → measurement-capable (not just upper limit)
  SO 5-yr:          σ_r ~ 0.003 → will either measure r or set < 0.010 limit

For the Unitary Manifold (r = 0.0315), the SO 5-year projection implies:
  - If r = 0.0315 is true: SO should *detect* it at ~10σ (5-yr) or ~4–6σ (DR1)
  - If SO sets r < 0.010 limit at ≥3σ: P2 falsifier triggered (FALSIFIED)
  - If SO sets r < 0.020 but does not measure < 0.010: TENSION_MAINTAINED

Crucially, SO is the first ground-based experiment that, under the UM
prediction, should *measure* (not just bound) the tensor-to-scalar ratio —
resolving whether the ACT DR6 HIGH_TENSION is a systematic effect or a real
limit.

UM predictions vs. SO projections
------------------------------------
  n_s = 0.9635 (DERIVED, P1): at σ_{n_s}~0.002, pull ~ 1.1σ → TENSION possible
  r   = 0.0315 (DERIVED, P2): at σ_r~0.003, detectable at ~10σ (5-yr)

Preregistered routing thresholds (locked at v11.10)
----------------------------------------------------
  These thresholds are locked at preregistration and must not be adjusted
  post-hoc, following the protocol established in Pillars 247, 288, 292, 294.

  SO DR1 r routing:
    r_meas ≥ 0.020 (central value, any CL): CONSISTENT — UM prediction
        in measurement band; strengthen P2 status; log OBSERVATION_TRACKER
    0.010 ≤ r_meas < 0.020 at ≥2σ:         TENSION_MAINTAINED — same
        HIGH_TENSION category as ACT DR6; await SO 5-yr and CMB-S4
    r_meas < 0.010 at ≥3σ:                 FALSIFIED — P2 falsifier
        triggered; immediate action required (see Docs to Update)

  SO 5-yr n_s routing:
    |n_s_meas − 0.9635| / σ_{n_s} < 2.0:   CONSISTENT
    2.0 ≤ pull < 3.0:                        TENSION
    pull ≥ 3.0:                              FALSIFIED (P1 falsifier)

  Note: The P1 falsifier condition is n_s ∉ [0.955, 0.972] at <0.001 precision.
  At SO 5-yr precision (σ~0.002), the pull of 0.9635 from n_s=0.955 (lower
  falsifier boundary) would be ~4.3σ — already distinguishable.
"""
from __future__ import annotations

import math
from typing import Dict, List

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "PILLAR_NUMBER",
    "PILLAR_TITLE",
    "UM_R_HARDGATED",
    "UM_NS_HARDGATED",
    "SO_SIGMA_R_DR1",
    "SO_SIGMA_R_5YR",
    "SO_SIGMA_NS_5YR",
    "SO_DR1_YEAR_EST",
    "SO_5YR_YEAR_EST",
    "SO_FSKY",
    "P1_FALSIFIER_NS_LOW",
    "P1_FALSIFIER_NS_HIGH",
    "P2_FALSIFIER_R_THRESHOLD",
    "SO_ROUTING_CONSISTENT_R",
    "SO_ROUTING_FALSIFIED_R",
    "DOCS_TO_UPDATE",
    "separation_guard",
    "so_r_detection_snr",
    "so_ns_pull",
    "so_dr1_r_routing",
    "so_5yr_r_routing",
    "so_ns_routing",
    "so_preregistration_checklist",
    "so_preregistration_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
PILLAR_NUMBER: int = 298
PILLAR_TITLE: str = "Simons Observatory CMB Preregistration Package"
OPERATIONAL_MODULE: bool = True
OPERATIONAL_MODULE_CATEGORY: str = "PREREGISTRATION_DOCUMENT"

# UM hardgated predictions
UM_R_HARDGATED: float = 0.0315    # P2 DERIVED (braided winding)
UM_NS_HARDGATED: float = 0.9635   # P1 DERIVED

# Simons Observatory projected sensitivities (arXiv:1808.07445)
SO_SIGMA_R_DR1: float = 0.006     # DR1 estimate (conservative 1-yr baseline)
SO_SIGMA_R_5YR: float = 0.003     # 5-year LAT baseline
SO_SIGMA_NS_5YR: float = 0.002    # 5-year n_s sensitivity
SO_DR1_YEAR_EST: int = 2027       # estimated DR1 release year
SO_5YR_YEAR_EST: int = 2029       # estimated 5-yr data release
SO_FSKY: float = 0.40             # LAT sky coverage fraction

# P1 falsifier bounds
P1_FALSIFIER_NS_LOW: float = 0.955   # n_s < 0.955 at <0.001 → FALSIFIED
P1_FALSIFIER_NS_HIGH: float = 0.972  # n_s > 0.972 at <0.001 → FALSIFIED

# P2 falsifier threshold
P2_FALSIFIER_R_THRESHOLD: float = 0.010  # r < 0.010 at ≥3σ *measured* → FALSIFIED

# Preregistered SO routing thresholds
SO_ROUTING_CONSISTENT_R: float = 0.020    # r ≥ 0.020 (central value) → CONSISTENT
SO_ROUTING_FALSIFIED_R: float = 0.010     # r < 0.010 at ≥3σ → FALSIFIED

# Documents to update upon SO measurement
DOCS_TO_UPDATE: List[str] = [
    "docs/CLAIM_MASTER_BOARD.md",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "FALLIBILITY.md",
    "docs/TRUTH_LAYER.md",
    "docs/GATEKEEPER_SUMMARY.md",
    "docs/WAVE_CHANGELOG.md",
    "STATUS.md",
]


def separation_guard() -> Dict[str, object]:
    """Non-hardgate separation guard for Pillar 298."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "alters_falsifier_window": False,
        "preregistration": True,
        "target_experiment": "Simons Observatory",
        "expected_dr1_year": SO_DR1_YEAR_EST,
        "expected_5yr_year": SO_5YR_YEAR_EST,
    }


def so_r_detection_snr(
    r_true: float = UM_R_HARDGATED,
    sigma_r: float = SO_SIGMA_R_5YR,
) -> Dict[str, object]:
    """Compute the SNR for SO to detect the UM r prediction.

    If r_true = 0.0315 and sigma_r = SO_SIGMA_R_5YR = 0.003:
        SNR = r_true / sigma_r = 0.0315 / 0.003 = 10.5σ

    This means the Unitary Manifold predicts SO (5-yr) should DETECT
    the tensor-to-scalar ratio at ~10σ.  If SO does NOT detect a signal,
    it either means (a) r < 0.010 (approaching falsification), or
    (b) the measurement falls in the 0.010–0.020 range (tension maintained).

    Parameters
    ----------
    r_true : float
        Assumed true r value (default: UM prediction 0.0315).
    sigma_r : float
        1σ sensitivity on r (default: SO 5-yr).
    """
    if sigma_r <= 0.0:
        raise ValueError("sigma_r must be positive")
    snr = r_true / sigma_r
    detectable_3sigma = snr >= 3.0
    detectable_5sigma = snr >= 5.0
    return {
        "r_assumed": r_true,
        "sigma_r": sigma_r,
        "snr": snr,
        "detectable_at_3sigma": detectable_3sigma,
        "detectable_at_5sigma": detectable_5sigma,
        "experiment": "Simons Observatory",
        "note": (
            f"If UM r={r_true} is correct, SO should detect it at {snr:.1f}σ. "
            "A non-detection at ≥5σ level effectively sets r < limit, "
            "routing to TENSION_MAINTAINED or FALSIFIED depending on the limit."
        ),
    }


def so_ns_pull(sigma_ns: float = SO_SIGMA_NS_5YR) -> Dict[str, object]:
    """Compute the expected n_s pull at SO 5-yr precision.

    With σ_{n_s} ~ 0.002 (SO 5-yr), the UM prediction n_s = 0.9635
    is pulled from:
      - Planck central value 0.9649: (0.9649 - 0.9635)/0.002 = 0.70σ → CONSISTENT
      - P1 falsifier lower bound 0.955: (0.9635 - 0.955)/0.002 = 4.25σ distinguishable

    Parameters
    ----------
    sigma_ns : float
        1σ sensitivity on n_s (default: SO 5-yr ~0.002).
    """
    if sigma_ns <= 0.0:
        raise ValueError("sigma_ns must be positive")
    planck_ns = 0.9649
    pull_from_planck = abs(UM_NS_HARDGATED - planck_ns) / sigma_ns
    pull_from_falsifier_low = abs(UM_NS_HARDGATED - P1_FALSIFIER_NS_LOW) / sigma_ns
    return {
        "um_ns": UM_NS_HARDGATED,
        "planck_ns": planck_ns,
        "sigma_ns": sigma_ns,
        "pull_from_planck_sigma": pull_from_planck,
        "p1_falsifier_low": P1_FALSIFIER_NS_LOW,
        "p1_falsifier_high": P1_FALSIFIER_NS_HIGH,
        "pull_from_falsifier_low_sigma": pull_from_falsifier_low,
        "p1_distinguishable": pull_from_falsifier_low > 2.0,
        "ns_verdict_expected": (
            "CONSISTENT" if pull_from_planck < 2.0 else "TENSION"
        ),
    }


def so_dr1_r_routing(
    r_measured: float,
    sigma_r: float,
) -> Dict[str, object]:
    """Route a SO DR1 r measurement to a verdict.

    Parameters
    ----------
    r_measured : float
        Central value of r from SO DR1.
    sigma_r : float
        1σ uncertainty on r.
    """
    if sigma_r <= 0.0:
        raise ValueError("sigma_r must be positive")
    pull_from_um = (r_measured - UM_R_HARDGATED) / sigma_r
    pull_from_zero = r_measured / sigma_r if r_measured > 0 else 0.0
    # Classify by routing threshold
    if r_measured >= SO_ROUTING_CONSISTENT_R:
        verdict = "CONSISTENT"
        action = (
            "P2 HIGH_TENSION resolved → CONSISTENT. "
            "Update CLAIM_MASTER_BOARD.md P3 row and OBSERVATION_TRACKER.md. "
            "CMB-S4 will provide definitive confirmation."
        )
    elif r_measured < SO_ROUTING_FALSIFIED_R and pull_from_zero >= 3.0:
        verdict = "FALSIFIED"
        action = (
            "P2 falsifier triggered: r < 0.010 at ≥3σ measured. "
            "Update all truth surfaces immediately. Open retraction issue."
        )
    else:
        verdict = "TENSION_MAINTAINED"
        action = (
            f"r={r_measured:.4f} in tension zone [{SO_ROUTING_FALSIFIED_R}, "
            f"{SO_ROUTING_CONSISTENT_R}). Maintain HIGH_TENSION status. "
            "Await SO 5-yr and CMB-S4 for resolution."
        )
    return {
        "experiment": "Simons Observatory DR1",
        "r_measured": r_measured,
        "sigma_r": sigma_r,
        "um_r": UM_R_HARDGATED,
        "pull_from_um": pull_from_um,
        "pull_from_zero": pull_from_zero,
        "verdict": verdict,
        "action": action,
        "p2_falsifier_triggered": verdict == "FALSIFIED",
    }


def so_5yr_r_routing(
    r_measured: float,
    sigma_r: float,
) -> Dict[str, object]:
    """Route a SO 5-year r measurement to a verdict.

    The same routing thresholds apply as DR1, but at higher precision
    (sigma_r ~ 0.003).  The key difference is that at 5-yr precision,
    UM predicts a ~10σ detection if r = 0.0315.

    Parameters
    ----------
    r_measured : float
        Central value of r from SO 5-yr data.
    sigma_r : float
        1σ uncertainty on r.
    """
    return so_dr1_r_routing(r_measured, sigma_r)


def so_ns_routing(
    ns_measured: float,
    sigma_ns: float,
) -> Dict[str, object]:
    """Route a SO n_s measurement to a verdict.

    Parameters
    ----------
    ns_measured : float
        Central value of n_s from SO.
    sigma_ns : float
        1σ uncertainty on n_s.
    """
    if sigma_ns <= 0.0:
        raise ValueError("sigma_ns must be positive")
    pull_from_um = abs(ns_measured - UM_NS_HARDGATED) / sigma_ns
    outside_falsifier = (
        ns_measured < P1_FALSIFIER_NS_LOW or ns_measured > P1_FALSIFIER_NS_HIGH
    )
    if outside_falsifier and pull_from_um >= 3.0:
        verdict = "FALSIFIED"
        action = "P1 falsifier triggered. Open retraction issue immediately."
    elif pull_from_um < 2.0:
        verdict = "CONSISTENT"
        action = "P1 remains CONSISTENT. Update OBSERVATION_TRACKER.md."
    else:
        verdict = "TENSION"
        action = "P1 tension elevated. Monitor CMB-S4 for resolution."
    return {
        "experiment": "Simons Observatory",
        "ns_measured": ns_measured,
        "sigma_ns": sigma_ns,
        "um_ns": UM_NS_HARDGATED,
        "pull_from_um": pull_from_um,
        "verdict": verdict,
        "action": action,
        "p1_falsifier_triggered": verdict == "FALSIFIED",
    }


def so_preregistration_checklist() -> List[Dict[str, object]]:
    """Return the preregistered action checklist for SO data release.

    This checklist mirrors the JUNO DR1 preregistration pattern and
    the DESI DR3 publication-day runbook.
    """
    return [
        {
            "step": 1,
            "action": "Download SO DR1 / 5-yr CMB power spectrum within 24 hours",
            "key_quantities": ["r_measured", "sigma_r", "ns_measured", "sigma_ns"],
        },
        {
            "step": 2,
            "action": "Call `so_dr1_r_routing(r_measured, sigma_r)` for r verdict",
            "module": "pillar298_simons_observatory_preregistration",
        },
        {
            "step": 3,
            "action": "Call `so_ns_routing(ns_measured, sigma_ns)` for n_s verdict",
            "module": "pillar298_simons_observatory_preregistration",
        },
        {
            "step": 4,
            "action": "Update OBSERVATION_TRACKER.md Observational Record row for SO",
            "deadline": "Within 30 days of SO DR1 publication",
        },
        {
            "step": 5,
            "action": "Update CLAIM_MASTER_BOARD.md P2 (r) and P1 (n_s) rows",
            "deadline": "Same day as verdict",
        },
        {
            "step": 6,
            "action": "If FALSIFIED: open retraction issue + update all truth surfaces",
            "docs": DOCS_TO_UPDATE,
        },
        {
            "step": 7,
            "action": "Add entry to WAVE_CHANGELOG.md with full epistemic impact",
            "deadline": "Within 7 days of verdict",
        },
    ]


def so_preregistration_report() -> Dict[str, object]:
    """Generate the complete Simons Observatory preregistration report."""
    guard = separation_guard()
    r_snr_dr1 = so_r_detection_snr(sigma_r=SO_SIGMA_R_DR1)
    r_snr_5yr = so_r_detection_snr(sigma_r=SO_SIGMA_R_5YR)
    ns_5yr = so_ns_pull()
    checklist = so_preregistration_checklist()

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_guard": guard,
        "um_predictions": {
            "r": UM_R_HARDGATED,
            "ns": UM_NS_HARDGATED,
        },
        "so_projections": {
            "sigma_r_dr1": SO_SIGMA_R_DR1,
            "sigma_r_5yr": SO_SIGMA_R_5YR,
            "sigma_ns_5yr": SO_SIGMA_NS_5YR,
            "dr1_year_est": SO_DR1_YEAR_EST,
            "5yr_year_est": SO_5YR_YEAR_EST,
        },
        "r_snr_dr1": r_snr_dr1,
        "r_snr_5yr": r_snr_5yr,
        "ns_pull_5yr": ns_5yr,
        "routing_thresholds": {
            "r_consistent": SO_ROUTING_CONSISTENT_R,
            "r_falsified_3sigma": SO_ROUTING_FALSIFIED_R,
            "ns_p1_falsifier_low": P1_FALSIFIER_NS_LOW,
            "ns_p1_falsifier_high": P1_FALSIFIER_NS_HIGH,
            "preregistration_version": "v11.10",
            "preregistration_date": "2026-05-20",
        },
        "checklist": checklist,
        "significance": (
            "SO is the first ground-based CMB instrument projected to DETECT "
            f"r = {UM_R_HARDGATED} at >{r_snr_5yr['snr']:.0f}σ (5-yr baseline), "
            "rather than merely setting upper limits. It will definitively "
            "distinguish between: (a) UM r correct → detection; "
            "(b) r in tension zone [0.010, 0.020] → sustained tension; "
            "(c) r < 0.010 at ≥3σ → P2 falsifier triggered."
        ),
        "status": "PREREGISTRATION_LOCKED",
        "decisive_before": "CMB-S4 (~2030)",
    }
