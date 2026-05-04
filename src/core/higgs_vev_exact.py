# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/higgs_vev_exact.py
============================
Pillar 139 — Higgs VEV from Geometry.

Derives v (Higgs vacuum expectation value) from the UM geometric
parameters via the quartic self-coupling and one-loop RGE correction.

Key steps
---------
1. Tree-level quartic:
       λ_H^tree = 25/148 ≈ 0.168919
       (from n_w=5, k_CS=74: numerator=n_w²=25, denominator=2×k_CS=148)

2. KK threshold scale:
       M_KK = M_Pl × exp(-πkR)   with M_Pl=1.2209×10¹⁹ GeV, πkR=37
       → M_KK ≈ 1041.8 GeV

3. One-loop top-Yukawa RGE correction (dominant contribution):
       Δλ = -(6 y_t⁴)/(16π²) × log(M_KK / v)
       with y_t = c_R^(ν₁) = 23/25 = 0.920 (from n_w=5 geometry)

4. Effective coupling:
       λ_eff = λ_H^tree + Δλ ≈ 0.12966

5. VEV prediction:
       v_pred = m_H / sqrt(2 λ_eff)
       → v_pred ≈ 245.96 GeV   (PDG: 246.22 GeV,  error ≈ 0.10%)
"""

from __future__ import annotations
import math
from src.core.sm_free_parameters import (
    N_W, K_CS, PI_K_R,
    V_HIGGS_GEV, M_HIGGS_GEV,
)

__all__ = [
    "higgs_vev_from_geometry",
    "higgs_vev_rge_correction",
    "higgs_vev_closure_status",
]

_M_PL_GEV: float = 1.2209e19   # reduced Planck mass [GeV]


def higgs_vev_rge_correction(y_t: float, m_kk_gev: float, v_gev: float) -> float:
    """One-loop top-Yukawa correction to the Higgs quartic coupling.

    Δλ = -(6 y_t⁴) / (16π²) × log(M_KK / v)

    Parameters
    ----------
    y_t      : top Yukawa coupling
    m_kk_gev : KK threshold scale [GeV]
    v_gev    : Higgs VEV [GeV] (used as IR scale)

    Returns
    -------
    float : Δλ  (negative, reducing λ from tree value)
    """
    log_ratio = math.log(m_kk_gev / v_gev)
    delta_lambda = -(6.0 * y_t**4) / (16.0 * math.pi**2) * log_ratio
    return delta_lambda


def higgs_vev_from_geometry(
    n_w: int = 5,
    k_cs: int = 74,
    pi_kr: float = 37.0,
    m_h_gev: float = 125.25,
    y_t: float = 0.920,
    max_iter: int = 50,
    tol: float = 1e-6,
) -> dict:
    """Derive the Higgs VEV from UM geometry via self-consistent iteration.

    The RGE correction Δλ = -(6 y_t⁴)/(16π²) × log(M_KK/v) depends on v
    itself.  A genuine self-consistent prediction requires iterating:

        1. Start with v_guess from the tree-level quartic.
        2. Compute Δλ(v_guess) using v_guess as the IR renormalization scale.
        3. Update v_new = m_H / √(2 λ_eff(v_guess)).
        4. Repeat until |v_new - v_guess| < tol × v_guess.

    This eliminates the circularity of the previous implementation, which
    used the PDG VEV as the IR scale in its own correction.

    NOTE ON INPUTS: m_H is taken from PDG (or from Pillar 134 which itself
    uses v_PDG and m_t_PDG).  The prediction of v therefore depends on m_H
    as a PDG input, which limits the independence of the result.

    Parameters
    ----------
    n_w    : winding number (default 5)
    k_cs   : Chern-Simons level (default 74)
    pi_kr  : πkR Randall-Sundrum parameter (default 37)
    m_h_gev: Higgs boson mass [GeV] (default PDG 125.25)
    y_t    : top Yukawa (geometric: c_R = 23/25 = 0.920)
    max_iter: maximum self-consistency iterations (default 50)
    tol    : fractional convergence tolerance (default 1e-6)

    Returns
    -------
    dict with full calculation details and comparison to PDG
    """
    lambda_tree = n_w**2 / (2.0 * k_cs)        # 25/148
    m_kk_gev = _M_PL_GEV * math.exp(-pi_kr)

    # Self-consistent iteration: v_guess → λ_eff(v_guess) → v_new
    # Seed with the tree-level VEV (no RGE correction yet)
    v_guess = m_h_gev / math.sqrt(2.0 * lambda_tree)
    converged = False
    n_iter = 0
    for n_iter in range(1, max_iter + 1):
        delta_lambda = higgs_vev_rge_correction(y_t, m_kk_gev, v_guess)
        lambda_eff = lambda_tree + delta_lambda
        if lambda_eff <= 0:
            break
        v_new = m_h_gev / math.sqrt(2.0 * lambda_eff)
        if abs(v_new - v_guess) < tol * v_guess:
            v_guess = v_new
            converged = True
            break
        v_guess = v_new

    v_pred_gev = v_guess
    pct_error = abs(v_pred_gev - V_HIGGS_GEV) / V_HIGGS_GEV * 100.0

    if converged:
        status = f"GEOMETRIC PREDICTION (self-consistent, {pct_error:.2f}%, m_H PDG input)"
    else:
        status = "CONSTRAINED (self-consistent iteration did not converge; result unreliable)"

    return {
        "lambda_tree": lambda_tree,
        "M_KK_gev": m_kk_gev,
        "delta_lambda": delta_lambda if lambda_eff > 0 else 0.0,
        "lambda_eff": lambda_eff if lambda_eff > 0 else float("nan"),
        "v_pred_gev": v_pred_gev,
        "v_pdg_gev": V_HIGGS_GEV,
        "pct_error": pct_error,
        "status": status,
        "y_t_used": y_t,
        "pi_kr": pi_kr,
        "converged": converged,
        "n_iterations": n_iter,
        "honest_note": (
            "v is derived self-consistently: the RGE correction log(M_KK/v) "
            "is evaluated at the iterated v rather than the PDG value. "
            "m_H = 125.25 GeV is a PDG input; the prediction is conditional on it."
        ),
    }


def higgs_vev_closure_status() -> dict:
    """Return closure status for Pillar 139."""
    r = higgs_vev_from_geometry()
    return {
        "pillar": 139,
        "parameter": "v (Higgs VEV)",
        "status": r["status"],
        "predicted_gev": r["v_pred_gev"],
        "pdg_gev": V_HIGGS_GEV,
        "pct_error": r["pct_error"],
        "formula": "v = m_H / sqrt(2 λ_eff),  λ_eff = 25/148 + Δλ_top (self-consistent)",
        "inputs": [
            "n_w=5 (topology)",
            "k_CS=74 (braiding)",
            "πkR=37 (RS geometry)",
            "m_H=125.25 GeV (PDG, derived by Pillar 134)",
        ],
        "converged": r["converged"],
        "n_iterations": r["n_iterations"],
        "honest_note": r["honest_note"],
        "closed": r["converged"],
    }
