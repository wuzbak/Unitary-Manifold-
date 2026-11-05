# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Cross-module scientific acceptance and receipt rejection tests."""

from copy import deepcopy

import numpy as np
import pytest

pytest.importorskip("sympy")

from TOOLS.checks.run_planar_radion_acceptance import (
    acceptance_gates,
    bessel_state,
    gauge_wave_state,
    run_acceptance,
)
from src.physics.planar_radion.geometry import evaluate_planar_ricci


@pytest.fixture(scope="module")
def acceptance_report():
    return run_acceptance()


@pytest.mark.slow
def test_complete_experiment_passes_every_declared_gate(acceptance_report):
    assert acceptance_report["passed"], acceptance_report["gates"]
    assert all(acceptance_report["gates"].values())
    assert len(acceptance_report["source_sha256"]) == 4
    for case in acceptance_report["bessel_cases"]:
        assert [row["n"] for row in case["rows"]] == [32, 64, 128, 256]


@pytest.mark.slow
@pytest.mark.parametrize(
    "mutation,gate",
    [
        ("order", "bessel_solution_second_order"),
        ("absolute", "finest_field_errors_below_tolerance"),
        ("nan", "finest_uplift_below_tolerance"),
        ("temporal", "fourth_order_time_differences"),
        ("control", "negative_controls_rejected"),
        ("matrix", "complete_experiment_matrix"),
        ("symbolic", "symbolic_identities_verified"),
    ],
)
def test_acceptance_rejects_bad_evidence(acceptance_report, mutation, gate):
    report = deepcopy(acceptance_report)
    if mutation == "order":
        report["bessel_cases"][0]["field_orders"][-1] = 0.1
    elif mutation == "absolute":
        report["bessel_cases"][0]["rows"][-1]["six_field_rms_error"] = 0.1
    elif mutation == "nan":
        report["bessel_cases"][0]["rows"][-1][
            "maximum_orthonormal_5d_ricci_in_interior_window"
        ] = float("nan")
    elif mutation == "temporal":
        report["temporal_refinement"]["observed_order"] = 1.0
    elif mutation == "control":
        report["negative_controls"]["wrong_frame_uplift_detected"] = False
    elif mutation == "matrix":
        report["bessel_cases"].pop()
    else:
        report["symbolic_checks"]["all_zero"] = False
    assert not acceptance_gates(report)[gate]


def test_multimode_exact_reference_satisfies_independent_uplift():
    errors = []
    for n in (32, 64):
        x = np.arange(n) * 2 * np.pi / n
        times = np.linspace(1.0, 1.5, n + 1)
        states = [bessel_state(n, float(time), (0.04, 0.025)) for time in times]
        result = evaluate_planar_ricci(
            times, x,
            *(np.stack([getattr(state, name) for state in states])
              for name in ("r", "sigma", "psi")),
        )
        errors.append(np.max(result.frame_norm))
    assert errors[0] / errors[1] > 12
    assert errors[-1] < 2e-5


def test_coordinate_inhomogeneous_reference_has_spatial_area_and_vacuum_uplift():
    errors = []
    for n in (32, 64):
        x = np.arange(n) * 2 * np.pi / n
        times = np.linspace(1.0, 1.5, n + 1)
        states = [gauge_wave_state(n, float(time)) for time in times]
        assert np.ptp(states[0].r) > 0.01
        result = evaluate_planar_ricci(
            times, x,
            *(np.stack([getattr(state, name) for state in states])
              for name in ("r", "sigma", "psi")),
        )
        errors.append(np.max(result.frame_norm))
    assert errors[0] / errors[1] > 12
    assert errors[-1] < 5e-5


@pytest.mark.parametrize("n,time,amplitudes", [(4, 1, (0.1,)), (16, 0, (0.1,)), (16, 1, ())])
def test_unresolved_or_invalid_reference_is_rejected(n, time, amplitudes):
    with pytest.raises(ValueError):
        bessel_state(n, time, amplitudes)
