# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 867 — ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE

Single registry for every route to α_s(M_Z) attempted in the framework,
from the 5D EFT routes through the 7D geometric routes.

The audit is a bookkeeping object with one honest verdict per route.  It does
not upgrade any route: the 5D architecture limit stays certified, and the 7D
routes stay PARTIAL because both share an undetermined volume/scale parameter.
"""
from __future__ import annotations

from typing import Any

from src.core.pillar866_alphas_7d_route_d_tightened import (
    ALPHA_S_COMBINED,
    ALPHA_S_KAHLER,
    ALPHA_S_ROUTE_D,
    TENSION_SIGMA as COMBINED_TENSION_SIGMA,
    TIGHTENED_INTERVAL,
)
from src.core.pillar865_alphas_7d_kahler_constraint import ALPHA_S_PDG, ALPHA_S_PDG_ERR

PILLAR_NUMBER: int = 867
PILLAR_GATE: str = "ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE"

LEAN4_THEOREM_COUNT: int = 15
LEAN4_TOTAL_BEFORE: int = 2341
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

ROUTES: list[dict[str, Any]] = [
    {
        "route": "A",
        "dimension": 5,
        "mechanism": "KK threshold matching at M_KK",
        "verdict": "ARCHITECTURE_LIMIT",
        "pillar": 816,
        "note": "TYPE_B structural floor 40.2%–41.8%; cannot be closed inside 5D.",
    },
    {
        "route": "B",
        "dimension": 5,
        "mechanism": "NSVZ exact beta function closure",
        "verdict": "ARCHITECTURE_LIMIT",
        "pillar": 816,
        "note": "Lean4 certified in AlphaSNSVZClosure.lean; 5D data insufficient.",
    },
    {
        "route": "C",
        "dimension": 5,
        "mechanism": "Winding-number threshold correction",
        "verdict": "ARCHITECTURE_LIMIT",
        "pillar": 816,
        "note": "Δα_s^winding < 1%; does not close the 5D gap.",
    },
    {
        "route": "D",
        "dimension": 7,
        "mechanism": "Discrete torsion on T²/Z₃ (Vol ratio)",
        "verdict": "PARTIAL",
        "pillar": 844,
        "note": "α_s(M_Z) ≈ 0.1164; R₆/R₅ volume ratio not uniquely fixed.",
    },
    {
        "route": "E",
        "dimension": 7,
        "mechanism": "GS tadpole Kähler modulus ρ_K = 74",
        "verdict": "PARTIAL_NARROWED",
        "pillar": 865,
        "note": "α_s(M_Z) ≈ 0.1162; ρ_K pinned but M₇ not fixed.",
    },
    {
        "route": "D+E",
        "dimension": 7,
        "mechanism": "Intersection of Routes D and E",
        "verdict": "TIGHTENED",
        "pillar": 866,
        "note": "Band halved; central value ≈ 1.6σ below PDG.",
    },
]

ARCHITECTURE_LIMITS_CERTIFIED: list[str] = [
    "ALPHA_S_5D_ARCHITECTURE_LIMIT: Routes A–C cannot be closed within the 5D EFT.",
    "ALPHA_S_7D_SCALE_ARCHITECTURE_LIMIT: Routes D and E share an undetermined "
    "7D volume/scale parameter (R₆/R₅ and M₇/M_KK respectively).",
]

REMAINING_OPEN: list[str] = [
    "ALPHA_S_M7_FROM_UV_OPEN: fixing M₇ requires the 10D/11D UV completion.",
    "ALPHA_S_LATTICE_DATA_OPEN: sub-percent discrimination needs FLAG NNLO averages.",
]

N_ROUTES: int = len(ROUTES)
N_ARCHITECTURE_LIMIT_ROUTES: int = sum(r["verdict"] == "ARCHITECTURE_LIMIT" for r in ROUTES)
N_PARTIAL_ROUTES: int = sum(str(r["verdict"]).startswith("PARTIAL") for r in ROUTES)
DIMENSIONS_AUDITED: list[int] = sorted({int(r["dimension"]) for r in ROUTES})
BEST_CENTRAL: float = ALPHA_S_COMBINED
BEST_TENSION_SIGMA: float = COMBINED_TENSION_SIGMA
AUDIT_COMPLETE: bool = all("verdict" in r and "pillar" in r for r in ROUTES)

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "ROUTES",
    "N_ROUTES",
    "N_ARCHITECTURE_LIMIT_ROUTES",
    "N_PARTIAL_ROUTES",
    "DIMENSIONS_AUDITED",
    "BEST_CENTRAL",
    "BEST_TENSION_SIGMA",
    "AUDIT_COMPLETE",
    "ARCHITECTURE_LIMITS_CERTIFIED",
    "REMAINING_OPEN",
    "route_by_label",
    "alphas_cross_dimensional_audit_summary",
]


def route_by_label(label: str) -> dict[str, Any]:
    """Return the audit record for a route label such as 'A' or 'D+E'."""
    for record in ROUTES:
        if record["route"] == label:
            return record
    raise KeyError(f"unknown route label: {label}")


def alphas_cross_dimensional_audit_summary() -> dict[str, Any]:
    """Return the machine-readable cross-dimensional α_s audit."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "routes": ROUTES,
        "n_routes": N_ROUTES,
        "n_architecture_limit_routes": N_ARCHITECTURE_LIMIT_ROUTES,
        "n_partial_routes": N_PARTIAL_ROUTES,
        "dimensions_audited": DIMENSIONS_AUDITED,
        "alpha_s_route_d": ALPHA_S_ROUTE_D,
        "alpha_s_kahler": ALPHA_S_KAHLER,
        "alpha_s_best_central": BEST_CENTRAL,
        "tightened_interval": list(TIGHTENED_INTERVAL),
        "alpha_s_pdg": ALPHA_S_PDG,
        "alpha_s_pdg_err": ALPHA_S_PDG_ERR,
        "best_tension_sigma": BEST_TENSION_SIGMA,
        "audit_complete": AUDIT_COMPLETE,
        "architecture_limits_certified": ARCHITECTURE_LIMITS_CERTIFIED,
        "epistemic_status": (
            "AUDIT_COMPLETE: every route is registered with an explicit verdict. "
            "No route is promoted; the 5D limit and the 7D scale limit both stand."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
