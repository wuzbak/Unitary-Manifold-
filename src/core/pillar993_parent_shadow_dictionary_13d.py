# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 993 — Parent→Shadow dictionary for 13D geometry."""

from __future__ import annotations

from typing import Any, Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "PARENT_INVARIANTS_13D",
    "PARENT_SHADOW_DICTIONARY_13D",
    "parent_shadow_dictionary_13d",
]

PILLAR_NUMBER: int = 993
PILLAR_GATE: str = "PARENT_SHADOW_DICTIONARY_13D"

PARENT_INVARIANTS_13D: Dict[str, Any] = {
    "n_w": 5,
    "braid_pair": (5, 7),
    "k_cs": 74,
    "eta_bar": 0.5,
    "pi_kR": 37,
}

PARENT_SHADOW_DICTIONARY_13D: List[Dict[str, Any]] = [
    {
        "parent_symbol": "n_w",
        "shadow_lane": "N_GEN_6D",
        "projection_kind": "TRUE_PROJECTION",
        "notes": "Orbifold fixed-point counting anchors the generation projection.",
    },
    {
        "parent_symbol": "k_cs",
        "shadow_lane": "GAUGE_RANK_8D",
        "projection_kind": "TRUE_PROJECTION",
        "notes": "Gauge-rank conservation survives as a direct dimensional projection.",
    },
    {
        "parent_symbol": "eta_bar",
        "shadow_lane": "CP_PHASE_7D",
        "projection_kind": "TRUE_PROJECTION",
        "notes": "Discrete torsion phase routing remains a direct topological projection.",
    },
    {
        "parent_symbol": "pi_kR",
        "shadow_lane": "CKM_THETA13",
        "projection_kind": "EFFECTIVE_SHADOW",
        "notes": "Requires global flavor bundle geometry not yet fixed in-runtime.",
    },
    {
        "parent_symbol": "pi_kR",
        "shadow_lane": "FERMION_MASS_MAGNITUDES",
        "projection_kind": "EFFECTIVE_SHADOW",
        "notes": "Magnitude closure still depends on species-resolved radii locking.",
    },
    {
        "parent_symbol": "k_cs",
        "shadow_lane": "ALPHA_S_TYPE_B_FLOOR",
        "projection_kind": "EFFECTIVE_SHADOW",
        "notes": "Needs a fully fixed CY moduli point plus threshold map.",
    },
]


def parent_shadow_dictionary_13d() -> Dict[str, Any]:
    """Return canonical parent→shadow dictionary with hard consistency gates."""
    invariants = PARENT_INVARIANTS_13D
    gate_checks = {
        "k_cs_identity": int(invariants["k_cs"]) == 5**2 + 7**2,
        "n_w_in_braid_pair": int(invariants["n_w"]) in tuple(invariants["braid_pair"]),
        "pi_kR_consistency": float(invariants["pi_kR"]) > float(invariants["k_cs"]) / 3.0,
        "dictionary_has_true_and_shadow": {
            row["projection_kind"] for row in PARENT_SHADOW_DICTIONARY_13D
        }
        == {"TRUE_PROJECTION", "EFFECTIVE_SHADOW"},
    }
    is_valid = all(gate_checks.values())

    true_projection_count = sum(
        1 for row in PARENT_SHADOW_DICTIONARY_13D if row["projection_kind"] == "TRUE_PROJECTION"
    )
    effective_shadow_count = sum(
        1 for row in PARENT_SHADOW_DICTIONARY_13D if row["projection_kind"] == "EFFECTIVE_SHADOW"
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": is_valid,
        "parent_invariants": invariants,
        "rows": PARENT_SHADOW_DICTIONARY_13D,
        "counts": {
            "true_projection": true_projection_count,
            "effective_shadow": effective_shadow_count,
        },
        "non_negotiable_consistency_gates": gate_checks,
    }


PILLAR_STATUS: str = "PARENT_SHADOW_DICTIONARY_13D_COMPLETE"
PILLAR_VALID: bool = parent_shadow_dictionary_13d()["valid"]
