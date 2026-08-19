# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 693 — α_s 13D moduli pathway."""

import math

from src.core.pillar693_alpha_s_13d_moduli_pathway import (
    N_W,
    K_CS,
    ALPHA_S_PDG_MZ,
    PI,
    gauge_kinetic_function_13d,
    alpha_s_13d_moduli,
    alpha_s_13d_status,
)


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert ALPHA_S_PDG_MZ == 0.1180


def test_pi_matches_math():
    assert abs(PI - math.pi) < 1e-15


def test_gauge_function_returns_dict():
    assert isinstance(gauge_kinetic_function_13d(), dict)


def test_k_gs_value():
    data = gauge_kinetic_function_13d()
    assert abs(data["k_gs"] - 2.5) < 1e-12


def test_delta_13d_exact():
    data = gauge_kinetic_function_13d()
    assert abs(data["delta_13d"] - (5 / 148)) < 1e-12


def test_f_tree_formula():
    data = gauge_kinetic_function_13d()
    assert abs(data["f_tree"] - (K_CS / (2 * math.pi))) < 1e-12


def test_f_total_larger_than_tree():
    data = gauge_kinetic_function_13d()
    assert data["f_total"] > data["f_tree"]


def test_alpha_13d_positive():
    data = gauge_kinetic_function_13d()
    assert data["alpha_s_13d"] > 0.0


def test_alpha_13d_tiny():
    data = gauge_kinetic_function_13d()
    assert data["alpha_s_13d"] < 0.001


def test_fractional_shift_negative():
    data = gauge_kinetic_function_13d()
    assert data["fractional_shift_from_tree"] < 0.0


def test_alpha_moduli_returns_dict():
    assert isinstance(alpha_s_13d_moduli(), dict)


def test_alpha_moduli_matches_gauge_data():
    result = alpha_s_13d_moduli()
    gauge = gauge_kinetic_function_13d()
    assert abs(result["alpha_s_13d"] - gauge["alpha_s_13d"]) < 1e-15


def test_alpha_moduli_residual_huge():
    result = alpha_s_13d_moduli()
    assert result["residual_pct"] > 90.0


def test_alpha_moduli_not_missing_lever():
    result = alpha_s_13d_moduli()
    assert result["missing_lever_found"] is False


def test_alpha_moduli_verdict_irreducible():
    result = alpha_s_13d_moduli()
    assert result["verdict"] == "IRREDUCIBLE"


def test_alpha_moduli_worse_than_ads():
    result = alpha_s_13d_moduli()
    assert result["residual_reduction_vs_ads_pct_points"] < 0.0


def test_status_returns_dict():
    assert isinstance(alpha_s_13d_status(), dict)


def test_status_architecture_limit():
    cert = alpha_s_13d_status()
    assert cert["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_status_certificate_irreducible():
    cert = alpha_s_13d_status()
    assert cert["certificate"] == "IRREDUCIBLE"


def test_status_contains_nested_result():
    cert = alpha_s_13d_status()
    assert "result" in cert
    assert "gauge_kinetic_function" in cert
