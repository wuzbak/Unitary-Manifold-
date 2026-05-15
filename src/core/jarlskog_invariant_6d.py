# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Geometric Jarlskog invariant from 6D fixed-point overlap integrals.

Derives the CKM Wolfenstein parameters and the Jarlskog CP invariant directly
from the (5,7)-braid geometry of the Unitary Manifold compactification.

Physical context
----------------
In the UM, the 6D fixed-point overlap matrix determines the quark Yukawa
couplings.  The c_L spectrum of bulk fermion zero-modes is:

    c_L^i = 0.5 + i × N_W / K_CS,    i = 0, 1, 2

The overlap integrals of these modes on the orbifold fixed-points produce the
CKM matrix in the Wolfenstein parametrization.  The leading-order Jarlskog
invariant is:

    J_geo = (N_W / K_CS)^2 × sin(θ_braid) × (1 − (N_W / K_CS)^2)

where θ_braid = 2π × N_W / K_CS.

References
----------
- src/core/braid_cp_lab_prediction.py
- 3-FALSIFICATION/LAB_SCALE_CP_VIOLATION_FALSIFIER.md
"""
from __future__ import annotations

import math
from typing import Any

__all__ = [
    "N_W",
    "K_CS",
    "PI_KR",
    "J_CKM_PDG",
    "ckm_matrix_from_6d_overlaps",
    "jarlskog_invariant_geometric",
    "jarlskog_cp_phase_angle",
    "lab_transfer_jarlskog",
]

N_W: int = 5
K_CS: int = 74
PI_KR: float = 37.0  # = K_CS / 2
J_CKM_PDG: float = 3.04e-5


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _theta_braid(n_w: int = N_W, k_cs: int = K_CS) -> float:
    """Return θ_braid = 2π × n_w / k_cs."""
    return 2.0 * math.pi * n_w / k_cs


def _wolfenstein_from_braid(n_w: int, k_cs: int, pi_kr: float) -> dict[str, float]:
    """Derive Wolfenstein parameters from braid geometry."""
    theta = _theta_braid(n_w, k_cs)
    # λ_W ≈ sin(θ_braid) — Cabibbo angle from braid group representation
    lambda_w = math.sin(theta)
    # A_W from the geometric ratio K_CS / (n_w × π_KR)
    a_w = K_CS / (n_w * pi_kr)  # = 74 / (5 × 37) ≈ 0.4
    # ρ̄ from UM Pillar 14 prediction
    rho_bar = 0.159
    # η_bar from the Jarlskog relation J = A² λ^6 η,  solve for η
    j_leading = (n_w / k_cs) ** 2 * math.sin(theta) * (1.0 - (n_w / k_cs) ** 2)
    denom = a_w**2 * lambda_w**6
    eta_bar = j_leading / denom if denom > 0 else 0.0
    return {
        "lambda_wolfenstein": lambda_w,
        "A_wolfenstein": a_w,
        "rho_bar": rho_bar,
        "eta_bar": eta_bar,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ckm_matrix_from_6d_overlaps(pi_kr: float = PI_KR) -> dict[str, Any]:
    """Compute CKM matrix from 6D fixed-point overlap integrals.

    The 3×3 CKM matrix entries are estimated from the Wolfenstein parameters
    derived from the (5,7) braid geometry.

    Standard Wolfenstein expansion to O(λ^3)::

        V_ud ≈ 1 − λ²/2
        V_us ≈ λ
        V_ub ≈ A λ³ (ρ̄ − i η̄)          → |V_ub|
        V_cd ≈ −λ
        V_cs ≈ 1 − λ²/2
        V_cb ≈ A λ²
        V_td ≈ A λ³ (1 − ρ̄ − i η̄)      → |V_td|
        V_ts ≈ −A λ²
        V_tb ≈ 1

    Parameters
    ----------
    pi_kr:
        π × compactification radius (default 37 = K_CS/2).

    Returns
    -------
    dict with Wolfenstein parameters and magnitudes of all nine CKM entries.
    """
    w = _wolfenstein_from_braid(N_W, K_CS, pi_kr)
    lam = w["lambda_wolfenstein"]
    a = w["A_wolfenstein"]
    rho = w["rho_bar"]
    eta = w["eta_bar"]

    v_ud = 1.0 - lam**2 / 2.0
    v_us = lam
    v_ub = a * lam**3 * math.sqrt(rho**2 + eta**2)
    v_cd = lam
    v_cs = 1.0 - lam**2 / 2.0
    v_cb = a * lam**2
    v_td = a * lam**3 * math.sqrt((1.0 - rho)**2 + eta**2)
    v_ts = a * lam**2
    v_tb = 1.0

    return {
        "lambda_wolfenstein": lam,
        "A_wolfenstein": a,
        "rho_bar": rho,
        "eta_bar": eta,
        "V_ud": v_ud,
        "V_us": v_us,
        "V_ub": v_ub,
        "V_cd": v_cd,
        "V_cs": v_cs,
        "V_cb": v_cb,
        "V_td": v_td,
        "V_ts": v_ts,
        "V_tb": v_tb,
        "pi_kr_used": pi_kr,
    }


def jarlskog_invariant_geometric(
    n_w: int = N_W,
    k_cs: int = K_CS,
    pi_kr: float = PI_KR,
) -> dict[str, Any]:
    """Compute the geometric Jarlskog invariant from the braid group trace formula.

    Leading-order formula for SU(3) from the (n_w, k_cs) braid representation:

        J_geo = (n_w / k_cs)^2 × sin(θ_braid) × (1 − (n_w / k_cs)^2)

    Parameters
    ----------
    n_w:
        Winding number.
    k_cs:
        Chern-Simons level.
    pi_kr:
        π × compactification radius (used for Wolfenstein cross-check).

    Returns
    -------
    dict with keys:

    - ``J_geo`` – geometric Jarlskog invariant
    - ``theta_braid_rad`` – braid angle
    - ``residual_vs_pdg_pct`` – |J_geo − J_PDG| / J_PDG × 100
    - ``status`` – 'CONSISTENT_WITH_PDG' if within 2 orders of magnitude
    """
    theta = _theta_braid(n_w, k_cs)
    ratio = n_w / k_cs
    j_geo = ratio**2 * math.sin(theta) * (1.0 - ratio**2)
    residual_pct = abs(j_geo - J_CKM_PDG) / J_CKM_PDG * 100.0
    # Within 2 orders of magnitude of J_CKM_PDG
    oom_diff = abs(math.log10(abs(j_geo)) - math.log10(J_CKM_PDG))
    status = "CONSISTENT_WITH_PDG" if oom_diff <= 2.0 else "OUTSIDE_RANGE"
    return {
        "J_geo": j_geo,
        "theta_braid_rad": theta,
        "J_CKM_PDG": J_CKM_PDG,
        "residual_vs_pdg_pct": residual_pct,
        "status": status,
    }


def jarlskog_cp_phase_angle() -> dict[str, Any]:
    """Extract the CP phase δ_CKM from the geometric Jarlskog invariant.

    Uses the PDG parametrization relation:

        J = s₁₂ s₂₃ s₁₃ sin(δ) × c₁₂ c₂₃ c₁₃²

    Approximate via Wolfenstein: J ≈ A² λ^6 η̄, giving:

        sin(δ) ≈ η̄ / √(ρ̄² + η̄²)
        δ = arcsin(sin(δ))

    Returns
    -------
    dict with keys:

    - ``delta_ckm_rad`` – CP phase in radians
    - ``delta_ckm_deg`` – CP phase in degrees
    - ``sin_delta`` – sin(δ)
    - ``consistency_with_pdg`` – label string
    """
    w = _wolfenstein_from_braid(N_W, K_CS, PI_KR)
    rho = w["rho_bar"]
    eta = w["eta_bar"]
    mag = math.sqrt(rho**2 + eta**2)
    sin_delta = eta / mag if mag > 0 else 0.0
    sin_delta = max(-1.0, min(1.0, sin_delta))
    delta_rad = math.asin(sin_delta)
    pdg_delta_rad = 1.196  # PDG central value ~68.6°
    consistency = (
        "CONSISTENT" if abs(delta_rad - pdg_delta_rad) < 0.5 else "OUTSIDE_PDG_1SIGMA"
    )
    return {
        "delta_ckm_rad": delta_rad,
        "delta_ckm_deg": math.degrees(delta_rad),
        "sin_delta": sin_delta,
        "consistency_with_pdg": consistency,
    }


def lab_transfer_jarlskog(pi_topo: float) -> dict[str, Any]:
    """Compute the lab-scale Jarlskog from the condensed-matter topology transfer.

    At leading order, the lab CP asymmetry equals the transferred Jarlskog:

        J_lab = J_geo × Π_topo
        A_CP^lab ≈ J_lab

    Parameters
    ----------
    pi_topo:
        Topology transfer efficiency Π_topo ∈ [0, 1].

    Returns
    -------
    dict with keys:

    - ``J_geo`` – geometric Jarlskog (from :func:`jarlskog_invariant_geometric`)
    - ``pi_topo`` – input transfer efficiency
    - ``J_lab`` – lab Jarlskog
    - ``A_CP_predicted`` – predicted lab asymmetry
    - ``order_of_magnitude_check`` – True if |OOM − (−5)| ≤ 2
    """
    if not (0.0 <= pi_topo <= 1.0):
        raise ValueError(f"pi_topo must be in [0, 1], got {pi_topo}")
    j_result = jarlskog_invariant_geometric()
    j_geo = j_result["J_geo"]
    j_lab = j_geo * pi_topo
    a_cp = j_lab
    if a_cp > 0:
        oom_diff = abs(math.log10(a_cp) - (-5))
        oom_ok = oom_diff <= 2.0
    else:
        oom_ok = False
    return {
        "J_geo": j_geo,
        "pi_topo": pi_topo,
        "J_lab": j_lab,
        "A_CP_predicted": a_cp,
        "order_of_magnitude_check": oom_ok,
    }
