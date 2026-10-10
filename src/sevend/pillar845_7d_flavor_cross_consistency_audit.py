# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 845 — SEVEND_FLAVOR_CROSS_CONSISTENCY_AUDIT_PARTIAL

7D flavour-sector cross-consistency audit.

Honest status
-------------
This is a PARTIAL closure.  Pillar 843 (CKM SVD mixing) and Pillar 844
(α_s discrete-torsion Route D) independently fix structural/hierarchical
predictions from the same 7D geometry (n_w=5, K_CS=74, πkR=37), while
Pillar 575's discrete-torsion CP-phase module (`discrete_torsion_cp.py`)
separately derives δ_CP.  This module audits that the three 7D results
remain within their individually-declared kill-switch tolerances *at the
same time*, i.e. the 7D rung as a whole is self-consistent before Pillar
846's phase-2 regression certificate closes it out.  It does not derive
any new physical quantity and does not weaken any pillar's individual
open items.
"""
from __future__ import annotations

from typing import Dict, List

from src.sevend.discrete_torsion_cp import (
    KILL_SWITCH_PASS as CP_KILL_SWITCH_PASS,
    RESIDUAL_PHYSICAL as CP_RESIDUAL_PHYSICAL,
    RESIDUAL_TOLERANCE as CP_RESIDUAL_TOLERANCE,
)
from src.sevend.pillar843_7d_ckm_svd_mixing_angles import (
    PILLAR_GATE as GATE_843,
    PILLAR_NUMBER as NUM_843,
    ckm_7d_mixing_summary,
)
from src.sevend.pillar844_7d_alphas_discrete_torsion import (
    PILLAR_GATE as GATE_844,
    PILLAR_NUMBER as NUM_844,
    alphas_7d_summary,
)

PILLAR_NUMBER: int = 845
PILLAR_GATE: str = "SEVEND_FLAVOR_CROSS_CONSISTENCY_AUDIT_PARTIAL"
PILLAR_TITLE: str = "7D Flavor-Sector Cross-Consistency Audit"

N_W: int = 5
K_CS: int = 74
PI_KR: float = 37.0

LEAN4_THEOREM_COUNT: int = 0
LEAN4_TOTAL_AFTER: int = 1996  # unchanged: this pillar adds no Lean4 theorems


def audited_pillars() -> List[int]:
    """Return the 7D-rung pillar numbers audited by this module."""
    return [NUM_843, NUM_844]


def cross_consistency_rows() -> List[Dict[str, object]]:
    """Return the per-pillar kill-switch state used in the joint audit."""
    ckm = ckm_7d_mixing_summary()
    alphas = alphas_7d_summary()
    return [
        {
            "pillar": NUM_843,
            "gate": GATE_843,
            "kill_switch_pass": bool(
                ckm["hierarchy_correct"] and ckm["all_within_factor_two_of_pdg"]
            ),
        },
        {
            "pillar": NUM_844,
            "gate": GATE_844,
            "kill_switch_pass": bool(alphas["in_expected_range"]),
        },
        {
            "pillar": 575,
            "gate": "FTHEORY_12D_RUNG7_SYNC_DISCRETE_TORSION_CP",
            "kill_switch_pass": bool(CP_KILL_SWITCH_PASS),
            "residual_physical": CP_RESIDUAL_PHYSICAL,
            "residual_tolerance": CP_RESIDUAL_TOLERANCE,
        },
    ]


def sevend_cross_consistency_summary() -> Dict[str, object]:
    """Return the machine-readable 7D cross-consistency certificate."""
    rows = cross_consistency_rows()
    all_pass = all(bool(row["kill_switch_pass"]) for row in rows)
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "title": PILLAR_TITLE,
        "n_w": N_W,
        "k_cs": K_CS,
        "pi_kR": PI_KR,
        "audited_pillars": audited_pillars(),
        "rows": rows,
        "all_kill_switches_pass": all_pass,
        "acceptance_gate_passed": bool(all_pass),
        "epistemic_status": (
            "PARTIAL: confirms the 7D CKM, α_s, and CP-phase results are "
            "simultaneously within their own declared tolerances; this is "
            "a consistency audit, not an independent derivation."
        ),
        "remaining_open": [
            "CKM_7D_EXACT_ANGLES_OPEN: carried over from Pillar 843 (unchanged).",
            "ALPHA_S_7D_VOL_PARAMETER_OPEN: carried over from Pillar 844 (unchanged).",
        ],
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_TITLE",
    "N_W",
    "K_CS",
    "PI_KR",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "audited_pillars",
    "cross_consistency_rows",
    "sevend_cross_consistency_summary",
]
