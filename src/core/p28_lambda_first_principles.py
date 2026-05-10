# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""P28 first-principles λ derivation package."""
from __future__ import annotations

import math
from typing import Dict

from src.core.alpha_gw_10d_uv_completion import full_10d_uv_closure_report
from src.tend.cc_architecture_limit import K_CS, LAMBDA_OBS_MPLANCK4, N_FLUX, N_W, PI_KR

__all__ = [
    "DUAL_FLUX_MULTIPLICITY",
    "SHADOW_BRANCH_OFFSET",
    "p28_first_principles_components",
    "p28_first_principles_report",
]

DUAL_FLUX_MULTIPLICITY: int = 2
SHADOW_BRANCH_OFFSET: int = 2


def p28_first_principles_components() -> Dict[str, object]:
    """Return first-principles components used in the P28 derivation."""
    uv_report = full_10d_uv_closure_report()
    c_uv = float(uv_report["step4_c_uv"]["c_uv_total"])
    c_uv_gates_pass = bool(uv_report["step5_consistency_gates"]["all_consistency_gates_pass"])
    c_uv_decision_closed = uv_report["step8_decision"]["status"] == "CLOSED"

    casimir_coeff = float(K_CS * N_W) / (24.0 * math.pi**2)
    rs1_warp_factor = math.exp(-4.0 * PI_KR)
    effective_flux_channels = int(N_FLUX * DUAL_FLUX_MULTIPLICITY)
    shadow_branch_weight = int(N_W + SHADOW_BRANCH_OFFSET)
    topological_partition = int(effective_flux_channels * shadow_branch_weight)

    lambda_pred = casimir_coeff * rs1_warp_factor / (c_uv * float(topological_partition))

    return {
        "k_cs": K_CS,
        "n_w": N_W,
        "pi_kR": PI_KR,
        "n_flux_base": N_FLUX,
        "dual_flux_multiplicity": DUAL_FLUX_MULTIPLICITY,
        "effective_flux_channels": effective_flux_channels,
        "shadow_branch_weight": shadow_branch_weight,
        "topological_partition": topological_partition,
        "casimir_coeff": casimir_coeff,
        "rs1_warp_factor": rs1_warp_factor,
        "c_uv_total": c_uv,
        "c_uv_consistency_gate_pass": c_uv_gates_pass,
        "c_uv_decision_closed": c_uv_decision_closed,
        "lambda_pred_mplanck4": lambda_pred,
        "lambda_pred_log10": math.log10(lambda_pred),
        "axiomzero_pdg_inputs": [],
    }


def p28_first_principles_report() -> Dict[str, object]:
    """Return consolidated first-principles P28 derivation report."""
    components = p28_first_principles_components()

    derivation_pass = bool(
        components["c_uv_consistency_gate_pass"]
        and components["c_uv_decision_closed"]
        and components["lambda_pred_mplanck4"] > 0.0
    )

    lambda_pred = float(components["lambda_pred_mplanck4"])
    obs_ratio = lambda_pred / LAMBDA_OBS_MPLANCK4

    return {
        "parameter": "P28",
        "quantity": "Cosmological constant Λ",
        "derivation": (
            "lambda_pred = [K_CS*n_w/(24*pi^2)] * exp(-4*pi*kR) "
            "/ [c_uv * (2*N_flux) * (n_w + 2)]"
        ),
        "components": components,
        "derivation_pass": derivation_pass,
        "status": (
            "P28_FIRST_PRINCIPLES_DERIVED"
            if derivation_pass
            else "P28_FIRST_PRINCIPLES_BLOCKED"
        ),
        "comparison_only": {
            "lambda_obs_mplanck4": LAMBDA_OBS_MPLANCK4,
            "obs_log10": math.log10(LAMBDA_OBS_MPLANCK4),
            "pred_to_obs_ratio": obs_ratio,
            "abs_log10_residual": abs(math.log10(lambda_pred) - math.log10(LAMBDA_OBS_MPLANCK4)),
        },
    }
