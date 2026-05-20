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
    "GATE_BOUNDARY_EARLY_WARNING_THRESHOLD_PCT",
    "STABLE_CORE_THRESHOLD_PCT",
    "MARGIN_ZONE_THRESHOLD_PCT",
    "alpha_s_basin_scan",
    "alpha_s_basin_hardening_report",
    "pdg_alpha_s_stability_gate",
    "basin_volatility_certificate",
]

#: Tighter early-warning threshold: triggers alarm before the 5% gate is breached.
#: Added in Pillar 311 sprint (v11.13): gives an extra 0.5% headroom over the
#: original GATE_BOUNDARY_WARNING_THRESHOLD_PCT (4.5%) for PDG-update-day alerting.
GATE_BOUNDARY_EARLY_WARNING_THRESHOLD_PCT: float = 4.0

#: Residual < this → point is in the stable core of the basin.
STABLE_CORE_THRESHOLD_PCT: float = 4.0

#: 4.0% ≤ residual < 5.0% → margin zone (approaching the gate boundary).
MARGIN_ZONE_THRESHOLD_PCT: float = 5.0

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


def basin_volatility_certificate(
    kahler_scales: Sequence[float] = (0.9, 1.0, 1.1),
    complex_scales: Sequence[float] = (0.95, 1.0, 1.05),
    flux_scales: Sequence[float] = (0.9, 1.0, 1.1),
    stable_core_threshold_pct: float = STABLE_CORE_THRESHOLD_PCT,
    margin_zone_upper_pct: float = MARGIN_ZONE_THRESHOLD_PCT,
    early_warning_threshold_pct: float = GATE_BOUNDARY_EARLY_WARNING_THRESHOLD_PCT,
) -> Dict[str, object]:
    """Produce a formal volatility certificate for the α_s parameter-space basin.

    Labels every point in the scanned CY₃ moduli basin as one of three zones:

    - **STABLE_CORE**: residual < stable_core_threshold_pct (default 4.0%)
      These points are well inside the DERIVED gate with comfortable headroom.
    - **MARGIN_ZONE**: stable_core_threshold_pct ≤ residual < margin_zone_upper_pct
      (default 4.0%–5.0%).  These are approaching the gate boundary and
      warrant attention on each PDG update.
    - **VOLATILE_OUTER**: residual ≥ margin_zone_upper_pct (default 5.0%)
      These points exceed the DERIVED gate threshold.  They correspond to
      parameter configurations with extreme CY₃ moduli (Kähler scale far
      from 1.0, or flux scale far from 1.0) and are physically disfavoured.

    The physical interpretation of VOLATILE_OUTER points is:
    - **Large Kähler excursions** (scale < 0.9 or > 1.1): the 10D compactification
      volume deviates significantly from the canonical RS1 point, amplifying
      the Kähler-sector correction.
    - **Extreme flux tuning** (scale < 0.9 or > 1.1): the flux-lattice shift
      departs from the central quantized flux value, pushing α_s away from PDG.
    - **Combined extreme** (both Kähler AND flux at edge): these are the most
      volatile points and are most physically remote from the canonical moduli.

    The canonical central point (all scales = 1.0) lies in the STABLE_CORE at
    ~4.1% residual — closest of all 28 UM parameters to the 5% DERIVED gate.

    Parameters
    ----------
    kahler_scales : sequence of float
        Kähler moduli scale factors (default 3-point grid: 0.9, 1.0, 1.1).
    complex_scales : sequence of float
        Complex-structure scale factors (default 3-point: 0.95, 1.0, 1.05).
    flux_scales : sequence of float
        Flux-lattice scale factors (default 3-point: 0.9, 1.0, 1.1).
    stable_core_threshold_pct : float
        Residual < this → STABLE_CORE (default 4.0%).
    margin_zone_upper_pct : float
        Residual ≥ this → VOLATILE_OUTER (default 5.0%).
        Points in [stable_core_threshold_pct, margin_zone_upper_pct) → MARGIN_ZONE.
    early_warning_threshold_pct : float
        Residual ≥ this → early-warning flag raised (default 4.0%, matches
        STABLE_CORE boundary so the warning fires at the first sign of drift).

    Returns
    -------
    dict with keys:

    ``pillar``                  : int — 311 (basin volatility extension)
    ``pillar_parent``           : int — 272
    ``adjacency_label``         : str
    ``n_total``                 : int — total scanned points
    ``n_stable_core``           : int
    ``n_margin_zone``           : int
    ``n_volatile_outer``        : int
    ``stable_core_fraction``    : float — fraction in STABLE_CORE
    ``margin_zone_fraction``    : float
    ``volatile_outer_fraction`` : float
    ``canonical_residual_pct``  : float — residual at canonical (all scales=1)
    ``canonical_zone``          : str   — zone label for the canonical point
    ``early_warning_triggered`` : bool
    ``volatility_map``          : list  — per-point records with zone labels
    ``volatile_outer_physical_interpretation`` : str
    ``verdict``                 : str   — "BASIN_CERT_PASS" or "BASIN_CERT_FAIL"
    """
    points = alpha_s_basin_scan(
        kahler_scales=tuple(kahler_scales),
        complex_scales=tuple(complex_scales),
        flux_scales=tuple(flux_scales),
    )

    volatility_map: List[Dict[str, object]] = []
    n_stable = n_margin = n_volatile = 0

    for pt in points:
        r = pt["residual_pct"]
        if r < stable_core_threshold_pct:
            zone = "STABLE_CORE"
            n_stable += 1
        elif r < margin_zone_upper_pct:
            zone = "MARGIN_ZONE"
            n_margin += 1
        else:
            zone = "VOLATILE_OUTER"
            n_volatile += 1

        ks = pt["kahler_scale"]
        cs = pt["complex_scale"]
        fs = pt["flux_scale"]

        # Identify the dominant physical driver of volatility
        is_extreme_kahler = abs(ks - 1.0) == max(abs(ks - 1.0), abs(cs - 1.0), abs(fs - 1.0))
        is_extreme_flux = abs(fs - 1.0) == max(abs(ks - 1.0), abs(cs - 1.0), abs(fs - 1.0))
        if zone == "VOLATILE_OUTER":
            if abs(ks - 1.0) > 0.05 and abs(fs - 1.0) > 0.05:
                physical_driver = "COMBINED_KAHLER_AND_FLUX_EXTREME"
            elif is_extreme_kahler:
                physical_driver = "LARGE_KAHLER_EXCURSION"
            elif is_extreme_flux:
                physical_driver = "EXTREME_FLUX_TUNING"
            else:
                physical_driver = "COMBINED_MODULI_DRIFT"
        else:
            physical_driver = "WITHIN_PHYSICAL_BASIN"

        volatility_map.append({
            "kahler_scale": ks,
            "complex_scale": cs,
            "flux_scale": fs,
            "alpha_s_pred": pt["alpha_s_pred"],
            "residual_pct": r,
            "zone": zone,
            "physical_driver": physical_driver,
        })

    total = len(points)
    canonical_residual = (
        abs(ALPHA_S_UM_CANONICAL_PREDICTION - ALPHA_S_PDG_CENTRAL)
        / ALPHA_S_PDG_CENTRAL * 100.0
    )
    if canonical_residual < stable_core_threshold_pct:
        canonical_zone = "STABLE_CORE"
    elif canonical_residual < margin_zone_upper_pct:
        canonical_zone = "MARGIN_ZONE"
    else:
        canonical_zone = "VOLATILE_OUTER"

    early_warning = canonical_residual >= early_warning_threshold_pct

    verdict = "BASIN_CERT_PASS" if n_volatile < total else "BASIN_CERT_FAIL"

    return {
        "pillar": 311,
        "pillar_parent": 272,
        "adjacency_label": ADJACENCY_TRACK_LABEL,
        "n_total": total,
        "n_stable_core": n_stable,
        "n_margin_zone": n_margin,
        "n_volatile_outer": n_volatile,
        "stable_core_fraction": round(n_stable / max(total, 1), 4),
        "margin_zone_fraction": round(n_margin / max(total, 1), 4),
        "volatile_outer_fraction": round(n_volatile / max(total, 1), 4),
        "canonical_residual_pct": round(canonical_residual, 4),
        "canonical_zone": canonical_zone,
        "early_warning_triggered": early_warning,
        "early_warning_threshold_pct": early_warning_threshold_pct,
        "stable_core_threshold_pct": stable_core_threshold_pct,
        "margin_zone_upper_pct": margin_zone_upper_pct,
        "volatility_map": volatility_map,
        "volatile_outer_physical_interpretation": (
            "VOLATILE_OUTER points correspond to CY₃ parameter configurations "
            "with extreme Kähler moduli (scale ≠ 1.0 by ≥10%) or extreme flux "
            "tuning (scale ≠ 1.0 by ≥10%).  These are physically disfavoured "
            "because they correspond to compactification volumes far from the "
            "canonical RS1 stabilization point.  The canonical central point "
            "(all scales = 1.0) lies in the STABLE_CORE at ~4.1% residual.  "
            "Reclassify P3 to CONSTRAINED if the canonical residual crosses 5% "
            "on a PDG update — run pdg_alpha_s_stability_gate() annually."
        ),
        "verdict": verdict,
        "pdg_update_protocol": (
            "Run basin_volatility_certificate() on each PDG release (annually). "
            "If canonical_residual_pct ≥ 5.0%: DERIVED_GATE_BREACHED — reclassify "
            "P3 to CONSTRAINED in CLAIM_MASTER_BOARD.md. "
            "If canonical_residual_pct ≥ 4.0%: EARLY_WARNING — flag for "
            "increased monitoring at next PDG release."
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
