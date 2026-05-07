# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""7D δ_CP integration into CKM ρ̄ chain (Wave 7 / W7-C)."""

from __future__ import annotations

import math
from typing import Dict

from src.core.ckm_rhobar_nlo_braid_correction import (
    RHO_BAR_NLO_PCT_ERR,
    RHO_BAR_PDG,
    r_b_geometric,
)
from src.sevend.discrete_torsion_cp import DELTA_CP_GEO_RAD

__all__ = [
    "DELTA_CP_7D_RAD",
    "DELTA_CP_7D_DEG",
    "RHO_BAR_7D",
    "RHO_BAR_7D_PCT_ERR",
    "STATUS",
    "delta_cp_constraint_7d",
    "rho_bar_with_7d_delta",
    "rhobar_integration_kill_switch",
    "ckm_rhobar_7d_summary",
]

DELTA_CP_7D_RAD = DELTA_CP_GEO_RAD
DELTA_CP_7D_DEG = math.degrees(DELTA_CP_7D_RAD)



def delta_cp_constraint_7d() -> Dict[str, float]:
    """Return the geometric 7D δ_CP constraint used in the CKM chain."""
    return {
        "delta_cp_rad": DELTA_CP_7D_RAD,
        "delta_cp_deg": DELTA_CP_7D_DEG,
    }



def rho_bar_with_7d_delta(delta_cp_rad: float = DELTA_CP_7D_RAD) -> Dict[str, float]:
    """Compute ρ̄ using the 7D geometric CP phase constraint."""
    r_b = float(r_b_geometric()["R_b"])
    rho = r_b * math.cos(delta_cp_rad)
    residual = abs(rho - RHO_BAR_PDG) / max(RHO_BAR_PDG, 1e-30)
    return {
        "rho_bar": rho,
        "delta_cp_rad": delta_cp_rad,
        "delta_cp_deg": math.degrees(delta_cp_rad),
        "R_b": r_b,
        "rho_bar_pdg": RHO_BAR_PDG,
        "pct_err_vs_pdg": residual * 100.0,
        "residual": residual,
    }


_RHO = rho_bar_with_7d_delta()
RHO_BAR_7D = float(_RHO["rho_bar"])
RHO_BAR_7D_PCT_ERR = float(_RHO["pct_err_vs_pdg"])
STATUS = "CONSTRAINED+" if RHO_BAR_7D_PCT_ERR < 10.0 else "CONSTRAINED"



def rhobar_integration_kill_switch(max_pct_err: float = 20.0) -> Dict[str, object]:
    """Kill-switch for W7-C: ρ̄ residual must be <= 20%."""
    current = rho_bar_with_7d_delta()
    passed = current["pct_err_vs_pdg"] <= max_pct_err
    improvement = float(RHO_BAR_NLO_PCT_ERR) - float(current["pct_err_vs_pdg"])
    return {
        "rho_bar_7d": current["rho_bar"],
        "rho_bar_pdg": current["rho_bar_pdg"],
        "pct_err_7d": current["pct_err_vs_pdg"],
        "pct_err_previous_nlo": float(RHO_BAR_NLO_PCT_ERR),
        "improvement_pct_points": improvement,
        "threshold_pct": max_pct_err,
        "pass": passed,
        "status": STATUS,
    }



def ckm_rhobar_7d_summary() -> Dict[str, object]:
    """Consolidated W7-C artifact for MAS gate updates."""
    ks = rhobar_integration_kill_switch()
    return {
        "module": "src/sevend/ckm_rhobar_7d_integration.py",
        "delta_cp_constraint": delta_cp_constraint_7d(),
        "rho_bar_result": rho_bar_with_7d_delta(),
        "kill_switch": ks,
        "p14_gate_update": {
            "current_status": STATUS,
            "recommendation": (
                "Promote to CONSTRAINED+" if STATUS == "CONSTRAINED+" else "Maintain CONSTRAINED"
            ),
        },
    }
