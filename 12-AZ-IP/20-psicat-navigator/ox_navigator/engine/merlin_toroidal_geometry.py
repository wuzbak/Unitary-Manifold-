# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Exact toroidal phase-lattice core for non-smooth Merlin navigation.

ADJACENT TRACK (software emulation, not a hardgate physics claim).

The Navigator's discrete geometry is the phase lattice ``Z_74`` (k_cs = 5² + 7²)
on each circle of a torus ``T^m``.  On this lattice:

* unitary rotations are integer additions mod 74 (exact, zero drift, 7 bits);
* the S¹/Z₂ orbifold reflection ``θ → −θ`` has fixed points {0, 37} — these are
  the non-smooth creases; trajectories reflect there like elastic impacts;
* the flat-torus distance is piecewise linear, with Clarke-generalised
  gradients at coincidence (minimum) and at the cut locus (maximum);
* a purely unitary iteration never converges (it is periodic), so exits are
  explicit, non-unitary first-hitting read-outs;
* a bit-exact integer CORDIC emulator measures the drift that Cartesian
  fixed-point rotations accumulate, as the contrast case.
"""

from __future__ import annotations

import hashlib
import math
from functools import lru_cache
from typing import Any, Iterable, Sequence

import numpy as np

from .constants import K_CS, MERLIN_TICK_DENOMINATOR, MERLIN_TICK_NUMERATOR

LATTICE_ORDER = K_CS  # 74
HALF_TURN = LATTICE_ORDER // 2  # 37: orbifold fixed point and cut locus
BRAID_WINDINGS = (5, 7)
ORBIFOLD_FIXED_POINTS = (0, HALF_TURN)
# 12/37 cadence expressed on Z_74: 12/37 = 24/74.
TICK_PHASE_STEP = (MERLIN_TICK_NUMERATOR * LATTICE_ORDER) // MERLIN_TICK_DENOMINATOR
EXPECTED_RANDOM_CIRCULAR_DISTANCE = LATTICE_ORDER / 4.0
PHASE_INDEX_BITS = math.ceil(math.log2(LATTICE_ORDER))  # 7
DEFAULT_SKETCH_DIMS = 16
STATUS_LABEL = "ADJACENT_TRACK"

if BRAID_WINDINGS[0] ** 2 + BRAID_WINDINGS[1] ** 2 != LATTICE_ORDER:
    raise RuntimeError("braid windings must satisfy n1² + n2² = k_cs")


# ---------------------------------------------------------------------------
# Lattice arithmetic and metric
# ---------------------------------------------------------------------------

def wrap(index: int) -> int:
    return int(index) % LATTICE_ORDER


def circular_distance(a: int, b: int) -> int:
    delta = (int(a) - int(b)) % LATTICE_ORDER
    return min(delta, LATTICE_ORDER - delta)


def circular_distance_subdifferential(a: int, b: int) -> dict[str, Any]:
    """Clarke generalised gradient of ``d(·, b)`` at ``a`` (phase units).

    Away from the kinks the gradient is ±1.  At coincidence (a minimum) and at
    the cut locus (a maximum) the Clarke gradient is the interval [-1, 1]; both
    points are Clarke-stationary, so stationarity alone cannot tell a minimum
    from a maximum.  Directional derivatives resolve this.
    """
    delta = (int(a) - int(b)) % LATTICE_ORDER
    if delta == 0:
        return {
            "kind": "coincidence_minimum",
            "clarke_gradient": [-1, 1],
            "clarke_stationary": True,
            "is_minimum": True,
            "descent_directions": [],
        }
    if delta == HALF_TURN:
        return {
            "kind": "cut_locus_maximum",
            "clarke_gradient": [-1, 1],
            "clarke_stationary": True,
            "is_minimum": False,
            "descent_directions": [-1, 1],
        }
    gradient = 1 if delta < HALF_TURN else -1
    return {
        "kind": "smooth",
        "clarke_gradient": [gradient, gradient],
        "clarke_stationary": False,
        "is_minimum": False,
        "descent_directions": [-gradient],
    }


def toroidal_distance(code_a: Sequence[int], code_b: Sequence[int]) -> int:
    if len(code_a) != len(code_b):
        raise ValueError("torus codes must have equal dimension")
    return sum(circular_distance(a, b) for a, b in zip(code_a, code_b))


def toroidal_geodesic(code_a: Sequence[int], code_b: Sequence[int]) -> dict[str, Any]:
    """Shortest signed displacement on the flat L1 torus, with branch points.

    Coordinates sitting exactly on the cut locus admit two geodesic arcs; they
    are reported as ``branch_coordinates`` (the non-smooth geodesic fan).
    The returned displacement takes the positive orientation on each branch.
    """
    if len(code_a) != len(code_b):
        raise ValueError("torus codes must have equal dimension")
    displacement: list[int] = []
    branches: list[int] = []
    for index, (a, b) in enumerate(zip(code_a, code_b)):
        delta = (int(b) - int(a)) % LATTICE_ORDER
        if delta == HALF_TURN:
            branches.append(index)
            displacement.append(HALF_TURN)
        elif delta < HALF_TURN:
            displacement.append(delta)
        else:
            displacement.append(delta - LATTICE_ORDER)
    return {
        "length": sum(abs(step) for step in displacement),
        "displacement": displacement,
        "branch_coordinates": branches,
        "geodesic_branch_count": 2 ** len(branches),
    }


def braid_bank(code: Sequence[int]) -> int:
    """Static bank address ``(5·θ1 + 7·θ2) mod 74``.

    gcd(5, 74) = 1, so the map is surjective and every bank receives an equal
    share of uniformly distributed codes.
    """
    if len(code) < 2:
        raise ValueError("braid bank requires at least two torus coordinates")
    return (BRAID_WINDINGS[0] * int(code[0]) + BRAID_WINDINGS[1] * int(code[1])) % LATTICE_ORDER


# ---------------------------------------------------------------------------
# Exact unitary operators on Z_74 (discrete Weyl–Heisenberg pair)
# ---------------------------------------------------------------------------

def shift_operator(step: int = 1) -> np.ndarray:
    """Cyclic shift ``|k⟩ → |k+step⟩``: an integer permutation matrix (exactly unitary)."""
    matrix = np.zeros((LATTICE_ORDER, LATTICE_ORDER), dtype=np.int64)
    for k in range(LATTICE_ORDER):
        matrix[wrap(k + step), k] = 1
    return matrix


def reflection_operator() -> np.ndarray:
    """Orbifold reflection ``|k⟩ → |−k⟩``: involutive permutation with fixed points {0, 37}."""
    matrix = np.zeros((LATTICE_ORDER, LATTICE_ORDER), dtype=np.int64)
    for k in range(LATTICE_ORDER):
        matrix[wrap(-k), k] = 1
    return matrix


def clock_operator() -> np.ndarray:
    phases = np.exp(2j * np.pi * np.arange(LATTICE_ORDER) / LATTICE_ORDER)
    return np.diag(phases)


def verify_lattice_operators() -> dict[str, Any]:
    shift = shift_operator(1)
    reflection = reflection_operator()
    identity = np.eye(LATTICE_ORDER, dtype=np.int64)
    clock = clock_operator()
    omega = np.exp(2j * np.pi / LATTICE_ORDER)
    weyl_residual = float(np.max(np.abs(clock @ shift - omega * (shift @ clock))))
    fixed = [k for k in range(LATTICE_ORDER) if reflection[k, k] == 1]
    return {
        "shift_exactly_unitary": bool(np.array_equal(shift.T @ shift, identity)),
        "reflection_exactly_unitary": bool(np.array_equal(reflection.T @ reflection, identity)),
        "reflection_involution": bool(np.array_equal(reflection @ reflection, identity)),
        "reflection_fixed_points": fixed,
        "shift_order": orbit_period(1),
        "weyl_commutation_residual": weyl_residual,
        "arithmetic": "integer permutation matrices; float only for the clock check",
    }


# ---------------------------------------------------------------------------
# Orbifold impacts, recurrence, and explicit exits
# ---------------------------------------------------------------------------

def orbifold_fold(index: int) -> int:
    k = wrap(index)
    return k if k <= HALF_TURN else LATTICE_ORDER - k


def orbifold_bounce(start: int, step: int, n_steps: int) -> dict[str, Any]:
    """Trajectory on the fundamental domain [0, 37] with elastic reflections.

    The unfolded motion is a uniform rotation on Z_74; folding by S¹/Z₂ turns
    every passage through a fixed point into an impact (direction reversal).
    """
    if n_steps < 0:
        raise ValueError("n_steps must be non-negative")
    unfolded = [int(start) + i * int(step) for i in range(n_steps + 1)]
    positions = [orbifold_fold(p) for p in unfolded]
    impacts: list[dict[str, int]] = []
    for i in range(n_steps):
        lo, hi = sorted((unfolded[i], unfolded[i + 1]))
        first = -((-lo) // HALF_TURN)  # ceil(lo / 37): closed interval [lo, hi]
        for multiple in range(first, hi // HALF_TURN + 1):
            if multiple * HALF_TURN == unfolded[i]:
                continue
            impacts.append({"after_step": i + 1, "crease": orbifold_fold(multiple * HALF_TURN)})
    return {
        "positions": positions,
        "impacts": impacts,
        "impact_count": len(impacts),
        "norm_preserved_exactly": True,
        "note": "folding acts on basis labels only; the state norm is untouched by construction",
    }


def orbit_period(step: int) -> int:
    step = wrap(step)
    if step == 0:
        return 1
    return LATTICE_ORDER // math.gcd(step, LATTICE_ORDER)


def first_hitting_time(start: int, step: int, targets: Iterable[int], *, max_steps: int | None = None) -> dict[str, Any]:
    """Explicit non-unitary exit: stop when the unitary orbit first enters a target facet."""
    target_set = {wrap(t) for t in targets}
    period = orbit_period(step)
    limit = period if max_steps is None else min(int(max_steps), period)
    position = wrap(start)
    for n in range(limit + 1):
        if position in target_set:
            return {"hit": True, "steps": n, "facet": position, "period": period}
        position = wrap(position + step)
    return {"hit": False, "steps": None, "facet": None, "period": period,
            "note": "orbit is periodic; targets outside the orbit are never reached"}


def unitary_iteration_report(start: int, step: int) -> dict[str, Any]:
    period = orbit_period(step)
    visited = {wrap(start + i * step) for i in range(period)}
    return {
        "start": wrap(start),
        "step": wrap(step),
        "period": period,
        "distinct_states": len(visited),
        "converges": period == 1,
        "reason": "eigenvalues of a unitary lie on the unit circle; iteration is periodic, not contractive",
        "exit_rule": "first_hitting_time on a target facet (projective read-out, deliberately non-unitary)",
    }


# ---------------------------------------------------------------------------
# Bit-exact integer CORDIC (contrast case: Cartesian fixed point drifts)
# ---------------------------------------------------------------------------

ANGLE_FRAC_BITS = 24


@lru_cache(maxsize=64)
def _cordic_tables(iterations: int) -> tuple[tuple[int, ...], float]:
    atans = tuple(int(round(math.atan(2.0 ** -i) * (1 << ANGLE_FRAC_BITS))) for i in range(iterations))
    gain = 1.0
    for i in range(iterations):
        gain *= math.sqrt(1.0 + 2.0 ** (-2 * i))
    return atans, gain


_HALF_PI_FIXED = int(round((math.pi / 2) * (1 << ANGLE_FRAC_BITS)))
_TWO_PI_FIXED = int(round((2 * math.pi) * (1 << ANGLE_FRAC_BITS)))


def phase_index_to_angle_fixed(index: int) -> int:
    return (wrap(index) * _TWO_PI_FIXED + LATTICE_ORDER // 2) // LATTICE_ORDER


def cordic_rotate(x: int, y: int, angle_fixed: int, *, iterations: int, frac_bits: int) -> tuple[int, int]:
    """Rotate integer (x, y) by ``angle_fixed`` using shifts/adds plus one gain multiply."""
    angle = int(angle_fixed)
    while angle > _HALF_PI_FIXED:
        x, y = -y, x
        angle -= _HALF_PI_FIXED
    while angle < -_HALF_PI_FIXED:
        x, y = y, -x
        angle += _HALF_PI_FIXED
    atans, gain = _cordic_tables(iterations)
    for i in range(iterations):
        if angle >= 0:
            x, y = x - (y >> i), y + (x >> i)
            angle -= atans[i]
        else:
            x, y = x + (y >> i), y - (x >> i)
            angle += atans[i]
    inverse_gain = int(round((1 << frac_bits) / gain))
    half = 1 << (frac_bits - 1)
    return (x * inverse_gain + half) >> frac_bits, (y * inverse_gain + half) >> frac_bits


def cordic_vector_phase(x: int, y: int, *, iterations: int = 24) -> int:
    """Vectoring-mode CORDIC: integer (x, y) → nearest Z_74 phase index (integer-only)."""
    if x == 0 and y == 0:
        return 0
    angle = 0
    if x < 0:
        x, y = -x, -y
        angle = _TWO_PI_FIXED // 2
    atans, _ = _cordic_tables(iterations)
    for i in range(iterations):
        if y > 0:
            x, y = x + (y >> i), y - (x >> i)
            angle += atans[i]
        else:
            x, y = x - (y >> i), y + (x >> i)
            angle -= atans[i]
    numerator = angle * LATTICE_ORDER
    return wrap((numerator + _TWO_PI_FIXED // 2) // _TWO_PI_FIXED)


def cordic_closure_drift(*, bits: int, step: int = 1, laps: int = 1) -> dict[str, Any]:
    """Chain ``period·laps`` rotations by ``step`` lattice phases and measure closure error.

    Exact geometry returns to the start.  Cartesian fixed point does not; the
    phase-index representation does, by construction (0 drift with 7 bits).
    """
    if bits < 4:
        raise ValueError("bits must be at least 4")
    frac_bits = bits - 1
    amplitude = 1 << (bits - 2)  # headroom for CORDIC growth before compensation
    angle_fixed = phase_index_to_angle_fixed(step)
    n_rotations = orbit_period(step) * max(1, int(laps))
    x, y = amplitude, 0
    for _ in range(n_rotations):
        x, y = cordic_rotate(x, y, angle_fixed, iterations=bits, frac_bits=frac_bits)
    norm = math.hypot(x, y)
    position_error = math.hypot(x - amplitude, y)
    phase_after = wrap(0 + n_rotations * step)
    return {
        "bits": bits,
        "rotations": n_rotations,
        "amplitude": amplitude,
        "final_xy": [x, y],
        "relative_norm_drift": round(abs(norm - amplitude) / amplitude, 6),
        "relative_closure_error": round(position_error / amplitude, 6),
        "phase_lattice_final_index": phase_after,
        "phase_lattice_closure_error": 0 if phase_after == 0 else circular_distance(phase_after, 0),
    }


def quantization_error_table(bits_list: Sequence[int] = (4, 8, 12, 16), *, step: int = 1) -> dict[str, Any]:
    rows = [cordic_closure_drift(bits=b, step=step) for b in bits_list]
    return {
        "rows": rows,
        "phase_index_bits": PHASE_INDEX_BITS,
        "finding": (
            "Cartesian fixed-point rotations accumulate drift that shrinks with bit width; "
            "phase-index arithmetic on Z_74 is exact at 7 bits. Amplitudes are carried separately."
        ),
    }


# ---------------------------------------------------------------------------
# Toroidal phase sketch (integer-only locality-sensitive address)
# ---------------------------------------------------------------------------

_ROOT_TABLE_FRAC_BITS = 14


@lru_cache(maxsize=1)
def _root_table() -> tuple[tuple[int, int], ...]:
    scale = 1 << _ROOT_TABLE_FRAC_BITS
    return tuple(
        (int(round(math.cos(2 * math.pi * k / LATTICE_ORDER) * scale)),
         int(round(math.sin(2 * math.pi * k / LATTICE_ORDER) * scale)))
        for k in range(LATTICE_ORDER)
    )


@lru_cache(maxsize=65536)
def _token_phases(token: str, dims: int) -> tuple[int, ...]:
    digest = hashlib.blake2b(token.encode("utf-8"), digest_size=max(8, 2 * dims)).digest()
    return tuple(int.from_bytes(digest[2 * j:2 * j + 2], "big") % LATTICE_ORDER for j in range(dims))


def phase_sketch(tokens: Iterable[str], *, dims: int = DEFAULT_SKETCH_DIMS) -> dict[str, Any]:
    """Map a token set to a point on ``T^dims`` using integer roots-of-unity sums.

    Each token contributes ω^{h_j(token)} on circle j (ω = e^{2πi/74}); the
    summed vector's phase is read out with integer vectoring CORDIC.  Shared
    tokens pull codes together; unrelated sets sit ~74/4 apart per circle.
    This is a locality-sensitive approximation, not an exact similarity.
    """
    if dims < 2 or dims > 32:
        raise ValueError("dims must be in [2, 32]")
    unique = sorted({str(t) for t in tokens if str(t)})
    table = _root_table()
    acc = [[0, 0] for _ in range(dims)]
    for token in unique:
        for j, phase in enumerate(_token_phases(token, dims)):
            acc[j][0] += table[phase][0]
            acc[j][1] += table[phase][1]
    code = tuple(cordic_vector_phase(x, y) for x, y in acc)
    return {
        "code": list(code),
        "bank": braid_bank(code),
        "token_count": len(unique),
        "empty": not unique,
    }


def sketch_similarity(code_a: Sequence[int], code_b: Sequence[int]) -> float:
    expected = EXPECTED_RANDOM_CIRCULAR_DISTANCE * len(code_a)
    if expected <= 0:
        return 0.0
    return round(max(0.0, 1.0 - toroidal_distance(code_a, code_b) / expected), 4)


def get_toroidal_geometry_report() -> dict[str, Any]:
    return {
        "status": STATUS_LABEL,
        "lattice_order": LATTICE_ORDER,
        "braid_windings": list(BRAID_WINDINGS),
        "orbifold_fixed_points": list(ORBIFOLD_FIXED_POINTS),
        "phase_index_bits": PHASE_INDEX_BITS,
        "tick_phase_step": TICK_PHASE_STEP,
        "tick_orbit_period": orbit_period(TICK_PHASE_STEP),
        "braid_orbit_periods": {str(n): orbit_period(n) for n in BRAID_WINDINGS},
        "operators": verify_lattice_operators(),
        "quantization": quantization_error_table(),
        "claims_boundary": (
            "Software emulation of discrete toroidal navigation. Exactness claims cover the integer "
            "lattice arithmetic only; they do not imply answer correctness or hardware speedups."
        ),
    }


__all__ = [
    "BRAID_WINDINGS",
    "HALF_TURN",
    "LATTICE_ORDER",
    "ORBIFOLD_FIXED_POINTS",
    "TICK_PHASE_STEP",
    "braid_bank",
    "circular_distance",
    "circular_distance_subdifferential",
    "cordic_closure_drift",
    "cordic_rotate",
    "cordic_vector_phase",
    "first_hitting_time",
    "get_toroidal_geometry_report",
    "orbifold_bounce",
    "orbifold_fold",
    "orbit_period",
    "phase_sketch",
    "quantization_error_table",
    "reflection_operator",
    "shift_operator",
    "sketch_similarity",
    "toroidal_distance",
    "toroidal_geodesic",
    "unitary_iteration_report",
    "verify_lattice_operators",
]
