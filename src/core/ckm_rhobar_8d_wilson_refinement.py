# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""WS-C++: 8D Wilson-line CKM ρ̄ refinement hard-gate package (P14)."""

from __future__ import annotations

import math
from typing import Dict

from src.core.ckm_rhobar_nlo_braid_correction import RHO_BAR_PDG, r_b_geometric
from src.core.pillar215_ckm_rhobar_closure import K_CS, N_W, PI_K_R, delta_q_deg
from src.eightd.wilson_line_gauge import rung3_gate_evidence
from src.sevend.ckm_rhobar_7d_integration import DELTA_CP_7D_RAD

__all__ = [
    "WILSON_BLEND_WEIGHT",
    "DELTA_CP_8D_REFINED_RAD",
    "DELTA_CP_8D_REFINED_DEG",
    "RHO_BAR_8D_REFINED",
    "RHO_BAR_8D_REFINED_PCT_ERR",
    "GATE_PASSED",
    "P14_STATUS",
    "wilson_line_blend_weight",
    "delta_cp_8d_refined",
    "rho_bar_8d_refined",
    "p14_hard_gates",
    "wscpp_summary",
]


def wilson_line_blend_weight() -> float:
    """Return the 8D Wilson-line blend weight used for phase refinement."""
    return PI_K_R / (PI_K_R + (K_CS / 2.0) + N_W)


def delta_cp_8d_refined() -> Dict[str, float]:
    """Blend 7D discrete-torsion δ with q-deformed phase using 8D weight."""
    weight = wilson_line_blend_weight()
    delta_q_rad = math.radians(delta_q_deg())
    delta_refined = (1.0 - weight) * DELTA_CP_7D_RAD + weight * delta_q_rad
    return {
        "weight": weight,
        "delta_7d_rad": DELTA_CP_7D_RAD,
        "delta_q_rad": delta_q_rad,
        "delta_refined_rad": delta_refined,
        "delta_refined_deg": math.degrees(delta_refined),
    }


def rho_bar_8d_refined(delta_cp_rad: float | None = None) -> Dict[str, float]:
    """Compute ρ̄ from the 8D-refined CKM phase."""
    if delta_cp_rad is None:
        delta_cp_rad = delta_cp_8d_refined()["delta_refined_rad"]
    r_b = float(r_b_geometric()["R_b"])
    rho = r_b * math.cos(delta_cp_rad)
    pct_err = abs(rho - RHO_BAR_PDG) / max(RHO_BAR_PDG, 1e-30) * 100.0
    return {
        "delta_cp_rad": delta_cp_rad,
        "delta_cp_deg": math.degrees(delta_cp_rad),
        "R_b": r_b,
        "rho_bar": rho,
        "rho_bar_pdg": RHO_BAR_PDG,
        "pct_err_vs_pdg": pct_err,
    }


def p14_hard_gates(
    residual_threshold_pct: float = 5.0,
    robustness_window_deg: float = 2.0,
    robustness_threshold_pct: float = 5.5,
) -> Dict[str, object]:
    """Evaluate residual, robustness, and AxiomZero purity gates for P14."""
    base = rho_bar_8d_refined()
    delta_base = base["delta_cp_rad"]
    minus = rho_bar_8d_refined(delta_base - math.radians(robustness_window_deg))
    plus = rho_bar_8d_refined(delta_base + math.radians(robustness_window_deg))
    worst_case = max(minus["pct_err_vs_pdg"], plus["pct_err_vs_pdg"])
    rung3 = rung3_gate_evidence()
    gates = {
        "residual_gate": base["pct_err_vs_pdg"] <= residual_threshold_pct,
        "robustness_gate": worst_case <= robustness_threshold_pct,
        "axiomzero_purity_gate": bool(rung3["kill_switch_pass"]),
    }
    return {
        "base_result": base,
        "robustness_minus": minus,
        "robustness_plus": plus,
        "worst_case_pct_err": worst_case,
        "residual_threshold_pct": residual_threshold_pct,
        "robustness_threshold_pct": robustness_threshold_pct,
        "gates": gates,
        "hard_gate_pass": all(gates.values()),
    }


_DELTA = delta_cp_8d_refined()
_RHO = rho_bar_8d_refined(_DELTA["delta_refined_rad"])
_GATES = p14_hard_gates()

WILSON_BLEND_WEIGHT: float = _DELTA["weight"]
DELTA_CP_8D_REFINED_RAD: float = _DELTA["delta_refined_rad"]
DELTA_CP_8D_REFINED_DEG: float = _DELTA["delta_refined_deg"]
RHO_BAR_8D_REFINED: float = _RHO["rho_bar"]
RHO_BAR_8D_REFINED_PCT_ERR: float = _RHO["pct_err_vs_pdg"]
GATE_PASSED: bool = bool(_GATES["hard_gate_pass"])
P14_STATUS: str = "GEOMETRIC PREDICTION" if GATE_PASSED else "CONSTRAINED"


def wscpp_summary() -> Dict[str, object]:
    """Return consolidated WS-C++ evidence payload for MAS ledgers."""
    return {
        "workstream": "WS-C++",
        "parameter": "P14 (ρ̄_CKM)",
        "delta_refined_deg": DELTA_CP_8D_REFINED_DEG,
        "rho_bar_refined": RHO_BAR_8D_REFINED,
        "rho_bar_refined_pct_err": RHO_BAR_8D_REFINED_PCT_ERR,
        "hard_gates": _GATES,
        "gate_passed": GATE_PASSED,
        "status": P14_STATUS,
        "verdict": (
            "8D refinement attempted with hard-gate matrix. "
            "Residual can improve strongly, but robustness gate is not yet closed; "
            "status remains CONSTRAINED until all gates pass."
            if not GATE_PASSED
            else "All gates passed; P14 eligible for promotion."
        ),
    }
