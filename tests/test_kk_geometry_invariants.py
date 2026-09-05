# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Independent line-element, analytic curvature and derivative-convention checks."""

import importlib.util
from pathlib import Path

import numpy as np
import pytest
import sympy as sp

from src.core import metric
from src.core.evolution import _divergence_vec


def fields(n):
    x = np.linspace(-0.7, 0.8, n)
    g = np.tile(np.diag([-1., 1., 1., 1.]), (n, 1, 1))
    B = np.column_stack((0.2 * np.sin(x), 0.3 * x**2,
                         0.1 * np.cos(x), 0.15 * x))
    phi = 1.7 * np.exp(0.2 * x)
    return x, g, B, phi


def test_symbolic_completed_square_schur_inverse_and_gauge_pullback():
    p, lam = sp.symbols("p lambda", positive=True)
    b0, b1, q0, q1 = sp.symbols("b0 b1 q0 q1", real=True)
    dt, dx, dy = sp.symbols("dt dx dy", real=True)
    line = -dt**2 + 2 * dx**2 + p**2 * (dy + lam * (b0 * dt + b1 * dx))**2
    coords = (dt, dx, dy)
    G = sp.hessian(line, coords) / 2
    assert G[0, 2] == lam * p**2 * b0
    assert sp.simplify(G.det() + 2 * p**2) == 0
    schur = G[:2, :2] - G[:2, 2:3] * G[2:3, :2] / G[2, 2]
    assert sp.simplify(schur) == sp.diag(-1, 2)
    inverse = sp.Matrix([[-1, 0, lam * b0], [0, sp.Rational(1, 2), -lam*b1/2],
                         [lam*b0, -lam*b1/2, p**-2 + lam**2*(-b0**2+b1**2/2)]])
    assert sp.simplify(G * inverse) == sp.eye(3)
    transformed = line.subs({b0: b0 + q0, b1: b1 + q1,
                            dy: dy - lam * (q0 * dt + q1 * dx)}, simultaneous=True)
    assert sp.simplify(transformed - line) == 0


@pytest.mark.parametrize("lam", [-1.3, 0., 2.1])
def test_numeric_line_element_inverse_determinant_and_signature(lam):
    x, g, B, phi = fields(9)
    g[:, 0, 2] = g[:, 2, 0] = 0.1
    G = metric.assemble_5d_metric(g, B, phi, lam)
    rng = np.random.default_rng(842)
    v = rng.normal(size=(len(x), 5))
    expected = np.einsum("ni,nij,nj->n", v[:, :4], g, v[:, :4])
    expected += phi**2 * (v[:, 4] + lam * np.sum(B * v[:, :4], axis=1))**2
    np.testing.assert_allclose(np.einsum("ni,nij,nj->n", v, G, v), expected)
    np.testing.assert_allclose(np.linalg.det(G), phi**2 * np.linalg.det(g))
    np.testing.assert_allclose(G @ metric.inverse_5d_metric(g, B, phi, lam),
                               np.broadcast_to(np.eye(5), G.shape), atol=2e-15)
    assert np.all(np.sum(np.linalg.eigvalsh(G) < 0, axis=1) == 1)


@pytest.mark.parametrize("coordinate", [0, 1, 2, 3])
def test_field_strength_differentiates_exactly_one_coordinate(coordinate):
    x = np.linspace(-1, 1, 11)
    slopes = np.array([2., -3., 5., 7.])
    B = x[:, None]**2 * slopes
    expected = np.zeros((len(x), 4, 4))
    expected[:, coordinate, :] = 2*x[:, None]*slopes
    expected[:, :, coordinate] -= 2*x[:, None]*slopes
    np.testing.assert_allclose(metric.field_strength(B, x[1]-x[0], coordinate),
                               expected, atol=1e-13)


def test_longitudinal_pure_gauge_and_divergence():
    x = np.linspace(-1, 1, 11)
    B = np.zeros((len(x), 4))
    B[:, 1] = x**2
    np.testing.assert_allclose(metric.field_strength(B, x[1]-x[0]), 0)
    B[:, 0] = 100*x
    np.testing.assert_allclose(_divergence_vec(B, x[1]-x[0]), 2*x, atol=1e-13)


@pytest.mark.parametrize("coordinate", [-1, 4, 1.5])
def test_invalid_base_coordinate_rejected(coordinate):
    x, g, B, phi = fields(5)
    with pytest.raises(ValueError, match="coordinate_index"):
        metric.compute_5d_curvature(g, B, phi, x[1]-x[0], coordinate_index=coordinate)


def test_analytic_circle_reduction_and_gauge_scalar_converge_quadratically():
    errors, gauge_errors = [], []
    for n in (129, 257, 513):
        x, g, B, phi = fields(n)
        dx, lam = x[1]-x[0], 1.3
        # Independent continuum identity for a flat base, with electric AND magnetic H.
        h_squared = 2 * (-(0.2*np.cos(x))**2 + (-0.1*np.sin(x))**2 + 0.15**2)
        expected = -lam**2 * phi**2 * h_squared / 4 - 2*0.2**2
        *_, scalar = metric.compute_5d_curvature(g, B, phi, dx, lam)
        shifted = B.copy()
        shifted[:, 1] += 0.4 * x  # dχ with χ=0.2x²
        *_, scalar_shift = metric.compute_5d_curvature(g, shifted, phi, dx, lam)
        errors.append(np.max(np.abs(scalar[3:-3] - expected[3:-3])))
        gauge_errors.append(np.max(np.abs(scalar_shift[3:-3] - scalar[3:-3])))
    assert errors[-1] < 1e-5
    assert gauge_errors[-1] < 6e-6
    assert all(a/b > 3.7 for a, b in zip(errors, errors[1:]))
    assert all(a/b > 3.7 for a, b in zip(gauge_errors, gauge_errors[1:]))


def test_frw_time_derivatives_are_explicit_not_spatial_aliases():
    t = np.linspace(-0.3, 0.3, 129)
    h = 0.4
    g = np.tile(np.eye(4), (len(t), 1, 1))
    g[:, 0, 0] = -1
    g[:, 1, 1] = g[:, 2, 2] = g[:, 3, 3] = np.exp(2*h*t)
    B, phi = np.zeros((len(t), 4)), np.ones(len(t))
    gamma, _, _, scalar = metric.compute_5d_curvature(
        g, B, phi, t[1]-t[0], coordinate_index=0)
    np.testing.assert_allclose(gamma[2:-2, 1, 0, 1], h, rtol=1e-5)
    np.testing.assert_allclose(scalar[3:-3], 12*h*h, rtol=2e-5)
    *_, spatial_scalar = metric.compute_5d_curvature(g, B, phi, t[1]-t[0])
    assert np.all(spatial_scalar[3:-3] < 0)


def test_full_scalar_is_not_legacy_coordinate_block_contraction():
    x, g, B, phi = fields(129)
    B[:] = 0
    dx = x[1]-x[0]
    *_, full = metric.compute_5d_curvature(g, B, phi, dx)
    *_, block = metric.compute_curvature(g, B, phi, dx)
    np.testing.assert_allclose(full[3:-3], -0.08, rtol=2e-5)
    np.testing.assert_allclose(block[3:-3], -0.04, rtol=2e-5)


def test_inverse_radius_api_is_not_a_nonminimal_action_coefficient():
    x, g, B, phi = fields(17)
    diagnostic, cross = metric.extract_alpha_from_curvature(g, B, phi, x[1]-x[0])
    assert diagnostic == pytest.approx(np.mean(phi**-2))
    assert metric.inverse_radius_squared(phi) == diagnostic
    assert metric.inverse_radius_squared(2*phi) == pytest.approx(diagnostic/4)
    assert diagnostic > 0
    assert np.linalg.norm(cross) > 0
    # The independently checked circle reduction has H², but no R H² operator.
    from src.core.symbolic_metric import symbolic_5d_ricci_scalar_decomposition
    R5, symbols = symbolic_5d_ricci_scalar_decomposition()
    density = sp.expand(symbols["phi"]*R5)
    assert density.coeff(symbols["R4"]).coeff(symbols["H_sq"]) == 0
    assert metric.circle_eh_rh2_coefficient() == 0.0
    assert density.coeff(symbols["H_sq"]) == -symbols["lam"]**2*symbols["phi"]**3/4


@pytest.mark.parametrize("phi", [[], [0.], [np.nan], [np.inf]])
def test_inverse_radius_diagnostic_rejects_invalid_input(phi):
    with pytest.raises(ValueError, match="finite nonzero"):
        metric.inverse_radius_squared(phi)


def test_proof_entry_point_is_canonical_not_independent_evidence():
    path = Path(__file__).resolve().parents[1] / "proof" / "metric.py"
    spec = importlib.util.spec_from_file_location("proof_metric_exports", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.assemble_5d_metric is metric.assemble_5d_metric
    assert module.compute_5d_curvature is metric.compute_5d_curvature


def test_proof_evolution_import_spatial_divergence_and_smoke_step():
    from proof import evolution
    x = np.linspace(-1, 1, 9)
    vector = np.column_stack((100*x, x*x, np.zeros_like(x), np.zeros_like(x)))
    np.testing.assert_allclose(evolution._divergence_vec(vector, x[1]-x[0]),
                               2*x, atol=1e-12)
    assert evolution.field_strength is metric.field_strength
    result = evolution.step(evolution.FieldState.flat(N=9, dx=0.1), dt=1e-5)
    assert all(np.isfinite(a).all() for a in (result.g, result.B, result.phi))


def test_warped_slice_uses_radius_in_entire_connection_square():
    x, g, B, phi = fields(9)
    radius, y, k, lam = 2 + 0.1*x, -0.4, 0.6, 1.2
    G = metric.assemble_warped_5d_metric(g, B, phi, radius, k, lam, y)
    schur = G[:, :4, :4] - G[:, :4, 4, None] * G[:, None, 4, :4] / radius[:, None, None]**2
    np.testing.assert_allclose(schur, np.exp(-2*k*abs(y)*radius)[:, None, None]*g,
                               atol=1e-15)
    np.testing.assert_allclose(G, metric.assemble_warped_5d_metric(
        g, B, 7*phi, radius, k, lam, y))


def test_optional_jax_paths_against_analytic_derivatives_and_numpy():
    pytest.importorskip("jax")
    from src.core.jax_backend import field_strength_jax, assemble_metric_jax
    from src.core.jax_metric import jax_field_strength, jax_assemble_5d_metric, jax_compute_curvature
    x, g, B, phi = fields(17)
    dx = x[1]-x[0]
    for assemble in (assemble_metric_jax, jax_assemble_5d_metric):
        np.testing.assert_allclose(assemble(g, B, phi, 1.3),
                                   metric.assemble_5d_metric(g, B, phi, 1.3), atol=1e-12)
    for strength in (field_strength_jax, jax_field_strength):
        np.testing.assert_allclose(strength(B, dx), metric.field_strength(B, dx), atol=1e-12)
    for a, b in zip(jax_compute_curvature(g, B, phi, dx),
                    metric.compute_curvature(g, B, phi, dx)):
        np.testing.assert_allclose(a, b, atol=1e-10)


def test_geodesic_fifth_momentum_and_lorentz_force_are_gauge_invariant():
    from src.core.kk_geodesic_reduction import fifth_momentum, lorentz_acceleration
    x, g, B, phi = fields(17)
    lam = 1.3
    u4 = np.tile([1., 0.2, -0.1, 0.3], (len(x), 1))
    u5 = 0.4 + 0.1*x
    U = np.column_stack((u4, u5))
    G = metric.assemble_5d_metric(g, B, phi, lam)
    p5 = fifth_momentum(B, phi, u4, u5, lam)
    np.testing.assert_allclose(p5, np.einsum("ni,ni->n", G[:, 4, :], U))
    shift = np.zeros_like(B)
    shift[:, 1] = 0.3*x
    u5_shift = u5 - lam*np.sum(shift*u4, axis=1)
    np.testing.assert_allclose(p5, fifth_momentum(B+shift, phi, u4, u5_shift, lam))
    for a, b in zip(lorentz_acceleration(B, phi, u4, u5, g, x[1]-x[0], lam),
                    lorentz_acceleration(B+shift, phi, u4, u5_shift, g, x[1]-x[0], lam)):
        np.testing.assert_allclose(a, b, atol=1e-14)


def test_full_geodesic_reduces_to_gravity_lorentz_and_radion_with_convergence():
    from src.core.kk_geodesic_reduction import geodesic_decomposition, verify_christoffel_nu5
    errors, christoffel_errors = [], []
    for n in (129, 257, 513):
        x, g, B, phi = fields(n)
        g[:, 0, 0] = -np.exp(0.1*x)
        dx, lam = x[1]-x[0], 1.3
        u4 = np.tile([1., 0.2, -0.1, 0.3], (n, 1))
        u5 = 0.4 + 0.1*x
        result = geodesic_decomposition(g, B, phi, u4, u5, dx, lam)
        radion = (result.p5**2 / phi**3 * 0.2*phi)[:, None] * np.linalg.inv(g)[:, :, 1]
        errors.append(np.max(np.abs((result.residual+radion)[3:-3])))
        check = verify_christoffel_nu5(g, B, phi, dx, lam)
        christoffel_errors.append(np.max(np.abs(
            (check["Gamma_nu5"]-check["expected"])[3:-3])))
    assert errors[-1] < 2e-6
    assert christoffel_errors[-1] < 2e-6
    assert all(a/b > 3.7 for a, b in zip(errors, errors[1:]))
    assert all(a/b > 3.7 for a, b in zip(christoffel_errors, christoffel_errors[1:]))
