# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 40 — AdS₅/CFT₄ KK Tower Holographic Dictionary
=========================================================
Implements the full AdS₅/CFT₄ holographic dictionary for the entire
Kaluza-Klein tower, addressing the zero-mode truncation failure
documented in FALLIBILITY.md §4.1.

Physical quantities are in natural (Planck) units throughout.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from typing import Union

import numpy as np

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural / Planck units)
# ---------------------------------------------------------------------------
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74               # = 5² + 7²; birefringence resonance
ADS_RADIUS_PLANCK: float = 1.0         # AdS radius in Planck units
COMPACTIFICATION_RADIUS: float = 1.0e-30  # physical R; KK tower numerically invisible
N_MAX_DEFAULT: int = 50
DELTA_0: float = 4.0                   # Δ₀ = conformal dimension of zero mode
CMB_PEAK_AMPLITUDE_SUPPRESSION: float = 5.0  # documented ×4–7 factor

# ---------------------------------------------------------------------------
# Core KK / holographic functions
# ---------------------------------------------------------------------------

def kk_mode_mass(n: int, R: float) -> float:
    """Return the KK mode mass m_n = n / R.

    Parameters
    ----------
    n : int
        KK mode number (≥ 0).
    R : float
        Compactification radius in Planck units (> 0).
    """
    if n < 0:
        raise ValueError(f"Mode number n must be >= 0, got {n}")
    if R <= 0:
        raise ValueError(f"Compactification radius R must be > 0, got {R}")
    return n / R


def conformal_dimension(n: int, R: float, L: float) -> float:
    """Return Δ_n = 2 + √(4 + (n·L/R)²).

    At n = 0 this reduces to Δ₀ = 4.

    Parameters
    ----------
    n : int
        KK mode number (≥ 0).
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    """
    if n < 0:
        raise ValueError(f"Mode number n must be >= 0, got {n}")
    if R <= 0:
        raise ValueError(f"Compactification radius R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"AdS radius L must be > 0, got {L}")
    return 2.0 + math.sqrt(4.0 + (n * L / R) ** 2)


def kk_mode_spectral_weight(n: int, k_cs: int = K_CS_CANONICAL) -> float:
    """Return spectral weight w_n = exp(−n²/k_cs), with w_0 = 1.

    Parameters
    ----------
    n : int
        KK mode number (≥ 0).
    k_cs : int
        Braided-winding resonance constant (default K_CS_CANONICAL = 74).
    """
    if n < 0:
        raise ValueError(f"Mode number n must be >= 0, got {n}")
    return math.exp(-n * n / k_cs)


def kk_tower_partition_function(
    R: float,
    L: float,
    T: float,
    n_max: int = N_MAX_DEFAULT,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Return Z = Σ_{n=0}^{n_max} w_n · exp(−Δ_n / T).

    Parameters
    ----------
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    T : float
        Effective temperature (> 0).
    n_max : int
        Truncation of the KK tower.
    k_cs : int
        Braided-winding resonance constant.
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    if T <= 0:
        raise ValueError(f"Temperature T must be > 0, got {T}")
    Z = 0.0
    for n in range(n_max + 1):
        w = kk_mode_spectral_weight(n, k_cs)
        delta = conformal_dimension(n, R, L)
        Z += w * math.exp(-delta / T)
    return Z


def holographic_operator_spectrum(
    n_max: int,
    R: float,
    L: float,
    k_cs: int = K_CS_CANONICAL,
) -> np.ndarray:
    """Return array of shape (n_max+1, 3) with columns [n, Δ_n, w_n].

    Parameters
    ----------
    n_max : int
        Highest KK mode to include.
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    k_cs : int
        Braided-winding resonance constant.
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    rows = []
    for n in range(n_max + 1):
        delta = conformal_dimension(n, R, L)
        w = kk_mode_spectral_weight(n, k_cs)
        rows.append([float(n), delta, w])
    return np.array(rows, dtype=float)


def zero_mode_vs_full_tower(
    R: float,
    L: float,
    T: float,
    n_max: int = N_MAX_DEFAULT,
) -> dict:
    """Return dict with Z_zero, Z_full, and ratio = Z_full / Z_zero.

    Parameters
    ----------
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    T : float
        Effective temperature (> 0).
    n_max : int
        Truncation of the KK tower.
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    if T <= 0:
        raise ValueError(f"T must be > 0, got {T}")
    z_zero = math.exp(-DELTA_0 / T)
    z_full = kk_tower_partition_function(R, L, T, n_max)
    return {
        "Z_zero": z_zero,
        "Z_full": z_full,
        "ratio": z_full / z_zero,
    }


def cmb_amplitude_correction(
    n_max: int = N_MAX_DEFAULT,
    R: float = COMPACTIFICATION_RADIUS,
    L: float = ADS_RADIUS_PLANCK,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Return 1 + Σ_{n=1}^{n_max} w_n · (Δ₀ / Δ_n)².

    Measures the fractional amplitude boost from the full KK tower
    relative to the zero-mode-only approximation.

    Parameters
    ----------
    n_max : int
        Truncation of the KK tower.
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    k_cs : int
        Braided-winding resonance constant.
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    correction = 1.0
    for n in range(1, n_max + 1):
        w = kk_mode_spectral_weight(n, k_cs)
        delta_n = conformal_dimension(n, R, L)
        correction += w * (DELTA_0 / delta_n) ** 2
    return correction


def cmb_acoustic_peak_amplitude(
    ell: float,
    n_max: int = N_MAX_DEFAULT,
    R: float = COMPACTIFICATION_RADIUS,
    L: float = ADS_RADIUS_PLANCK,
    k_cs: int = K_CS_CANONICAL,
    ell_max: float = 3000.0,
) -> float:
    """Return 1 + Σ_{n=1}^{n_max} w_n · (Δ₀/Δ_n)² · cos(ℓ·n·π/ℓ_max).

    Encodes the modulation of CMB acoustic peaks by the KK tower.

    Parameters
    ----------
    ell : float
        Multipole moment ℓ.
    n_max : int
        Truncation of the KK tower.
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    k_cs : int
        Braided-winding resonance constant.
    ell_max : float
        Maximum multipole used to normalise the cosine argument.
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    result = 1.0
    for n in range(1, n_max + 1):
        w = kk_mode_spectral_weight(n, k_cs)
        delta_n = conformal_dimension(n, R, L)
        result += w * (DELTA_0 / delta_n) ** 2 * math.cos(ell * n * math.pi / ell_max)
    return result


def rs1_warp_factor(k_rs: float, r_c: float, y: float) -> float:
    """Return the Randall-Sundrum-1 warp factor exp(−k_rs · |y|).

    Parameters
    ----------
    k_rs : float
        RS1 curvature scale.
    r_c : float
        Compactification radius of the extra dimension (unused here but
        kept for API symmetry with rs1_kk_coupling).
    y : float
        Position in the extra dimension.
    """
    return math.exp(-k_rs * abs(y))


def rs1_kk_coupling(n: int, k_rs: float, r_c: float) -> float:
    """Return RS1 KK coupling g_n = exp(−k_rs · r_c · n · π).

    Parameters
    ----------
    n : int
        KK mode number (≥ 0).
    k_rs : float
        RS1 curvature scale.
    r_c : float
        Compactification radius of the extra dimension.
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n}")
    return math.exp(-k_rs * r_c * n * math.pi)


def rs1_amplitude_correction(
    n_max: int,
    k_rs: float,
    r_c: float,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Return 1 + Σ_{n=1}^{n_max} w_n · g_n.

    Combines spectral weights with RS1 KK couplings to give the
    amplitude correction from the RS1 tower.

    Parameters
    ----------
    n_max : int
        Truncation of the KK tower.
    k_rs : float
        RS1 curvature scale.
    r_c : float
        Compactification radius.
    k_cs : int
        Braided-winding resonance constant.
    """
    correction = 1.0
    for n in range(1, n_max + 1):
        w = kk_mode_spectral_weight(n, k_cs)
        g = rs1_kk_coupling(n, k_rs, r_c)
        correction += w * g
    return correction


def entropy_from_tower(
    R: float,
    L: float,
    T: float,
    n_max: int = N_MAX_DEFAULT,
    k_cs: int = K_CS_CANONICAL,
) -> float:
    """Return von-Neumann-style tower entropy S = −Σ p_n ln p_n.

    Probabilities are p_n = w_n · exp(−Δ_n/T) / Z.

    Parameters
    ----------
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    T : float
        Effective temperature (> 0).
    n_max : int
        Truncation of the KK tower.
    k_cs : int
        Braided-winding resonance constant.
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    if T <= 0:
        raise ValueError(f"T must be > 0, got {T}")
    Z = kk_tower_partition_function(R, L, T, n_max, k_cs)
    S = 0.0
    for n in range(n_max + 1):
        w = kk_mode_spectral_weight(n, k_cs)
        delta = conformal_dimension(n, R, L)
        p = w * math.exp(-delta / T) / Z
        if p > 0.0:
            S -= p * math.log(p)
    return S


def truncation_error(
    n_trunc: int,
    n_full: int,
    R: float,
    L: float,
    T: float,
) -> float:
    """Return |Z(n_trunc) − Z(n_full)| / Z(n_full).

    Measures how much of the partition function is missed when the
    tower is truncated at n_trunc rather than n_full.

    Parameters
    ----------
    n_trunc : int
        Truncation level being tested.
    n_full : int
        Reference (full) truncation level.
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    T : float
        Effective temperature (> 0).
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    if T <= 0:
        raise ValueError(f"T must be > 0, got {T}")
    z_trunc = kk_tower_partition_function(R, L, T, n_trunc)
    z_full = kk_tower_partition_function(R, L, T, n_full)
    return abs(z_trunc - z_full) / z_full


def ads5_volume(L: float, R: float) -> float:
    """Return AdS₅ effective volume = L⁴ · R.

    Parameters
    ----------
    L : float
        AdS radius (> 0).
    R : float
        Compactification radius (> 0).
    """
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    return L ** 4 * R


def kk_tower_summary(
    n_max: int = 10,
    R: float = COMPACTIFICATION_RADIUS,
    L: float = ADS_RADIUS_PLANCK,
) -> dict:
    """Return a summary dict of key KK tower properties.

    Parameters
    ----------
    n_max : int
        Highest KK mode to include.
    R : float
        Compactification radius (> 0).
    L : float
        AdS radius (> 0).
    """
    if R <= 0:
        raise ValueError(f"R must be > 0, got {R}")
    if L <= 0:
        raise ValueError(f"L must be > 0, got {L}")
    spectrum = holographic_operator_spectrum(n_max, R, L)
    return {
        "n_max": n_max,
        "delta_0": spectrum[0, 1],
        "delta_1": spectrum[1, 1] if n_max >= 1 else None,
        "w_0": spectrum[0, 2],
        "w_1": spectrum[1, 2] if n_max >= 1 else None,
        "ads5_volume": ads5_volume(L, R),
        "cmb_amplitude_correction": cmb_amplitude_correction(n_max, R, L),
    }
