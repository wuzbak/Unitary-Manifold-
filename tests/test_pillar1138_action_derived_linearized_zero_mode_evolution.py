# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import importlib
from pathlib import Path

import pytest

sp = pytest.importorskip("sympy")

import src.core.pillar1138_action_derived_linearized_zero_mode_evolution as pillar
from src.core.pillar1138_action_derived_linearized_zero_mode_evolution import (
    DOES_NOT_ESTABLISH,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    action_derived_linearized_zero_mode_certificate,
)


def test_pillar_identity_and_scope():
    assert PILLAR_NUMBER == 1138
    assert PILLAR_GATE == "ACTION_DERIVED_LINEARIZED_ZERO_MODE_EVOLUTION"
    assert PILLAR_STATUS == "LINEARIZED_ZERO_MODE_RADION_GAUGE_EVOLUTION_CERTIFIED"
    assert VERSION == "v38.9"
    assert NEXT_PILLAR_SLOT == 1139
    assert "physical time" in pillar.SCOPE
    assert "relaxation-time law" in " ".join(DOES_NOT_ESTABLISH)


def test_linearized_euler_equations_and_gauss_constraint():
    residuals = pillar._linearized_euler_residuals()
    t, x = sp.symbols("t x", real=True)
    chi, ay, az = [sp.Function(name)(t, x) for name in ("chi", "ay", "az")]
    assert sp.simplify(residuals["radion_wave"] - (sp.diff(chi, t, 2) - sp.diff(chi, x, 2))) == 0
    assert sp.simplify(residuals["transverse_y_wave"] - (sp.diff(ay, t, 2) - sp.diff(ay, x, 2))) == 0
    assert sp.simplify(residuals["transverse_z_wave"] - (sp.diff(az, t, 2) - sp.diff(az, x, 2))) == 0
    assert sp.simplify(
        residuals["gauss_constraint"] - residuals["electric_field_spatial_derivative"]
    ) == 0
    assert sp.simplify(
        residuals["longitudinal_evolution"] - residuals["electric_field_time_derivative"]
    ) == 0


def test_certificate_is_verified_without_claiming_full_closure():
    packet = action_derived_linearized_zero_mode_certificate()
    assert packet["verified"] is True
    assert all(packet["checks"].values())
    assert packet["framework_closure_earned"] is False
    assert packet["status"] == PILLAR_STATUS
    assert "omega^2 = k^2" == packet["dispersion_relation"]
    assert any("nonlinear metric backreaction" in item for item in packet["does_not_establish"])


def test_flat_import_resolves_to_sharded_source():
    module = importlib.import_module("src.core.pillar1138_action_derived_linearized_zero_mode_evolution")
    assert Path(module.__file__).parent.name == "pillar_1129_1168"
    assert module.__name__ == "src.core.pillar1138_action_derived_linearized_zero_mode_evolution"


def test_certificate_fails_closed_when_equation_check_fails(monkeypatch):
    original = pillar._linearized_euler_residuals
    residuals = original()
    residuals["radion_wave"] += 1
    monkeypatch.setattr(pillar, "_linearized_euler_residuals", lambda: residuals)
    packet = pillar.action_derived_linearized_zero_mode_certificate()
    assert packet["verified"] is False
    assert packet["checks"]["radion_wave"] is False
    assert packet["status"] == "LINEARIZED_ZERO_MODE_RADION_GAUGE_NOT_VERIFIED"
    assert packet["framework_closure_earned"] is False


def test_quadratic_action_fails_closed_when_radion_kinetic_check_fails(monkeypatch):
    expansion = pillar._quadratic_action_expansion()
    expansion["radion_quadratic"] += 1
    monkeypatch.setattr(pillar, "_quadratic_action_expansion", lambda: expansion)

    packet = pillar.action_derived_linearized_zero_mode_certificate()

    assert packet["checks"]["radion_action_retains_canonical_quadratic_kinetic_term"] is False
    assert packet["quadratic_action_expansion"]["verified"] is False
    assert packet["verified"] is False
    assert packet["status"] == "LINEARIZED_ZERO_MODE_RADION_GAUGE_NOT_VERIFIED"
