# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Small holon hierarchy explorer for Ω₀ navigation."""

from __future__ import annotations

HOLON_HIERARCHY = [
    "Ω₀ Ground State",
    "P1-P208 Hardgate Physics",
    "P209-P785 Adjacent Tracks",
    "Unitary Pentad HILS",
]

_TREE = {
    "Ω₀ Ground State": {"parent": None, "children": HOLON_HIERARCHY[1:], "coupling_strength": 1.0},
    "P1-P208 Hardgate Physics": {"parent": "Ω₀ Ground State", "children": [], "coupling_strength": 0.95},
    "P209-P785 Adjacent Tracks": {"parent": "Ω₀ Ground State", "children": [], "coupling_strength": 0.74},
    "Unitary Pentad HILS": {"parent": "Ω₀ Ground State", "children": [], "coupling_strength": 35 / 74},
}
_ALIASES = {
    "omega0": "Ω₀ Ground State",
    "ω0": "Ω₀ Ground State",
    "hardgate": "P1-P208 Hardgate Physics",
    "adjacent": "P209-P785 Adjacent Tracks",
    "pentad": "Unitary Pentad HILS",
}


def expand_holon(holon_id: str) -> dict:
    """Expand a holon into parent/children/coupling metadata."""
    key = holon_id.strip()
    canonical = _ALIASES.get(key.lower(), key)
    if canonical not in _TREE:
        raise KeyError(f"Unknown holon id: {holon_id}")
    node = _TREE[canonical]
    return {
        "holon_id": canonical,
        "parent": node["parent"],
        "children": list(node["children"]),
        "coupling_strength": node["coupling_strength"],
    }
