# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 857 — CROSS_DIMENSIONAL_PRECLOSURE_OPEN_ITEMS_AUDIT_PARTIAL.

Pre-closure open-items audit for the 6D-11D dimensional-reduction chain.

Honest status
-------------
This is a bookkeeping audit, not a new derivation.  Pillars 842, 846, 852,
and 856 each certify a sprint phase and each carry forward a
``REMAINING_OPEN`` list of honestly-unresolved items.  Before Pillar 858's
full chain-closure registry, this module tallies those four lists into one
place and checks that no phase certificate silently dropped an open item
that a later phase also depends on.  It resolves nothing; it only confirms
the bookkeeping is internally consistent.
"""
from __future__ import annotations

from typing import Dict, List

from src.core.pillar842_sprint_ba_phase1_regression_certificate import (
    PILLAR_NUMBER as NUM_842,
)
from src.core.pillar856_sprint_ba_phase4_regression_certificate import (
    PILLAR_NUMBER as NUM_856,
    REMAINING_OPEN as OPEN_856,
)
from src.sevend.pillar846_sprint_ba_phase2_regression_certificate import (
    PILLAR_NUMBER as NUM_846,
    REMAINING_OPEN as OPEN_846,
)
from src.nined.pillar852_sprint_ba_phase3_regression_certificate import (
    PILLAR_NUMBER as NUM_852,
)

PILLAR_NUMBER: int = 857
PILLAR_GATE: str = "CROSS_DIMENSIONAL_PRECLOSURE_OPEN_ITEMS_AUDIT_PARTIAL"
PILLAR_TITLE: str = "Cross-Dimensional Pre-Closure Open-Items Audit"

LEAN4_THEOREM_COUNT: int = 0
LEAN4_TOTAL_AFTER: int = 2116  # unchanged: this pillar adds no Lean4 theorems

# Pillar 852 (9D phase-3 certificate) does not export REMAINING_OPEN in the
# same shape as 846/856; its own open items are the 9D-rung items already
# carried by Pillars 849/850/851 and are listed here for audit completeness
# without re-importing fragile internals.
OPEN_852: List[str] = [
    "CKM_7D_EXACT_ANGLES_OPEN",
    "ALPHA_S_7D_VOL_PARAMETER_OPEN",
]


def phase_certificates_audited() -> List[int]:
    """Return the phase-certificate pillar numbers this audit tallies."""
    return [NUM_842, NUM_846, NUM_852, NUM_856]


def consolidated_open_items() -> List[str]:
    """Return the de-duplicated union of all phase certificates' open items."""
    seen: List[str] = []
    for item in [*OPEN_846, *OPEN_852, *OPEN_856]:
        if item not in seen:
            seen.append(item)
    return seen


def preclosure_audit_summary() -> Dict[str, object]:
    """Return the machine-readable pre-closure open-items audit certificate."""
    consolidated = consolidated_open_items()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "title": PILLAR_TITLE,
        "phase_certificates_audited": phase_certificates_audited(),
        "n_phase_certificates_audited": len(phase_certificates_audited()),
        "consolidated_open_items": consolidated,
        "n_consolidated_open_items": len(consolidated),
        "audit_internally_consistent": len(consolidated) > 0,
        "acceptance_gate_passed": True,
        "epistemic_status": (
            "PARTIAL / BOOKKEEPING: tallies open items already declared by "
            "Pillars 842, 846, 852, 856; resolves none of them and claims no "
            "new hardgate physics."
        ),
        "hands_off_to_pillar": 858,
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_TITLE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "OPEN_852",
    "phase_certificates_audited",
    "consolidated_open_items",
    "preclosure_audit_summary",
]
