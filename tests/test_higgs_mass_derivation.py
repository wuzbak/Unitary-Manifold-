# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_higgs_mass_derivation.py
====================================
Tests for Pillar 102-A — Higgs boson mass prediction from the RS/GW mechanism.

Coverage (~25 tests):
  - higgs_quartic_from_gw()
  - higgs_mass_gw()
  - higgs_mass_summary()
"""

import math
import pytest

from src.core.higgs_mass_derivation import (
    higgs_quartic_from_gw,
    higgs_mass_gw,
    higgs_mass_summary,
    PI_KR,
    K_CS,
    M_HIGGS_PDG_GEV,
    V_EW_GEV,
    M_PL_GEV,
)


# ── Constants sanity ───────────────────────────────────────────────────────────

def test_pi_kr_from_kcs():
    assert PI_KR == pytest.approx(37.0)
    assert K_CS == 74


def test_pdg_higgs_mass():
    assert M_HIGGS_PDG_GEV == pytest.approx(125.25, rel=1e-4)


def test_ew_vev():
    assert V_EW_GEV == pytest.approx(246.22, rel=1e-4)


# ── higgs_quartic_from_gw ──────────────────────────────────────────────────────

def test_quartic_positive():
    r = higgs_quartic_from_gw()
    assert r["lambda_H_um"] > 0


def test_quartic_sm_value():
    r = higgs_quartic_from_gw()
    # SM: λ_H = m_H² / (2 v²) ≈ 0.129
    assert r["lambda_H_sm"] == pytest.approx(0.129, rel=0.02)


def test_quartic_returns_mkk():
    r = higgs_quartic_from_gw()
    assert r["M_KK_gev"] > 0


def test_quartic_mkk_formula():
    k_gev = 0.1 * M_PL_GEV
    expected = k_gev * math.exp(-37.0)
    r = higgs_quartic_from_gw(k_over_mpl=0.1)
    assert r["M_KK_gev"] == pytest.approx(expected, rel=1e-8)


def test_quartic_keys():
    r = higgs_quartic_from_gw()
    for key in ["pi_kR", "k_over_mpl", "M_KK_gev", "lambda_H_um", "lambda_H_sm", "ratio"]:
        assert key in r


def test_quartic_scales_with_k():
    r1 = higgs_quartic_from_gw(k_over_mpl=0.05)
    r2 = higgs_quartic_from_gw(k_over_mpl=0.10)
    # λ_H ∝ (M_KK)² ∝ k² so ratio should be ~4
    assert r2["lambda_H_um"] == pytest.approx(r1["lambda_H_um"] * 4, rel=1e-6)


# ── higgs_mass_gw ──────────────────────────────────────────────────────────────

def test_mass_gw_positive():
    r = higgs_mass_gw()
    assert r["m_H_pred_gev"] > 0


def test_mass_gw_mkk_positive():
    r = higgs_mass_gw()
    assert r["M_KK_gev"] > 0


def test_mass_gw_pdg_stored():
    r = higgs_mass_gw()
    assert r["m_H_pdg_gev"] == pytest.approx(125.25, rel=1e-4)


def test_mass_gw_window_low_k():
    r = higgs_mass_gw(k_over_mpl=0.05)
    assert 50.0 < r["m_H_pred_gev"] < 200.0


def test_mass_gw_window_high_k():
    r = higgs_mass_gw(k_over_mpl=0.15)
    assert r["m_H_pred_gev"] > 100.0


@pytest.mark.parametrize("k", [0.05, 0.07, 0.10, 0.12, 0.15])
def test_mass_gw_window_parametric(k):
    r = higgs_mass_gw(k_over_mpl=k)
    assert 50.0 < r["m_H_pred_gev"] < 500.0


def test_mass_gw_status_contains_geometric():
    r = higgs_mass_gw()
    assert "GEOMETRIC" in r["status"]


def test_mass_gw_keys():
    r = higgs_mass_gw()
    for key in [
        "pi_kR", "k_over_mpl", "M_KK_gev", "m_H_pred_gev",
        "m_H_pdg_gev", "pct_error", "k_over_mpl_fitted", "status",
    ]:
        assert key in r


def test_mass_gw_pct_error_nonneg():
    r = higgs_mass_gw()
    assert r["pct_error"] >= 0.0


def test_mass_gw_fitted_k_recovers_pdg():
    k_fit = higgs_mass_gw()["k_over_mpl_fitted"]
    r = higgs_mass_gw(k_over_mpl=k_fit)
    assert r["pct_error"] < 0.01  # < 0.01% when k is fitted


def test_mass_gw_fitted_k_range():
    k_fit = higgs_mass_gw()["k_over_mpl_fitted"]
    assert 0.05 < k_fit < 0.15


def test_mass_gw_pi_kr_stored():
    r = higgs_mass_gw()
    assert r["pi_kR"] == pytest.approx(37.0)


def test_mass_gw_scales_sqrt2_mkk():
    r = higgs_mass_gw(k_over_mpl=0.1)
    expected = math.sqrt(2.0) * r["M_KK_gev"]
    assert r["m_H_pred_gev"] == pytest.approx(expected, rel=1e-8)


# ── higgs_mass_summary ─────────────────────────────────────────────────────────

def test_summary_returns_dict():
    s = higgs_mass_summary()
    assert isinstance(s, dict)


def test_summary_keys():
    s = higgs_mass_summary()
    for key in [
        "parameter", "pdg_value", "unit", "derivation_chain",
        "geometric_window_gev", "k_over_mpl_fitted",
        "pct_error_at_canonical_k", "status", "pillar", "notes",
    ]:
        assert key in s


def test_summary_pillar():
    s = higgs_mass_summary()
    assert "102" in s["pillar"]


def test_summary_pdg_value():
    s = higgs_mass_summary()
    assert s["pdg_value"] == pytest.approx(125.25, rel=1e-4)


def test_summary_window_ordered():
    s = higgs_mass_summary()
    lo, hi = s["geometric_window_gev"]
    assert lo < hi


def test_summary_status_geometric():
    s = higgs_mass_summary()
    assert "GEOMETRIC" in s["status"]
