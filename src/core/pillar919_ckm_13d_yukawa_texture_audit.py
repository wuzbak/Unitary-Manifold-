# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 919 — CKM 13D Yukawa Texture Audit.

🔵 ADJACENT TRACK — Non-hardgate.  Does not alter core 5D predictions.

═══════════════════════════════════════════════════════════════════════════
THE GAP THIS ADDRESSES
═══════════════════════════════════════════════════════════════════════════

Sprint BD (Pillar 913) established CKM_TENSION_PERSISTS_13D: no Sp(2,ℝ)
shadow gauge simultaneously reproduces all three PDG CKM angles.

This pillar attempts a unified FN+Sp(2,ℝ) approach:
  1. Build the 13D Yukawa texture matrix Y^u (3×3) from braided winding
     suppression factors ε^{q_i+q_j} where q_i are FN charges.
  2. Cross-check via SVD (building on Pillar 914/YukawaSVDClosure).
  3. Extract CKM = U_L^u (U_L^d)† from the left singular vectors.
  4. Attempt to simultaneously satisfy:
       - PDG angle ordering  θ₁₂ > θ₂₃ > θ₁₃
       - Jarlskog invariant  J ≈ 3.08×10⁻⁵

HONEST RESULT
─────────────
CLOSED if all three angles reproduced within 30% of PDG AND J within
an order of magnitude.
PARTIAL_TENSION if ordering reproduced but magnitudes off by >30%.
IRREDUCIBLE_ARCHITECTURE_LIMIT if ordering cannot be reproduced at all.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

__all__ = [
    "N_W",
    "K_CS",
    "EPSILON_FN",
    "PDG_THETA_12",
    "PDG_THETA_23",
    "PDG_THETA_13",
    "PDG_JARLSKOG",
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "build_yukawa_texture",
    "ckm_from_texture",
    "jarlskog_invariant",
    "ckm_13d_yukawa_audit",
    "ckm_13d_summary",
]

N_W: int = 5
K_CS: int = 74
PI: float = math.pi

# FN suppression parameter (Pillar 887)
EPSILON_FN: float = K_CS ** (-0.25)          # ≈ 0.336

# PDG reference (2022)
PDG_SIN12: float = 0.22650
PDG_SIN23: float = 0.04053
PDG_SIN13: float = 0.003731
PDG_THETA_12: float = math.asin(PDG_SIN12)  # ≈ 0.2283 rad
PDG_THETA_23: float = math.asin(PDG_SIN23)  # ≈ 0.04055 rad
PDG_THETA_13: float = math.asin(PDG_SIN13)  # ≈ 0.003731 rad
PDG_JARLSKOG: float = 3.08e-5

PILLAR_NUMBER: int = 919
PILLAR_GATE: str = "CKM_13D_YUKAWA_TEXTURE_AUDIT"


def _fn_charges_unified(alpha: float, beta: float) -> Tuple[float, float, float]:
    """
    Unified FN + Sp(2,ℝ) charge assignment.
    q_i = n_w - i * alpha / n_w  (FN ladder, Pillar 887)
    with  alpha ∈ [1, n_w]  and  beta  controlling Sp(2,ℝ) weight mixing.
    Down-type: q_i^d = q_i^u + beta / n_w.
    """
    qu = [N_W - i * alpha / N_W for i in range(1, 4)]
    qd = [q + beta / N_W for q in qu]
    return tuple(qu), tuple(qd)  # type: ignore[return-value]


def build_yukawa_texture(
    qu: Tuple[float, float, float],
    qd: Tuple[float, float, float],
) -> Tuple[np.ndarray, np.ndarray]:
    """Build 3×3 Yukawa texture matrices Y^u and Y^d."""
    Yu = np.array(
        [[EPSILON_FN ** abs(qu[i] + qu[j]) for j in range(3)] for i in range(3)],
        dtype=float,
    )
    Yd = np.array(
        [[EPSILON_FN ** abs(qd[i] + qd[j]) for j in range(3)] for i in range(3)],
        dtype=float,
    )
    return Yu, Yd


def ckm_from_texture(Yu: np.ndarray, Yd: np.ndarray) -> np.ndarray:
    """Extract CKM matrix from Yukawa textures via SVD."""
    Uu, _, _ = np.linalg.svd(Yu)
    Ud, _, _ = np.linalg.svd(Yd)
    V_ckm = Uu.T @ Ud
    return V_ckm


def jarlskog_invariant(V: np.ndarray) -> float:
    """Compute Jarlskog invariant J from CKM matrix."""
    J: float = 0.0
    for a in range(3):
        for b in range(3):
            for c in range(3):
                for d in range(3):
                    if a != b and c != d:
                        J = max(
                            J,
                            abs(
                                (V[a, c] * V[b, d] * np.conj(V[a, d]) * np.conj(V[b, c])).imag
                            ),
                        )
    return float(J)


def _evaluate_candidate(
    alpha: float, beta: float
) -> Dict[str, Any]:
    """Evaluate a single (alpha, beta) candidate."""
    qu, qd = _fn_charges_unified(alpha, beta)
    Yu, Yd = build_yukawa_texture(qu, qd)
    V = ckm_from_texture(Yu, Yd)
    sin12 = min(abs(V[0, 1]), 1.0)
    sin23 = min(abs(V[1, 2]), 1.0)
    sin13 = min(abs(V[0, 2]), 1.0)
    # Ordering
    ordering_ok: bool = sin12 > sin23 > sin13 > 0.0
    # Closeness to PDG
    r12 = sin12 / PDG_SIN12 if PDG_SIN12 > 0 else 999.0
    r23 = sin23 / PDG_SIN23 if PDG_SIN23 > 0 else 999.0
    r13 = sin13 / PDG_SIN13 if PDG_SIN13 > 0 else 999.0
    magnitudes_within_30 = all(0.7 <= r <= 1.3 for r in [r12, r23, r13])
    # Jarlskog
    J = jarlskog_invariant(V)
    J_ratio = J / PDG_JARLSKOG if PDG_JARLSKOG > 0 else 999.0
    J_within_order = 0.1 <= J_ratio <= 10.0 if J > 0 else False
    return {
        "alpha": alpha,
        "beta": beta,
        "fn_charges_up": tuple(round(q, 4) for q in qu),
        "fn_charges_down": tuple(round(q, 4) for q in qd),
        "sin12": round(float(sin12), 6),
        "sin23": round(float(sin23), 6),
        "sin13": round(float(sin13), 6),
        "r12": round(r12, 4),
        "r23": round(r23, 4),
        "r13": round(r13, 4),
        "ordering_ok": ordering_ok,
        "magnitudes_within_30": magnitudes_within_30,
        "jarlskog": float(J),
        "jarlskog_ratio": float(J_ratio),
        "J_within_order": J_within_order,
        "closed": ordering_ok and magnitudes_within_30 and J_within_order,
        "partial": ordering_ok and not magnitudes_within_30,
    }


def _scan() -> List[Dict[str, Any]]:
    """Scan (alpha, beta) grid (cached at module level)."""
    results: List[Dict[str, Any]] = []
    for alpha in [1.0, 2.0, 3.0, 4.0, float(N_W)]:
        for beta in [0.0, 0.5, 1.0, 2.0, float(N_W)]:
            results.append(_evaluate_candidate(alpha, beta))
    return results


# Module-level cached scan (computed once at import)
_SCAN_CACHE: List[Dict[str, Any]] = _scan()


def ckm_13d_yukawa_audit() -> Dict[str, Any]:
    """Full audit of unified FN+Sp(2,ℝ) Yukawa texture."""
    scan = _SCAN_CACHE
    best_closed: Optional[Dict[str, Any]] = next(
        (r for r in scan if r["closed"]), None
    )
    best_partial: Optional[Dict[str, Any]] = next(
        (r for r in scan if r["partial"]), None
    )
    if best_closed is not None:
        status = "CLOSED"
        interpretation = (
            f"Unified FN+Sp(2,ℝ) Yukawa texture achieves CLOSED status at "
            f"α={best_closed['alpha']}, β={best_closed['beta']}: all three CKM angles "
            f"reproduced within 30% of PDG and Jarlskog invariant within one order of magnitude."
        )
    elif best_partial is not None:
        status = "PARTIAL_TENSION"
        interpretation = (
            f"Unified FN+Sp(2,ℝ) Yukawa texture reproduces the CKM angle ordering "
            f"θ₁₂ > θ₂₃ > θ₁₃ at α={best_partial['alpha']}, β={best_partial['beta']}, "
            f"but the angle magnitudes or Jarlskog invariant remain outside 30% of PDG.  "
            f"CKM_TENSION_PERSISTS — open architecture item."
        )
    else:
        status = "IRREDUCIBLE_ARCHITECTURE_LIMIT"
        interpretation = (
            "No (α, β) combination in the scan simultaneously reproduces the PDG CKM "
            "angle ordering θ₁₂ > θ₂₃ > θ₁₃.  This confirms CKM_TENSION_PERSISTS_13D "
            "as an irreducible architecture limit at the 5D + FN + Sp(2,ℝ) level.  "
            "Resolution requires matter-curve intersection numbers from a full CY₄ geometry."
        )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": status,
        "epsilon_fn": EPSILON_FN,
        "pdg_sin12": PDG_SIN12,
        "pdg_sin23": PDG_SIN23,
        "pdg_sin13": PDG_SIN13,
        "pdg_jarlskog": PDG_JARLSKOG,
        "best_closed": best_closed,
        "best_partial": best_partial,
        "n_scan_candidates": len(scan),
        "interpretation": interpretation,
        "open_item": (
            "CKM_TEXTURE_13D_OPEN: unified FN+Sp(2,ℝ) charge assignment does not "
            "fully reproduce the PDG CKM mixing pattern — requires CY₄ matter-curve "
            "intersection numbers for resolution."
            if status != "CLOSED"
            else None
        ),
        "references": [
            "Pillar 887 — FN charge assignment from 7D monodromy",
            "Pillar 913 — CKM Sp(2,R) shadow gauge scan",
            "YukawaSVDClosure.lean — SVD Yukawa architecture (hardgate memory)",
            "Beasley-Heckman-Vafa 2009 — F-theory GUT Yukawa couplings",
        ],
    }


def ckm_13d_summary() -> Dict[str, Any]:
    r = ckm_13d_yukawa_audit()
    return {"pillar": r["pillar"], "gate": r["gate"], "status": r["status"]}


def _compute_status() -> str:
    for r in _SCAN_CACHE:
        if r["closed"]:
            return "CLOSED"
    for r in _SCAN_CACHE:
        if r["partial"]:
            return "PARTIAL_TENSION"
    return "IRREDUCIBLE_ARCHITECTURE_LIMIT"


PILLAR_STATUS: str = _compute_status()


if __name__ == "__main__":
    import json
    print(json.dumps(ckm_13d_yukawa_audit(), indent=2, default=str))
