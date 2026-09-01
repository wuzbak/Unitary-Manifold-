# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""ASCII/SVG Yukawa-style mass-hierarchy helpers."""

from __future__ import annotations

import math
from pathlib import Path

PHI = (1 + math.sqrt(5)) / 2
_QUARK_LABELS = ['u', 'd', 's', 'c', 'b', 't']
_LEPTON_LABELS = ['νe', 'νμ', 'ντ', 'e', 'μ', 'τ']
_QUARK_MASSES_MEV = [2.2, 4.7, 96.0, 1270.0, 4180.0, 173100.0]
_LEPTON_MASSES_MEV = [0.0000022, 0.0086, 0.05, 0.511, 105.66, 1776.86]
_PALETTE = ' .:-=+*#%@'


def _phi_scaled_log_ratio(a: float, b: float) -> float:
    ratio = max(a, 1e-12) / max(b, 1e-12)
    return abs(math.log(ratio, PHI))


def compute_mass_hierarchy(n_quarks=6, n_leptons=6) -> dict:
    """Return a phi-normalized pairwise mass-ratio matrix."""
    nq = max(1, min(int(n_quarks), len(_QUARK_LABELS)))
    nl = max(1, min(int(n_leptons), len(_LEPTON_LABELS)))
    labels = _QUARK_LABELS[:nq] + _LEPTON_LABELS[:nl]
    masses = _QUARK_MASSES_MEV[:nq] + _LEPTON_MASSES_MEV[:nl]
    matrix: list[list[float]] = []
    for mass_a in masses:
        row = []
        for mass_b in masses:
            row.append(_phi_scaled_log_ratio(mass_a, mass_b))
        matrix.append(row)
    return {
        'phi': PHI,
        'labels': labels,
        'masses_mev': masses,
        'matrix': matrix,
        'quark_count': nq,
        'lepton_count': nl,
    }


def render_heatmap_ascii(matrix: list) -> str:
    """Render a small numeric matrix as an ASCII heatmap."""
    if not matrix:
        return ''
    flat = [float(value) for row in matrix for value in row]
    vmax = max(flat) if flat else 1.0
    if vmax <= 0:
        vmax = 1.0
    lines = []
    for row in matrix:
        chars = []
        for value in row:
            idx = min(len(_PALETTE) - 1, int(round((float(value) / vmax) * (len(_PALETTE) - 1))))
            chars.append(_PALETTE[idx])
        lines.append(''.join(chars))
    return '\n'.join(lines)


def export_svg_heatmap(matrix: list, filepath: str) -> None:
    """Write a minimal SVG heatmap to ``filepath``."""
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = len(matrix)
    cols = len(matrix[0]) if rows else 0
    cell = 18
    flat = [float(value) for row in matrix for value in row]
    vmax = max(flat) if flat else 1.0
    if vmax <= 0:
        vmax = 1.0
    rects = []
    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            shade = 255 - int((float(value) / vmax) * 200)
            rects.append(
                f'<rect x="{c * cell}" y="{r * cell}" width="{cell}" height="{cell}" fill="rgb({shade},{shade},{shade})" />'
            )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols * cell}" height="{rows * cell}" '
        f'viewBox="0 0 {cols * cell} {rows * cell}">' + ''.join(rects) + '</svg>'
    )
    path.write_text(svg, encoding='utf-8')
