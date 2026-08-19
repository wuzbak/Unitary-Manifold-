# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 689 — CKM triangle FN geometry."""
from __future__ import annotations

import pytest

from src.core.pillar689_ckm_triangle_fn_geometry import (
    EPSILON_FN,
    W_A_PDG,
    W_ETABAR_PDG,
    W_J_PDG,
    W_LAMBDA_PDG,
    ckm_triangle_fn_geometry,
    eta_bar_fn,
    jarlskog_invariant_fn,
    wolfenstein_fn_corrected,
)


@pytest.fixture(scope="module")
def eta():
    return eta_bar_fn()


@pytest.fixture(scope="module")
def wolf():
    return wolfenstein_fn_corrected()


@pytest.fixture(scope="module")
def jcp():
    return jarlskog_invariant_fn()


@pytest.fixture(scope="module")
def triangle():
    return ckm_triangle_fn_geometry()


def test_eta_payload_is_dict(eta):
    assert isinstance(eta, dict)


def test_eta_bar_fn_value(eta):
    assert eta["eta_bar_fn"] == pytest.approx(0.3545021758, abs=1e-10)


def test_eta_bar_fn_above_pdg(eta):
    assert eta["eta_bar_fn"] > W_ETABAR_PDG


def test_eta_bar_residual_small(eta):
    assert eta["residual_percent"] == pytest.approx(1.8684413165, abs=1e-8)


def test_eta_formula_present(eta):
    assert "sqrt" in eta["formula"]


def test_wolf_payload_is_dict(wolf):
    assert isinstance(wolf, dict)


def test_lambda_fn_slightly_above_geo(wolf):
    assert wolf["lambda_fn"] > W_LAMBDA_PDG


def test_lambda_fn_value(wolf):
    assert wolf["lambda_fn"] == pytest.approx(0.2252054419, abs=1e-10)


def test_a_fn_slightly_above_geo(wolf):
    assert wolf["A_fn"] > W_A_PDG


def test_a_fn_value(wolf):
    assert wolf["A_fn"] == pytest.approx(0.8278855004, abs=1e-10)


def test_order_tracking_linear_in_epsilon(wolf):
    assert wolf["order_tracking"] == "O(epsilon_FN)"


def test_charge_coefficients_present(wolf):
    assert {"c_lambda", "c_A"} == set(wolf["charge_coefficients"].keys())


def test_rho_eta_forwarded(wolf, eta):
    assert wolf["rho_bar_fn"] == pytest.approx(eta["rho_bar_fn"])
    assert wolf["eta_bar_fn"] == pytest.approx(eta["eta_bar_fn"])


def test_j_payload_is_dict(jcp):
    assert isinstance(jcp, dict)


def test_j_geo_value(jcp):
    assert jcp["J_CP_geo"] == pytest.approx(3.1381529613e-5, abs=1e-15)


def test_j_fn_value(jcp):
    assert jcp["J_CP_fn"] == pytest.approx(3.1698064309e-5, abs=1e-15)


def test_j_fn_close_to_pdg(jcp):
    assert jcp["fn_residual_percent"] < 5.0


def test_j_geo_close_to_pdg(jcp):
    assert jcp["geo_residual_percent"] < 5.0


def test_j_fn_above_j_geo(jcp):
    assert jcp["J_CP_fn"] > jcp["J_CP_geo"]


def test_triangle_payload_is_dict(triangle):
    assert isinstance(triangle, dict)


def test_triangle_status(triangle):
    assert triangle["status"] == "CKM_TRIANGLE_FN_GEOMETRY_BUILT"


def test_triangle_apex_coordinates(triangle):
    apex = triangle["triangle_coordinates"]["apex"]
    assert apex[0] == pytest.approx(0.0961145280, abs=1e-10)
    assert apex[1] == pytest.approx(0.3545021758, abs=1e-10)


def test_triangle_delta_eff(triangle):
    assert triangle["delta_eff_deg"] == pytest.approx(74.8303449301, abs=1e-9)


def test_triangle_embeds_jarlskog(triangle, jcp):
    assert triangle["jarlskog"]["J_CP_fn"] == pytest.approx(jcp["J_CP_fn"])


def test_triangle_honest_note_mentions_rho_bar(triangle):
    assert "rho-bar" in triangle["honest_note"].lower() or "rho-bar" in triangle["honest_note"]
