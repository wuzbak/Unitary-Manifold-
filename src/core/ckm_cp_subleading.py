# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/ckm_cp_subleading.py
==============================
Pillar 133 — CKM CP Sub-Leading Closure from Braid Geometry.

Physical Context
----------------
The CKM CP-violating phase δ was previously given (Pillar 82) at leading order
by the winding-topology formula δ_lead = 2π/n_w = 72°, which sits 1.35σ from
the PDG central value of 68.5° ± 2.6°.

This Pillar derives a more precise formula from the braid geometry of the
(n₁, n₂) = (5, 7) vacuum braid pair.

Braid Geometry Derivation
--------------------------
In the RS/UM framework the physical vacuum is the braided state |Ψ_{(n₁,n₂)}⟩
with n₁ = 5, n₂ = 7 (Pillar 58).  The braid opening angle θ_braid is the
angle in the (n₁, n₂) winding plane that separates the two braid strands:

    θ_braid = arctan(n₁ / n₂) = arctan(5/7) ≈ 35.54°

The cross-sector Yukawa amplitude Y_{ij} connecting a quark zero-mode in
sector n₁ to a quark zero-mode in sector n₂ acquires a complex phase equal
to the braid opening angle:

    arg Y_{ij} = θ_braid   (bra–ket overlap picks up single braid angle)

The CKM matrix is the product V_CKM = U_L^u† × U_L^d, where U_L^{u,d} each
diagonalise their respective mass matrices M = Y × v.  The bilinear M†M
relevant for diagonalisation is proportional to Y × Y†, which picks up the
phase twice:

    arg(Y × Y†) = 2 × θ_braid

Therefore the physical CKM CP-violating phase is:

    δ_sub = 2 × θ_braid = 2 × arctan(n₁/n₂) = 2 × arctan(5/7) ≈ 71.08°

Comparison with PDG
-------------------
    PDG 2024: δ = 68.5° ± 2.6°
    δ_sub = 71.08°
    Tension: |71.08 − 68.5| / 2.6 = 0.99σ  ←  CONSISTENT (< 1σ)

This is the tightest geometric prediction of the CKM CP phase currently
achievable from the Unitary Manifold framework.  It closes the last ⚠️ entry
in the TOE table.

Relationship to Leading Order
------------------------------
Both formulas emerge from the same braid geometry:
- Leading:    δ_lead = 2π/n_w = 72.0°   (full revolution / winding number)
- Sub-leading: δ_sub  = 2·arctan(n₁/n₂) = 71.08°   (braid opening angle ×2)

The sub-leading formula is more refined because it uses both braid parameters
(n₁ and n₂) rather than only n_w = n₁.

Public API
----------
braid_opening_angle(n1, n2) → dict
    θ_braid = arctan(n₁/n₂) with physical interpretation.

ckm_cp_subleading(n1, n2) → dict
    δ_sub = 2·arctan(n₁/n₂) with PDG comparison and σ-tension.

cp_closure_status(n1, n2) → dict
    Full closure report: leading vs sub-leading tensions, best prediction.

ckm_cp_subleading_consistency_check(n1, n2) → dict
    Assert δ_sub is within 2σ of PDG; raise ValueError if not.

braid_cp_phase_vs_nw(n_w_range) → list[dict]
    Survey δ_sub across a range of winding numbers for sensitivity analysis.

Code architecture, test suites, document engineering, and synthesis:
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import math
from typing import Dict, List

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

#: Canonical braided pair — lower winding (Pillar 58)
N1_CANONICAL: int = 5

#: Canonical braided pair — upper winding (Pillar 58)
N2_CANONICAL: int = 7

#: Canonical winding number n_w = n₁ (Pillars 67, 80)
N_W_CANONICAL: int = 5

#: PDG 2024 CKM CP-violating phase δ [degrees]
DELTA_CP_PDG_DEG: float = 68.5

#: PDG δ 1σ uncertainty [degrees]
DELTA_CP_SIGMA_DEG: float = 2.6

#: PDG δ [radians]
DELTA_CP_PDG_RAD: float = math.radians(DELTA_CP_PDG_DEG)

#: PDG δ 1σ [radians]
DELTA_CP_SIGMA_RAD: float = math.radians(DELTA_CP_SIGMA_DEG)

#: Leading-order CP phase δ_lead = 2π/n_w [degrees]
DELTA_CP_LEAD_DEG: float = 360.0 / N_W_CANONICAL  # = 72.0°

#: Sub-leading CP phase δ_sub = 2·arctan(n₁/n₂) [degrees]
DELTA_CP_SUB_DEG: float = 2.0 * math.degrees(
    math.atan2(N1_CANONICAL, N2_CANONICAL)
)  # ≈ 71.08°

#: Sub-leading tension with PDG [σ]
DELTA_CP_SUB_SIGMA: float = (
    abs(DELTA_CP_SUB_DEG - DELTA_CP_PDG_DEG) / DELTA_CP_SIGMA_DEG
)  # ≈ 0.99σ

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------


def braid_opening_angle(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
) -> Dict[str, object]:
    """Return the braid opening angle θ_braid = arctan(n₁/n₂).

    Physical interpretation
    ----------------------
    In the RS/UM braided vacuum |(n₁, n₂)⟩, the two braid strands subtend
    an angle θ_braid in the (n₁, n₂) winding plane:

        θ_braid = arctan(n₁/n₂)

    This is the half-angle of the CP phase acquired by a single Yukawa
    amplitude in the cross-sector channel.

    Parameters
    ----------
    n1 : int  Lower braid winding (default 5).
    n2 : int  Upper braid winding (default 7).

    Returns
    -------
    dict
        'theta_braid_deg'    : float — braid opening angle [degrees].
        'theta_braid_rad'    : float — braid opening angle [radians].
        'n1'                 : int.
        'n2'                 : int.
        'physical_origin'    : str.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"Winding numbers must be positive; got n1={n1}, n2={n2}.")
    theta = math.atan2(n1, n2)
    theta_deg = math.degrees(theta)
    return {
        "n1": n1,
        "n2": n2,
        "theta_braid_rad": theta,
        "theta_braid_deg": theta_deg,
        "physical_origin": (
            f"Braid opening angle in the (n₁={n1}, n₂={n2}) winding plane: "
            f"θ_braid = arctan({n1}/{n2}) = {theta_deg:.4f}°. "
            "This is the phase acquired by a single Y cross-sector Yukawa amplitude "
            "in the RS/UM (n₁, n₂) braided vacuum."
        ),
    }


def ckm_cp_subleading(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
) -> Dict[str, object]:
    """Return the sub-leading CKM CP phase δ_sub = 2·arctan(n₁/n₂).

    Derivation
    ----------
    The CKM matrix V = U_L^u† × U_L^d involves the bilinear M†M ∝ Y × Y†.
    Since the cross-sector Yukawa amplitude Y acquires phase θ_braid, the
    bilinear Y × Y† picks up 2θ_braid:

        δ_sub = 2 × arctan(n₁/n₂) = 2 × arctan(5/7) ≈ 71.08°

    This gives tension 0.99σ with PDG 68.5° ± 2.6° — CONSISTENT < 1σ.

    Parameters
    ----------
    n1 : int  Braid lower winding (default 5).
    n2 : int  Braid upper winding (default 7).

    Returns
    -------
    dict
        'delta_sub_deg'       : float — sub-leading CP phase [degrees].
        'delta_sub_rad'       : float — sub-leading CP phase [radians].
        'delta_lead_deg'      : float — leading-order 2π/n₁ [degrees].
        'delta_pdg_deg'       : float — PDG central value [degrees].
        'delta_pdg_sigma_deg' : float — PDG 1σ [degrees].
        'sigma_tension_sub'   : float — sub-leading tension [σ].
        'sigma_tension_lead'  : float — leading-order tension [σ].
        'best_prediction_deg' : float — canonical best prediction [degrees].
        'status'              : str   — 'CONSISTENT (< 1σ)' or similar.
        'derivation'          : str   — step-by-step explanation.
    """
    if n1 <= 0 or n2 <= 0:
        raise ValueError(f"Winding numbers must be positive; got n1={n1}, n2={n2}.")

    theta_braid = math.atan2(n1, n2)
    delta_sub = 2.0 * theta_braid
    delta_sub_deg = math.degrees(delta_sub)

    n_w = n1  # by convention n_w = n₁ for the leading winding sector
    delta_lead_deg = 360.0 / n_w

    sigma_sub = abs(delta_sub_deg - DELTA_CP_PDG_DEG) / DELTA_CP_SIGMA_DEG
    sigma_lead = abs(delta_lead_deg - DELTA_CP_PDG_DEG) / DELTA_CP_SIGMA_DEG

    if sigma_sub < 1.0:
        status = "CONSISTENT (< 1σ) — CLOSED ✅"
    elif sigma_sub < 2.0:
        status = "CONSISTENT (≤ 2σ)"
    else:
        status = f"TENSION ({sigma_sub:.2f}σ)"

    return {
        "n1": n1,
        "n2": n2,
        "theta_braid_deg": math.degrees(theta_braid),
        "delta_sub_deg": delta_sub_deg,
        "delta_sub_rad": delta_sub,
        "delta_lead_deg": delta_lead_deg,
        "delta_pdg_deg": DELTA_CP_PDG_DEG,
        "delta_pdg_sigma_deg": DELTA_CP_SIGMA_DEG,
        "sigma_tension_sub": sigma_sub,
        "sigma_tension_lead": sigma_lead,
        "best_prediction_deg": delta_sub_deg,
        "status": status,
        "derivation": (
            f"Step 1: braid opening angle θ_braid = arctan({n1}/{n2}) = "
            f"{math.degrees(theta_braid):.4f}°.\n"
            f"Step 2: CKM matrix ∝ Y·Y† → picks up phase 2θ_braid.\n"
            f"Step 3: δ_sub = 2·θ_braid = {delta_sub_deg:.4f}°.\n"
            f"Step 4: PDG δ = {DELTA_CP_PDG_DEG}° ± {DELTA_CP_SIGMA_DEG}° → "
            f"tension {sigma_sub:.2f}σ.\n"
            f"Status: {status}.\n"
            f"(Leading-order: δ_lead = 2π/{n_w} = {delta_lead_deg:.1f}° → "
            f"{sigma_lead:.2f}σ.)"
        ),
    }


def cp_closure_status(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
) -> Dict[str, object]:
    """Return a full closure report for the CKM CP phase.

    Summarises leading vs sub-leading predictions, best tension, and
    closure verdict for the TOE table entry.

    Parameters
    ----------
    n1, n2 : int  Braid winding numbers (default 5, 7).

    Returns
    -------
    dict
        'is_closed'       : bool — True if best_sigma < 1σ.
        'best_sigma'      : float — tension of best prediction.
        'best_formula'    : str  — formula label.
        'best_value_deg'  : float — best prediction [degrees].
        'pdg_deg'         : float — PDG central value.
        'toe_status'      : str  — '✅ CLOSED' or '⚠️ CONSISTENT (≤2σ)' etc.
        'leading'         : dict — leading-order results.
        'subleading'      : dict — sub-leading results.
    """
    sub = ckm_cp_subleading(n1, n2)
    is_closed = sub["sigma_tension_sub"] < 1.0
    toe_status = "✅ CLOSED (< 1σ)" if is_closed else "⚠️ CONSISTENT (≤2σ)"

    return {
        "n1": n1,
        "n2": n2,
        "is_closed": is_closed,
        "best_sigma": sub["sigma_tension_sub"],
        "best_formula": f"δ_sub = 2·arctan({n1}/{n2})",
        "best_value_deg": sub["delta_sub_deg"],
        "pdg_deg": DELTA_CP_PDG_DEG,
        "toe_status": toe_status,
        "leading": {
            "formula": f"δ_lead = 2π/{n1}",
            "value_deg": sub["delta_lead_deg"],
            "sigma": sub["sigma_tension_lead"],
        },
        "subleading": {
            "formula": f"δ_sub = 2·arctan({n1}/{n2})",
            "value_deg": sub["delta_sub_deg"],
            "sigma": sub["sigma_tension_sub"],
        },
    }


def ckm_cp_subleading_consistency_check(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
    sigma_threshold: float = 2.0,
) -> Dict[str, object]:
    """Assert that δ_sub is within sigma_threshold of PDG.

    Parameters
    ----------
    n1, n2           : int   Braid winding numbers.
    sigma_threshold  : float Maximum allowed tension (default 2.0σ).

    Returns
    -------
    dict
        'passed'     : bool — True if tension ≤ sigma_threshold.
        'sigma'      : float — actual tension.
        'threshold'  : float — requested threshold.
        'message'    : str.

    Raises
    ------
    ValueError
        If sigma_tension > sigma_threshold.
    """
    sub = ckm_cp_subleading(n1, n2)
    sigma = sub["sigma_tension_sub"]
    passed = sigma <= sigma_threshold
    msg = (
        f"δ_sub = 2·arctan({n1}/{n2}) = {sub['delta_sub_deg']:.3f}° — "
        f"{sigma:.3f}σ from PDG {DELTA_CP_PDG_DEG}° ± {DELTA_CP_SIGMA_DEG}°. "
        f"{'PASS' if passed else 'FAIL'} (threshold: {sigma_threshold}σ)."
    )
    if not passed:
        raise ValueError(
            f"CKM CP sub-leading consistency check FAILED: {sigma:.3f}σ > "
            f"{sigma_threshold}σ threshold. {msg}"
        )
    return {
        "passed": passed,
        "sigma": sigma,
        "threshold": sigma_threshold,
        "delta_sub_deg": sub["delta_sub_deg"],
        "message": msg,
    }


def braid_cp_phase_vs_nw(
    n_w_range: List[int] | None = None,
) -> List[Dict[str, object]]:
    """Survey δ_sub = 2·arctan(n_w/(n_w+2)) across winding numbers.

    Uses the partner convention n₂ = n₁ + 2 (as in the (5,7) canonical pair).

    Parameters
    ----------
    n_w_range : list[int]  Winding numbers to survey (default [3, 4, 5, 6, 7]).

    Returns
    -------
    list[dict]
        One dict per n_w with 'n_w', 'delta_sub_deg', 'sigma_tension'.
    """
    if n_w_range is None:
        n_w_range = [3, 4, 5, 6, 7]

    results = []
    for n_w in n_w_range:
        n1 = n_w
        n2 = n_w + 2  # canonical partner convention
        sub = ckm_cp_subleading(n1=n1, n2=n2)
        results.append(
            {
                "n_w": n_w,
                "n1": n1,
                "n2": n2,
                "delta_sub_deg": sub["delta_sub_deg"],
                "delta_lead_deg": sub["delta_lead_deg"],
                "sigma_tension_sub": sub["sigma_tension_sub"],
                "sigma_tension_lead": sub["sigma_tension_lead"],
                "status": sub["status"],
            }
        )
    return results


def pillar133_summary() -> Dict[str, object]:
    """Return a structured summary of Pillar 133 closure status.

    Returns
    -------
    dict
        Full closure status for documentation and audit tools.
    """
    sub = ckm_cp_subleading()
    closure = cp_closure_status()
    check = ckm_cp_subleading_consistency_check(sigma_threshold=2.0)

    return {
        "pillar": 133,
        "title": "CKM CP Sub-Leading Closure",
        "braid_pair": (N1_CANONICAL, N2_CANONICAL),
        "formula": "δ_sub = 2·arctan(n₁/n₂) = 2·arctan(5/7)",
        "prediction_deg": sub["delta_sub_deg"],
        "pdg_deg": DELTA_CP_PDG_DEG,
        "sigma_tension": sub["sigma_tension_sub"],
        "toe_status": closure["toe_status"],
        "is_closed": closure["is_closed"],
        "consistency_check_passed": check["passed"],
        "leading_order_deg": sub["delta_lead_deg"],
        "leading_order_sigma": sub["sigma_tension_lead"],
        "derivation_summary": (
            "Braid opening angle θ_braid = arctan(5/7) ≈ 35.54°. "
            "CKM = U†U picks up 2θ_braid. "
            f"δ_sub = 2×35.54° ≈ {sub['delta_sub_deg']:.2f}°. "
            f"PDG {DELTA_CP_PDG_DEG}° ± {DELTA_CP_SIGMA_DEG}° → "
            f"{sub['sigma_tension_sub']:.2f}σ — CLOSED."
        ),
    }
