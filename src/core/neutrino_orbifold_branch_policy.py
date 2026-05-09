# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Explicit neutrino branch policy for the continuation sprint.

This module does not erase either existing branch.  Instead, it hardens the
runtime policy:
  - the minimal 5D EFT keeps the Dirac-leading branch,
  - the UV-extended branch keeps the allowed/proved Majorana seesaw path,
  - no module may mix the two without an explicit branch declaration.
"""

from __future__ import annotations

from typing import Dict

from src.core.neutrino_majorana_dirac import neutrino_mass_type_prediction
from src.core.neutrino_majorana_uv_proof import lightest_neutrino_mass_status

__all__ = [
    "minimal_5d_branch",
    "uv_extended_majorana_branch",
    "neutrino_branch_policy",
]


def minimal_5d_branch() -> Dict[str, object]:
    """Return the minimal-5D runtime branch."""
    base = neutrino_mass_type_prediction()
    return {
        "branch_id": "MINIMAL_5D_DIRAC",
        "selected_for_runtime": True,
        "predicted_type": base["predicted_type_minimal_um"],
        "justification": (
            "Use only 5D EFT seeds. Brane Majorana mass is not taken as a runtime "
            "seed; 0νββ is absent at leading order in the minimal branch."
        ),
        "blocking_observable": "0νββ detection or first-principles bulk Majorana closure",
        "source": base,
    }


def uv_extended_majorana_branch() -> Dict[str, object]:
    """Return the UV-extended Majorana/seesaw branch."""
    proof = lightest_neutrino_mass_status()
    return {
        "branch_id": "UV_EXTENDED_MAJORANA",
        "selected_for_runtime": False,
        "status": proof["new_status"],
        "requires": (
            "UV-localised ν_R branch",
            "GW-induced UV operator",
            "Planck-scale M_R saturation",
        ),
        "justification": (
            "This branch is admissible only when the UV completion is explicitly "
            "kept in the calculation. It is not the default reduced 5D runtime branch."
        ),
        "blocking_observable": "absolute mass scale and 0νββ branch discrimination",
        "source": proof,
    }


def neutrino_branch_policy() -> Dict[str, object]:
    """Return the branch-separation policy used by the continuation sprint."""
    minimal = minimal_5d_branch()
    uv_majorana = uv_extended_majorana_branch()
    return {
        "title": "Neutrino orbifold branch policy",
        "minimal_5d_branch": minimal,
        "uv_extended_majorana_branch": uv_majorana,
        "runtime_policy": (
            "No implicit branch mixing. P16/P17 oscillation modules may remain "
            "branch-agnostic, but P26/0νββ statements must declare branch."
        ),
        "canonical_runtime_branch": minimal["branch_id"],
        "uv_only_branch": uv_majorana["branch_id"],
        "score_policy": "no_parameter_promotion_from_branch-policy_clarification_alone",
        "status": "BRANCHES_SEPARATED_AND_EXPLICIT",
    }
