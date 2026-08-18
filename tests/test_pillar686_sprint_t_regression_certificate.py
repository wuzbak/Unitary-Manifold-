# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 686: Sprint T Regression Certificate v21.1."""

from __future__ import annotations

import math
import pytest

from src.core.pillar686_sprint_t_regression_certificate import (
    PILLAR_NUMBER, PILLAR_STATUS, PILLAR_TITLE, VERSION,
    SPRINT_T_PILLARS, SPRINT_T_TEST_COUNT, TOE_SCORE, NEXT_PILLAR_SLOT,
    sprint_t_summary,
    architecture_limit_inventory,
    open_monitoring_items,
    sprint_t_certificate,
)


# ── Metadata ──────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 686


def test_version():
    assert VERSION == "v21.1"


def test_status():
    assert PILLAR_STATUS == "SPRINT_T_REGRESSION_CERTIFICATE_ISSUED"


def test_sprint_t_pillars():
    assert 682 in SPRINT_T_PILLARS
    assert 683 in SPRINT_T_PILLARS
    assert 684 in SPRINT_T_PILLARS
    assert 685 in SPRINT_T_PILLARS
    assert 686 in SPRINT_T_PILLARS


def test_sprint_t_pillars_count():
    assert len(SPRINT_T_PILLARS) == 5


def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 687


def test_toe_score():
    assert abs(TOE_SCORE - 30.0) < 0.01


def test_sprint_t_test_count_positive():
    assert SPRINT_T_TEST_COUNT > 100


# ── sprint_t_summary ──────────────────────────────────────────────────────────

def test_summary_keys():
    s = sprint_t_summary()
    for k in ["sprint", "version", "pillars_added", "n_new_pillars",
              "toe_score", "toe_unchanged", "next_pillar_slot", "pillars"]:
        assert k in s


def test_summary_sprint_t():
    s = sprint_t_summary()
    assert s["sprint"] == "T"


def test_summary_toe_unchanged():
    s = sprint_t_summary()
    assert s["toe_unchanged"] is True
    assert s["toe_score"] == 30.0


def test_summary_n_new_pillars():
    s = sprint_t_summary()
    assert s["n_new_pillars"] == 5


def test_summary_next_slot():
    s = sprint_t_summary()
    assert s["next_pillar_slot"] == 687


def test_summary_pillars_dict():
    s = sprint_t_summary()
    pillars = s["pillars"]
    for pid in [682, 683, 684, 685, 686]:
        assert pid in pillars


def test_summary_pillar_682_tightening5():
    s = sprint_t_summary()
    p = s["pillars"][682]
    assert "Tightening" in p["label"] or "5" in p["label"]
    assert p["toe_delta"] == 0


def test_summary_pillar_684_np_bc9():
    s = sprint_t_summary()
    p = s["pillars"][684]
    assert "BC9" in p["label"] or "NP" in p["label"]


def test_summary_pillar_tests_positive():
    s = sprint_t_summary()
    for pid, pdata in s["pillars"].items():
        assert pdata["tests"] > 0, f"Pillar {pid} has 0 tests"


def test_summary_new_pillar_max():
    s = sprint_t_summary()
    assert s["new_pillar_max"] == 686


# ── architecture_limit_inventory ──────────────────────────────────────────────

def test_arch_inventory_is_list():
    inv = architecture_limit_inventory()
    assert isinstance(inv, list)
    assert len(inv) >= 4


def test_arch_inventory_keys():
    for item in architecture_limit_inventory():
        for k in ["claim", "status", "gap_pct", "certified_by", "closure_path"]:
            assert k in item


def test_arch_alpha_s_present():
    claims = [item["claim"] for item in architecture_limit_inventory()]
    assert any("P3" in c or "α_s" in c for c in claims)


def test_arch_m_h_present():
    claims = [item["claim"] for item in architecture_limit_inventory()]
    assert any("P5" in c or "m_H" in c for c in claims)


def test_arch_rho_bar_present():
    claims = [item["claim"] for item in architecture_limit_inventory()]
    assert any("P14" in c or "ρ̄" in c for c in claims)


def test_arch_theta13_present():
    claims = [item["claim"] for item in architecture_limit_inventory()]
    assert any("θ₁₃" in c or "theta13" in c.lower() for c in claims)


def test_arch_alpha_s_gap():
    for item in architecture_limit_inventory():
        if "P3" in item["claim"] or "α_s" in item["claim"]:
            assert item["gap_pct"] > 35.0


def test_arch_certified_by_is_list():
    for item in architecture_limit_inventory():
        assert isinstance(item["certified_by"], list)


# ── open_monitoring_items ─────────────────────────────────────────────────────

def test_monitoring_is_list():
    m = open_monitoring_items()
    assert isinstance(m, list)
    assert len(m) >= 4


def test_monitoring_keys():
    for item in open_monitoring_items():
        assert "item" in item
        assert "pillar" in item


def test_monitoring_litebird_present():
    items = [m["item"] for m in open_monitoring_items()]
    assert any("LiteBIRD" in i or "litebird" in i.lower() for i in items)


def test_monitoring_desi_present():
    items = [m["item"] for m in open_monitoring_items()]
    assert any("DESI" in i for i in items)


def test_monitoring_juno_present():
    items = [m["item"] for m in open_monitoring_items()]
    assert any("JUNO" in i for i in items)


# ── sprint_t_certificate ──────────────────────────────────────────────────────

def test_certificate_keys():
    cert = sprint_t_certificate()
    for k in ["pillar", "title", "version", "status", "sprint",
              "toe_score", "next_pillar_slot", "regression_verdict",
              "architecture_limits", "open_monitoring"]:
        assert k in cert


def test_certificate_pillar():
    cert = sprint_t_certificate()
    assert cert["pillar"] == 686


def test_certificate_regression_pass():
    cert = sprint_t_certificate()
    assert cert["regression_verdict"] == "PASS"


def test_certificate_estimated_tests():
    cert = sprint_t_certificate()
    # Should be > 51951 (prior) + ~200 (sprint T)
    assert cert["estimated_total_tests"] > 52000


def test_certificate_toe():
    cert = sprint_t_certificate()
    assert abs(cert["toe_score"] - 30.0) < 0.01


def test_certificate_np_bc_ledger():
    cert = sprint_t_certificate()
    assert "BC9" in cert["np_bc_ledger_status"]
    assert "BC10" in cert["np_bc_ledger_status"]


def test_certificate_nw_kcs_check():
    cert = sprint_t_certificate()
    check = cert["sprint_t_nw_kcs_check"]
    assert check["n_w"] == 5
    assert check["k_cs"] == 74
    assert check["n_w_times_k_cs"] == 370
    assert abs(check["pi_kr"] - math.pi * 74 / 5) < 1e-10


def test_certificate_next_pillar():
    cert = sprint_t_certificate()
    assert cert["next_pillar_slot"] == 687


def test_certificate_test_count_added():
    cert = sprint_t_certificate()
    assert cert["test_count_added"] > 100


def test_certificate_prior_test_count():
    cert = sprint_t_certificate()
    assert cert["prior_test_count"] == 51951
