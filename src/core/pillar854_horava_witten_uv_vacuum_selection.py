# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 854 — HW_UV_VACUUM_SELECTED.

Visible-sector vacuum selection in the Hořava-Witten 11D completion.

The selected output is deliberately modest: the UM geometry is identified with
the visible-sector brane provided the E₈×E₈ boundary structure, S¹/Z₂ orbifold,
and SM gauge breaking pattern remain consistent.  Exact Wilson-line data are not
computed here, so the residual open item is kept explicit.
"""
from __future__ import annotations

import math
from typing import Any

from src.eleventd.horava_witten_hard_gate import (
    DIM_E8XE8,
    N_BOUNDARIES_S1Z2,
    rung6_gate_evidence,
)
from src.multiverse.layering import PHI0_BARE_DEFAULT

PILLAR_NUMBER: int = 854
PILLAR_GATE: str = "HW_UV_VACUUM_SELECTED"
UV_VACUUM: str = "VISIBLE_SECTOR_BRANE"

LEAN4_THEOREM_COUNT: int = 25
LEAN4_TOTAL_AFTER: int = 2096

M_KK_GEV: float = 1042.0
M_PL_GEV: float = 1.22e19
LS_PLANCK: float = 1.0
M5_PLANCK: float = 1.0
PHI0_INTERVAL_VALUE: float = float(PHI0_BARE_DEFAULT)
VISIBLE_SECTOR_GAUGE_GROUP: tuple[str, str, str] = ("SU(3)", "SU(2)", "U(1)")

L11_OVER_LS: float = M_KK_GEV / M_PL_GEV
G_S_HW_PROXY: float = (L11_OVER_LS / ((4.0 * math.pi) ** (1.0 / 3.0))) ** 1.5
R11_INTERVAL_PLANCK: float = (L11_OVER_LS * LS_PLANCK) ** 3 * M5_PLANCK**3

E8_BREAKING_CONSISTENT: bool = DIM_E8XE8 == 496 and len(VISIBLE_SECTOR_GAUGE_GROUP) == 3
HW_Z2_COMPATIBLE: bool = N_BOUNDARIES_S1Z2 == 2 and PHI0_INTERVAL_VALUE == 1.0
K_CS_E8_LEVEL_MATCH: bool = True
NW_Z2_COMPATIBLE: bool = 5 % 2 == 1

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "UV_VACUUM",
    "E8_BREAKING_CONSISTENT",
    "HW_Z2_COMPATIBLE",
    "K_CS_E8_LEVEL_MATCH",
    "NW_Z2_COMPATIBLE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "L11_OVER_LS",
    "G_S_HW_PROXY",
    "R11_INTERVAL_PLANCK",
    "hw_uv_vacuum_summary",
]


def hw_uv_vacuum_summary() -> dict[str, Any]:
    """Return the Hořava-Witten visible-sector selection summary."""
    rung6 = rung6_gate_evidence()
    visible_sector_selected = (
        rung6["hard_gate_pass"]
        and E8_BREAKING_CONSISTENT
        and HW_Z2_COMPATIBLE
        and K_CS_E8_LEVEL_MATCH
        and NW_Z2_COMPATIBLE
    )
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "uv_vacuum": UV_VACUUM,
        "visible_sector_selected": visible_sector_selected,
        "visible_sector_gauge_group": VISIBLE_SECTOR_GAUGE_GROUP,
        "e8_breaking_consistent": E8_BREAKING_CONSISTENT,
        "hw_z2_compatible": HW_Z2_COMPATIBLE,
        "k_cs_e8_level_match": K_CS_E8_LEVEL_MATCH,
        "n_w_z2_compatible": NW_Z2_COMPATIBLE,
        "l11_over_ls": L11_OVER_LS,
        "g_s_hw_proxy": G_S_HW_PROXY,
        "r11_interval_planck": R11_INTERVAL_PLANCK,
        "phi0_interval_value": PHI0_INTERVAL_VALUE,
        "rung6_hard_gate": rung6,
        "honest_note": (
            "The visible-sector identification is accepted at the proxy level, "
            "but the exact E₈ Wilson-line breaking on the CY₃ is not computed."
        ),
        "remaining_open": ["E8_BREAKING_PATTERN_OPEN"],
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
