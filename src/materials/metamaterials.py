# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/materials/metamaterials.py
================================
Metamaterials as Engineered φ-Field Geometries — Pillar 26.
"""



from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}
import math
import numpy as np

_EPS = 1e-30


def negative_phi_index(epsilon_r: float, mu_r: float) -> float:
    """Refractive index of a double-negative metamaterial.

    n = −sqrt(|ε_r| × |μ_r|)   when both ε_r < 0 and μ_r < 0

    Parameters
    ----------
    epsilon_r : float — relative permittivity (negative for DNG medium)
    mu_r      : float — relative permeability (negative for DNG medium)

    Returns
    -------
    n : float — refractive index (negative for DNG)
    """
    sign = -1.0 if (epsilon_r < 0.0 and mu_r < 0.0) else 1.0
    return float(sign * math.sqrt(abs(epsilon_r) * abs(mu_r)))


def metamaterial_phi_resonance(omega: float, omega_0: float,
                                gamma: float, phi_0: float = 1.0) -> float:
    """φ-field amplitude at a metamaterial resonance.

    phi(ω) = phi_0 × omega_0² / sqrt((omega_0² − omega²)² + (gamma × omega)²)

    Parameters
    ----------
    omega   : float — drive angular frequency (must be ≥ 0)
    omega_0 : float — resonance frequency (must be > 0)
    gamma   : float — damping rate (must be ≥ 0)
    phi_0   : float — driving amplitude (default 1.0, must be ≥ 0)

    Returns
    -------
    phi_res : float — resonant amplitude
    """
    if omega < 0.0:
        raise ValueError(f"omega must be ≥ 0, got {omega!r}")
    if omega_0 <= 0.0:
        raise ValueError(f"omega_0 must be > 0, got {omega_0!r}")
    if gamma < 0.0:
        raise ValueError(f"gamma must be ≥ 0, got {gamma!r}")
    if phi_0 < 0.0:
        raise ValueError(f"phi_0 must be ≥ 0, got {phi_0!r}")
    denom = math.sqrt((omega_0 ** 2 - omega ** 2) ** 2 +
                      (gamma * omega) ** 2) + _EPS
    return float(phi_0 * omega_0 ** 2 / denom)


def photonic_phi_bandgap(lambda_nm: float, n_high: float, n_low: float,
                          d_high_nm: float, d_low_nm: float) -> float:
    """Centre-wavelength φ of a 1D photonic bandgap.

    λ_Bragg = 2 × (n_high × d_high + n_low × d_low)

    Parameters
    ----------
    lambda_nm : float — design wavelength nm (must be > 0)
    n_high    : float — high-index layer refractive index (must be > 0)
    n_low     : float — low-index layer refractive index (must be > 0)
    d_high_nm : float — high-index layer thickness nm (must be > 0)
    d_low_nm  : float — low-index layer thickness nm (must be > 0)

    Returns
    -------
    phi_BG : float — Bragg wavelength / design wavelength ratio
    """
    if lambda_nm <= 0.0:
        raise ValueError(f"lambda_nm must be > 0, got {lambda_nm!r}")
    for name, v in [("n_high", n_high), ("n_low", n_low),
                    ("d_high_nm", d_high_nm), ("d_low_nm", d_low_nm)]:
        if v <= 0.0:
            raise ValueError(f"{name} must be > 0, got {v!r}")
    lambda_Bragg = 2.0 * (n_high * d_high_nm + n_low * d_low_nm)
    return float(lambda_Bragg / lambda_nm)


def acoustic_phi_metamaterial(rho_meta: float, rho_host: float,
                               kappa_meta: float, kappa_host: float) -> float:
    """Acoustic impedance mismatch φ for metamaterial cloaking layer.

    Z_ratio = sqrt(rho_meta × kappa_meta) / sqrt(rho_host × kappa_host)

    Parameters
    ----------
    rho_meta   : float — metamaterial density kg m⁻³ (must be > 0)
    rho_host   : float — host medium density kg m⁻³ (must be > 0)
    kappa_meta : float — metamaterial bulk modulus Pa (must be > 0)
    kappa_host : float — host bulk modulus Pa (must be > 0)

    Returns
    -------
    Z_ratio : float — impedance ratio (1.0 = perfect match)
    """
    for name, v in [("rho_meta", rho_meta), ("rho_host", rho_host),
                    ("kappa_meta", kappa_meta), ("kappa_host", kappa_host)]:
        if v <= 0.0:
            raise ValueError(f"{name} must be > 0, got {v!r}")
    Z_meta = math.sqrt(rho_meta * kappa_meta)
    Z_host = math.sqrt(rho_host * kappa_host)
    return float(Z_meta / Z_host)


def cloaking_phi_efficiency(phi_scattered: float, phi_incident: float) -> float:
    """Cloaking efficiency as reduction in scattered φ.

    efficiency = 1 − phi_scattered / (phi_incident + ε)

    Parameters
    ----------
    phi_scattered : float — scattered field φ (must be ≥ 0)
    phi_incident  : float — incident field φ (must be ≥ 0)

    Returns
    -------
    efficiency : float ∈ [0, 1]
    """
    if phi_scattered < 0.0:
        raise ValueError(f"phi_scattered must be ≥ 0, got {phi_scattered!r}")
    if phi_incident < 0.0:
        raise ValueError(f"phi_incident must be ≥ 0, got {phi_incident!r}")
    return float(np.clip(1.0 - phi_scattered / (phi_incident + _EPS), 0.0, 1.0))


def epsilon_phi_near_zero(epsilon_r: float, tolerance: float = 0.1) -> bool:
    """Whether the permittivity is in the epsilon-near-zero regime.

    ENZ ↔ |ε_r| < tolerance

    Parameters
    ----------
    epsilon_r : float — relative permittivity
    tolerance : float — ENZ threshold (default 0.1, must be > 0)

    Returns
    -------
    is_ENZ : bool
    """
    if tolerance <= 0.0:
        raise ValueError(f"tolerance must be > 0, got {tolerance!r}")
    return bool(abs(epsilon_r) < tolerance)


def hyperbolic_phi_dispersion(k_x: float, k_z: float,
                               epsilon_x: float, epsilon_z: float,
                               omega: float, c: float = 3e8) -> float:
    """Dispersion relation check for a hyperbolic metamaterial.

    k_x²/ε_z + k_z²/ε_x = ω²/c²

    Returns residual (0 = on dispersion surface).

    Parameters
    ----------
    k_x, k_z   : float — wavevector components m⁻¹
    epsilon_x  : float — permittivity along x (non-zero)
    epsilon_z  : float — permittivity along z (non-zero)
    omega      : float — angular frequency rad s⁻¹ (must be > 0)
    c          : float — speed of light m s⁻¹ (default 3e8)

    Returns
    -------
    residual : float — dispersion residual
    """
    if abs(epsilon_x) < _EPS or abs(epsilon_z) < _EPS:
        raise ValueError("epsilon_x and epsilon_z must be non-zero")
    if omega <= 0.0:
        raise ValueError(f"omega must be > 0, got {omega!r}")
    lhs = k_x ** 2 / epsilon_z + k_z ** 2 / epsilon_x
    rhs = (omega / c) ** 2
    return float(lhs - rhs)


def nonlinear_phi_metamaterial(phi_input: float, chi3: float) -> float:
    """Third-order nonlinear φ response.

    phi_out = phi_input × (1 + chi3 × phi_input²)

    Parameters
    ----------
    phi_input : float — input field φ amplitude (must be ≥ 0)
    chi3      : float — third-order susceptibility (can be positive or negative)

    Returns
    -------
    phi_out : float
    """
    if phi_input < 0.0:
        raise ValueError(f"phi_input must be ≥ 0, got {phi_input!r}")
    return float(phi_input * (1.0 + chi3 * phi_input ** 2))


def topological_phi_insulator(phi_bulk: float, phi_surface: float,
                               n_surface_states: int) -> float:
    """Total conducting φ of a topological insulator (surface + bulk).

    phi_total = phi_surface × n_surface_states + phi_bulk × (1 − is_gapped)

    We model as phi_surface contribution only (phi_bulk = 0 in topological gap).

    Parameters
    ----------
    phi_bulk          : float — bulk contribution (should be ~0 in gap, must be ≥ 0)
    phi_surface       : float — surface state φ per state (must be ≥ 0)
    n_surface_states  : int   — number of topological surface states (must be ≥ 0)

    Returns
    -------
    phi_total : float
    """
    if phi_bulk < 0.0:
        raise ValueError(f"phi_bulk must be ≥ 0, got {phi_bulk!r}")
    if phi_surface < 0.0:
        raise ValueError(f"phi_surface must be ≥ 0, got {phi_surface!r}")
    if n_surface_states < 0:
        raise ValueError(f"n_surface_states must be ≥ 0, got {n_surface_states!r}")
    return float(phi_surface * n_surface_states + phi_bulk)


def phi_plasmon_resonance(lambda_nm: float, n_metal: float,
                           n_dielectric: float) -> float:
    """Localised surface plasmon resonance condition.

    Resonance when Re(ε_metal) = −2 × ε_dielectric.
    Returns proximity to this condition.

    phi_spr = |n_metal² + 2 × n_dielectric²|   (smaller → closer to resonance)

    Parameters
    ----------
    lambda_nm    : float — wavelength nm (must be > 0)
    n_metal      : float — complex refractive index real part of metal (can be negative)
    n_dielectric : float — dielectric refractive index (must be > 0)

    Returns
    -------
    phi_spr : float — resonance proximity (0 = exact resonance)
    """
    if lambda_nm <= 0.0:
        raise ValueError(f"lambda_nm must be > 0, got {lambda_nm!r}")
    if n_dielectric <= 0.0:
        raise ValueError(f"n_dielectric must be > 0, got {n_dielectric!r}")
    eps_metal = n_metal ** 2
    eps_dielectric = n_dielectric ** 2
    return float(abs(eps_metal + 2.0 * eps_dielectric))
