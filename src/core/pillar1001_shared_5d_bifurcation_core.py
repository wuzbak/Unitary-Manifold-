# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1001 — Shared 5D bifurcation core.

Lock one executable object for the common 5D structure that sits underneath the
recurring (5,6) and (5,7) patterns. The claim here is intentionally modest:
this pillar does not promote a new closure. It only makes explicit which pieces
are already shared before the 6D counting branch, the 7D torsion/shear branch,
and the downstream 13D compactification lane start doing different work.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.pillar537_shadow_pair_parent_derivation import (
    BRAID_STEP_DERIVED,
    K_CS_DERIVED,
    N_BEFORE,
    N_SHADOW_OBSERVED,
    N_W_OBSERVED,
    PARENT_PRIME,
    Z2_REMOVES,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "shared_5d_bifurcation_core",
]

PILLAR_NUMBER: int = 1001
PILLAR_GATE: str = "SHARED_5D_BIFURCATION_CORE"
PILLAR_STATUS: str = "SHARED_5D_BIFURCATION_CORE_COMPLETE"


def _pair_packet(label: str, pair: tuple[int, int]) -> Dict[str, Any]:
    return {
        "label": label,
        "pair": pair,
        "k_like": pair[0] ** 2 + pair[1] ** 2,
        "shares_five_core": pair[0] == N_W_OBSERVED,
    }


def shared_5d_bifurcation_core() -> Dict[str, Any]:
    """Return the common 5D packet before the 6D/7D split."""
    lower_pair = (N_W_OBSERVED, N_BEFORE)
    upper_pair = (N_W_OBSERVED, N_SHADOW_OBSERVED)
    rows: List[Dict[str, Any]] = [
        _pair_packet("6D_counting_shadow", lower_pair),
        _pair_packet("7D_torsion_shadow", upper_pair),
    ]
    gates = {
        "shared_five_locked": N_W_OBSERVED == 5,
        "parent_integer_locked": N_BEFORE == 6,
        "projection_step_locked": Z2_REMOVES == 1,
        "upper_pair_matches_primary_kcs": rows[1]["k_like"] == K_CS_DERIVED,
        "branch_spacing_is_one": lower_pair[1] - lower_pair[0] == 1 and upper_pair[1] - lower_pair[1] == 1,
        "both_realizations_share_same_first_coordinate": all(row["shares_five_core"] for row in rows),
        "parent_prime_locked": PARENT_PRIME == 37,
        "braid_step_is_minimal": BRAID_STEP_DERIVED == 2,
    }
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": all(gates.values()),
        "shared_core": {
            "n_w": N_W_OBSERVED,
            "parent_integer": N_BEFORE,
            "z2_projection_step": Z2_REMOVES,
            "parent_prime": PARENT_PRIME,
            "primary_k_cs": K_CS_DERIVED,
            "branch_second_coordinates": [lower_pair[1], upper_pair[1]],
        },
        "shadow_realizations": rows,
        "non_negotiable_consistency_gates": gates,
        "interpretation": (
            "The shared object is the 5D core with n_w=5 anchored against the parent integer 6. "
            "The recurrent companions 6 and 7 are carried forward as sibling branch coordinates, "
            "not as independent origins."
        ),
    }


PILLAR_VALID: bool = shared_5d_bifurcation_core()["valid"]
