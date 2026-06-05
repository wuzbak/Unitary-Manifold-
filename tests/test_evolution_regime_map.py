# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Executable regime-map tests for evolution architecture and winding tracking."""

import numpy as np
import pytest

try:
    from src.core.evolution import (
        FieldState,
        run_evolution,
        braid_winding_number,
        initialize_dynamic_braid,
        information_current_topological,
        calculate_topological_distance,
    )
except ImportError as exc:
    pytest.skip(f"Required evolution API unavailable: {exc}", allow_module_level=True)

try:
    from src.core.pillar516_kk_backreaction_architecture_audit import regime_map
except ImportError as exc:
    pytest.skip(f"Pillar 516 regime map unavailable: {exc}", allow_module_level=True)


def _field_distance(reference: FieldState, other: FieldState) -> float:
    return float(np.max(np.abs(other.phi - reference.phi)))


def test_factory_ic_near_flat_is_by_design():
    state = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(1))
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    metric_deviation = float(np.abs(state.g - eta[None, :, :]).max())
    phi_deviation = float(np.abs(state.phi - 1.0).max())

    assert metric_deviation < 0.01
    assert phi_deviation < 0.01
    assert metric_deviation >= 1.0e-4 / 10.0


def test_solver_can_handle_large_deviation_amplitude():
    state = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    result = run_evolution(state, dt=1.0e-4, steps=10, check_cfl=False)
    final_state = result[-1]

    assert np.all(np.isfinite(final_state.g))
    assert np.all(np.isfinite(final_state.B))
    assert np.all(np.isfinite(final_state.phi))


def test_braid_winding_number_returns_finite_value_for_valid_field_state():
    state = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    winding = braid_winding_number(state.phi, state.dx)

    assert np.isfinite(float(winding))


def test_run_evolution_track_winding_returns_winding_history_key():
    state = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    result = run_evolution(state, dt=1.0e-4, steps=10, check_cfl=False, track_winding=True)

    assert "winding_history" in result


def test_winding_tracking_history_length():
    steps = 10
    state = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    result = run_evolution(state, dt=1.0e-4, steps=steps, check_cfl=False, track_winding=True)

    assert len(result["winding_history"]) == steps + 1


def test_information_current_topological_exceeds_phi_squared_when_nw_positive():
    state = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    current = information_current_topological(state)

    assert float(np.mean(current[:, 0])) > float(np.mean(state.phi**2))


def test_calculate_topological_distance_is_non_negative():
    s1 = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    s2 = FieldState.flat(N=64, dx=0.05, rng=np.random.default_rng(2))

    assert calculate_topological_distance(s1, s2) >= 0


def test_regime_map_documents_factory_ic_correctly():
    description = regime_map()["factory_ic"].lower()
    assert "1e-4" in description or "near-flat" in description
    assert "factory" in description


def test_regime_map_documents_solver_large_deviation_correctly():
    description = regime_map()["solver_large_deviation"].lower()
    assert "0.5" in description or "large" in description
    assert "solver" in description or "run_evolution" in description


def test_regime_map_documents_backreaction_decoupled_correctly():
    description = regime_map()["backreaction_decoupled"].lower()
    assert "n_kk_modes=0" in description
    assert "kk_backreaction_coupling=0.0" in description


def test_regime_map_documents_winding_tracking_live_correctly():
    description = regime_map()["winding_tracking_live"].lower()
    assert "winding_history" in description
    assert "track_winding=true" in description or "track_winding" in description


def test_run_evolution_forward_ten_steps_gives_increasing_field_distance():
    state = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    result = run_evolution(state, dt=1.0e-4, steps=10, check_cfl=False)
    distances = [_field_distance(state, other) for other in result]

    assert distances[-1] > distances[0]
    assert all(b >= a - 1.0e-12 for a, b in zip(distances, distances[1:]))


def test_topological_distance_does_not_grow_faster_than_field_distance():
    state = initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=0.5)
    result = run_evolution(state, dt=1.0e-4, steps=10, check_cfl=False)
    final_state = result[-1]
    field_distance = _field_distance(state, final_state)
    topo_distance = calculate_topological_distance(state, final_state)

    assert field_distance > 0.0
    assert topo_distance == 0


def test_braid_winding_number_sign_consistent_across_phi_amplitudes():
    windings = [
        braid_winding_number(
            initialize_dynamic_braid(N=128, n_w_initial=1, dx=0.05, amplitude=amp).phi,
            0.05,
        )
        for amp in (0.2, 0.5, 0.8)
    ]
    signs = {int(np.sign(w)) for w in windings}

    assert signs == {1}


def test_factory_ic_at_amplitude_1e_minus_4_starts_within_1e_minus_3_of_zero_winding():
    state = FieldState.flat(N=64, dx=0.1, rng=np.random.default_rng(3))
    winding = braid_winding_number(state.phi, state.dx)

    assert abs(float(winding)) <= 1.0e-3
