# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 871 — HIGGS_6D_UV_COMPLETION_ARCHITECTURE_LIMIT

Strong-coupling audit of the one-loop Hosotani potential of Pillar 838.

The Wilson-line (Hosotani) potential is calculable at one loop, but the 6D
gauge theory is non-renormalisable and becomes strongly coupled at the naive
dimensional-analysis (NDA) cutoff

    Λ_NDA / M_KK = 4π / g   ≈ 19.3   for g = 0.65,

which admits N_KK = ⌊Λ_NDA/M_KK⌋ = 19 KK levels below the cutoff.  The
relative size of the leading uncalculable correction to the Higgs mass is
bounded by the NDA loop factor times the first-shell orbifold degeneracy,

    |δm_H / m_H| ≈ g² N_shell / (16π²) ≈ 1.61%,

comfortably below the certified envelope of 5%.

Honest status
-------------
ARCHITECTURE_LIMIT.  The bound says the one-loop Hosotani estimate is stable
to better than 5%; it does *not* supply the exact Higgs mass, because that
requires the non-perturbative UV completion (exact R₆ and g₆).  The limit is
certified as NON_PERTURBATIVE_ARCHITECTURE_LIMIT_6D rather than closed.
"""
from __future__ import annotations

import math
from typing import Any

from src.core.pillar838_6d_hosotani_higgs_mass import (
    FIRST_SHELL_DEGENERACY,
    G_SU2_EFFECTIVE,
    M_H_HOSOTANI_GEV,
    M_H_PDG_GEV,
    M_KK_GEV,
)

PILLAR_NUMBER: int = 871
PILLAR_GATE: str = "HIGGS_6D_UV_COMPLETION_ARCHITECTURE_LIMIT"
LIMIT_CERTIFICATE: str = "NON_PERTURBATIVE_ARCHITECTURE_LIMIT_6D"

LEAN4_THEOREM_COUNT: int = 20
LEAN4_TOTAL_BEFORE: int = 2431
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

BOUND_FRACTION: float = 0.05

REMAINING_OPEN: list[str] = [
    "HIGGS_6D_UV_COMPLETION_OPEN: exact R₆ and g₆ require the 10D/11D UV completion.",
    "HIGGS_6D_NONPERTURBATIVE_POTENTIAL_OPEN: the Hosotani potential above "
    "Λ_NDA is not computable in the 6D effective description.",
    "HIGGS_6D_PDG_OFFSET_OPEN: the NDA band around the one-loop estimate does "
    "not reach m_H^PDG = 125.25 GeV, so the residual offset is UV physics, not "
    "a loop uncertainty.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LIMIT_CERTIFICATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "BOUND_FRACTION",
    "NDA_CUTOFF_OVER_MKK",
    "N_KK_BELOW_CUTOFF",
    "DELTA_MH_OVER_MH",
    "DELTA_MH_GEV",
    "BOUND_SATISFIED",
    "REMAINING_OPEN",
    "nda_cutoff_ratio",
    "kk_levels_below_cutoff",
    "one_loop_relative_shift",
    "higgs_mass_band_gev",
    "higgs_uv_completion_limit_summary",
]


def nda_cutoff_ratio(g: float = G_SU2_EFFECTIVE) -> float:
    """Return the NDA strong-coupling cutoff in units of M_KK: 4π/g."""
    if g <= 0.0:
        raise ValueError("g must be positive")
    return 4.0 * math.pi / g


def kk_levels_below_cutoff(g: float = G_SU2_EFFECTIVE) -> int:
    """Return the number of KK levels below the NDA cutoff."""
    return int(math.floor(nda_cutoff_ratio(g)))


def one_loop_relative_shift(
    g: float = G_SU2_EFFECTIVE,
    n_shell: int = FIRST_SHELL_DEGENERACY,
) -> float:
    """Return the NDA bound |δm_H/m_H| ≈ g² N_shell / (16π²)."""
    if g <= 0.0:
        raise ValueError("g must be positive")
    if n_shell <= 0:
        raise ValueError("n_shell must be positive")
    return g * g * n_shell / (16.0 * math.pi**2)


def higgs_mass_band_gev(
    m_h: float = M_H_HOSOTANI_GEV,
    relative_shift: float | None = None,
) -> tuple[float, float]:
    """Return the NDA-bounded Higgs mass band around the Hosotani estimate."""
    delta = one_loop_relative_shift() if relative_shift is None else relative_shift
    return (m_h * (1.0 - delta), m_h * (1.0 + delta))


NDA_CUTOFF_OVER_MKK: float = nda_cutoff_ratio()
N_KK_BELOW_CUTOFF: int = kk_levels_below_cutoff()
DELTA_MH_OVER_MH: float = one_loop_relative_shift()
DELTA_MH_GEV: float = DELTA_MH_OVER_MH * M_H_HOSOTANI_GEV
HIGGS_BAND_GEV: tuple[float, float] = higgs_mass_band_gev()
BOUND_SATISFIED: bool = DELTA_MH_OVER_MH < BOUND_FRACTION
PDG_INSIDE_BAND: bool = HIGGS_BAND_GEV[0] <= M_H_PDG_GEV <= HIGGS_BAND_GEV[1]


def higgs_uv_completion_limit_summary() -> dict[str, Any]:
    """Return the machine-readable 6D Higgs UV architecture-limit certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "limit_certificate": LIMIT_CERTIFICATE,
        "g_su2_effective": G_SU2_EFFECTIVE,
        "first_shell_degeneracy": FIRST_SHELL_DEGENERACY,
        "m_kk_gev": M_KK_GEV,
        "nda_cutoff_over_mkk": NDA_CUTOFF_OVER_MKK,
        "n_kk_below_cutoff": N_KK_BELOW_CUTOFF,
        "delta_mh_over_mh": DELTA_MH_OVER_MH,
        "delta_mh_percent": DELTA_MH_OVER_MH * 100.0,
        "delta_mh_gev": DELTA_MH_GEV,
        "bound_fraction": BOUND_FRACTION,
        "bound_satisfied": BOUND_SATISFIED,
        "m_h_hosotani_gev": M_H_HOSOTANI_GEV,
        "m_h_pdg_gev": M_H_PDG_GEV,
        "higgs_band_gev": list(HIGGS_BAND_GEV),
        "pdg_inside_band": PDG_INSIDE_BAND,
        "epistemic_status": (
            "ARCHITECTURE_LIMIT: the one-loop Hosotani estimate is NDA-stable to "
            "better than 5%, but the exact Higgs mass needs the non-perturbative "
            "UV completion and is not supplied here."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
