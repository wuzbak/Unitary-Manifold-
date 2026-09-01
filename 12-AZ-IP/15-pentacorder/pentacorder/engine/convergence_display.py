# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""ASCII display helpers for Pentacorder convergence readouts."""

from __future__ import annotations


def get_alert_level(ci: float) -> str:
    """Map convergence index to a compact alert label."""
    ci = float(ci)
    if ci >= 0.8:
        return "NOMINAL"
    if ci >= 0.6:
        return "ELEVATED"
    if ci >= 0.4:
        return "ALERT"
    return "CRITICAL"


def format_5d_display(state: dict, ci: float) -> str:
    """Render a compact ASCII display for the 5D state vector."""
    dims = state.get("dimensions", {})
    alert = get_alert_level(ci)
    lines = [
        "Unitary Pentacorder 5D Display",
        f"dim_1_x        : {dims.get('dim_1_x', 0.0):.4f}",
        f"dim_2_y        : {dims.get('dim_2_y', 0.0):.4f}",
        f"dim_3_z        : {dims.get('dim_3_z', 0.0):.4f}",
        f"dim_4_t        : {dims.get('dim_4_t', 0.0):.4f}",
        f"dim_5_compact  : {dims.get('dim_5_compact', 0.0):.4f}",
        f"CI             : {float(ci):.4f}",
        f"Alert          : {alert}",
    ]
    return "\n".join(lines)
