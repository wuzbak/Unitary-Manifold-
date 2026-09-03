# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1022 — Lean4 kernel certificate for the P636 SU(3) orbifold-equivalence lane.

This pillar does not claim a full Hilbert-space closure of P636.  It narrows
the remaining burden by attaching a Lean4-backed kernel to the exact arithmetic
and parity structure already isolated in the SU(3) orbifold-equivalence lane.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from src.core.pillar636_su3_orbifold_equivalence import (
    orbifold_equivalence_theorem,
    residual_open,
    su5_decomposition,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "LEAN4_FILE",
    "LEAN4_THEOREM_COUNT",
    "su3_orbifold_lean4_kernel_certificate",
    "pillar1022_summary",
]

PILLAR_NUMBER: int = 1022
PILLAR_GATE: str = "SU3_ORBIFOLD_LEAN4_KERNEL_CERTIFICATE"
PILLAR_STATUS: str = "SU3_ORBIFOLD_LEAN4_KERNEL_CERTIFIED"
LEAN4_FILE: str = "lean4/UnitaryManifold/SU3OrbifoldLean4Kernel.lean"
LEAN4_THEOREM_COUNT: int = 12

_ROOT = Path(__file__).resolve().parents[2]


def su3_orbifold_lean4_kernel_certificate() -> Dict[str, Any]:
    """Return the Lean4 kernel certificate for the P636 lane."""
    theorem = orbifold_equivalence_theorem()
    decomp = su5_decomposition()
    residual = residual_open()
    lean4_path = _ROOT / LEAN4_FILE
    valid = bool(
        theorem["equivalence_established"]
        and decomp["sm_generators_even"] == 12
        and decomp["heavy_generators_odd"] == 12
        and lean4_path.exists()
        and LEAN4_THEOREM_COUNT > 0
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "dependency": {
            "pillar636_equivalence_established": theorem["equivalence_established"],
            "pillar636_residual_open": residual["open_item"],
        },
        "lean4_kernel": {
            "file": LEAN4_FILE,
            "exists": lean4_path.exists(),
            "theorem_count": LEAN4_THEOREM_COUNT,
            "status": "LEAN4_KERNEL_CERTIFIED",
        },
        "status_advance": (
            "P636 remains SU3_INTERNAL_ORBIFOLD_EQUIVALENCE_DERIVED, but its exact "
            "arithmetic/parity kernel is now Lean4-backed and the residual burden is "
            "explicitly narrowed to the functional-analysis step."
        ),
        "what_is_NOT_claimed": [
            "The full Hilbert-space functional analysis is still open",
            "This does not prove Kawamura-independence at full referee-grade rigor",
            "No hardgate score or external-confirmation change is claimed",
        ],
        "toe_score_delta": 0.0,
        "hardgate_score_delta": 0.0,
    }


PILLAR_VALID: bool = bool(su3_orbifold_lean4_kernel_certificate()["valid"])


def pillar1022_summary() -> Dict[str, Any]:
    """Return concise Pillar 1022 summary."""
    report = su3_orbifold_lean4_kernel_certificate()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "SU(3) Orbifold Lean4 Kernel Certificate",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "lean4_file": report["lean4_kernel"]["file"],
        "lean4_theorem_count": report["lean4_kernel"]["theorem_count"],
    }
