# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 847 — EIGHTD_WILSON_LINE_RUNG3_PILLAR_CERTIFICATE

Pillar-numbered certificate for the existing Rung 3 (7D → 8D) Wilson-line
gauge-group scaffold.

Honest status
-------------
This pillar does not introduce new physics.  `src/eightd/wilson_line_gauge.py`
already implements and passes the Rung 3 kill-switch (rank conservation,
Wilson-line quantization, unbroken-group validation, AxiomZero seed purity),
reaching RUNG_SOLID status.  This module gives that existing, already-tested
scaffold a pillar identity in the registry, consistent with how Pillar 1014
later audits Wilson-line robustness branches.  No constant, check, or
conclusion in `wilson_line_gauge.py` is modified.
"""
from __future__ import annotations

from typing import Dict

from src.eightd.wilson_line_gauge import (
    DIMENSION,
    EPISTEMIC_STATUS,
    KILL_SWITCH_PASS,
    RUNG_ID,
    STATUS,
    TARGET_RANK,
    kill_switch_check,
    rung3_gate_evidence,
)

PILLAR_NUMBER: int = 847
PILLAR_GATE: str = "EIGHTD_WILSON_LINE_RUNG3_PILLAR_CERTIFICATE"
PILLAR_TITLE: str = "8D Wilson-Line Gauge Scaffold (Rung 3) Pillar Certificate"
ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"

LEAN4_THEOREM_COUNT: int = 0
LEAN4_TOTAL_AFTER: int = 1996  # unchanged: this pillar adds no Lean4 theorems


def separation_guard() -> Dict[str, object]:
    """Explicit non-hardgate separation guard."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "is_hardgate": False,
        "modifies_hardgate_module": False,
        "wraps_existing_scaffold_only": True,
    }


def eightd_wilson_line_pillar_certificate() -> Dict[str, object]:
    """Return the Pillar 847 certificate wrapping the Rung 3 scaffold."""
    ks = kill_switch_check()
    evidence = rung3_gate_evidence()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "title": PILLAR_TITLE,
        "rung_id": RUNG_ID,
        "dimension": DIMENSION,
        "target_rank": TARGET_RANK,
        "status": STATUS,
        "epistemic_status": EPISTEMIC_STATUS,
        "kill_switch_pass": KILL_SWITCH_PASS,
        "kill_switch_detail": ks,
        "gate_evidence": evidence,
        "acceptance_gate_passed": bool(KILL_SWITCH_PASS),
        "source_module": "src/eightd/wilson_line_gauge.py",
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
        "separation_guard": separation_guard(),
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_TITLE",
    "ADJACENCY_TRACK_LABEL",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "separation_guard",
    "eightd_wilson_line_pillar_certificate",
]
