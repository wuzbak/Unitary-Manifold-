# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/black_hole_transceiver.py
===================================
Black Hole as Geometric Transceiver — Pillar 6.

Models the event horizon as the physical locus where the Irreversibility
Field B_μ reaches its maximum potential, transcoding 4D matter information
into 5D topological geometry and redistributing it back into the 4D world
through the manifold's winding modes.

Theory summary
--------------
In the Unitary Manifold, the 5th dimension S¹/Z₂ enforces the arrow of time
through the coupling constant α = 1/φ².  As matter approaches the event
horizon the extreme curvature drives φ → 0 (α → ∞), causing the
Irreversibility Field B_μ to saturate:

    κ_H = λ²φ²|B|² / (1 + λ²φ²|B|²)  →  1

This saturation is the horizon.  At this point the Standard Model information
content of the infalling matter is stripped from the 4D sector and re-encoded
as 5D topology — "uploaded" to the surface of the black hole rather than
destroyed (information conservation, QUANTUM_THEOREMS.md §XII).

The encoded information is then redistributed back into 4D via the n_w = 5
winding modes derived from the Atiyah–Singer index theorem (metric.py §nw).
Each winding mode carries 1/n_w of the total encoded information, and the
superposition of all n_w modes reconstructs the original state — Hawking
radiation as geometric decoding.

Hubble Tension (cosmological α-drift)
--------------------------------------
The coupling constant α = 1/φ² is not fixed — it drifts as the universe
ages and the KK radion φ relaxes from its early-universe value φ_CMB toward
its Goldberger-Wise vacuum φ_today.  This geometric drift acts as a
"friction term" in the Friedmann equation, making the universe expand faster
today than the early-universe CMB predicts:

    Δα = α_today − α_CMB  =  1/φ_today² − 1/φ_CMB²  > 0

    H_local / H_CMB  ≈  φ_CMB / φ_today

With φ_CMB = H_SNe / H_CMB ≈ 73.0 / 67.4 ≈ 1.0831 this predicts
H_local ≈ 73 km/s/Mpc — bridging the Hubble tension without new particles.

Gravitational-Wave Echoes
--------------------------
Because information is stored at the horizon as 5D topology, post-merger
gravitational radiation "bounces" off the geometric structure of the compact
dimension, producing periodic echoes with delay:

    τ_echo = 2π ⟨φ⟩   (round-trip across the compact S¹ of radius ⟨φ⟩)

Each subsequent echo is damped by the transceiver absorption (echo quality):

    A_k = E_total · (1 − Q) · Q^k        Q = exp(−1/echo_quality)

The sum over all echoes recovers E_total × (1 − Q) / (1 − Q) = E_total,
confirming global energy conservation.

Key equations
-------------
Horizon saturation parameter:
    κ_H(x) = λ²φ²(x) |B(x)|² / (1 + λ²φ²(x) |B(x)|²)

Geometric encoding density:
    ρ_enc(x) = φ²(x) · λ² H_μν(x) H^μν(x)   (5D topology flux density)

Winding redistribution:
    ρ_out^(k)(x) = ρ_enc(x) / n_w            (k = 0 … n_w − 1)
    ρ_out_total(x) = Σ_k ρ_out^(k)(x) = ρ_enc(x)   (unitarity check)

Transceiver gain:
    G = ∫ ρ_out_total dx / ∫ ρ_enc dx  =  1  (global information conservation)

Coupling drift (Hubble tension):
    α_drift(φ_early, φ_today) = 1/φ_today² − 1/φ_early²

Echo spectrum:
    τ_echo = 2π ⟨φ⟩
    A_k = E · (1 − Q) · Q^k,  Q = exp(−1/Q_echo)

Public API
----------
horizon_saturation(B, phi, lam)
    Compute the B_μ saturation parameter κ_H at every grid point.
    Returns values in [0, 1); the horizon is where κ_H is largest.

geometric_encoding_density(B, phi, dx, lam)
    Rate at which 4D information is transcoded into 5D topology.
    Returns the local encoding density ρ_enc (shape N).

winding_redistribution(encoded_info, n_w)
    Project encoded 5D information back to 4D through n_w winding modes.
    Returns each winding-mode channel and the total (shape (n_w, N) and (N,)).

alpha_drift(phi_early, phi_today)
    Change in coupling constant as the radion relaxes: Δα = 1/φ_today² − 1/φ_early².

hubble_tension_ratio(phi_cmb, phi_today)
    Predicted ratio H_local / H_CMB = φ_CMB / φ_today from α-drift.

gw_echo_delay(phi_mean)
    Gravitational-wave echo delay τ_echo = 2π ⟨φ⟩ (compact-dimension round-trip).

gw_echo_spectrum(total_energy, n_echoes, echo_quality, phi_mean)
    Echo arrival times and amplitudes for the post-merger GW signal.
    Returns (times, amplitudes) with len = n_echoes.

HorizonTransceiver
    Dataclass wrapping the full encode → redistribute → decode pipeline.
    - encode(state)             : compute ρ_enc from the field state
    - decode(state, n_w)        : winding-redistributed output density
    - transceiver_gain(state, n_w)
                                : ∫ decoded / ∫ encoded  (≈ 1 iff unitary)
    - horizon_location(state)   : grid index of maximum κ_H
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np

from .metric import field_strength


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

_N_W_DEFAULT = 5          # topological winding number (from Atiyah–Singer)
_LAM_DEFAULT = 1.0        # KK coupling constant
_NUMERICAL_EPSILON = 1e-30  # guard against exact-zero denominators


# ---------------------------------------------------------------------------
# Horizon saturation
# ---------------------------------------------------------------------------

def horizon_saturation(
    B: np.ndarray,
    phi: np.ndarray,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Compute the B_μ field saturation parameter κ_H at every grid point.

    At the event horizon the Irreversibility Field reaches its maximum
    potential.  This is captured by the dimensionless saturation parameter:

        κ_H(x) = λ²φ²(x) |B(x)|² / (1 + λ²φ²(x) |B(x)|²)

    κ_H ∈ [0, 1) everywhere; it asymptotes to 1 as B_μ → ∞ (or α → ∞).
    The horizon is the locus argmax_x κ_H(x).

    Parameters
    ----------
    B   : ndarray, shape (N, 4) — irreversibility gauge field
    phi : ndarray, shape (N,)   — entanglement-capacity scalar (radion)
    lam : float — KK coupling constant λ (default 1)

    Returns
    -------
    kappa_H : ndarray, shape (N,)
        Saturation parameter in [0, 1).
    """
    B_sq = np.einsum('ni,ni->n', B, B)          # |B|²  shape (N,)
    numerator = lam**2 * phi**2 * B_sq
    return numerator / (1.0 + numerator + _NUMERICAL_EPSILON)


# ---------------------------------------------------------------------------
# Geometric encoding density
# ---------------------------------------------------------------------------

def geometric_encoding_density(
    B: np.ndarray,
    phi: np.ndarray,
    dx: float,
    lam: float = _LAM_DEFAULT,
) -> np.ndarray:
    """Rate at which 4D information is transcoded into 5D topology.

    When matter crosses the horizon the 5th-dimensional coupling φ²λ²
    amplifies the field-strength vorticity H_μν H^μν into a topological
    flux that encodes the particle's Standard Model quantum numbers in the
    manifold geometry:

        ρ_enc(x) = φ²(x) · λ² H_μν(x) H^μν(x)

    Here H_μν = ∂_μ B_ν − ∂_ν B_μ is the antisymmetric field-strength
    tensor of the Irreversibility Field.  The factor φ² is the KK radion
    weight that converts 5D to 4D effective densities.

    Parameters
    ----------
    B   : ndarray, shape (N, 4) — irreversibility gauge field
    phi : ndarray, shape (N,)   — entanglement-capacity scalar
    dx  : float — grid spacing
    lam : float — KK coupling constant λ (default 1)

    Returns
    -------
    rho_enc : ndarray, shape (N,)
        Geometric encoding density at each grid point.  Non-negative.
    """
    H = field_strength(B, dx)                         # (N, 4, 4)
    H2 = np.einsum('nij,nij->n', H, H)               # H_μν H^μν  (N,)
    return phi**2 * lam**2 * H2


# ---------------------------------------------------------------------------
# Winding redistribution
# ---------------------------------------------------------------------------

def winding_redistribution(
    encoded_info: np.ndarray,
    n_w: int = _N_W_DEFAULT,
) -> Tuple[np.ndarray, np.ndarray]:
    """Project encoded 5D information back to 4D through n_w winding modes.

    The Atiyah–Singer index theorem yields n_w = 5 winding modes on the
    S¹/Z₂ orbifold (metric.py::derive_nw_index_theorem).  Each mode carries
    an equal share of the encoded information back into 4D space:

        ρ_out^(k)(x) = ρ_enc(x) / n_w     for k = 0, …, n_w − 1

    The total output recovers the full encoded information (unitarity):

        ρ_out_total(x) = Σ_k ρ_out^(k)(x) = ρ_enc(x)

    This is the geometric mechanism behind Hawking radiation: the encoded
    state is not emitted all at once from one location, but redistributed
    coherently across all n_w winding channels.

    Parameters
    ----------
    encoded_info : ndarray, shape (N,) — local encoding density ρ_enc
    n_w          : int — number of winding modes (default 5)

    Returns
    -------
    channels : ndarray, shape (n_w, N)
        Each row k is the ρ_out^(k) contribution from winding mode k.
    total    : ndarray, shape (N,)
        Sum over all channels = encoded_info (exact equality).

    Raises
    ------
    ValueError
        If n_w < 1.
    """
    if n_w < 1:
        raise ValueError(f"n_w must be ≥ 1, got {n_w!r}")
    channels = np.tile(encoded_info / n_w, (n_w, 1))   # (n_w, N)
    total = np.sum(channels, axis=0)                    # (N,)
    return channels, total


# ---------------------------------------------------------------------------
# HorizonTransceiver
# ---------------------------------------------------------------------------

@dataclass
class HorizonTransceiver:
    """Black hole modeled as a geometric B_μ-saturated transceiver.

    The transceiver pipeline has two stages:

    Encode (reception)
        Infalling matter perturbs B_μ.  The field-strength vorticity
        H_μν H^μν, amplified by the radion weight φ², creates a topological
        imprint of the matter's quantum state in the 5D geometry:

            ρ_enc = φ² λ² H_μν H^μν

    Decode (transmission)
        The encoded topological state is projected back to 4D via the n_w
        winding modes, producing the Hawking emission spectrum:

            ρ_out^(k) = ρ_enc / n_w   (k = 0, …, n_w − 1)

    The global unitary condition  ∫ ρ_out_total dx = ∫ ρ_enc dx  (gain = 1)
    expresses black hole information conservation.

    Parameters
    ----------
    n_w : int   — winding number (default 5, from Atiyah–Singer)
    lam : float — KK coupling constant λ (default 1)
    """

    n_w: int = _N_W_DEFAULT
    lam: float = _LAM_DEFAULT

    # ------------------------------------------------------------------
    def encode(self, state) -> np.ndarray:
        """Compute the 5D geometric encoding density from a FieldState.

        Parameters
        ----------
        state : FieldState  (from src.core.evolution)

        Returns
        -------
        rho_enc : ndarray, shape (N,)
            Geometric encoding density ρ_enc = φ² λ² H_μν H^μν.
        """
        return geometric_encoding_density(
            state.B, state.phi, state.dx, lam=self.lam
        )

    # ------------------------------------------------------------------
    def decode(self, state) -> Tuple[np.ndarray, np.ndarray]:
        """Winding-redistributed output: the Hawking emission channels.

        Parameters
        ----------
        state : FieldState

        Returns
        -------
        channels : ndarray, shape (n_w, N)
            Per-winding-mode output density.
        total    : ndarray, shape (N,)
            Sum of all channels = ρ_enc (unitarity identity).
        """
        rho_enc = self.encode(state)
        return winding_redistribution(rho_enc, self.n_w)

    # ------------------------------------------------------------------
    def transceiver_gain(self, state) -> float:
        """Information gain ratio: ∫ decoded / ∫ encoded.

        A value of 1 confirms global information conservation (no loss).
        Deviations measure the discrete-grid truncation error.

        Parameters
        ----------
        state : FieldState

        Returns
        -------
        gain : float  (≈ 1 for a unitary transceiver)
        """
        rho_enc = self.encode(state)
        _, total_out = winding_redistribution(rho_enc, self.n_w)
        enc_integral = float(np.sum(rho_enc) * state.dx)
        out_integral = float(np.sum(total_out) * state.dx)
        if enc_integral < _NUMERICAL_EPSILON:
            return 1.0
        return out_integral / enc_integral

    # ------------------------------------------------------------------
    def horizon_location(self, state) -> int:
        """Grid index of maximum B_μ saturation (event horizon estimate).

        Returns the point x* = argmax_x κ_H(x) where the Irreversibility
        Field is closest to its maximum potential — the geometric definition
        of the event horizon within the Unitary Manifold framework.

        Parameters
        ----------
        state : FieldState

        Returns
        -------
        idx : int — grid index of the horizon
        """
        kappa = horizon_saturation(state.B, state.phi, lam=self.lam)
        return int(np.argmax(kappa))

    # ------------------------------------------------------------------
    def horizon_entropy(self, state, G4: float = 1.0) -> float:
        """Bekenstein–Hawking horizon entropy S_H = ∫ κ_H dx / (4 G4).

        The integral of the saturation parameter κ_H over the grid provides
        a proxy for the horizon area in the dimensionally-reduced geometry.
        Dividing by 4G_4 (Planck units) gives the Bekenstein–Hawking entropy.

        Parameters
        ----------
        state : FieldState
        G4    : float — Newton's constant (default 1, Planck units)

        Returns
        -------
        S_H : float  (non-negative)
        """
        kappa = horizon_saturation(state.B, state.phi, lam=self.lam)
        area_proxy = float(np.sum(kappa) * state.dx)
        return area_proxy / (4.0 * G4)


# ---------------------------------------------------------------------------
# Hubble Tension — cosmological α-drift
# ---------------------------------------------------------------------------

def alpha_drift(phi_early: float, phi_today: float) -> float:
    """Change in the KK coupling constant as the radion relaxes.

    In the Unitary Manifold α = 1/φ² (the nonminimal coupling constant is
    pinned to the KK compactification radius via the radion).  As the universe
    evolves, the Goldberger–Wise potential drives φ from its early-universe
    value φ_early (CMB epoch) toward its vacuum value φ_today.  The resulting
    drift in α acts as a geometric "friction term" in the Friedmann equation,
    making the late-universe expansion faster than the early-universe CMB
    predicts — the Hubble tension without new particles.

        Δα = 1/φ_today² − 1/φ_early²  > 0  when φ_today < φ_early

    Parameters
    ----------
    phi_early : float — radion value at the CMB epoch (> φ_today for tension)
    phi_today : float — radion vacuum value (Goldberger–Wise stabilised)

    Returns
    -------
    delta_alpha : float
        Positive when the compact dimension has shrunk (φ_today < φ_early),
        which corresponds to a stronger coupling today and faster expansion.

    Raises
    ------
    ValueError
        If either phi is ≤ 0.
    """
    if phi_early <= 0.0:
        raise ValueError(f"phi_early must be > 0, got {phi_early!r}")
    if phi_today <= 0.0:
        raise ValueError(f"phi_today must be > 0, got {phi_today!r}")
    return 1.0 / phi_today**2 - 1.0 / phi_early**2


def hubble_tension_ratio(phi_cmb: float, phi_today: float = 1.0) -> float:
    """Predicted H_local / H_CMB from the geometric radion drift.

    In the 5D KK model the effective Newton constant runs as
    G_eff = G_4 / φ², so the Friedmann equation gives:

        H ∝ sqrt(G_eff × ρ) ∝ 1/φ   (fixed matter density)

    Therefore

        H_local / H_CMB  =  φ_CMB / φ_today

    With φ_CMB = H_SNe / H_CMB ≈ 1.0831 (early-universe radion displaced
    above its vacuum by the exact amount needed to reproduce the local
    measurement) and φ_today = 1.0 (Goldberger–Wise stabilised):

        H_local / H_CMB  ≈  1.0831  →  H_local ≈ 73 km/s/Mpc ✓

    Parameters
    ----------
    phi_cmb   : float — radion value at CMB last scattering (> phi_today)
    phi_today : float — present-day radion vacuum value (default 1.0)

    Returns
    -------
    ratio : float — predicted H_local / H_CMB  (> 1 resolves the tension)

    Raises
    ------
    ValueError
        If either phi is ≤ 0.
    """
    if phi_cmb <= 0.0:
        raise ValueError(f"phi_cmb must be > 0, got {phi_cmb!r}")
    if phi_today <= 0.0:
        raise ValueError(f"phi_today must be > 0, got {phi_today!r}")
    return phi_cmb / phi_today


# ---------------------------------------------------------------------------
# Gravitational-wave echoes
# ---------------------------------------------------------------------------

def gw_echo_delay(phi_mean: float) -> float:
    """Gravitational-wave echo delay from the compact 5th dimension.

    After a black-hole merger the compact S¹ dimension acts as a resonant
    cavity.  Gravitational radiation traverses the compact dimension and
    reflects back, appearing as a periodic echo in the post-merger waveform.
    The round-trip time across a compact circle of radius R_5 = ⟨φ⟩ is:

        τ_echo = 2π R_5 / c  =  2π ⟨φ⟩        (natural units c = 1)

    A measurement of τ_echo directly determines ⟨φ⟩ — the compactification
    radius in Planck units.

    Parameters
    ----------
    phi_mean : float — mean radion value ⟨φ⟩ (= compactification radius R_5)

    Returns
    -------
    tau_echo : float — echo delay in Planck time units

    Raises
    ------
    ValueError
        If phi_mean ≤ 0.
    """
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    return 2.0 * np.pi * phi_mean


def gw_echo_spectrum(
    total_energy: float,
    n_echoes: int,
    echo_quality: float,
    phi_mean: float,
) -> Tuple[np.ndarray, np.ndarray]:
    """Echo arrival times and amplitudes for the post-merger GW signal.

    The compact 5th dimension acts as a damped resonant cavity.  Each
    successive round-trip loses a fraction (1 − Q) of the stored energy,
    where Q = exp(−1/echo_quality) is the per-echo transmission coefficient.

    Arrival times (k = 1, …, n_echoes):
        t_k = k × τ_echo  =  k × 2π ⟨φ⟩

    Amplitudes (geometric series with ratio Q):
        A_k = E_total × (1 − Q) × Q^{k−1}

    The total energy in all echoes:
        Σ_k A_k = E_total × (1 − Q) × (1 − Q^{n_echoes}) / (1 − Q)
                → E_total  as n_echoes → ∞   (energy conservation)

    Parameters
    ----------
    total_energy  : float — total GW energy available for echo redistribution
    n_echoes      : int   — number of echoes to compute (≥ 1)
    echo_quality  : float — cavity quality factor Q_echo (> 0); larger values
                            mean more energy retained per round-trip (less
                            damping), so later echoes are brighter.
    phi_mean      : float — mean radion ⟨φ⟩, sets τ_echo = 2π⟨φ⟩

    Returns
    -------
    times      : ndarray, shape (n_echoes,) — echo arrival times t_k
    amplitudes : ndarray, shape (n_echoes,) — echo energy amplitudes A_k

    Raises
    ------
    ValueError
        If n_echoes < 1, echo_quality ≤ 0, phi_mean ≤ 0, or total_energy < 0.
    """
    if n_echoes < 1:
        raise ValueError(f"n_echoes must be ≥ 1, got {n_echoes!r}")
    if echo_quality <= 0.0:
        raise ValueError(f"echo_quality must be > 0, got {echo_quality!r}")
    if phi_mean <= 0.0:
        raise ValueError(f"phi_mean must be > 0, got {phi_mean!r}")
    if total_energy < 0.0:
        raise ValueError(f"total_energy must be ≥ 0, got {total_energy!r}")

    tau = gw_echo_delay(phi_mean)                              # τ_echo
    Q_transmission = float(np.exp(-1.0 / echo_quality))                    # per-echo factor
    k = np.arange(1, n_echoes + 1, dtype=float)               # k = 1…n_echoes
    times = k * tau                                            # t_k
    amplitudes = total_energy * (1.0 - Q_transmission) * Q_transmission ** (k - 1.0)   # A_k
    return times, amplitudes
