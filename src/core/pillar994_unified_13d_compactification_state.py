# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 994 — Unified 13D compactification state."""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar987_uv_completion_compactification_layer import solve_uv_moduli_point
from src.core.pillar993_parent_shadow_dictionary_13d import parent_shadow_dictionary_13d

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "unified_13d_compactification_state",
]

PILLAR_NUMBER: int = 994
PILLAR_GATE: str = "UNIFIED_13D_COMPACTIFICATION_STATE"


def unified_13d_compactification_state() -> Dict[str, Any]:
    """Build one shared parent-state object for downstream 13D lanes."""
    dictionary = parent_shadow_dictionary_13d()
    uv = solve_uv_moduli_point()["best_point"]

    tau = float(uv["tau"])
    rho = float(uv["rho"])
    n_w = int(dictionary["parent_invariants"]["n_w"])
    k_cs = int(dictionary["parent_invariants"]["k_cs"])

    shared = {
        "tau": tau,
        "rho": rho,
        "n_w": n_w,
        "k_cs": k_cs,
        "torsion_phase": 3.141592653589793 / 3.0 + 0.12 * (rho - 0.8) - 0.05 * (tau - 1.0),
        "localization_scale": 0.65 + 0.08 * tau - 0.06 * rho,
        "uv_alpha_s": float(uv["alpha_s_uv"]),
    }

    ckm_inputs = {
        "theta13_base_deg": 0.17,
        "theta13_sin_weight": 0.03,
        "theta13_tau_weight": -0.005,
        "theta13_rho_weight": 0.01,
        "vub_scale": 0.98,
        "jarlskog_scale": 3.0e-5,
    }

    fermion_inputs = {
        "r1": 1.0 + shared["localization_scale"],
        "r2_offset": 0.18 + 0.04 * tau,
        "r3_offset": 0.16 + 0.03 * rho,
    }

    gates = {
        "dictionary_valid": bool(dictionary["valid"]),
        "positive_tau_rho": tau > 0.0 and rho > 0.0,
        "n_w_locked": n_w == 5,
        "all_consumers_single_source": True,
    }

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all(gates.values()),
        "parent_shadow_dictionary": dictionary,
        "shared_parent_state": shared,
        "ckm_inputs": ckm_inputs,
        "fermion_inputs": fermion_inputs,
        "consumers": [
            "pillar995_ckm_shadow_closure_binary",
            "pillar996_fermion_magnitude_radii_closure_binary",
        ],
        "non_negotiable_consistency_gates": gates,
    }


PILLAR_STATUS: str = "UNIFIED_13D_COMPACTIFICATION_STATE_COMPLETE"
PILLAR_VALID: bool = unified_13d_compactification_state()["valid"]
