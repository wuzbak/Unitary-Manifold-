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
    z = (y - loc.center) / max(loc.width, 1e-12)
    return math.exp(-0.5 * z * z)


def zero_mode_overlap(loc_l: Localization, loc_r: Localization, n_points: int = 4001) -> float:
    """Numerically integrate overlap ∫ ψ_L ψ_R dy on [0,1]."""
    step = 1.0 / (n_points - 1)
    acc = 0.0
    for i in range(n_points):
        y = i * step
        acc += _gaussian(y, loc_l) * _gaussian(y, loc_r)
    return acc * step


def yukawa_matrix_three_sector() -> Dict[str, object]:
    """Build a 3×3 geometric Yukawa texture from sector-localized overlaps."""
    loc = default_sector_localization()
    left = (loc["uv"], loc["bulk"], loc["ir"])
    right = (loc["uv"], loc["bulk"], loc["ir"])
    matrix = []
    for li in left:
        row = []
        for rj in right:
            row.append(zero_mode_overlap(li, rj))
        matrix.append(row)
    return {
        "matrix": matrix,
        "status": "DERIVED",
        "epistemic_note": (
            "Geometric overlap texture is derived from fixed sector localization; "
            "mapping to physical masses remains FITTED unless electroweak and RG "
            "normalization are closed with no external calibration."
        ),
    }


def hierarchy_ratios_from_texture() -> Dict[str, float]:
    """Return simple hierarchy ratios from diagonal overlaps."""
    m = yukawa_matrix_three_sector()["matrix"]
    d1, d2, d3 = m[0][0], m[1][1], m[2][2]
    eps = 1e-16
    return {
        "gen2_over_gen1": d2 / max(d1, eps),
        "gen3_over_gen2": d3 / max(d2, eps),
        "gen3_over_gen1": d3 / max(d1, eps),
    }


def yukawa_geometric_report() -> Dict[str, object]:
    """Return complete three-sector Yukawa report."""
    tex = yukawa_matrix_three_sector()
    ratios = hierarchy_ratios_from_texture()
    return {
        "inputs": {"n_w": N_W, "n_parent": N_PARENT, "n_shadow": N_SHADOW, "pi_kR": PI_KR},
        "texture": tex,
        "hierarchy_ratios": ratios,
        "status": "FITTED",
        "epistemic_note": (
            "Texture-level derivation is complete; full SM mass hierarchy closure "
            "still needs non-fitted RG + Higgs-sector normalization."
        ),
    }

