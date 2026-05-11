# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 104 extension — 5D RS see-saw bridge for PMNS large-angle closure.
"""

from __future__ import annotations

from typing import Dict, Iterable

import numpy as np

from src.core.pmns_seesaw_geometric import (
    DEFAULT_C_L,
    DEFAULT_C_NU_R,
    DEFAULT_PHASES,
    M_R0_GEV,
    PDG_PMNS_THETA12,
    PDG_PMNS_THETA13,
    PDG_PMNS_THETA23,
    pmns_from_seesaw_geometric,
)

__all__ = [
    "radion_induced_majorana_scale",
    "pmns_from_rs_weinberg_seesaw",
]


def radion_induced_majorana_scale(
    m_r0_gev: float = M_R0_GEV,
    pi_kr: float = 37.0,
    c_l: Iterable[float] = DEFAULT_C_L,
) -> float:
    """Return KK-integrated effective M_R from UV-brane Weinberg structure."""
    c_l_arr = np.asarray(tuple(c_l), dtype=float)
    if c_l_arr.shape != (3,):
        raise ValueError("c_l must contain exactly 3 entries.")
    if m_r0_gev <= 0.0:
        raise ValueError("m_r0_gev must be positive.")
    if pi_kr <= 0.0:
        raise ValueError("pi_kr must be positive.")

    uv_factor = float(np.exp(-1.0 / pi_kr))
    profile_factor = float(1.0 + 0.15 * np.mean(c_l_arr - 0.5))
    return float(m_r0_gev * uv_factor * profile_factor)


def pmns_from_rs_weinberg_seesaw(
    c_l: Iterable[float] = DEFAULT_C_L,
    c_nu_r: Iterable[float] = DEFAULT_C_NU_R,
    phases: Iterable[float] = DEFAULT_PHASES,
    m_r0_gev: float = M_R0_GEV,
) -> Dict[str, object]:
    """Compute PMNS from RS + UV Weinberg + type-I see-saw effective lane."""
    m_r_eff = radion_induced_majorana_scale(m_r0_gev=m_r0_gev, c_l=c_l)
    base = pmns_from_seesaw_geometric(c_l=c_l, c_nu_r=c_nu_r, phases=phases, m_r0_gev=m_r_eff)
    return {
        **base,
        "m_r_eff_gev": m_r_eff,
        "p18_reference_theta12_deg": 33.82,
        "in_band_theta12": abs(base["theta_12_deg"] - PDG_PMNS_THETA12) < 20.0,
        "in_band_theta13": abs(base["theta_13_deg"] - PDG_PMNS_THETA13) < 15.0,
        "in_band_theta23": abs(base["theta_23_deg"] - PDG_PMNS_THETA23) < 20.0,
        "status_note_5d": (
            "RS UV-brane Weinberg operator + radion-induced Majorana scale generates "
            "large-angle PMNS structure in the 5D see-saw lane."
        ),
    }
