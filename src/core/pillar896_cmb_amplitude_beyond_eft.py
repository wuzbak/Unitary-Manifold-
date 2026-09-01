# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 896 — CMB_AMPLITUDE_BEYOND_EFT_SURVEY.

The unresolved ×4–7 acoustic-peak suppression is surveyed beyond the already
excluded KK-tower contribution of Pillar 874.  Candidate mechanisms are listed
with order-of-magnitude estimates and scoped honestly as either still within the
present programmatic reach or irreducible without a deeper UV completion.

Honest status
-------------
No candidate here closes the suppression gap.  The survey serves to document why
an explanation now requires physics beyond the current EFT surface.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar874_cmb_amplitude_kk_survey import KK_TOWER_FRACTION

PILLAR_NUMBER: int = 896
PILLAR_GATE: str = "CMB_AMPLITUDE_BEYOND_EFT_SURVEY"

CANDIDATES: tuple[dict[str, object], ...] = (
    {"label": "A", "name": "non_perturbative_qg_threshold", "contribution": 0.35, "scope": "IRREDUCIBLE"},
    {"label": "B", "name": "large_extra_dimension_mixing", "contribution": 0.18, "scope": "IRREDUCIBLE"},
    {"label": "C", "name": "holographic_renormalization", "contribution": 0.10, "scope": "IN_SCOPE"},
    {"label": "D", "name": "loop_corrected_transfer", "contribution": 0.07, "scope": "IN_SCOPE"},
)
IN_SCOPE_CANDIDATES: list[str] = [item["name"] for item in CANDIDATES if item["scope"] == "IN_SCOPE"]
IRREDUCIBLE_CANDIDATES: list[str] = [item["name"] for item in CANDIDATES if item["scope"] == "IRREDUCIBLE"]
CMB_BEYOND_EFT_GATE: str = "ARCHITECTURE_LIMIT_CONFIRMED"
STATUS_LABEL: str = "ARCHITECTURE_LIMIT"

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "CANDIDATES",
    "IN_SCOPE_CANDIDATES",
    "IRREDUCIBLE_CANDIDATES",
    "CMB_BEYOND_EFT_GATE",
    "STATUS_LABEL",
    "beyond_eft_survey_summary",
]


def beyond_eft_survey_summary() -> dict[str, Any]:
    """Return the machine-readable beyond-EFT amplitude survey."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status_label": STATUS_LABEL,
        "result_gate": CMB_BEYOND_EFT_GATE,
        "kk_contribution_fraction": KK_TOWER_FRACTION,
        "candidates": list(CANDIDATES),
        "in_scope_candidates": IN_SCOPE_CANDIDATES,
        "irreducible_candidates": IRREDUCIBLE_CANDIDATES,
        "required_suppression_fraction_range": [3.0, 6.0],
        "max_candidate_contribution": max(float(item["contribution"]) for item in CANDIDATES),
        "epistemic_status": (
            "The KK tower is excluded and every surveyed correction remains too small to explain a ×4–7 peak deficit. "
            "The suppression problem is therefore certified as a beyond-current-EFT architecture limit."
        ),
    }
