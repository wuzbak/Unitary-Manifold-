# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 865 — ALPHA_S_7D_VOLUME_NARROWED

Strong coupling from the Green-Schwarz tadpole condition on T².

Geometry
--------
The GS tadpole condition of the 9D→7D reduction (Pillar 849) reads

    N_flux · Vol(T²) = k_CS · l_s²,

so with the minimal non-zero flux N_flux = 1 and k_CS = 74,

    Vol(T²) = 74 l_s²   ⟹   ρ_K ≡ Vol(T²)/l_s² = 74.

The Kähler modulus is therefore *not* a free parameter.  Reducing the 7D gauge
kinetic term on T² and then on S¹/Z₂ gives

    α_s(M_KK) = 4π / (ρ_K · (M₇ / M_KK)),

which is run down to M_Z at one loop with b₀ = 11 − 2n_f/3 = 7 (n_f = 6).

Result
------
At the minimal identification M₇ = M_KK the prediction is

    α_s(M_Z) ≈ 0.1162,

which is ≈ 1.6σ from the PDG value 0.1179 ± 0.0010.

Honest status
-------------
NARROWED, not pinned.  The Kähler modulus is fixed by the tadpole, but the 7D
fundamental scale M₇ is not, and a scan over M₇/M_KK ∈ [0.5, 2] spans
α_s(M_Z) ∈ [0.069, 0.177].  That residual is registered as an architecture
limit rather than hidden.
"""
from __future__ import annotations

import math
from typing import Any

PILLAR_NUMBER: int = 865
PILLAR_GATE: str = "ALPHA_S_7D_VOLUME_NARROWED"

LEAN4_THEOREM_COUNT: int = 30
LEAN4_TOTAL_BEFORE: int = 2296
LEAN4_TOTAL_AFTER: int = LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT

K_CS: int = 74
N_FLUX: int = 1
KAHLER_MODULUS_RHO: float = float(K_CS) / N_FLUX
VOL_T2_OVER_LS2: float = KAHLER_MODULUS_RHO

M_KK_GEV: float = 1042.0
M_Z_GEV: float = 91.2
N_F: int = 6
B0_QCD: float = 11.0 - 2.0 * N_F / 3.0

M7_OVER_MKK_CANONICAL: float = 1.0
M7_SCAN: tuple[float, ...] = (0.5, 0.75, 1.0, 1.5, 2.0)

ALPHA_S_PDG: float = 0.1179
ALPHA_S_PDG_ERR: float = 0.0010

REMAINING_OPEN: list[str] = [
    "ALPHA_S_7D_M7_SCALE_OPEN: the 7D fundamental scale M₇ is not fixed by the "
    "tadpole condition; only the ratio M₇/M_KK enters and it is not derived.",
    "ALPHA_S_7D_TWO_LOOP_OPEN: the running is one-loop only.",
]

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_BEFORE",
    "LEAN4_TOTAL_AFTER",
    "K_CS",
    "N_FLUX",
    "KAHLER_MODULUS_RHO",
    "VOL_T2_OVER_LS2",
    "M_KK_GEV",
    "M_Z_GEV",
    "B0_QCD",
    "M7_OVER_MKK_CANONICAL",
    "M7_SCAN",
    "ALPHA_S_PDG",
    "ALPHA_S_PDG_ERR",
    "ALPHA_S_MZ_CENTRAL",
    "ALPHA_S_MZ_INTERVAL",
    "TENSION_SIGMA",
    "PDG_INSIDE_INTERVAL",
    "REMAINING_OPEN",
    "gs_tadpole_volume",
    "kahler_modulus",
    "alpha_s_at_mkk",
    "run_alpha_s_to_mz",
    "alpha_s_mz",
    "volume_scan",
    "alphas_kahler_summary",
]


def gs_tadpole_volume(n_flux: int = N_FLUX, k_cs: int = K_CS) -> float:
    """Return Vol(T²)/l_s² = k_CS / N_flux from the GS tadpole condition."""
    if n_flux <= 0:
        raise ValueError("n_flux must be positive")
    if k_cs <= 0:
        raise ValueError("k_cs must be positive")
    return float(k_cs) / n_flux


def kahler_modulus(n_flux: int = N_FLUX, k_cs: int = K_CS) -> float:
    """Return the Kähler modulus ρ_K = Vol(T²)/l_s²."""
    return gs_tadpole_volume(n_flux=n_flux, k_cs=k_cs)


def alpha_s_at_mkk(
    m7_over_mkk: float = M7_OVER_MKK_CANONICAL,
    rho_k: float = KAHLER_MODULUS_RHO,
) -> float:
    """Return α_s(M_KK) = 4π / (ρ_K · (M₇/M_KK))."""
    if m7_over_mkk <= 0.0:
        raise ValueError("m7_over_mkk must be positive")
    if rho_k <= 0.0:
        raise ValueError("rho_k must be positive")
    return 4.0 * math.pi / (rho_k * m7_over_mkk)


def run_alpha_s_to_mz(
    alpha_high: float,
    m_high: float = M_KK_GEV,
    m_low: float = M_Z_GEV,
    b0: float = B0_QCD,
) -> float:
    """Run α_s down from m_high to m_low at one loop."""
    if alpha_high <= 0.0:
        raise ValueError("alpha_high must be positive")
    if m_high <= m_low:
        raise ValueError("m_high must exceed m_low")
    denominator = 1.0 + (alpha_high / (2.0 * math.pi)) * b0 * math.log(m_high / m_low)
    return alpha_high / denominator


def alpha_s_mz(m7_over_mkk: float = M7_OVER_MKK_CANONICAL) -> float:
    """Return α_s(M_Z) for a given M₇/M_KK ratio."""
    return run_alpha_s_to_mz(alpha_s_at_mkk(m7_over_mkk))


def volume_scan(ratios: tuple[float, ...] = M7_SCAN) -> list[dict[str, float]]:
    """Return an honest scan over the undetermined M₇/M_KK ratio."""
    return [
        {
            "m7_over_mkk": r,
            "alpha_s_mkk": alpha_s_at_mkk(r),
            "alpha_s_mz": alpha_s_mz(r),
        }
        for r in ratios
    ]


ALPHA_S_MKK_CENTRAL: float = alpha_s_at_mkk()
ALPHA_S_MZ_CENTRAL: float = alpha_s_mz()
_SCAN: list[dict[str, float]] = volume_scan()
ALPHA_S_MZ_INTERVAL: tuple[float, float] = (
    min(row["alpha_s_mz"] for row in _SCAN),
    max(row["alpha_s_mz"] for row in _SCAN),
)
TENSION_SIGMA: float = abs(ALPHA_S_MZ_CENTRAL - ALPHA_S_PDG) / ALPHA_S_PDG_ERR
PDG_INSIDE_INTERVAL: bool = ALPHA_S_MZ_INTERVAL[0] <= ALPHA_S_PDG <= ALPHA_S_MZ_INTERVAL[1]
CENTRAL_WITHIN_2SIGMA: bool = TENSION_SIGMA <= 2.0


def alphas_kahler_summary() -> dict[str, Any]:
    """Return the machine-readable GS-tadpole α_s certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "n_flux": N_FLUX,
        "k_cs": K_CS,
        "kahler_modulus_rho": KAHLER_MODULUS_RHO,
        "vol_t2_over_ls2": VOL_T2_OVER_LS2,
        "m_kk_gev": M_KK_GEV,
        "m_z_gev": M_Z_GEV,
        "b0_qcd": B0_QCD,
        "m7_over_mkk_canonical": M7_OVER_MKK_CANONICAL,
        "alpha_s_mkk_central": ALPHA_S_MKK_CENTRAL,
        "alpha_s_mz_central": ALPHA_S_MZ_CENTRAL,
        "alpha_s_mz_interval": list(ALPHA_S_MZ_INTERVAL),
        "alpha_s_pdg": ALPHA_S_PDG,
        "alpha_s_pdg_err": ALPHA_S_PDG_ERR,
        "tension_sigma": TENSION_SIGMA,
        "central_within_2sigma": CENTRAL_WITHIN_2SIGMA,
        "pdg_inside_interval": PDG_INSIDE_INTERVAL,
        "scan": _SCAN,
        "epistemic_status": (
            "NARROWED: the Kähler modulus is pinned to ρ_K = 74 by the GS tadpole, "
            "but M₇ is not fixed, so α_s is narrowed to a band rather than derived."
        ),
        "remaining_open": REMAINING_OPEN,
        "lean4_theorem_count": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }
