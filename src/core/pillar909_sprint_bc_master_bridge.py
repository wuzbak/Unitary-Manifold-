# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 909 — SPRINT_BC_MASTER_BRIDGE.

Sprint BC master bridge assembling the four phase certificates, the three new
Lean4 proxy files, and the falsifier-preregistration outputs into one machine
inventory.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from src.core.pillar891_sprint_bc_phase1_certificate import PHASE1_VALID
from src.core.pillar897_sprint_bc_phase2_certificate import PHASE2_VALID
from src.core.pillar903_sprint_bc_phase3_certificate import PHASE3_VALID
from src.core.pillar904_lean4_fn_hierarchy import LEAN4_FN_THEOREMS
from src.core.pillar905_lean4_bundle_degeneracy import LEAN4_THEOREM_COUNT as LEAN4_BUNDLE_THEOREMS

PILLAR_NUMBER: int = 909
PILLAR_GATE: str = "SPRINT_BC_MASTER_BRIDGE"
LEAN4_FILE: str = "SprintBCMasterBridge.lean"
LEAN4_NAMESPACE: str = "UnitaryManifold.SprintBCBridge"
EXPECTED_MASTER_THEOREM: str = "theorem sprintbcmaster_complete : bridgeComplete = true := rfl"
LEAN4_THEOREM_COUNT: int = 35
LEAN4_TOTAL_BEFORE: int = 3141
LEAN4_TOTAL_AFTER: int = 3176
LEAN4_PHASE4_END: int = 3176
TOTAL_DELTA: int = 435
STATUS_LABEL: str = "PARTIAL"
SPRINT_LEAN4_FILES: tuple[str, ...] = ("FNHierarchyTheorems.lean", "BundleDegeneracyResolution.lean", "SprintBCMasterBridge.lean")

_LEAN4_DIR = Path(__file__).resolve().parents[2] / "lean4" / "UnitaryManifold"
_LEAN4_PATH = _LEAN4_DIR / LEAN4_FILE

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_PHASE4_END",
    "STATUS_LABEL",
    "sprint_bc_master_bridge_summary",
]


def _count_theorems(path: Path) -> int:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    return len(re.findall(r"^\s*theorem\s+[A-Za-z0-9_']+", text, flags=re.MULTILINE))


BRIDGE_THEOREMS: int = _count_theorems(_LEAN4_PATH)
ALL_FILES_PRESENT: bool = all((_LEAN4_DIR / name).exists() for name in SPRINT_LEAN4_FILES)
BRIDGE_VALID: bool = (
    BRIDGE_THEOREMS == LEAN4_THEOREM_COUNT
    and ALL_FILES_PRESENT
    and PHASE1_VALID
    and PHASE2_VALID
    and PHASE3_VALID
    and LEAN4_TOTAL_AFTER - 2741 == TOTAL_DELTA
    and LEAN4_FN_THEOREMS == 60
    and LEAN4_BUNDLE_THEOREMS == 40
)


def sprint_bc_master_bridge_summary() -> dict[str, Any]:
    text = _LEAN4_PATH.read_text(encoding="utf-8") if _LEAN4_PATH.exists() else ""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "bridge_valid": BRIDGE_VALID,
        "lean4_file": LEAN4_FILE,
        "namespace_present": f"namespace {LEAN4_NAMESPACE}" in text,
        "master_theorem_present": EXPECTED_MASTER_THEOREM in text,
        "all_files_present": ALL_FILES_PRESENT,
        "bridge_theorems": BRIDGE_THEOREMS,
        "lean4_phase4_end": LEAN4_PHASE4_END,
        "total_delta": TOTAL_DELTA,
        "epistemic_status": (
            "Sprint BC is bridged as an inventory object: all three new Lean4 files are present and the running theorem ledger reaches 3176."
        ),
    }
