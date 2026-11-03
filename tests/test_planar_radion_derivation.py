# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

import sympy as sp

from src.physics.planar_radion.derivation import (
    areal_sigma_integrability_residuals,
    bessel_mode_residual,
    constraint_propagation_residuals,
    direct_ricci_residuals,
    frw_branch_residuals,
    frw_kasner_parameters,
    frozen_spectator_residuals,
    metric_variation_residuals,
)


def test_pre_gauge_metric_variation_gives_both_null_constraints():
    assert metric_variation_residuals() == {
        "uu": 0,
        "vv": 0,
        "uv": 0,
        "radion_euler_reduction": 0,
        "psi_euler_reduction": 0,
    }


def test_null_constraints_propagate_from_evolution_equations_alone():
    assert constraint_propagation_residuals() == {"u": 0, "v": 0}


def test_actual_four_dimensional_metric_ricci_matches_warped_formulas():
    residuals = direct_ricci_residuals()
    assert len(residuals) == 16
    assert set(residuals) == {f"R_{i}{j}" for i in range(4) for j in range(4)}
    assert all(value == 0 for value in residuals.values())


def test_direct_five_dimensional_uplift_ricci_vanishes_on_reduced_equations():
    from src.physics.planar_radion.derivation import direct_five_dimensional_uplift_residuals

    residuals = direct_five_dimensional_uplift_residuals()
    assert len(residuals) == 25
    assert all(value == 0 for value in residuals.values())


def test_frozen_real_spectator_has_nonzero_stress_unless_constant():
    residuals = frozen_spectator_residuals()
    assert residuals["base_einstein_uu"] == 0
    assert residuals["base_einstein_uv"] == 0
    assert residuals["base_einstein_vv"] == 0
    sigma = sp.Function("sigma")(sp.Symbol("u", real=True), sp.Symbol("v", real=True))
    r0 = sp.Symbol("r0", positive=True)
    curvature = 8 * sp.exp(-2 * sigma) * sp.diff(
        sigma, sp.Symbol("u", real=True), sp.Symbol("v", real=True)
    )
    assert sp.simplify(residuals["transverse_einstein_xx"] + r0**2 * curvature / 2) == 0
    assert sp.simplify(residuals["transverse_einstein_yy"] + r0**2 * curvature / 2) == 0
    assert sp.simplify(residuals["radion_equation"] - 2 * r0 * curvature) == 0
    assert residuals["source_uu"] == sp.Rational(3, 2) * sp.Symbol(
        "psi_u", real=True
    ) ** 2
    assert residuals["source_vv"] == sp.Rational(3, 2) * sp.Symbol(
        "psi_v", real=True
    ) ** 2
    assert residuals["nonflat_example"] != 0
    assert residuals["transverse_einstein_xx"] != 0
    assert residuals["transverse_einstein_yy"] != 0


def test_exact_frw_branches_and_kasner_mapping_for_either_sign():
    assert all(value == 0 for value in frw_branch_residuals().values())
    for sign in (-1, 1):
        parameters = frw_kasner_parameters(sign * 2, sp.Rational(3, 5))
        p_x = parameters["longitudinal_kasner_exponent"]
        p_perp = parameters["transverse_kasner_exponent"]
        scalar = parameters["scalar_kasner_amplitude"]
        assert sp.simplify(p_x + 2 * p_perp - 1) == 0
        assert sp.simplify(p_x**2 + 2 * p_perp**2 + sp.Rational(3, 2) * scalar**2 - 1) == 0


def test_bessel_benchmark_and_periodic_momentum_compatibility():
    result = bessel_mode_residual()
    assert result["mode_equation"] == 0
    assert result["periodic_wavenumber"] == 2 * sp.pi * sp.Symbol(
        "n", integer=True
    ) / sp.Symbol("L", positive=True, real=True)
    assert result["momentum_integral"] == 0
    assert all(value == 0 for value in result["sigma_integrability"].values())


def test_frozen_radion_equation_requires_flat_two_metric():
    residual = frozen_spectator_residuals()["radion_equation"]
    # With psi constant and r constant, delta S / delta r = 2 r R[q].
    assert sp.simplify(residual.subs(sp.diff(
        sp.Function("sigma")(sp.Symbol("u", real=True), sp.Symbol("v", real=True)),
        sp.Symbol("u", real=True),
        sp.Symbol("v", real=True),
    ), 0)) == 0
