# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for 7D CKM ρ̄ integration: src/sevend/ckm_rhobar_7d_integration.py"""

from __future__ import annotations

import math

import pytest

from src.sevend.ckm_rhobar_7d_integration import (
    DELTA_CP_7D_DEG,
    DELTA_CP_7D_RAD,
    RHO_BAR_7D,
    RHO_BAR_7D_PCT_ERR,
    STATUS,
    ckm_rhobar_7d_summary,
    delta_cp_constraint_7d,
    rhobar_integration_kill_switch,
    rho_bar_with_7d_delta,
)


def test_delta_cp_is_pi_third():
    assert DELTA_CP_7D_RAD == pytest.approx(math.pi / 3.0, rel=1e-6)
    assert DELTA_CP_7D_DEG == pytest.approx(60.0, rel=1e-6)


def test_delta_constraint_payload():
    d = delta_cp_constraint_7d()
    assert d["delta_cp_rad"] == DELTA_CP_7D_RAD


def test_rho_bar_result_positive():
    r = rho_bar_with_7d_delta()
    assert r["rho_bar"] > 0.0


def test_rho_bar_kill_switch_meets_20pct_threshold():
    ks = rhobar_integration_kill_switch()
    assert ks["pass"] is True
    assert ks["pct_err_7d"] <= 20.0


def test_status_is_constrained_or_better():
    assert STATUS in {"CONSTRAINED", "CONSTRAINED+"}


def test_module_constants_match_function_output():
    r = rho_bar_with_7d_delta()
    assert RHO_BAR_7D == pytest.approx(r["rho_bar"])
    assert RHO_BAR_7D_PCT_ERR == pytest.approx(r["pct_err_vs_pdg"])


def test_summary_contains_gate_update():
    s = ckm_rhobar_7d_summary()
    assert "p14_gate_update" in s
    assert "recommendation" in s["p14_gate_update"]
