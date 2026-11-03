# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Direct metric-jet and stored-slab tests, independent of evolution solvers."""

import numpy as np
import pytest
from scipy.special import j0, j1

from src.physics.planar_radion.geometry import (
    evaluate_planar_ricci,
    ricci_frame_norm,
    ricci_from_metric_jet,
)


ETA = np.diag([-1.0, 1.0, 1.0, 1.0, 1.0])


def _power_jet(t, powers, coefficients=None):
    powers = np.asarray(powers, dtype=float)
    if coefficients is None:
        coefficients = np.diag(ETA)
    metric = np.diag(coefficients * t**powers)
    first = np.zeros((5, 5, 5))
    second = np.zeros((5, 5, 5, 5))
    first[0] = np.diag(coefficients * powers * t**(powers - 1))
    second[0, 0] = np.diag(
        coefficients * powers * (powers - 1) * t**(powers - 2)
    )
    return metric, first, second


def _kasner_fields(t, x, circle_sign):
    px, py, pchi = (0.5, 0.5, -0.5) if circle_sign < 0 else (-0.5, 0.5, 0.5)
    tau = ((1 - px) * t[:, None]) ** (1 / (1 - px))
    log_tau = np.log(tau) + np.zeros((len(t), len(x)))
    return (
        np.exp((py + pchi / 2) * log_tau),
        (px + pchi / 2) * log_tau,
        pchi * log_tau,
    )


def _bessel_fields(t, x, amplitude=0.17):
    tt, xx = np.meshgrid(t, x, indexing="ij")
    psi = amplitude * j0(tt) * np.cos(xx)
    sigma = (
        -np.log(tt) / 4
        + 3 * amplitude**2 * tt**2 * (j0(tt)**2 + j1(tt)**2) / 8
        - 3 * amplitude**2 * tt * j0(tt) * j1(tt) * np.cos(xx)**2 / 4
    )
    return np.sqrt(tt), sigma, psi


def test_minkowski_metric_jet_and_batched_jet_are_exactly_zero():
    for batch in ((), (3,), (2, 3)):
        metric = np.broadcast_to(ETA, batch + (5, 5))
        first = np.zeros(batch + (5, 5, 5))
        second = np.zeros(batch + (5, 5, 5, 5))
        np.testing.assert_array_equal(
            ricci_from_metric_jet(metric, first, second), np.zeros_like(metric)
        )


@pytest.mark.parametrize("p", [(0.5, 0.5, 0.5, -0.5), (-0.5, 0.5, 0.5, 0.5)])
@pytest.mark.parametrize("t", [0.8, 1.3, 2.1])
def test_curved_vacuum_kasner_exact_jets_both_radion_signs(p, t):
    powers = 2 * np.array([p[0], *p]) / (1 - p[0])
    coefficients = np.diag(ETA) * (1 - p[0])**powers
    jet = _power_jet(t, powers, coefficients)
    assert np.max(np.abs(jet[2])) > 0.01
    np.testing.assert_allclose(ricci_from_metric_jet(*jet), 0, atol=3e-13)


@pytest.mark.parametrize("p,coefficient", [
    ((0.5, 0.5, 0.5, -0.5), 4.5),
    ((-0.5, 0.5, 0.5, 0.5), 4.5),
    ((0.0, 0.0, 0.0, 1.0), 0.0),
])
@pytest.mark.parametrize("proper_time", [0.8, 1.7])
def test_kasner_riemann_curvature_and_flat_milne_control(p, coefficient, proper_time):
    metric, first, second = _power_jet(proper_time, [0, *np.multiply(2, p)])
    inverse = np.linalg.inv(metric)
    inverse_first = np.empty((5, 5, 5))
    for derivative in range(5):
        inverse_first[derivative] = -inverse @ first[derivative] @ inverse
    gamma = np.empty((5, 5, 5))
    gamma_first = np.empty((5, 5, 5, 5))
    for a, b, c in np.ndindex(5, 5, 5):
        kernel = first[b, c, :] + first[c, b, :] - first[:, b, c]
        gamma[a, b, c] = inverse[a] @ kernel / 2
        for derivative in range(5):
            kernel_first = (
                second[derivative, b, c, :] + second[derivative, c, b, :]
                - second[derivative, :, b, c]
            )
            gamma_first[derivative, a, b, c] = (
                inverse_first[derivative, a] @ kernel
                + inverse[a] @ kernel_first
            ) / 2
    riemann = np.empty((5, 5, 5, 5))
    for a, b, c, d in np.ndindex(5, 5, 5, 5):
        riemann[a, b, c, d] = (
            gamma_first[c, a, d, b] - gamma_first[d, a, c, b]
            + gamma[a, c, :] @ gamma[:, d, b]
            - gamma[a, d, :] @ gamma[:, c, b]
        )
    lowered = np.einsum("ae,ebcd->abcd", metric, riemann)
    kretschmann = np.einsum(
        "abcd,abcd,a,b,c,d", lowered, lowered, *([np.diag(inverse)] * 4)
    )
    exponents = np.asarray(p)
    analytic_coefficient = 4 * (
        np.sum(exponents**2 * (exponents - 1)**2)
        + sum(exponents[i]**2 * exponents[j]**2
              for i in range(4) for j in range(i + 1, 4))
    )
    assert analytic_coefficient == coefficient
    assert kretschmann == pytest.approx(coefficient / proper_time**4, abs=1e-13)
    np.testing.assert_allclose(
        ricci_from_metric_jet(metric, first, second), 0, atol=1e-14
    )
    if coefficient:
        assert np.max(np.abs(riemann)) > 0.01
    else:
        # Milne has nonzero metric second derivatives but no spacetime curvature.
        assert np.max(np.abs(second)) > 0
        np.testing.assert_allclose(riemann, 0, atol=1e-14)


def test_generic_nondiagonal_metric_and_all_coordinate_derivatives():
    jet = _power_jet(1.3, [2, 2, 2, 2, -2])
    transform = np.array([
        [1.0, 0.2, -0.1, 0.07, 0.12],
        [0.1, 1.0, 0.1, 0.0, 0.0],
        [0.0, 0.1, 1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 1.0, 0.1],
        [0.0, 0.0, 0.0, 0.1, 1.0],
    ])
    metric = transform.T @ jet[0] @ transform
    # Only the old time derivative is nonzero.
    first = transform[0, :, None, None] * (transform.T @ jet[1][0] @ transform)
    second = np.einsum(
        "c,d,ab->cdab", transform[0], transform[0],
        transform.T @ jet[2][0, 0] @ transform,
    )
    assert np.max(np.abs(metric - np.diag(np.diag(metric)))) > 0.01
    np.testing.assert_allclose(ricci_from_metric_jet(metric, first, second), 0, atol=1e-13)


def test_general_conformal_curvature_has_correct_mixed_components():
    t, x = 1.2, 0.7
    f = 0.1 * t**2 + 0.2 * t * x - 0.15 * x**2
    gradient = np.array([0.2 * t + 0.2 * x, 0.2 * t - 0.3 * x, 0, 0, 0])
    hessian = np.zeros((5, 5))
    hessian[:2, :2] = [[0.2, 0.2], [0.2, -0.3]]
    metric = np.exp(2 * f) * ETA
    first = 2 * gradient[:, None, None] * metric
    second = (
        2 * hessian + 4 * np.outer(gradient, gradient)
    )[:, :, None, None] * metric
    expected = (
        -3 * hessian - ETA * np.einsum("ab,ab", ETA, hessian)
        + 3 * (np.outer(gradient, gradient) - ETA * (gradient @ ETA @ gradient))
    )
    actual = ricci_from_metric_jet(metric, first, second)
    np.testing.assert_allclose(actual, expected, atol=1e-14)
    assert abs(actual[0, 1]) > 0.1
    np.testing.assert_allclose(actual, actual.T, atol=1e-14)


def test_scalar_flat_nonvacuum_is_not_mistaken_for_vacuum():
    jet = _power_jet(1.4, np.full(5, 4 / 3))
    ricci = ricci_from_metric_jet(*jet)
    scalar = np.einsum("ab,ab", np.linalg.inv(jet[0]), ricci)
    assert abs(scalar) < 1e-14
    assert ricci_frame_norm(jet[0], ricci) > 0.5


def test_frame_norm_is_positive_and_scales_every_component():
    metric = np.diag([-4.0, 9.0, 16.0, 25.0, 36.0])
    ricci = np.arange(25, dtype=float).reshape(5, 5) / 10
    scale = np.sqrt(np.abs(np.diag(metric)))
    expected = np.linalg.norm(ricci / scale[:, None] / scale[None, :])
    assert ricci_frame_norm(metric, ricci) == pytest.approx(expected)
    null_tensor = np.zeros((5, 5))
    null_tensor[0, 0] = null_tensor[0, 1] = 1
    assert np.einsum("ab,ac,bd,cd", null_tensor, ETA, ETA, null_tensor) == 0
    assert ricci_frame_norm(ETA, null_tensor) == pytest.approx(np.sqrt(2))


def test_flat_spacetime_slabs_shapes_times_and_zero_residual():
    t, x = np.linspace(0, 1, 9), np.arange(7) / 7
    one = np.ones((len(t), len(x)))
    result = evaluate_planar_ricci(t, x, one, one * 0, one * 0)
    assert result.ricci.shape == (5, 7, 5, 5)
    assert result.frame_norm.shape == result.scalar.shape == (5, 7)
    np.testing.assert_array_equal(result.times, t[2:-2])
    np.testing.assert_array_equal(result.ricci, 0)
    np.testing.assert_array_equal(result.frame_norm, 0)
    np.testing.assert_array_equal(result.scalar, 0)


@pytest.mark.parametrize("circle_sign", [-1, 1])
def test_kasner_slabs_converge_fourth_order(circle_sign):
    errors = []
    for n in (33, 65):
        t, x = np.linspace(1.0, 2.0, n), np.arange(5) / 5
        result = evaluate_planar_ricci(t, x, *_kasner_fields(t, x, circle_sign))
        errors.append(np.max(result.frame_norm))
    assert errors[1] < errors[0] / 10
    assert errors[1] < 2e-5


def test_wrong_jordan_frame_uplift_is_nonvacuum():
    t = 1.3
    # Correct Kasner Einstein-frame fields have sigma=log(t/2)/2,
    # psi=-log(t/2), r=sqrt(t/2). Omitting exp(-psi) from the 4D
    # block produces powers (1,1,1,1,-2), not vacuum (2,2,2,2,-2).
    correct = _power_jet(t, [2, 2, 2, 2, -2])
    wrong = _power_jet(t, [1, 1, 1, 1, -2])
    assert ricci_frame_norm(correct[0], ricci_from_metric_jet(*correct)) < 1e-13
    assert ricci_frame_norm(wrong[0], ricci_from_metric_jet(*wrong)) > 0.1


@pytest.fixture(scope="module")
def bessel_metric_jet():
    """Differentiate only diagonal metric entries, never a symbolic Ricci tensor."""
    sp = pytest.importorskip("sympy")
    t, x = sp.symbols("t x", positive=True)
    amplitude = sp.Rational(17, 100)
    b0, b1 = sp.besselj(0, t), sp.besselj(1, t)
    psi = amplitude * b0 * sp.cos(x)
    sigma = (
        -sp.log(t) / 4 + 3 * amplitude**2 * t**2 * (b0**2 + b1**2) / 8
        - 3 * amplitude**2 * t * b0 * b1 * sp.cos(x)**2 / 4
    )
    diagonal = [
        -sp.exp(2 * sigma - psi), sp.exp(2 * sigma - psi),
        t * sp.exp(-psi), t * sp.exp(-psi), sp.exp(2 * psi),
    ]
    expressions = (
        diagonal
        + [sp.diff(g, c) for c in (t, x) for g in diagonal]
        + [sp.diff(g, c, d) for c in (t, x) for d in (t, x) for g in diagonal]
    )
    function = sp.lambdify((t, x), expressions, modules="scipy", cse=True)

    def evaluate(time, position):
        values = np.asarray(function(time, position), dtype=float)
        metric = np.diag(values[:5])
        first, second = np.zeros((5, 5, 5)), np.zeros((5, 5, 5, 5))
        for coordinate in range(2):
            first[coordinate] = np.diag(values[5 + 5 * coordinate:10 + 5 * coordinate])
            for other in range(2):
                start = 15 + 5 * (2 * coordinate + other)
                second[coordinate, other] = np.diag(values[start:start + 5])
        return metric, first, second

    return evaluate


@pytest.mark.parametrize("t,x", [(0.8, 0.3), (1.3, 1.1), (2.1, 2.3)])
def test_bessel_inhomogeneous_vacuum_analytic_jets(bessel_metric_jet, t, x):
    metric, first, second = bessel_metric_jet(t, x)
    assert np.max(np.abs(first[1])) > 0.01
    assert np.max(np.abs(second[0, 1])) > 0.01
    ricci = ricci_from_metric_jet(metric, first, second)
    np.testing.assert_allclose(ricci, 0, atol=2e-14)


def test_inhomogeneous_bessel_slabs_converge_fourth_order():
    errors = []
    for n in (32, 64):
        t, x = np.linspace(1, 2, n + 1), np.arange(n) * 2 * np.pi / n
        result = evaluate_planar_ricci(t, x, *_bessel_fields(t, x))
        errors.append(np.max(result.frame_norm))
        assert np.all(np.isfinite(result.ricci))
    assert errors[1] < errors[0] / 12
    assert errors[1] < 2e-6


def test_nonvacuum_inhomogeneous_slabs_are_detected():
    t, x = np.linspace(1, 2, 13), np.arange(16) * 2 * np.pi / 16
    r, sigma, psi = _bessel_fields(t, x)
    sigma += 0.12 * np.cos(x)[None, :]
    result = evaluate_planar_ricci(t, x, r, sigma, psi)
    assert np.max(result.frame_norm) > 0.1
    assert np.max(np.abs(result.ricci[..., 0, 1])) > 0.01


@pytest.mark.parametrize("which", ["metric", "first", "second"])
@pytest.mark.parametrize("problem", ["shape", "nan", "complex"])
def test_invalid_metric_jet_inputs(which, problem):
    arrays = [ETA.copy(), np.zeros((5, 5, 5)), np.zeros((5, 5, 5, 5))]
    index = ["metric", "first", "second"].index(which)
    if problem == "shape":
        arrays[index] = arrays[index][:-1]
    elif problem == "nan":
        arrays[index].flat[0] = np.nan
    else:
        arrays[index] = arrays[index].astype(complex) + 1j
    with pytest.raises(ValueError, match={"shape": "shape", "nan": "finite", "complex": "real"}[problem]):
        ricci_from_metric_jet(*arrays)


@pytest.mark.parametrize("index,indices", [
    (0, (0, 1)), (1, (0, 0, 1)), (2, (0, 0, 0, 1)), (2, (0, 1, 0, 0)),
])
def test_metric_jet_symmetry_validation(index, indices):
    arrays = [ETA.copy(), np.zeros((5, 5, 5)), np.zeros((5, 5, 5, 5))]
    arrays[index][indices] = 1
    with pytest.raises(ValueError, match="symmetric"):
        ricci_from_metric_jet(*arrays)


@pytest.mark.parametrize("diagonal", [
    [1, 1, 1, 1, 1], [-1, -1, 1, 1, 1], [-1, 0, 1, 1, 1],
])
def test_lorentz_signature_validation(diagonal):
    with pytest.raises(ValueError, match="Lorentz"):
        ricci_from_metric_jet(np.diag(diagonal), np.zeros((5, 5, 5)), np.zeros((5, 5, 5, 5)))


@pytest.mark.parametrize("problem", ["short_t", "short_x", "nonuniform", "decreasing",
                                   "shape", "negative_r", "nan", "overflow"])
def test_invalid_slab_inputs(problem):
    t, x = np.linspace(1, 2, 7), np.arange(8) / 8
    r, sigma, psi = np.ones((7, 8)), np.zeros((7, 8)), np.zeros((7, 8))
    if problem == "short_t":
        t = t[:4]
    elif problem == "short_x":
        x = x[:4]
    elif problem == "nonuniform":
        t[3] += 0.01
    elif problem == "decreasing":
        x = x[::-1]
    elif problem == "shape":
        psi = psi[:-1]
    elif problem == "negative_r":
        r[0, 0] = -1
    elif problem == "nan":
        sigma[0, 0] = np.nan
    else:
        psi[0, 0] = 1000
    with pytest.raises(ValueError):
        evaluate_planar_ricci(t, x, r, sigma, psi)


def test_frame_norm_rejects_nondiagonal_metric_and_wrong_time_axis():
    metric = ETA.copy()
    metric[0, 1] = metric[1, 0] = 0.1
    with pytest.raises(ValueError, match="diagonal"):
        ricci_frame_norm(metric, np.zeros((5, 5)))
    with pytest.raises(ValueError, match="timelike"):
        ricci_frame_norm(np.diag([1, -1, 1, 1, 1]), np.zeros((5, 5)))
    with pytest.raises(ValueError, match="shape"):
        ricci_frame_norm(ETA, np.zeros((4, 4)))


def test_minimum_five_by_five_slab_is_supported():
    t, x = np.arange(5, dtype=float), np.arange(5, dtype=float)
    one = np.ones((5, 5))
    result = evaluate_planar_ricci(t, x, one, one * 0, one * 0)
    assert result.ricci.shape == (1, 5, 5, 5)
    np.testing.assert_array_equal(result.times, [2])
    np.testing.assert_array_equal(result.frame_norm, 0)


def test_overflowing_curvature_is_rejected_with_clear_error():
    metric, first, second = _power_jet(1.0, np.zeros(5))
    first[0, 0, 0] = 1e308
    with pytest.raises(ValueError, match="overflows|nonfinite"):
        ricci_from_metric_jet(metric, first, second)
