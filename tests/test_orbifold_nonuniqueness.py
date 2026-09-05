# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Independent finite-interval and internal-lift counterexamples."""

import math
from fractions import Fraction

import numpy as np
import pytest
from scipy.integrate import quad, trapezoid

from src.core.pillar636_su3_orbifold_equivalence import su5_involution
from src.core.pillar677_fermion_cl_orbifold_closure import (
    cl_generation, cl_orbifold_spectrum, cl_residual_higher_order_bound,
    dirac_boundary_form, dirac_zero_mode_condition, g4_bc_spectrum_report,
    rs1_nonuniqueness_example, rs1_weighted_overlap, rs1_zero_mode,
)


@pytest.mark.parametrize("chirality", ["L", "R"])
@pytest.mark.parametrize("c", [-3., -0.5, 0., 0.5, 1., 4.])
@pytest.mark.parametrize("k,length", [(0., 1.3), (0.7, 2.4)])
def test_action_weighted_normalisation_and_first_order_zero_mode(c, chirality, k, length):
    f = lambda y: rs1_zero_mode(c, y, k, length, chirality)
    norm, _ = quad(lambda y: math.exp(k*y) * f(y)**2, 0, length, epsabs=1e-12)
    assert norm == pytest.approx(1, abs=2e-12)
    y, h = 0.43*length, 1e-5
    derivative = (f(y+h)-f(y-h))/(2*h)
    expected = (-1 if chirality == "L" else 1)*c*k*f(y)
    assert derivative == pytest.approx(expected, abs=1e-9, rel=2e-9)
    # Undo the rescaling and use sqrt(|g|) Gamma^mu = exp(-3ky).
    norm_unrescaled, _ = quad(
        lambda y: math.exp(-3*k*y)*(math.exp(2*k*y)*f(y))**2, 0, length)
    assert norm_unrescaled == pytest.approx(1, abs=2e-12)


@pytest.mark.parametrize("c", [-1., 0., 0.5, 1., 2.])
def test_weighted_overlap_against_independent_quadrature(c):
    actual, _ = quad(lambda y: math.exp(y)*rs1_zero_mode(c, y)*rs1_zero_mode(0, y),
                     0, 2, epsabs=1e-12)
    assert rs1_weighted_overlap(c, 0) == pytest.approx(actual, abs=2e-12)
    assert rs1_weighted_overlap(c, c) == pytest.approx(1, abs=1e-12)
    assert rs1_weighted_overlap(c, 0) == pytest.approx(rs1_weighted_overlap(0, c))
    assert 0 < actual <= 1 + 1e-12


def test_same_geometry_and_domain_give_different_target_free_overlaps():
    result = rs1_nonuniqueness_example()
    overlaps = [row["overlap_with_fixed_reference"] for row in result["examples"]]
    assert overlaps[0] == pytest.approx(1)
    assert overlaps[0] > overlaps[1] > overlaps[2] > 0
    assert result["uses_mass_or_ckm_targets"] is False
    assert dirac_zero_mode_condition(-2)["normalisable"] is True
    assert dirac_zero_mode_condition(-2)["z2_bc_selects_uv"] is False
    assert dirac_zero_mode_condition(-2)["uv_localised"] is False


def test_right_handed_flat_point_is_minus_one_half_in_signed_mass_convention():
    y = np.linspace(0, 2, 9)
    for chirality, c in (("L", 0.5), ("R", -0.5)):
        density = [math.exp(t)*rs1_zero_mode(c, t, chirality=chirality)**2 for t in y]
        np.testing.assert_allclose(density, 0.5, atol=1e-14)


def test_green_identity_complex_profiles_and_maximal_chiral_endpoint_domain():
    k, c, length = 0.8, -0.7, 1.4
    u = lambda y: np.array([1+1j*y, (2-1j)*y*y])
    v = lambda y: np.array([y+2j, 1-y*y+1j*y])
    du = lambda y: np.array([1j, 2*(2-1j)*y])
    dv = lambda y: np.array([1, -2*y+1j])
    D = lambda f, df, y: math.exp(-k*y)*np.array([-df(y)[1]+c*k*f(y)[1],
                                                  df(y)[0]+c*k*f(y)[0]])
    integrand = lambda y: math.exp(k*y)*(np.vdot(u(y), D(v, dv, y))
                                         - np.vdot(D(u, du, y), v(y)))
    integral = quad(lambda y: integrand(y).real, 0, length)[0]
    integral += 1j*quad(lambda y: integrand(y).imag, 0, length)[0]
    assert integral == pytest.approx(dirac_boundary_form(u(0), u(length), v(0), v(length)))
    # Endpoint ordering (L0,R0,LL,RL). The 2D allowed subspace is its annihilator.
    J = np.array([[0, -1], [1, 0]])
    boundary = np.zeros((4, 4))
    boundary[:2, :2], boundary[2:, 2:] = -J, J
    allowed = np.eye(4)[:, [0, 2]]
    np.testing.assert_array_equal(allowed.T @ boundary @ allowed, 0)
    constraints = allowed.T @ boundary
    assert np.linalg.matrix_rank(constraints) == 2
    np.testing.assert_array_equal(constraints[:, [0, 2]], 0)
    assert np.linalg.matrix_rank(constraints[:, [1, 3]]) == 2


@pytest.mark.parametrize("c", [-1000., 0.5, 1000.])
def test_log_normalisation_handles_strong_localisation(c):
    assert math.isfinite(rs1_zero_mode(c, 0))
    assert math.isfinite(rs1_zero_mode(c, 2))
    assert rs1_weighted_overlap(c, c) == pytest.approx(1)


@pytest.mark.parametrize("kwargs", [{"c": math.inf}, {"y": math.nan},
                                     {"k": -1}, {"length": 0}, {"y": 3}])
def test_invalid_profile_inputs(kwargs):
    values = {"c": 0.2, "y": 0.5}
    values.update(kwargs)
    with pytest.raises(ValueError):
        rs1_zero_mode(**values)


def test_conditional_ladder_and_no_fabricated_remainder_bound():
    expected = (Fraction(71, 74), Fraction(141, 148), Fraction(35, 37))
    spectrum = cl_orbifold_spectrum()
    for i, value in enumerate(expected, start=1):
        assert cl_generation(i) == pytest.approx(float(value))
        assert Fraction(spectrum["generations"][i]["fraction"]) == value
    assert cl_generation(3) != pytest.approx(69/74)
    bounds = cl_residual_higher_order_bound()
    assert bounds["combined_bound"] == pytest.approx(float(Fraction(693, 405224)))
    assert bounds["bound_proved"] is False
    assert bounds["all_within_combined_bound"] is False
    assert bounds["per_generation"][2]["within_NLO_plus_NNLO"] is False
    assert bounds["per_generation"][3]["within_NLO_plus_NNLO"] is False
    assert "arithmetic proxy only" in g4_bc_spectrum_report()["lean4_scope"]


@pytest.mark.parametrize("negative,expected", [(0, 24), (2, 12), (4, 16)])
def test_internal_involution_on_explicit_traceless_hermitian_basis(negative, expected):
    report = su5_involution(negative)
    P = np.diag(report["diagonal"])
    basis = []
    for i in range(5):
        for j in range(i+1, 5):
            real = np.zeros((5, 5), complex)
            imag = np.zeros((5, 5), complex)
            real[i, j] = real[j, i] = 1
            imag[i, j], imag[j, i] = 1j, -1j
            basis.extend((real, imag))
    for i in range(4):
        diagonal = np.zeros((5, 5))
        diagonal[i, i], diagonal[4, 4] = 1, -1
        basis.append(diagonal)
    even = sum(np.array_equal(P @ T @ P, T) for T in basis)
    odd = sum(np.array_equal(P @ T @ P, -T) for T in basis)
    assert even == expected == report["even_generators"]
    assert even + odd == 24
    np.testing.assert_array_equal(P @ P, np.eye(5))
    assert np.linalg.det(P) == pytest.approx(1)
    if negative == 2:
        assert "/Z6" in report["fixed_group_in_SU5"]


@pytest.mark.parametrize("negative", [True, 2.0, 1, 3, -2])
def test_internal_lift_rejects_invalid_counts(negative):
    with pytest.raises(ValueError):
        su5_involution(negative)


def test_odd_field_even_radion_has_no_boundary_or_constant_mode():
    y = np.linspace(-math.pi, math.pi, 1001)
    odd = np.sin(y) + 0.3*np.sin(3*y)
    even = 2 + 0.2*np.cos(y)
    composite = even**2 * odd
    np.testing.assert_allclose(composite, -composite[::-1], atol=1e-14)
    np.testing.assert_allclose(composite[[0, 500, -1]], 0, atol=1e-14)
    assert abs(trapezoid(composite, y)) < 1e-13
