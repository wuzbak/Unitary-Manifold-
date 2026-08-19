# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar689_ckm_triangle_fn_geometry.py
==========================
Pillar 689 — CKM Triangle FN Geometry

Builds the Wolfenstein/FN CKM triangle using the Layer 2 FN phase-shift ansatz.
The rho-bar channel remains poor (~39.6% residual), but eta-bar and the
Jarlskog invariant stay numerically close to PDG once the triangle is closed.
So the triangle is internally consistent while the rho-bar observable remains an
architecture-limit bottleneck.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
from typing import Any, Dict, Tuple

__all__ = [
    "N_W",
    "K_CS",
    "N1",
    "N2",
    "W_RHOBAR_PDG",
    "W_LAMBDA_PDG",
    "W_A_PDG",
    "W_ETABAR_PDG",
    "W_J_PDG",
    "EPSILON_FN",
    "FN_CHARGES_U",
    "FN_CHARGES_D",
    "eta_bar_fn",
    "wolfenstein_fn_corrected",
    "jarlskog_invariant_fn",
    "ckm_triangle_fn_geometry",
]

N_W = 5
K_CS = 74
N1 = 5
N2 = 7
W_RHOBAR_PDG = 0.159
W_LAMBDA_PDG = 0.225
W_A_PDG = 0.826
W_ETABAR_PDG = 0.348
W_J_PDG = 3.08e-5
EPSILON_FN = N_W / K_CS
M_U_MEV = 2.16
M_T_MEV = 172760.0
FN_CHARGES_U: Tuple[int, int, int] = (0, 2, 5)
FN_CHARGES_D: Tuple[int, int, int] = (3, 2, 0)


def _r_b() -> float:
    vub_geo = math.sqrt(M_U_MEV / M_T_MEV)
    a_geo = math.sqrt(N1 / N2)
    return vub_geo / (a_geo * W_LAMBDA_PDG**3)


def _delta_fn_rad() -> float:
    harmonic = 2.0 * math.pi / N_W
    return math.atan2(EPSILON_FN * math.sin(harmonic), 1.0 - EPSILON_FN * math.cos(harmonic))


def _delta_sub_rad() -> float:
    return 2.0 * math.atan2(N1, N2)


def _rho_bar_fn_value() -> float:
    return _r_b() * math.cos(_delta_sub_rad() + _delta_fn_rad())


def eta_bar_fn() -> Dict[str, Any]:
    """Return the FN-closed eta-bar from R_b^2 = rho-bar^2 + eta-bar^2."""
    r_b = _r_b()
    rho_bar = _rho_bar_fn_value()
    eta_bar = math.sqrt(max(r_b * r_b - rho_bar * rho_bar, 0.0))
    return {
        "r_b": r_b,
        "rho_bar_fn": rho_bar,
        "eta_bar_fn": eta_bar,
        "eta_bar_pdg": W_ETABAR_PDG,
        "residual_percent": abs(eta_bar - W_ETABAR_PDG) / W_ETABAR_PDG * 100.0,
        "formula": "eta_bar = sqrt(R_b^2 - rho_bar_FN^2)",
    }


def wolfenstein_fn_corrected() -> Dict[str, Any]:
    """Return Wolfenstein parameters with explicit O(epsilon_FN) bookkeeping."""
    c_lambda = abs(FN_CHARGES_D[0] - FN_CHARGES_D[1]) / K_CS
    c_a = (abs(FN_CHARGES_U[1] - FN_CHARGES_U[2]) + abs(FN_CHARGES_D[1] - FN_CHARGES_D[2])) / (2.0 * K_CS)
    lambda_fn = W_LAMBDA_PDG * (1.0 + EPSILON_FN * c_lambda)
    a_fn = W_A_PDG * (1.0 + EPSILON_FN * c_a)
    eta = eta_bar_fn()
    return {
        "lambda_geo": W_LAMBDA_PDG,
        "lambda_fn": lambda_fn,
        "lambda_correction": lambda_fn - W_LAMBDA_PDG,
        "A_geo": W_A_PDG,
        "A_fn": a_fn,
        "A_correction": a_fn - W_A_PDG,
        "rho_bar_fn": eta["rho_bar_fn"],
        "eta_bar_fn": eta["eta_bar_fn"],
        "epsilon_fn": EPSILON_FN,
        "order_tracking": "O(epsilon_FN)",
        "charge_coefficients": {
            "c_lambda": c_lambda,
            "c_A": c_a,
        },
    }


def jarlskog_invariant_fn() -> Dict[str, Any]:
    """Return geometric and FN-corrected Jarlskog invariants."""
    eta = eta_bar_fn()
    wolf = wolfenstein_fn_corrected()
    j_geo = W_LAMBDA_PDG**6 * W_A_PDG**2 * eta["eta_bar_fn"]
    j_fn = wolf["lambda_fn"]**6 * wolf["A_fn"]**2 * eta["eta_bar_fn"]
    return {
        "J_CP_geo": j_geo,
        "J_CP_fn": j_fn,
        "J_CP_pdg": W_J_PDG,
        "geo_residual_percent": abs(j_geo - W_J_PDG) / W_J_PDG * 100.0,
        "fn_residual_percent": abs(j_fn - W_J_PDG) / W_J_PDG * 100.0,
        "formula_geo": "lambda^6 * A^2 * eta_bar",
        "formula_fn": "lambda_FN^6 * A_FN^2 * eta_bar_FN",
    }


def ckm_triangle_fn_geometry() -> Dict[str, Any]:
    """Return the FN-corrected CKM unitarity triangle package."""
    eta = eta_bar_fn()
    wolf = wolfenstein_fn_corrected()
    jarlskog = jarlskog_invariant_fn()
    delta_eff_rad = _delta_sub_rad() + _delta_fn_rad()
    return {
        "pillar": 689,
        "status": "CKM_TRIANGLE_FN_GEOMETRY_BUILT",
        "triangle_coordinates": {
            "origin": (0.0, 0.0),
            "apex": (wolf["rho_bar_fn"], wolf["eta_bar_fn"]),
            "unit_point": (1.0, 0.0),
        },
        "r_b": eta["r_b"],
        "delta_eff_deg": math.degrees(delta_eff_rad),
        "wolfenstein": wolf,
        "eta_bar": eta,
        "jarlskog": jarlskog,
        "honest_note": (
            "The FN geometry produces a healthy eta-bar and J_CP, but rho-bar itself "
            "remains far from PDG because the positive phase shift suppresses cos(delta_eff)."
        ),
    }
