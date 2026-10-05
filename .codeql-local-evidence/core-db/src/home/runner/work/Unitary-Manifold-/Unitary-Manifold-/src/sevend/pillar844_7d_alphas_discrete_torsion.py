# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 844 — ALPHA_S_7D_TORSION_ROUTE_D_PARTIAL

7D discrete-torsion Route D proxy for the strong coupling.

Honest status
-------------
This route is TYPE_B / PARTIAL.  The 7D torsion geometry fixes the structural
form of the coupling, but the exact torus-to-orbifold volume ratio is not yet
uniquely derived.  We therefore expose a canonical central representative and
leave the exact R₆/R₅ ratio as an open item.
"""
from __future__ import annotations

import math
from typing import Final

PILLAR_NUMBER: Final[int] = 844
PILLAR_GATE: Final[str] = "ALPHA_S_7D_TORSION_ROUTE_D_PARTIAL"

ALPHA_S_PDG: Final[float] = 0.1179
ALPHA_S_PDG_ERR: Final[float] = 0.0010
M_KK_GEV: Final[float] = 1042.0
M_Z_GEV: Final[float] = 91.2
K_CS_7D: Final[int] = 74
PI_KR: Final[float] = 37.0
N_W: Final[int] = 5
TORSION_ORDER: Final[int] = 3
N_F: Final[int] = 6
B0_QCD: Final[float] = 11.0 - 2.0 * N_F / 3.0

K5_CURVATURE: Final[float] = 1.0
R5_CANONICAL: Final[float] = PI_KR / (math.pi * K5_CURVATURE)
R6_CANONICAL: Final[float] = float(N_W + TORSION_ORDER)

LEAN4_THEOREM_COUNT: Final[int] = 20
LEAN4_TOTAL_AFTER: Final[int] = 1996


def volume_t2_z3(r6: float = R6_CANONICAL) -> float:
    """Return Vol(T²/Z₃) = R₆² (√3/2) / 3."""
    if r6 <= 0.0:
        raise ValueError("r6 must be positive")
    return r6 * r6 * (math.sqrt(3.0) / 2.0) / 3.0


def volume_s1_z2(r5: float = R5_CANONICAL) -> float:
    """Return Vol(S¹/Z₂) = π R₅."""
    if r5 <= 0.0:
        raise ValueError("r5 must be positive")
    return math.pi * r5


def inverse_g3_squared(
    k_cs: int = K_CS_7D,
    r5: float = R5_CANONICAL,
    r6: float = R6_CANONICAL,
) -> float:
    """Return the 7D torsion estimate for 1 / g₃² at M_KK."""
    return (k_cs / (8.0 * math.pi**2)) * (volume_t2_z3(r6) / volume_s1_z2(r5))


def g3_squared_mkk(
    k_cs: int = K_CS_7D,
    r5: float = R5_CANONICAL,
    r6: float = R6_CANONICAL,
) -> float:
    """Return the geometric g₃²(M_KK)."""
    inv_g2 = inverse_g3_squared(k_cs=k_cs, r5=r5, r6=r6)
    return 1.0 / inv_g2


def alpha_s_mkk(
    k_cs: int = K_CS_7D,
    r5: float = R5_CANONICAL,
    r6: float = R6_CANONICAL,
) -> float:
    """Return α_s(M_KK) = g₃² / (4π)."""
    return g3_squared_mkk(k_cs=k_cs, r5=r5, r6=r6) / (4.0 * math.pi)


def run_alpha_s_to_mz(
    alpha_high: float,
    m_high: float = M_KK_GEV,
    m_low: float = M_Z_GEV,
    b0: float = B0_QCD,
) -> float:
    """Run α_s from M_KK to M_Z using the route-D one-loop proxy formula."""
    if alpha_high <= 0.0:
        raise ValueError("alpha_high must be positive")
    if m_high <= m_low:
        raise ValueError("m_high must exceed m_low")
    denominator = 1.0 + (alpha_high / (2.0 * math.pi)) * b0 * math.log(m_high / m_low)
    return alpha_high / denominator


def volume_parameter_scan(r6_values: tuple[float, ...] = (7.0, 8.0, 9.0)) -> list[dict[str, float]]:
    """Return a small honest scan over canonical torsion-cell radii."""
    rows: list[dict[str, float]] = []
    for r6 in r6_values:
        alpha_high = alpha_s_mkk(r6=r6)
        rows.append(
            {
                "r6": r6,
                "alpha_s_mkk": alpha_high,
                "alpha_s_mz": run_alpha_s_to_mz(alpha_high),
            }
        )
    return rows


ALPHA_S_7D_CENTRAL: Final[float] = run_alpha_s_to_mz(alpha_s_mkk())


def alphas_7d_summary() -> dict[str, object]:
    """Return the machine-readable Route-D certificate."""
    scan = volume_parameter_scan()
    residual = abs(ALPHA_S_7D_CENTRAL - ALPHA_S_PDG) / ALPHA_S_PDG
    return {
        "pillar": PILLAR_NUMBER,
        "gate": PILLAR_GATE,
        "k_cs_7d": K_CS_7D,
        "m_kk_gev": M_KK_GEV,
        "m_z_gev": M_Z_GEV,
        "r5_canonical": R5_CANONICAL,
        "r6_canonical": R6_CANONICAL,
        "volumes": {
            "t2_z3": volume_t2_z3(),
            "s1_z2": volume_s1_z2(),
        },
        "g3_squared_mkk": g3_squared_mkk(),
        "alpha_s_mkk": alpha_s_mkk(),
        "alpha_s_mz_central": ALPHA_S_7D_CENTRAL,
        "alpha_s_pdg": ALPHA_S_PDG,
        "alpha_s_pdg_err": ALPHA_S_PDG_ERR,
        "residual_percent": residual * 100.0,
        "in_expected_range": 0.10 <= ALPHA_S_7D_CENTRAL <= 0.13,
        "scan": scan,
        "scan_range_mz": {
            "min": min(row["alpha_s_mz"] for row in scan),
            "max": max(row["alpha_s_mz"] for row in scan),
        },
        "epistemic_status": (
            "PARTIAL / TYPE_B: route form fixed by 7D torsion geometry, "
            "canonical central value depends on unresolved R₆/R₅ volume choice."
        ),
        "remaining_open": [
            "ALPHA_S_7D_VOL_PARAMETER_OPEN: exact R6/R5 ratio not uniquely fixed",
            "ALPHA_S_7D_HIGHER_LOOP_OPEN: one-loop running only in this route-D proxy",
        ],
        "lean4_theorems": LEAN4_THEOREM_COUNT,
        "lean4_total_after": LEAN4_TOTAL_AFTER,
    }


__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_GATE",
    "ALPHA_S_7D_CENTRAL",
    "ALPHA_S_PDG",
    "ALPHA_S_PDG_ERR",
    "M_KK_GEV",
    "M_Z_GEV",
    "K_CS_7D",
    "LEAN4_THEOREM_COUNT",
    "LEAN4_TOTAL_AFTER",
    "volume_t2_z3",
    "volume_s1_z2",
    "inverse_g3_squared",
    "g3_squared_mkk",
    "alpha_s_mkk",
    "run_alpha_s_to_mz",
    "volume_parameter_scan",
    "alphas_7d_summary",
]
