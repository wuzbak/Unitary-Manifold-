# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
delay_field.py — Pillar 41: 5D Delay Field Model (DFM)

Provides a conceptual bridge for two conjectural Unitary Manifold identifications:
  1. φ = entanglement capacity (radion = √(causal delay through the 5th dimension))
  2. 5th dimension = irreversibility (causal asymmetry δτ ≥ 0 gives the arrow of time)

Also resolves Gemini Issue 4 (Ricci-flow time vs coordinate time double-counting).

All physical quantities are in natural (Planck) units.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

# ---------------------------------------------------------------------------
# Module-level constants (Planck units)
# ---------------------------------------------------------------------------
PHI_0_FTUM: float = 1.0          # FTUM fixed-point value of the radion
PHI_STAR: float = 1.0            # Equilibrium radion value (= PHI_0_FTUM)
N1_CANONICAL: int = 5            # First canonical braid winding number
N2_CANONICAL: int = 7            # Second canonical braid winding number
K_CS_CANONICAL: int = 74         # = N1² + N2² = 5² + 7²; birefringence datum
C_S_CANONICAL: float = 12.0 / 37.0  # Canonical braided sound speed c_s = (49-25)/74


# ---------------------------------------------------------------------------
# DFM-UM Bridge:  G₅₅ = φ² = δτ
# ---------------------------------------------------------------------------

def delay_from_phi(phi: float) -> float:
    """Return causal delay δτ = φ²."""
    return phi * phi


def phi_from_delay(delta_tau: float) -> float:
    """Return radion φ = √(δτ).

    Raises ValueError if delta_tau < 0 (acausal delay is unphysical).
    """
    if delta_tau < 0:
        raise ValueError(f"Causal delay δτ must be non-negative; got {delta_tau}")
    return math.sqrt(delta_tau)


def entanglement_capacity(phi: float) -> float:
    """Return entanglement capacity = φ² (identical to delay_from_phi)."""
    return phi * phi


# ---------------------------------------------------------------------------
# Gemini Issue 4 resolution: Ricci-flow time ↔ coordinate time
# ---------------------------------------------------------------------------

def ricci_flow_time_factor(phi: float) -> float:
    """Return Ω(φ) = 1/φ.

    Conversion factor: dt_coord = dt_ricci / φ.

    Raises ValueError if phi ≤ 0.
    """
    if phi <= 0:
        raise ValueError(f"Radion φ must be positive; got {phi}")
    return 1.0 / phi


def coord_time_from_ricci(t_ricci: float, phi: float) -> float:
    """Return coordinate time t_coord = t_ricci / φ."""
    if phi <= 0:
        raise ValueError(f"Radion φ must be positive; got {phi}")
    return t_ricci / phi


def ricci_from_coord_time(t_coord: float, phi: float) -> float:
    """Return Ricci-flow time t_ricci = t_coord × φ."""
    if phi <= 0:
        raise ValueError(f"Radion φ must be positive; got {phi}")
    return t_coord * phi


def gemini_issue4_correction(phi: float, t_ricci: float) -> dict[str, float]:
    """Compute the Gemini Issue 4 time-reckoning correction.

    Returns a dict with keys:
      t_coord      — coordinate time = t_ricci / φ
      t_ricci      — Ricci-flow time (input, echoed)
      omega        — Ω(φ) = 1/φ
      discrepancy  — |t_coord - t_ricci| / |t_ricci|  (fractional offset)
                     At φ = 1 (FTUM fixed point) this is exactly 0.
                     At φ ≠ 1 this equals |1/φ - 1|.
    """
    if phi <= 0:
        raise ValueError(f"Radion φ must be positive; got {phi}")
    t_coord = coord_time_from_ricci(t_ricci, phi)
    omega = ricci_flow_time_factor(phi)
    if t_ricci == 0.0:
        discrepancy = 0.0
    else:
        discrepancy = abs(t_coord - t_ricci) / abs(t_ricci)
    return {
        "t_coord": t_coord,
        "t_ricci": t_ricci,
        "omega": omega,
        "discrepancy": discrepancy,
    }


# ---------------------------------------------------------------------------
# Quantum delay statistics
# ---------------------------------------------------------------------------

def quantum_delay_variance(phi_mean: float, phi_spread: float) -> float:
    """Return Var(δτ) ≈ 4 φ_mean² φ_spread² (leading-order Gaussian propagation).

    At phi_spread = 0 the variance is exactly 0 (classical limit).
    """
    return 4.0 * phi_mean ** 2 * phi_spread ** 2


def decoherence_time(phi_mean: float, phi_spread: float) -> float:
    """Return τ_dec = φ_mean² / φ_spread.

    Raises ValueError if phi_spread ≤ 0.
    """
    if phi_spread <= 0:
        raise ValueError(f"phi_spread must be positive; got {phi_spread}")
    return phi_mean ** 2 / phi_spread


# ---------------------------------------------------------------------------
# Irreversibility and entropy
# ---------------------------------------------------------------------------

def irreversibility_measure(phi: float, phi_0: float = PHI_0_FTUM) -> float:
    """Return I = φ² / φ₀².

    I = 1 at φ = φ₀ (equilibrium), < 1 below, > 1 above.
    """
    return (phi / phi_0) ** 2


def entropy_production_rate(phi: float, phi_dot: float, phi_0: float = PHI_0_FTUM) -> float:
    """Return dS/dt = 2 φ φ̇ / φ₀².

    Zero when φ̇ = 0, positive (negative) when φ̇ > 0 (< 0).
    """
    return 2.0 * phi * phi_dot / phi_0 ** 2


# ---------------------------------------------------------------------------
# Consistency check
# ---------------------------------------------------------------------------

def dfm_um_consistency_check(phi: float, delta_tau: float, tol: float = 1e-10) -> bool:
    """Return True iff |φ² - δτ| / max(|δτ|, 1e-30) < tol."""
    denominator = max(abs(delta_tau), 1e-30)
    return abs(phi ** 2 - delta_tau) / denominator < tol


# ---------------------------------------------------------------------------
# Braided delay spectrum
# ---------------------------------------------------------------------------

def braided_delay_spectrum(n1: int, n2: int, k_cs: int) -> dict[str, float]:
    """Compute the two-mode braided delay spectrum.

    c_s = (n2² - n1²) / k_cs
    δτ_i = nᵢ × c_s
    φᵢ = √(|δτᵢ|)

    Returns dict: c_s, delta_tau_1, delta_tau_2, phi_1, phi_2.
    """
    c_s = (n2 ** 2 - n1 ** 2) / k_cs
    delta_tau_1 = n1 * c_s
    delta_tau_2 = n2 * c_s
    phi_1 = math.sqrt(abs(delta_tau_1))
    phi_2 = math.sqrt(abs(delta_tau_2))
    return {
        "c_s": c_s,
        "delta_tau_1": delta_tau_1,
        "delta_tau_2": delta_tau_2,
        "phi_1": phi_1,
        "phi_2": phi_2,
    }


# ---------------------------------------------------------------------------
# Causal arrow of time
# ---------------------------------------------------------------------------

def causal_arrow_of_time(phi_initial: float, phi_final: float) -> str:
    """Return 'forward', 'backward', or 'equilibrium' based on Δφ."""
    if phi_final > phi_initial:
        return "forward"
    if phi_final < phi_initial:
        return "backward"
    return "equilibrium"


# ---------------------------------------------------------------------------
# Summary convenience function
# ---------------------------------------------------------------------------

def dfm_summary(phi: float = PHI_STAR, t_ricci: float = 1.0) -> dict[str, float]:
    """Return a dict of all primary DFM-derived quantities for given φ and t_ricci."""
    correction = gemini_issue4_correction(phi, t_ricci)
    return {
        "phi": phi,
        "delta_tau": delay_from_phi(phi),
        "entanglement_capacity": entanglement_capacity(phi),
        "omega": ricci_flow_time_factor(phi),
        "t_coord": correction["t_coord"],
        "t_ricci": correction["t_ricci"],
        "discrepancy": correction["discrepancy"],
        "irreversibility": irreversibility_measure(phi),
        "entropy_production_rate_unit": entropy_production_rate(phi, 1.0),
    }
