# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Modular positional primitives used by the architecture.

The default model uses exact integer rotations and a learned scalar-bank
distance bias on the Z_74 lattice (`toroidal_geometry.py`), rather than
continuous sinusoids:

1. **Toroidal rotary encoding** (``toroidal_rotation_table``): each pair of
   query/key channels is rotated by an *exact* phase index
   ``wrap(step_k * position)`` on Z_74, instead of a continuous frequency.
   Because rotation is a group action, ``q'_i . k'_j`` depends only on
   ``(i - j) mod period_k`` — relative position is carried by rotation
   composition, exactly as in RoPE (Su et al., 2021), but every angle is one
   of 74 exact lattice points and each pair's orbit period
   (``74 / gcd(step_k, 74)``) is a *finite wraparound*: tokens far apart in
   raw index have identical rotary phases after a full orbit; this is finite
   modular aliasing, not a physical information-flow claim.

2. **Learned scalar-bank relative bias**
   (``toroidal_relative_bias_indices``): per-head bias keyed by circular
   distance between the scalar outputs of ``position_bank``. Although
   ``position_code`` starts with two modular coordinates, the bias does not
   retain or independently use those axes; the scalar projection is periodic
   and can alias distinct raw positions.

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
    position_code,
    wrap,
)

__all__ = [
    "rotation_steps_for_dim",
    "toroidal_rotation_table",
    "apply_toroidal_rotation",
    "toroidal_relative_bias_indices",
    "rotation_orbit_periods",
    "relative_distance",
    "modular_alias_diagnostics",
]


def rotation_steps_for_dim(head_dim: int) -> np.ndarray:
    """One Z_74 rotation step per (even, odd) channel pair, alternating braid strands.

    Pair ``k`` uses step ``5*(k+1)`` if ``k`` is even, ``7*(k+1)`` if odd —
    both braid windings contribute steps at increasing "frequency" (shorter
    orbit period), mirroring how standard sinusoidal/RoPE encodings assign
    geometrically increasing frequencies to successive channel pairs.
    """
    if head_dim <= 0 or head_dim % 2 != 0:
        raise ValueError("head_dim must be positive and even (rotation acts on channel pairs)")
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


def _collision_summary(values: list[object]) -> dict[str, object]:
    counts: dict[object, int] = {}
    first_position: dict[object, int] = {}
    first_collision: list[int] | None = None
    for position, value in enumerate(values):
        if value in counts and first_collision is None:
            first_collision = [first_position[value], position]
        else:
            first_position[value] = position
        counts[value] = counts.get(value, 0) + 1
    collision_pairs = sum(count * (count - 1) // 2 for count in counts.values())
    return {
        "unique_values": len(counts),
        "collision_pair_count": collision_pairs,
        "first_collision_positions": first_collision,
    }


def modular_alias_diagnostics(seq_len: int, head_dim: int) -> dict[str, object]:
    """Summarize phase, two-coordinate code, and scalar-bank aliases.

    Counts are exact for the requested finite position range. The torus code
    and bank reports intentionally remain separate: the bank is a scalar
    projection of the two-coordinate code, not an independent-axis encoding.
    """
    if seq_len < 1:
        raise ValueError("seq_len must be positive")
    steps = rotation_steps_for_dim(head_dim)
    positions = np.arange(seq_len, dtype=np.int64)
    phase_reports = []
    for pair, step in enumerate(steps):
        phases = ((positions * int(step)) % LATTICE_ORDER).tolist()
        report = _collision_summary(phases)
        report.update(
            pair_index=pair,
            step=int(step),
            orbit_period=orbit_period(int(step)),
        )
        phase_reports.append(report)

    codes = [position_code(i) for i in range(seq_len)]
    banks = [position_bank(i) for i in range(seq_len)]
    return {
        "seq_len": seq_len,
        "head_dim": head_dim,
        "rotation_pairs": phase_reports,
        "two_coordinate_torus_code": _collision_summary(codes),
        "scalar_bank_projection": {
            **_collision_summary(banks),
            "source_coordinate_count": 2,
            "output_coordinate_count": 1,
        },
    }
