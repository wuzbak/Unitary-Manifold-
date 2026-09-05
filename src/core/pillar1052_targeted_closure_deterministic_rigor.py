# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1052 — targeted closure with deterministic formal routing."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List

from src.core.pillar1044_su3_functional_bridge_alignment import (
    HIGH_LEVEL_REMAINING_BURDEN,
    su3_functional_bridge_alignment,
)
from src.core.pillar1049_sprint_ca_full_throttle_execution import DECISION_GATES, OPEN_LANES
from src.core.pillar1051_merge_gate_baseline_lock import merge_gate_baseline_lock

PILLAR_NUMBER: int = 1052
PILLAR_GATE: str = "TARGETED_CLOSURE_DETERMINISTIC_RIGOR"
PILLAR_STATUS: str = "TARGETED_CLOSURE_DETERMINISTIC_RIGOR_COMPLETE"
VERSION: str = "v35.8"
SPRINT_NAME: str = "CB"
NEXT_PILLAR_SLOT: int = 1058

LEAN4_FILE: str = "lean4/UnitaryManifold/SprintCBDeterministicClosure.lean"
LEAN4_THEOREM_COUNT: int = 12
LEAN4_START: int = 3988
LEAN4_END: int = 4000
LEAN4_DELTA: int = LEAN4_END - LEAN4_START

_ROOT = Path(__file__).resolve().parents[2]

SEMANTIC_MARKERS: List[str] = [
    "DeterministicClosureRule",
    "NoLabelInflation",
    "OpenLaneCarryForwardExplicit",
    "BoundaryTighteningDeterministic",
    "KawamuraIndependenceResidualOpen",
]


def _count_kernels(text: str) -> int:
    return len(re.findall(r"^\s*theorem\s+cb_closure_kernel_\d+\b", text, flags=re.MULTILINE))


def _go_no_go(runtime_flip_earned: bool, boundary_tightened: bool) -> str:
    if runtime_flip_earned:
        return "CLOSURE_EARNED"
    if boundary_tightened:
        return "BOUNDARY_TIGHTENED"
    return "CARRY_FORWARD_OPEN"


def _open_substeps_after_cb() -> List[str]:
    return [
        "Full referee-grade Kawamura-independence functional analysis closure proof",
    ]


def targeted_closure_deterministic_rigor() -> Dict[str, Any]:
    merge_gate = merge_gate_baseline_lock()
    prior = su3_functional_bridge_alignment()
    lean4_path = _ROOT / LEAN4_FILE
    lean4_text = lean4_path.read_text(encoding="utf-8") if lean4_path.exists() else ""
    theorem_count = _count_kernels(lean4_text)
    marker_hits = {marker: marker in lean4_text for marker in SEMANTIC_MARKERS}

    prior_after = list(prior["substep_map"]["after"])
    after_cb = list(prior_after)

    closure_attempts = {
        "formal_projection_continuity": _go_no_go(runtime_flip_earned=False, boundary_tightened=False),
        "kawamura_independence_final_step": _go_no_go(runtime_flip_earned=False, boundary_tightened=False),
        "label_honesty_guardrail": _go_no_go(runtime_flip_earned=False, boundary_tightened=False),
    }

    deterministic_gate_coverage = all(g in DECISION_GATES for g in closure_attempts.values())
    remaining_burden = "Full referee-grade Kawamura-independence functional analysis closure proof"

    valid = bool(
        merge_gate["valid"]
        and prior["valid"]
        and lean4_path.exists()
        and theorem_count == LEAN4_THEOREM_COUNT
        and all(marker_hits.values())
        and deterministic_gate_coverage
        and HIGH_LEVEL_REMAINING_BURDEN in prior["remaining_burdens"]
        and after_cb == prior_after
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT_NAME,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "open_lanes": list(OPEN_LANES),
        "decision_gates": list(DECISION_GATES),
        "closure_attempts": closure_attempts,
        "deterministic_gate_coverage": deterministic_gate_coverage,
        "packet_valid": valid,
        "scientific_progress": False,
        "physical_theorem_proved": False,
        "boundary_tightened": False,
        "remaining_burden": remaining_burden,
        "historical_proposed_open_substeps": _open_substeps_after_cb(),
        "merge_gate_dependency": merge_gate,
        "prior_formal_alignment": prior,
        "lean4": {
            "file": LEAN4_FILE,
            "exists": lean4_path.exists(),
            "theorem_count": theorem_count,
            "expected_theorem_count": LEAN4_THEOREM_COUNT,
            "semantic_markers": marker_hits,
            "lean4_start": LEAN4_START,
            "lean4_end": LEAN4_END,
            "lean4_delta": LEAN4_DELTA,
            "evidence_kind": "SOURCE_TEXT_INVENTORY_ONLY",
            "compilation_verified": False,
            "physical_theorem_count_verified": 0,
        },
        "formal_open_substeps": {
            "before": prior_after,
            "after": after_cb,
            "before_count": len(prior_after),
            "after_count": len(after_cb),
        },
        "non_claims": [
            "No hardgate claim promotion is made in this formal closure increment.",
            "Full Kawamura-independence closure remains open until the final functional-analysis step is proved.",
        ],
        "valid": valid,
    }


def _safe_pillar_valid() -> bool:
    try:
        return bool(targeted_closure_deterministic_rigor()["valid"])
    except Exception:
        return False


PILLAR_VALID: bool = _safe_pillar_valid()


def pillar1052_summary() -> Dict[str, Any]:
    report = targeted_closure_deterministic_rigor()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "Targeted Closure Deterministic Rigor",
        "status": PILLAR_STATUS,
        "valid": report["valid"],
        "after_count": report["formal_open_substeps"]["after_count"],
    }
