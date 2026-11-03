# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Physical-time evolution of the conformal planar radion--scalar system.

The periodic spatial grid uses centered finite differences and classical RK4
in coordinate time.  The zero-potential, massless-circle equations are evolved
as a first-order-in-time system; no relaxation or elliptic solve is performed.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]

__all__ = [
    "PlanarRadionState",
    "PlanarRadionTrajectory",
    "constrained_areal_initial_data",
    "planar_constraint_diagnostic",
    "evolve_planar_radion",
]


def _finite_float(value: float, name: str) -> float:
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must be a finite real number")
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite real number") from exc
    if not math.isfinite(converted):
        raise ValueError(f"{name} must be finite")
    return converted


def _float_array(value: object, name: str) -> FloatArray:
    if np.iscomplexobj(value):
        raise ValueError(f"{name} must contain real numeric values, not complex values")
    try:
        return np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must contain real numeric values") from exc


@dataclass(frozen=True)
class PlanarRadionState:
    """Fields and coordinate-time velocities on a uniform periodic grid.

    ``dx`` is the periodic grid spacing.  The arrays are copied, validated,
    and made read-only on construction; they represent ``r, sigma, psi`` and
    their time derivatives at time ``t``.
    """

    t: float
    dx: float
    r: FloatArray
    sigma: FloatArray
    psi: FloatArray
    r_t: FloatArray
    sigma_t: FloatArray
    psi_t: FloatArray

    def __post_init__(self) -> None:
        time = _finite_float(self.t, "state time")
        dx = _finite_float(self.dx, "dx")
        object.__setattr__(self, "t", time)
        object.__setattr__(self, "dx", dx)
        if dx <= 0.0:
            raise ValueError("dx must be finite and positive")
        names = ("r", "sigma", "psi", "r_t", "sigma_t", "psi_t")
        arrays = []
        for name in names:
            value = _float_array(getattr(self, name), name)
            if value.ndim != 1 or value.size < 3:
                raise ValueError(f"{name} must be a one-dimensional array with at least 3 points")
            if not np.all(np.isfinite(value)):
                raise ValueError(f"{name} must contain only finite values")
            arrays.append(value.copy())
            object.__setattr__(self, name, arrays[-1])
        sizes = {array.size for array in arrays}
        if len(sizes) != 1:
            raise ValueError("all state arrays must have the same shape")
        if np.any(self.r <= 0.0):
            raise ValueError("r must remain strictly positive")
        _check_safe_exponents(self.sigma, "sigma")
        _check_safe_exponents(self.psi, "psi")
        # Five-dimensional uplift: diag(-A, A, B, B, C), where these are
        # log(A), log(B), log(C).  Separate field checks do not protect it.
        with np.errstate(over="ignore", invalid="ignore"):
            metric_logs = (
                2.0 * self.sigma - self.psi,
                2.0 * np.log(self.r) - self.psi,
                2.0 * self.psi,
            )
        for values, name in zip(
            metric_logs,
            ("uplift conformal metric", "uplift planar metric", "uplift circle metric"),
        ):
            _check_safe_exponents(values, name)
        for array in arrays:
            array.flags.writeable = False

    @property
    def n(self) -> int:
        """Number of periodic grid points."""
        return int(self.r.size)


@dataclass(frozen=True)
class PlanarRadionTrajectory:
    """Saved states and their coordinate times, including both endpoints."""

    times: FloatArray
    states: tuple[PlanarRadionState, ...]

    def __post_init__(self) -> None:
        times = _float_array(self.times, "times")
        if times.ndim != 1 or times.size != len(self.states) or times.size == 0:
            raise ValueError("times must be a non-empty 1D array matching states")
        if not np.all(np.isfinite(times)) or np.any(np.diff(times) <= 0.0):
            raise ValueError("trajectory times must be finite and strictly increasing")
        if any(time != state.t for time, state in zip(times, self.states)):
            raise ValueError("trajectory times must match the corresponding state times")
        first = self.states[0]
        if any(state.n != first.n or state.dx != first.dx for state in self.states):
            raise ValueError("trajectory states must share the same periodic grid")
        object.__setattr__(self, "times", times.copy())


def _check_safe_exponents(values: FloatArray, name: str) -> None:
    # Keep exp(sigma) and exp(psi) representable and nonzero in float64.
    lower = math.log(np.finfo(np.float64).tiny)
    upper = math.log(np.finfo(np.float64).max)
    if np.any(values < lower) or np.any(values > upper):
        raise ValueError(f"{name} is outside the safe float64 exponential range")


def _periodic_d1(values: FloatArray, dx: float) -> FloatArray:
    return (np.roll(values, -1) - np.roll(values, 1)) / (2.0 * dx)


def _periodic_d2(values: FloatArray, dx: float) -> FloatArray:
    return (np.roll(values, -1) - 2.0 * values + np.roll(values, 1)) / (dx * dx)


def constrained_areal_initial_data(
    t0: float,
    x: Iterable[float] | FloatArray,
    psi: Iterable[float] | FloatArray,
    psi_t: Iterable[float] | FloatArray,
    *,
    psi_x: Iterable[float] | FloatArray | None = None,
) -> PlanarRadionState:
    """Construct periodic, areal-gauge initial data at ``t=t0>0``.

    The grid must be uniform and periodic (the endpoint is not repeated).
    ``sigma_x = 3 t0 psi_t psi_x / 2`` is integrated spectrally with zero
    mean.  Periodicity requires the source's mean to vanish; for even grids
    its Nyquist coefficient must also vanish because that mode has no spectral
    derivative.  Neither incompatibility is silently projected away.

    By default ``psi_x`` uses centered finite differences: these data satisfy
    the slice sum discretely, but are only second-order approximations to
    continuum constrained data.  The spectral antiderivative and centered
    diagnostic derivatives differ, so the slice difference has truncation
    error.  Supplying an independent analytic ``psi_x`` permits exact sampled
    continuum data when the source is resolved without spectral aliasing;
    arbitrary sampled functions do not imply exact continuum constraints.
    """
    t0 = _finite_float(t0, "t0")
    x_arr = _float_array(x, "x")
    psi_arr = _float_array(psi, "psi")
    v_arr = _float_array(psi_t, "psi_t")
    if t0 <= 0.0:
        raise ValueError("t0 must be finite and positive")
    if x_arr.ndim != 1 or x_arr.size < 4:
        raise ValueError("x must be a one-dimensional periodic grid with at least 4 points")
    if psi_arr.shape != x_arr.shape or v_arr.shape != x_arr.shape:
        raise ValueError("psi and psi_t must have the same shape as x")
    if not np.all(np.isfinite(x_arr)) or not np.all(np.isfinite(psi_arr)) or not np.all(np.isfinite(v_arr)):
        raise ValueError("x, psi, and psi_t must contain only finite values")
    differences = np.diff(x_arr)
    dx = float(differences[0])
    if dx <= 0.0 or not np.allclose(differences, dx, rtol=1e-10, atol=1e-12):
        raise ValueError("x must be strictly increasing and uniformly spaced")
    _check_safe_exponents(psi_arr, "psi")

    psix = _periodic_d1(psi_arr, dx) if psi_x is None else _float_array(psi_x, "psi_x")
    if psix.shape != x_arr.shape or not np.all(np.isfinite(psix)):
        raise ValueError("psi_x must be finite and have the same shape as x")
    with np.errstate(over="ignore", invalid="ignore"):
        source = 1.5 * t0 * v_arr * psix
        sigma_t = -1.0 / (4.0 * t0) + 0.75 * t0 * (v_arr * v_arr + psix * psix)
    if not np.all(np.isfinite(source)) or not np.all(np.isfinite(sigma_t)):
        raise ValueError("initial constraint coefficients overflow the finite domain")
    scale = max(1.0, float(np.max(np.abs(source))))
    tolerance = 256.0 * np.finfo(np.float64).eps * scale
    if abs(float(np.mean(source))) > tolerance:
        raise ValueError("periodic sigma reconstruction requires mean(psi_t * psi_x) = 0")

    source_hat = np.fft.fft(source)
    if x_arr.size % 2 == 0 and abs(source_hat[x_arr.size // 2]) > tolerance * x_arr.size:
        raise ValueError("sigma_x has an incompatible Nyquist mode")
    wave_numbers = 2.0 * np.pi * np.fft.fftfreq(x_arr.size, d=dx)
    sigma_hat = np.zeros_like(source_hat)
    nonzero = wave_numbers != 0.0
    sigma_hat[nonzero] = source_hat[nonzero] / (1j * wave_numbers[nonzero])
    sigma = np.fft.ifft(sigma_hat).real
    r_value = math.sqrt(t0)
    return PlanarRadionState(
        t=t0,
        dx=dx,
        r=np.full(x_arr.shape, r_value),
        sigma=sigma,
        psi=psi_arr,
        r_t=np.full(x_arr.shape, 1.0 / (2.0 * r_value)),
        sigma_t=sigma_t,
        psi_t=v_arr,
    )


def planar_constraint_diagnostic(state: PlanarRadionState) -> dict[str, FloatArray]:
    """Return slice constraints ``Cu`` and ``Cv`` without estimating ``r_tt``.

    The Hamiltonian-like sum substitutes the evolution equation for ``r_tt``,
    so it depends only on one-time slice data and centered spatial derivatives.
    The returned pointwise arrays obey ``Cu+Cv=sum`` and ``Cv-Cu=difference``.
    """
    dx = state.dx
    rx = _periodic_d1(state.r, dx)
    rxx = _periodic_d2(state.r, dx)
    sigmax = _periodic_d1(state.sigma, dx)
    psix = _periodic_d1(state.psi, dx)
    rtx = _periodic_d1(state.r_t, dx)
    # r_tt = r_xx - (r_t^2-r_x^2)/r eliminates the second time derivative.
    constraint_sum = (
        2.0 * rxx
        - (state.r_t * state.r_t - rx * rx) / state.r
        - 2.0 * (state.sigma_t * state.r_t + sigmax * rx)
        + 0.75 * state.r * (state.psi_t * state.psi_t + psix * psix)
    )
    constraint_difference = (
        2.0 * rtx
        - 2.0 * (state.sigma_t * rx + sigmax * state.r_t)
        + 1.5 * state.r * state.psi_t * psix
    )
    return {
        "Cu": 0.5 * (constraint_sum - constraint_difference),
        "Cv": 0.5 * (constraint_sum + constraint_difference),
        "Cu_plus_Cv": constraint_sum,
        "Cv_minus_Cu": constraint_difference,
    }


def _rhs(state: PlanarRadionState) -> tuple[FloatArray, ...]:
    with np.errstate(over="raise", divide="raise", invalid="raise"):
        rx = _periodic_d1(state.r, state.dx)
        sigmax = _periodic_d1(state.sigma, state.dx)
        psix = _periodic_d1(state.psi, state.dx)
        rtt = _periodic_d2(state.r, state.dx) - (
            state.r_t * state.r_t - rx * rx
        ) / state.r
        sigmatt = _periodic_d2(state.sigma, state.dx) + (
            state.r_t * state.r_t - rx * rx
        ) / (state.r * state.r) - 0.75 * (
            state.psi_t * state.psi_t - psix * psix
        )
        psitt = _periodic_d2(state.psi, state.dx) - 2.0 / state.r * (
            state.r_t * state.psi_t - rx * psix
        )
    derivatives = (state.r_t, state.sigma_t, state.psi_t, rtt, sigmatt, psitt)
    if not all(np.all(np.isfinite(value)) for value in derivatives):
        raise ValueError("evolution produced a non-finite derivative")
    return derivatives


def _shift(state: PlanarRadionState, derivative: tuple[FloatArray, ...], dt: float) -> PlanarRadionState:
    arrays = [
        value + dt * rate
        for value, rate in zip(
            (state.r, state.sigma, state.psi, state.r_t, state.sigma_t, state.psi_t),
            derivative,
        )
    ]
    return PlanarRadionState(
        t=state.t + dt,
        dx=state.dx,
        r=arrays[0],
        sigma=arrays[1],
        psi=arrays[2],
        r_t=arrays[3],
        sigma_t=arrays[4],
        psi_t=arrays[5],
    )


def _rk4_step(state: PlanarRadionState, dt: float) -> PlanarRadionState:
    try:
        k1 = _rhs(state)
        k2 = _rhs(_shift(state, k1, 0.5 * dt))
        k3 = _rhs(_shift(state, k2, 0.5 * dt))
        k4 = _rhs(_shift(state, k3, dt))
        values = (state.r, state.sigma, state.psi, state.r_t, state.sigma_t, state.psi_t)
        result = [
            value + (dt / 6.0) * (a + 2.0 * b + 2.0 * c + d)
            for value, a, b, c, d in zip(values, k1, k2, k3, k4)
        ]
        return PlanarRadionState(
            t=state.t + dt,
            dx=state.dx,
            r=result[0],
            sigma=result[1],
            psi=result[2],
            r_t=result[3],
            sigma_t=result[4],
            psi_t=result[5],
        )
    except (FloatingPointError, OverflowError) as exc:
        raise ValueError("evolution left the finite physical domain") from exc


def evolve_planar_radion(
    initial: PlanarRadionState,
    t_final: float,
    dt: float,
    *,
    save_every: int = 1,
) -> PlanarRadionTrajectory:
    """Evolve to ``t_final`` using physical coordinate-time RK4.

    The periodic centered-difference wave system uses the conservative CFL
    restriction ``dt <= dx``.  A shorter final step is allowed.  The returned
    trajectory contains the initial state, every ``save_every``-th step, and
    always the final state.  Invalid stages (including ``r <= 0`` or unsafe
    exponentials) raise ``ValueError``; fields are never clipped.
    """
    t_final = _finite_float(t_final, "t_final")
    dt = _finite_float(dt, "dt")
    if t_final < initial.t:
        raise ValueError("t_final must be finite and no earlier than the initial time")
    if dt <= 0.0:
        raise ValueError("dt must be finite and positive")
    if dt > initial.dx * (1.0 + 16.0 * np.finfo(np.float64).eps):
        raise ValueError("dt violates the conservative centered-wave CFL bound dt <= dx")
    if not isinstance(save_every, int) or isinstance(save_every, bool) or save_every < 1:
        raise ValueError("save_every must be a positive integer")
    states = [initial]
    current = initial
    step = 0
    while current.t < t_final:
        step_dt = min(dt, t_final - current.t)
        if step_dt <= 0.0 or current.t + step_dt == current.t:
            raise ValueError("time step cannot advance the current coordinate time")
        current = _rk4_step(current, step_dt)
        step += 1
        if step % save_every == 0 or current.t >= t_final:
            states.append(current)
    return PlanarRadionTrajectory(
        times=np.asarray([state.t for state in states], dtype=np.float64),
        states=tuple(states),
    )
