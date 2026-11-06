# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.special import j0, j1

from src.physics.planar_radion.evolution import (
    PlanarRadionState,
    PlanarRadionTrajectory,
    constrained_areal_initial_data,
    evolve_planar_radion,
    planar_constraint_diagnostic,
)


def test_uniform_off_constraint_slice_has_canonical_null_normalization():
    ones = np.ones(8)
    zeros = np.zeros(8)
    state = PlanarRadionState(0.0, 0.1, ones, zeros, zeros, ones, zeros, zeros)
    result = planar_constraint_diagnostic(state)
    np.testing.assert_array_equal(result["Cu"], -0.25 * ones)
    np.testing.assert_array_equal(result["Cv"], -0.25 * ones)
    np.testing.assert_array_equal(result["Cu_plus_Cv"], -0.5 * ones)
    np.testing.assert_array_equal(result["Cv_minus_Cu"], zeros)


def test_slice_diagnostics_match_independent_null_coordinate_definitions():
    n = 64
    dx = 2 * np.pi / n
    x = dx * np.arange(n)
    state = PlanarRadionState(
        0.0, dx, 1.2 + 0.1 * np.cos(x), 0.2 * np.sin(2 * x),
        0.3 * np.cos(3 * x), 0.4 + 0.05 * np.sin(x),
        0.1 * np.cos(x), 0.2 * np.sin(2 * x),
    )

    def d_x(values):
        return (np.roll(values, -1) - np.roll(values, 1)) / (2 * dx)

    r_x = d_x(state.r)
    r_tx = d_x(state.r_t)
    r_xx = (np.roll(state.r, -1) - 2 * state.r + np.roll(state.r, 1)) / dx**2
    r_tt = r_xx - (state.r_t**2 - r_x**2) / state.r
    null_constraints = []
    for sign in (-1, 1):
        r_null = (state.r_t + sign * r_x) / 2
        sigma_null = (state.sigma_t + sign * d_x(state.sigma)) / 2
        psi_null = (state.psi_t + sign * d_x(state.psi)) / 2
        r_null_null = (r_tt + 2 * sign * r_tx + r_xx) / 4
        null_constraints.append(
            r_null_null - 2 * sigma_null * r_null + 0.75 * state.r * psi_null**2
        )
    cu, cv = null_constraints
    expected = {"Cu": cu, "Cv": cv, "Cu_plus_Cv": cu + cv, "Cv_minus_Cu": cv - cu}
    for name, actual in planar_constraint_diagnostic(state).items():
        np.testing.assert_allclose(actual, expected[name], rtol=1e-13, atol=1e-15)


def _bessel_reference(n: int, amplitudes: tuple[float, ...], t0: float, tf: float):
    """Independent spectral-mode integration of sigma's forced oscillator."""
    length = 2.0 * np.pi
    dx = length / n
    x = dx * np.arange(n)
    modes = np.arange(1, len(amplitudes) + 1, dtype=np.float64)
    k = modes

    def scalar_fields(t):
        phase = np.outer(k, x)
        amps = np.asarray(amplitudes)[:, None] * j0(k * t)[:, None]
        amps_t = -np.asarray(amplitudes)[:, None] * k[:, None] * j1(k * t)[:, None]
        psi = np.sum(amps * np.cos(phase), axis=0)
        psi_t = np.sum(amps_t * np.cos(phase), axis=0)
        psi_x = np.sum(-amps * k[:, None] * np.sin(phase), axis=0)
        return psi, psi_t, psi_x

    psi0, psi_t0, psi_x0 = scalar_fields(t0)
    source0 = 1.5 * t0 * psi_t0 * psi_x0
    source_hat = np.fft.fft(source0)
    wave_numbers = 2.0 * np.pi * np.fft.fftfreq(n, d=dx)
    sigma_hat0 = np.zeros(n, dtype=np.complex128)
    nonzero = wave_numbers != 0.0
    sigma_hat0[nonzero] = source_hat[nonzero] / (1j * wave_numbers[nonzero])
    sigma0 = np.fft.ifft(sigma_hat0).real
    sigma_t0 = -1.0 / (4.0 * t0) + 0.75 * t0 * (psi_t0**2 + psi_x0**2)
    sigma_t_hat0 = np.fft.fft(sigma_t0)

    def oscillator_rhs(t, packed):
        sigma_hat = packed[:n]
        sigma_t_hat = packed[n:]
        _, psi_t, psi_x = scalar_fields(t)
        forcing = np.fft.fft(1.0 / (4.0 * t * t) - 0.75 * (psi_t**2 - psi_x**2))
        return np.concatenate(
            (sigma_t_hat, -(wave_numbers**2) * sigma_hat + forcing)
        )

    solution = solve_ivp(
        oscillator_rhs,
        (t0, tf),
        np.concatenate((sigma_hat0, sigma_t_hat0)),
        rtol=2e-11,
        atol=2e-13,
    )
    assert solution.success
    sigma = np.fft.ifft(solution.y[:n, -1]).real
    psi, psi_t, _ = scalar_fields(tf)
    return x, np.sqrt(tf), sigma, psi, psi_t


def _evolve_bessel(n: int, amplitudes: tuple[float, ...], dt_factor: float = 0.2):
    t0, tf = 0.5, 0.8
    x, _, _, _, _ = _bessel_reference(n, amplitudes, t0, tf)
    psi, psi_t, psi_x = _bessel_initial_fields(x, amplitudes, t0)
    state = constrained_areal_initial_data(t0, x, psi, psi_t)
    trajectory = evolve_planar_radion(state, tf, dt_factor * state.dx)
    return trajectory.states[-1], _bessel_reference(n, amplitudes, t0, tf)


def _bessel_initial_fields(x, amplitudes, t):
    modes = np.arange(1, len(amplitudes) + 1, dtype=np.float64)
    phase = np.outer(modes, x)
    amps = np.asarray(amplitudes)[:, None] * j0(modes * t)[:, None]
    amps_t = -np.asarray(amplitudes)[:, None] * modes[:, None] * j1(modes * t)[:, None]
    return (
        np.sum(amps * np.cos(phase), axis=0),
        np.sum(amps_t * np.cos(phase), axis=0),
        np.sum(-amps * modes[:, None] * np.sin(phase), axis=0),
    )


@pytest.mark.parametrize("amplitudes", [(0.04,), (0.12,), (0.04, 0.025)])
def test_bessel_and_multimode_four_grid_second_order_convergence(amplitudes):
    errors = []
    for n in (32, 64, 128, 256):
        state, (_, r_exact, sigma_exact, psi_exact, psi_t_exact) = _evolve_bessel(n, amplitudes)
        errors.append(
            np.sqrt(
                np.mean(
                    (state.sigma - sigma_exact) ** 2
                    + (state.psi - psi_exact) ** 2
                    + (state.psi_t - psi_t_exact) ** 2
                    + (state.r - r_exact) ** 2
                )
            )
        )
    assert errors[0] > errors[1] > errors[2] > errors[3]
    assert errors[0] / errors[1] > 3.0
    assert errors[1] / errors[2] > 3.0
    assert errors[2] / errors[3] > 3.0


def test_homogeneous_zero_scalar_solution_matches_exact_coordinate_time():
    n, t0, tf = 32, 0.5, 1.0
    dx = 2.0 * np.pi / n
    x = dx * np.arange(n)
    psi0 = np.full(n, 0.3)
    state = PlanarRadionState(
        t=t0,
        dx=dx,
        r=np.full(n, np.sqrt(t0)),
        sigma=np.full(n, -0.25 * np.log(t0)),
        psi=psi0,
        r_t=np.full(n, 1.0 / (2.0 * np.sqrt(t0))),
        sigma_t=np.full(n, -1.0 / (4.0 * t0)),
        psi_t=np.zeros(n),
    )
    final = evolve_planar_radion(state, tf, 0.2 * dx).states[-1]
    assert final.r == pytest.approx(np.sqrt(tf), rel=2e-7)
    assert final.sigma == pytest.approx(
        np.full(n, -0.25 * np.log(tf)), rel=2e-7, abs=3e-7
    )
    assert final.psi == pytest.approx(psi0, abs=1e-14)


@pytest.mark.parametrize("charge", [0.08, -1.0, 1.0])
def test_homogeneous_scalar_anisotropic_and_flat_frw_solutions(charge):
    n, t0, tf = 24, 0.6, 1.0
    dx = 2.0 * np.pi / n
    x = dx * np.arange(n)
    sigma_coefficient = -0.25 + 0.75 * charge**2
    state = PlanarRadionState(
        t=t0,
        dx=dx,
        r=np.full(n, np.sqrt(t0)),
        sigma=np.full(n, sigma_coefficient * np.log(t0)),
        psi=np.full(n, charge * np.log(t0)),
        r_t=np.full(n, 1.0 / (2.0 * np.sqrt(t0))),
        sigma_t=np.full(n, sigma_coefficient / t0),
        psi_t=np.full(n, charge / t0),
    )
    final = evolve_planar_radion(state, tf, 0.15 * dx).states[-1]
    assert final.r == pytest.approx(np.sqrt(tf), rel=3e-7)
    assert final.sigma == pytest.approx(
        np.full(n, sigma_coefficient * np.log(tf)), rel=3e-7, abs=3e-7
    )
    assert final.psi == pytest.approx(
        np.full(n, charge * np.log(tf)), rel=3e-7, abs=3e-7
    )
    if abs(charge) == 1.0:
        assert sigma_coefficient == 0.5
        assert np.exp(final.sigma) == pytest.approx(final.r, abs=3e-7)


@pytest.mark.parametrize("charge", [-1.0, 1.0])
def test_flat_frw_temporal_fourth_order_against_exact_solution(charge):
    t0, tf = 0.5, 1.0
    initial = constrained_areal_initial_data(
        t0, np.arange(8) * 0.2, np.full(8, charge * np.log(t0)),
        np.full(8, charge / t0)
    )
    errors = []
    for steps in (10, 20, 40, 80):
        final = evolve_planar_radion(initial, tf, (tf - t0) / steps).states[-1]
        # Initial sigma has zero mean, hence its analytic additive constant.
        exact_sigma = 0.5 * np.log(tf / t0)
        errors.append(np.sqrt(np.mean(
            (final.r - np.sqrt(tf))**2
            + (final.sigma - exact_sigma)**2
            + (final.psi - charge * np.log(tf))**2
        )))
    assert all(13.0 < coarse / fine < 19.0 for coarse, fine in zip(errors, errors[1:]))


def test_constrained_areal_data_and_constraint_slice_diagnostic():
    n, t0 = 64, 0.7
    dx = 2.0 * np.pi / n
    x = dx * np.arange(n)
    psi = 0.06 * np.cos(x) + 0.025 * np.sin(2.0 * x)
    psi_t = 0.04 * np.cos(x) + 0.015 * np.sin(2.0 * x)
    state = constrained_areal_initial_data(t0, x, psi, psi_t)
    assert state.r == pytest.approx(np.full(n, np.sqrt(t0)))
    assert state.r_t == pytest.approx(np.full(n, 1.0 / (2.0 * np.sqrt(t0))))
    assert np.mean(state.sigma) == pytest.approx(0.0, abs=1e-14)
    constraints = planar_constraint_diagnostic(state)
    assert constraints["Cu_plus_Cv"] == pytest.approx(
        constraints["Cu"] + constraints["Cv"]
    )
    assert constraints["Cv_minus_Cu"] == pytest.approx(
        constraints["Cv"] - constraints["Cu"]
    )


def test_temporal_refinement_converges_at_fixed_grid():
    n, t0, tf = 96, 0.5, 0.8
    dx = 2.0 * np.pi / n
    x = dx * np.arange(n)
    psi, psi_t, _ = _bessel_initial_fields(x, (0.07,), t0)
    initial = constrained_areal_initial_data(t0, x, psi, psi_t)
    exact = _bessel_reference(n, (0.07,), t0, tf)[2]
    errors = []
    for factor in (0.4, 0.2, 0.1):
        result = evolve_planar_radion(initial, tf, factor * dx).states[-1]
        errors.append(np.linalg.norm(result.sigma - exact))
    # Spatial error is shared by the runs; compare their temporal differences.
    coarse_to_mid = np.linalg.norm(
        evolve_planar_radion(initial, tf, 0.4 * dx).states[-1].sigma
        - evolve_planar_radion(initial, tf, 0.2 * dx).states[-1].sigma
    )
    mid_to_fine = np.linalg.norm(
        evolve_planar_radion(initial, tf, 0.2 * dx).states[-1].sigma
        - evolve_planar_radion(initial, tf, 0.1 * dx).states[-1].sigma
    )
    assert coarse_to_mid / mid_to_fine > 8.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"r": np.array([1.0, 1.0, -1.0])},
        {"psi": np.array([0.0, np.nan, 0.0])},
        {"sigma": np.array([0.0, 0.0])},
        {"sigma": np.array([1000.0, 0.0, 0.0])},
        {"psi": np.array([-1000.0, 0.0, 0.0])},
        {"sigma": np.array([0.0, 0.0, 0.0], dtype=complex)},
        {"psi": np.array([1j, 0.0, 0.0])},
        {"dx": np.inf},
        {"t": np.nan},
    ],
)
def test_state_rejects_bad_shapes_nonfinite_or_unphysical_fields(kwargs):
    fields = dict(
        t=0.0,
        dx=0.1,
        r=np.ones(3),
        sigma=np.zeros(3),
        psi=np.zeros(3),
        r_t=np.zeros(3),
        sigma_t=np.zeros(3),
        psi_t=np.zeros(3),
    )
    fields.update(kwargs)
    with pytest.raises(ValueError):
        PlanarRadionState(**fields)


def test_invalid_periodic_constrained_data_and_cfl_are_rejected():
    n = 16
    dx = 2.0 * np.pi / n
    x = dx * np.arange(n)
    with pytest.raises(ValueError, match="mean"):
        constrained_areal_initial_data(0.5, x, np.cos(x), np.sin(x))
    initial = PlanarRadionState(
        t=0.5,
        dx=dx,
        r=np.ones(n),
        sigma=np.zeros(n),
        psi=np.zeros(n),
        r_t=np.zeros(n),
        sigma_t=np.zeros(n),
        psi_t=np.zeros(n),
    )
    with pytest.raises(ValueError, match="CFL"):
        evolve_planar_radion(initial, 0.6, 1.1 * dx)
    with pytest.raises(ValueError, match="positive"):
        evolve_planar_radion(initial, 0.6, 0.1 * dx, save_every=0)


def test_evolution_rejects_radion_domain_crossing_without_clipping():
    n = 8
    state = PlanarRadionState(
        t=0.0,
        dx=0.2,
        r=np.ones(n),
        sigma=np.zeros(n),
        psi=np.zeros(n),
        r_t=np.full(n, -10.0),
        sigma_t=np.zeros(n),
        psi_t=np.zeros(n),
    )
    with pytest.raises(ValueError, match="positive|physical domain"):
        evolve_planar_radion(state, 0.1, 0.02)


def test_analytic_derivative_constructs_resolved_continuum_data():
    x = 2.0 * np.pi * np.arange(32) / 32
    t0, amplitude, velocity = 0.7, 0.06, 0.04
    exact = constrained_areal_initial_data(
        t0, x, amplitude * np.cos(x), velocity * np.cos(x),
        psi_x=-amplitude * np.sin(x),
    )
    expected_sigma = 0.375 * t0 * amplitude * velocity * np.cos(2.0 * x)
    np.testing.assert_allclose(exact.sigma, expected_sigma, atol=1e-16)
    np.testing.assert_allclose(
        exact.sigma_t,
        -1.0 / (4.0 * t0) + 0.75 * t0 * (
            velocity**2 * np.cos(x)**2 + amplitude**2 * np.sin(x)**2
        ),
    )


def test_constraint_initializer_rejects_nyquist_and_overflow():
    n = 16
    x = 2.0 * np.pi * np.arange(n) / n
    # sin(x) sin(7x) has a nonzero Nyquist cos(8x) source.
    with pytest.raises(ValueError, match="Nyquist"):
        constrained_areal_initial_data(0.5, x, np.cos(x), np.sin(7*x))
    with pytest.raises(ValueError, match="overflow"):
        constrained_areal_initial_data(0.5, x, np.zeros(n), np.full(n, 1e308))
    with pytest.raises(ValueError, match="psi_x"):
        constrained_areal_initial_data(0.5, x, np.zeros(n), np.zeros(n), psi_x=np.zeros(3))


def test_trajectory_requires_increasing_matched_times_and_grid():
    from dataclasses import replace

    state = constrained_areal_initial_data(0.5, np.arange(8)*0.2, np.zeros(8), np.zeros(8))
    later = replace(state, t=0.6)
    for times, states in [
        ([0.5, 0.5], (state, state)),
        ([0.5, 0.7], (state, later)),
        ([0.5, 0.6], (state, replace(later, dx=0.3))),
        ([0.5, 0.6], (state, constrained_areal_initial_data(
            0.6, np.arange(10)*0.2, np.zeros(10), np.zeros(10)
        ))),
    ]:
        with pytest.raises(ValueError):
            PlanarRadionTrajectory(np.asarray(times), states)


def test_finite_overflow_and_evolving_unsafe_exponent_are_value_errors():
    state = constrained_areal_initial_data(0.5, np.arange(8)*0.2, np.zeros(8), np.zeros(8))
    from dataclasses import replace

    with pytest.raises(ValueError, match="physical domain"):
        evolve_planar_radion(replace(state, r_t=np.full(8, 1e308)), 0.6, 0.01)
    with pytest.raises(ValueError, match="exponential"):
        evolve_planar_radion(
            replace(state, sigma=np.full(8, 340.0), sigma_t=np.full(8, 1e4)),
            0.6, 0.01,
        )


def test_exponential_domain_boundary_is_not_clipped():
    from dataclasses import replace

    state = constrained_areal_initial_data(0.5, np.arange(8)*0.2, np.zeros(8), np.zeros(8))
    lower, upper = np.log(np.finfo(float).tiny), np.log(np.finfo(float).max)
    boundary = replace(state, sigma=np.full(8, 0.5 * upper))
    assert np.all(np.isfinite(np.exp(2.0 * boundary.sigma)))
    lower_boundary = replace(state, psi=np.full(8, 0.5 * lower))
    assert np.all(np.exp(2.0 * lower_boundary.psi) > 0.0)
    for field, outside in [
        ("sigma", np.nextafter(upper, np.inf)),
        ("psi", np.nextafter(lower, -np.inf)),
    ]:
        with pytest.raises(ValueError, match="exponential"):
            replace(state, **{field: np.full(8, outside)})


@pytest.mark.parametrize(
    "fields, message",
    [
        ({"sigma": 400.0}, "uplift conformal metric"),
        ({"sigma": -400.0}, "uplift conformal metric"),
        ({"sigma": 300.0, "psi": -200.0}, "uplift conformal metric"),
        ({"r": 1e200}, "uplift planar metric"),
        ({"r": 1e-200}, "uplift planar metric"),
        ({"psi": 400.0}, "uplift circle metric"),
        ({"psi": -400.0}, "uplift circle metric"),
    ],
)
def test_state_rejects_nonrepresentable_physical_uplift(fields, message):
    from dataclasses import replace

    state = constrained_areal_initial_data(0.5, np.arange(8)*0.2, np.zeros(8), np.zeros(8))
    with pytest.raises(ValueError, match=message):
        replace(state, **{name: np.full(8, value) for name, value in fields.items()})


def test_state_copies_and_locks_field_arrays():
    source = np.zeros(8)
    state = constrained_areal_initial_data(0.5, np.arange(8)*0.2, source, source)
    source[0] = 100.0
    assert state.psi[0] == 0.0
    for field in ("r", "sigma", "psi", "r_t", "sigma_t", "psi_t"):
        with pytest.raises(ValueError, match="read-only"):
            getattr(state, field)[0] = 1.0
