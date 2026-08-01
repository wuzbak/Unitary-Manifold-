# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 618 — NP-BC-6 Sub-gap P: KK loop correction algebraic kernel.

STATUS: NP_BC6_SUBGAP_P_KK_LOOP_KERNEL_PROVED
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "N_W",
    "K_CS",
    "K_CS_HALF",
    "LEAN4_NEW_FILE",
    "LEAN4_THEOREM_COUNT",
    "SUBGAP_P_STATUS",
    "PROVED_COMPONENTS",
    "BLOCKING_RESIDUAL",
    "subgap_p_proof_state",
    "proved_components",
    "remaining_gap_assessment",
    "lean4_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 618
PILLAR_STATUS: str = "NP_BC6_SUBGAP_P_KK_LOOP_KERNEL_PROVED"
PILLAR_TITLE: str = "NP-BC-6 Sub-gap P — KK Loop Correction Algebraic Kernel Proved"
VERSION: str = "v20.7"

N_W: int = 5
K_CS: int = 74
K_CS_HALF: int = 37

LEAN4_NEW_FILE: Dict[str, Any] = {
    "path": "lean4/UnitaryManifold/NPBC6SubgapP.lean",
    "theorems": 11,
}
LEAN4_THEOREM_COUNT: Dict[str, int] = {
    "total_previous": 308,
    "total_new": 11,
    "total": 319,
}
SUBGAP_P_STATUS: str = "KK_LOOP_KERNEL_PROVED"
PROVED_COMPONENTS: List[str] = [
    "kk_loop_order_bound",
    "kk_loop_correction_proxy",
    "winding_tower_convergence",
    "loop_level_consistency",
    "braid_loop_period",
    "first_kk_loop_level",
    "kk_mass_hierarchy_proxy",
    "loop_trace_proxy",
    "braid_pair_identity",
    "kk_loop_suppression_honest",
    "np_bc6_subgap_p_kk_loop_kernel",
]
BLOCKING_RESIDUAL: str = (
    "Full non-perturbative two-loop EW-KK diagram and Bessel-resummed "
    "infinite KK-tower loop sum — outside current Mathlib scope."
)


def subgap_p_proof_state() -> Dict[str, Any]:
    """Return the Sub-gap P proof state."""
    return {
        "subgap": "P",
        "status": SUBGAP_P_STATUS,
        "np_bc_chain": 6,
        "kernel_type": "KK_loop_correction",
        "n_w": N_W,
        "k_cs": K_CS,
        "lean4_new_file": LEAN4_NEW_FILE,
    }


def proved_components() -> List[str]:
    """Return the eleven proved algebraic kernel components."""
    return PROVED_COMPONENTS


def remaining_gap_assessment() -> Dict[str, Any]:
    """Return the honest remaining-gap assessment."""
    return {
        "loop_kernel_proved": True,
        "full_loop_integral_proved": False,
        "blocking_residual": BLOCKING_RESIDUAL,
        "honest_note": (
            "The algebraic kernel (loop-order bound, winding convergence, braid consistency) "
            "is finite and machine-verified. The full infinite KK-tower Bessel resummation "
            "requires Mathlib extensions for Bessel function series — not yet available."
        ),
    }


def lean4_certificate() -> Dict[str, Any]:
    """Return the Lean4 certificate for Sub-gap P."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "lean4_file": LEAN4_NEW_FILE["path"],
        "new_theorems": LEAN4_NEW_FILE["theorems"],
        "lean4_total_after": LEAN4_THEOREM_COUNT["total"],
        "proved_components": len(PROVED_COMPONENTS),
        "blocking_residual": BLOCKING_RESIDUAL,
    }


def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 618 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "subgap_p_proof_state": subgap_p_proof_state(),
        "proved_components": proved_components(),
        "remaining_gap_assessment": remaining_gap_assessment(),
        "lean4_certificate": lean4_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
