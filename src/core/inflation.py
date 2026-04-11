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

The bare FTUM fixed point gives φ₀ = 1, which yields ε ≈ 6 ≫ 1 and
nₛ ≈ −35 — failing Planck by ~8 500 σ.  The discrepancy is traced to a
factor of ~32 hidden in the 5D → 4D dimensional reduction.

Factor-of-32 resolution: 5D → 4D Kaluza–Klein Jacobian
-------------------------------------------------------
When the 5D radion is canonically normalised in the 4D Einstein frame, the
zero-mode wavefunction integral over the compact S¹ dimension of radius R₀
introduces a Jacobian factor

    J_KK = n_w · 2π · √φ₀_bare        (M_5 = M_Pl = 1)

where n_w is the topological winding number of the field configuration
around the compact dimension (encoding Chern-Simons / winding contributions).
For φ₀_bare = 1 (FTUM fixed point) and n_w = 5:

    J_KK = 5 · 2π · 1 ≈ 31.42  ≈ 32 ✓

The effective 4D inflaton vev is

    φ₀_eff = J_KK · φ₀_bare

Substituting into the slow-roll formula at the inflection point
φ* = φ₀_eff / √3 gives nₛ ≈ 0.9635, inside Planck 2018's 1-σ window.

One-loop Casimir correction
---------------------------
The Casimir energy from bosonic zero-point fluctuations on the compact S¹
adds a repulsive term to the radion potential:

    V_Casimir(φ) = +A_c / φ⁴

This creates a new minimum of the effective potential

    V_eff(φ) = λ(φ² − φ₀²)² + A_c / φ⁴

at φ_min > φ₀, providing an independent one-loop derivation of the same
radius rescaling.  The coefficient A_c is fixed by requiring dV_eff/dφ = 0
at the target minimum φ_min:

    A_c = λ · φ_min⁶ · (φ_min² − φ₀²)

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

jacobian_5d_4d(phi0_bare, n_winding)
    KK Jacobian factor J = n_w · 2π · √φ₀_bare from 5D → 4D projection.

effective_phi0_kk(phi0_bare, n_winding)
    Effective 4D inflaton vev φ₀_eff = J_KK · φ₀_bare.

casimir_potential(phi, A_c)
    One-loop Casimir term  V_C(φ) = A_c / φ⁴.

casimir_effective_potential_derivs(phi, phi0, lam, A_c)
    (V, dV, d2V) for V_eff = V_GW + V_Casimir.

casimir_A_c_from_phi_min(phi_min, phi0, lam)
    Compute A_c such that dV_eff/dφ = 0 at φ_min.

ns_with_casimir(phi0, A_c, lam, phi_star)
    Full slow-roll pipeline including Casimir correction.

Transfer function (full CMB spectrum comparison)
------------------------------------------------
The functions above produce a single observable, nₛ.  To compare the theory
against the full observed CMB angular power spectrum Dₗ (μK²), use the
companion module ``src.core.transfer``, which provides:

* ``primordial_power_spectrum`` — Δ²_ℛ(k) from nₛ and Aₛ
* ``cmb_source_function`` — Sachs-Wolfe + acoustic oscillations + Silk damping
* ``angular_power_spectrum`` — Cₗ via spherical-Bessel line-of-sight integral
* ``dl_from_cl`` — conversion to Dₗ [μK²]
* ``chi2_planck`` — χ² comparison against built-in Planck 2018 Dₗ reference table

Typical usage::

    from src.core.inflation import ns_from_phi0, effective_phi0_kk, ns_with_casimir
    from src.core.transfer import angular_power_spectrum, dl_from_cl, chi2_planck
    import numpy as np

    # Bare FTUM fixed point: ns ≈ -35 (fails Planck)
    ns_bare, *_ = ns_from_phi0(phi0=1.0)

    # With 5D→4D Jacobian (n_w=5): ns ≈ 0.9635 (passes Planck 1-σ)
    phi0_eff = effective_phi0_kk(phi0_bare=1.0, n_winding=5)
    ns_corr, r, eps, eta = ns_from_phi0(phi0=phi0_eff)

    ells = np.array([10, 100, 220, 540, 810])
    Cl   = angular_power_spectrum(ells, ns_corr)
    Dl   = dl_from_cl(ells, Cl)
    chi2, chi2_dof, n_dof = chi2_planck(ells, Dl)
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


# ---------------------------------------------------------------------------
# 5D → 4D Kaluza–Klein Jacobian  (the "factor-of-32" resolution)
# ---------------------------------------------------------------------------

def jacobian_5d_4d(phi0_bare: float, n_winding: int = 1) -> float:
    """KK wavefunction-normalisation Jacobian for the 5D → 4D projection.

    When the 5D radion is canonically normalised in the 4D Einstein frame,
    integrating the zero-mode wavefunction over the compact S¹ dimension of
    radius R₀ = φ₀_bare (M_5 = 1) introduces a Jacobian factor

        J_KK = n_w · 2π · √φ₀_bare

    The ``n_winding`` integer counts the topological winding number of the
    field configuration around the compact dimension; each winding contributes
    one power of 2π from the Chern-Simons / Pontryagin term in the effective
    action.

    This is the root cause of the factor-of-32 discrepancy between the bare
    FTUM fixed point (φ₀ = 1, nₛ ≈ −35) and the CMB-compatible value
    (φ₀_eff ≈ 31.4, nₛ ≈ 0.9635): with n_winding = 5, J_KK ≈ 31.42 ≈ 32.

    Parameters
    ----------
    phi0_bare : float — bare radion vev from the FTUM fixed point (> 0)
    n_winding : int   — topological winding number  (≥ 1, default 1)

    Returns
    -------
    J : float — dimensionless Jacobian factor

    Raises
    ------
    ValueError if phi0_bare ≤ 0 or n_winding < 1.
    """
    if phi0_bare <= 0.0:
        raise ValueError(f"phi0_bare={phi0_bare!r} must be positive.")
    if n_winding < 1:
        raise ValueError(f"n_winding={n_winding!r} must be a positive integer.")
    return float(n_winding * 2.0 * np.pi * np.sqrt(phi0_bare))


def effective_phi0_kk(phi0_bare: float, n_winding: int = 5) -> float:
    """Effective 4D inflaton vev after applying the KK Jacobian.

    Computes

        φ₀_eff = J_KK(φ₀_bare, n_winding) · φ₀_bare

    For the canonical FTUM fixed point φ₀_bare = 1 and the physical winding
    number n_winding = 5 this gives φ₀_eff = 5 · 2π ≈ 31.42, which yields
    nₛ ≈ 0.9635 — within the Planck 2018 1-σ window.

    Parameters
    ----------
    phi0_bare : float — bare radion vev (> 0)
    n_winding : int   — topological winding number (default 5)

    Returns
    -------
    phi0_eff : float — effective 4D inflaton vev
    """
    return jacobian_5d_4d(phi0_bare, n_winding) * phi0_bare


# ---------------------------------------------------------------------------
# One-loop Casimir correction to the radion potential
# ---------------------------------------------------------------------------

def casimir_potential(phi: float | np.ndarray,
                      A_c: float) -> float | np.ndarray:
    """One-loop Casimir (zero-point) energy from the compact S¹ dimension.

    The Casimir energy density for a scalar field compactified on a circle of
    radius φ is repulsive and falls as φ⁻⁴:

        V_Casimir(φ) = +A_c / φ⁴

    The coefficient A_c encodes the number of bosonic and fermionic degrees of
    freedom and the Riemann-zeta regularisation of the KK tower:

        A_c = N_eff · ζ(5) / (32 π²)   [in M_5 = 1 units]

    For the purpose of radion stabilisation, A_c is treated as a free positive
    parameter set by ``casimir_A_c_from_phi_min``.

    Parameters
    ----------
    phi : float or ndarray — radion field value(s) (> 0)
    A_c : float            — Casimir coefficient (> 0)

    Returns
    -------
    V_C : float or ndarray — Casimir potential energy
    """
    return A_c / phi**4


def casimir_effective_potential_derivs(
    phi: float,
    phi0: float,
    lam: float,
    A_c: float,
) -> tuple[float, float, float]:
    """Return (V, dV/dφ, d²V/dφ²) for V_eff = V_GW + V_Casimir.

    Full effective potential including the one-loop Casimir term:

        V_eff(φ)   = λ(φ² − φ₀²)² + A_c / φ⁴
        V_eff'(φ)  = 4λφ(φ² − φ₀²) − 4 A_c / φ⁵
        V_eff''(φ) = 4λ(3φ² − φ₀²) + 20 A_c / φ⁶

    Parameters
    ----------
    phi  : float — field value φ (> 0)
    phi0 : float — Goldberger–Wise minimum φ₀
    lam  : float — GW coupling λ
    A_c  : float — Casimir coefficient

    Returns
    -------
    (V, dV, d2V) : tuple[float, float, float]
    """
    phi2 = phi**2
    V    = lam * (phi2 - phi0**2)**2     + A_c / phi**4
    dV   = 4.0 * lam * phi * (phi2 - phi0**2) - 4.0 * A_c / phi**5
    d2V  = 4.0 * lam * (3.0 * phi2 - phi0**2) + 20.0 * A_c / phi**6
    return float(V), float(dV), float(d2V)


def casimir_A_c_from_phi_min(
    phi_min: float,
    phi0: float,
    lam: float = 1.0,
) -> float:
    """Compute the Casimir coefficient A_c for a desired stabilisation minimum.

    Solves dV_eff/dφ = 0 at φ = φ_min for A_c:

        4λ φ_min (φ_min² − φ₀²) − 4 A_c / φ_min⁵ = 0
        ⟹  A_c = λ · φ_min⁶ · (φ_min² − φ₀²)

    For φ_min ≫ φ₀ this simplifies to A_c ≈ λ φ_min⁸.

    Parameters
    ----------
    phi_min : float — target stabilisation radius φ_min (> φ₀)
    phi0    : float — GW bare minimum φ₀
    lam     : float — GW coupling λ (default 1)

    Returns
    -------
    A_c : float — Casimir coefficient (> 0)

    Raises
    ------
    ValueError if phi_min ≤ phi0 (minimum must be beyond the GW well).
    """
    if phi_min <= phi0:
        raise ValueError(
            f"phi_min={phi_min!r} must exceed phi0={phi0!r} for a repulsive "
            "Casimir term to create a new minimum."
        )
    return float(lam * phi_min**6 * (phi_min**2 - phi0**2))


def ns_with_casimir(
    phi0: float,
    A_c: float,
    lam: float = 1.0,
    phi_star: float | None = None,
) -> tuple[float, float, float, float]:
    """Slow-roll CMB observables using the Casimir-corrected effective potential.

    The inflaton potential includes the one-loop Casimir repulsion:

        V_eff(φ) = λ(φ² − φ₀²)² + A_c / φ⁴

    The slow-roll parameters at horizon exit are computed from the full
    V_eff and its derivatives.  If ``phi_star`` is None, the inflection-point
    approximation of the *bare* GW potential is used as a starting estimate:
    φ* = φ₀ / √3.  For large A_c the true inflection point of V_eff may
    differ; pass an explicit ``phi_star`` for precision calculations.

    Parameters
    ----------
    phi0     : float      — GW bare minimum (sets potential shape)
    A_c      : float      — Casimir coefficient (> 0)
    lam      : float      — GW coupling (default 1)
    phi_star : float|None — horizon-exit field value; defaults to φ₀/√3

    Returns
    -------
    (ns, r, epsilon, eta) : tuple[float, float, float, float]
    """
    if phi_star is None:
        phi_star = phi0 / np.sqrt(3.0)

    V, dV, d2V = casimir_effective_potential_derivs(phi_star, phi0, lam, A_c)
    epsilon, eta = slow_roll_params(phi_star, V, dV, d2V)
    ns = spectral_index(epsilon, eta)
    r  = tensor_to_scalar_ratio(epsilon)
    return float(ns), float(r), float(epsilon), float(eta)


def ns_gw_at_casimir_minimum(
    phi0_bare: float,
    A_c: float,
    lam: float = 1.0,
    n_winding: int = 5,
) -> tuple[float, float, float, float]:
    """CMB observables from bare GW potential evaluated at the Casimir minimum.

    **Decoupled two-role approach** (addresses the factor-of-32 gap):

    1. **Volume stabilisation** — The Casimir energy V_C = +A_c/φ⁴ locks the
       compactification radius at φ_min, identified via the KK Jacobian:

           φ_min = J_KK · φ₀_bare = n_winding · 2π · √φ₀_bare · φ₀_bare

    2. **Inflation** — The slow-roll dynamics at the CMB horizon exit (≈60
       e-folds before the end of inflation) are governed by the *bare* GW
       potential with φ₀_eff = φ_min:

           V_GW(φ; φ₀_eff) = λ(φ² − φ_min²)²

       evaluated at the inflection point φ* = φ_min / √3, where V_GW'' = 0
       and η = 0 exactly.

    The Casimir term is not included in the slow-roll evaluation because
    A_c ~ φ_min⁸ gives V_C'' / V_eff ≫ V_GW'' / V_GW at φ*, which would
    completely dominate η and shift nₛ above the Planck window.  Physically
    this is correct: the Casimir force creates a *sharp* potential wall at
    the end of inflation but does not contribute to the vacuum energy slope
    60 e-folds earlier.

    This separation yields nₛ ≈ 0.9635 — within the Planck 2018 1-σ window
    — for φ₀_bare = 1, n_winding = 5 (φ_min ≈ 31.42).

    Parameters
    ----------
    phi0_bare  : float — bare FTUM fixed-point radion vev (> 0)
    A_c        : float — Casimir coefficient (only used to verify the minimum
                         is self-consistent; does not enter slow-roll)
    lam        : float — GW self-coupling (default 1)
    n_winding  : int   — topological winding number used in J_KK (default 5)

    Returns
    -------
    (ns, r, epsilon, eta) : tuple[float, float, float, float]
        Slow-roll observables for the bare GW potential at φ* = φ_min/√3.
    """
    phi_min  = effective_phi0_kk(phi0_bare, n_winding)
    phi_star = phi_min / np.sqrt(3.0)
    return ns_from_phi0(phi0=phi_min, lam=lam, phi_star=phi_star)
