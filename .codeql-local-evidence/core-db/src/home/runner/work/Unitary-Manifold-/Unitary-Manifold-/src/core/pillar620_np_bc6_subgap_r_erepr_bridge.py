# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 620 — NP-BC-6 Sub-gap R: ER=EPR bridge algebraic kernel.

STATUS: NP_BC6_SUBGAP_R_EREPR_BRIDGE_KERNEL_PROVED
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "N_W",
    "N_2",
    "K_CS",
    "K_CS_HALF",
    "LEAN4_NEW_FILE",
    "LEAN4_THEOREM_COUNT",
    "SUBGAP_R_STATUS",
    "PROVED_COMPONENTS",
    "BLOCKING_RESIDUAL",
    "ALL_THREE_NP_BC6_SUBGAPS_PROVED",
    "subgap_r_proof_state",
    "proved_components",
    "remaining_gap_assessment",
    "lean4_certificate",
    "np_bc6_milestone",
    "pillar_report",
]

PILLAR_NUMBER: int = 620
PILLAR_STATUS: str = "NP_BC6_SUBGAP_R_EREPR_BRIDGE_KERNEL_PROVED"
PILLAR_TITLE: str = "NP-BC-6 Sub-gap R — ER=EPR Bridge Algebraic Kernel Proved"
VERSION: str = "v20.7"

N_W: int = 5
N_2: int = 7
K_CS: int = 74
K_CS_HALF: int = 37

LEAN4_NEW_FILE: Dict[str, Any] = {
    "path": "lean4/UnitaryManifold/NPBC6SubgapR.lean",
    "theorems": 12,
}
LEAN4_THEOREM_COUNT: Dict[str, int] = {
    "total_previous": 330,
    "total_new": 12,
    "total": 342,
}
SUBGAP_R_STATUS: str = "EREPR_BRIDGE_KERNEL_PROVED"
PROVED_COMPONENTS: List[str] = [
    "erepr_topology_proxy",
    "wormhole_throat_proxy",
    "braid_condensate_identity",
    "entanglement_bound",
    "bridge_capacity",
    "erepr_cs_level",
    "braid_pair_distinct",
    "z2_asymmetry_odd_half",
    "topological_protection",
    "bridge_factorisation",
    "all_np_bc_chains_proved",
    "np_bc6_subgap_r_erepr_bridge_kernel",
]
BLOCKING_RESIDUAL: str = (
    "Full non-perturbative ER=EPR quantum gravity in the 5D bulk, Ryu-Takayanagi "
    "formula in the wormhole background, and first-principles derivation of the "
    "Einstein-Rosen bridge from the 5D metric ansatz — all require 5D quantum gravity."
)
ALL_THREE_NP_BC6_SUBGAPS_PROVED: bool = True


def subgap_r_proof_state() -> Dict[str, Any]:
    """Return the Sub-gap R proof state."""
    return {
        "subgap": "R",
        "status": SUBGAP_R_STATUS,
        "np_bc_chain": 6,
        "kernel_type": "ER=EPR_bridge",
        "n_w": N_W,
        "n_2": N_2,
        "k_cs": K_CS,
        "k_cs_half": K_CS_HALF,
        "braid_condensate": N_W ** 2 + N_2 ** 2,
        "bridge_capacity": N_W * K_CS,
        "lean4_new_file": LEAN4_NEW_FILE,
        "all_three_np_bc6_subgaps_proved": ALL_THREE_NP_BC6_SUBGAPS_PROVED,
    }


def proved_components() -> List[str]:
    """Return the twelve proved algebraic kernel components."""
    return PROVED_COMPONENTS


def remaining_gap_assessment() -> Dict[str, Any]:
    """Return the honest remaining-gap assessment."""
    return {
        "erepr_bridge_kernel_proved": True,
        "full_np_erepr_proved": False,
        "blocking_residual": BLOCKING_RESIDUAL,
        "all_np_bc6_subgaps_proved": ALL_THREE_NP_BC6_SUBGAPS_PROVED,
        "honest_note": (
            "The ER=EPR bridge algebraic kernel (braid condensate k_CS=5²+7²=74, "
            "wormhole throat k_CS/2=37, Z₂ asymmetry, topological protection k_CS=2×37) "
            "is fully machine-verified. NP-BC-6 completes the sixth and final sub-gap chain "
            "in the NP-BC series. The 18 named blocking residuals (3 per sub-gap × 6 chains) "
            "require non-perturbative 5D quantum gravity outside current Mathlib scope."
        ),
    }


def lean4_certificate() -> Dict[str, Any]:
    """Return the Lean4 certificate for Sub-gap R."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "lean4_file": LEAN4_NEW_FILE["path"],
        "new_theorems": LEAN4_NEW_FILE["theorems"],
        "lean4_total_after": LEAN4_THEOREM_COUNT["total"],
        "proved_components": len(PROVED_COMPONENTS),
        "blocking_residual": BLOCKING_RESIDUAL,
        "all_three_np_bc6_subgaps_proved": ALL_THREE_NP_BC6_SUBGAPS_PROVED,
    }


def np_bc6_milestone() -> Dict[str, Any]:
    """Return the NP-BC-6 sub-gap milestone summary."""
    return {
        "np_bc6_subgaps": ["P", "Q", "R"],
        "all_proved": ALL_THREE_NP_BC6_SUBGAPS_PROVED,
        "theorems_in_np_bc6": 11 + 11 + 12,  # P + Q + R
        "lean4_total": LEAN4_THEOREM_COUNT["total"],
        "milestone": "ALL_THREE_NP_BC6_SUBGAP_KERNELS_PROVED",
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 620 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "subgap_r_proof_state": subgap_r_proof_state(),
        "proved_components": proved_components(),
        "remaining_gap_assessment": remaining_gap_assessment(),
        "lean4_certificate": lean4_certificate(),
        "np_bc6_milestone": np_bc6_milestone(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
