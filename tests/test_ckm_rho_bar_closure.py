# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 142: CKM ρ̄ Closure (src/core/ckm_rho_bar_closure.py).

Honest: both leading and subleading give ρ̄ ~ 0.113–0.119 vs PDG 0.159; ~25% discrepancy.
"""

import math
import pytest

from src.core.ckm_rho_bar_closure import (
    rho_bar_leading_order,
    rho_bar_subleading,
    ckm_rho_bar_closure_status,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def leading():
    return rho_bar_leading_order()


@pytest.fixture(scope="module")
def subleading():
    return rho_bar_subleading()


@pytest.fixture(scope="module")
def status():
    return ckm_rho_bar_closure_status()


# ---------------------------------------------------------------------------
# rho_bar_leading_order — return type and keys
# ---------------------------------------------------------------------------

def test_leading_is_dict(leading):
    assert isinstance(leading, dict)


def test_leading_has_rho_bar(leading):
    assert "rho_bar" in leading


def test_leading_has_pct_error(leading):
    assert "pct_error" in leading


def test_leading_has_delta_deg(leading):
    assert "delta_deg" in leading


def test_leading_has_r_b(leading):
    assert "R_b" in leading


# ---------------------------------------------------------------------------
# Leading order values
# ---------------------------------------------------------------------------

def test_rho_lead_positive(leading):
    assert leading["rho_bar"] > 0


def test_rho_lead_value(leading):
    assert abs(leading["rho_bar"] - 0.11350) < 0.001


def test_rho_lead_below_pdg(leading):
    # PDG is 0.159; we get ~0.1135
    assert leading["rho_bar"] < 0.159


def test_r_b_value(leading):
    assert abs(leading["R_b"] - 0.36730) < 0.001


def test_r_b_in_range(leading):
    assert 0.30 < leading["R_b"] < 0.45


def test_delta_deg_leading_72(leading):
    assert abs(leading["delta_deg"] - 72.0) < 0.1


def test_pct_error_lead_positive(leading):
    assert leading["pct_error"] > 0


def test_pct_error_lead_above_25(leading):
    assert leading["pct_error"] > 25.0


def test_pct_error_lead_value(leading):
    assert abs(leading["pct_error"] - 28.61) < 0.5


# ---------------------------------------------------------------------------
# rho_bar_subleading — return type and keys
# ---------------------------------------------------------------------------

def test_subleading_is_dict(subleading):
    assert isinstance(subleading, dict)


def test_subleading_has_rho_bar_sub(subleading):
    assert "rho_bar_sub" in subleading


def test_subleading_has_pct_error(subleading):
    assert "pct_error" in subleading


def test_subleading_has_delta_sub_deg(subleading):
    assert "delta_sub_deg" in subleading


def test_subleading_has_r_b(subleading):
    assert "R_b" in subleading


def test_subleading_has_improvement_pct(subleading):
    assert "improvement_pct" in subleading


# ---------------------------------------------------------------------------
# Subleading order values
# ---------------------------------------------------------------------------

def test_rho_sub_positive(subleading):
    assert subleading["rho_bar_sub"] > 0


def test_rho_sub_value(subleading):
    assert abs(subleading["rho_bar_sub"] - 0.11912) < 0.001


def test_rho_sub_below_pdg(subleading):
    assert subleading["rho_bar_sub"] < 0.159


def test_delta_sub_deg_value(subleading):
    expected = math.degrees(2 * math.atan(5 / 7))
    assert abs(subleading["delta_sub_deg"] - expected) < 0.01


def test_delta_sub_deg_near_71(subleading):
    assert abs(subleading["delta_sub_deg"] - 71.0754) < 0.01


def test_pct_error_sub_positive(subleading):
    assert subleading["pct_error"] > 0


def test_pct_error_sub_below_30(subleading):
    assert subleading["pct_error"] < 30.0


def test_pct_error_sub_value(subleading):
    assert abs(subleading["pct_error"] - 25.08) < 0.5


# ---------------------------------------------------------------------------
# Comparison between leading and subleading
# ---------------------------------------------------------------------------

def test_rho_sub_gt_rho_lead(leading, subleading):
    # Subleading is slightly larger, closer to PDG
    assert subleading["rho_bar_sub"] > leading["rho_bar"]


def test_pct_error_lead_gt_pct_error_sub(leading, subleading):
    # Subleading has smaller error (improvement)
    assert leading["pct_error"] > subleading["pct_error"]


def test_r_b_consistent(leading, subleading):
    assert abs(leading["R_b"] - subleading["R_b"]) < 1e-10


def test_delta_sub_lt_delta_lead(leading, subleading):
    # 71.075 < 72
    assert subleading["delta_sub_deg"] < leading["delta_deg"]


# ---------------------------------------------------------------------------
# ckm_rho_bar_closure_status
# ---------------------------------------------------------------------------

def test_status_is_dict(status):
    assert isinstance(status, dict)


def test_status_pillar_142(status):
    assert status["pillar"] == 142


def test_status_final_status_estimate(status):
    assert "ESTIMATE" in status["final_status"]


def test_status_improvement_achieved_true(status):
    assert status["improvement_achieved"] is True


def test_status_rho_bar_leading(status):
    assert abs(status["rho_bar_leading"] - 0.11350) < 0.001


def test_status_rho_bar_subleading(status):
    assert abs(status["rho_bar_subleading"] - 0.11912) < 0.001


def test_status_pdg_value(status):
    assert abs(status["pdg"] - 0.159) < 0.001


def test_status_has_honest_note(status):
    assert "honest_note" in status


def test_status_honest_note_non_empty(status):
    assert len(status["honest_note"]) > 0


def test_status_closed_true(status):
    assert status.get("closed") is True
