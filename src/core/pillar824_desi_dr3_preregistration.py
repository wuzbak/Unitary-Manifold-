# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 824 — DESI_DR3_PRE_REGISTRATION

Machine-readable pre-registration of the DESI DR3 dark energy falsification
routing for the UM wₐ = 0 prediction.

Status: DESI_DR3_PREREGISTERED   (falsification protocol machine-readable)

Background
----------
Pillar 808 derived wₐ = 0 from the frozen-radion breathing mode of the UM
5D geometry: the radion φ is stabilised by the Z₂ orbifold Goldberger-Wise
mechanism, leading to w(a) = −1 + ε where ε is exponentially small.

The current tension with DESI DR2 is σ_DR2 = 2.75σ (registered in
CLAIM_MASTER_BOARD.md, Lane C tension T1).

This pillar pre-registers:
  1. The exact observable to compare: wₐ from CPL parametrization w(a) = w₀ + wₐ(1−a)
  2. The DESI DR3 data ingestion protocol (BAO-only + combined)
  3. The σ computation procedure
  4. The routing thresholds: FALSIFIED / TENSION / PASS

Pre-registration Protocol
--------------------------
Observable:
  wₐ from CPL fit to DESI BAO measurements of D_H(z)/r_d and D_M(z)/r_d.

UM prediction:
  wₐ = 0 exactly (frozen radion; w₀ = −1 + δw₀ where δw₀ ~ exp(−2πkR) ≈ 0)

Tension metric:
  σ = |wₐ_DESI − 0| / σ(wₐ_DESI)

Routing thresholds (pre-registered 2026-08-26):
  σ ≥ 5.0  → FALSIFIED         (discovery-level tension, framework falsified)
  3.0 ≤ σ < 5.0 → HIGH_TENSION (strong tension, not yet falsified)
  2.0 ≤ σ < 3.0 → TENSION      (current status: 2.75σ)
  σ < 2.0  → PASS              (consistent with UM prediction)

DESI DR3 Timeline:
  Expected: ~2027 (DESI Year 3 data release)
  This pillar will be upgraded to DESI_DR3_VERDICT when data arrives.

Gate: DESI_DR3_PREREGISTERED

Lean4: DesiDR3PreRegistration.lean +15 theorems (1491→1506)
"""
from __future__ import annotations

import math
from datetime import date
from typing import NamedTuple

# ---------------------------------------------------------------------------
# Constants and prediction
# ---------------------------------------------------------------------------
UM_WA_PREDICTION: float = 0.0           # UM predicts frozen radion → wₐ = 0
UM_W0_PREDICTION: float = -1.0          # w₀ = −1 (cosmological constant limit)
DESI_DR2_WA_CENTRAL: float = -0.62     # DESI DR2 wₐ central value (approximation)
DESI_DR2_WA_SIGMA: float = 0.226       # DESI DR2 σ(wₐ) (approximation)
DESI_DR2_TENSION_SIGMA: float = 2.75   # Current tension with UM prediction

# Routing thresholds
THRESHOLD_FALSIFIED: float = 5.0
THRESHOLD_HIGH_TENSION: float = 3.0
THRESHOLD_TENSION: float = 2.0

# Pre-registration date
PREREGISTRATION_DATE: str = "2026-08-26"

PILLAR_NUMBER: int = 824
PILLAR_GATE: str = "DESI_DR3_PREREGISTERED"
LEAN4_THEOREM_COUNT: int = 15
LEAN4_TOTAL_BEFORE: int = 1491
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "UM_WA_PREDICTION",
    "DESI_DR2_TENSION_SIGMA",
    "THRESHOLD_FALSIFIED",
    "THRESHOLD_HIGH_TENSION",
    "THRESHOLD_TENSION",
    "compute_tension_sigma",
    "route_desi_verdict",
    "desi_dr3_verdict",
    "DESI_DR3_PROTOCOL",
]


# ---------------------------------------------------------------------------
# Routing logic
# ---------------------------------------------------------------------------

class DesiTensionResult(NamedTuple):
    """Result of DESI tension computation."""
    wa_desi: float              # DESI measured wₐ
    wa_sigma: float             # DESI 1σ uncertainty
    wa_um: float                # UM prediction = 0
    tension_sigma: float        # |wₐ_DESI − 0| / σ
    verdict: str                # FALSIFIED / HIGH_TENSION / TENSION / PASS
    pre_registered: bool        # always True for this module


def compute_tension_sigma(wa_desi: float, wa_sigma: float) -> float:
    """
    Compute tension in units of σ between DESI wₐ and UM prediction wₐ=0.

    Parameters
    ----------
    wa_desi : float
        DESI central value of wₐ from CPL fit.
    wa_sigma : float
        DESI 1σ uncertainty on wₐ.

    Returns
    -------
    float
        Tension in units of σ.
    """
    if wa_sigma <= 0:
        raise ValueError("wa_sigma must be positive")
    return abs(wa_desi - UM_WA_PREDICTION) / wa_sigma


def route_desi_verdict(tension_sigma: float) -> str:
    """
    Route DESI tension to verdict using pre-registered thresholds.

    Parameters
    ----------
    tension_sigma : float
        Tension in units of σ.

    Returns
    -------
    str
        One of: FALSIFIED, HIGH_TENSION, TENSION, PASS
    """
    if tension_sigma >= THRESHOLD_FALSIFIED:
        return "FALSIFIED"
    elif tension_sigma >= THRESHOLD_HIGH_TENSION:
        return "HIGH_TENSION"
    elif tension_sigma >= THRESHOLD_TENSION:
        return "TENSION"
    else:
        return "PASS"


def evaluate_current_dr2_status() -> DesiTensionResult:
    """
    Evaluate the current DESI DR2 tension with the pre-registered protocol.

    Returns
    -------
    DesiTensionResult
    """
    sigma = compute_tension_sigma(DESI_DR2_WA_CENTRAL, DESI_DR2_WA_SIGMA)
    verdict = route_desi_verdict(sigma)
    return DesiTensionResult(
        wa_desi=DESI_DR2_WA_CENTRAL,
        wa_sigma=DESI_DR2_WA_SIGMA,
        wa_um=UM_WA_PREDICTION,
        tension_sigma=sigma,
        verdict=verdict,
        pre_registered=True,
    )


def desi_dr3_verdict(
    wa_dr3: float | None = None,
    wa_dr3_sigma: float | None = None,
) -> dict[str, object]:
    """
    Return DESI DR3 pre-registration protocol and optionally compute verdict.

    Parameters
    ----------
    wa_dr3 : float, optional
        DESI DR3 central value of wₐ (None = data not yet available).
    wa_dr3_sigma : float, optional
        DESI DR3 uncertainty on wₐ.

    Returns
    -------
    dict
        Machine-readable pre-registration record and verdict (if data provided).
    """
    dr2 = evaluate_current_dr2_status()

    result: dict[str, object] = {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "preregistration_date": PREREGISTRATION_DATE,
        "um_prediction_wa": UM_WA_PREDICTION,
        "um_prediction_w0": UM_W0_PREDICTION,
        "um_mechanism": "frozen radion (Goldberger-Wise stabilisation, Pillar 808)",
        "observable": "wₐ from CPL fit w(a) = w₀ + wₐ(1−a) to DESI BAO",
        "tension_metric": "|wₐ_DESI − 0| / σ(wₐ_DESI)",
        "routing_thresholds": {
            "FALSIFIED": f"σ ≥ {THRESHOLD_FALSIFIED}",
            "HIGH_TENSION": f"{THRESHOLD_HIGH_TENSION} ≤ σ < {THRESHOLD_FALSIFIED}",
            "TENSION": f"{THRESHOLD_TENSION} ≤ σ < {THRESHOLD_HIGH_TENSION}",
            "PASS": f"σ < {THRESHOLD_TENSION}",
        },
        "desi_dr2_status": {
            "wa_central": DESI_DR2_WA_CENTRAL,
            "wa_sigma": DESI_DR2_WA_SIGMA,
            "tension_sigma": dr2.tension_sigma,
            "verdict": dr2.verdict,
        },
        "desi_dr3_status": "AWAITING_DATA",
        "desi_dr3_expected": "~2027 (DESI Year 3)",
    }

    if wa_dr3 is not None and wa_dr3_sigma is not None:
        sigma_dr3 = compute_tension_sigma(wa_dr3, wa_dr3_sigma)
        verdict_dr3 = route_desi_verdict(sigma_dr3)
        result["desi_dr3_status"] = {
            "wa_central": wa_dr3,
            "wa_sigma": wa_dr3_sigma,
            "tension_sigma": sigma_dr3,
            "verdict": verdict_dr3,
        }

    result["lean4_theorems"] = LEAN4_THEOREM_COUNT
    result["lean4_total"] = LEAN4_TOTAL_AFTER
    return result


# Module-level pre-registration protocol
DESI_DR3_PROTOCOL: dict[str, object] = desi_dr3_verdict()
