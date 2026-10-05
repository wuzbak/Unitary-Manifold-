# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 587 — NP-BC-4 Sub-gap K: ADM Inhomogeneous Non-Perturbative Algebraic Kernel.

STATUS: NP_BC4_SUBGAP_K_ADM_INHOMOGENEOUS_KERNEL_PROVED

This pillar records the arithmetic kernel for the ADM inhomogeneous,
non-perturbative residual inside NP-BC-4. It is deliberately modest: only
integer and rational proxies formalizable in Lean 4 are claimed.

What IS proved:
1. ADM momentum proxy uses n_w = 5 as the canonical component count.
2. Hamiltonian constraint numerator proxy is k_CS = 74.
3. KK reduction of the 3-metric has five periodic braid modes.
4. Lapse+shift constraint count proxy is 4 × n_w = 20.
5. Non-perturbative scalar-mode bound proxy is ||δg|| ≤ 5/74.
6. Even Z₂ inhomogeneous modes survive; odd modes are suppressed.
7. KK mass-gap proxy for inhomogeneous modes is 25/74.
8. Dirac-algebra consistency is represented by mod-k_CS structural closure.
9. Braid regularization keeps the NP sector bounded by k_CS.
10. Convergence proxy uses a finite truncation through n = k_CS.
11. Summary theorem: the ADM algebraic kernel is internally consistent.

What is NOT proved:
- The full inhomogeneous non-perturbative ADM quantization.
- A rigorous continuum proof of the Dirac constraint algebra in 5D.
- The full convergence of quantum-gravitational mode sums.
"""
from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "LEAN4_NEW_FILE",
    "LEAN4_THEOREM_COUNT",
    "SUBGAP_K_STATUS",
    "PROVED_COMPONENTS",
    "REMAINING_GAPS",
    "subgap_k_proof_state",
    "proved_components",
    "remaining_gap_assessment",
    "pillar_report",
]

PILLAR_NUMBER: int = 587
PILLAR_STATUS: str = "NP_BC4_SUBGAP_K_ADM_INHOMOGENEOUS_KERNEL_PROVED"
PILLAR_TITLE: str = "NP-BC-4 Sub-gap K: ADM Inhomogeneous Non-Perturbative Algebraic Kernel"
VERSION: str = "v20.1"

_K_CS: int = 74
_N_W: int = 5
_N_2: int = 7
_LAPSE_SHIFT_CONSTRAINTS_PER_POINT: int = 4
_ADM_LAPSE_CONSTRAINT_COUNT: int = 1
_SHIFT_CONSTRAINT_COUNT: int = 3
_NP_SCALAR_BOUND_NUMERATOR: int = 5
_NP_SCALAR_BOUND_DENOMINATOR: int = 74
_KK_MASS_GAP_NUMERATOR: int = 25
_KK_MASS_GAP_DENOMINATOR: int = 74

LEAN4_NEW_FILE: Dict[str, Any] = {
    "path": "lean4/UnitaryManifold/NPBC4SubgapK.lean",
    "theorems": 11,
    "status": "ADM_INHOMOGENEOUS_KERNEL_PROVED",
    "content": (
        "ADM momentum proxy with n_w=5; Hamiltonian numerator k_CS=74; "
        "five KK periodic modes; four lapse/shift constraints per point; "
        "non-perturbative metric bound 5/74; Z₂ even/odd mode split; "
        "KK mass gap 25/74; mod-74 Dirac-algebra proxy; bounded NP sector; "
        "finite truncation through k_CS; summary theorem"
    ),
    "honest_status": (
        "Algebraic ADM inhomogeneous kernel proved. "
        "The full non-perturbative continuum ADM/Wheeler-DeWitt sector remains open — "
        "sub-gap K is PARTIALLY_CLOSED."
    ),
}

LEAN4_THEOREM_COUNT: Dict[str, int] = {
    "total_previous": 251,
    "total_new": 11,
    "total": 262,
    "NPBC4SubgapK.lean": 11,
}

SUBGAP_K_STATUS: Dict[str, Any] = {
    "source": "NP-BC-4 residual — ADM inhomogeneous non-perturbative sector",
    "physical_statement": (
        "The ADM inhomogeneous sector admits a bounded braid-compatible algebraic "
        "kernel with KK mode count n_w = 5 and metric-perturbation proxy bound 5/74."
    ),
    "proof_state": "ADM_INHOMOGENEOUS_KERNEL_PROVED — partial advance",
    "kernel_proved": True,
    "full_closure_achieved": False,
    "advance_statement": (
        "The inhomogeneous ADM residual is reduced to an 11-theorem arithmetic kernel; "
        "the continuum non-perturbative quantization remains unformalized."
    ),
}

PROVED_COMPONENTS: List[Dict[str, str]] = [
    {
        "name": "ADM momentum constraint proxy",
        "theorem": "adm_momentum_constraint_proxy",
        "status": "PROVED",
        "content": "The canonical ADM momentum proxy uses n_w = 5 as the braid-supported component count.",
    },
    {
        "name": "Hamiltonian constraint kernel",
        "theorem": "adm_hamiltonian_constraint_kernel",
        "status": "PROVED",
        "content": "The integer numerator proxy for the ADM Hamiltonian constraint is k_CS = 74.",
    },
    {
        "name": "KK reduction of the 3-metric",
        "theorem": "kk_reduction_periodic_modes",
        "status": "PROVED",
        "content": "The S¹/Z₂ KK reduction uses five periodic braid modes associated with n_w = 5.",
    },
    {
        "name": "Lapse-shift constraint count",
        "theorem": "adm_lapse_shift_constraint_count",
        "status": "PROVED",
        "content": "There are 4 constraints per point, giving the proxy 4 × 5 = 20.",
    },
    {
        "name": "Non-perturbative scalar bound",
        "theorem": "adm_scalar_mode_bound",
        "status": "PROVED",
        "content": "The braid bound on scalar perturbations is represented by 5/74.",
    },
    {
        "name": "Z₂ parity of inhomogeneous modes",
        "theorem": "adm_z2_mode_parity",
        "status": "PROVED",
        "content": "Even inhomogeneous modes survive the orbifold projection; odd modes are suppressed.",
    },
    {
        "name": "KK mass gap for inhomogeneous modes",
        "theorem": "adm_kk_mass_gap",
        "status": "PROVED",
        "content": "The first inhomogeneous KK mass-gap proxy is m² = n_w²/k_CS = 25/74.",
    },
    {
        "name": "ADM constraint algebra proxy",
        "theorem": "adm_constraint_algebra_proxy",
        "status": "PROVED",
        "content": "The Dirac-algebra closure is represented by a mod-k_CS structural proxy with k_CS = 74.",
    },
    {
        "name": "Braid regularization",
        "theorem": "adm_braid_regularization_bound",
        "status": "PROVED",
        "content": "The non-perturbative mode sector is bounded by the braid invariant k_CS = 74.",
    },
    {
        "name": "Convergence proxy",
        "theorem": "adm_np_corrections_finite_truncation",
        "status": "PROVED",
        "content": "The Σ 1/n² convergence proxy is represented by finite truncation at n = k_CS = 74.",
    },
    {
        "name": "Summary theorem",
        "theorem": "np_bc4_subgap_k_adm_kernel",
        "status": "PROVED",
        "content": "All listed ADM inhomogeneous algebraic kernel constraints are simultaneously consistent.",
    },
]

REMAINING_GAPS: List[Dict[str, str]] = [
    {
        "name": "Continuum Dirac algebra in 5D",
        "status": "OPEN",
        "reason": "A genuine field-theoretic proof of the full ADM constraint algebra is outside the arithmetic proxy sector.",
    },
    {
        "name": "Non-perturbative inhomogeneous wavefunctional",
        "status": "OPEN",
        "reason": "The full Wheeler-DeWitt functional on inhomogeneous metrics is not formalized here.",
    },
    {
        "name": "Mode-sum convergence without truncation",
        "status": "OPEN",
        "reason": "The finite-k_CS proxy does not prove the continuum infinite-mode limit.",
    },
]


def subgap_k_proof_state() -> Dict[str, Any]:
    """Return the current proof state for NP-BC-4 Sub-gap K."""
    return {
        "subgap": "K",
        "bc": "NP-BC-4",
        "status": PILLAR_STATUS,
        "kernel_proved": SUBGAP_K_STATUS["kernel_proved"],
        "full_closure": SUBGAP_K_STATUS["full_closure_achieved"],
        "lean4_theorems": LEAN4_NEW_FILE["theorems"],
        "constraint_count_proxy": _LAPSE_SHIFT_CONSTRAINTS_PER_POINT * _N_W,
        "scalar_bound": f"{_NP_SCALAR_BOUND_NUMERATOR}/{_NP_SCALAR_BOUND_DENOMINATOR}",
    }



def proved_components() -> List[Dict[str, str]]:
    """Return the proved algebraic components for Sub-gap K."""
    return PROVED_COMPONENTS



def remaining_gap_assessment() -> List[Dict[str, str]]:
    """Return the remaining open gaps for Sub-gap K."""
    return REMAINING_GAPS



def pillar_report() -> Dict[str, Any]:
    """Return the full Pillar 587 report."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "lean4": LEAN4_NEW_FILE,
        "theorem_count": LEAN4_THEOREM_COUNT,
        "subgap_k_status": SUBGAP_K_STATUS,
        "proved": proved_components(),
        "remaining": remaining_gap_assessment(),
    }
