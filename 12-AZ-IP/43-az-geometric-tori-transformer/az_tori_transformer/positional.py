# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Geometric-tori positional structure: the architecture's core novelty.

Two independent geometric mechanisms carry positional information through
the network, both built from exact integer rotations/distances on the Z_74
phase lattice (`toroidal_geometry.py`) rather than continuous sinusoids:

1. **Toroidal rotary encoding** (``toroidal_rotation_table``): each pair of
   query/key channels is rotated by an *exact* phase index
   ``wrap(step_k * position)`` on Z_74, instead of a continuous frequency.
   Because rotation is a group action, ``q'_i . k'_j`` depends only on
   ``(i - j) mod period_k`` — relative position is carried by rotation
   composition, exactly as in RoPE (Su et al., 2021), but every angle is one
   of 74 exact lattice points and each pair's orbit period
   (``74 / gcd(step_k, 74)``) is a *finite wraparound*: tokens far apart in
   raw index become geometrically close again after a full orbit. That
   periodic wraparound — information "flowing" back around a torus instead
   of attenuating monotonically with distance — is the "tori information
   flowing" behaviour this product is named for.

2. **Toroidal relative attention bias** (``toroidal_relative_bias_indices``):
   a second, independent per-head bias keyed by the circular distance
   (``circular_distance``, which is exactly the orbifold-folded distance,
   see ``PSICAT_TOROIDAL_ISA_SPEC.md``) between the two-torus *bank*
   addresses (`toroidal_geometry.position_bank`) of a query/key pair. Because
   the bank address is itself a modular combination of two windings, two
   sequence positions that are far apart in raw index can land on nearby (or
   identical) bank addresses — a second, independent channel through which
   non-adjacent tokens can be pulled geometrically close.

Both mechanisms are ADJACENT TRACK architecture choices: they are motivated
by, and reuse the exact arithmetic of, the repository's existing (5, 7)
braid-winding / Z_74 lattice constants, but neither is a hardgate physics
claim, and no claim is made that either outperforms standard RoPE or T5
relative bias in general; see the product README's epistemic status.
"""

from __future__ import annotations

import numpy as np

from .toroidal_geometry import (
    BRAID_WINDINGS,
    LATTICE_ORDER,
    circular_distance,
    orbit_period,
    position_bank,
    wrap,
)

__all__ = [
    "rotation_steps_for_dim",
    "toroidal_rotation_table",
    "apply_toroidal_rotation",
    "toroidal_relative_bias_indices",
    "rotation_orbit_periods",
    "relative_distance",
]


def rotation_steps_for_dim(head_dim: int) -> np.ndarray:
    """One Z_74 rotation step per (even, odd) channel pair, alternating braid strands.

    Pair ``k`` uses step ``5*(k+1)`` if ``k`` is even, ``7*(k+1)`` if odd —
    both braid windings contribute steps at increasing "frequency" (shorter
    orbit period), mirroring how standard sinusoidal/RoPE encodings assign
    geometrically increasing frequencies to successive channel pairs.
    """
    if head_dim % 2 != 0:
        raise ValueError("head_dim must be even (rotation acts on channel pairs)")
    n_pairs = head_dim // 2
    steps = np.empty(n_pairs, dtype=np.int64)
    for k in range(n_pairs):
        base = BRAID_WINDINGS[k % 2]
        steps[k] = wrap(base * (k + 1))
    return steps


def toroidal_rotation_table(seq_len: int, head_dim: int) -> tuple[np.ndarray, np.ndarray]:
    """Precompute ``(cos, sin)`` tables of shape ``(seq_len, head_dim // 2)``.

    Each entry is ``cos(2*pi*wrap(step_k * i) / 74)`` / ``sin(...)`` — the
    exact Z_74 lattice angle for position ``i``, rotation-pair ``k``.
    """
    steps = rotation_steps_for_dim(head_dim)
    positions = np.arange(seq_len, dtype=np.int64).reshape(-1, 1)
    phase_index = (positions * steps.reshape(1, -1)) % LATTICE_ORDER
    angle = 2.0 * np.pi * phase_index.astype(np.float64) / LATTICE_ORDER
    return np.cos(angle), np.sin(angle)


def apply_toroidal_rotation(x: np.ndarray, cos: np.ndarray, sin: np.ndarray) -> np.ndarray:
    """Rotate the last axis of ``x`` (..., seq_len, head_dim) pairwise by (cos, sin).

    ``cos``/``sin`` have shape ``(seq_len, head_dim // 2)`` and broadcast over
    any leading (batch, head) axes of ``x``.
    """
    *lead, seq_len, head_dim = x.shape
    x_even = x[..., 0::2]
    x_odd = x[..., 1::2]
    rotated_even = x_even * cos - x_odd * sin
    rotated_odd = x_even * sin + x_odd * cos
    out = np.empty_like(x)
    out[..., 0::2] = rotated_even
    out[..., 1::2] = rotated_odd
    return out


def toroidal_relative_bias_indices(seq_len: int) -> np.ndarray:
    """``(seq_len, seq_len)`` matrix of circular distances between bank addresses.

    Values lie in ``[0, HALF_TURN]`` (37 buckets); a learned per-head bias
    table of that size can then be gathered by this index matrix.
    """
    banks = np.array([position_bank(i) for i in range(seq_len)], dtype=np.int64)
    diff = banks.reshape(-1, 1) - banks.reshape(1, -1)
    delta = diff % LATTICE_ORDER
    return np.minimum(delta, LATTICE_ORDER - delta)


def rotation_orbit_periods(head_dim: int) -> np.ndarray:
    """Orbit period (<=74) of each rotation-pair's step — diagnostic/report use."""
    steps = rotation_steps_for_dim(head_dim)
    return np.array([orbit_period(int(s)) for s in steps], dtype=np.int64)


def relative_distance(position_a: int, position_b: int) -> int:
    """Public helper: circular distance between two positions' bank addresses."""
    return circular_distance(position_bank(position_a), position_bank(position_b))
