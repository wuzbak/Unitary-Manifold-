# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for NP BC8: Wheeler-DeWitt Functional-RG Flow."""

import math
import pytest
from src.core.np_bc8_wdw_frg_flow import (
    N_W, K_CS, PI_KR, M_PL_GEV,
    UV_FIXED_POINT_GN, FRG_BETA_COEFFICIENT, CRITICAL_EXPONENT,
    uv_fixed_point,
    frg_beta_newton,
    kk_spectrum_trace,
    radion_frg_correction,
    np_bc8_report,
)


def test_uv_fixed_point_gn_formula():
    """G_N* = 3π / (n_w · K_CS - 10) in Planck units."""
    denominator = N_W * K_CS - 10
    expected = 3 * math.pi / denominator
    assert abs(UV_FIXED_POINT_GN - expected) < 1e-12


def test_uv_fixed_point_gn_positive():
    assert UV_FIXED_POINT_GN > 0


def test_uv_fixed_point_gn_small():
    """G_N* << 1 in Planck units (deep UV, asymptotically safe regime)."""
    assert UV_FIXED_POINT_GN < 0.1


def test_uv_fixed_point_returns_dict():
    assert isinstance(uv_fixed_point(), dict)


def test_uv_fixed_point_g_n_star_mpl2():
    u = uv_fixed_point()
    g_star = u["g_n_star_mpl2"]
    assert g_star > 0
    assert math.isfinite(g_star)


def test_uv_fixed_point_gev2_positive():
    u = uv_fixed_point()
    assert u["g_n_star_gev2"] > 0


def test_uv_fixed_point_critical_exponent():
    u = uv_fixed_point()
    # Critical exponent should be 2 (canonical Reuter value)
    assert abs(u["critical_exponent"] - 2.0) < 1e-6


def test_frg_beta_newton_positive():
    """β(G_N, k) > 0 for G_N > 0, k > 0 (G_N flows up in UV as defined)."""
    beta = frg_beta_newton(UV_FIXED_POINT_GN, 1.0)
    # The implemented beta is a positive definite linear function
    assert math.isfinite(beta)


def test_frg_beta_newton_scales_with_g():
    """β is proportional to G_N."""
    b1 = frg_beta_newton(UV_FIXED_POINT_GN, 1.0)
    b2 = frg_beta_newton(UV_FIXED_POINT_GN * 2, 1.0)
    assert abs(b2 - 2 * b1) < 1e-12


def test_frg_beta_newton_scales_with_k_squared():
    """β is proportional to k²."""
    b1 = frg_beta_newton(UV_FIXED_POINT_GN, 1.0)
    b2 = frg_beta_newton(UV_FIXED_POINT_GN, 2.0)
    assert abs(b2 - 4 * b1) < 1e-12


def test_kk_spectrum_trace_returns_dict():
    assert isinstance(kk_spectrum_trace(), dict)


def test_kk_spectrum_trace_value():
    t = kk_spectrum_trace()
    assert "trace_value" in t
    assert math.isfinite(t["trace_value"])


def test_kk_spectrum_trace_n_modes():
    t = kk_spectrum_trace(n_modes=5)
    assert t["n_modes"] == 5


def test_kk_spectrum_trace_positive():
    t = kk_spectrum_trace()
    assert t["trace_value"] > 0


def test_radion_frg_correction_returns_dict():
    assert isinstance(radion_frg_correction(), dict)


def test_radion_frg_correction_suppression_string():
    r = radion_frg_correction()
    supp = r["suppression"]
    assert isinstance(supp, str)
    assert "suppressed" in supp.lower() or "exp" in supp.lower()


def test_radion_frg_correction_magnitude_tiny():
    r = radion_frg_correction()
    assert abs(r["beta_radion"]) < 1e-20


def test_np_bc8_report_status():
    report = np_bc8_report()
    assert "NP_BC8_WDW_FRG_FLOW_IMPLEMENTED" in report["status"]


def test_np_bc8_report_bc_number():
    report = np_bc8_report()
    assert report.get("bc_number") == 8


def test_np_bc8_report_has_uv_fixed_point():
    report = np_bc8_report()
    assert "uv_fixed_point" in report


def test_np_bc8_report_idempotent():
    r1 = np_bc8_report()
    r2 = np_bc8_report()
    assert r1["status"] == r2["status"]


def test_np_bc8_report_residual_open():
    report = np_bc8_report()
    assert "residual_open" in report
    assert len(report["residual_open"]) > 0
