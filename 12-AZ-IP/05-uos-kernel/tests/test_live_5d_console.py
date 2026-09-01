# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from uos_kernel.engine import live_5d_console as console


def test_constants_match_requested_values():
    assert console.WINDING_NUMBER == 5
    assert console.K_CS == 74
    assert console.PHI_0 == 1.0
    assert console.N_S == pytest.approx(0.9635)
    assert console.R_BRAIDED == pytest.approx(0.0315)


def test_compute_5d_state_defaults():
    state = console.compute_5d_state()
    assert state['winding'] == 5
    assert state['phi_0'] == 1.0


def test_compute_5d_state_positive_outputs():
    state = console.compute_5d_state(5)
    assert state['metric_curvature'] > 0
    assert state['kk_mass'] > 0
    assert state['braided_speed'] > 0


def test_compute_5d_state_scales_with_winding():
    low = console.compute_5d_state(3)
    high = console.compute_5d_state(7)
    assert high['metric_curvature'] > low['metric_curvature']
    assert high['braided_speed'] > low['braided_speed']


def test_compute_5d_state_rejects_nonpositive_winding():
    with pytest.raises(ValueError):
        console.compute_5d_state(0)


def test_get_axiom_registry_returns_entries():
    registry = console.get_axiom_registry()
    assert len(registry) >= 22
    assert {'name', 'label', 'status', 'lean4_ref', 'pillars'} <= set(registry[0])


def test_get_axiom_registry_prefers_compactification_file():
    registry = console.get_axiom_registry()
    assert any(item['name'] == 'A0_MANIFOLD' for item in registry)


def test_parameter_sensitivity_winding():
    result = console.parameter_sensitivity('winding', 1.0)
    assert result['perturbed']['winding'] == 6
    assert result['downstream_changes']['metric_curvature'] > 0


def test_parameter_sensitivity_kcs():
    result = console.parameter_sensitivity('k_cs', 10.0)
    assert result['perturbed']['kk_mass'] < result['baseline']['kk_mass']


def test_parameter_sensitivity_speed():
    result = console.parameter_sensitivity('braided_sound_speed', 0.1)
    assert result['perturbed']['braided_speed'] > result['baseline']['braided_speed']


def test_parameter_sensitivity_phi0():
    result = console.parameter_sensitivity('phi_0', 0.25)
    assert result['perturbed']['phi_0'] == pytest.approx(1.25)


def test_parameter_sensitivity_ns():
    result = console.parameter_sensitivity('n_s', -0.01)
    assert result['perturbed']['n_s'] == pytest.approx(0.9535)


def test_parameter_sensitivity_r_braided():
    result = console.parameter_sensitivity('r_braided', 0.002)
    assert result['perturbed']['r_braided'] == pytest.approx(0.0335)


def test_parameter_sensitivity_unknown_rejected():
    with pytest.raises(KeyError):
        console.parameter_sensitivity('mystery', 1.0)


def test_parameter_sensitivity_invalid_kcs_rejected():
    with pytest.raises(ValueError):
        console.parameter_sensitivity('k_cs', -1000.0)


def test_parameter_sensitivity_invalid_speed_rejected():
    with pytest.raises(ValueError):
        console.parameter_sensitivity('braided_sound_speed', -10.0)
