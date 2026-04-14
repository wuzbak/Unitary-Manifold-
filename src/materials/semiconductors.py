# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/materials/semiconductors.py
================================
Semiconductors as φ-Field Switching Devices — Pillar 26.
"""

from __future__ import annotations
import math
import numpy as np

_EPS = 1e-30
_k_B = 8.617333262e-5   # eV K⁻¹


def carrier_phi_density(N_c: float, E_F: float, E_c: float, T_K: float) -> float:
    """Electron carrier density via Boltzmann approximation.

    n = N_c × exp(−(E_c − E_F) / k_B T)

    Parameters
    ----------
    N_c  : float — effective density of states cm⁻³ (must be > 0)
    E_F  : float — Fermi level eV
    E_c  : float — conduction band edge eV (must be ≥ E_F for electron device)
    T_K  : float — temperature K (must be > 0)

    Returns
    -------
    n : float — electron density cm⁻³
    """
    if N_c <= 0.0:
        raise ValueError(f"N_c must be > 0, got {N_c!r}")
    if T_K <= 0.0:
        raise ValueError(f"T_K must be > 0, got {T_K!r}")
    return float(N_c * math.exp(-(E_c - E_F) / (_k_B * T_K)))


def dopant_phi_concentration(n_dopant: float, N_host: float) -> float:
    """Dopant fraction relative to host lattice sites.

    x = n_dopant / N_host

    Parameters
    ----------
    n_dopant : float — dopant atom density cm⁻³ (must be ≥ 0)
    N_host   : float — host lattice site density cm⁻³ (must be > 0)

    Returns
    -------
    x : float ∈ [0, 1]
    """
    if n_dopant < 0.0:
        raise ValueError(f"n_dopant must be ≥ 0, got {n_dopant!r}")
    if N_host <= 0.0:
        raise ValueError(f"N_host must be > 0, got {N_host!r}")
    return float(np.clip(n_dopant / N_host, 0.0, 1.0))


def pn_junction_phi(V_built_in: float, V_applied: float) -> float:
    """Effective φ barrier of a p-n junction.

    phi_barrier = V_built_in − V_applied

    Parameters
    ----------
    V_built_in : float — built-in potential (must be ≥ 0)
    V_applied  : float — forward bias voltage (positive → reduces barrier)

    Returns
    -------
    phi_barrier : float (clipped to 0)
    """
    if V_built_in < 0.0:
        raise ValueError(f"V_built_in must be ≥ 0, got {V_built_in!r}")
    return float(max(0.0, V_built_in - V_applied))


def transistor_phi_gain(I_collector: float, I_base: float) -> float:
    """Bipolar transistor current gain β.

    β = I_collector / (I_base + ε)

    Parameters
    ----------
    I_collector : float — collector current (must be ≥ 0)
    I_base      : float — base current (must be ≥ 0)

    Returns
    -------
    beta : float — current gain
    """
    if I_collector < 0.0:
        raise ValueError(f"I_collector must be ≥ 0, got {I_collector!r}")
    if I_base < 0.0:
        raise ValueError(f"I_base must be ≥ 0, got {I_base!r}")
    return float(I_collector / (I_base + _EPS))


def semiconductor_phi_noise(phi_mean: float, B_johnson: float,
                             B_flicker: float, f_Hz: float = 1.0) -> float:
    """Total semiconductor noise φ (Johnson + 1/f).

    noise² = B_johnson² + B_flicker² / f

    Parameters
    ----------
    phi_mean  : float — signal φ (used for context; unused in formula)
    B_johnson : float — Johnson-Nyquist noise (must be ≥ 0)
    B_flicker : float — flicker noise amplitude (must be ≥ 0)
    f_Hz      : float — frequency Hz (must be > 0)

    Returns
    -------
    noise : float — RMS noise
    """
    if B_johnson < 0.0:
        raise ValueError(f"B_johnson must be ≥ 0, got {B_johnson!r}")
    if B_flicker < 0.0:
        raise ValueError(f"B_flicker must be ≥ 0, got {B_flicker!r}")
    if f_Hz <= 0.0:
        raise ValueError(f"f_Hz must be > 0, got {f_Hz!r}")
    return float(math.sqrt(B_johnson ** 2 + B_flicker ** 2 / f_Hz))


def solar_cell_phi_efficiency(J_sc: float, V_oc: float,
                               FF: float, P_incident: float) -> float:
    """Solar cell power conversion efficiency.

    η = J_sc × V_oc × FF / P_incident

    Parameters
    ----------
    J_sc        : float — short-circuit current density mA cm⁻² (must be ≥ 0)
    V_oc        : float — open-circuit voltage V (must be ≥ 0)
    FF          : float — fill factor ∈ (0, 1]
    P_incident  : float — incident power density mW cm⁻² (must be > 0)

    Returns
    -------
    eta : float ∈ [0, 1]
    """
    if J_sc < 0.0:
        raise ValueError(f"J_sc must be ≥ 0, got {J_sc!r}")
    if V_oc < 0.0:
        raise ValueError(f"V_oc must be ≥ 0, got {V_oc!r}")
    if not (0.0 < FF <= 1.0):
        raise ValueError(f"FF must be in (0,1], got {FF!r}")
    if P_incident <= 0.0:
        raise ValueError(f"P_incident must be > 0, got {P_incident!r}")
    return float(np.clip(J_sc * V_oc * FF / P_incident, 0.0, 1.0))


def led_phi_efficiency(phi_photons: float, phi_electrons: float) -> float:
    """LED external quantum efficiency.

    EQE = phi_photons / (phi_electrons + ε)

    Parameters
    ----------
    phi_photons  : float — emitted photon flux φ (must be ≥ 0)
    phi_electrons: float — injected electron flux φ (must be ≥ 0)

    Returns
    -------
    EQE : float ∈ [0, 1]
    """
    if phi_photons < 0.0:
        raise ValueError(f"phi_photons must be ≥ 0, got {phi_photons!r}")
    if phi_electrons < 0.0:
        raise ValueError(f"phi_electrons must be ≥ 0, got {phi_electrons!r}")
    return float(np.clip(phi_photons / (phi_electrons + _EPS), 0.0, 1.0))


def diode_phi_current(I_0: float, V: float, T_K: float = 300.0,
                       n_ideal: float = 1.0) -> float:
    """Shockley ideal diode equation.

    I = I_0 × (exp(eV / n k_B T) − 1)

    Parameters
    ----------
    I_0    : float — reverse saturation current (must be ≥ 0)
    V      : float — applied voltage
    T_K    : float — temperature K (default 300, must be > 0)
    n_ideal: float — ideality factor (default 1.0, must be > 0)

    Returns
    -------
    I : float — diode current
    """
    if I_0 < 0.0:
        raise ValueError(f"I_0 must be ≥ 0, got {I_0!r}")
    if T_K <= 0.0:
        raise ValueError(f"T_K must be > 0, got {T_K!r}")
    if n_ideal <= 0.0:
        raise ValueError(f"n_ideal must be > 0, got {n_ideal!r}")
    exponent = V / (n_ideal * _k_B * T_K)
    # clamp to avoid overflow
    exponent_clamped = min(exponent, 500.0)
    return float(I_0 * (math.exp(exponent_clamped) - 1.0))


def quantum_phi_dot(n_x: int, n_y: int, n_z: int,
                    L_nm: float, m_eff: float = 0.067) -> float:
    """Quantum dot confinement energy in eV.

    E = (ℏ²π²) / (2 m_eff m_e L²) × (n_x² + n_y² + n_z²)

    Parameters
    ----------
    n_x, n_y, n_z : int   — quantum numbers (each ≥ 1)
    L_nm          : float — dot size in nm (must be > 0)
    m_eff         : float — effective mass ratio (default 0.067 for GaAs)

    Returns
    -------
    E_eV : float — confinement energy in eV
    """
    for name, n in [("n_x", n_x), ("n_y", n_y), ("n_z", n_z)]:
        if n < 1:
            raise ValueError(f"{name} must be ≥ 1, got {n!r}")
    if L_nm <= 0.0:
        raise ValueError(f"L_nm must be > 0, got {L_nm!r}")
    hbar_eV_s = 6.582119569e-16   # eV·s
    m_e_kg = 9.1093837015e-31
    L_m = L_nm * 1e-9
    E_J = (math.pi ** 2 * (hbar_eV_s * 1.60218e-19) ** 2 *
           (n_x ** 2 + n_y ** 2 + n_z ** 2) /
           (2 * m_eff * m_e_kg * L_m ** 2))
    return float(E_J / 1.60218e-19)


def semiconductor_phi_bandgap(E_g0: float, T_K: float,
                               alpha: float = 5e-4, beta: float = 300.0) -> float:
    """Temperature-dependent band gap via Varshni equation.

    E_g(T) = E_g0 − alpha × T² / (T + beta)

    Parameters
    ----------
    E_g0  : float — 0 K band gap eV (must be ≥ 0)
    T_K   : float — temperature K (must be ≥ 0)
    alpha : float — Varshni α parameter eV K⁻¹ (default 5e-4)
    beta  : float — Varshni β parameter K (default 300)

    Returns
    -------
    E_g : float — band gap at temperature T (eV)
    """
    if E_g0 < 0.0:
        raise ValueError(f"E_g0 must be ≥ 0, got {E_g0!r}")
    if T_K < 0.0:
        raise ValueError(f"T_K must be ≥ 0, got {T_K!r}")
    return float(E_g0 - alpha * T_K ** 2 / (T_K + beta + _EPS))
