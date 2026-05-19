# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 272 — α_s basin hardening.

🔵 ADJACENT TRACK — NON_HARDGATE_ADJACENT

Extends the α_s robustness story from a one-dimensional Kähler sweep to a small
multi-parameter basin scan over Kähler, complex-structure, and flux-lattice
variations around the canonical 10D point.
"""
from __future__ import annotations

from typing import Dict, Iterable, List, Sequence

from src.tend.cy3_full_moduli_flux_alpha_s_10d import (
    ALPHA_S_BASE_5D,
    ALPHA_S_PDG,
    complex_structure_sector_shift,
    flux_lattice_shift,
    kahler_sector_shift,
)

__all__ = [
    "ADJACENCY_TRACK_LABEL",
    "alpha_s_basin_scan",
    "alpha_s_basin_hardening_report",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
RESIDUAL_THRESHOLD_PCT: float = 5.0


def alpha_s_basin_scan(
    kahler_scales: Sequence[float] = (0.9, 1.0, 1.1),
    complex_scales: Sequence[float] = (0.95, 1.0, 1.05),
    flux_scales: Sequence[float] = (0.9, 1.0, 1.1),
) -> List[Dict[str, float]]:
    """Return a small α_s basin scan around the canonical 10D closure point."""
    points: List[Dict[str, float]] = []
    for ks in kahler_scales:
        for cs in complex_scales:
            for fs in flux_scales:
                alpha = (
                    ALPHA_S_BASE_5D
                    + kahler_sector_shift(stabilization_gain=0.0065 * ks)
                    + complex_structure_sector_shift(per_mode_shift=2.2e-4 * cs)
                    + flux_lattice_shift(per_flux_shift=4.6e-4 * fs)
                )
                residual = abs(alpha - ALPHA_S_PDG) / ALPHA_S_PDG * 100.0
                points.append(
                    {
                        "kahler_scale": float(ks),
                        "complex_scale": float(cs),
                        "flux_scale": float(fs),
                        "alpha_s_pred": alpha,
                        "residual_pct": residual,
                    }
                )
    return points


def alpha_s_basin_hardening_report(
    kahler_scales: Iterable[float] = (0.9, 1.0, 1.1),
    complex_scales: Iterable[float] = (0.95, 1.0, 1.05),
    flux_scales: Iterable[float] = (0.9, 1.0, 1.1),
) -> Dict[str, object]:
    """Return the α_s basin hardening verdict."""
    points = alpha_s_basin_scan(
        kahler_scales=tuple(kahler_scales),
        complex_scales=tuple(complex_scales),
        flux_scales=tuple(flux_scales),
    )
    pass_points = [point for point in points if point["residual_pct"] < RESIDUAL_THRESHOLD_PCT]
    basin_fraction = len(pass_points) / max(len(points), 1)
    worst = max(point["residual_pct"] for point in points)
    best = min(point["residual_pct"] for point in points)
    outer_edge_tension = worst >= RESIDUAL_THRESHOLD_PCT
    return {
        "pillar": 272,
        "title": "α_s basin hardening",
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "points": points,
        "n_points": len(points),
        "n_pass_points": len(pass_points),
        "basin_fraction": basin_fraction,
        "best_residual_pct": best,
        "worst_residual_pct": worst,
        "outer_edge_tension": outer_edge_tension,
        "status": (
            "ROBUST_BASIN_CONFIRMED"
            if basin_fraction >= 0.5
            else "ROBUSTNESS_TENSION"
        ),
        "note": (
            "The central basin is stable across the majority of nearby Kähler / "
            "complex-structure / flux variations, while the outer-most corners "
            "remain explicitly flagged if they exceed the 5% line."
        ),
    }
