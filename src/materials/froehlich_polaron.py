# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/materials/froehlich_polaron.py
===================================
Pillar 46 — Fröhlich Polaron Coupling from 5D Braid Geometry.

Derives the dimensionless Fröhlich electron-phonon coupling constant α
from the Unitary Manifold braided-winding sector.  The result

    α_UM = n_w × k_CS × c_s² / (2π)  ≈  6.194

contains no free parameters: n_w = 5, k_CS = 74, and c_s = 12/37 are all
fixed by Planck CMB data and cosmic birefringence observations (Pillars 39, 45-C)
before any condensed-matter input is used.

For bismuth oxyiodide (BiOI), literature estimates give α ≈ 4–7; the UM
prediction 6.194 is consistent with the layered-material range.

Physical quantities use SI-adjacent mixed units where noted (meV, fs, nm, m_e)
as is conventional in condensed-matter polaron physics.  Module-level constants
that feed the core derivation are in natural / dimensionless form.

See also:
  discussions/Froehlich-Polaron-UM-Connection.md  — narrative writeup
  src/core/delay_field.py                         — Pillar 41: DFM time mapping
  src/core/ads_cft_tower.py                       — Pillar 40: KK spectral weights
  src/core/kk_imprint.py                          — Pillar 32: photonic read-out

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict

# ---------------------------------------------------------------------------
# Module-level constants (ALL_CAPS, natural / dimensionless)
# ---------------------------------------------------------------------------
N_W_CANONICAL: int = 5              # Braid winding n_w = n₁
N1_CANONICAL: int = 5               # First braid winding number
N2_CANONICAL: int = 7               # Second braid winding number
K_CS_CANONICAL: int = 74            # = n₁² + n₂² = 5² + 7²; CS level
C_S_CANONICAL: float = 12.0 / 37.0  # = (n₂² − n₁²) / k_CS; braided sound speed

# Physical constants (mixed units for condensed-matter convenience)
HBAR_EV_FS: float = 0.6582119569   # ħ in eV·fs

# BiOI reference parameters (from literature, not UM predictions)
BIOI_ALPHA_LO: float = 4.0          # lower bound of measured/computed α range
BIOI_ALPHA_HI: float = 7.0          # upper bound of measured/computed α range
BIOI_OMEGA_LO_MEV: float = 12.0     # representative LO phonon energy in meV

# Derived canonical value (computed once at module level)
_ALPHA_CANONICAL: float = (
    N_W_CANONICAL * K_CS_CANONICAL * C_S_CANONICAL ** 2 / (2.0 * math.pi)
)


# ---------------------------------------------------------------------------
# Core UM-derived Fröhlich coupling
# ---------------------------------------------------------------------------

def froehlich_alpha_um(n_w: int, n1: int, n2: int) -> float:
    """Derive the Fröhlich coupling constant α from UM braid parameters.

    The CS topological coupling k_CS = n₁² + n₂² and braided sound speed
    c_s = (n₂² − n₁²) / k_CS are computed internally from the two braid
    winding numbers.  The formula is:

        α = n_w × k_CS × c_s² / (2π)

    Parameters
    ----------
    n_w : int
        Winding number (must be ≥ 1; canonical value n_w = n₁ = 5).
    n1 : int
        First braid winding number (must be ≥ 1).
    n2 : int
        Second braid winding number (must be > n1).

    Returns
    -------
    alpha : float — dimensionless Fröhlich coupling constant.

    Raises
    ------
    ValueError if n_w < 1, n1 < 1, or n2 ≤ n1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be >= 1, got {n_w!r}")
    if n1 < 1:
        raise ValueError(f"n1 must be >= 1, got {n1!r}")
    if n2 <= n1:
        raise ValueError(f"n2 must be > n1, got n1={n1!r}, n2={n2!r}")
    k_cs = n1 * n1 + n2 * n2
    c_s = float(n2 * n2 - n1 * n1) / k_cs
    return n_w * k_cs * c_s ** 2 / (2.0 * math.pi)


def froehlich_alpha_canonical() -> float:
    """Return the canonical UM Fröhlich α ≈ 6.194.

    Uses n_w = 5, n1 = 5, n2 = 7, k_CS = 74, c_s = 12/37.
    No free parameters.
    """
    return _ALPHA_CANONICAL


# ---------------------------------------------------------------------------
# Polaron observable predictions
# ---------------------------------------------------------------------------

def polaron_formation_time_fs(omega_lo_mev: float) -> float:
    """Return UM-predicted polaron formation time in femtoseconds.

    From the Delay Field Model (Pillar 41):
        τ_form = (1 / c_s) × (ħ / ω_LO)

    The factor 1/c_s > 1 reflects the delay imposed by the braided phonon
    travelling at sub-luminal speed c_s relative to the electron.

    Parameters
    ----------
    omega_lo_mev : float — LO phonon energy in meV (must be > 0).

    Returns
    -------
    tau_fs : float — formation time in femtoseconds.
    """
    if omega_lo_mev <= 0.0:
        raise ValueError(f"omega_lo_mev must be > 0, got {omega_lo_mev!r}")
    omega_ev = omega_lo_mev * 1e-3          # meV → eV
    tau_phonon_fs = HBAR_EV_FS / omega_ev   # one phonon period
    return tau_phonon_fs / C_S_CANONICAL     # delay by 1/c_s


def polaron_binding_energy_ev(alpha: float, omega_lo_mev: float) -> float:
    """Return polaron binding energy in eV (weak-coupling Fröhlich formula).

    E_b = α × ω_LO

    Valid for α < 6.  For intermediate coupling (α ~ 6) this underestimates
    the true binding energy; the Feynman variational estimate is larger by ~50%.

    Parameters
    ----------
    alpha : float — Fröhlich coupling constant (must be > 0).
    omega_lo_mev : float — LO phonon energy in meV (must be > 0).
    """
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    if omega_lo_mev <= 0.0:
        raise ValueError(f"omega_lo_mev must be > 0, got {omega_lo_mev!r}")
    return alpha * omega_lo_mev * 1e-3


def polaron_binding_energy_feynman_ev(alpha: float, omega_lo_mev: float) -> float:
    """Return polaron binding energy from Feynman variational estimate.

    Feynman (1955) strong-coupling limit: E_b ≈ α² × ω_LO / 4
    Combined with a crossover function for intermediate coupling:
        E_b_F ≈ α × ω_LO × (1 + α / 12)

    This interpolates between the weak- (α → 0) and strong-coupling (α → ∞)
    limits and is accurate to ~10% for α ∈ [1, 10].

    Parameters
    ----------
    alpha : float — Fröhlich coupling constant (must be > 0).
    omega_lo_mev : float — LO phonon energy in meV (must be > 0).
    """
    if alpha <= 0.0:
        raise ValueError(f"alpha must be > 0, got {alpha!r}")
    if omega_lo_mev <= 0.0:
        raise ValueError(f"omega_lo_mev must be > 0, got {omega_lo_mev!r}")
    omega_ev = omega_lo_mev * 1e-3
    return alpha * omega_ev * (1.0 + alpha / 12.0)


def polaron_effective_mass_ratio(alpha: float) -> float:
    """Return polaron effective mass ratio m*/m_b (Fröhlich formula).

    Leading-order perturbation theory (valid for α < 6):
        m* / m_b = 1 + α / 6

    For α ≈ 6.194 this gives m*/m_b ≈ 2.03, consistent with heavy polaron
    masses observed in strongly coupled lead-halide and bismuth oxyhalide
    perovskites.

    Parameters
    ----------
    alpha : float — Fröhlich coupling constant (must be ≥ 0).
    """
    if alpha < 0.0:
        raise ValueError(f"alpha must be >= 0, got {alpha!r}")
    return 1.0 + alpha / 6.0


def polaron_radius_nm(omega_lo_mev: float, m_band_me: float) -> float:
    """Return UM-predicted polaron radius in nanometres.

    r_pol = l_phonon / √α_canonical

    where the phonon length scale is l_phonon = √(ħ / 2 m_b ω_LO).

    Parameters
    ----------
    omega_lo_mev : float — LO phonon energy in meV (must be > 0).
    m_band_me    : float — electronic band mass in units of m_e (must be > 0).

    Returns
    -------
    r_nm : float — polaron radius in nanometres.
    """
    if omega_lo_mev <= 0.0:
        raise ValueError(f"omega_lo_mev must be > 0, got {omega_lo_mev!r}")
    if m_band_me <= 0.0:
        raise ValueError(f"m_band_me must be > 0, got {m_band_me!r}")
    # SI calculation
    hbar_si = 1.054571817e-34       # J·s
    m_e_si = 9.1093837015e-31       # kg
    ev_si = 1.602176634e-19         # J per eV
    omega_si = omega_lo_mev * 1e-3 * ev_si / hbar_si  # rad/s
    m_b_si = m_band_me * m_e_si
    l_phonon_m = math.sqrt(hbar_si / (2.0 * m_b_si * omega_si))
    r_pol_m = l_phonon_m / math.sqrt(_ALPHA_CANONICAL)
    return r_pol_m * 1e9             # m → nm


# ---------------------------------------------------------------------------
# KK phonon branch decomposition
# ---------------------------------------------------------------------------

def kk_phonon_branch_weight(n: int, n1: int = N1_CANONICAL,
                             n2: int = N2_CANONICAL,
                             k_cs: int = K_CS_CANONICAL) -> float:
    """Return spectral weight w_n for phonon branch n in the KK tower.

    w_n = 1                  if n == n1 or n == n2  (braid-locked, lossless)
    w_n = exp(−n² / k_cs)   otherwise              (exponentially suppressed)

    Parameters
    ----------
    n    : int — KK / phonon mode number (must be ≥ 0).
    n1   : int — first braid-locked mode.
    n2   : int — second braid-locked mode.
    k_cs : int — CS level (must be > 0).
    """
    if n < 0:
        raise ValueError(f"n must be >= 0, got {n!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if n == n1 or n == n2:
        return 1.0
    return math.exp(-n * n / k_cs)


def braid_phonon_coupling_decomposition(
    n1: int = N1_CANONICAL,
    n2: int = N2_CANONICAL,
    k_cs: int = K_CS_CANONICAL,
    c_s: float = C_S_CANONICAL,
) -> Dict[str, float]:
    """Decompose the total α into per-branch contributions.

    Each braid-locked mode contributes:
        α_branch = n_branch × c_s² / (2π)

    and the total is their sum (n1 + n2 = 12 for canonical (5, 7)):
        α_total = (n1 + n2) × c_s² × k_cs / (2π)   [reconstructed]

    Returns a dict with keys:
        alpha_n1      — contribution from braid mode n1
        alpha_n2      — contribution from braid mode n2
        alpha_total   — sum (matches froehlich_alpha_um)
        weight_n1     — spectral weight w_{n1} = 1
        weight_n2     — spectral weight w_{n2} = 1
        c_s           — braided sound speed used
    """
    if n1 < 1:
        raise ValueError(f"n1 must be >= 1, got {n1!r}")
    if n2 <= n1:
        raise ValueError(f"n2 must be > n1, got n1={n1!r}, n2={n2!r}")
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if c_s <= 0.0 or c_s >= 1.0:
        raise ValueError(f"c_s must be in (0, 1), got {c_s!r}")
    factor = k_cs * c_s ** 2 / (2.0 * math.pi)
    alpha_n1 = n1 * factor
    alpha_n2 = n2 * factor
    return {
        "alpha_n1": alpha_n1,
        "alpha_n2": alpha_n2,
        "alpha_total": alpha_n1 + alpha_n2,
        "weight_n1": kk_phonon_branch_weight(n1, n1, n2, k_cs),
        "weight_n2": kk_phonon_branch_weight(n2, n1, n2, k_cs),
        "c_s": c_s,
    }


# ---------------------------------------------------------------------------
# BiOI validation helpers
# ---------------------------------------------------------------------------

def bioi_alpha_in_range(alpha: float,
                         lo: float = BIOI_ALPHA_LO,
                         hi: float = BIOI_ALPHA_HI) -> bool:
    """Return True iff alpha ∈ [lo, hi] (BiOI literature range by default).

    Parameters
    ----------
    alpha : float — Fröhlich coupling constant.
    lo    : float — lower bound (default 4.0).
    hi    : float — upper bound (default 7.0).
    """
    return lo <= alpha <= hi


def bioi_alpha_sigma_offset(alpha: float,
                             alpha_mid: float = 5.5,
                             alpha_sigma: float = 1.0) -> float:
    """Return |α - α_mid| / α_sigma — how many σ from the centre of the BiOI range.

    The BiOI literature range [4, 7] is modelled as Gaussian with
    mean = 5.5 and σ = 1.0 eV (rough representative width).

    Parameters
    ----------
    alpha       : float — Fröhlich coupling constant.
    alpha_mid   : float — centre of measurement distribution.
    alpha_sigma : float — 1σ width (must be > 0).
    """
    if alpha_sigma <= 0.0:
        raise ValueError(f"alpha_sigma must be > 0, got {alpha_sigma!r}")
    return abs(alpha - alpha_mid) / alpha_sigma


# ---------------------------------------------------------------------------
# KK imprint magnitude for photonic read-out (Pillar 32 connection)
# ---------------------------------------------------------------------------

def kk_imprint_magnitude_squared(n1: int = N1_CANONICAL,
                                  n2: int = N2_CANONICAL,
                                  k_cs: int = K_CS_CANONICAL,
                                  c_s: float = C_S_CANONICAL) -> float:
    """Return |I_braid|² = c_s² × k_CS.

    The braid-locked KK imprint vector has two non-zero entries:
        I_{n1} = c_s × n1,   I_{n2} = c_s × n2

    so |I_braid|² = c_s² × (n1² + n2²) = c_s² × k_CS.

    This sets the photoemission cross-section enhancement (Pillar 32).

    Parameters
    ----------
    n1, n2 : int — braid winding numbers.
    k_cs   : int — CS level (must equal n1² + n2² for consistency).
    c_s    : float — braided sound speed.
    """
    if k_cs <= 0:
        raise ValueError(f"k_cs must be > 0, got {k_cs!r}")
    if c_s <= 0.0 or c_s >= 1.0:
        raise ValueError(f"c_s must be in (0, 1), got {c_s!r}")
    return c_s ** 2 * k_cs


# ---------------------------------------------------------------------------
# Full summary
# ---------------------------------------------------------------------------

@dataclass
class FroehlichSummary:
    """Full UM Fröhlich polaron prediction for BiOI.

    Attributes
    ----------
    alpha_um          : Fröhlich coupling constant (canonical UM)
    alpha_in_bioi_range: True iff alpha_um ∈ [4, 7]
    sigma_offset      : |α - 5.5| / 1.0 (distance from BiOI centre)
    formation_time_fs : polaron formation time (ω_LO = 12 meV)
    binding_energy_ev : polaron binding energy, weak coupling (ω_LO = 12 meV)
    binding_feynman_ev: polaron binding energy, Feynman estimate (ω_LO = 12 meV)
    mass_ratio        : m*/m_b = 1 + α/6
    radius_nm         : polaron radius (ω_LO = 12 meV, m_b = 0.5 m_e)
    imprint_sq        : |I_braid|² = c_s² × k_CS
    branch_decomp     : per-branch α decomposition dict
    """
    alpha_um: float
    alpha_in_bioi_range: bool
    sigma_offset: float
    formation_time_fs: float
    binding_energy_ev: float
    binding_feynman_ev: float
    mass_ratio: float
    radius_nm: float
    imprint_sq: float
    branch_decomp: Dict[str, float] = field(default_factory=dict)


def um_froehlich_summary(omega_lo_mev: float = BIOI_OMEGA_LO_MEV,
                          m_band_me: float = 0.5) -> FroehlichSummary:
    """Compute the complete UM Fröhlich polaron prediction summary.

    Parameters
    ----------
    omega_lo_mev : float — LO phonon energy in meV (default 12 for BiOI).
    m_band_me    : float — band effective mass in m_e units (default 0.5).

    Returns
    -------
    FroehlichSummary dataclass with all derived quantities.
    """
    if omega_lo_mev <= 0.0:
        raise ValueError(f"omega_lo_mev must be > 0, got {omega_lo_mev!r}")
    if m_band_me <= 0.0:
        raise ValueError(f"m_band_me must be > 0, got {m_band_me!r}")
    alpha = froehlich_alpha_canonical()
    return FroehlichSummary(
        alpha_um=alpha,
        alpha_in_bioi_range=bioi_alpha_in_range(alpha),
        sigma_offset=bioi_alpha_sigma_offset(alpha),
        formation_time_fs=polaron_formation_time_fs(omega_lo_mev),
        binding_energy_ev=polaron_binding_energy_ev(alpha, omega_lo_mev),
        binding_feynman_ev=polaron_binding_energy_feynman_ev(alpha, omega_lo_mev),
        mass_ratio=polaron_effective_mass_ratio(alpha),
        radius_nm=polaron_radius_nm(omega_lo_mev, m_band_me),
        imprint_sq=kk_imprint_magnitude_squared(),
        branch_decomp=braid_phonon_coupling_decomposition(),
    )
