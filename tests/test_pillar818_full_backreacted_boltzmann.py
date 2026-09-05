# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Dimensional audit and no-fabricated-spectrum contract for 5D dynamics."""
import json
import math

import numpy as np
import pytest

from src.core import pillar818_full_backreacted_boltzmann as boltzmann


def test_mass_conversion_is_not_a_massless_cmb_field():
    audit = boltzmann.radion_mass_audit()
    mass_gev = math.exp(-37) * 2.435e18
    mass_mpc_inv = mass_gev / 1.973269804e-16 * 3.085677581491367e22
    assert 200 < audit["mass_gev"] < 220
    assert audit["mass_gev"] == pytest.approx(mass_gev)
    assert audit["mass_mpc_inv"] == pytest.approx(mass_mpc_inv)
    assert audit["conformal_mass_squared_mpc_inv2"] == pytest.approx(
        (mass_mpc_inv / 1090) ** 2,
    )
    assert audit["conformal_mass_to_k"] == pytest.approx(mass_mpc_inv / 1090 / 0.05)
    assert audit["conformal_mass_to_k"] > 1e38
    assert audit["mass_dominates_supplied_mode"]
    assert audit["backreaction_prediction"] is None
    assert "assumption" in audit
    json.dumps(audit, allow_nan=False)


@pytest.mark.parametrize("k", [1e-4, 0.001, 0.05, 0.5])
@pytest.mark.parametrize("a", [1 / 1090, 0.01, 1.0])
def test_conformal_mass_has_scale_factor_squared(k, a):
    audit = boltzmann.radion_mass_audit(k, a)
    assert audit["conformal_mass_squared_mpc_inv2"] == pytest.approx(
        a**2 * boltzmann.M_PHI_MPC_INV**2,
    )
    assert audit["conformal_mass_to_k"] == pytest.approx(a * boltzmann.M_PHI_MPC_INV / k)
    assert audit["mass_dominates_supplied_mode"]


def test_mass_comparison_uses_requested_scale_not_a_hardcoded_boolean():
    audit = boltzmann.radion_mass_audit(k_mpc_inv=1e50)
    assert not audit["mass_dominates_supplied_mode"]
    assert audit["backreaction_prediction"] is None


@pytest.mark.parametrize("kwargs", [
    {"k_mpc_inv": 0}, {"k_mpc_inv": -1}, {"k_mpc_inv": np.inf},
    {"k_mpc_inv": np.nan}, {"scale_factor": 0}, {"scale_factor": -1},
    {"scale_factor": 1.1}, {"scale_factor": np.nan}, {"scale_factor": np.inf},
])
def test_invalid_mass_audit_inputs(kwargs):
    with pytest.raises(ValueError):
        boltzmann.radion_mass_audit(**kwargs)


def test_unrepresentable_mass_ratio_fails_explicitly():
    with pytest.raises(ValueError, match="numeric range"):
        boltzmann.radion_mass_audit(k_mpc_inv=1e-320)


@pytest.mark.parametrize("kwargs", [{}, {"n_k": 1, "n_eta": 1, "n_ell": 1, "max_iter": 1},
                                    {"n_k": 100, "n_eta": 500, "tol": 1e-12}])
def test_no_resolution_or_tolerance_can_close_absent_equations(kwargs):
    result = boltzmann.run_full_backreacted_boltzmann(**kwargs)
    assert isinstance(result, boltzmann.BackreactedBoltzmannResult)
    assert result.gate == "FULL_5D_BOLTZMANN_UNSUPPORTED"
    assert not boltzmann.FULL_5D_BOLTZMANN_CLOSED
    assert not result.converged
    assert result.a_br_median is None
    assert result.a_br_max is None
    assert result.delta_cl_median is None
    assert result.n_modes == 0
    assert result.n_iter_max == 0
    assert result.mode_results == []
    assert set(result.open_items) == set(boltzmann.OPEN_ITEMS)
    assert boltzmann.A_BR_CANONICAL is None
    assert boltzmann.DELTA_CL_CANONICAL is None
    json.dumps(result._asdict(), allow_nan=False)


def test_returned_open_items_do_not_mutate_module_registry():
    result = boltzmann.run_full_backreacted_boltzmann()
    result.open_items.clear()
    assert boltzmann.run_full_backreacted_boltzmann().open_items


@pytest.mark.parametrize("field", ["n_k", "n_eta", "n_ell", "max_iter"])
@pytest.mark.parametrize("value", [0, -1, 2.5, True])
def test_invalid_solver_grid_requests(field, value):
    with pytest.raises(ValueError, match="positive integers"):
        boltzmann.run_full_backreacted_boltzmann(**{field: value})


@pytest.mark.parametrize("tol", [0, -1, np.inf, np.nan])
def test_invalid_tolerance(tol):
    with pytest.raises(ValueError, match="Tolerance"):
        boltzmann.run_full_backreacted_boltzmann(tol=tol)


@pytest.mark.parametrize("name", [
    "radion_source_term", "solve_radion_mode", "boltzmann_br_mode",
    "boltzmann_gr_mode", "backreaction_amplitude", "run_backreaction_loop",
    "compute_transfer_functions", "compute_cl_tt",
])
def test_mixed_unit_solver_cannot_be_called_through_legacy_api(name):
    with pytest.raises(NotImplementedError, match="normalized action"):
        getattr(boltzmann, name)()


def test_residual_uses_actual_control_power_without_normalization_floor():
    reference = np.array([2, 4, 10, 1e-100])
    candidate = np.array([3, 2, 0, 2e-100])
    np.testing.assert_allclose(
        boltzmann.delta_cl_from_backreaction(reference, candidate), [0.5, 0.5, 1, 1],
    )
    np.testing.assert_array_equal(
        boltzmann.delta_cl_from_backreaction(reference, reference), np.zeros(4),
    )
    np.testing.assert_array_equal(reference, [2, 4, 10, 1e-100])


@pytest.mark.parametrize("reference,candidate", [
    ([0, 1], [0, 1]), ([1, 0], [1, 2]), ([-1, 1], [1, 1]),
    ([1, 1], [-1, 1]), ([np.nan], [1]), ([1], [np.inf]), ([], []),
    ([[1, 2]], [[1, 2]]), ([1, 2], [1]), ([1], [[1]]),
])
def test_missing_support_and_invalid_controls_are_not_zero_residuals(reference, candidate):
    with pytest.raises(ValueError, match="positive reference"):
        boltzmann.delta_cl_from_backreaction(reference, candidate)


def test_unrepresentable_relative_residual_fails_explicitly():
    with pytest.raises(ValueError, match="numeric range"):
        boltzmann.delta_cl_from_backreaction([1e-320], [1e300])


def test_open_items_identify_missing_derivations_and_projection():
    items = "\n".join(boltzmann.OPEN_ITEMS)
    for required in ["NORMALIZED_ACTION", "BACKGROUND", "SOURCE", "HIERARCHY",
                     "MASS_AUDIT", "PROJECTION_RETRACTED", "NO_ZERO_FILL"]:
        assert required in items
