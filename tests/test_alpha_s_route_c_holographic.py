# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Sprint AO Wave 7: α_s Route C holographic."""
import pytest
from src.core.alpha_s_route_c_holographic import (
    route_c_sakai_sugimoto,
    architecture_limit_bound,
    holographic_string_coupling_bound,
    alpha_s_all_routes_combined,
    alpha_s_p3_certificate,
    ALPHA_S_ROUTE_C_STATUS,
)


def test_status_token():
    assert ALPHA_S_ROUTE_C_STATUS == "ARCHITECTURE_LIMIT_CONFIRMED_ROUTE_C_INSUFFICIENT"


def test_route_c_returns_dict():
    r = route_c_sakai_sugimoto()
    assert isinstance(r, dict)


def test_route_c_alpha_s_ab_positive():
    r = route_c_sakai_sugimoto()
    assert r["alpha_s_AB"] > 0


def test_route_c_delta_positive():
    r = route_c_sakai_sugimoto()
    assert r["delta_alpha_s_C"] >= 0


def test_route_c_does_not_close_gap():
    r = route_c_sakai_sugimoto()
    assert r["route_c_closes_gap"] is False


def test_route_c_residual_pct_positive():
    r = route_c_sakai_sugimoto()
    assert r["residual_pct_after_C"] > 0


def test_architecture_bound_returns_dict():
    b = architecture_limit_bound()
    assert isinstance(b, dict)


def test_holographic_bound_returns_dict():
    b = holographic_string_coupling_bound()
    assert isinstance(b, dict)


def test_all_routes_returns_dict():
    r = alpha_s_all_routes_combined()
    assert isinstance(r, dict)


def test_certificate_status():
    cert = alpha_s_p3_certificate()
    assert cert["ALPHA_S_ROUTE_C_STATUS"] == "ARCHITECTURE_LIMIT_CONFIRMED_ROUTE_C_INSUFFICIENT"
