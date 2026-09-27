# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Geometric Yukawa overlaps for three-sector S¹/Z₂ model.

Implements a zero-mode overlap construction on S¹/Z₂ with explicit UV/bulk/IR
localization centers derived from the (5, 6, 7) three-sector split.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
N_W: int = 5
N_PARENT: int = 6
N_SHADOW: int = 7
PI_KR: float = 37.0


@dataclass(frozen=True)
class Localization:
    center: float
    width: float


def default_sector_localization() -> Dict[str, Localization]:
    """Return canonical UV/bulk/IR localization settings on y ∈ [0, 1]."""
    return {
        "uv": Localization(center=0.0, width=1.0 / N_W),
        "bulk": Localization(center=0.5, width=1.0 / N_PARENT),
        "ir": Localization(center=1.0, width=1.0 / N_SHADOW),
    }


def _gaussian(y: float, loc: Localization) -> float:
    width = max(loc.width, 1e-12)
    direct = abs(y - loc.center)
    wrapped = min(direct, 1.0 - direct)
    mirrored = abs(y - (1.0 - loc.center))
    d_orbifold = min(wrapped, mirrored)
    z = d_orbifold / width
    return math.exp(-0.5 * z * z)


def _orbifold_distance_array(y: np.ndarray, center: float) -> np.ndarray:
    direct = np.abs(y - center)
    wrapped = np.minimum(direct, 1.0 - direct)
    mirrored = np.abs(y - (1.0 - center))
    return np.minimum(wrapped, mirrored)


def _sampled_normalized_profile(loc: Localization, n_points: int = 4001) -> Tuple[np.ndarray, np.ndarray]:
    if n_points <= 1:
        raise ValueError("n_points must be > 1 for overlap integration")
    y = np.linspace(0.0, 1.0, n_points)
    width = max(loc.width, 1e-12)
    d = _orbifold_distance_array(y, loc.center)
    psi = np.exp(-0.5 * (d / width) ** 2)
    norm = float(np.sqrt(max(np.trapezoid(psi * psi, y), 1e-16)))
    return y, psi / norm


def zero_mode_overlap(loc_l: Localization, loc_r: Localization, n_points: int = 4001) -> float:
    """Numerically integrate overlap ∫ ψ_L ψ_R dy on [0,1]."""
    if n_points <= 1:
        raise ValueError("n_points must be > 1 for overlap integration")
    y_l, psi_l = _sampled_normalized_profile(loc_l, n_points=n_points)
    y_r, psi_r = _sampled_normalized_profile(loc_r, n_points=n_points)
    if not np.allclose(y_l, y_r):
        raise ValueError("profile grids must match for overlap integration")
    return float(np.trapezoid(psi_l * psi_r, y_l))


def yukawa_matrix_three_sector() -> Dict[str, object]:
    """Build a 3×3 geometric Yukawa texture from sector-localized overlaps."""
    loc = default_sector_localization()
    sectors = ("uv", "bulk", "ir")
    profiles = {s: _sampled_normalized_profile(loc[s], n_points=4001) for s in sectors}
    matrix = [[0.0 for _ in range(3)] for _ in range(3)]
    for i in range(3):
        for j in range(i, 3):
            y_i, psi_i = profiles[sectors[i]]
            y_j, psi_j = profiles[sectors[j]]
            if not np.allclose(y_i, y_j):
                raise ValueError("profile grids must match for overlap integration")
            value = float(np.trapezoid(psi_i * psi_j, y_i))
            matrix[i][j] = value
            matrix[j][i] = value
    return {
        "matrix": matrix,
        "status": "DERIVED",
        "epistemic_note": (
            "Geometric overlap texture is derived from fixed sector localization; "
            "mapping to physical masses remains FITTED unless electroweak and RG "
            "normalization are closed with no external calibration."
        ),
    }


def hierarchy_ratios_from_texture(matrix: list[list[float]] | None = None) -> Dict[str, float]:
    """Return hierarchy ratios from singular values of the full texture."""
    source = matrix if matrix is not None else yukawa_matrix_three_sector()["matrix"]
    m = np.array(source, dtype=float)
    if m.shape != (3, 3):
        raise ValueError(f"Expected a 3x3 Yukawa texture, got shape {m.shape}.")
    singular_values = np.linalg.svd(m, compute_uv=False)
    s1, s2, s3 = sorted(float(v) for v in singular_values)
    eps = 1e-16
    return {
        "mode2_over_mode1": s2 / max(s1, eps),
        "mode3_over_mode2": s3 / max(s2, eps),
        "mode3_over_mode1": s3 / max(s1, eps),
    }


def yukawa_geometric_report() -> Dict[str, object]:
    """Return complete three-sector Yukawa report."""
    tex = yukawa_matrix_three_sector()
    ratios = hierarchy_ratios_from_texture(tex["matrix"])
    return {
        "inputs": {"n_w": N_W, "n_parent": N_PARENT, "n_shadow": N_SHADOW, "PI_KR": PI_KR},
        "texture": tex,
        "hierarchy_ratios": ratios,
        "status": "FITTED",
        "epistemic_note": (
            "Texture-level derivation is complete; full SM mass hierarchy closure "
            "still needs non-fitted RG + Higgs-sector normalization."
        ),
    }
