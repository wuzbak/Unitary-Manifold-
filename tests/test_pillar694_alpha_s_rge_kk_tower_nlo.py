# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 694 — α_s RGE KK tower NLO."""

import math

from src.core.pillar694_alpha_s_rge_kk_tower_nlo import (
    N_W,
    K_CS,
    ALPHA_S_PDG_MZ,
    M_Z_GEV,
    M_KK_MEV,
    M_KK_GEV,
    PI,
    beta_function_kk_corrected,
    alpha_s_nlo_kk_tower,
    nlo_residual,
)


def test_constants():
    assert N_W == 5
    assert K_CS == 74
    assert ALPHA_S_PDG_MZ == 0.1180


def test_scales():
    assert abs(M_Z_GEV - 91.1876) < 1e-12
    assert abs(M_KK_MEV - 110.0) < 1e-12
    assert abs(M_KK_GEV - 0.110) < 1e-12


def test_pi_matches_math():
    assert abs(PI - math.pi) < 1e-15


def test_beta_returns_dict():
    assert isinstance(beta_function_kk_corrected(), dict)


def test_beta_sm_formula():
    beta = beta_function_kk_corrected()
    expected = (11 * 3 - 2 * 6 / 2 - 0.5) / (2 * math.pi)
    assert abs(beta["b_0_sm"] - expected) < 1e-12


def test_beta_increment_formula():
    beta = beta_function_kk_corrected()
    assert abs(beta["kk_increment"] - (N_W / (2 * math.pi))) < 1e-12


def test_beta_kk_larger_than_sm():
    beta = beta_function_kk_corrected()
    assert beta["b_0_kk"] > beta["b_0_sm"]


def test_alpha_s_kk_reasonable():
    beta = beta_function_kk_corrected()
    assert 0.02 < beta["alpha_s_kk"] < 0.04


def test_nlo_returns_dict():
    assert isinstance(alpha_s_nlo_kk_tower(), dict)


def test_log_ratio_large_positive():
    result = alpha_s_nlo_kk_tower()
    assert result["log_mz2_over_mkk2"] > 10.0


def test_denominator_above_one():
    result = alpha_s_nlo_kk_tower()
    assert result["denominator"] > 1.0


def test_nlo_alpha_lower_than_alpha_kk():
    result = alpha_s_nlo_kk_tower()
    assert result["alpha_s_mz_nlo"] < result["alpha_s_kk"]


def test_nlo_alpha_positive():
    result = alpha_s_nlo_kk_tower()
    assert result["alpha_s_mz_nlo"] > 0.0


def test_nlo_alpha_small():
    result = alpha_s_nlo_kk_tower()
    assert result["alpha_s_mz_nlo"] < 0.03


def test_nlo_residual_large():
    result = alpha_s_nlo_kk_tower()
    assert result["residual_pct"] > 70.0


def test_nlo_verdict_irreducible():
    result = alpha_s_nlo_kk_tower()
    assert result["verdict"] == "IRREDUCIBLE"


def test_residual_returns_dict():
    assert isinstance(nlo_residual(), dict)


def test_residual_status():
    cert = nlo_residual()
    assert cert["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_residual_contains_beta_function():
    cert = nlo_residual()
    assert "beta_function" in cert


def test_residual_nested_result():
    cert = nlo_residual()
    assert "result" in cert
