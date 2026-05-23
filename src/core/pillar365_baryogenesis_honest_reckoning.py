# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar365_baryogenesis_honest_reckoning.py
====================================================
Pillar 365 — Baryogenesis Honest Reckoning: ARCHITECTURE_LIMIT Certification.

════════════════════════════════════════════════════════════════════════════
STATUS: ARCHITECTURE_LIMIT — SPHALERONS + KK BARYOGENESIS CENTRAL ESTIMATE
         IS ~2000× BELOW OBSERVED η_B
════════════════════════════════════════════════════════════════════════════

Pillar 338 (KK Baryogenesis) established:
  - O(30) theoretical uncertainty in the washout factor
  - Central PTFT estimate ~ 10^{-13} (vs observed 6.1×10^{-10})
  - Gap factor: ~2000×

The O(30) uncertainty means the actual value could range from:
  η_B^{min} ≈ 10^{-13} / 30 ≈ 3×10^{-15}
  η_B^{max} ≈ 10^{-13} × 30 ≈ 3×10^{-12}

Observed: η_B = 6.1×10^{-10}

Even the MAXIMUM estimate (×30 favorable) falls 200× short of observed.

This is not an uncertainty — it is a genuine physics gap.

════════════════════════════════════════════════════════════════════════════
SYSTEMATIC AUDIT OF POSSIBLE MISSING FACTORS
════════════════════════════════════════════════════════════════════════════

Checked:
1. KK temperature T_KK vs EW temperature T_EW:
   The KK sphaleron rate Γ_sphal ~ T³ × exp(-E_sphal/T).
   If T_KK maps to T_EW ≈ 100 GeV, the rate is correctly computed.
   Pillar 338 uses T_EW = 100 GeV → no error here.

2. Braid enhancement to sphaleron rate:
   The (5,7) braid could enhance Γ_sphal by a factor K_CS = 74.
   η_B^{enhanced} ~ 74 × 10^{-13} ≈ 7×10^{-12}  → still ~100× short.

3. Leptogenesis route (Pillar 323):
   Already documented as ARCHITECTURE_LIMIT.
   The UM seesaw gives too high a leptogenesis scale.
   This is confirmed by Pillar 323.

4. Two-step mechanism (KK baryogenesis + sphalerons):
   PTFT estimate × KK enhancement: 74 × 10^{-13} ≈ 7×10^{-12}.
   Still 100× short. Even with O(30) favorable uncertainty: 74 × 30 × 10^{-13}
   = 2×10^{-10}. This approaches the observed range (~3× short).
   But the O(30) uncertainty is not a guaranteed enhancement — it is symmetric.

CONCLUSION: The UM KK baryogenesis mechanism (as currently formulated)
produces a central η_B estimate ~2000× below observed. Even with the most
favorable O(30) uncertainty and the KK braid enhancement (~74×), the
maximum estimate is ~3× short. The mechanism cannot explain η_B without
additional physics.

FORMAL STATUS: ARCHITECTURE_LIMIT (analogous to leptogenesis, Pillar 323).
This requires physics beyond the minimal 5D-EFT — most likely:
(a) A higher-dimensional baryogenesis mechanism from the full UV completion
(b) Electroweak baryogenesis with modified Higgs potential from KK contributions
(c) Affleck-Dine baryogenesis from radion-inflaton dynamics

This is honestly documented and not hidden.

*Theory: ThomasCory Walker-Pearson.*
*Code, tests, document engineering: GitHub Copilot (AI).*
"""
from __future__ import annotations
import math
from typing import Dict, List

__all__ = [
    "PILLAR_NUMBER", "PILLAR_TITLE", "PILLAR_STATUS", "ADJACENCY_TRACK_LABEL",
    "ETA_B_OBSERVED", "ETA_B_CENTRAL_ESTIMATE", "UNCERTAINTY_FACTOR",
    "K_CS", "SPHALERON_TEMP_GEV",
    "separation_guard",
    "ptft_central_estimate",
    "braid_enhancement_factor",
    "maximum_eta_b_estimate",
    "gap_factor",
    "washout_factor_sensitivity",
    "missing_factor_audit",
    "baryogenesis_honest_reckoning",
    "pillar365_summary",
]

PILLAR_NUMBER: int = 365
PILLAR_TITLE: str = (
    "Baryogenesis Honest Reckoning: ARCHITECTURE_LIMIT Certification "
    "and Missing Factor Audit"
)
PILLAR_STATUS: str = "ARCHITECTURE_LIMIT"
ADJACENCY_TRACK_LABEL: str = "HARDGATE_ADJACENT"

ETA_B_OBSERVED: float = 6.1e-10    # Observed baryon asymmetry
ETA_B_CENTRAL_ESTIMATE: float = 1.0e-13   # PTFT central estimate (Pillar 338)
UNCERTAINTY_FACTOR: float = 30.0   # O(30) uncertainty (Pillar 338)
K_CS: int = 74
SPHALERON_TEMP_GEV: float = 100.0   # EW sphaleron temperature


def separation_guard() -> str:
    return (
        "HARDGATE_ADJACENT: Pillar 365 performs honest reckoning on the "
        "KK baryogenesis mechanism. Status: ARCHITECTURE_LIMIT. "
        "No ToE score affected."
    )


def ptft_central_estimate() -> float:
    """PTFT central estimate of η_B from Pillar 338."""
    return ETA_B_CENTRAL_ESTIMATE


def braid_enhancement_factor() -> float:
    """Braid enhancement to sphaleron rate from K_CS."""
    return float(K_CS)


def maximum_eta_b_estimate() -> float:
    """Maximum η_B from central estimate × O(30) × braid enhancement.

    This is the most favorable scenario consistent with Pillar 338 uncertainty.
    """
    return ETA_B_CENTRAL_ESTIMATE * UNCERTAINTY_FACTOR * braid_enhancement_factor()


def gap_factor(
    estimate: float = ETA_B_CENTRAL_ESTIMATE,
    observed: float = ETA_B_OBSERVED,
) -> float:
    """Gap factor: observed / estimate.

    Parameters
    ----------
    estimate, observed : float

    Returns
    -------
    float
        Ratio observed / estimate (how much is missing).
    """
    return observed / estimate


def washout_factor_sensitivity() -> Dict[str, float]:
    """Sensitivity of η_B to the O(30) washout uncertainty.

    Returns range of η_B predictions given Pillar 338 uncertainty.

    Returns
    -------
    dict
    """
    eta_min = ETA_B_CENTRAL_ESTIMATE / UNCERTAINTY_FACTOR
    eta_max = ETA_B_CENTRAL_ESTIMATE * UNCERTAINTY_FACTOR
    eta_max_with_braid = eta_max * braid_enhancement_factor()

    gap_central = gap_factor(ETA_B_CENTRAL_ESTIMATE)
    gap_max = gap_factor(eta_max)
    gap_max_with_braid = gap_factor(eta_max_with_braid)

    return {
        "eta_b_min": eta_min,
        "eta_b_central": ETA_B_CENTRAL_ESTIMATE,
        "eta_b_max_no_braid": eta_max,
        "eta_b_max_with_braid": eta_max_with_braid,
        "gap_central": gap_central,
        "gap_max_no_braid": gap_max,
        "gap_max_with_braid": gap_max_with_braid,
        "within_observed_range": eta_max_with_braid >= ETA_B_OBSERVED,
        "comment": (
            "Even maximum estimate (×O(30) favorable × braid enhancement ×74) "
            "gives η_B ~ {:.1e}. Observed: {:.1e}. Gap: {:.0f}×.".format(
                eta_max_with_braid, ETA_B_OBSERVED,
                gap_factor(eta_max_with_braid) if eta_max_with_braid < ETA_B_OBSERVED else 1.0
            )
        ),
    }


def missing_factor_audit() -> List[Dict[str, object]]:
    """Systematic audit of possible missing physics factors.

    Returns
    -------
    list of dict
    """
    return [
        {
            "mechanism": "KK temperature mapping T_KK → T_EW",
            "claimed_enhancement": "1× (already included in Pillar 338)",
            "verdict": "INCLUDED — not a missing factor",
            "result": "T_EW = 100 GeV correctly used",
        },
        {
            "mechanism": "Braid enhancement to sphaleron rate (×K_CS = 74)",
            "claimed_enhancement": "74×",
            "eta_b_with_enhancement": ETA_B_CENTRAL_ESTIMATE * K_CS,
            "verdict": "INSUFFICIENT — gives 7×10⁻¹² vs observed 6×10⁻¹⁰ (gap ~100×)",
            "result": "Partial mitigation only",
        },
        {
            "mechanism": "O(30) favorable washout uncertainty",
            "claimed_enhancement": "30×",
            "eta_b_with_enhancement": ETA_B_CENTRAL_ESTIMATE * UNCERTAINTY_FACTOR,
            "verdict": "SYMMETRIC UNCERTAINTY — cannot guarantee 30× enhancement",
            "result": "Cannot invoke as guaranteed enhancement",
        },
        {
            "mechanism": "Combined braid + O(30) favorable",
            "claimed_enhancement": "74 × 30 = 2220×",
            "eta_b_with_enhancement": ETA_B_CENTRAL_ESTIMATE * K_CS * UNCERTAINTY_FACTOR,
            "verdict": (
                "BARELY_SUFFICIENT numerically ({:.1e} vs {:.1e}) but requires "
                "BOTH maximum braid enhancement AND most favorable washout — "
                "requires fine-tuning".format(
                    ETA_B_CENTRAL_ESTIMATE * K_CS * UNCERTAINTY_FACTOR,
                    ETA_B_OBSERVED
                )
            ),
            "result": "Fine-tuned; cannot serve as natural explanation",
        },
        {
            "mechanism": "Affleck-Dine from radion-inflaton sector",
            "claimed_enhancement": "model-dependent (could be >> 2000×)",
            "verdict": "CANDIDATE — requires UV completion beyond 5D-EFT",
            "result": "Path to resolution: radion-inflaton AD baryogenesis",
        },
        {
            "mechanism": "EW baryogenesis with KK-modified Higgs potential",
            "claimed_enhancement": "model-dependent",
            "verdict": "CANDIDATE — KK modes modify the EW phase transition",
            "result": "Path to resolution: KK-enhanced EWPT baryogenesis",
        },
    ]


def baryogenesis_honest_reckoning() -> Dict[str, object]:
    """Complete Pillar 365 baryogenesis reckoning."""
    washout = washout_factor_sensitivity()
    audit = missing_factor_audit()

    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "track": ADJACENCY_TRACK_LABEL,
        "eta_b_observed": ETA_B_OBSERVED,
        "eta_b_central": ETA_B_CENTRAL_ESTIMATE,
        "gap_central": gap_factor(),
        "washout_sensitivity": washout,
        "missing_factor_audit": audit,
        "architecture_limit_statement": (
            "The KK baryogenesis mechanism (sphaleron + PTFT, Pillar 338) gives "
            "eta_B ~ 1e-13 at the central estimate -- ~{:.0f}x below the observed "
            "6.1e-10. Even with braid enhancement (x{}) and most favorable "
            "washout (x{}), the maximum estimate approaches but may not reach "
            "the observed value. The mechanism requires physics BEYOND the minimal "
            "5D-EFT: Affleck-Dine baryogenesis or KK-enhanced EWPT are the "
            "most natural paths. Certified as ARCHITECTURE_LIMIT (analogous to "
            "Pillar 323 leptogenesis).".format(
                gap_factor(), K_CS, int(UNCERTAINTY_FACTOR)
            )
        ),
        "paths_forward": [
            "Affleck-Dine baryogenesis from radion-inflaton dynamics",
            "KK-enhanced electroweak phase transition baryogenesis",
            "Higher-dimensional gravitational baryogenesis from UV completion",
        ],
        "separation_guard": separation_guard(),
    }


def pillar365_summary() -> Dict[str, object]:
    """Summary for Pillar 365."""
    return baryogenesis_honest_reckoning()
