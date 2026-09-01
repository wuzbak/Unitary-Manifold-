# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 903 — SPRINT_BC_PHASE3_CERTIFICATE.

Phase 3 gathers the quark, lepton, neutrino-ordering, unified Yukawa, and chain
certificate outputs into one Lean4-ledger checkpoint.
"""
from __future__ import annotations

from typing import Any

from src.sevend.pillar898_quark_mass_ratios_fn import STATUS_LABEL as STATUS_898
from src.sevend.pillar899_lepton_mass_ratios_fn import STATUS_LABEL as STATUS_899
from src.sevend.pillar900_neutrino_mass_ordering import STATUS_LABEL as STATUS_900
from src.sevend.pillar901_yukawa_svd_fn_unified import STATUS_LABEL as STATUS_901
from src.sevend.pillar902_fermion_mass_chain_certificate import STATUS_LABEL as STATUS_902

PILLAR_NUMBER: int = 903
PILLAR_GATE: str = "SPRINT_BC_PHASE3_CERTIFICATE"
STATUS_LABEL: str = "PARTIAL"
LEAN4_PHASE2_END: int = 2941
LEAN4_PHASE3_END: int = 3041
LEAN4_DELTA: int = LEAN4_PHASE3_END - LEAN4_PHASE2_END

REGISTERED_STATUSES: dict[int, str] = {
    898: STATUS_898,
    899: STATUS_899,
    900: STATUS_900,
    901: STATUS_901,
    902: STATUS_902,
}
PHASE3_VALID: bool = LEAN4_DELTA == 100 and len(REGISTERED_STATUSES) == 5

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "STATUS_LABEL",
    "LEAN4_PHASE3_END",
    "LEAN4_DELTA",
    "PHASE3_VALID",
    "phase3_summary",
]


def phase3_summary() -> dict[str, Any]:
    """Return the Sprint BC Phase 3 certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "phase_valid": PHASE3_VALID,
        "lean4_start": LEAN4_PHASE2_END,
        "lean4_end": LEAN4_PHASE3_END,
        "lean4_delta": LEAN4_DELTA,
        "registered_statuses": REGISTERED_STATUSES,
        "epistemic_status": (
            "Phase 3 closes the neutrino-ordering proxy and unified-ledger bookkeeping, while charged-fermion mass ratios remain explicit tensions."
        ),
    }
