# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 996 — Fermion magnitude/radii closure binary decision."""

from __future__ import annotations

import math
from typing import Any, Dict, Tuple

from src.core.pillar951_fermion_ri_constraint_scaffold import (
    DR21_DOWN,
    DR21_UP,
    DR32_DOWN,
    DR32_UP,
)
from src.core.pillar994_unified_13d_compactification_state import (
    unified_13d_compactification_state,
)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "fermion_magnitude_radii_closure_binary",
]

PILLAR_NUMBER: int = 996
PILLAR_GATE: str = "FERMION_MAGNITUDE_RADII_CLOSURE_BINARY"


def _target_windows() -> Dict[str, Tuple[float, float]]:
    return {
        "delta21_abs_window": tuple(sorted((abs(DR21_UP), abs(DR21_DOWN)))),
        "delta32_abs_window": tuple(sorted((abs(DR32_UP), abs(DR32_DOWN)))),
    }


def _share(a: float, b: float) -> Tuple[float, float]:
    total = a + b
    return (a / total, b / total)


def fermion_magnitude_radii_closure_binary() -> Dict[str, Any]:
    """Return binary fermion magnitude/radii closure outcome from unified state."""
    state = unified_13d_compactification_state()
    shared = state["shared_parent_state"]
    fin = state["fermion_inputs"]

    r1 = float(fin["r1"])
    r2 = r1 + float(fin["r2_offset"])
    r3 = r2 + float(fin["r3_offset"])

    n_w = float(shared["n_w"])
    y1 = math.exp(-math.pi * n_w * r1)
    y2 = math.exp(-math.pi * n_w * r2)
    y3 = math.exp(-math.pi * n_w * r3)

    ratios = {
        "m2_over_m1": y2 / y1,
        "m3_over_m2": y3 / y2,
        "m3_over_m1": y3 / y1,
    }

    delta21_geom = r2 - r1
    delta32_geom = r3 - r2
    target = _target_windows()
    delta21_target = 0.5 * sum(target["delta21_abs_window"])
    delta32_target = 0.5 * sum(target["delta32_abs_window"])
    geom_share = _share(delta21_geom, delta32_geom)
    target_share = _share(delta21_target, delta32_target)
    normalized_gap = max(abs(a - b) for a, b in zip(geom_share, target_share))

    within_windows = (
        target["delta21_abs_window"][0] <= delta21_geom <= target["delta21_abs_window"][1]
        and target["delta32_abs_window"][0] <= delta32_geom <= target["delta32_abs_window"][1]
    )
    hierarchy_ok = ratios["m3_over_m2"] < ratios["m2_over_m1"] < 1.0

    closed = normalized_gap < 0.02 and within_windows and hierarchy_ok
    runtime_status = (
        "FERMION_MAGNITUDE_RADII_CLOSED_FROM_PARENT_13D"
        if closed
        else "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED"
    )

    named_missing_object = (
        "NONE" if closed else "SPECIES_RESOLVED_RI_GEOMETRY_WITH_BUNDLE_MODULI_LOCK"
    )

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "runtime_status": runtime_status,
        "closed": closed,
        "generation_radii": [r1, r2, r3],
        "ratios": ratios,
        "normalized_gap": normalized_gap,
        "within_windows": within_windows,
        "hierarchy_ok": hierarchy_ok,
        "named_missing_object": named_missing_object,
        "input_source": "PILLAR_994_UNIFIED_13D_COMPACTIFICATION_STATE",
    }


PILLAR_STATUS: str = "FERMION_MAGNITUDE_RADII_CLOSURE_BINARY_COMPLETE"
PILLAR_VALID: bool = True
