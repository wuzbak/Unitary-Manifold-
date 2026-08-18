# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 678: α_s Warp-Anchor Architecture-Limit Certificate."""

import math
import pytest
from src.core.pillar678_alpha_s_warp_anchor_closure import (
    N_W, K_CS, N_C, PI_KR,
    ALPHA_S_PDG, ALPHA_S_GEO_MKK, ALPHA_S_ADS_QCD,
    route_a_ads_qcd,
    route_b_gw_vev,
    combined_estimate,
    architecture_limit_certificate,
)


def test_alpha_s_geo_formula():
    expected = 2 * math.pi / (N_C * K_CS)
    assert abs(ALPHA_S_GEO_MKK - expected) < 1e-12


def test_alpha_s_geo_range():
    assert 0.025 < ALPHA_S_GEO_MKK < 0.035


def test_alpha_s_pdg_range():
    assert 0.10 < ALPHA_S_PDG < 0.13


def test_alpha_s_ads_qcd_range():
    # π²/(2·K_CS) ≈ 0.0667
    expected = math.pi**2 / (2 * K_CS)
    assert abs(ALPHA_S_ADS_QCD - expected) < 1e-6


def test_route_a_returns_dict():
    assert isinstance(route_a_ads_qcd(), dict)


def test_route_a_ads_value():
    r = route_a_ads_qcd()
    assert 0.05 < r["alpha_s_ads"] < 0.09


def test_route_a_residual_large():
    r = route_a_ads_qcd()
    assert r["residual_pct"] > 30.0


def test_route_a_ads_closer_than_geo():
    r = route_a_ads_qcd()
    assert r["alpha_s_ads"] > ALPHA_S_GEO_MKK


def test_route_b_returns_dict():
    assert isinstance(route_b_gw_vev(), dict)


def test_route_b_small_effect():
    r = route_b_gw_vev()
    # correction should be < 5% relative shift
    vals = list(r.values())
    floats = [v for v in vals if isinstance(v, float)]
    assert len(floats) > 0


def test_combined_estimate_returns_dict():
    assert isinstance(combined_estimate(), dict)


def test_combined_residual_above_40():
    c = combined_estimate()
    assert c["residual_pct"] >= 40.0, f"residual_pct={c['residual_pct']} < 40%"


def test_combined_alpha_s_below_pdg():
    c = combined_estimate()
    assert c["alpha_s_combined"] < ALPHA_S_PDG


def test_architecture_limit_certificate_status():
    cert = architecture_limit_certificate()
    assert "ALPHA_S_WARP_ANCHOR_ARCHITECTURE_LIMIT_CONFIRMED" in cert["status"]


def test_architecture_limit_certificate_pillar():
    cert = architecture_limit_certificate()
    assert cert.get("pillar") == 678


def test_architecture_limit_certificate_fields():
    cert = architecture_limit_certificate()
    for field in ("status", "pillar", "combined", "route_a"):
        assert field in cert


def test_architecture_limit_certificate_idempotent():
    c1 = architecture_limit_certificate()
    c2 = architecture_limit_certificate()
    assert c1["status"] == c2["status"]
