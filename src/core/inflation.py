# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/inflation.py
=====================
Slow-roll inflation observables for the Unitary Manifold.

Bridges the Kaluza–Klein radion φ₀ (derived from the FTUM fixed point via
``src.multiverse.fixed_point.derive_alpha_from_fixed_point``) to CMB
observables testable against the Planck 2018 results.

Theory background
-----------------
When the KK radion φ is dynamically active during the inflationary epoch it
plays the role of the inflaton.  Its potential is identified with the
Goldberger–Wise stabilisation potential already present in the evolution
equations (see ``src.core.evolution``, the ``m_phi²(φ − φ₀)`` term):

    V(φ; φ₀, λ) = λ (φ² − φ₀²)²

This is a double-well potential whose minimum sits at φ = ±φ₀.  Near the
top of the potential (φ ≈ 0) it acts as a *hilltop* inflaton with

    V  ≈  λ φ₀⁴        (background energy density)
    V' = 4λ φ (φ² − φ₀²)
    V''= 4λ (3φ² − φ₀²)

The standard Hubble-flow slow-roll parameters are (with M_Pl = 1):

    ε = (1/2)(V'/V)²
    η = V''/V

and the CMB scalar spectral index is:

    nₛ = 1 − 6ε + 2η        (evaluated at horizon exit φ = φ*)

The Planck 2018 best-fit value is nₛ = 0.9649 ± 0.0042 (68 % CL).

Public API
----------
gw_potential(phi, phi0, lam)
    V(φ) = λ(φ² − φ₀²)²  — the Goldberger–Wise inflaton potential.

gw_potential_derivs(phi, phi0, lam)
    Returns (V, dV, d2V) at a given field value.

slow_roll_params(phi, V, dV, d2V)
    Compute Hubble-flow slow-roll parameters (ε, η).

spectral_index(epsilon, eta)
    Scalar tilt  nₛ = 1 − 6ε + 2η.

tensor_to_scalar_ratio(epsilon)
    Tensor-to-scalar ratio  r = 16ε.

gw_spectral_index(epsilon)
    Tensor spectral tilt  nₜ = −2ε  (consistency relation).

ns_from_phi0(phi0, lam, phi_star)
    Full pipeline: given φ₀, coupling λ, and horizon-exit field value φ*,
    return (nₛ, r, ε, η).

planck2018_check(ns_predicted)
    Return True iff nₛ lies within the Planck 2018 1-σ window.
"""

from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Planck 2018 observational target (Table 2, Planck Collaboration 2020)
# ---------------------------------------------------------------------------

PLANCK_NS_CENTRAL = 0.9649
PLANCK_NS_SIGMA   = 0.0042   # 1-σ uncertainty


# ---------------------------------------------------------------------------
# Goldberger–Wise inflaton potential
# ---------------------------------------------------------------------------

def gw_potential(phi: float | np.ndarray,
                 phi0: float,
                 lam: float = 1.0) -> float | np.ndarray:
    """Goldberger–Wise double-well potential V(φ) = λ(φ² − φ₀²)².

    Parameters
    ----------
    phi  : float or ndarray — field value(s)
    phi0 : float            — background / minimum value φ₀  (> 0)
    lam  : float            — self-coupling constant λ  (> 0, default 1)

    Returns
    -------
    V : float or ndarray — potential energy
    """
    return lam * (phi**2 - phi0**2)**2


def gw_potential_derivs(
    phi: float,
    phi0: float,
    lam: float = 1.0,
) -> tuple[float, float, float]:
    """Return (V, dV/dφ, d²V/dφ²) for the Goldberger–Wise potential.

    Analytic derivatives:
        V   = λ (φ² − φ₀²)²
        V'  = 4λ φ (φ² − φ₀²)
        V'' = 4λ (3φ² − φ₀²)

    Parameters
    ----------
    phi  : float — field value φ
    phi0 : float — background value φ₀
    lam  : float — coupling λ  (default 1)

    Returns
    -------
    (V, dV, d2V) : tuple of float
    """
    V   = lam * (phi**2 - phi0**2)**2
    dV  = 4.0 * lam * phi * (phi**2 - phi0**2)
    d2V = 4.0 * lam * (3.0 * phi**2 - phi0**2)
    return float(V), float(dV), float(d2V)


# ---------------------------------------------------------------------------
# Slow-roll parameters
# ---------------------------------------------------------------------------

def slow_roll_params(
    phi: float,
    V: float,
    dV: float,
    d2V: float,
) -> tuple[float, float]:
    """Hubble-flow slow-roll parameters ε and η (Planck units, M_Pl = 1).

    Definitions (Liddle & Lyth convention):
        ε = (1/2)(V'/V)²
        η = V''/V

    Parameters
    ----------
    phi  : float — field value (kept for API symmetry / future extensions)
    V    : float — potential V(φ)
    dV   : float — first derivative V'(φ)
    d2V  : float — second derivative V''(φ)

    Returns
    -------
    (epsilon, eta) : tuple[float, float]

    Raises
    ------
    ValueError if V ≤ 0 (potential must be positive during inflation).
    """
    if V <= 0.0:
        raise ValueError(
            f"Potential V={V!r} must be strictly positive during inflation."
        )
    epsilon = 0.5 * (dV / V) ** 2
    eta     = d2V / V
    return float(epsilon), float(eta)


# ---------------------------------------------------------------------------
# CMB observables
# ---------------------------------------------------------------------------

def spectral_index(epsilon: float, eta: float) -> float:
    """Scalar spectral index  nₛ = 1 − 6ε + 2η.

    Parameters
    ----------
    epsilon : float — first slow-roll parameter ε
    eta     : float — second slow-roll parameter η

    Returns
    -------
    ns : float — scalar tilt
    """
    return 1.0 - 6.0 * epsilon + 2.0 * eta


def tensor_to_scalar_ratio(epsilon: float) -> float:
    """Tensor-to-scalar ratio  r = 16ε.

    Parameters
    ----------
    epsilon : float — first slow-roll parameter ε

    Returns
    -------
    r : float — tensor-to-scalar ratio
    """
    return 16.0 * epsilon


def gw_spectral_index(epsilon: float) -> float:
    """Tensor spectral tilt  nₜ = −2ε  (single-field consistency relation).

    Parameters
    ----------
    epsilon : float — first slow-roll parameter ε

    Returns
    -------
    nt : float — tensor tilt
    """
    return -2.0 * epsilon


# ---------------------------------------------------------------------------
# Full pipeline convenience function
# ---------------------------------------------------------------------------

def ns_from_phi0(
    phi0: float,
    lam: float = 1.0,
    phi_star: float | None = None,
) -> tuple[float, float, float, float]:
    """Compute CMB observables from the FTUM fixed-point radion φ₀.

    Uses the Goldberger–Wise potential V(φ) = λ(φ² − φ₀²)².  Horizon exit
    is evaluated at ``phi_star``.  If ``phi_star`` is None, the canonical
    hilltop approximation φ* = φ₀ / √3 is used, which places the field
    at the inflection point where V'' = 0, giving η = 0 and therefore
    nₛ ≈ 1 − 6ε.

    Parameters
    ----------
    phi0     : float       — stabilised radion background value φ₀
    lam      : float       — self-coupling λ (default 1; nₛ is λ-independent
                             at leading order in slow roll because ε ∝ λ⁰)
    phi_star : float|None  — field value at CMB horizon exit; defaults to
                             the inflection point φ₀ / √3

    Returns
    -------
    (ns, r, epsilon, eta) : tuple[float, float, float, float]
        ns      — scalar spectral index nₛ
        r       — tensor-to-scalar ratio r
        epsilon — slow-roll parameter ε
        eta     — slow-roll parameter η

    Notes
    -----
    The leading-order nₛ prediction is independent of λ because the slow-roll
    parameters ε = (V'/V)² / 2 and η = V''/V are ratios within the same
    potential.  The coupling λ cancels exactly.  Physical predictions therefore
    depend only on the geometry through φ₀ (which sets α = φ₀⁻²).
    """
    if phi_star is None:
        # Inflection-point approximation: d²V/dφ² = 4λ(3φ*² − φ₀²) = 0
        # → φ* = φ₀ / √3
        phi_star = phi0 / np.sqrt(3.0)

    V, dV, d2V = gw_potential_derivs(phi_star, phi0, lam)
    epsilon, eta = slow_roll_params(phi_star, V, dV, d2V)
    ns = spectral_index(epsilon, eta)
    r  = tensor_to_scalar_ratio(epsilon)
    return float(ns), float(r), float(epsilon), float(eta)


# ---------------------------------------------------------------------------
# Planck 2018 falsifiability check
# ---------------------------------------------------------------------------

def planck2018_check(ns_predicted: float, n_sigma: float = 1.0) -> bool:
    """Return True iff nₛ lies within *n_sigma* of the Planck 2018 best fit.

    Planck 2018 (TT,TE,EE+lowE+lensing):
        nₛ = 0.9649 ± 0.0042  (68 % CL)

    Parameters
    ----------
    ns_predicted : float — theory prediction for nₛ
    n_sigma      : float — number of σ to use as acceptance window (default 1)

    Returns
    -------
    bool — True if |nₛ_pred − 0.9649| ≤ n_sigma × 0.0042
    """
    return abs(ns_predicted - PLANCK_NS_CENTRAL) <= n_sigma * PLANCK_NS_SIGMA
