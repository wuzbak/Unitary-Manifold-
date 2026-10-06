# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.maxwell_kk_reduction import (
    K_CS,
    M_PL_GEV,
    N_W,
    PI_K_R,
    PILLAR,
    PILLAR_STATUS,
    MaxwellTestFieldState,
    kk_reduction_gauge_coupling,
    maxwell_equations_4d,
    maxwell_kk_reduction_report,
    maxwell_test_field_cfl_timestep,
    maxwell_test_field_diagnostics,
    maxwell_test_field_rhs,
    maxwell_test_field_surface,
    metric_kk_decomposition,
    photon_z2_parity,
    photon_zero_mode_bc,
    step_maxwell_test_field,
)


def test_constants_match_context():
    assert N_W == 5
    assert K_CS == 74
    assert PI_K_R == pytest.approx(37.0)
    assert M_PL_GEV > 1e18


def test_pillar_metadata():
    assert PILLAR == 773
    assert PILLAR_STATUS == "CIRCLE_MAXWELL_CONDITIONAL_ORBIFOLD_PHOTON_UNSUPPORTED"


def test_metric_decomposition_fields_present():
    result = metric_kk_decomposition()
    assert result["status"] == "DERIVED"
    assert result["fields"]["A_mu"].startswith("KK U(1)")
    assert "G_munu" in result["value"]
    assert "G_mu5" in result["value"]
    assert "G_55" in result["value"]


def test_metric_vector_constant_mode_is_projected_out_not_massless():
    result = photon_zero_mode_bc()
    assert result["status"] == "PROJECTED_OUT"
    assert result["value"] is None
    assert result["photon_mass_zero_gev"] is None
    assert result["zero_mode_survives"] is False
    assert result["boundary_conditions"] == ["f0(0)=0", "f0(pi R)=0"]
    assert result["observed_photon_identified"] is False


def test_independent_even_bulk_u1_retains_conditional_neumann_solution():
    result = photon_zero_mode_bc(field_origin="independent_bulk_u1")
    assert result["status"] == "CONDITIONAL"
    assert result["field_origin"] == "independent_bulk_u1"
    assert result["photon_mass_zero_gev"] == 0.0
    assert result["zero_mode_profile"] == "constant"
    assert result["c2_forced"] == 0.0
    assert result["boundary_conditions"] == ["f0'(0)=0", "f0'(pi R)=0"]
    assert result["zero_mode_survives"] is True
    assert result["observed_photon_identified"] is False


def test_field_origin_must_be_explicitly_supported():
    with pytest.raises(ValueError, match="field_origin"):
        photon_zero_mode_bc(field_origin="photon")


def test_zero_mode_bc_requires_positive_pi_kr():
    with pytest.raises(ValueError):
        photon_zero_mode_bc(pi_kr=0.0)


def test_z2_parity_assignments():
    result = photon_z2_parity()
    assert result["a_mu_parity"] == -1
    assert result["g_mu5_parity"] == -1
    assert result["g_55_parity"] == 1
    assert result["survives_orbifold"] is False
    assert result["a_mu_parity"] * result["g_55_parity"] == result["g_mu5_parity"]


def test_gauge_coupling_returns_dict():
    result = kk_reduction_gauge_coupling()
    assert result["status"] == "CONSTRAINED"
    assert result["epistemic_status"] == "CONSTRAINED"


def test_tree_level_g4_sq_is_order_unity():
    result = kk_reduction_gauge_coupling()
    assert 0.9 < result["g4_tree_sq"] < 1.1


def test_effective_g4_sq_is_smaller_after_warp_overlap():
    result = kk_reduction_gauge_coupling()
    assert result["g4_effective_sq"] < result["g4_tree_sq"]
    assert 0.09 < result["g4_effective_sq"] < 0.10


def test_assigned_coupling_obeys_its_formula_not_an_em_prediction():
    result = kk_reduction_gauge_coupling()
    alpha = result["alpha_em_geometric"]
    assert alpha == pytest.approx(result["g4_effective_sq"] / (4 * math.pi))
    assert result["inverse_alpha_em"] == pytest.approx(1 / alpha)
    assert result["observed_photon_identified"] is False
    assert result["coupling_derivation_complete"] is False
    assert "independent bulk U(1)" in result["model_scope"]


def test_custom_g5_sq_changes_coupling():
    default = kk_reduction_gauge_coupling()["g4_effective_sq"]
    modified = kk_reduction_gauge_coupling(g5_sq=2.0 * K_CS / M_PL_GEV)["g4_effective_sq"]
    assert modified == pytest.approx(2.0 * default, rel=1e-12)


def test_negative_g5_raises():
    with pytest.raises(ValueError):
        kk_reduction_gauge_coupling(g5_sq=-1.0)


def test_maxwell_equations_content():
    result = maxwell_equations_4d()
    assert result["status"] == "CONDITIONAL"
    assert result["metric_orbifold_zero_mode"] is False
    assert result["mass_term"] == 0.0
    assert "partial_nu F^{mu nu}" in result["equation_of_motion"]
    assert "F_{mu nu}" in result["field_strength"]


def test_report_contains_sections():
    report = maxwell_kk_reduction_report()
    assert report["status"] == PILLAR_STATUS
    for key in ("decomposition", "boundary_value_problem", "parity", "gauge_coupling", "maxwell_equations"):
        assert key in report


def test_report_does_not_promote_conditional_coupling_to_observed_photon():
    report = maxwell_kk_reduction_report()
    assert report["gauge_coupling"]["alpha_em_geometric"] > 0
    assert report["value"]["alpha_em_geometric"] is None
    assert report["value"]["photon_mass_zero_gev"] is None
    assert report["observed_photon_identified"] is False
    assert report["closure_earned"] is False


@pytest.mark.parametrize("pi_kr", [1.0, 10.0, 37.0, 50.0])
def test_varying_warp_parameter_cannot_reverse_orbifold_projection(pi_kr):
    metric = photon_zero_mode_bc(pi_kr)
    independent = photon_zero_mode_bc(pi_kr, field_origin="independent_bulk_u1")
    assert metric["zero_mode_survives"] is False
    assert independent["zero_mode_survives"] is True


@pytest.mark.parametrize("pi_kr", [float("nan"), float("inf")])
def test_nonfinite_geometry_is_rejected(pi_kr):
    with pytest.raises(ValueError, match="finite"):
        photon_zero_mode_bc(pi_kr)


def _traveling_fields(x, time, mode, direction, polarization, amplitude=0.3, omega=None):
    """Continuum plane wave, or independent centered-grid Fourier eigenmode."""
    frequency = mode if omega is None else omega
    profile = amplitude * np.cos(mode * x - direction * frequency * time + 0.23)
    electric = np.zeros((len(x), 3))
    magnetic = np.zeros_like(electric)
    electric[:, polarization] = profile
    if polarization == 1:
        magnetic[:, 2] = direction * profile
    else:
        magnetic[:, 1] = -direction * profile
    return electric, magnetic


def _standing_fields(x, time, mode, polarization, amplitude=0.3):
    electric = np.zeros((len(x), 3))
    magnetic = np.zeros_like(electric)
    electric[:, polarization] = amplitude * np.cos(mode * x) * np.cos(mode * time)
    magnetic_profile = amplitude * np.sin(mode * x) * np.sin(mode * time)
    if polarization == 1:
        magnetic[:, 2] = magnetic_profile
    else:
        magnetic[:, 1] = -magnetic_profile
    return electric, magnetic


def _integrate_maxwell(state, duration, nominal_dt):
    steps = math.ceil(duration / nominal_dt)
    dt = duration / steps
    for _ in range(steps):
        state = step_maxwell_test_field(state, dt)
    return state


def _field_error(state, electric, magnetic):
    return float(np.sqrt(np.mean((state.electric - electric)**2 + (state.magnetic - magnetic)**2)))


def test_physical_time_surface_is_scoped_without_contract_promotion():
    surface = maxwell_test_field_surface()
    assert surface["status"] == "PRESCRIBED_BACKGROUND_TEST_FIELD"
    assert "Einstein-frame Minkowski" in surface["background"]
    assert "positive constant" in surface["radion"]
    assert "circle" in surface["compactification"]
    assert "not the metric orbifold" in surface["compactification"]
    assert "physical" in surface["time"] and "lapse 1" in surface["time"]
    assert "no cleaning" in surface["constraint_policy"]
    assert "discrete" in surface["constraint_policy"]
    assert "not a continuum certificate" in surface["constraint_policy"]
    assert "not evolved" in surface["backreaction"]
    for name in (
        "self_consistent_backreaction", "observed_photon_identified",
        "action_evolution_contract_promoted", "closure_earned",
    ):
        assert surface[name] is False
    assert any("F^2=0" in note for note in surface["limitations"])
    assert any("Nyquist" in note for note in surface["limitations"])
    assert maxwell_kk_reduction_report()["closure_earned"] is False


@pytest.mark.parametrize("direction", [-1, 1])
@pytest.mark.parametrize("polarization", [1, 2])
@pytest.mark.parametrize("mode", [1, 3, 5])
def test_plane_waves_propagate_in_both_directions_and_polarizations(direction, polarization, mode):
    count = 512
    dx = 2 * math.pi / count
    x = np.arange(count) * dx
    electric, magnetic = _traveling_fields(x, 0.0, mode, direction, polarization)
    initial = MaxwellTestFieldState(electric, magnetic, dx, phi0=1.7, lam=0.4)
    duration = 0.73
    final = _integrate_maxwell(initial, duration, 0.25 * dx)
    expected_e, expected_b = _traveling_fields(x, duration, mode, direction, polarization)
    assert _field_error(final, expected_e, expected_b) < 6e-4
    assert final.time == pytest.approx(duration)
    diagnostics = maxwell_test_field_diagnostics(final)
    assert diagnostics["electric_gauss_rms"] == 0.0
    assert diagnostics["magnetic_gauss_rms"] == 0.0
    np.testing.assert_allclose(diagnostics["F2_lorentzian"], 0.0, atol=1e-15)
    assert direction * np.mean(diagnostics["poynting_flux"][:, 0]) > 0.0
    np.testing.assert_array_equal(diagnostics["poynting_flux"][:, 1:], 0.0)
    assert final.dx == dx and final.phi0 == initial.phi0 and final.lam == initial.lam


@pytest.mark.parametrize("polarization", [1, 2])
@pytest.mark.parametrize("mode", [1, 3])
def test_standing_wave_fields_energy_flux_and_radion_source_against_analytic_solution(polarization, mode):
    count = 512
    dx = 2 * math.pi / count
    x = np.arange(count) * dx
    amplitude = 0.3
    time = 0.37
    electric, magnetic = _standing_fields(x, 0.0, mode, polarization, amplitude)
    initial = MaxwellTestFieldState(electric, magnetic, dx, phi0=1.4, lam=0.7)
    final = _integrate_maxwell(initial, time, 0.25 * dx)
    expected_e, expected_b = _standing_fields(x, time, mode, polarization, amplitude)
    assert _field_error(final, expected_e, expected_b) < 1.5e-4
    diagnostics = maxwell_test_field_diagnostics(final)
    weight = 0.7**2 * 1.4**3
    expected_density = 0.5 * weight * amplitude**2 * (
        np.cos(mode * x)**2 * np.cos(mode * time)**2
        + np.sin(mode * x)**2 * np.sin(mode * time)**2
    )
    expected_flux_x = weight * amplitude**2 * (
        np.cos(mode * x) * np.sin(mode * x) * np.cos(mode * time) * np.sin(mode * time)
    )
    np.testing.assert_allclose(diagnostics["energy_density"], expected_density, atol=6e-5, rtol=0)
    np.testing.assert_allclose(diagnostics["poynting_flux"][:, 0], expected_flux_x, atol=6e-5, rtol=0)
    np.testing.assert_array_equal(diagnostics["poynting_flux"][:, 1:], 0.0)
    assert diagnostics["energy"] == pytest.approx(weight * amplitude**2 * (2 * math.pi) / 4, rel=1e-8)
    assert diagnostics["electric_gauss_rms"] == 0.0
    assert diagnostics["magnetic_gauss_rms"] == 0.0
    expected_f2 = 2 * amplitude**2 * (
        np.sin(mode * x)**2 * np.sin(mode * time)**2
        - np.cos(mode * x)**2 * np.cos(mode * time)**2
    )
    np.testing.assert_allclose(diagnostics["F2_lorentzian"], expected_f2, atol=1e-4, rtol=0)
    assert np.max(np.abs(diagnostics["F2_lorentzian"])) > 0.01


@pytest.mark.parametrize("polarization", [1, 2])
def test_local_energy_balance_converges_to_independent_analytic_flux_divergence(polarization):
    errors = []
    amplitude, mode, time = 0.3, 3, 0.37
    weight = 0.7**2 * 1.4**3
    for count in (32, 64, 128):
        dx = 2 * math.pi / count
        x = np.arange(count) * dx
        electric, magnetic = _standing_fields(x, time, mode, polarization, amplitude)
        state = MaxwellTestFieldState(electric, magnetic, dx, phi0=1.4, lam=0.7)
        electric_rhs, magnetic_rhs = maxwell_test_field_rhs(state)
        energy_time_derivative = weight * np.sum(
            electric * electric_rhs + magnetic * magnetic_rhs, axis=1,
        )
        flux_divergence = (
            weight * amplitude**2 * mode * np.cos(2 * mode * x)
            * np.cos(mode * time) * np.sin(mode * time)
        )
        errors.append(float(np.sqrt(np.mean((energy_time_derivative + flux_divergence)**2))))
    orders = np.log2(np.array(errors[:-1]) / errors[1:])
    assert np.all((orders > 1.9) & (orders < 2.1)), (errors, orders)


@pytest.mark.parametrize("direction", [-1, 1])
@pytest.mark.parametrize("polarization", [1, 2])
def test_second_order_spatial_convergence_to_independent_continuum_wave(direction, polarization):
    errors = []
    for count in (32, 64, 128):
        dx = 2 * math.pi / count
        x = np.arange(count) * dx
        electric, magnetic = _traveling_fields(x, 0.0, 3, direction, polarization)
        state = MaxwellTestFieldState(electric, magnetic, dx)
        final = _integrate_maxwell(state, 0.73, 0.2 * dx)
        exact_e, exact_b = _traveling_fields(x, 0.73, 3, direction, polarization)
        errors.append(_field_error(final, exact_e, exact_b))
    orders = np.log2(np.array(errors[:-1]) / errors[1:])
    assert np.all((orders > 1.9) & (orders < 2.1)), (errors, orders)


@pytest.mark.parametrize("direction", [-1, 1])
@pytest.mark.parametrize("polarization", [1, 2])
def test_fourth_order_temporal_convergence_to_independent_semidiscrete_fourier_solution(direction, polarization):
    count = 32
    dx = 2 * math.pi / count
    x = np.arange(count) * dx
    mode = 3
    duration = 8 * dx
    # Applying a centered derivative to exp(i*k*x) gives i*sin(k*dx)/dx.
    frequency = math.sin(mode * dx) / dx
    exact_e, exact_b = _traveling_fields(x, duration, mode, direction, polarization, omega=frequency)
    electric, magnetic = _traveling_fields(x, 0.0, mode, direction, polarization)
    initial = MaxwellTestFieldState(electric, magnetic, dx)
    errors = []
    for divisor in (2, 4, 8, 16):
        final = _integrate_maxwell(initial, duration, dx / divisor)
        errors.append(_field_error(final, exact_e, exact_b))
    orders = np.log2(np.array(errors[:-1]) / errors[1:])
    assert np.all((orders > 3.9) & (orders < 4.1)), (errors, orders)


@pytest.mark.parametrize("value", [0.0, 0.3])
def test_vacuum_and_uniform_fields_are_exact_stationary_solutions(value):
    electric = np.full((16, 3), value)
    magnetic = np.full((16, 3), -2 * value)
    initial = MaxwellTestFieldState(electric, magnetic, 0.1)
    rhs_e, rhs_b = maxwell_test_field_rhs(initial)
    np.testing.assert_array_equal(rhs_e, 0.0)
    np.testing.assert_array_equal(rhs_b, 0.0)
    final = _integrate_maxwell(initial, 0.3, 0.05)
    np.testing.assert_array_equal(final.electric, initial.electric)
    np.testing.assert_array_equal(final.magnetic, initial.magnetic)
    assert final.time == pytest.approx(0.3)
    assert maxwell_test_field_diagnostics(final)["energy"] == maxwell_test_field_diagnostics(initial)["energy"]


def test_actual_gauss_violations_are_detected_and_preserved_not_projected():
    count = 64
    dx = 2 * math.pi / count
    x = np.arange(count) * dx
    electric, magnetic = _traveling_fields(x, 0.0, 2, 1, 1)
    electric[:, 0] = 0.2 * np.sin(3 * x)
    magnetic[:, 0] = 0.4 * np.cos(2 * x)
    initial = MaxwellTestFieldState(electric, magnetic, dx)
    before = maxwell_test_field_diagnostics(initial)
    np.testing.assert_allclose(before["electric_divergence"], 0.2 * math.sin(3 * dx) / dx * np.cos(3 * x), atol=2e-15)
    np.testing.assert_allclose(before["magnetic_divergence"], -0.4 * math.sin(2 * dx) / dx * np.sin(2 * x), atol=3e-15)
    assert before["electric_gauss_rms"] > 0.4
    assert before["magnetic_gauss_rms"] > 0.5
    final = _integrate_maxwell(initial, 0.7, 0.5 * dx)
    after = maxwell_test_field_diagnostics(final)
    np.testing.assert_array_equal(final.electric[:, 0], initial.electric[:, 0])
    np.testing.assert_array_equal(final.magnetic[:, 0], initial.magnetic[:, 0])
    np.testing.assert_array_equal(after["electric_divergence"], before["electric_divergence"])
    np.testing.assert_array_equal(after["magnetic_divergence"], before["magnetic_divergence"])


def test_centered_constraints_explicitly_have_a_nyquist_resolution_limit():
    electric = np.zeros((16, 3))
    electric[:, 0] = (-1.0)**np.arange(16)
    state = MaxwellTestFieldState(electric, np.zeros_like(electric), 0.1)
    assert maxwell_test_field_diagnostics(state)["electric_gauss_rms"] == 0.0
    assert any("Nyquist" in note for note in maxwell_test_field_surface()["limitations"])


@pytest.mark.parametrize("field_name", ["electric", "magnetic"])
def test_diagnostics_reject_overflowing_squares_of_finite_fields(field_name):
    fields = {"electric": np.zeros((16, 3)), "magnetic": np.zeros((16, 3))}
    fields[field_name][:, 1] = 1e200
    state = MaxwellTestFieldState(**fields, dx=0.1)
    assert np.all(np.isfinite(getattr(state, field_name)))
    with pytest.raises(ValueError, match="finite representable"):
        maxwell_test_field_diagnostics(state)


@pytest.mark.parametrize(
    "amplitude,lam,dx",
    [(1e100, 1e100, 0.1), (1e154, 1.0, 1.0), (1.0, 1.0, 1e-308)],
)
def test_diagnostics_reject_overflowing_weighted_products_totals_or_constraint_norms(amplitude, lam, dx):
    electric = np.zeros((16, 3))
    electric[:, 0] = amplitude * np.cos(2 * math.pi * np.arange(16) / 16)
    state = MaxwellTestFieldState(electric, np.zeros_like(electric), dx, lam=lam)
    assert math.isfinite(state.gauge_weight)
    with pytest.raises(ValueError, match="finite representable"):
        maxwell_test_field_diagnostics(state)


def test_semidiscrete_energy_derivative_vanishes_by_periodic_summation_by_parts():
    rng = np.random.default_rng(18)
    electric = rng.normal(size=(41, 3))
    magnetic = rng.normal(size=(41, 3))
    state = MaxwellTestFieldState(electric, magnetic, 0.2, phi0=1.7, lam=-0.4)
    electric_rhs, magnetic_rhs = maxwell_test_field_rhs(state)
    derivative = state.gauge_weight * state.dx * np.sum(
        state.electric * electric_rhs + state.magnetic * magnetic_rhs,
    )
    assert abs(derivative) < 1e-13


@pytest.mark.parametrize("direction", [-1, 1])
@pytest.mark.parametrize("polarization", [1, 2])
def test_plane_wave_energy_and_flux_have_independent_action_normalization(direction, polarization):
    count = 64
    dx = 2 * math.pi / count
    x = np.arange(count) * dx
    amplitude = 0.3
    electric, magnetic = _traveling_fields(x, 0.0, 2, direction, polarization, amplitude)
    initial = MaxwellTestFieldState(electric, magnetic, dx, phi0=1.3, lam=0.7)
    weight = 0.7**2 * 1.3**3
    diagnostics = maxwell_test_field_diagnostics(initial)
    density = weight * amplitude**2 * np.cos(2 * x + 0.23)**2
    np.testing.assert_allclose(diagnostics["energy_density"], density, atol=1e-16)
    np.testing.assert_allclose(diagnostics["poynting_flux"][:, 0], direction * density, atol=1e-16)
    expected_energy = weight * amplitude**2 * (2 * math.pi) / 2
    assert diagnostics["energy"] == pytest.approx(expected_energy, rel=1e-14)
    final = _integrate_maxwell(initial, 10.0, 0.2 * dx)
    assert maxwell_test_field_diagnostics(final)["energy"] == pytest.approx(expected_energy, rel=1e-7)


def test_energy_drift_decreases_with_time_refinement_instead_of_being_projected_away():
    dx = 2 * math.pi / 32
    x = np.arange(32) * dx
    electric, magnetic = _traveling_fields(x, 0.0, 3, 1, 1)
    initial = MaxwellTestFieldState(electric, magnetic, dx)
    energy0 = maxwell_test_field_diagnostics(initial)["energy"]
    drifts = []
    for divisor in (2, 4, 8):
        final = _integrate_maxwell(initial, 8 * dx, dx / divisor)
        energy = maxwell_test_field_diagnostics(final)["energy"]
        drifts.append((energy0 - energy) / energy0)
    assert all(drift > 0.0 for drift in drifts)
    assert drifts[0] < 2e-4
    assert drifts[0] / drifts[1] > 25
    assert drifts[1] / drifts[2] > 25


def test_constant_gauge_weight_changes_energy_not_vacuum_dynamics():
    x = np.arange(32) * 0.1
    electric, magnetic = _traveling_fields(x, 0.0, 2, 1, 2)
    first = MaxwellTestFieldState(electric, magnetic, 0.1, phi0=1.0, lam=1.0)
    second = MaxwellTestFieldState(electric, magnetic, 0.1, phi0=2.0, lam=-0.5)
    first_final = step_maxwell_test_field(first, 0.05)
    second_final = step_maxwell_test_field(second, 0.05)
    np.testing.assert_array_equal(first_final.electric, second_final.electric)
    np.testing.assert_array_equal(first_final.magnetic, second_final.magnetic)
    assert second.gauge_weight == 2.0
    assert maxwell_test_field_diagnostics(second)["energy"] == pytest.approx(
        2 * maxwell_test_field_diagnostics(first)["energy"],
    )


def test_hyperbolic_cfl_scales_linearly_with_dx_and_not_with_gauge_weight():
    fields = np.zeros((16, 3))
    first = MaxwellTestFieldState(fields, fields, 0.1)
    second = MaxwellTestFieldState(fields, fields, 0.05, phi0=2.0, lam=0.5)
    assert maxwell_test_field_cfl_timestep(first) == pytest.approx(0.05)
    assert maxwell_test_field_cfl_timestep(second) == pytest.approx(0.025)
    step_maxwell_test_field(first, first.dx)


@pytest.mark.parametrize("dt", [0.0, -0.1, float("nan"), float("inf"), 0.101])
def test_invalid_or_super_cfl_timestep_is_rejected(dt):
    fields = np.zeros((16, 3))
    with pytest.raises(ValueError):
        step_maxwell_test_field(MaxwellTestFieldState(fields, fields, 0.1), dt)


@pytest.mark.parametrize("cfl", [0.0, -0.1, float("nan"), float("inf"), 1.001])
def test_invalid_cfl_is_rejected(cfl):
    fields = np.zeros((16, 3))
    with pytest.raises(ValueError):
        maxwell_test_field_cfl_timestep(MaxwellTestFieldState(fields, fields, 0.1), cfl)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"dx": 0.0}, {"dx": -1.0}, {"dx": float("nan")},
        {"phi0": 0.0}, {"phi0": -1.0}, {"phi0": float("inf")},
        {"lam": 0.0}, {"lam": float("nan")}, {"lam": float("inf")},
        {"time": float("nan")}, {"time": float("inf")}, {"time": 1j},
        {"lam": 1e200}, {"phi0": 1e200}, {"lam": 1e-200}, {"phi0": 1e-200},
    ],
)
def test_prescribed_background_requires_finite_positive_action_weight(kwargs):
    fields = np.zeros((16, 3))
    arguments = {"dx": 0.1, **kwargs}
    with pytest.raises(ValueError):
        MaxwellTestFieldState(fields, fields, **arguments)


@pytest.mark.parametrize(
    "electric,magnetic",
    [
        (np.zeros(16), np.zeros((16, 3))),
        (np.zeros((2, 3)), np.zeros((2, 3))),
        (np.zeros((16, 4)), np.zeros((16, 3))),
        (np.zeros((16, 3)), np.zeros((17, 3))),
        (np.full((16, 3), np.nan), np.zeros((16, 3))),
        (np.zeros((16, 3)), np.full((16, 3), np.inf)),
        (np.full((16, 3), 1j), np.zeros((16, 3))),
    ],
)
def test_invalid_field_initial_data_is_rejected(electric, magnetic):
    with pytest.raises(ValueError):
        MaxwellTestFieldState(electric, magnetic, 0.1)


def test_initial_data_and_previous_state_are_not_modified_or_aliased():
    dx = 2 * math.pi / 16
    electric, magnetic = _traveling_fields(np.arange(16) * dx, 0.0, 1, 1, 1)
    expected_e, expected_b = electric.copy(), magnetic.copy()
    initial = MaxwellTestFieldState(electric, magnetic, dx, time=1.5)
    electric[:] = 99
    magnetic[:] = 99
    final = step_maxwell_test_field(initial, 0.1)
    np.testing.assert_array_equal(initial.electric, expected_e)
    np.testing.assert_array_equal(initial.magnetic, expected_b)
    assert not np.shares_memory(initial.electric, final.electric)
    assert not np.shares_memory(initial.magnetic, final.magnetic)
    assert final.time == pytest.approx(1.6)
    assert initial.time == 1.5
    with pytest.raises(ValueError):
        initial.electric[0, 0] = 1.0
