# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 619 — NP-BC-6 Sub-gap Q: holographic screen entropy algebraic kernel.

STATUS: NP_BC6_SUBGAP_Q_HOLOGRAPHIC_SCREEN_KERNEL_PROVED
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
    "SUBGAP_Q_STATUS",
    "PROVED_COMPONENTS",
    "BLOCKING_RESIDUAL",
    "subgap_q_proof_state",
    "proved_components",
    "remaining_gap_assessment",
    "lean4_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 619
PILLAR_STATUS: str = "NP_BC6_SUBGAP_Q_HOLOGRAPHIC_SCREEN_KERNEL_PROVED"
PILLAR_TITLE: str = "NP-BC-6 Sub-gap Q — Holographic Screen Entropy Algebraic Kernel Proved"
VERSION: str = "v20.7"

N_W: int = 5
K_CS: int = 74
K_CS_HALF: int = 37

LEAN4_NEW_FILE: Dict[str, Any] = {
    "path": "lean4/UnitaryManifold/NPBC6SubgapQ.lean",
    "theorems": 11,
}
LEAN4_THEOREM_COUNT: Dict[str, int] = {
    "total_previous": 319,
    "total_new": 11,
    "total": 330,
}
SUBGAP_Q_STATUS: str = "HOLOGRAPHIC_SCREEN_KERNEL_PROVED"
PROVED_COMPONENTS: List[str] = [
    "holographic_bound_proxy",
    "screen_area_proxy",
    "entropy_floor_half_cs",
    "screen_dimension_bound",
    "cs_level_parity_bosonic",
    "braid_screen_link",
    "entropy_monotone_proxy",
    "winding_screen_capacity",
    "half_level_entropy",
    "screen_entropy_balance",
    "np_bc6_subgap_q_holographic_kernel",
]
BLOCKING_RESIDUAL: str = (
    "Full Ryu-Takayanagi formula in the 5D KK bulk and Bousso covariant entropy "
    "bound in the curved RS1 background — requires full 5D quantum gravity."
)


def subgap_q_proof_state() -> Dict[str, Any]:
    """Return the Sub-gap Q proof state."""
    return {
        "subgap": "Q",
        "status": SUBGAP_Q_STATUS,
        "np_bc_chain": 6,
        "kernel_type": "holographic_screen_entropy",
        "n_w": N_W,
        "k_cs": K_CS,
        "k_cs_half": K_CS_HALF,
        "winding_screen_capacity": N_W * K_CS,
        "lean4_new_file": LEAN4_NEW_FILE,
    }


def proved_components() -> List[str]:
    """Return the eleven proved algebraic kernel components."""
    return PROVED_COMPONENTS


def remaining_gap_assessment() -> Dict[str, Any]:
    """Return the honest remaining-gap assessment."""
    return {
        "screen_kernel_proved": True,
        "full_rt_formula_proved": False,
        "blocking_residual": BLOCKING_RESIDUAL,
        "honest_note": (
            "The holographic screen capacity (k_CS × n_w = 370), entropy floor (k_CS/2 = 37), "
            "and bosonic parity are machine-verified. The full Ryu-Takayanagi computation "
            "in the warped RS1 background requires non-perturbative 5D quantum gravity "
            "well beyond current Mathlib scope."
        ),
    }


def lean4_certificate() -> Dict[str, Any]:
    """Return the Lean4 certificate for Sub-gap Q."""
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
    """Return the full Pillar 619 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "subgap_q_proof_state": subgap_q_proof_state(),
        "proved_components": proved_components(),
        "remaining_gap_assessment": remaining_gap_assessment(),
        "lean4_certificate": lean4_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
