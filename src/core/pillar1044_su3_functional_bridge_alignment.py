# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1044 — Sprint BY SU(3) functional-bridge alignment."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar1035_sprint_bx_formal_residual_tightening import sprint_bx_formal_residual_tightening

PILLAR_NUMBER: int = 1044
PILLAR_GATE: str = "SU3_FUNCTIONAL_BRIDGE_ALIGNMENT"
PILLAR_STATUS: str = "SU3_FUNCTIONAL_BRIDGE_ALIGNMENT_COMPLETE"
LEAN4_FILE: str = "lean4/UnitaryManifold/SprintBYFunctionalBridgeAlignment.lean"
LEAN4_THEOREM_COUNT: int = 12
_ROOT = Path(__file__).resolve().parents[2]
HIGH_LEVEL_REMAINING_BURDEN = "Full functional-analysis bridge proving referee-grade Kawamura independence"
SEMANTIC_MARKERS: List[str] = [
    "ParityProjectorBounded",
    "ParityProjectorRespectsSU3",
    "OrbifoldIntertwinerContinuous",
    "HilbertCompletionSpectralEquivalent",
    "ProjectionContinuityLocked",
    "KawamuraIndependenceOpen",
]


def _open_substeps_before() -> List[str]:
    return [
        "boundedness of the parity-projector completion map",
        "norm-continuous intertwiner across the orbifold quotient completion",
        "spectral equivalence after Hilbert-space domain completion",
    ]


def _open_substeps_after() -> List[str]:
    return [
        "norm-continuous intertwiner across the orbifold quotient completion",
        "spectral equivalence after Hilbert-space domain completion",
    ]


def _count_kernels(text: str) -> int:
    return len(re.findall(r"^\s*theorem\s+by_alignment_\d+\b", text, flags=re.MULTILINE))


def su3_functional_bridge_alignment() -> Dict[str, Any]:
    prior = sprint_bx_formal_residual_tightening()
    lean4_path = _ROOT / LEAN4_FILE
    lean4_text = lean4_path.read_text(encoding="utf-8") if lean4_path.exists() else ""
    theorem_count = _count_kernels(lean4_text)
    before = list(dict.fromkeys(
        prior["residual_map"]["open_steps_after"] + _open_substeps_before()
    ))
    after = list(before)
    remaining_burdens = [HIGH_LEVEL_REMAINING_BURDEN]
    semantic_markers_present = all(marker in lean4_text for marker in SEMANTIC_MARKERS)
    valid = bool(
        prior["valid"]
        and lean4_path.exists()
        and theorem_count == LEAN4_THEOREM_COUNT
        and semantic_markers_present
        and HIGH_LEVEL_REMAINING_BURDEN in prior["residual_map"]["open_steps_after"]
        and HIGH_LEVEL_REMAINING_BURDEN in remaining_burdens
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "packet_valid": valid,
        "scientific_progress": False,
        "physical_theorem_proved": False,
        "dependency": prior,
        "lean4_kernel": {
            "file": LEAN4_FILE,
            "exists": lean4_path.exists(),
            "theorem_count": theorem_count,
            "expected_theorem_count": LEAN4_THEOREM_COUNT,
            "semantic_markers_present": semantic_markers_present,
            "evidence_kind": "SOURCE_TEXT_INVENTORY_ONLY",
            "compilation_verified": False,
        },
        "high_level_remaining_burden": HIGH_LEVEL_REMAINING_BURDEN,
        "remaining_burdens": remaining_burdens,
        "substep_map": {
            "before": before,
            "after": after,
            "before_count": len(before),
            "after_count": len(after),
            "historical_proposed_after": _open_substeps_after(),
        },
        "explicit_non_claims": [
            "Full Hilbert-space closure remains open",
            "No Kawamura-independence completion claim is made",
        ],
        "interpretation": (
            "No functional-analysis or internal-lift burden is discharged by source "
            "text inventory. All inherited and targeted open substeps are retained."
        ),
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(su3_functional_bridge_alignment()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1044_summary() -> Dict[str, Any]:
    report = su3_functional_bridge_alignment()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "SU(3) Functional Bridge Alignment",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "lean4_theorem_count": report["lean4_kernel"]["theorem_count"],
        "after_count": report["substep_map"]["after_count"],
    }
