# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1012 — 10D branch canonicality lift ((5,6) vs (5,7)).

Adjacent sprint lane B:
- map the existing 5D branch canonicality object into 10D compactification/selection terms
- keep both sectors explicit while showing why only one survives the 10D gate chain
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from src.core.pillar541_branch_canonicality_certificate import (
    BETA_CANONICAL_DEG,
    BETA_SHADOW_DEG,
    z2_odd_boundary_phase,
)
from src.core.pillar1011_tend_flux_selection_measure_audit import flux_selection_measure_audit
from src.eleventd.g4_flux_vacuum_link import CANDIDATES
from src.tend.flux_landscape import landscape_resolution_check

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "branch_projection_row",
    "branch_projection_table",
    "branch_canonicality_lift_report",
    "pillar1012_summary",
]

PILLAR_NUMBER: int = 1012
PILLAR_GATE: str = "TEN_D_BRANCH_CANONICALITY_LIFT"
PILLAR_STATUS: str = "TEN_D_BRANCH_CANONICALITY_LIFT_COMPLETE"

_PAIR_57: Tuple[int, int] = (5, 7)
_PAIR_56: Tuple[int, int] = (5, 6)


def branch_projection_row(n1: int, n2: int) -> Dict[str, Any]:
    """Return one branch row lifted into 10D compactification/selection fields."""
    k_cs = int(n1 * n1 + n2 * n2)
    n_flux = int(k_cs // 2)
    z2 = z2_odd_boundary_phase(n1, n2)
    flux_resolution = landscape_resolution_check(n_flux=n_flux)
    candidate_in_uv_gate = n1 in CANDIDATES
    survives_uv_selection = bool(candidate_in_uv_gate and n1 == 5 and z2["is_z2_odd"])

    suppression_reasons: List[str] = []
    if not z2["is_z2_odd"]:
        suppression_reasons.append("fails_Z2_odd_boundary_phase")
    if n_flux != 37:
        suppression_reasons.append("does_not_match_shared_flux_count_37")
    if not candidate_in_uv_gate:
        suppression_reasons.append("not_in_uv_candidate_set_{5,7}")
    if candidate_in_uv_gate and n1 == 7:
        suppression_reasons.append("excluded_by_uv_flux_selection")

    status = (
        "PRESERVED_IN_10D_SELECTION_CHAIN"
        if survives_uv_selection
        else "SUPPRESSED_IN_10D_SELECTION_CHAIN"
    )
    return {
        "pair": (n1, n2),
        "k_cs": k_cs,
        "n_flux": n_flux,
        "z2_odd_boundary_pass": bool(z2["is_z2_odd"]),
        "is_uv_candidate": candidate_in_uv_gate,
        "flux_resolution_pass": bool(flux_resolution["pass"]),
        "survives_uv_selection": survives_uv_selection,
        "status": status,
        "suppression_reasons": suppression_reasons,
    }


def branch_projection_table() -> List[Dict[str, Any]]:
    """Return canonical-vs-shadow branch projection rows in fixed order."""
    return [
        branch_projection_row(*_PAIR_57),
        branch_projection_row(*_PAIR_56),
    ]


def branch_canonicality_lift_report() -> Dict[str, Any]:
    """Return full 10D lift report for canonical/shadow branch handling."""
    projection = branch_projection_table()
    measure = flux_selection_measure_audit()

    canonical_row = projection[0]
    shadow_row = projection[1]
    canonical_preserved = bool(canonical_row["survives_uv_selection"])
    shadow_preserved = bool(shadow_row["survives_uv_selection"])

    valid = bool(
        canonical_row["pair"] == _PAIR_57
        and shadow_row["pair"] == _PAIR_56
        and canonical_preserved
        and not shadow_preserved
        and measure["selected_n_w"] == 5
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": valid,
        "projection_table": projection,
        "selection_bridge": {
            "selected_n_w": measure["selected_n_w"],
            "candidate_measure_table": measure["candidate_measure_table"],
        },
        "birefringence_discriminator": {
            "beta_57_deg": BETA_CANONICAL_DEG,
            "beta_56_deg": BETA_SHADOW_DEG,
            "gap_deg": BETA_CANONICAL_DEG - BETA_SHADOW_DEG,
        },
        "open_assumptions": [
            "full_10d_moduli_dynamics_still_required_for_non_adjacent_promotion",
            "this_lift_is_epistemic_structure_not_new_physics_promotion",
        ],
        "interpretation": (
            "The branch pair is kept explicit: (5,7) is preserved through the 10D gate chain, "
            "while (5,6) remains documented as a non-canonical/suppressed branch in 10D terms."
        ),
    }


PILLAR_VALID: bool = branch_canonicality_lift_report()["valid"]


def pillar1012_summary() -> Dict[str, Any]:
    """Return concise Pillar 1012 summary."""
    report = branch_canonicality_lift_report()
    return {
        "pillar": PILLAR_NUMBER,
        "title": "10D Branch Canonicality Lift",
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "selected_n_w": report["selection_bridge"]["selected_n_w"],
        "canonical_status": report["projection_table"][0]["status"],
        "shadow_status": report["projection_table"][1]["status"],
    }
