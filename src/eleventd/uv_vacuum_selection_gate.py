# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Canonical UV vacuum-selection gate for the 11D continuation sprint.

This gate consolidates:
  - the Pillar 70-D pure theorem,
  - the Pillar 84 gravitino/Majorana selection logic,
  - the Pillar 92 G₄-flux tadpole/Bianchi closure, and
  - the Hořava-Witten Rung-6 hard-gate evidence.

The output is intentionally small and machine-readable: one canonical UV verdict,
one rejected candidate, one reduced 5D seed.  No score change is claimed.
"""

from __future__ import annotations

from typing import Dict, Tuple

from src.core.nw5_pure_theorem import nw5_pure_theorem
from src.core.vacuum_selection import euclidean_saddle_comparison, gravitino_chirality_constraint
from src.eleventd.g4_flux_vacuum_link import CANDIDATES, g4_flux_selection_summary
from src.eleventd.horava_witten_hard_gate import rung6_gate_evidence

__all__ = [
    "CANDIDATES",
    "candidate_uv_report",
    "canonical_uv_vacuum_selection_gate",
    "vacuum_selection_falsifier_map",
]


def candidate_uv_report(n_w: int) -> Dict[str, object]:
    """Return the consolidated UV gate report for one winding candidate."""
    if n_w not in CANDIDATES:
        raise ValueError(f"n_w must be one of {CANDIDATES}, got {n_w}.")
    theorem = nw5_pure_theorem()["candidate_checks"][n_w]
    majorana = gravitino_chirality_constraint(list(CANDIDATES))[n_w]
    saddle = euclidean_saddle_comparison(list(CANDIDATES))[n_w]
    flux = g4_flux_selection_summary()["candidate_reports"][n_w]
    uv_consistent = bool(
        theorem["z2_consistent"]
        and majorana["majorana_compatible"]
        and flux["candidate_survives_flux_background"]
    )
    selected = bool(uv_consistent and saddle["dominates"])
    return {
        "n_w": n_w,
        "pure_theorem_gate": theorem,
        "majorana_gate": majorana,
        "g4_flux_gate": flux,
        "euclidean_saddle_gate": saddle,
        "uv_consistent": uv_consistent,
        "selected": selected,
        "status": (
            "SELECTED"
            if selected
            else "REJECTED"
        ),
    }


def canonical_uv_vacuum_selection_gate() -> Dict[str, object]:
    """Return the unique UV-selected vacuum and reduced 5D seed."""
    rung6 = rung6_gate_evidence()
    theorem = nw5_pure_theorem()
    flux = g4_flux_selection_summary()
    candidate_reports = {n_w: candidate_uv_report(n_w) for n_w in CANDIDATES}
    winners = [n_w for n_w, report in candidate_reports.items() if report["selected"]]
    unique = len(winners) == 1
    winner = winners[0] if unique else None
    reduced_seed = {
        "n_w": 5,
        "braid_pair": (5, 7),
        "k_cs": 74,
        "eta_bar": 0.5,
        "pi_kR": 37.0,
    }
    return {
        "title": "Canonical UV vacuum-selection gate",
        "candidate_reports": candidate_reports,
        "pure_theorem": theorem,
        "g4_flux_selection": flux,
        "rung6_gate": rung6,
        "selected_n_w": winner,
        "unique_selection": unique,
        "reduced_5d_seed": reduced_seed,
        "status": (
            "CANONICAL_UV_VACUUM_FIXED"
            if unique and winner == 5 and rung6["hard_gate_pass"]
            else "VACUUM_GATE_BLOCKED"
        ),
        "no_score_inflation": True,
        "epistemic_note": (
            "This gate fixes the canonical UV seed for downstream 5D runtime use. "
            "It does not promote any P1–P28 status by itself."
        ),
    }


def vacuum_selection_falsifier_map() -> Dict[str, object]:
    """Return explicit conditions that would invalidate the UV gate."""
    return {
        "claim": "n_w = 5 is the canonical UV-selected vacuum seed",
        "falsified_if": [
            "Hořava-Witten Rung-6 hard-gate evidence fails (boundary count, E8×E8, or N=1 reduction).",
            "The Z₂-odd CS boundary phase condition no longer excludes n_w = 7.",
            "The G₄-flux shifted Dirac phase fails to match the APS sector for the selected candidate.",
            "The Euclidean saddle no longer favors n_w = 5 over n_w = 7.",
        ],
        "selected_seed": (5, 7, 74),
        "no_score_inflation": True,
    }
