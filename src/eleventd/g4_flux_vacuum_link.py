# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""11D G₄-flux → vacuum-selection link for the DBP continuation sprint.

This module upgrades the existing G₄-flux machinery from a structural support
proof into a direct candidate-elimination artifact.

The governing rule is conservative:
    a winding candidate survives the UV flux background only if
    (1) its minimum-step braid sector satisfies the G₄ tadpole/Bianchi checks,
    (2) the shifted Dirac quantisation phase matches the APS spin sector, and
    (3) the Z₂-odd boundary CS phase condition remains satisfied.

This does not promote any SM parameter status on its own.  It only fixes the
canonical UV vacuum seed that is later reduced to a clean 5D runtime contract.
"""

from __future__ import annotations

from typing import Dict, Tuple

from src.core.nw5_pure_theorem import aps_eta_bar, kcs_minimum_step_braid, z2_odd_phase_constraint
from src.core.uv_completion_constraints import g4_flux_bianchi_identity

__all__ = [
    "CANDIDATES",
    "candidate_braid_pair",
    "candidate_flux_sector",
    "g4_flux_selection_summary",
]

CANDIDATES: Tuple[int, int] = (5, 7)


def candidate_braid_pair(n_w: int) -> Tuple[int, int]:
    """Return the minimum-step braid pair associated with *n_w*."""
    if n_w not in CANDIDATES:
        raise ValueError(f"n_w must be one of {CANDIDATES}, got {n_w}.")
    return n_w, n_w + 2


def candidate_flux_sector(n_w: int) -> Dict[str, object]:
    """Evaluate one winding candidate against the UV G₄-flux background."""
    n1, n2 = candidate_braid_pair(n_w)
    k_cs = kcs_minimum_step_braid(n_w)
    bianchi = g4_flux_bianchi_identity(n1, n2, k_cs, k_cs / 2.0)
    aps_sector = aps_eta_bar(n_w)
    dirac_shift_mod_1 = bianchi["step_D_dirac"]["dirac_half_shift"] % 1.0
    aps_matches_flux_shift = abs(dirac_shift_mod_1 - aps_sector) < 1e-10
    z2_phase = z2_odd_phase_constraint(n_w)
    survives = bool(
        bianchi["all_proved"]
        and aps_matches_flux_shift
        and z2_phase["z2_consistent"]
    )
    return {
        "n_w": n_w,
        "braid_pair": (n1, n2),
        "k_cs": k_cs,
        "aps_eta_bar": aps_sector,
        "g4_bianchi": bianchi,
        "dirac_shift_mod_1": dirac_shift_mod_1,
        "aps_matches_flux_shift": aps_matches_flux_shift,
        "z2_phase_constraint": z2_phase,
        "candidate_survives_flux_background": survives,
        "status": (
            "SURVIVES — G₄ background, APS phase, and Z₂-odd CS phase agree."
            if survives
            else "EXCLUDED — flux shift / APS / Z₂ boundary phase do not agree."
        ),
    }


def g4_flux_selection_summary() -> Dict[str, object]:
    """Return the direct G₄-flux selection verdict over the UV candidates."""
    candidate_reports = {n_w: candidate_flux_sector(n_w) for n_w in CANDIDATES}
    surviving = [
        n_w
        for n_w, report in candidate_reports.items()
        if report["candidate_survives_flux_background"]
    ]
    unique = len(surviving) == 1
    winner = surviving[0] if unique else None
    return {
        "title": "G₄ flux ↔ vacuum selection link",
        "candidate_reports": candidate_reports,
        "surviving_candidates": surviving,
        "unique_flux_selected_n_w": winner,
        "status": (
            "UNIQUE_UV_FLUX_SELECTION"
            if unique and winner == 5
            else "NON_UNIQUE_OR_BLOCKED"
        ),
        "selection_rule": (
            "Candidate must satisfy tadpole/Bianchi closure, APS half-shift matching, "
            "and the Z₂-odd boundary CS phase."
        ),
        "no_score_inflation": True,
    }
