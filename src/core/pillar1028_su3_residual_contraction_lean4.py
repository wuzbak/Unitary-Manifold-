# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1028 — Sprint BV SU(3) residual contraction with Lean4-backed kernels."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar636_su3_orbifold_equivalence import residual_open
from src.core.pillar1022_su3_orbifold_lean4_kernel import pillar1022_summary

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "LEAN4_FILE",
    "LEAN4_THEOREM_COUNT",
    "su3_residual_contraction_report",
    "pillar1028_summary",
]

PILLAR_NUMBER: int = 1028
PILLAR_GATE: str = "SU3_RESIDUAL_CONTRACTION_LEAN4"
PILLAR_STATUS: str = "SU3_RESIDUAL_CONTRACTION_LEAN4_COMPLETE"
LEAN4_FILE: str = "lean4/UnitaryManifold/SU3ResidualContractionBV.lean"
LEAN4_THEOREM_COUNT: int = 16

_ROOT = Path(__file__).resolve().parents[2]


def _open_steps_before() -> List[str]:
    return [
        "Hilbert-space operator-domain equivalence for Z2 parity projectors",
        "Continuity/closure proof for projected SM gauge subspace",
        "Full functional-analysis bridge proving referee-grade Kawamura independence",
    ]


def _open_steps_after() -> List[str]:
    return [
        "Continuity/closure proof for projected SM gauge subspace",
        "Full functional-analysis bridge proving referee-grade Kawamura independence",
    ]


def su3_residual_contraction_report() -> Dict[str, Any]:
    """Return Sprint BV formal residual contraction status for the SU(3) lane."""
    p636 = residual_open()
    p1022 = pillar1022_summary()
    lean4_path = _ROOT / LEAN4_FILE
    before = _open_steps_before() + [p636["open_item"]]
    after = list(before)

    reduction_earned = False

    valid = bool(
        lean4_path.exists()
        and p1022["valid"]
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "packet_valid": valid,
        "scientific_progress": False,
        "physical_theorem_proved": False,
        "dependency": {
            "pillar636_open_item": p636["open_item"],
            "pillar1022_status": p1022["status"],
            "pillar1022_valid": p1022["valid"],
        },
        "lean4_kernel": {
            "file": LEAN4_FILE,
            "exists": lean4_path.exists(),
            "theorem_count": LEAN4_THEOREM_COUNT,
            "evidence_kind": "DECLARED_SOURCE_INVENTORY_ONLY",
            "compilation_verified": False,
        },
        "residual_map": {
            "open_steps_before": before,
            "open_steps_after": after,
            "before_count": len(before),
            "after_count": len(after),
            "formal_reduction_earned": reduction_earned,
            "historical_proposed_after": _open_steps_after(),
        },
        "explicit_non_claims": [
            "Full Hilbert-space closure remains open",
            "No hardgate promotion is claimed",
        ],
        "interpretation": (
            "The residual domain is retained unchanged. Source inventory and assigned "
            "blocker deletions do not establish functional or internal-lift proofs."
        ),
    }


_REPORT = su3_residual_contraction_report()
PILLAR_VALID: bool = bool(_REPORT["valid"])


def pillar1028_summary() -> Dict[str, Any]:
    """Return concise Pillar 1028 summary."""
    report = su3_residual_contraction_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "SU(3) Residual Contraction Lean4",
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "lean4_theorem_count": report["lean4_kernel"]["theorem_count"],
        "before_count": report["residual_map"]["before_count"],
        "after_count": report["residual_map"]["after_count"],
    }
