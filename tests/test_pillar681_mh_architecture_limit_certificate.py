# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 681: m_H Architecture-Limit Certificate."""

import math
import pytest
from src.core.pillar681_mh_architecture_limit_certificate import (
    N_W, K_CS, N_C, PI_KR,
    M_H_OBS_GEV, M_TOP_GEV, V_EW_GEV, M_KK_GEV,
    case_a_ghu,
    case_b_cw,
    case_d_combined_maximum,
    mh_architecture_certificate,
)


def test_m_h_obs():
    assert abs(M_H_OBS_GEV - 125.25) < 0.1


def test_m_top():
    assert 172 < M_TOP_GEV < 174


def test_v_ew():
    assert 245 < V_EW_GEV < 248


def test_case_a_returns_dict():
    assert isinstance(case_a_ghu(), dict)


def test_case_a_lambda_tiny():
    a = case_a_ghu()
    assert a["lambda_h_ghu"] < 0.01


def test_case_a_m_h_tiny():
    a = case_a_ghu()
    assert a["m_h_ghu_gev"] < 50.0


def test_case_a_gap_large():
    a = case_a_ghu()
    assert a["gap_factor"] > 10


def test_case_b_returns_dict():
    assert isinstance(case_b_cw(), dict)


def test_case_b_lambda_positive():
    b = case_b_cw()
    assert b["lambda_h_cw"] > 0


def test_case_b_m_h_range():
    b = case_b_cw()
    assert 20 < b["m_h_cw_gev"] < 110


def test_case_b_below_obs():
    b = case_b_cw()
    assert b["m_h_cw_gev"] < M_H_OBS_GEV


def test_case_b_cw_formula():
    """CW λ = N_c*(m_t/v)^4/(4π²)*log(M_KK/m_t)."""
    b = case_b_cw()
    lam = b["lambda_h_cw"]
    expected = N_C * (M_TOP_GEV / V_EW_GEV)**4 / (4*math.pi**2) * math.log(M_KK_GEV / M_TOP_GEV)
    assert abs(lam - expected) < 1e-6


def test_case_d_returns_dict():
    assert isinstance(case_d_combined_maximum(), dict)


def test_case_d_ceiling_range():
    d = case_d_combined_maximum()
    assert 50 < d["m_h_5d_ceiling_gev"] < 100


def test_case_d_gap_pct():
    d = case_d_combined_maximum()
    assert d["ceiling_gap_pct"] > 30.0


def test_case_d_ceiling_below_obs():
    d = case_d_combined_maximum()
    assert d["m_h_5d_ceiling_gev"] < M_H_OBS_GEV


def test_mh_architecture_certificate_status():
    cert = mh_architecture_certificate()
    assert "MH_ARCHITECTURE_LIMIT_CERTIFIED" in cert["status"]


def test_mh_architecture_certificate_pillar():
    cert = mh_architecture_certificate()
    assert cert.get("pillar") == 681


def test_mh_architecture_certificate_fields():
    cert = mh_architecture_certificate()
    for field in ("status", "pillar", "case_d_combined"):
        assert field in cert


def test_mh_architecture_certificate_idempotent():
    c1 = mh_architecture_certificate()
    c2 = mh_architecture_certificate()
    assert c1["status"] == c2["status"]
