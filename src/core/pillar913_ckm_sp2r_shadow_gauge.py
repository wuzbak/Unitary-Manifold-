# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 913 — CKM Flavour from Sp(2,ℝ) Shadow Gauge.

🔵 ADJACENT TRACK — Non-hardgate.  Does not alter core 5D predictions.

═══════════════════════════════════════════════════════════════════════════
THE GAP THIS ADDRESSES
═══════════════════════════════════════════════════════════════════════════

Sprint BC (Pillar 888 + 904) established that the 7D Froggatt-Nielsen (FN)
charge assignment improves the CKM hierarchy but leaves a residual tension:
the predicted θ₁₂ and θ₁₃ angles agree with PDG to within 20%, but θ₂₃
is reproduced only at order-of-magnitude level (TENSION_PERSISTS).

In two-time physics (Bars) different shadow gauge-fixings of Sp(2,ℝ) give
different 1T shadows of the same 13D parent.  The FN charge table
{Q_i ∈ ℤ} is effectively a choice of integer grading on the 7D orbifold —
which in the I-Theory parent is a shadow of the Sp(2,ℝ) weight-space
decomposition.

This pillar asks: is there a canonical shadow gauge (a specific integer
grading of the Sp(2,ℝ) Lie algebra generators) that simultaneously
  (a) reproduces the observed quark-angle ordering  θ₁₂ > θ₂₃ > θ₁₃, and
  (b) reduces to the known Wolfenstein parameter  λ ≈ 0.225?

METHOD
------
We parametrise the shadow-gauge by a single integer n_shadow ∈ {1,…,n_w}
and compute the induced FN charges:

    Q_i(n_shadow) = n_w - i · n_shadow / n_w      (i = 1,2,3 generation)

The resulting mixing angles scale as:

    θ₁₂ ~ ε^{Q_2 - Q_1},  θ₂₃ ~ ε^{Q_3 - Q_2},  θ₁₃ ~ ε^{Q_3 - Q_1}

with  ε = ε_FN = 1/k_CS^{1/4}  (the Sp(2,ℝ) suppression from Pillar 887).

We check whether the ordering  θ₁₂ > θ₂₃ > θ₁₃  holds for any n_shadow.

HONEST RESULT
-------------
If n_shadow = n_w (the "maximal shadow") reproduces the ordering and gives
λ within a factor-2 of 0.225 → `CKM_SP2R_SHADOW_FIXED`.
Otherwise → `CKM_TENSION_PERSISTS_13D`.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

__all__ = [
    "N_W",
    "K_CS",
    "EPSILON_FN",
    "WOLFENSTEIN_PDG",
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "shadow_gauge_scan",
    "ckm_sp2r_shadow",
    "ckm_sp2r_summary",
]

N_W: int = 5
K_CS: int = 74
PI: float = math.pi

# FN suppression parameter from Sp(2,ℝ) anomaly (Pillar 887)
EPSILON_FN: float = K_CS ** (-0.25)           # ≈ 0.336

# PDG reference values
WOLFENSTEIN_PDG: float = 0.22650              # λ (PDG 2022)
THETA_12_PDG: float = math.asin(0.22650)     # ≈ 13.1°
THETA_23_PDG: float = math.asin(0.04053)     # ≈ 2.32°
THETA_13_PDG: float = math.asin(0.003731)    # ≈ 0.214°

PILLAR_NUMBER: int = 913
PILLAR_GATE: str = "CKM_SP2R_SHADOW_GAUGE"


def _fn_charges(n_shadow: int) -> Tuple[float, float, float]:
    """Compute generation FN charges from shadow gauge integer n_shadow."""
    q1 = N_W - 1 * n_shadow / N_W
    q2 = N_W - 2 * n_shadow / N_W
    q3 = N_W - 3 * n_shadow / N_W
    return q1, q2, q3


def _angles_from_charges(q1: float, q2: float, q3: float) -> Tuple[float, float, float]:
    """Estimate CKM angles from FN charge differences."""
    # θ₁₂ ~ ε^(q2-q1), etc.  Protect against negative exponents → large angles → clip at π/2.
    def _theta(dq: float) -> float:
        raw = EPSILON_FN ** dq if dq >= 0 else 1.0 / (EPSILON_FN ** (-dq))
        return min(raw, 1.0)   # sin(θ) ≤ 1

    sin12 = _theta(q2 - q1)
    sin23 = _theta(q3 - q2)
    sin13 = _theta(q3 - q1)
    return sin12, sin23, sin13


def shadow_gauge_scan() -> List[Dict[str, Any]]:
    """Scan n_shadow ∈ {1,…,n_w} and evaluate CKM angle ordering."""
    results: List[Dict[str, Any]] = []
    for n_s in range(1, N_W + 1):
        q1, q2, q3 = _fn_charges(n_s)
        sin12, sin23, sin13 = _angles_from_charges(q1, q2, q3)
        ordering_ok: bool = sin12 > sin23 > sin13 > 0
        # Wolfenstein λ ~ sin12
        lambda_pred: float = sin12
        lambda_ratio: float = lambda_pred / WOLFENSTEIN_PDG if WOLFENSTEIN_PDG > 0 else 9999.0
        results.append({
            "n_shadow": n_s,
            "fn_charges": (round(q1, 4), round(q2, 4), round(q3, 4)),
            "sin_theta12": round(sin12, 6),
            "sin_theta23": round(sin23, 6),
            "sin_theta13": round(sin13, 6),
            "ordering_ok": ordering_ok,
            "lambda_pred": round(lambda_pred, 6),
            "lambda_ratio": round(lambda_ratio, 4),
            "lambda_within_factor2": 0.5 <= lambda_ratio <= 2.0,
        })
    return results


def ckm_sp2r_shadow() -> Dict[str, Any]:
    """Full CKM shadow-gauge analysis."""
    scan = shadow_gauge_scan()
    # Find best candidate: ordering correct AND λ within factor-2
    best: Optional[Dict[str, Any]] = None
    for entry in scan:
        if entry["ordering_ok"] and entry["lambda_within_factor2"]:
            best = entry
            break

    status: str = "CKM_SP2R_SHADOW_FIXED" if best is not None else "CKM_TENSION_PERSISTS_13D"
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": status,
        "epsilon_fn": EPSILON_FN,
        "wolfenstein_pdg": WOLFENSTEIN_PDG,
        "scan": scan,
        "best_shadow": best,
        "interpretation": (
            f"Shadow gauge n_shadow={best['n_shadow']} reproduces the CKM angle ordering "
            f"θ₁₂ > θ₂₃ > θ₁₃ and gives λ={best['lambda_pred']:.4f} (ratio {best['lambda_ratio']:.3f} "
            f"to PDG {WOLFENSTEIN_PDG}).  The Sp(2,R) shadow-gauge choice is not fully canonical "
            f"— a unique preferred shadow requires additional geometric input."
            if best is not None
            else
            "No shadow gauge n_shadow ∈ {1,…,n_w} simultaneously reproduces the CKM angle "
            "ordering AND gives λ within a factor-2 of PDG.  The CKM θ ordering tension "
            "PERSISTS at the I-Theory level — registered as an open architecture item."
        ),
        "open_item": (
            "CKM_TENSION_PERSISTS_13D: the Sp(2,R) shadow-gauge freedom does not canonically "
            "fix the FN charges to reproduce all three PDG CKM angles.  Additional geometric "
            "input (e.g., precise matter-curve intersection numbers in CY₄) would be required."
        ),
        "references": [
            "Pillar 887 — FN charge assignment from 7D monodromy",
            "Pillar 888 — CKM 7D FN correction",
            "Pillar 904 — Lean4 FN hierarchy theorems",
            "Bars & Terning, Extra Dimensions in Space and Time (2010) §4",
        ],
    }


def ckm_sp2r_summary() -> Dict[str, Any]:
    """Concise summary for the sprint certificate."""
    r = ckm_sp2r_shadow()
    return {
        "pillar": r["pillar"],
        "gate": r["gate"],
        "status": r["status"],
        "best_shadow": r["best_shadow"],
    }


# Module-level status (computed after functions are defined)
def _compute_pillar_status() -> str:
    for n_s in range(1, N_W + 1):
        q1, q2, q3 = _fn_charges(n_s)
        sin12, sin23, sin13 = _angles_from_charges(q1, q2, q3)
        if sin12 > sin23 > sin13 > 0:
            ratio = sin12 / WOLFENSTEIN_PDG if WOLFENSTEIN_PDG > 0 else 9999.0
            if 0.5 <= ratio <= 2.0:
                return "CKM_SP2R_SHADOW_FIXED"
    return "CKM_TENSION_PERSISTS_13D"


PILLAR_STATUS: str = _compute_pillar_status()


if __name__ == "__main__":
    import json
    print(json.dumps(ckm_sp2r_shadow(), indent=2, default=str))
