# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 976 — G2 alpha_s Route C Audit."""

import math
import pytest

from src.core.pillar976_alpha_s_route_c_audit import (
    PILLAR_STATUS,
    PILLAR_VALID,
    K_CS,
    N_C,
    M_KK_REFERENCE_GEV,
    M_PL_GEV,
    ALPHA_S_ROUTE_A,
    ALPHA_S_PDG_MZ,
    ALPHA_S_TEV_REFERENCE,
    FLAG_NNLO_THRESHOLD,
    ALPHA_S_GAP_FRACTION,
    ROUTE_C_CANDIDATES,
    ROUTE_C_STATUS,
    alpha_s_route_a,
    route_c_enumeration,
    route_c_verdict,
    g2_floor_certification,
    falsification_update,
    fallibility_update,
    pillar976_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "ALPHA_S_ROUTE_C_NONEXISTENT_CERTIFIED"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_core_constants():
    assert K_CS == 74
    assert N_C == 3
    assert M_KK_REFERENCE_GEV == 1000.0
    assert M_PL_GEV > 1e18


def test_alpha_s_route_a_constant():
    expected = math.pi ** 2 / (2.0 * 74.0)
    assert abs(ALPHA_S_ROUTE_A - expected) < 1e-15


def test_alpha_s_route_a_value_is_low():
    assert ALPHA_S_ROUTE_A < ALPHA_S_PDG_MZ
    assert ALPHA_S_ROUTE_A < ALPHA_S_TEV_REFERENCE


def test_gap_fraction_floor():
    assert ALPHA_S_GAP_FRACTION == 0.40


def test_route_c_candidates_count():
    assert len(ROUTE_C_CANDIDATES) == 5


def test_route_c_status():
    assert ROUTE_C_STATUS == "NONEXISTENT_IN_5D_EFT"


def test_alpha_s_route_a_function():
    result = alpha_s_route_a()
    assert result["formula"] == "pi^2/(2*K_CS)"
    assert result["status"] == "ROUTE_A_EXHAUSTED"
    assert result["residual_fraction_vs_pdg"] > 0.4


def test_route_c_enumeration_structure():
    routes = route_c_enumeration()
    assert len(routes) == 5
    assert all("candidate" in route for route in routes)


def test_two_inside_5d_are_negligible():
    routes = route_c_enumeration()
    inside = [route for route in routes if route["within_5d_eft"]]
    assert len(inside) == 2
    assert all(route["status"] == "NEGLIGIBLE" for route in inside)


def test_instonton_route_is_tiny():
    routes = route_c_enumeration()
    instanton = routes[1]
    assert instanton["size_estimate"] < 1e-50
    assert instanton["suppression_exponent"] > 100.0


def test_kk_loop_route_is_tiny():
    routes = route_c_enumeration()
    kk_loop = routes[2]
    assert kk_loop["size_estimate"] < 1e-30


def test_routes_outside_5d_count():
    verdict = route_c_verdict()
    assert verdict["routes_requiring_exit_from_5d"] == 3


def test_route_c_verdict():
    verdict = route_c_verdict()
    assert verdict["route_c_exists"] is False
    assert verdict["all_routes_negligible_or_exiting_5d"] is True
    assert verdict["route_c_status"] == ROUTE_C_STATUS


def test_floor_certification():
    cert = g2_floor_certification()
    assert cert["gap_label"] == "G2"
    assert cert["type_b_classification"] == "TYPE_B_STRUCTURAL_FLOOR"
    assert cert["closure_claimed"] is False


def test_falsification_update_values():
    update = falsification_update()
    assert update["section"] == "§XVII.3"
    assert update["flag_nnlo_threshold"] == FLAG_NNLO_THRESHOLD
    assert update["experimental_reference_at_1tev"] == ALPHA_S_TEV_REFERENCE
    assert update["um_route_a_value"] < update["experimental_reference_at_1tev"]


def test_flag_threshold_reasonable():
    assert FLAG_NNLO_THRESHOLD > ALPHA_S_TEV_REFERENCE
    assert FLAG_NNLO_THRESHOLD > ALPHA_S_ROUTE_A


def test_fallibility_update():
    fb = fallibility_update()
    assert fb["pillar"] == 976
    assert "nonexistent" in fb["new_status"].lower()
    assert "≥40%" in fb["residual_gap"]


def test_summary():
    summary = pillar976_summary()
    assert summary["pillar"] == 976
    assert summary["valid"] is True
    assert len(summary["derivation_chain"]) >= 5

