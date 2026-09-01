# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 839 — APS_T2Z2_NGEN_LEAN4_BRIDGE

Lean4 proxy bridge for the conditional 6D APS index chain

    T²/Z₂ fixed points
        → APS index = c₁
        → c₁ = 3
        → N_gen = 3.

This pillar is about the formal bridge file itself.  The proof content is proxy
arithmetic in Lean4, not a full Mathlib Dirac-operator formalisation.
"""
from __future__ import annotations

from pathlib import Path
import re

from src.core.pillar837_6d_t2z2_dirac_spectrum import (
    CHERN_NUMBER_C1,
    FIXED_POINT_COUNT,
    N_GEN_DERIVED,
    PILLAR_GATE as P837_GATE,
    dirac_spectrum_t2z2_summary,
)

PILLAR_NUMBER: int = 839
PILLAR_GATE: str = "APS_T2Z2_NGEN_LEAN4_BRIDGE"
LEAN4_FILE: str = "APS_T2Z2_NgenBridge.lean"
LEAN4_THEOREM_COUNT: int = 35
LEAN4_TOTAL_BEFORE: int = 1876
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_FILE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "lean4_bridge_metadata",
    "aps_t2z2_ngen_bridge_summary",
]


def _lean4_path() -> Path:
    return Path(__file__).resolve().parents[2] / "lean4" / "UnitaryManifold" / LEAN4_FILE


def lean4_bridge_metadata() -> dict[str, object]:
    """Inspect the Lean4 proxy file for presence, theorem count, and sorry-freedom."""
    lean_path = _lean4_path()
    if not lean_path.exists():
        return {
            "lean4_path": str(lean_path),
            "exists": False,
            "theorem_count": 0,
            "contains_sorry": False,
            "native_decide_count": 0,
        }
    text = lean_path.read_text(encoding="utf-8")
    theorem_count = len(re.findall(r"^theorem\s+", text, flags=re.MULTILINE))
    return {
        "lean4_path": str(lean_path),
        "exists": True,
        "theorem_count": theorem_count,
        "contains_sorry": "sorry" in text,
        "native_decide_count": len(re.findall(r"native_decide", text)),
    }


def aps_t2z2_ngen_bridge_summary() -> dict[str, object]:
    """Return the summary of the Lean4 bridge and its conditional derivation chain."""
    metadata = lean4_bridge_metadata()
    p837 = dirac_spectrum_t2z2_summary()
    valid = (
        metadata["exists"]
        and metadata["theorem_count"] == LEAN4_THEOREM_COUNT
        and metadata["contains_sorry"] is False
        and FIXED_POINT_COUNT == 4
        and CHERN_NUMBER_C1 == 3
        and N_GEN_DERIVED == 3
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "lean4_file": LEAN4_FILE,
        "lean4_metadata": metadata,
        "bridge_valid": valid,
        "supporting_gate": P837_GATE,
        "fixed_point_count": FIXED_POINT_COUNT,
        "chern_number_c1": CHERN_NUMBER_C1,
        "n_gen_derived": N_GEN_DERIVED,
        "honest_status": (
            "This is a Lean4 proxy bridge: arithmetic/topological proxy theorems "
            "formalise the conditional chain, but not the full analytic APS theorem."
        ),
        "source_summary": p837,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


PILLAR: int = PILLAR_NUMBER
GATE: str = PILLAR_GATE
LEAN4_COUNT: int = LEAN4_THEOREM_COUNT
LEAN4_TOTAL: int = LEAN4_TOTAL_AFTER
LEAN4_PRIOR: int = LEAN4_TOTAL_BEFORE
