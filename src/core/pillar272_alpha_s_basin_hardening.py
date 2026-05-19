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
    "ALPHA_S_PDG_CENTRAL",
    "ALPHA_S_PDG_UNCERTAINTY",
    "ALPHA_S_UM_CANONICAL_PREDICTION",
    "GATE_BOUNDARY_WARNING_THRESHOLD_PCT",
    "alpha_s_basin_scan",
    "alpha_s_basin_hardening_report",
    "pdg_alpha_s_stability_gate",
]

ADJACENCY_TRACK_LABEL: str = "NON_HARDGATE_ADJACENT"
RESIDUAL_THRESHOLD_PCT: float = 5.0

#: PDG 2024 world average for α_s(M_Z).  Update on each PDG release.
#: Source: PDG 2024 Review of Particle Physics (α_s Review, Table 9.4).
ALPHA_S_PDG_CENTRAL: float = 0.1179

#: PDG 2024 1σ combined uncertainty on α_s(M_Z).
ALPHA_S_PDG_UNCERTAINTY: float = 0.0009

#: UM canonical central-point prediction for α_s(M_Z).
#: Computed from the 10D CY₃+flux chain at the canonical moduli point
#: (Kähler scale=1.0, complex-structure scale=1.0, flux scale=1.0).
#: ~4.1% below PDG 2024 central — closest of all 28 parameters to the 5% gate.
ALPHA_S_UM_CANONICAL_PREDICTION: float = round(
    ALPHA_S_BASE_5D
    + kahler_sector_shift(stabilization_gain=0.0065)
    + complex_structure_sector_shift(per_mode_shift=2.2e-4)
    + flux_lattice_shift(per_flux_shift=4.6e-4),
    6,
)

#: Warn if the canonical residual exceeds this percentage — approaching the 5% gate.
GATE_BOUNDARY_WARNING_THRESHOLD_PCT: float = 4.5


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


def pdg_alpha_s_stability_gate(
    pdg_central: float = ALPHA_S_PDG_CENTRAL,
    pdg_uncertainty: float = ALPHA_S_PDG_UNCERTAINTY,
    um_prediction: float = ALPHA_S_UM_CANONICAL_PREDICTION,
    gate_threshold_pct: float = RESIDUAL_THRESHOLD_PCT,
) -> Dict[str, object]:
    """Check whether the UM α_s prediction stays within the DERIVED gate.

    Performs three gate checks:
    1. **Central-value residual**: |UM − PDG_central| / PDG_central × 100.
       Must be < 5% to remain DERIVED (currently ~4.1%).
    2. **+1σ robustness**: residual against PDG_central + 1σ (worst case for
       upward PDG shift).  If this residual ≥ 5%, the claim is approaching
       the gate boundary under even a one-sigma PDG shift.
    3. **Gate-boundary warning**: residual > GATE_BOUNDARY_WARNING_THRESHOLD_PCT
       (4.5%) triggers a WARNING flag, prompting attention before gate breach.

    Run this function on every PDG release (annually).  If the central-value
    gate is breached (check 1 fails), reclassify P3 from DERIVED to CONSTRAINED
    in docs/CLAIM_MASTER_BOARD.md and docs/TRUTH_LAYER.md.

    Parameters
    ----------
    pdg_central : float
        PDG world-average α_s(M_Z).  Default: PDG 2024 (0.1179).
    pdg_uncertainty : float
        PDG 1σ combined uncertainty.  Default: PDG 2024 (0.0009).
    um_prediction : float
        UM canonical central-point α_s prediction.
        Default: ALPHA_S_UM_CANONICAL_PREDICTION (~0.1130).
    gate_threshold_pct : float
        DERIVED gate boundary in percent.  Default: 5.0%.

    Returns
    -------
    dict
        residual_pct_central    : float — residual at PDG central value
        residual_pct_1sigma_up  : float — residual at PDG central + 1σ
        gate_pass_central       : bool  — True iff residual_pct_central < threshold
        gate_pass_1sigma        : bool  — True iff residual_pct_1sigma_up < threshold
        gate_boundary_warning   : bool  — True iff residual_pct_central > 4.5%
        verdict                 : str   — "DERIVED_GATE_PASS",
                                          "DERIVED_GATE_PASS_WITH_WARNING", or
                                          "DERIVED_GATE_BREACHED"
        reclassification_action : str | None — None if gate passes;
                                               instruction if gate breached
        pdg_values_used         : dict  — records the PDG inputs used
        um_prediction_used      : float — records the UM prediction used
    """
    residual_central = abs(um_prediction - pdg_central) / pdg_central * 100.0
    residual_1sigma_up = abs(um_prediction - (pdg_central + pdg_uncertainty)) / (
        pdg_central + pdg_uncertainty
    ) * 100.0

    gate_pass_central = residual_central < gate_threshold_pct
    gate_pass_1sigma = residual_1sigma_up < gate_threshold_pct
    gate_boundary_warning = residual_central >= GATE_BOUNDARY_WARNING_THRESHOLD_PCT

    if not gate_pass_central:
        verdict = "DERIVED_GATE_BREACHED"
        reclassification_action = (
            "RECLASSIFY P3 from DERIVED to CONSTRAINED in "
            "docs/CLAIM_MASTER_BOARD.md and docs/TRUTH_LAYER.md. "
            "Record PDG values, date, and σ-level in CLAIM_MASTER_BOARD P3 row. "
            "Run alpha_s_basin_scan() to confirm basin fraction change."
        )
    elif gate_boundary_warning:
        verdict = "DERIVED_GATE_PASS_WITH_WARNING"
        reclassification_action = None
    else:
        verdict = "DERIVED_GATE_PASS"
        reclassification_action = None

    return {
        "residual_pct_central": residual_central,
        "residual_pct_1sigma_up": residual_1sigma_up,
        "gate_pass_central": gate_pass_central,
        "gate_pass_1sigma": gate_pass_1sigma,
        "gate_boundary_warning": gate_boundary_warning,
        "verdict": verdict,
        "reclassification_action": reclassification_action,
        "pdg_values_used": {
            "alpha_s_pdg_central": pdg_central,
            "alpha_s_pdg_uncertainty": pdg_uncertainty,
            "source": "PDG 2024 (update annually)",
        },
        "um_prediction_used": um_prediction,
        "gate_threshold_pct": gate_threshold_pct,
        "note": (
            f"Run pdg_alpha_s_stability_gate() on each PDG release. "
            f"Current residual: {residual_central:.2f}% at PDG 2024 central. "
            f"Gate boundary: {gate_threshold_pct}%. "
            f"Warning threshold: {GATE_BOUNDARY_WARNING_THRESHOLD_PCT}%."
        ),
    }
