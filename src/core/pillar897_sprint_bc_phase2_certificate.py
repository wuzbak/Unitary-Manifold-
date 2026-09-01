# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 897 — SPRINT_BC_PHASE2_CERTIFICATE.

Phase 2 bundles the third-filter degeneracy audits, α_s volume pinning, the TCC
NLO check, and the beyond-EFT CMB survey into a single certificate.  Negative
results remain visible rather than being absorbed into the registry.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar895_tcc_efold_nlo import STATUS_LABEL as STATUS_895, TCC_GATE
from src.core.pillar896_cmb_amplitude_beyond_eft import CMB_BEYOND_EFT_GATE, STATUS_LABEL as STATUS_896
from src.nined.pillar894_alpha_s_vol_pinning import ALPHA_S_PINNING_GATE, STATUS_LABEL as STATUS_894
from src.sixd.pillar892_ngen_bundle_third_filter import NGEN_BUNDLE_GATE, STATUS_LABEL as STATUS_892
from src.sixd.pillar893_e8_breaking_third_filter import E8_GATE, STATUS_LABEL as STATUS_893

PILLAR_NUMBER: int = 897
PILLAR_GATE: str = "SPRINT_BC_PHASE2_CERTIFICATE"
STATUS_LABEL: str = "PARTIAL"
LEAN4_PHASE1_END: int = 2851
LEAN4_PHASE2_END: int = 2941
LEAN4_DELTA: int = LEAN4_PHASE2_END - LEAN4_PHASE1_END

REGISTERED_GATES: list[dict[str, object]] = [
    {"pillar": 892, "status_label": STATUS_892, "verdict": NGEN_BUNDLE_GATE},
    {"pillar": 893, "status_label": STATUS_893, "verdict": E8_GATE},
    {"pillar": 894, "status_label": STATUS_894, "verdict": ALPHA_S_PINNING_GATE},
    {"pillar": 895, "status_label": STATUS_895, "verdict": TCC_GATE},
    {"pillar": 896, "status_label": STATUS_896, "verdict": CMB_BEYOND_EFT_GATE},
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "STATUS_LABEL",
    "LEAN4_PHASE2_END",
    "LEAN4_DELTA",
    "PHASE2_VALID",
    "phase2_summary",
]

PHASE2_VALID: bool = LEAN4_DELTA == 90 and len(REGISTERED_GATES) == 5


def phase2_summary() -> dict[str, Any]:
    """Return the Sprint BC Phase 2 certificate."""
    counts: dict[str, int] = {}
    for row in REGISTERED_GATES:
        counts[row["status_label"]] = counts.get(row["status_label"], 0) + 1
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "phase_valid": PHASE2_VALID,
        "lean4_start": LEAN4_PHASE1_END,
        "lean4_end": LEAN4_PHASE2_END,
        "lean4_delta": LEAN4_DELTA,
        "registered_gates": REGISTERED_GATES,
        "status_counts": counts,
        "epistemic_status": (
            "Phase 2 keeps two irreducible degeneracy limits visible, narrows α_s, resolves the reduced TCC count, "
            "and confirms the CMB amplitude architecture limit."
        ),
    }
