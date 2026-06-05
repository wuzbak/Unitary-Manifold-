# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 511 — Braid Winding Number as a Dynamic Observable.

STATUS: BRAID_WINDING_OBSERVABLE_CERTIFIED

Closes the first structural gap identified in the dynamic irreversibility critique:
the codebase previously had no executable representation of the topological winding
number n_w as a live, queryable, integer-valued observable of the field state.

This pillar adds:
  - braid_winding_number(phi, dx) — module-level function in evolution.py
  - FieldState.initialize_dynamic_braid() — factory for topologically non-trivial ICs
  - FieldState.get_winding_number() — instance method wrapping the above function

Physical significance
---------------------
The braid winding number n_w is the integer topological charge of the (5, 7, 74)
Unitary Manifold triad.  In the 5D KK framework the winding sector is the carrier
of the irreversibility arrow: the direction of n_w evolution under the Chern-Simons
coupling k_CS = 74 determines whether a process is topologically forward or backward.

The previous code treated n_w as a *static background label* embedded in comments
and constants.  Pillar 511 promotes it to an *executable, field-level observable*
with a well-defined numerical algorithm and integer round-trip guarantee.

Mathematical definition
-----------------------
For a real scalar field φ(x) on a periodic 1-D grid, the winding number is the
integer winding of the phase-space vector (φ, −∂_x φ) around the origin:

    n_w = (1/2π) ∮ dθ   where θ(x) = arctan2(−∂_x φ, φ)

The integral is replaced by a sum of wrapped phase increments on the discrete grid.
For φ = A·cos(2π n_w x/L) the result equals n_w exactly (up to rounding of the
finite-difference gradient approximation with second-order accuracy).

Honest limitations
------------------
- The winding number is ill-defined when |φ| ≈ 0 AND |∂_x φ| ≈ 0 simultaneously
  at the same grid point (phase-space origin crossing).  In practice this requires
  amplitude → 0 uniformly, which does not occur for the bounded cosine modes used
  in the framework.
- The current implementation is 1+1D only (one spatial direction).  The 5D
  topological structure requires a full 5D winding number which remains an
  open theoretical gap (documented in FALLIBILITY.md §III).
- The integer quantisation relies on the discrete gradient approximation;
  for very small N or very high n_w (N < 4·n_w), accuracy degrades.
"""
from __future__ import annotations

from typing import Dict, List

__all__ = [
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "VERSION",
    "WINDING_ALGORITHM",
    "HONEST_LIMITATIONS",
    "pillar_report",
]

PILLAR_NUMBER: int = 511
PILLAR_STATUS: str = "BRAID_WINDING_OBSERVABLE_CERTIFIED"
PILLAR_TITLE: str = "Braid winding number promoted to dynamic executable observable"
VERSION: str = "v15.8"

WINDING_ALGORITHM: Dict[str, str] = {
    "step_1": "Compute gradient dphi = np.gradient(phi, dx, edge_order=2)",
    "step_2": "Compute phase angle theta = arctan2(-dphi, phi)",
    "step_3": "Close the loop: theta_closed = [theta..., theta[0]]",
    "step_4": "Compute increments d_theta = diff(theta_closed)",
    "step_5": "Phase-wrap: d_theta = (d_theta + pi) % (2*pi) - pi",
    "step_6": "Sum and round: n_w = round(sum(d_theta) / (2*pi))",
}

HONEST_LIMITATIONS: List[str] = [
    "Ill-defined when |phi| ~ 0 and |dphi| ~ 0 simultaneously.",
    "1D implementation only; 5D winding requires higher-dimensional extension.",
    "Requires N >= 4 * |n_w| for reliable quantisation.",
    "Relies on second-order finite-difference gradient; O(dx^2) accuracy.",
    "Does not track path history; only instantaneous winding of current state.",
]


def pillar_report() -> Dict[str, object]:
    """Return a machine-readable Pillar 511 status certificate."""
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "what_was_added": [
            "braid_winding_number(phi, dx) in src/core/evolution.py",
            "FieldState.initialize_dynamic_braid() factory",
            "FieldState.get_winding_number() instance method",
        ],
        "gap_closed": (
            "n_w was a static background label; it is now an executable "
            "integer-valued observable derived from the live field state."
        ),
        "honest_limitations": HONEST_LIMITATIONS,
        "winding_algorithm": WINDING_ALGORITHM,
        "cs_level_k": 74,
        "braid_triad": (5, 7, 74),
    }
