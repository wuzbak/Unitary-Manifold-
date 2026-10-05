# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/core/pillar688_jarlskog_layer2_fn_mixing.py
==========================
Pillar 688 — Jarlskog Layer 2 FN Mixing

Implements the Sprint Y Froggatt-Nielsen (FN) Layer 2 correction to the CKM
phase relevant for the Wolfenstein rho-bar closure problem.

Honest status
-------------
Using the requested FN phase-shift formula,
    delta_FN = arctan(epsilon_FN * sin(2*pi/n_w) / (1 - epsilon_FN*cos(2*pi/n_w)))
with epsilon_FN = 5/74, the effective phase moves from
    delta_sub ≈ 71.08°  to  delta_eff ≈ 74.83°.
That decreases rho-bar from the Layer 1 value ~0.119 to ~0.096, i.e. the PDG
residual grows to ~39.6%.  So this implementation does NOT close the rho-bar
gap; it certifies an architecture-limit outcome for this specific Layer 2 ansatz.

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
    "EPSILON_FN",
    "M_U_MEV",
    "M_T_MEV",
    "FN_CHARGES_U",
    "FN_CHARGES_D",
    "fn_phase_correction",
    "rho_bar_fn_corrected",
    "layer2_closure_status",
    "jarlskog_layer2_result",
]

N_W = 5
K_CS = 74
N1 = 5
N2 = 7
W_RHOBAR_PDG = 0.159
W_LAMBDA_PDG = 0.225
W_A_PDG = 0.826
EPSILON_FN = N_W / K_CS
M_U_MEV = 2.16
M_T_MEV = 172760.0
FN_CHARGES_U: Tuple[int, int, int] = (0, 2, 5)
FN_CHARGES_D: Tuple[int, int, int] = (3, 2, 0)
PILLAR_STATUS = "ARCHITECTURE_LIMIT_CERTIFIED"


def _r_b() -> float:
    vub_geo = math.sqrt(M_U_MEV / M_T_MEV)
    a_geo = math.sqrt(N1 / N2)
    return vub_geo / (a_geo * W_LAMBDA_PDG**3)


def _delta_sub_rad() -> float:
    return 2.0 * math.atan2(N1, N2)


def _rho_gap_percent(rho_bar: float) -> float:
    return abs(rho_bar - W_RHOBAR_PDG) / W_RHOBAR_PDG * 100.0


def fn_phase_correction() -> Dict[str, Any]:
    """Return the FN phase correction entering the effective CKM phase."""
    harmonic = 2.0 * math.pi / N_W
    numerator = EPSILON_FN * math.sin(harmonic)
    denominator = 1.0 - EPSILON_FN * math.cos(harmonic)
    delta_fn_rad = math.atan2(numerator, denominator)
    return {
        "epsilon_fn": EPSILON_FN,
        "harmonic_rad": harmonic,
        "harmonic_deg": math.degrees(harmonic),
        "numerator": numerator,
        "denominator": denominator,
        "delta_fn_rad": delta_fn_rad,
        "delta_fn_deg": math.degrees(delta_fn_rad),
        "fn_charges_u": FN_CHARGES_U,
        "fn_charges_d": FN_CHARGES_D,
        "formula": "atan(epsilon_FN*sin(2*pi/n_w)/(1-epsilon_FN*cos(2*pi/n_w)))",
    }


def rho_bar_fn_corrected() -> Dict[str, Any]:
    """Compute rho-bar after applying the FN Layer 2 phase shift."""
    r_b = _r_b()
    delta_sub_rad = _delta_sub_rad()
    delta_fn = fn_phase_correction()
    delta_eff_rad = delta_sub_rad + delta_fn["delta_fn_rad"]
    rho_bar_fn = r_b * math.cos(delta_eff_rad)
    layer1_rho = r_b * math.cos(delta_sub_rad)
    layer1_gap = _rho_gap_percent(layer1_rho)
    fn_gap = _rho_gap_percent(rho_bar_fn)
    return {
        "r_b": r_b,
        "delta_sub_rad": delta_sub_rad,
        "delta_sub_deg": math.degrees(delta_sub_rad),
        "delta_fn_rad": delta_fn["delta_fn_rad"],
        "delta_fn_deg": delta_fn["delta_fn_deg"],
        "delta_eff_rad": delta_eff_rad,
        "delta_eff_deg": math.degrees(delta_eff_rad),
        "rho_bar_layer1": layer1_rho,
        "rho_bar_fn": rho_bar_fn,
        "rho_bar_pdg": W_RHOBAR_PDG,
        "residual_percent": fn_gap,
        "improvement_vs_layer1_percent_points": layer1_gap - fn_gap,
        "formula": "rho_bar_FN = R_b*cos(delta_sub + delta_FN)",
        "honest_note": (
            "For the requested positive FN phase shift, the effective angle grows and "
            "rho-bar moves away from the PDG central value rather than toward it."
        ),
    }


def layer2_closure_status() -> Dict[str, Any]:
    """Classify the FN Layer 2 outcome against 10% and 5% targets."""
    rho = rho_bar_fn_corrected()
    gap = rho["residual_percent"]
    if gap < 5.0:
        status = "HARDGATE_CANDIDATE"
    elif gap < 10.0:
        status = "ARCHITECTURE_LIMIT"
    else:
        status = "ARCHITECTURE_LIMIT_CERTIFIED"
    return {
        "pillar": 688,
        "status": status,
        "gap_percent": gap,
        "passes_10_percent": gap < 10.0,
        "passes_5_percent": gap < 5.0,
        "rho_bar_fn": rho["rho_bar_fn"],
        "rho_bar_pdg": W_RHOBAR_PDG,
        "delta_eff_deg": rho["delta_eff_deg"],
        "architecture_limit_reason": (
            "The requested FN Layer 2 ansatz increases the CKM phase by about 3.75°, "
            "which suppresses rho-bar further to about 0.096."
        ),
    }


def jarlskog_layer2_result() -> Dict[str, Any]:
    """Return the full Pillar 688 analytic package."""
    return {
        "pillar": 688,
        "title": "Jarlskog Layer 2 FN Mixing",
        "status": PILLAR_STATUS,
        "constants": {
            "N_W": N_W,
            "K_CS": K_CS,
            "N1": N1,
            "N2": N2,
            "W_RHOBAR_PDG": W_RHOBAR_PDG,
            "EPSILON_FN": EPSILON_FN,
        },
        "fn_phase_correction": fn_phase_correction(),
        "rho_bar_fn_corrected": rho_bar_fn_corrected(),
        "layer2_closure_status": layer2_closure_status(),
    }
