# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""T²/Z₃ orbifold modular geometry for the Unitary Manifold 6D compactification.

The extra compact dimensions form a 2-torus T² with complex structure
τ = e^{2πi/3} quotiented by the Z₃ orbifold action z → ω·z where ω = e^{2πi/3}.

Three fixed points (equilateral on T²):
  z₀ = 0
  z₁ = (2+τ)/3  →  (1/2, √3/6) in Cartesian
  z₂ = (1+2τ)/3  →  (0, 1/√3) in Cartesian

All pairwise distances equal 1/√3 (equilateral triangle in T² metric).

Status: GEOMETRIC_ESTIMATE (analytic T²/Z₃ computation)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import cmath
import math
from typing import Dict, List, Tuple

__all__ = [
    "TAU_REAL",
    "TAU_IMAG",
    "Z3_PHASE",
    "FIXED_POINTS_REAL",
    "FIXED_POINTS_IMAG",
    "Z3_CHARGES",
    "OMEGA_Z3",
    "fixed_point_positions",
    "fixed_point_distances",
    "discrete_torsion_phase",
    "t2_area_metric",
    "kk_mass_spectrum_t2",
    "orbifold_selection_rules",
    "modular_weight_factor",
]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

TAU_REAL: float = -0.5
TAU_IMAG: float = 0.8660254037844387  # √3/2
Z3_PHASE: complex = complex(TAU_REAL, TAU_IMAG)  # e^{2πi/3}

# Exact fixed-point positions on T²/Z₃ in Cartesian coordinates.
# z₀=0,  z₁=(2+τ)/3=(1/2, √3/6),  z₂=(1+2τ)/3=(0, 1/√3)
# These form an equilateral triangle with all sides = 1/√3.
FIXED_POINTS_REAL: List[float] = [
    0.0,
    1.0 / 2.0,
    0.0,
]
FIXED_POINTS_IMAG: List[float] = [
    0.0,
    math.sqrt(3.0) / 6.0,       # ≈ 0.28868
    math.sqrt(3.0) / 3.0,       # = 1/√3 ≈ 0.57735
]

Z3_CHARGES: List[int] = [0, 1, 2]
OMEGA_Z3: complex = Z3_PHASE  # primitive Z₃ root = e^{2πi/3}


# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def fixed_point_positions() -> List[Tuple[float, float]]:
    """Return the three T²/Z₃ fixed-point positions as (real, imag) pairs.

    Computed exactly from z₀=0, z₁=(2+τ)/3, z₂=(1+2τ)/3 with τ=e^{2πi/3}.
    All pairwise distances equal 1/√3 (equilateral).
    """
    tau = complex(TAU_REAL, TAU_IMAG)
    z0 = complex(0.0, 0.0)
    z1 = (2.0 + tau) / 3.0
    z2 = (1.0 + 2.0 * tau) / 3.0
    return [(z0.real, z0.imag), (z1.real, z1.imag), (z2.real, z2.imag)]


def fixed_point_distances() -> Dict[str, float]:
    """Return all pairwise distances |z_i − z_j| in T² lattice units.

    For the equilateral T²/Z₃ fixed points, all non-zero distances equal 1/√3.
    """
    pos = fixed_point_positions()
    zs = [complex(r, im) for r, im in pos]
    d01 = abs(zs[1] - zs[0])
    d12 = abs(zs[2] - zs[1])
    d02 = abs(zs[2] - zs[0])
    return {
        "d_01": d01,
        "d_12": d12,
        "d_02": d02,
        "equilateral_reference": 1.0 / math.sqrt(3.0),
        "status": "GEOMETRIC_ESTIMATE",
    }


def discrete_torsion_phase(i: int, j: int) -> complex:
    """Discrete torsion phase ω^{n_i − n_j} from H¹(T²/Z₃, U(1)) = Z₃.

    Parameters
    ----------
    i, j : int
        Fixed-point indices in {0, 1, 2}.

    Returns
    -------
    complex
        Phase ω^{n_i − n_j} with |phase| = 1.
    """
    if not (0 <= i <= 2 and 0 <= j <= 2):
        raise ValueError(f"Fixed-point indices must be in {{0,1,2}}; got ({i},{j})")
    exponent = (Z3_CHARGES[i] - Z3_CHARGES[j]) % 3
    if exponent == 0:
        return complex(1.0, 0.0)
    elif exponent == 1:
        return OMEGA_Z3
    else:  # exponent == 2
        return OMEGA_Z3 * OMEGA_Z3  # ω²


def t2_area_metric() -> Dict[str, float]:
    """Return T² metric data for τ = e^{2πi/3} (R_T² = 1 units).

    Area of fundamental domain = Im(τ) = √3/2 (in R_T²=1 units).
    """
    area = TAU_IMAG  # √3/2 for the rhombic fundamental domain
    return {
        "area_fundamental_domain": area,
        "im_tau": TAU_IMAG,
        "re_tau": TAU_REAL,
        "abs_tau": 1.0,
        "description": "T² with complex structure τ=e^{2πi/3}, unit lattice",
    }


def kk_mass_spectrum_t2(
    r_t2_over_r_s1: float = 1.0 / 74.0,
    pi_kr: float = 37.0,
) -> Dict[str, object]:
    """KK mass spectrum on T² for modes (p,q) with p,q ∈ {-1,0,1}.

    m²_{p,q} = M_KK² × |p + q·τ|² / R_T2²
    |p + q·τ|² = p² − p·q + q²   (for τ = e^{2πi/3})

    Parameters
    ----------
    r_t2_over_r_s1 : float
        Ratio R_T2 / R_S1 (default 1/K_CS = 1/74).
    pi_kr : float
        π·k·R (default 37.0).

    Returns
    -------
    dict with 'zero_mode_mass', 'level1_mass', 'level3_mass', 'modes' list.
    """
    m_kk_rs1 = 1.22e19 * math.exp(-pi_kr)  # GeV
    m_kk_t2 = m_kk_rs1 / r_t2_over_r_s1

    modes = []
    for p in (-1, 0, 1):
        for q in (-1, 0, 1):
            mag2 = p * p - p * q + q * q
            mass = m_kk_t2 * math.sqrt(float(mag2))
            modes.append({"p": p, "q": q, "mass2_units": mag2, "mass_gev": mass})

    return {
        "zero_mode_mass": 0.0,
        "level1_mass_gev": m_kk_t2,
        "level3_mass_gev": m_kk_t2 * math.sqrt(3.0),
        "modes": modes,
        "m_kk_rs1_gev": m_kk_rs1,
        "m_kk_t2_gev": m_kk_t2,
        "status": "GEOMETRIC_ESTIMATE",
    }


def orbifold_selection_rules() -> Dict[str, object]:
    """Z₃ selection rules for Yukawa couplings on T²/Z₃.

    A three-point interaction between fixed points (i, j, k) is Z₃-allowed
    if and only if  n_i + n_j + n_k ≡ 0 (mod 3).

    Returns
    -------
    dict with 'allowed_triplets' (list of (i,j,k)) and 'selection_rule'.
    """
    allowed: List[Tuple[int, int, int]] = []
    forbidden: List[Tuple[int, int, int]] = []
    for i in range(3):
        for j in range(3):
            for k in range(3):
                charge_sum = (Z3_CHARGES[i] + Z3_CHARGES[j] + Z3_CHARGES[k]) % 3
                if charge_sum == 0:
                    allowed.append((i, j, k))
                else:
                    forbidden.append((i, j, k))
    return {
        "allowed_triplets": allowed,
        "forbidden_triplets": forbidden,
        "selection_rule": "n_i + n_j + n_k ≡ 0 (mod 3)",
        "n_allowed": len(allowed),
        "n_forbidden": len(forbidden),
    }


def modular_weight_factor(c_l: float, pi_kr: float = 37.0) -> float:
    """RS1 localisation weight for a fermion with bulk mass parameter c_L.

    Returns exp(−(c_L − 0.5)·π·k·R) for c_L > 0.5 (IR localised),
    and 1.0 for c_L ≤ 0.5 (flat or UV localised).

    Parameters
    ----------
    c_l : float
        Fermion bulk mass parameter.
    pi_kr : float
        π·k·R (default 37.0).

    Returns
    -------
    float
        Modular weight in (0, 1].
    """
    delta = c_l - 0.5
    if delta <= 0.0:
        return 1.0
    return math.exp(-delta * pi_kr)
