# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Control spectra, numerical sensitivity and explicit unsupported UM physics."""
from dataclasses import asdict, replace
import json
import runpy
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from src.core import pillar814_zph_camb_bridge as bridge


ELL = [200, 540, 1000]


@pytest.fixture
def fake_camb(monkeypatch):
    """Deterministic solver double for accounting tests, not physical evidence."""
    calls = []

    def run(ell, cosmology, primordial, accuracy, margin):
        calls.append((ell.copy(), cosmology, primordial, accuracy, margin))
        return (10 * np.arange(1, len(ell) + 1) + accuracy - 1) * (
            primordial.As / bridge.A_S_PLANCK
        )

    monkeypatch.setattr(bridge, "CAMB_AVAILABLE", True)
    monkeypatch.setattr(bridge, "_run_camb_cl_tt", run)
    monkeypatch.setitem(sys.modules, "camb", SimpleNamespace(__version__="test-double"))
    return calls


def test_missing_derivations_are_not_numerical_constants():
    assert bridge.A_S_UM is None
    assert bridge.Z_PHI is None
    assert bridge.PLANCK_2018_ELL == bridge.DEFAULT_ELL


@pytest.mark.parametrize("name", [
    "compute_z_phi", "breathing_mode_damping", "compute_damping_filter",
    "um_transfer_correction", "toy_cl_tt_um", "planck_reference_cl",
])
def test_unsupported_historical_corrections_fail_explicitly(name):
    with pytest.raises(NotImplementedError, match="derivation"):
        getattr(bridge, name)()


def test_toy_identity_is_not_a_sky_prediction_or_closure():
    primordial = bridge.PrimordialSpectrum()
    result = bridge.compare_cmb_spectra(
        ELL, reference=primordial, candidate=primordial, backend="toy",
    )
    np.testing.assert_array_equal(result.candidate_dl, result.reference_dl)
    np.testing.assert_array_equal(result.residual_dl, np.zeros(3))
    assert not result.camb_used
    assert not result.closure_earned
    assert result.gate == bridge.PILLAR_GATE
    assert bridge.evaluate_closure_gate(result, threshold=1) == bridge.PILLAR_GATE
    assert result.reference_numerical_error is None
    assert result.candidate_numerical_error is None
    assert result.residual_numerical_error is None
    assert result.observed_residual_dl is None
    assert result.chi_square is None
    assert result.metadata["units"] == "arbitrary"
    assert result.metadata["convention"] is None
    assert "no physical transfer" in result.metadata["transfer_physics"]
    assert result.metadata["corrections_applied"] == []
    assert "not empirical Planck" in result.metadata["reference_kind"]
    assert json.loads(json.dumps(result.to_dict(), allow_nan=False))["ell"] == ELL


def test_toy_primordial_sensitivity_without_peak_matching():
    primordial = bridge.PrimordialSpectrum()
    candidate = replace(primordial, As=1.5 * primordial.As, ns=primordial.ns + 0.1)
    result = bridge.compare_cmb_spectra(
        ELL, reference=primordial, candidate=candidate, backend="toy",
    )
    expected_ratio = 1.5 * (np.array(ELL) / 700.0) ** 0.1
    np.testing.assert_allclose(result.candidate_dl / result.reference_dl, expected_ratio)
    np.testing.assert_allclose(result.relative_residual, expected_ratio - 1)


def test_toy_cannot_model_tensors():
    with pytest.raises(NotImplementedError, match="tensor"):
        bridge.compare_cmb_spectra(
            ELL, backend="toy", candidate=bridge.PrimordialSpectrum(r=0.03),
        )


def test_backend_selection_without_camb(monkeypatch):
    monkeypatch.setattr(bridge, "CAMB_AVAILABLE", False)
    with pytest.raises(ImportError, match="CAMB"):
        bridge.compare_cmb_spectra(ELL, backend="camb")
    automatic = bridge.run_zph_camb_bridge(ELL, use_camb=True)
    assert automatic.metadata["backend"] == "toy"
    assert automatic.metadata["fallback_reason"] == "CAMB unavailable"
    explicit = bridge.run_zph_camb_bridge(ELL, use_camb=False)
    assert explicit.metadata["fallback_reason"] is None


@pytest.mark.parametrize("backend", ["auto", "toy"])
def test_command_line_without_camb_reports_labeled_toy(monkeypatch, capsys, backend):
    find_spec = bridge.importlib.util.find_spec
    monkeypatch.setattr(
        bridge.importlib.util, "find_spec",
        lambda name, *args, **kwargs: None if name == "camb" else find_spec(name, *args, **kwargs),
    )
    argv = [bridge.__file__] + ([] if backend == "auto" else ["--backend", backend])
    monkeypatch.setattr(sys, "argv", argv)
    runpy.run_path(bridge.__file__, run_name="__main__")
    result = json.loads(capsys.readouterr().out)
    assert result["metadata"]["backend"] == "toy"
    assert result["metadata"]["backend_requested"] == backend
    assert result["metadata"]["units"] == "arbitrary"
    assert result["closure_earned"] is False
    assert result["metadata"]["fallback_reason"] == (
        "CAMB unavailable" if backend == "auto" else None
    )


def test_command_line_explicit_camb_does_not_fall_back(monkeypatch):
    find_spec = bridge.importlib.util.find_spec
    monkeypatch.setattr(
        bridge.importlib.util, "find_spec",
        lambda name, *args, **kwargs: None if name == "camb" else find_spec(name, *args, **kwargs),
    )
    monkeypatch.setattr(sys, "argv", [bridge.__file__, "--backend", "camb"])
    with pytest.raises(ImportError, match="CAMB"):
        runpy.run_path(bridge.__file__, run_name="__main__")


def test_auto_uses_camb_when_available(fake_camb):
    result = bridge.compare_cmb_spectra(ELL)
    assert result.camb_used
    assert len(fake_camb) == 4
    assert result.metadata["fallback_reason"] is None


def test_solver_failure_is_not_silently_replaced_with_toy(fake_camb, monkeypatch):
    def fail(*args):
        raise RuntimeError("solver failed")

    monkeypatch.setattr(bridge, "_run_camb_cl_tt", fail)
    with pytest.raises(RuntimeError, match="solver failed"):
        bridge.compare_cmb_spectra(ELL, backend="auto")


def test_independent_runs_and_numerical_sensitivity(fake_camb):
    primordial = bridge.PrimordialSpectrum()
    candidate = replace(primordial, As=1.5 * primordial.As)
    cosmology = bridge.Cosmology(H0=70.0)
    result = bridge.compare_cmb_spectra(
        ELL, reference=primordial, candidate=candidate, cosmology=cosmology,
        backend="camb",
    )
    assert [c[2] for c in fake_camb] == [primordial, primordial, candidate, candidate]
    assert [c[3:] for c in fake_camb] == [(1.0, 150), (2.0, 300)] * 2
    assert all(c[1] == cosmology for c in fake_camb)
    np.testing.assert_array_equal(result.reference_dl, [11, 21, 31])
    np.testing.assert_array_equal(result.candidate_dl, [16.5, 31.5, 46.5])
    np.testing.assert_array_equal(result.reference_numerical_error, [1, 1, 1])
    np.testing.assert_array_equal(result.candidate_numerical_error, [1.5, 1.5, 1.5])
    np.testing.assert_array_equal(result.residual_numerical_error, [2.5, 2.5, 2.5])
    np.testing.assert_allclose(result.relative_residual, 0.5)
    assert not result.closure_earned
    assert result.metadata["camb_version"] == "test-double"
    assert result.metadata["cosmology"] == asdict(cosmology)
    assert result.metadata["candidate_primordial"] == asdict(candidate)
    assert "not a bound" in result.metadata["numerical_error_kind"]
    assert "not quantified" in result.metadata["model_error"]
    assert result.metadata["units"] == "microK^2"


@pytest.mark.parametrize("invalid", [[0, 1, 2], [-1, 2, 3], [np.nan, 2, 3],
                                     [np.inf, 2, 3], [1], [[1, 2, 3]]])
@pytest.mark.parametrize("bad_run", [0, 1, 2, 3])
def test_every_solver_run_requires_finite_positive_full_support(fake_camb, monkeypatch,
                                                               invalid, bad_run):
    good = bridge._run_camb_cl_tt
    count = 0

    def run(*args):
        nonlocal count
        index = count
        count += 1
        return np.array(invalid) if index == bad_run else good(*args)

    monkeypatch.setattr(bridge, "_run_camb_cl_tt", run)
    with pytest.raises(RuntimeError, match="invalid TT"):
        bridge.compare_cmb_spectra(ELL, backend="camb")


def test_supplied_covariance_quadratic_form_not_control_residual(fake_camb):
    observed = np.array([10, 23, 28])
    cov = np.array([[4, 1, 0], [1, 9, 0], [0, 0, 16]])
    result = bridge.compare_cmb_spectra(
        ELL, backend="camb", observed_dl=observed, covariance=cov,
        observation_source="synthetic unit-test data, not Planck",
    )
    residual = np.array([1, -2, 3])
    np.testing.assert_array_equal(result.residual_dl, np.zeros(3))
    np.testing.assert_array_equal(result.observed_residual_dl, residual)
    np.testing.assert_array_equal(result.covariance, cov)
    assert result.chi_square == pytest.approx(residual @ np.linalg.solve(cov, residual))
    assert result.metadata["covariance_units"] == "microK^4"
    assert "not fitted/reduced" in result.metadata["chi_square_kind"]
    assert not result.closure_earned


def test_observations_without_covariance_do_not_invent_a_chi_square(fake_camb):
    result = bridge.compare_cmb_spectra(
        ELL, backend="camb", observed_dl=[11, 21, 31], observation_source="synthetic",
    )
    np.testing.assert_array_equal(result.observed_residual_dl, np.zeros(3))
    assert result.chi_square is None
    assert result.covariance is None
    assert not result.closure_earned


@pytest.mark.parametrize("kwargs", [
    {"observed_dl": [1, 2]},
    {"observed_dl": [1, 2, np.nan]},
    {"observed_dl": [1, 2, 3]},
    {"observed_dl": [1, 2, 3], "observation_source": " "},
    {"covariance": np.eye(3)},
    {"observed_dl": [1, 2, 3], "observation_source": "test", "covariance": np.eye(2)},
    {"observed_dl": [1, 2, 3], "observation_source": "test", "covariance": np.zeros((3, 3))},
    {"observed_dl": [1, 2, 3], "observation_source": "test",
     "covariance": [[1, 2, 0], [0, 1, 0], [0, 0, 1]]},
    {"observed_dl": [1, 2, 3], "observation_source": "test",
     "covariance": np.diag([1, -1, 1])},
    {"observed_dl": [1, 2, 3], "observation_source": "test",
     "covariance": np.diag([1, np.nan, 1])},
])
def test_invalid_observation_inputs_fail_before_solver(fake_camb, kwargs):
    with pytest.raises(ValueError):
        bridge.compare_cmb_spectra(ELL, backend="camb", **kwargs)
    assert fake_camb == []


def test_no_comparison_between_arbitrary_units_and_observations():
    with pytest.raises(ValueError, match="Arbitrary-unit"):
        bridge.compare_cmb_spectra(
            ELL, backend="toy", observed_dl=[1, 2, 3], observation_source="synthetic",
        )


def test_covariance_statistic_overflow_is_not_reported_as_valid(fake_camb):
    with pytest.raises(ValueError, match="numeric range"):
        bridge.compare_cmb_spectra(
            ELL, backend="camb", observed_dl=[1e300] * 3,
            covariance=np.eye(3), observation_source="synthetic",
        )


@pytest.mark.parametrize("ell", [
    [], [1, 2], [2, 2], [3, 2], [2.1, 3], [2, np.nan], [2, np.inf],
    [[2, 3]], ["2", "3"], [2 + 0j, 3 + 0j], [False, True],
    np.array([3, 2], dtype=np.uint64), [2, 2**63],
])
def test_invalid_multipoles(ell):
    with pytest.raises(ValueError, match="Multipoles"):
        bridge.compare_cmb_spectra(ell, backend="toy")


@pytest.mark.parametrize("kwargs", [
    {"backend": "unknown"}, {"accuracy_settings": (1, 1)},
    {"accuracy_settings": (0, 2)}, {"accuracy_settings": (1, np.inf)},
    {"accuracy_settings": (1,)}, {"lmax_margins": (300, 150)},
    {"lmax_margins": (-1, 100)}, {"lmax_margins": (150.0, 300)},
    {"lmax_margins": (150,)}, {"lmax_margins": (False, True)},
])
def test_invalid_backend_or_convergence_controls(kwargs):
    with pytest.raises(ValueError):
        bridge.compare_cmb_spectra(ELL, **kwargs)


@pytest.mark.parametrize("kwargs", [
    {"As": 0}, {"As": -1e-9}, {"r": -1}, {"ns": np.nan}, {"nt": np.inf},
    {"pivot_scalar": 0}, {"pivot_tensor": -1},
])
def test_invalid_primordial_inputs(kwargs):
    with pytest.raises(ValueError):
        bridge.PrimordialSpectrum(**kwargs)


@pytest.mark.parametrize("kwargs", [
    {"H0": 0}, {"ombh2": 0}, {"omch2": -1}, {"tau": -1}, {"mnu": -1},
    {"TCMB": 0}, {"nnu": 0}, {"YHe": 0}, {"YHe": 1}, {"omk": np.nan},
])
def test_invalid_cosmology(kwargs):
    with pytest.raises(ValueError):
        bridge.Cosmology(**kwargs)


@pytest.fixture(scope="module")
def real_camb_controls():
    pytest.importorskip("camb")
    primordial = bridge.PrimordialSpectrum()
    variants = {
        "identity": primordial,
        "amplitude": replace(primordial, As=1.2 * primordial.As),
        "tilt": replace(primordial, ns=bridge.N_S),
        "tensor": replace(primordial, r=bridge.R_BRAIDED),
    }
    ell = [2, 30, 200, 540, 1000, 1600, 2000]
    return {
        name: bridge.compare_cmb_spectra(
            ell, reference=primordial, candidate=candidate, backend="camb",
        )
        for name, candidate in variants.items()
    }


@pytest.mark.slow
def test_real_camb_identity_control_and_error_budget(real_camb_controls):
    result = real_camb_controls["identity"]
    assert result.camb_used
    np.testing.assert_array_equal(result.reference_dl, result.candidate_dl)
    np.testing.assert_array_equal(result.residual_dl, np.zeros(len(result.ell)))
    assert result.reference_dl[2] > 4000  # Unlensed acoustic TT, microK^2, not C_ell.
    assert result.reference_dl[-1] > 0
    assert np.all(np.isfinite(result.reference_numerical_error))
    assert np.any(result.reference_numerical_error > 0)
    np.testing.assert_allclose(
        result.residual_numerical_error,
        result.reference_numerical_error + result.candidate_numerical_error,
    )
    assert np.max(result.reference_numerical_error / result.reference_dl) < 0.02
    assert result.chi_square is None
    assert not result.closure_earned


@pytest.mark.slow
def test_real_camb_scalar_amplitude_scales_power_without_hidden_normalization(real_camb_controls):
    result = real_camb_controls["amplitude"]
    np.testing.assert_allclose(result.candidate_dl / result.reference_dl, 1.2, rtol=2e-5)
    np.testing.assert_allclose(result.relative_residual, 0.2, rtol=2e-4)


@pytest.mark.slow
def test_real_camb_tilt_change_is_independent_and_scale_dependent(real_camb_controls):
    result = real_camb_controls["tilt"]
    assert not np.allclose(result.reference_dl, result.candidate_dl, rtol=1e-5)
    assert np.ptp(result.relative_residual) > 0.001
    assert result.relative_residual[0] > 0
    assert result.relative_residual[-1] < 0
    assert result.metadata["corrections_applied"] == []
    assert not result.closure_earned


@pytest.mark.slow
def test_real_camb_tensor_transfer_changes_large_angle_tt(real_camb_controls):
    result = real_camb_controls["tensor"]
    assert result.relative_residual[0] > 0.001
    assert abs(result.relative_residual[-1]) < result.relative_residual[0] / 100
    assert result.metadata["candidate_primordial"]["r"] == bridge.R_BRAIDED
    assert not result.closure_earned


@pytest.mark.slow
def test_real_camb_units_against_independent_raw_cl():
    camb = pytest.importorskip("camb")
    ell = np.array(ELL)
    cosmology, primordial = bridge.Cosmology(), bridge.PrimordialSpectrum()
    pars = camb.CAMBparams()
    pars.set_cosmology(**asdict(cosmology), num_massive_neutrinos=1)
    pars.InitPower.set_params(**asdict(primordial))
    pars.DoLensing = False
    pars.NonLinear = camb.model.NonLinear_none
    pars.set_accuracy(AccuracyBoost=1, lAccuracyBoost=1, lSampleBoost=1)
    pars.set_for_lmax(1150, lens_potential_accuracy=0)
    raw = camb.get_results(pars).get_cmb_power_spectra(CMB_unit="muK", raw_cl=True)
    expected = raw["unlensed_total"][ell, 0] * ell * (ell + 1) / (2 * np.pi)
    actual = bridge._run_camb_cl_tt(ell, cosmology, primordial, 1, 150)
    np.testing.assert_allclose(actual, expected, rtol=1e-10)
