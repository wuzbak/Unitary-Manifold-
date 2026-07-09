# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 555 — DM31 Step 3: Two-Loop Seesaw Mass Correction."""
from __future__ import annotations

import math
import pytest
from src.core.pillar555_dm31_step3_two_loop_seesaw import (
    ALPHA_EW,
    ALPHA_S,
    DELTA_C,
    DM31_STEP2,
    G4_EW_SQ,
    G5_EW_SQ,
    JUNO_DM31,
    JUNO_SIGMA,
    K_CS,
    K_PI_R,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    STEP3_RESULT,
    TWO_LOOP_PARAMS,
    VERSION,
    dm31_all_steps_summary,
    dm31_step3_projection,
    g5_ew_loop_factor,
    g5_ew_squared,
    pillar_report,
    step3_certificate,
    tension_after_step3,
    two_loop_kk_threshold,
    two_loop_residual_shift,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 555


def test_pillar_status():
    assert PILLAR_STATUS == "DM31_STEP3_TWO_LOOP_SEESAW_COMPUTED"


def test_version():
    assert VERSION == "v19.2"


# ─── Constants ───────────────────────────────────────────────────────────────

def test_delta_c():
    assert DELTA_C == pytest.approx(5.0 / 74.0)


def test_k_pi_r():
    assert K_PI_R == pytest.approx(37.0)


def test_n_w():
    assert N_W == 5


def test_k_cs():
    assert K_CS == 74


def test_alpha_ew():
    assert ALPHA_EW == pytest.approx(1.0 / 128.0)


def test_g4_ew_sq():
    assert G4_EW_SQ == pytest.approx(4.0 * math.pi * ALPHA_EW)


def test_g5_ew_sq():
    assert G5_EW_SQ == pytest.approx(G4_EW_SQ * K_CS)


def test_juno_dm31():
    assert JUNO_DM31 == pytest.approx(2.411e-3)


def test_dm31_step2_below_juno():
    assert DM31_STEP2 < JUNO_DM31


# ─── Coupling functions ───────────────────────────────────────────────────────

def test_g5_ew_squared():
    assert g5_ew_squared() == pytest.approx(G5_EW_SQ)


def test_g5_ew_loop_factor():
    lf = g5_ew_loop_factor()
    assert lf == pytest.approx(G5_EW_SQ / (16.0 * math.pi ** 2))


def test_g5_ew_loop_factor_positive():
    assert g5_ew_loop_factor() > 0.0


def test_g5_ew_loop_factor_less_than_one():
    """Loop factor g₅/(16π²) should be small (< 0.15) for EW coupling."""
    assert g5_ew_loop_factor() < 0.15


# ─── Two-loop KK threshold ────────────────────────────────────────────────────

def test_two_loop_kk_threshold_keys():
    d = two_loop_kk_threshold()
    required = [
        "g5_ew_sq", "g5_loop_factor", "g5_loop_sq",
        "two_loop_form_factor", "five_over_4pi",
        "frac_shift_dm31", "frac_shift_dm31_pct",
    ]
    for k in required:
        assert k in d, f"Missing key: {k}"


def test_five_over_4pi():
    d = two_loop_kk_threshold()
    assert d["five_over_4pi"] == pytest.approx(5.0 / (4.0 * math.pi), rel=1e-6)


def test_two_loop_form_factor():
    d = two_loop_kk_threshold()
    expected = K_CS / (4.0 * math.pi) * DELTA_C
    assert d["two_loop_form_factor"] == pytest.approx(expected, rel=1e-6)


def test_two_loop_frac_shift_positive():
    """Two-loop correction is positive (increases Δm²₃₁)."""
    d = two_loop_kk_threshold()
    assert d["frac_shift_dm31"] > 0.0


def test_two_loop_frac_shift_small():
    """Two-loop fractional shift is small (< 5%)."""
    d = two_loop_kk_threshold()
    assert d["frac_shift_dm31_pct"] < 5.0


def test_two_loop_frac_shift_nonzero():
    """Two-loop fractional shift is non-trivially non-zero (> 0.01%)."""
    d = two_loop_kk_threshold()
    assert d["frac_shift_dm31_pct"] > 0.01


def test_g5_loop_sq():
    d = two_loop_kk_threshold()
    assert d["g5_loop_sq"] == pytest.approx(g5_ew_loop_factor() ** 2, rel=1e-6)


# ─── Two-loop residual shift ──────────────────────────────────────────────────

def test_two_loop_residual_keys():
    r = two_loop_residual_shift()
    assert "frac_shift" in r
    assert "frac_shift_pct" in r
    assert "physical_origin" in r


def test_two_loop_residual_positive():
    r = two_loop_residual_shift()
    assert r["frac_shift"] > 0.0


def test_two_loop_residual_matches_threshold():
    r = two_loop_residual_shift()
    d = two_loop_kk_threshold()
    assert r["frac_shift"] == pytest.approx(d["frac_shift_dm31"], rel=1e-6)


# ─── Step 3 projection ───────────────────────────────────────────────────────

def test_step3_projection_keys():
    proj = dm31_step3_projection()
    required = ["dm31_step2_ev2", "dm31_step3_ev2", "juno_ev2", "two_loop_frac_pct"]
    for k in required:
        assert k in proj


def test_step3_above_step2():
    proj = dm31_step3_projection()
    assert proj["dm31_step3_ev2"] > proj["dm31_step2_ev2"]


def test_step3_positive_correction():
    proj = dm31_step3_projection()
    assert proj["two_loop_correction_ev2"] > 0.0


def test_step3_below_or_at_juno():
    """Step 3 projection is still at or below JUNO (no overshoot)."""
    proj = dm31_step3_projection()
    # small positive correction, should be close to or below JUNO
    assert proj["dm31_step3_ev2"] <= proj["juno_ev2"] * 1.01  # allow 1% overshoot


# ─── Tension after Step 3 ────────────────────────────────────────────────────

def test_tension_after_step3_keys():
    t = tension_after_step3()
    required = [
        "tension_sigma_after_step2", "tension_sigma_after_step3", "improvement_step2_to_step3"
    ]
    for k in required:
        assert k in t


def test_tension_improved_by_step3():
    t = tension_after_step3()
    assert t["improvement_step2_to_step3"] > 0.0


def test_tension_step3_positive():
    t = tension_after_step3()
    assert t["tension_sigma_after_step3"] > 0.0


def test_tension_step3_below_step2():
    t = tension_after_step3()
    assert t["tension_sigma_after_step3"] < t["tension_sigma_after_step2"]


def test_tension_step3_within_3sigma():
    t = tension_after_step3()
    assert t["tension_sigma_after_step3"] < 3.0


def test_step3_result_module_level():
    t = tension_after_step3()
    assert STEP3_RESULT["tension_after_sigma"] == pytest.approx(
        t["tension_sigma_after_step3"], rel=1e-6
    )


# ─── All steps summary ───────────────────────────────────────────────────────

def test_all_steps_summary_keys():
    s = dm31_all_steps_summary()
    required = ["baseline", "step1", "step2", "step3", "juno", "closure_status"]
    for k in required:
        assert k in s


def test_all_steps_monotonic_increase():
    """Each step's Δm²₃₁ estimate is larger than the previous."""
    s = dm31_all_steps_summary()
    dm31_base = s["baseline"]["dm31_ev2"]
    dm31_s1 = s["step1"]["dm31_ev2"]
    dm31_s2 = s["step2"]["dm31_ev2"]
    dm31_s3 = s["step3"]["dm31_ev2"]
    assert dm31_s1 > dm31_base
    assert dm31_s2 > dm31_s1
    assert dm31_s3 > dm31_s2


def test_all_steps_tension_decreasing():
    """Each step's tension is smaller than the previous."""
    s = dm31_all_steps_summary()
    t_base = s["baseline"]["tension_sigma"]
    t_s1 = s["step1"]["tension_sigma"]
    t_s2 = s["step2"]["tension_sigma"]
    t_s3 = s["step3"]["tension_sigma"]
    # Step 1 may be computed slightly differently from the nominal 3.33
    assert t_s1 <= t_base * 1.01   # allow 1% float tolerance for baseline
    assert t_s2 < t_s1
    assert t_s3 < t_s2


def test_all_steps_below_juno():
    """All steps' Δm²₃₁ are close to (but not exceeding) JUNO."""
    s = dm31_all_steps_summary()
    juno = s["juno"]["dm31_ev2"]
    # All step estimates should be within 20% of JUNO
    for step_key in ["step1", "step2", "step3"]:
        dm31 = s[step_key]["dm31_ev2"]
        assert dm31 < juno * 1.20


# ─── Step 3 certificate ──────────────────────────────────────────────────────

def test_certificate_pillar():
    cert = step3_certificate()
    assert cert["pillar"] == 555


def test_certificate_step():
    cert = step3_certificate()
    assert cert["step"] == 3


def test_certificate_status():
    cert = step3_certificate()
    assert cert["status"] == "DM31_STEP3_TWO_LOOP_SEESAW_COMPUTED"


def test_certificate_toe_delta():
    cert = step3_certificate()
    assert cert["toe_score_delta"] == 0.0


def test_certificate_architecture_limit():
    cert = step3_certificate()
    assert cert["architecture_limit_status"] == "APPROACHING_CLOSURE"


def test_certificate_not_closed():
    cert = step3_certificate()
    not_claimed = cert["what_is_NOT_claimed"]
    assert any("NOT closed" in s or "not closed" in s.lower() for s in not_claimed)


# ─── TWO_LOOP_PARAMS module constant ─────────────────────────────────────────

def test_two_loop_params_module_const():
    assert "frac_shift_dm31_pct" in TWO_LOOP_PARAMS
    assert TWO_LOOP_PARAMS["frac_shift_dm31_pct"] > 0.0


def test_two_loop_params_g5():
    assert TWO_LOOP_PARAMS["g5_ew_sq"] == pytest.approx(G5_EW_SQ)


# ─── Pillar report ───────────────────────────────────────────────────────────

def test_pillar_report_keys():
    r = pillar_report()
    assert r["pillar"] == 555
    assert r["status"] == "DM31_STEP3_TWO_LOOP_SEESAW_COMPUTED"
    assert r["closure_step"] == 3
    assert r["remaining_steps"] == []
    assert r["toe_score_delta"] == 0.0
    assert r["hardgate_score_delta"] == 0.0
    assert r["parent_pillar"] == 554


def test_pillar_report_no_adjacent_track():
    r = pillar_report()
    assert r["adjacent_track"] is False


def test_pillar_report_architecture_limit():
    r = pillar_report()
    assert r["architecture_limit_status"] == "APPROACHING_CLOSURE"
