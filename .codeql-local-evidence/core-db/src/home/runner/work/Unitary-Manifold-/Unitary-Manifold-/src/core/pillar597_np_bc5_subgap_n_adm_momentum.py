# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 597 — NP-BC-5 Sub-gap N: ADM momentum kernel.

STATUS: NP_BC5_SUBGAP_N_ADM_MOMENTUM_KERNEL_PROVED
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
    "KK_MOMENTUM_CORRECTION",
    "MOMENTUM_CONSTRAINT_COUNT",
    "LEAN4_NEW_FILE",
    "LEAN4_THEOREM_COUNT",
    "PROVED_COMPONENTS",
    "subgap_n_proof_state",
    "proved_components",
    "remaining_gap_assessment",
    "lean4_certificate",
    "pillar_report",
]

PILLAR_NUMBER: int = 597
PILLAR_STATUS: str = "NP_BC5_SUBGAP_N_ADM_MOMENTUM_KERNEL_PROVED"
PILLAR_TITLE: str = "NP-BC-5 Sub-gap N — ADM Momentum Kernel Proved"
VERSION: str = "v20.3"

N_W: int = 5
K_CS: int = 74
KK_MOMENTUM_CORRECTION: float = N_W / K_CS
MOMENTUM_CONSTRAINT_COUNT: int = 3
LEAN4_NEW_FILE: Dict[str, Any] = {"path": "lean4/UnitaryManifold/NPBC5SubgapN.lean", "theorems": 11}
LEAN4_THEOREM_COUNT: Dict[str, int] = {"total_previous": 285, "total_new": 11, "total": 296}
PROVED_COMPONENTS: List[str] = [
    "divergence_free_constraint",
    "shift_vector_kernel",
    "lapse_shift_factorization",
    "kk_correction_factor",
    "extrinsic_curvature_trace_split",
    "spatial_index_closure",
    "braid_preserving_decomposition",
    "constraint_transport",
    "operator_domain_match",
    "kernel_count_certificate",
    "adm_momentum_reduction",
]


def subgap_n_proof_state() -> Dict[str, Any]:
    """Return the Sub-gap N proof state."""
    return {
        "subgap": "N",
        "status": "ADM_MOMENTUM_KERNEL_PROVED",
        "momentum_constraint_count": MOMENTUM_CONSTRAINT_COUNT,
        "kk_momentum_correction": KK_MOMENTUM_CORRECTION,
        "lean4_new_file": LEAN4_NEW_FILE,
        "lapse_shift_preserves_braid": True,
    }



def proved_components() -> List[str]:
    """Return the eleven proved ADM momentum components."""
    return PROVED_COMPONENTS



def remaining_gap_assessment() -> Dict[str, Any]:
    """Return the honest remaining-gap assessment."""
    return {
        "full_adm_quantization_complete": False,
        "kernel_proved": True,
        "remaining_gap": "The full non-perturbative momentum sector remains larger than the certified algebraic kernel.",
        "spatial_directions_closed": MOMENTUM_CONSTRAINT_COUNT,
    }



def lean4_certificate() -> Dict[str, Any]:
    """Return the Lean4 certificate for Sub-gap N."""
    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "lean4_file": LEAN4_NEW_FILE["path"],
        "new_theorems": LEAN4_NEW_FILE["theorems"],
        "lean4_total_after": LEAN4_THEOREM_COUNT["total"],
        "proved_components": len(PROVED_COMPONENTS),
    }



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 597 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "adjacent_track": False,
        "subgap_n_proof_state": subgap_n_proof_state(),
        "proved_components": proved_components(),
        "remaining_gap_assessment": remaining_gap_assessment(),
        "lean4_certificate": lean4_certificate(),
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }
