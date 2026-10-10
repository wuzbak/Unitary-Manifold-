# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Feature 4: general-purpose, dependency-free SVG chart creation.

Deliberately distinct from Product 17 (`um-image-generator`), which
renders UM-physics-specific plots. This module takes arbitrary labelled
numeric data and produces a self-contained SVG string -- no numpy,
matplotlib, or network access required, so PsiCat can create a chart for
any Q/A, registry, or dashboard data it already has in hand.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence

_PALETTE = (
    "#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2",
    "#937860", "#DA8BC3", "#8C8C8C", "#CCB974", "#64B5CD",
)


class ChartInputError(ValueError):
    """Raised when labels/values are empty, mismatched, or non-numeric."""


def _validate(labels: Sequence[str], values: Sequence[float]) -> None:
    if not labels or not values:
        raise ChartInputError("labels and values must both be non-empty")
    if len(labels) != len(values):
        raise ChartInputError(f"labels ({len(labels)}) and values ({len(values)}) length mismatch")
    for value in values:
        float(value)  # raises TypeError/ValueError for non-numeric input


def _svg_header(width: int, height: int, title: str) -> List[str]:
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
             f'viewBox="0 0 {width} {height}" font-family="sans-serif">']
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="white" />')
    if title:
        parts.append(f'<text x="{width / 2}" y="22" text-anchor="middle" font-size="16" '
                      f'font-weight="bold">{_escape(title)}</text>')
    return parts


def _escape(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def create_bar_chart_svg(
    labels: Sequence[str],
    values: Sequence[float],
    width: int = 640,
    height: int = 400,
    title: str = "",
) -> str:
    _validate(labels, values)
    margin_top = 50 if title else 20
    margin_bottom = 60
    margin_side = 40
    plot_width = width - 2 * margin_side
    plot_height = height - margin_top - margin_bottom
    max_value = max(float(value) for value in values) or 1.0
    bar_width = plot_width / len(values) * 0.7
    gap = plot_width / len(values) * 0.3

    parts = _svg_header(width, height, title)
    parts.append(f'<line x1="{margin_side}" y1="{margin_top + plot_height}" '
                  f'x2="{width - margin_side}" y2="{margin_top + plot_height}" stroke="black" />')
    for index, (label, value) in enumerate(zip(labels, values)):
        value_f = float(value)
        bar_height = (value_f / max_value) * plot_height
        x = margin_side + index * (bar_width + gap) + gap / 2
        y = margin_top + plot_height - bar_height
        color = _PALETTE[index % len(_PALETTE)]
        parts.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{bar_width:.2f}" height="{bar_height:.2f}" '
                      f'fill="{color}" />')
        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{y - 4:.2f}" text-anchor="middle" '
                      f'font-size="11">{_escape(round(value_f, 3))}</text>')
        parts.append(f'<text x="{x + bar_width / 2:.2f}" y="{margin_top + plot_height + 16:.2f}" '
                      f'text-anchor="middle" font-size="11">{_escape(label)}</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def create_line_chart_svg(
    x_values: Sequence[float],
    y_values: Sequence[float],
    width: int = 640,
    height: int = 400,
    title: str = "",
) -> str:
    _validate(x_values, y_values)
    margin_top = 50 if title else 20
    margin_bottom = 40
    margin_side = 40
    plot_width = width - 2 * margin_side
    plot_height = height - margin_top - margin_bottom

    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = min(y_values), max(y_values)
    x_span = (x_max - x_min) or 1.0
    y_span = (y_max - y_min) or 1.0

    def _scale(x: float, y: float) -> tuple:
        px = margin_side + (float(x) - x_min) / x_span * plot_width
        py = margin_top + plot_height - (float(y) - y_min) / y_span * plot_height
        return px, py

    points = [_scale(x, y) for x, y in zip(x_values, y_values)]
    path = " ".join(f"{px:.2f},{py:.2f}" for px, py in points)

    parts = _svg_header(width, height, title)
    parts.append(f'<polyline fill="none" stroke="{_PALETTE[0]}" stroke-width="2" points="{path}" />')
    for px, py in points:
        parts.append(f'<circle cx="{px:.2f}" cy="{py:.2f}" r="3" fill="{_PALETTE[0]}" />')
    parts.append("</svg>")
    return "\n".join(parts)


def create_pie_chart_svg(
    labels: Sequence[str],
    values: Sequence[float],
    width: int = 480,
    height: int = 480,
    title: str = "",
) -> str:
    _validate(labels, values)
    total = sum(float(value) for value in values)
    if total <= 0:
        raise ChartInputError("pie chart values must sum to a positive total")

    margin_top = 50 if title else 20
    cx, cy = width / 2, margin_top + (height - margin_top - 60) / 2
    radius = min(width, height - margin_top - 60) / 2 - 10

    parts = _svg_header(width, height, title)
    angle = -90.0
    import math

    for index, (label, value) in enumerate(zip(labels, values)):
        fraction = float(value) / total
        sweep = fraction * 360.0
        start_rad = math.radians(angle)
        end_rad = math.radians(angle + sweep)
        x1 = cx + radius * math.cos(start_rad)
        y1 = cy + radius * math.sin(start_rad)
        x2 = cx + radius * math.cos(end_rad)
        y2 = cy + radius * math.sin(end_rad)
        large_arc = 1 if sweep > 180 else 0
        color = _PALETTE[index % len(_PALETTE)]
        parts.append(
            f'<path d="M {cx:.2f},{cy:.2f} L {x1:.2f},{y1:.2f} '
            f'A {radius:.2f},{radius:.2f} 0 {large_arc} 1 {x2:.2f},{y2:.2f} Z" fill="{color}" />'
        )
        mid_rad = math.radians(angle + sweep / 2)
        label_x = cx + (radius + 14) * math.cos(mid_rad)
        label_y = cy + (radius + 14) * math.sin(mid_rad)
        parts.append(f'<text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="middle" '
                      f'font-size="11">{_escape(label)} ({fraction * 100:.1f}%)</text>')
        angle += sweep
    parts.append("</svg>")
    return "\n".join(parts)
