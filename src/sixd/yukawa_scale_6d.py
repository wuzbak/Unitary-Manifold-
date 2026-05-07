# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""6D Yukawa scale bridge from fixed-point overlap integrals (Wave 7 / W7-B)."""

from __future__ import annotations

import math
from typing import Dict, Sequence, Tuple

from src.sixd.field_equations_6d import K_CS, N_W, PI_KR, cl_from_fixed_point

__all__ = [
    "FIXED_POINTS_T2Z3",
    "DEFAULT_G5",
    "DEFAULT_C_R",
    "TOP_YUKAWA_SM",
    "TOP_YUKAWA_TOLERANCE",
    "parameter_gate_status",
    "zero_mode_profile_amplitude",
    "fixed_point_overlap",
    "yukawa_entry",
    "diagonal_yukawa_spectrum",
    "top_yukawa_kill_switch",
    "yukawa_scale_bridge_summary",
]

FIXED_POINTS_T2Z3: Tuple[complex, complex, complex] = (
    complex(0.0, 0.0),
    complex(1.0 / 3.0, 0.0),
    complex(2.0 / 3.0, 0.0),
)

DEFAULT_G5 = 1.0
DEFAULT_C_R = 0.47
TOP_YUKAWA_SM = 0.935
TOP_YUKAWA_TOLERANCE = 0.50


def parameter_gate_status(residual: float) -> str:
    return "CONSTRAINED" if residual <= TOP_YUKAWA_TOLERANCE else "FITTED"


def zero_mode_profile_amplitude(c_bulk: float, pi_kr: float = PI_KR) -> float:
    """RS-like zero-mode amplitude at the IR brane (dimensionless, normalized)."""
    if c_bulk <= 0.5:
        return 1.0
    return math.exp(-0.5 * (c_bulk - 0.5) * pi_kr)


def fixed_point_overlap(
    i: int,
    j: int,
    sigma: float = 1.0 / 3.0,
    points: Sequence[complex] = FIXED_POINTS_T2Z3,
) -> float:
    """Fixed-point overlap factor on T²/Z₃ (Gaussian kernel + Z₃ suppression)."""
    if not (0 <= i < len(points) and 0 <= j < len(points)):
        raise ValueError("fixed-point indices out of range")
    distance = abs(points[i] - points[j])
    gaussian = math.exp(-(distance ** 2) / max(2.0 * sigma ** 2, 1e-12))
    z3_suppression = 1.0 if i == j else math.exp(-math.pi)
    return gaussian * z3_suppression


def yukawa_entry(
    i: int,
    j: int,
    g5: float = DEFAULT_G5,
    c_r: float = DEFAULT_C_R,
) -> float:
    """Compute Y_ij = g5² |ψ_L(i)|² |ψ_R(j)|² × overlap_ij."""
    c_l = cl_from_fixed_point(i)
    psi_l = zero_mode_profile_amplitude(c_l)
    psi_r = zero_mode_profile_amplitude(c_r)
    overlap = fixed_point_overlap(i, j)
    return (g5 ** 2) * (psi_l ** 2) * (psi_r ** 2) * overlap


def diagonal_yukawa_spectrum(g5: float = DEFAULT_G5, c_r: float = DEFAULT_C_R) -> Dict[str, object]:
    """Return the diagonal Yukawa bridge spectrum for the three generations."""
    diagonal = [yukawa_entry(i, i, g5=g5, c_r=c_r) for i in range(3)]
    return {
        "inputs": {
            "N_W": N_W,
            "K_CS": K_CS,
            "pi_kR": PI_KR,
            "g5": g5,
            "c_r": c_r,
        },
        "diagonal": diagonal,
        "hierarchy": diagonal[0] > diagonal[1] > diagonal[2],
        "mass_ratio_01": diagonal[0] / max(diagonal[1], 1e-30),
        "mass_ratio_12": diagonal[1] / max(diagonal[2], 1e-30),
        "top_candidate": max(diagonal),
    }


def top_yukawa_kill_switch(
    g5: float = DEFAULT_G5,
    c_r: float = DEFAULT_C_R,
    target: float = TOP_YUKAWA_SM,
    tolerance: float = TOP_YUKAWA_TOLERANCE,
) -> Dict[str, object]:
    """Kill-switch: top-like Yukawa residual must be <= 50%."""
    spec = diagonal_yukawa_spectrum(g5=g5, c_r=c_r)
    predicted = float(spec["top_candidate"])
    residual = abs(predicted - target) / max(target, 1e-30)
    return {
        "predicted_top_yukawa": predicted,
        "target_top_yukawa": target,
        "residual": residual,
        "residual_pct": residual * 100.0,
        "tolerance": tolerance,
        "tolerance_pct": tolerance * 100.0,
        "pass": residual <= tolerance,
        "status_recommendation": parameter_gate_status(residual),
    }


def yukawa_scale_bridge_summary(g5: float = DEFAULT_G5, c_r: float = DEFAULT_C_R) -> Dict[str, object]:
    """Consolidated W7-B artifact for P6/P7/P8/P16 gate updates."""
    spec = diagonal_yukawa_spectrum(g5=g5, c_r=c_r)
    ks = top_yukawa_kill_switch(g5=g5, c_r=c_r)
    status = ks["status_recommendation"]
    return {
        "module": "src/sixd/yukawa_scale_6d.py",
        "mechanism": "Y_i = g5² × |ψ_L|² × |ψ_R|² × overlap(T²/Z₃)",
        "spectrum": spec,
        "kill_switch": ks,
        "parameter_gate_updates": {
            "P6": status,
            "P7": status,
            "P8": status,
            "P16": status,
        },
        "epistemic_note": (
            "This is a geometric bridge estimate anchored in 6D overlaps; "
            "it constrains the Yukawa scale but does not claim exact closure."
        ),
    }
