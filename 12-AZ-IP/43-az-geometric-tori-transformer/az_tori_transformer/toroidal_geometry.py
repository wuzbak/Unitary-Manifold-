# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Exact integer toroidal phase-lattice primitives for the Geometric Tori Transformer.

ADJACENT TRACK — software architecture, not a hardgate physics claim.

This module intentionally duplicates (rather than imports) the small set of
exact Z_74 lattice primitives already specified in
`12-AZ-IP/20-psicat-navigator/PSICAT_TOROIDAL_ISA_SPEC.md` and implemented in
`ox_navigator/engine/merlin_toroidal_geometry.py`, so that this product has
no hard runtime dependency on a sibling product. `tests/test_toroidal_geometry.py`
cross-checks this copy against the Navigator's own golden-vector export when
the sibling product is importable, so the two never silently drift apart.

Constants mirror the repository's hardgated physics constants (see
`src/core/` and the top-level ``README.md``):

* ``WINDING_NUMBER = 5`` and the companion braid winding ``7`` — the (5, 7)
  resonance pair selected by Planck n_s / birefringence data.
* ``K_CS = 74 = 5**2 + 7**2`` — the lattice order used throughout the
  Navigator's toroidal lane.
* ``TICK_PHASE_STEP = 24`` — the discrete Z_74 encoding of the Unitary
  Pentad's 12/37 cadence (``12/37 == 24/74``), used as one position-code
  coordinate step. It is not a physical velocity or sound speed; the
  downstream bank function projects the two-coordinate code to one scalar.
"""

from __future__ import annotations

import math
from typing import Sequence

WINDING_NUMBER = 5
COMPANION_WINDING = 7
K_CS = WINDING_NUMBER ** 2 + COMPANION_WINDING ** 2  # 74
LATTICE_ORDER = K_CS
HALF_TURN = LATTICE_ORDER // 2  # 37 — the orbifold fixed point / cut locus
BRAID_WINDINGS = (WINDING_NUMBER, COMPANION_WINDING)
TICK_PHASE_STEP = 24  # 12/37 == 24/74

if BRAID_WINDINGS[0] ** 2 + BRAID_WINDINGS[1] ** 2 != LATTICE_ORDER:
    raise RuntimeError("braid windings must satisfy n1**2 + n2**2 == k_cs")

__all__ = [
    "WINDING_NUMBER",
    "COMPANION_WINDING",
    "K_CS",
    "LATTICE_ORDER",
    "HALF_TURN",
    "BRAID_WINDINGS",
    "TICK_PHASE_STEP",
    "wrap",
    "circular_distance",
    "orbifold_fold",
    "braid_bank",
    "orbit_period",
    "position_code",
    "position_bank",
]


def wrap(index: int) -> int:
    return int(index) % LATTICE_ORDER


def circular_distance(a: int, b: int) -> int:
    """Geodesic distance on the circle Z_74, in [0, HALF_TURN]."""
    delta = (int(a) - int(b)) % LATTICE_ORDER
    return min(delta, LATTICE_ORDER - delta)


def orbifold_fold(a: int) -> int:
    """Project onto the S^1/Z_2 orbifold fundamental domain [0, 37]."""
    k = wrap(a)
    return k if k <= HALF_TURN else LATTICE_ORDER - k


def braid_bank(code: Sequence[int]) -> int:
    """``(5*theta1 + 7*theta2) mod 74`` — the static (5, 7) braid bank address."""
    if len(code) < 2:
        raise ValueError("braid bank requires at least two torus coordinates")
    return (BRAID_WINDINGS[0] * int(code[0]) + BRAID_WINDINGS[1] * int(code[1])) % LATTICE_ORDER


def orbit_period(step: int) -> int:
    step = wrap(step)
    if step == 0:
        return 1
    return LATTICE_ORDER // math.gcd(step, LATTICE_ORDER)


def position_code(position: int) -> tuple[int, int]:
    """Embed a sequence position as a point on the 2-torus Z_74 x Z_74.

    Using the braid windings directly as ``(wrap(5*i), wrap(7*i))`` would make
    ``braid_bank`` of that code identically zero for every ``i``, because
    ``5**2 + 7**2 == 74 == 0 (mod 74)`` by construction (the defining relation
    of ``K_CS``). The second coordinate instead uses the tick-phase step
    (``TICK_PHASE_STEP = 24``, the discrete encoding of the Pentad's 12/37
    cadence), which keeps the two-coordinate code non-degenerate. The
    subsequent scalar bank projection does not preserve independent axes.
    """
    return wrap(WINDING_NUMBER * position), wrap(TICK_PHASE_STEP * position)


def position_bank(position: int) -> int:
    """The scalar bank address of a sequence position's 2-torus code."""
    return braid_bank(position_code(position))
