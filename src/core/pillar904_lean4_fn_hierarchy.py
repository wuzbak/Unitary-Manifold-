# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 904 — LEAN4_FN_HIERARCHY_THEOREMS.

This bridge counts the FN hierarchy theorem proxies for Sprint BC.  The file is
an inventory certificate for the Lean4 placeholder layer, not a claim that the
kernel has proved flavour phenomenology.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

PILLAR_NUMBER: int = 904
PILLAR_GATE: str = "LEAN4_FN_HIERARCHY_THEOREMS"
LEAN4_FILE: str = "FNHierarchyTheorems.lean"
LEAN4_NAMESPACE: str = "UnitaryManifold.FNHierarchy"
EXPECTED_MASTER_THEOREM: str = "theorem fnhierarchy_complete : hierarchyComplete = true := rfl"
LEAN4_THEOREM_COUNT: int = 60
LEAN4_TOTAL_BEFORE: int = 3041
LEAN4_TOTAL_AFTER: int = 3101
LEAN4_FN_THEOREMS: int = 60
STATUS_LABEL: str = "PARTIAL"

_LEAN4_PATH = Path(__file__).resolve().parents[2] / "lean4" / "UnitaryManifold" / LEAN4_FILE

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_FILE",
    "LEAN4_NAMESPACE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "LEAN4_FN_THEOREMS",
    "STATUS_LABEL",
    "lean4_fn_hierarchy_summary",
]


def _lean4_text() -> str:
    return _LEAN4_PATH.read_text(encoding="utf-8") if _LEAN4_PATH.exists() else ""


N_THEOREMS: int = len(re.findall(r"^\s*theorem\s+[A-Za-z0-9_']+", _lean4_text(), flags=re.MULTILINE))
THEOREM_COUNT_MATCHES: bool = N_THEOREMS == LEAN4_THEOREM_COUNT


def lean4_fn_hierarchy_summary() -> dict[str, Any]:
    text = _lean4_text()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "lean4_file": LEAN4_FILE,
        "namespace_present": f"namespace {LEAN4_NAMESPACE}" in text,
        "master_theorem_present": EXPECTED_MASTER_THEOREM in text,
        "n_theorems": N_THEOREMS,
        "theorem_count_matches": THEOREM_COUNT_MATCHES,
        "lean4_fn_theorems": LEAN4_FN_THEOREMS,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
        "epistemic_status": (
            "The Lean4 FN hierarchy layer is counted and registered.  Theorems are proxy placeholders, not a kernel-backed phenomenology proof."
        ),
    }
