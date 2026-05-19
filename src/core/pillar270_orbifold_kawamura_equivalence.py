# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 270 — Orbifold equivalence hardening.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Executable equivalence check between:
- the UM-internal winding-derived orbifold route, and
- the canonical Kawamura SU(5)/Z₂ projection route.
"""
from __future__ import annotations

from typing import Dict

from src.core.non_abelian_orbifold_emergence import su5_breaking_pattern, su5_zero_mode_count
from src.core.su5_orbifold_proof import (
    kawamura_from_winding,
    kawamura_projection_matrix,
    orbifold_spectrum,
)

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "orbifold_parity_equivalence",
    "orbifold_spectrum_equivalence",
    "orbifold_equivalence_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"


def orbifold_parity_equivalence() -> Dict[str, object]:
    """Compare the UM winding-derived parity matrix with the Kawamura matrix."""
    winding = kawamura_from_winding()
    kawamura = kawamura_projection_matrix()
    p_winding = list(winding["P_matrix"])
    p_kawamura = list(kawamura["P_eigenvalues"])
    equivalent = p_winding == p_kawamura and bool(winding["in_SU_n_w"])
    return {
        "winding_route": winding,
        "kawamura_route": kawamura,
        "equivalent": equivalent,
    }


def orbifold_spectrum_equivalence() -> Dict[str, object]:
    """Compare the low-energy spectrum counts across the two orbifold routes."""
    spectrum = orbifold_spectrum()
    breaking = su5_breaking_pattern()
    zero_modes = su5_zero_mode_count()
    equivalent = (
        spectrum["massless_zero_modes"]["count"] == breaking["n_zero_modes"] == zero_modes["total_sm"]
        and spectrum["massive_kk_modes"]["count"] == breaking["n_heavy_bosons"] == zero_modes["heavy_xy"]
        and bool(breaking["is_sm_gauge_group"])
        and bool(breaking["is_correct_zero_mode_count"])
    )
    return {
        "spectrum_route": spectrum,
        "breaking_route": breaking,
        "zero_mode_route": zero_modes,
        "equivalent": equivalent,
    }


def orbifold_equivalence_report() -> Dict[str, object]:
    """Return the executable orbifold-equivalence hardening report."""
    parity = orbifold_parity_equivalence()
    spectrum = orbifold_spectrum_equivalence()
    closed = bool(parity["equivalent"] and spectrum["equivalent"])
    return {
        "pillar": 270,
        "title": "Orbifold / Kawamura equivalence hardening",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "parity_equivalence": parity,
        "spectrum_equivalence": spectrum,
        "equivalence_closed": closed,
        "status": (
            "ORBIFOLD_EQUIVALENCE_EXECUTABLE_CLOSED"
            if closed
            else "ORBIFOLD_EQUIVALENCE_TENSION"
        ),
        "remaining_open": (
            "Further referee-facing prose can be improved, but the parity matrix "
            "and spectrum equivalence are now executable rather than asserted."
        ),
    }
