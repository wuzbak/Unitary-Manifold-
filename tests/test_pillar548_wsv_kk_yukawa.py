# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 548 — DM31 Step 1: WS-V KK Off-Diagonal Yukawa."""
from __future__ import annotations

import math
import pytest
from src.core.pillar548_wsv_kk_yukawa import (
    CL_VALUES,
    DELTA_C,
    JUNO_DM31,
    JUNO_SIGMA,
    K_CS,
    KPI_R,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    STEP1_RESULT,
    UM_BEST_ATTEMPT_DM31,
    VERSION,
    WSV_TEXTURE_PARAMS,
    dm31_step1_projection,
    kk_bulk_overlap,
    pillar_report,
    step1_certificate,
    tension_after_step1,
    wsv_leading_correction,
    wsv_off_diagonal_correction,
    wsv_off_diagonal_correction_total,
    wsv_subleading_correction,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 548


def test_pillar_status():
    assert PILLAR_STATUS == "DM31_STEP1_WS_V_YUKAWA_COMPUTED"


def test_version():
    assert VERSION == "v19.1"


# ─── Constants ───────────────────────────────────────────────────────────────

def test_delta_c():
    assert DELTA_C == pytest.approx(5.0 / 74.0)


def test_kpi_r():
    assert KPI_R == pytest.approx(37.0)


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_juno_dm31():
    assert JUNO_DM31 == pytest.approx(2.411e-3)


def test_um_best_attempt():
    assert UM_BEST_ATTEMPT_DM31 == pytest.approx(2.3457e-3)


def test_best_attempt_below_juno():
    assert UM_BEST_ATTEMPT_DM31 < JUNO_DM31


def test_cl_values_third_gen_zero():
    for f in ["t", "b", "tau"]:
        assert CL_VALUES[f] == pytest.approx(0.0)


def test_cl_values_second_gen():
    for f in ["c", "s", "mu"]:
        assert CL_VALUES[f] == pytest.approx(5.0 / 74.0)


def test_cl_values_first_gen():
    for f in ["u", "d", "e"]:
        assert CL_VALUES[f] == pytest.approx(10.0 / 74.0)


# ─── KK bulk overlap ─────────────────────────────────────────────────────────

def test_kk_bulk_overlap_ir_localized():
    # c_L = 0 → IR-localized, zero-mode overlap = 1
    f = kk_bulk_overlap(0.0, kpi_r=37.0, kk_mode=0)
    assert f == pytest.approx(1.0)


def test_kk_bulk_overlap_kk_mode1_positive():
    # KK mode 1 overlap should be positive for any c_L
    for c in [0.0, 5.0 / 74.0, 10.0 / 74.0]:
        f = kk_bulk_overlap(c, kpi_r=37.0, kk_mode=1)
        assert f > 0.0


def test_kk_bulk_overlap_mode1_decreases_with_c():
    # Higher c_L → more UV-peaked → smaller KK mode overlap
    f1 = kk_bulk_overlap(0.0, kpi_r=37.0, kk_mode=1)
    f2 = kk_bulk_overlap(5.0 / 74.0, kpi_r=37.0, kk_mode=1)
    f3 = kk_bulk_overlap(10.0 / 74.0, kpi_r=37.0, kk_mode=1)
    assert f1 > f2 > f3


def test_kk_bulk_overlap_mode1_formula():
    c = 5.0 / 74.0
    kpi_r = 37.0
    expected = math.sqrt(2.0 * kpi_r) * math.exp(-c * kpi_r)
    assert kk_bulk_overlap(c, kpi_r=kpi_r, kk_mode=1) == pytest.approx(expected)


# ─── WS-V off-diagonal correction ────────────────────────────────────────────

def test_wsv_off_diag_keys():
    result = wsv_off_diagonal_correction(CL_VALUES["mu"], CL_VALUES["tau"])
    for key in ["y_ij_off", "m_eff_ev", "delta_dm31_sq_ev2", "fractional_shift"]:
        assert key in result


def test_wsv_off_diag_y_positive():
    result = wsv_off_diagonal_correction(CL_VALUES["mu"], CL_VALUES["tau"])
    assert result["y_ij_off"] > 0


def test_wsv_off_diag_correction_positive():
    result = wsv_off_diagonal_correction(CL_VALUES["mu"], CL_VALUES["tau"])
    assert result["delta_dm31_sq_ev2"] > 0


def test_wsv_off_diag_delta_kt_zero_gives_zero():
    result = wsv_off_diagonal_correction(CL_VALUES["mu"], CL_VALUES["tau"], delta_kt=0.0)
    assert result["y_ij_off"] == pytest.approx(0.0)
    assert result["delta_dm31_sq_ev2"] == pytest.approx(0.0)


def test_wsv_off_diag_scales_with_delta_kt():
    r1 = wsv_off_diagonal_correction(CL_VALUES["mu"], CL_VALUES["tau"], delta_kt=0.053)
    r2 = wsv_off_diagonal_correction(CL_VALUES["mu"], CL_VALUES["tau"], delta_kt=0.106)
    # Y scales linearly → Δm²₃₁ scales quadratically (via m_eff²)
    assert r2["y_ij_off"] == pytest.approx(2.0 * r1["y_ij_off"], rel=1e-6)


# ─── Leading and sub-leading corrections ─────────────────────────────────────

def test_wsv_leading_correction_keys():
    result = wsv_leading_correction()
    assert "delta_dm31_sq_ev2" in result
    assert result["delta_dm31_sq_ev2"] > 0


def test_wsv_subleading_nonzero():
    subleading = wsv_subleading_correction()
    # The 1-3 sub-leading correction must be positive (non-zero contribution)
    assert subleading["delta_dm31_sq_ev2"] > 0


def test_wsv_total_correction():
    total = wsv_off_diagonal_correction_total()
    assert "total_delta_dm31_sq_ev2" in total
    assert total["total_delta_dm31_sq_ev2"] > 0
    assert "dominant_term" in total


# ─── DM31 projection after Step 1 ────────────────────────────────────────────

def test_dm31_step1_projection_keys():
    proj = dm31_step1_projection()
    for key in ["base_projection_ev2", "wsv_correction_ev2", "dm31_step1_ev2",
                "juno_value_ev2", "fractional_wsv_shift"]:
        assert key in proj


def test_dm31_step1_above_base():
    proj = dm31_step1_projection()
    assert proj["dm31_step1_ev2"] > proj["base_projection_ev2"]


def test_dm31_step1_toward_juno():
    proj = dm31_step1_projection()
    # Step 1 should move estimate toward JUNO (i.e., upward, since UM is below JUNO)
    gap_before = abs(JUNO_DM31 - proj["base_projection_ev2"])
    gap_after = abs(JUNO_DM31 - proj["dm31_step1_ev2"])
    assert gap_after < gap_before


def test_fractional_wsv_shift_positive():
    proj = dm31_step1_projection()
    assert proj["fractional_wsv_shift"] > 0


# ─── Tension after Step 1 ────────────────────────────────────────────────────

def test_tension_after_step1_keys():
    t = tension_after_step1()
    for key in ["tension_sigma_before", "tension_sigma_after", "improvement", "status"]:
        assert key in t


def test_tension_reduced():
    t = tension_after_step1()
    assert t["tension_sigma_after"] < t["tension_sigma_before"]


def test_tension_before_consistent_with_pillar544():
    t = tension_after_step1()
    # Pillar 544 reports 3.33σ tension at best-attempt level
    assert t["tension_sigma_before"] == pytest.approx(3.33, abs=0.15)


def test_improvement_positive():
    t = tension_after_step1()
    assert t["improvement"] > 0


# ─── Step 1 certificate ──────────────────────────────────────────────────────

def test_step1_certificate_keys():
    cert = step1_certificate()
    for key in ["pillar", "status", "step", "epistemic_delta",
                "what_is_claimed", "what_is_NOT_claimed", "toe_score_delta"]:
        assert key in cert


def test_step1_number():
    cert = step1_certificate()
    assert cert["step"] == 1


def test_toe_score_unchanged():
    cert = step1_certificate()
    assert cert["toe_score_delta"] == pytest.approx(0.0)


def test_what_is_not_claimed_not_empty():
    cert = step1_certificate()
    assert len(cert["what_is_NOT_claimed"]) >= 3


def test_architecture_limit_not_closed():
    cert = step1_certificate()
    # Step 1 alone does not close the architecture limit
    assert "not closed" in cert["what_is_NOT_claimed"][0].lower() or \
           "not" in cert["what_is_NOT_claimed"][0].lower()


# ─── STEP1_RESULT module-level dict ──────────────────────────────────────────

def test_step1_result_tension_improved():
    assert STEP1_RESULT["tension_after_sigma"] < STEP1_RESULT["tension_before_sigma"]


def test_step1_result_dm31_positive():
    assert STEP1_RESULT["dm31_step1_ev2"] > 0


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 548
    assert report["toe_score_delta"] == pytest.approx(0.0)
    assert report["parent_pillar"] == 544
    assert report["closure_step"] == 1
    assert 2 in report["remaining_steps"]
    assert 3 in report["remaining_steps"]
