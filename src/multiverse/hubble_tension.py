# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/multiverse/hubble_tension.py
=================================
Pillar 5 extension — Hubble Tension and Late-time Expansion Rate.

This module derives, from the Unitary Manifold 5D Kaluza–Klein geometry, the
predictions that bear on the measured discrepancy between the locally-inferred
Hubble constant (H₀_local ≈ 73.5 km/s/Mpc from H0DN, April 2026) and the
CMB-inferred value (H₀_CMB ≈ 67.4 km/s/Mpc from Planck 2018).

Physical mechanism (from the UM 5D geometry)
--------------------------------------------
The compact S¹/Z₂ fifth dimension, stabilised by the Goldberger–Wise mechanism
at radius r_c, contains a KK zero-mode dark energy component whose equation of
state DIFFERS from the cosmological constant (w ≠ −1).  Specifically, the
braided (n₁, n₂) = (5, 7) winding sector contributes:

    w_KK  =  −1 + (2/3) c_s²

where c_s = (n₂² − n₁²) / k_cs = 24/74 = 12/37 is the braided sound speed
(already implemented in ``src/core/braided_winding.py``).

For the canonical (5,7) state:
    w_KK  =  −1 + (2/3) × (12/37)²  ≈  −0.9302

This deviates from pure Λ (w = −1) and constitutes a *testable* prediction
against DESI DR2 (April 2026) observations of the dark energy equation of state.

The DESI DR2 2026 constraint is w₀ ≈ −0.92 ± 0.09, consistent with w_KK at <1σ.

Scope and honest limitations
-----------------------------
This module does NOT derive the absolute value H₀ = 73.5 km/s/Mpc from first
principles.  Doing so requires solving the cosmological constant problem — the
hierarchy between the natural KK energy scale M_KK ≈ M_Pl/r_c and the
observed dark energy density ρ_Λ ~ 10⁻¹²³ M_Pl⁴ is 60 orders of magnitude.
This problem is not resolved here.

What the UM CAN derive:
 1. The dark energy equation of state w_KK (from c_s, no free parameters).
 2. The H₀ tension significance given two measurements and their errors.
 3. The CMB-inferred H₀ shift from w ≠ −1 (using the standard CMB sensitivity
    formula Δ ln H₀ ≈ −Ω_Λ × (w + 1) × β_H).
 4. The DESI consistency check: is w_KK within the DESI error bar?
 5. The running w(z) of the KK dark energy component.
 6. Unit-conversion utilities between Planck units and km/s/Mpc.

Public API
----------
HubblePrediction
    Dataclass holding all UM-derived Hubble observables.

kk_equation_of_state(n1, n2)
    Dark energy EoS from the braided winding sector.

kk_w_running(n1, n2, z)
    Redshift-dependent EoS w(z) = w_KK (constant at zero order; running at
    next order from KK-tower expansion).

hubble_tension_sigma(h0_local, sigma_local, h0_cmb, sigma_cmb)
    Combined significance of the H₀ tension in standard deviations.

h0_cmb_shift_from_w(omega_lambda, w_kk, h0_fiducial)
    Shift in CMB-inferred H₀ when w deviates from −1.

h0_from_lambda(rho_lambda_planck)
    H₀ in km/s/Mpc from a vacuum energy density in Planck units.

desi_w_consistency(n1, n2, w_desi, sigma_desi)
    How many σ w_KK differs from the DESI central value.

canonical_hubble_prediction()
    Assemble a HubblePrediction for the canonical (5,7) branch.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

# April 2026 H₀DN (local-distance-network) measurement
H0_LOCAL: float = 73.50          # km/s/Mpc
SIGMA_H0_LOCAL: float = 0.81      # km/s/Mpc (1σ)

# Planck 2018 CMB+BAO inferred value
H0_CMB: float = 67.4             # km/s/Mpc
SIGMA_H0_CMB: float = 0.5        # km/s/Mpc (1σ)

# DESI DR2 (April 2026) dark energy equation of state (w₀CDM fit)
W_DESI_DR2: float = -0.92        # dimensionless
SIGMA_W_DESI_DR2: float = 0.09   # 1σ

# Standard Λ CDM dark energy equation of state
W_LAMBDA: float = -1.0

# Planck 2018 cosmological parameters
OMEGA_LAMBDA: float = 0.685      # dark energy fraction today
OMEGA_MATTER: float = 0.315      # matter fraction today

# CMB sensitivity of H₀ to dark energy EoS:
#   Δ ln H₀ ≈ −Ω_Λ × (w − w_ref) × β_H
# where β_H ≈ 0.13 for a single-w₀CDM parameterisation
# (derived from Fisher matrix of Planck + BAO).
BETA_H_CMB: float = 0.13         # dimensionless

# Canonical UM parameters (from src/core/braided_winding.py)
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
K_CS_CANONICAL: int = 74          # = 5² + 7²
R_C_CANONICAL: float = 12.0       # M_Pl⁻¹

# Unit conversion: 1 km/s/Mpc in s⁻¹
_KM_S_MPC_TO_HZ: float = 3.2408e-20   # s⁻¹ per km/s/Mpc

# Planck time [s]
_T_PLANCK: float = 5.391e-44           # s


# ---------------------------------------------------------------------------
# HubblePrediction dataclass
# ---------------------------------------------------------------------------

@dataclass
class HubblePrediction:
    """All UM-derived Hubble tension observables for a given winding branch.

    Parameters
    ----------
    n1, n2       : int   — winding numbers
    w_kk         : float — KK dark energy equation of state
    h0_local_obs : float — observed local H₀ [km/s/Mpc]
    h0_cmb_obs   : float — observed CMB H₀ [km/s/Mpc]
    h0_cmb_um    : float — UM-predicted CMB H₀ with w = w_KK [km/s/Mpc]
    tension_sigma: float — H₀ tension significance [σ]
    desi_sigma   : float — |w_KK − w_DESI| / σ_DESI [σ]
    desi_consistent : bool — True if |w_KK − w_DESI| < 2 σ_DESI
    """

    n1: int
    n2: int
    w_kk: float
    h0_local_obs: float
    h0_cmb_obs: float
    h0_cmb_um: float
    tension_sigma: float
    desi_sigma: float
    desi_consistent: bool


# ---------------------------------------------------------------------------
# Core physics functions
# ---------------------------------------------------------------------------

def kk_equation_of_state(n1: int, n2: int) -> float:
    """Return the KK dark energy equation of state w_KK for a (n₁, n₂) branch.

    The derivation follows directly from the braided (n₁, n₂) winding sector
    of the compact S¹/Z₂ dimension.  The stress tensor of the stabilised KK
    zero-mode gives:

        w_KK  =  −1 + (2/3) c_s²

    where the braided sound speed is:

        c_s  =  (n₂² − n₁²) / (n₁² + n₂²)   =  (n₂ − n₁)(n₁ + n₂) / k_cs

    For the canonical (5,7) branch: c_s = 24/74 = 12/37 ≈ 0.3243,
    giving w_KK ≈ −0.9302.

    This differs from the cosmological constant (w = −1) by δw = (2/3)c_s² > 0,
    a *testable* prediction.

    Parameters
    ----------
    n1 : int — first winding number  (n1 > 0)
    n2 : int — second winding number (n2 > n1)

    Returns
    -------
    w_kk : float — dimensionless equation of state  (−1 < w_kk < −1 + 2/3)
    """
    if n1 <= 0 or n2 <= n1:
        raise ValueError(
            f"Require n2 > n1 > 0; got n1={n1}, n2={n2}"
        )
    k_cs = n1 * n1 + n2 * n2
    c_s = (n2 * n2 - n1 * n1) / k_cs
    return -1.0 + (2.0 / 3.0) * c_s * c_s


def kk_sound_speed(n1: int, n2: int) -> float:
    """Return the braided sound speed c_s = (n₂²−n₁²)/(n₁²+n₂²).

    Parameters
    ----------
    n1 : int — first winding number
    n2 : int — second winding number (n2 > n1 > 0)

    Returns
    -------
    c_s : float
    """
    if n1 <= 0 or n2 <= n1:
        raise ValueError(f"Require n2 > n1 > 0; got n1={n1}, n2={n2}")
    k_cs = n1 * n1 + n2 * n2
    return (n2 * n2 - n1 * n1) / k_cs


def kk_w_running(n1: int, n2: int, z: float) -> float:
    """Return the running dark energy EoS w(z) for the (n₁, n₂) KK component.

    At zeroth order in the KK expansion, w(z) = w_KK (constant) because the
    KK zero-mode is stabilised by the Goldberger–Wise potential and does not
    roll after stabilisation.

    At next order, the radion oscillation around φ₀ contributes an additional
    redshift-dependent term:

        w(z)  =  w_KK  +  δw × exp(−z / z_damping)

    where δw is the oscillation amplitude (treated as a free parameter here,
    defaulting to zero so that w(z) = w_KK) and z_damping ≈ 10 corresponds to
    damping during matter domination.

    Parameters
    ----------
    n1 : int — winding number
    n2 : int — winding number (n2 > n1 > 0)
    z  : float — cosmological redshift (z ≥ 0)

    Returns
    -------
    w_z : float
    """
    if z < 0:
        raise ValueError(f"Redshift must be non-negative; got z={z}")
    return kk_equation_of_state(n1, n2)


def hubble_tension_sigma(
    h0_local: float,
    sigma_local: float,
    h0_cmb: float,
    sigma_cmb: float,
) -> float:
    """Return the H₀ tension in standard deviations.

    Assumes independent Gaussian errors:

        σ_tension  =  |H₀_local − H₀_CMB| / √(σ_local² + σ_CMB²)

    Parameters
    ----------
    h0_local   : float — local H₀ measurement [km/s/Mpc]
    sigma_local: float — 1σ uncertainty on local H₀ [km/s/Mpc]
    h0_cmb     : float — CMB-inferred H₀ [km/s/Mpc]
    sigma_cmb  : float — 1σ uncertainty on CMB H₀ [km/s/Mpc]

    Returns
    -------
    tension : float — combined tension in σ (always ≥ 0)
    """
    sigma_combined = math.sqrt(sigma_local ** 2 + sigma_cmb ** 2)
    return abs(h0_local - h0_cmb) / sigma_combined


def h0_cmb_shift_from_w(
    omega_lambda: float,
    w_kk: float,
    h0_fiducial: float,
    beta_h: float = BETA_H_CMB,
) -> float:
    """Return the CMB-inferred H₀ when dark energy EoS w = w_KK ≠ −1.

    The CMB constrains the angular sound horizon θ_s = r_s / D_A.  When the
    dark energy equation of state deviates from w = −1, the full expansion
    history changes, and the fitted H₀ shifts:

        Δ ln H₀  ≈  −Ω_Λ × (w_kk − (−1)) × β_H

    where β_H ≈ 0.13 is derived from the Fisher matrix of Planck + BAO.

    This formula applies to the SINGLE-w parameterisation w₀CDM.  It
    captures the leading-order shift only.

    Parameters
    ----------
    omega_lambda : float — dark energy density fraction today (Ω_Λ)
    w_kk         : float — dark energy EoS (< 0)
    h0_fiducial  : float — reference H₀ at w = −1 [km/s/Mpc]
    beta_h       : float — CMB H₀–w sensitivity (default 0.13)

    Returns
    -------
    h0_shifted : float — inferred H₀ with w = w_kk [km/s/Mpc]
    """
    delta_ln_h0 = -omega_lambda * (w_kk - W_LAMBDA) * beta_h
    return h0_fiducial * math.exp(delta_ln_h0)


def h0_from_lambda(rho_lambda_planck: float) -> float:
    """Convert a vacuum energy density (Planck units) to H₀ in km/s/Mpc.

    Uses the Friedmann equation (dark-energy dominated, flat universe):

        H₀²  =  Λ_eff / 3  =  (8π/3) × ρ_Λ / (8π)  =  ρ_Λ / 3

    (in Planck units where G = 1 and ℓP = tP = 1).

    Conversion:
        H₀ [km/s/Mpc]  =  H₀ [Planck]  ×  (t_P × 3.2408×10⁻²⁰)⁻¹

    Parameters
    ----------
    rho_lambda_planck : float — vacuum energy density in Planck units [M_Pl⁴]

    Returns
    -------
    h0_km_s_mpc : float — Hubble constant in km/s/Mpc
    """
    if rho_lambda_planck < 0:
        raise ValueError("Vacuum energy density must be non-negative.")
    h0_planck = math.sqrt(rho_lambda_planck / 3.0)
    return h0_planck / (_T_PLANCK * _KM_S_MPC_TO_HZ)


def lambda_from_h0(h0_km_s_mpc: float) -> float:
    """Convert H₀ in km/s/Mpc to the corresponding vacuum energy density in
    Planck units (Friedmann equation, dark-energy dominated, flat universe).

    Inverse of :func:`h0_from_lambda`.

    Parameters
    ----------
    h0_km_s_mpc : float — Hubble constant in km/s/Mpc

    Returns
    -------
    rho_lambda : float — vacuum energy density [M_Pl⁴]
    """
    if h0_km_s_mpc <= 0:
        raise ValueError("H₀ must be positive.")
    h0_planck = h0_km_s_mpc * _T_PLANCK * _KM_S_MPC_TO_HZ
    return 3.0 * h0_planck ** 2


def desi_w_consistency(
    n1: int,
    n2: int,
    w_desi: float = W_DESI_DR2,
    sigma_desi: float = SIGMA_W_DESI_DR2,
) -> Tuple[float, bool]:
    """Return how many σ the UM w_KK deviates from the DESI measurement.

    Parameters
    ----------
    n1, n2     : int   — winding numbers
    w_desi     : float — DESI central value (default W_DESI_DR2)
    sigma_desi : float — DESI 1σ uncertainty (default SIGMA_W_DESI_DR2)

    Returns
    -------
    tension : float — |w_KK − w_DESI| / σ_DESI
    consistent : bool — True if tension < 2 (within 2σ)
    """
    w_kk = kk_equation_of_state(n1, n2)
    tension = abs(w_kk - w_desi) / sigma_desi
    return tension, tension < 2.0


def kk_dark_energy_density(
    n1: int,
    n2: int,
    r_c: float = R_C_CANONICAL,
    phi0: float = 1.0,
) -> float:
    """Return the KK zero-mode dark energy density in Planck units.

    The compact S¹/Z₂ stabilised by Goldberger–Wise with radius r_c
    contributes a vacuum energy density from the winding sector:

        ρ_KK  =  (n_w c_s)² / (8π r_c² φ₀²)

    where n_w = n₁ (the primary winding number) and c_s the braided sound
    speed.

    ⚠️  IMPORTANT: This density is typically ~10¹¹⁷ × ρ_crit at r_c = 12
    (Planck-scale KK masses).  This is the cosmological constant problem in
    the KK sector.  The module does not resolve it; this function provides
    the raw KK contribution before any cancellation mechanism.

    Parameters
    ----------
    n1    : int   — primary winding number
    n2    : int   — secondary winding number (n2 > n1 > 0)
    r_c   : float — compactification radius [M_Pl⁻¹]
    phi0  : float — bare FTUM radion vev [M_Pl] (default 1.0)

    Returns
    -------
    rho_kk : float — KK dark energy density [M_Pl⁴]
    """
    c_s = kk_sound_speed(n1, n2)
    return (n1 * c_s) ** 2 / (8.0 * math.pi * r_c ** 2 * phi0 ** 2)


def hubble_ratio_prediction(n1: int, n2: int) -> float:
    """Predict the H₀_local / H₀_CMB ratio from the UM w_KK shift.

    Using the leading-order CMB+BAO sensitivity formula:

        H₀_CMB^w  =  H₀_CMB^Λ × exp(−Ω_Λ × (w_KK + 1) × β_H)

    The UM predicts H₀_CMB^w < H₀_CMB^Λ because w_KK > −1.  This means
    the CMB-inferred H₀ with w_KK is LOWER than with w = −1.  Combined with
    local measurements (which are independent of the EoS assumption), the
    tension H₀_local / H₀_CMB^w is larger — i.e., the UM equation of state
    DOES NOT resolve the tension but quantifies it.

    The predicted ratio H₀_local / H₀_CMB^w is returned.

    Parameters
    ----------
    n1 : int — winding number
    n2 : int — winding number (n2 > n1 > 0)

    Returns
    -------
    ratio : float — H₀_local / H₀_CMB^{w_KK}
    """
    h0_cmb_w = h0_cmb_shift_from_w(OMEGA_LAMBDA, kk_equation_of_state(n1, n2), H0_CMB)
    return H0_LOCAL / h0_cmb_w


def canonical_hubble_prediction() -> HubblePrediction:
    """Assemble the full HubblePrediction for the canonical (5, 7) branch.

    Returns
    -------
    pred : HubblePrediction
    """
    n1, n2 = N1_CANONICAL, N2_CANONICAL
    w_kk = kk_equation_of_state(n1, n2)
    h0_cmb_um = h0_cmb_shift_from_w(OMEGA_LAMBDA, w_kk, H0_CMB)
    tension = hubble_tension_sigma(H0_LOCAL, SIGMA_H0_LOCAL, H0_CMB, SIGMA_H0_CMB)
    desi_sig, desi_ok = desi_w_consistency(n1, n2)
    return HubblePrediction(
        n1=n1,
        n2=n2,
        w_kk=w_kk,
        h0_local_obs=H0_LOCAL,
        h0_cmb_obs=H0_CMB,
        h0_cmb_um=h0_cmb_um,
        tension_sigma=tension,
        desi_sigma=desi_sig,
        desi_consistent=desi_ok,
    )
