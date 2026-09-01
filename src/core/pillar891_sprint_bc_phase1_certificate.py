# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 891 — SPRINT_BC_PHASE1_CERTIFICATE.

Phase 1 of Sprint BC collects the FN charge assignment, CKM correction,
Jarlskog update, and PMNS bridge.  The certificate is an honest registry of
what improved and what remained in tension after the FN layer was switched on.
"""
from __future__ import annotations

from typing import Any

from src.sevend.pillar887_fn_charge_assignment import PILLAR_GATE as GATE_887, STATUS_LABEL as STATUS_887
from src.sevend.pillar888_ckm_7d_fn_correction import CKM_7D_FN_GATE, PILLAR_GATE as GATE_888, STATUS_LABEL as STATUS_888
from src.sevend.pillar889_jarlskog_fn import JARLSKOG_GATE, PILLAR_GATE as GATE_889, STATUS_LABEL as STATUS_889
from src.sevend.pillar890_pmns_fn_bridge import PILLAR_GATE as GATE_890, PMNS_FN_GATE, STATUS_LABEL as STATUS_890

PILLAR_NUMBER: int = 891
PILLAR_GATE: str = "SPRINT_BC_PHASE1_CERTIFICATE"
STATUS_LABEL: str = "PARTIAL"
LEAN4_START: int = 2741
LEAN4_PHASE1_END: int = 2851
LEAN4_DELTA: int = LEAN4_PHASE1_END - LEAN4_START

REGISTERED_GATES: list[dict[str, object]] = [
    {"pillar": 887, "gate": GATE_887, "status_label": STATUS_887},
    {"pillar": 888, "gate": GATE_888, "status_label": STATUS_888, "verdict": CKM_7D_FN_GATE},
    {"pillar": 889, "gate": GATE_889, "status_label": STATUS_889, "verdict": JARLSKOG_GATE},
    {"pillar": 890, "gate": GATE_890, "status_label": STATUS_890, "verdict": PMNS_FN_GATE},
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "STATUS_LABEL",
    "PHASE1_VALID",
    "LEAN4_START",
    "LEAN4_PHASE1_END",
    "LEAN4_DELTA",
    "REGISTERED_GATES",
    "phase1_summary",
]


def phase1_summary() -> dict[str, Any]:
    """Return the Sprint BC Phase 1 certificate."""
    resolved = sum(entry["status_label"] == "RESOLVED" for entry in REGISTERED_GATES)
    tensions = sum(entry["status_label"] == "TENSION_PERSISTS" for entry in REGISTERED_GATES)
    partial = sum(entry["status_label"] == "PARTIAL" for entry in REGISTERED_GATES)
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "phase_valid": PHASE1_VALID,
        "lean4_start": LEAN4_START,
        "lean4_end": LEAN4_PHASE1_END,
        "lean4_delta": LEAN4_DELTA,
        "registered_gates": REGISTERED_GATES,
        "counts": {"resolved": resolved, "partial": partial, "tension": tensions},
        "epistemic_status": (
            "Phase 1 is assembled with explicit FN outputs.  One bookkeeping layer is "
            "resolved, while CKM/Jarlskog tension and a partial PMNS bridge remain honestly labelled."
        ),
    }


PHASE1_VALID: bool = (
    LEAN4_DELTA == 110
    and len(REGISTERED_GATES) == 4
    and {entry["pillar"] for entry in REGISTERED_GATES} == {887, 888, 889, 890}
)
