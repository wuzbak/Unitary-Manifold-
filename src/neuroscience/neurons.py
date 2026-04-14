# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/neuroscience/neurons.py
============================
Neural Firing as φ-Field Threshold Dynamics — Pillar 20: Neuroscience.

Theory
------
In the Unitary Manifold framework a neuron is a localised φ-field oscillator.
The membrane potential V is the local φ-field amplitude; the action potential
fires when V crosses the irreversibility threshold V_th — the point at which
the entropic drive of the B_μ field can no longer be reversed:

    fire ↔  V ≥ V_th = φ_rest + k_B × B_μ

where k_B is the Boltzmann coupling constant.  The refractory period is the
relaxation time τ_r after which the φ-field returns to rest.
"""

from __future__ import annotations
import math
import numpy as np

_EPS = 1e-30


def action_potential_threshold(phi_rest: float, B_noise: float, k_B: float = 1.0) -> float:
    """Threshold membrane potential for action-potential firing.

    V_th = φ_rest + k_B × |B_μ|

    Parameters
    ----------
    phi_rest : float — resting membrane φ (must be finite)
    B_noise  : float — irreversibility-field noise floor (must be ≥ 0)
    k_B      : float — Boltzmann coupling (default 1.0, must be > 0)

    Returns
    -------
    V_th : float — threshold potential
    """
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    if k_B <= 0.0:
        raise ValueError(f"k_B must be > 0, got {k_B!r}")
    return float(phi_rest + k_B * B_noise)


def spike_frequency(phi_drive: float, V_th: float, tau_r: float) -> float:
    """Steady-state spike frequency of a tonically driven neuron.

    f = max(0,  (φ_drive − V_th)) / τ_r

    Parameters
    ----------
    phi_drive : float — sustained driving potential
    V_th      : float — action-potential threshold
    tau_r     : float — refractory period (must be > 0)

    Returns
    -------
    f : float — spike frequency (Hz-equivalent, ≥ 0)
    """
    if tau_r <= 0.0:
        raise ValueError(f"tau_r must be > 0, got {tau_r!r}")
    return float(max(0.0, phi_drive - V_th) / tau_r)


def refractory_period(tau_0: float, B_noise: float) -> float:
    """Effective refractory period modulated by irreversibility noise.

    τ_eff = τ_0 × (1 + B_noise)

    Higher irreversibility-field noise prolongs the refractory period by
    increasing the time needed to re-establish the resting φ fixed-point.

    Parameters
    ----------
    tau_0   : float — baseline refractory period (must be > 0)
    B_noise : float — B_μ noise level (must be ≥ 0)

    Returns
    -------
    tau_eff : float — effective refractory period (> 0)
    """
    if tau_0 <= 0.0:
        raise ValueError(f"tau_0 must be > 0, got {tau_0!r}")
    if B_noise < 0.0:
        raise ValueError(f"B_noise must be ≥ 0, got {B_noise!r}")
    return float(tau_0 * (1.0 + B_noise))


def membrane_phi_potential(V_rest: float, I_input: float, R_mem: float) -> float:
    """Steady-state membrane φ-potential under constant input current.

    V = V_rest + I_input × R_mem

    Parameters
    ----------
    V_rest  : float — resting potential
    I_input : float — injected current (φ-field drive)
    R_mem   : float — membrane resistance (must be > 0)

    Returns
    -------
    V : float — membrane potential
    """
    if R_mem <= 0.0:
        raise ValueError(f"R_mem must be > 0, got {R_mem!r}")
    return float(V_rest + I_input * R_mem)


def neural_noise_floor(kT: float, C_mem: float) -> float:
    """Johnson-Nyquist thermal noise floor of the membrane φ-field.

    σ_V = sqrt(kT / C_mem)

    Parameters
    ----------
    kT    : float — thermal energy k_B T (must be > 0)
    C_mem : float — membrane capacitance (must be > 0)

    Returns
    -------
    sigma_V : float — RMS voltage noise (≥ 0)
    """
    if kT <= 0.0:
        raise ValueError(f"kT must be > 0, got {kT!r}")
    if C_mem <= 0.0:
        raise ValueError(f"C_mem must be > 0, got {C_mem!r}")
    return float(math.sqrt(kT / C_mem))


def adaptation_current(phi_drive: float, tau_adapt: float, t: float) -> float:
    """Spike-frequency adaptation current decaying from initial drive.

    I_adapt(t) = φ_drive × exp(−t / τ_adapt)

    Parameters
    ----------
    phi_drive  : float — initial drive amplitude
    tau_adapt  : float — adaptation time constant (must be > 0)
    t          : float — elapsed time (must be ≥ 0)

    Returns
    -------
    I_adapt : float — adaptation current at time t (≥ 0)
    """
    if tau_adapt <= 0.0:
        raise ValueError(f"tau_adapt must be > 0, got {tau_adapt!r}")
    if t < 0.0:
        raise ValueError(f"t must be ≥ 0, got {t!r}")
    return float(abs(phi_drive) * math.exp(-t / tau_adapt))


def hodgkin_huxley_phi(V: float, V_Na: float, V_K: float,
                        g_Na: float, g_K: float, g_L: float, V_L: float) -> float:
    """Simplified Hodgkin-Huxley net ionic current in φ-field units.

    I_ion = g_Na(V − V_Na) + g_K(V − V_K) + g_L(V − V_L)

    Parameters
    ----------
    V    : float — current membrane potential
    V_Na : float — sodium reversal potential
    V_K  : float — potassium reversal potential
    g_Na : float — sodium conductance (must be ≥ 0)
    g_K  : float — potassium conductance (must be ≥ 0)
    g_L  : float — leak conductance (must be ≥ 0)
    V_L  : float — leak reversal potential

    Returns
    -------
    I_ion : float — net ionic current
    """
    for name, val in [("g_Na", g_Na), ("g_K", g_K), ("g_L", g_L)]:
        if val < 0.0:
            raise ValueError(f"{name} must be ≥ 0, got {val!r}")
    return float(g_Na * (V - V_Na) + g_K * (V - V_K) + g_L * (V - V_L))


def axon_phi_velocity(diameter_m: float, myelinated: bool = True) -> float:
    """Conduction velocity of a nerve impulse along an axon.

    Myelinated:   v = 5.5 × sqrt(diameter_m / 1e-6)  m/s  (empirical)
    Unmyelinated: v = 1.5 × (diameter_m / 1e-6)^0.5  m/s  (Cable theory)

    Parameters
    ----------
    diameter_m  : float — axon diameter in metres (must be > 0)
    myelinated  : bool  — whether the axon is myelinated (default True)

    Returns
    -------
    velocity : float — conduction velocity in m/s
    """
    if diameter_m <= 0.0:
        raise ValueError(f"diameter_m must be > 0, got {diameter_m!r}")
    d_um = diameter_m / 1e-6
    if myelinated:
        return float(5.5 * math.sqrt(d_um))
    return float(1.5 * math.sqrt(d_um))


def synaptic_phi_weight(base_weight: float, ltp_factor: float, ltd_factor: float) -> float:
    """Net synaptic φ-weight after LTP and LTD modulation.

    w_net = base_weight × (1 + ltp_factor − ltd_factor)

    Parameters
    ----------
    base_weight : float — initial synaptic weight (must be ≥ 0)
    ltp_factor  : float — long-term potentiation fractional increase (≥ 0)
    ltd_factor  : float — long-term depression fractional decrease (≥ 0)

    Returns
    -------
    w_net : float — net synaptic weight (clipped to 0 from below)
    """
    if base_weight < 0.0:
        raise ValueError(f"base_weight must be ≥ 0, got {base_weight!r}")
    return float(max(0.0, base_weight * (1.0 + ltp_factor - ltd_factor)))


def neural_phi_gain(phi_input: float, phi_threshold: float, gain_slope: float) -> float:
    """Sigmoidal φ-field gain function of a neuron.

    output = 1 / (1 + exp(−gain_slope × (φ_input − φ_threshold)))

    Parameters
    ----------
    phi_input     : float — input φ drive
    phi_threshold : float — half-activation threshold
    gain_slope    : float — steepness (must be > 0)

    Returns
    -------
    activation : float ∈ (0, 1)
    """
    if gain_slope <= 0.0:
        raise ValueError(f"gain_slope must be > 0, got {gain_slope!r}")
    return float(1.0 / (1.0 + math.exp(-gain_slope * (phi_input - phi_threshold))))
