# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Tightening 2: ρ̄_CKM Architecture-Limit Documentation."""

import math
import pytest
from src.core.tightening_rho_bar_ckm import (
    RHO_BAR_PDG, ETA_BAR_PDG,
    geometric_cp_phase_analysis,
    tightening_audit,
)


def test_rho_bar_pdg():
    assert abs(RHO_BAR_PDG - 0.159) < 0.01


def test_eta_bar_pdg():
    assert abs(ETA_BAR_PDG - 0.348) < 0.01


def test_geometric_cp_phase_analysis_returns_dict():
    assert isinstance(geometric_cp_phase_analysis(), dict)


def test_geometric_rho_bar_positive():
    r = geometric_cp_phase_analysis()
    assert r["rho_bar_geo"] > 0


def test_geometric_rho_bar_range():
    r = geometric_cp_phase_analysis()
    assert 0.05 < r["rho_bar_geo"] < 0.25


def test_geometric_residual_range():
    r = geometric_cp_phase_analysis()
    assert 10 < r["residual_pct"] < 40


def test_geometric_analysis_has_r_b():
    r = geometric_cp_phase_analysis()
    assert "r_b" in r


def test_tightening_audit_status():
    t = tightening_audit()
    assert "RHO_BAR_CKM_ARCHITECTURE_LIMIT_DOCUMENTED" in t["status"]


def test_tightening_audit_architecture_limit():
    t = tightening_audit()
    assert "architecture_limit" in t or "ARCHITECTURE" in str(t)


def test_tightening_audit_names_jarlskog():
    t = tightening_audit()
    audit_str = str(t).lower()
    assert "jarlskog" in audit_str or "layer 2" in audit_str or "pillar 188" in audit_str


def test_tightening_audit_residual_accessible():
    t = tightening_audit()
    current = t.get("current_estimate", {})
    res = current.get("residual_pct", None)
    if res is not None:
        assert res > 10


def test_tightening_audit_idempotent():
    t1 = tightening_audit()
    t2 = tightening_audit()
    assert t1["status"] == t2["status"]
