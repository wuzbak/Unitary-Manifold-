# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1004 — 13D bifurcation sink.

Rerun the checked-in 13D parent/shadow lane as a downstream consistency sink.
The 13D scaffold is treated here as a consumer of the shared 5D + 6D + 7D
structure, not as the origin of that structure.
"""

from __future__ import annotations

from typing import Any, Dict

from src.core.pillar1001_shared_5d_bifurcation_core import shared_5d_bifurcation_core
from src.core.pillar1002_sixd_projection_branch_rule import sixd_projection_branch_rule
from src.core.pillar1003_sevend_torsion_shear_branch_rule import (
    sevend_torsion_shear_branch_rule,
)
from src.core.pillar993_parent_shadow_dictionary_13d import parent_shadow_dictionary_13d
from src.core.pillar994_unified_13d_compactification_state import (
    unified_13d_compactification_state,
)
from src.core.pillar995_ckm_shadow_closure_binary import ckm_shadow_closure_binary
from src.core.pillar996_fermion_magnitude_radii_closure_binary import (
    fermion_magnitude_radii_closure_binary,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "thirteen_dimensional_bifurcation_sink",
]

PILLAR_NUMBER: int = 1004
PILLAR_GATE: str = "THIRTEEN_DIMENSIONAL_BIFURCATION_SINK"
PILLAR_STATUS: str = "THIRTEEN_DIMENSIONAL_BIFURCATION_SINK_COMPLETE"


def _row_by_shadow_lane(dictionary: Dict[str, Any], name: str) -> Dict[str, Any]:
    return next(row for row in dictionary["rows"] if row["shadow_lane"] == name)


def thirteen_dimensional_bifurcation_sink() -> Dict[str, Any]:
    """Return the downstream 13D sink verdict."""
    core = shared_5d_bifurcation_core()
    sixd = sixd_projection_branch_rule()
    sevend = sevend_torsion_shear_branch_rule()
    dictionary = parent_shadow_dictionary_13d()
    state = unified_13d_compactification_state()
    ckm = ckm_shadow_closure_binary()
    fermion = fermion_magnitude_radii_closure_binary()

    row_6d = _row_by_shadow_lane(dictionary, "N_GEN_6D")
    row_7d = _row_by_shadow_lane(dictionary, "CP_PHASE_7D")
    sink_outcome = (
        "SHARED_5_BIFURCATION_LOAD_BEARING"
        if ckm["closed"] and fermion["closed"]
        else "THIRTEEN_D_ORGANIZATIONAL_SINK_ONLY"
    )
    gates = {
        "dictionary_valid": bool(dictionary["valid"]),
        "has_6d_projection_row": row_6d["projection_kind"] == "TRUE_PROJECTION",
        "has_7d_projection_row": row_7d["projection_kind"] == "TRUE_PROJECTION",
        "shared_consumer_count_locked": len(state["consumers"]) == 2,
        "sixd_branch_matches_dictionary_parent": row_6d["parent_symbol"] == "n_w"
        and sixd["branch_pair"] == tuple(core["shadow_realizations"][0]["pair"]),
        "sevend_branch_matches_dictionary_parent": row_7d["parent_symbol"] == "eta_bar"
        and tuple(sevend["upper_branch_pair"]) == tuple(core["shadow_realizations"][1]["pair"]),
        "downstream_lanes_remain_honest": ckm["runtime_status"].endswith("CERTIFIED")
        and fermion["runtime_status"].endswith("CERTIFIED"),
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all(gates.values()),
        "sink_outcome": sink_outcome,
        "shared_core": core,
        "sixd_branch": sixd,
        "sevend_branch": sevend,
        "dictionary": dictionary,
        "unified_state": state,
        "downstream_binary_lanes": {
            "ckm": ckm,
            "fermion": fermion,
        },
        "non_negotiable_consistency_gates": gates,
        "interpretation": (
            "The 13D scaffold organizes the 6D counting row and the 7D phase row coherently, "
            "but the downstream CKM and fermion lanes remain architecture-limited. In the checked-in branch, "
            "13D is therefore a consistency sink, not a rescue origin."
        ),
    }


PILLAR_VALID: bool = thirteen_dimensional_bifurcation_sink()["valid"]
