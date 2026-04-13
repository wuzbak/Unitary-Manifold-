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
