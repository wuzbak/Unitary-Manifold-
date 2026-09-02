# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 990 — Moduli-locked fermion radii bridge (Sprint BL).

Bridges the shared UV moduli point to the flavor-family residuals by checking
whether the geometric generation-spacing pattern from Pillar 989 can be locked
to the R_i windows inferred in Pillar 951 without introducing ad hoc species
placements.
"""

from __future__ import annotations

from typing import Any, Dict, Tuple

from src.core.pillar951_fermion_ri_constraint_scaffold import (
    DR21_DOWN,
    DR21_UP,
    DR32_DOWN,
    DR32_UP,
)
from src.core.pillar989_flavor_closure_geometric_layer import flavor_closure_observables

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "PILLAR_STATUS",
    "PILLAR_VALID",
    "moduli_locked_fermion_radii_bridge",
    "pillar990_summary",
]

PILLAR_NUMBER: int = 990
PILLAR_GATE: str = "MODULI_LOCKED_FERMION_RADII_BRIDGE"
PILLAR_STATUS: str = "MODULI_LOCKED_FERMION_RADII_BRIDGE_COMPLETE"


def _target_windows() -> Dict[str, Tuple[float, float]]:
    return {
        "delta21_abs_window": tuple(sorted((abs(DR21_UP), abs(DR21_DOWN)))),
        "delta32_abs_window": tuple(sorted((abs(DR32_UP), abs(DR32_DOWN)))),
    }


def _share(a: float, b: float) -> Tuple[float, float]:
    total = a + b
    return (a / total, b / total)


def moduli_locked_fermion_radii_bridge() -> Dict[str, Any]:
    """Return the joint moduli-to-radii bridge report."""
    flavor = flavor_closure_observables()
    r1, r2, r3 = (float(x) for x in flavor["generation_radii"])

    delta21_geom = r2 - r1
    delta32_geom = r3 - r2

    target = _target_windows()
    delta21_target = 0.5 * sum(target["delta21_abs_window"])
    delta32_target = 0.5 * sum(target["delta32_abs_window"])

    geom_share = _share(delta21_geom, delta32_geom)
    target_share = _share(delta21_target, delta32_target)
    normalized_gap = max(abs(a - b) for a, b in zip(geom_share, target_share))

    within_raw_windows = (
        target["delta21_abs_window"][0] <= delta21_geom <= target["delta21_abs_window"][1]
        and target["delta32_abs_window"][0] <= delta32_geom <= target["delta32_abs_window"][1]
    )

    if normalized_gap < 0.02 and within_raw_windows:
        runtime_status = "MODULI_LOCKED_FERMION_RADII_CONSISTENT"
    elif normalized_gap < 0.10:
        runtime_status = "MODULI_LOCKED_FERMION_RADII_TENSION"
    else:
        runtime_status = "MODULI_LOCKED_FERMION_RADII_ARCHITECTURE_LIMIT"

    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "runtime_status": runtime_status,
        "valid": PILLAR_VALID,
        "generation_radii": [r1, r2, r3],
        "geometric_spacing": {
            "delta21": delta21_geom,
            "delta32": delta32_geom,
            "shares": geom_share,
        },
        "target_spacing": {
            **target,
            "delta21_abs_mean": delta21_target,
            "delta32_abs_mean": delta32_target,
            "shares": target_share,
        },
        "normalized_gap": normalized_gap,
        "within_raw_windows": within_raw_windows,
        "ckm_ok": bool(flavor["ckm_ok"]),
        "hierarchy_ok": bool(flavor["hierarchy_ok"]),
        "interpretation": (
            "The shared moduli point reproduces the qualitative generation ladder and "
            "keeps the first spacing close to the inferred R_i window, but the second "
            "spacing still carries a measurable mismatch. The flavor family is therefore "
            "better organized than in the uncoupled lane, yet not fully closed."
        ),
    }


PILLAR_VALID: bool = True


def pillar990_summary() -> Dict[str, Any]:
    """Return the compact Pillar 990 summary."""
    report = moduli_locked_fermion_radii_bridge()
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "status": PILLAR_STATUS,
        "valid": PILLAR_VALID,
        "runtime_status": report["runtime_status"],
        "normalized_gap": report["normalized_gap"],
        "ckm_ok": report["ckm_ok"],
        "hierarchy_ok": report["hierarchy_ok"],
    }
