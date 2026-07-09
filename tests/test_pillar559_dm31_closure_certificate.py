# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 559 — DM31 Formal Closure Certificate."""
from __future__ import annotations

import pytest
from src.core.pillar559_dm31_closure_certificate import (
    DM31_CLOSURE_VERDICT,
    DM31_CORRECTION_CASCADE,
    DM31_JUNO_MEASUREMENT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TOE_SCORE_DELTA,
    VERSION,
    closure_certificate,
    compute_final_tension,
    correction_cascade_summary,
    formal_closure_conditions,
    juno_phase2_prediction,
    pillar_report,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 559


def test_pillar_status():
    assert PILLAR_STATUS == "DM31_CLOSED_THREE_STEP_CASCADE"


def test_version():
    assert VERSION == "v19.3"


def test_toe_score_delta():
    assert TOE_SCORE_DELTA == 0.5


# ─── JUNO measurement ────────────────────────────────────────────────────────

def test_juno_measurement_central_value():
    assert abs(DM31_JUNO_MEASUREMENT["value_eV2"] - 2.411e-3) < 1e-7


def test_juno_measurement_sigma():
    # ~0.81% of 2.411e-3
    sigma = DM31_JUNO_MEASUREMENT["sigma_eV2"]
    assert 0.010e-3 < sigma < 0.030e-3


def test_juno_closure_threshold():
    assert DM31_JUNO_MEASUREMENT["tension_threshold_sigma"] == 1.0


# ─── Correction cascade ───────────────────────────────────────────────────────

def test_cascade_has_three_steps():
    assert len(DM31_CORRECTION_CASCADE) == 3


def test_cascade_step_1_pillar():
    assert DM31_CORRECTION_CASCADE[0]["pillar"] == 548


def test_cascade_step_2_pillar():
    assert DM31_CORRECTION_CASCADE[1]["pillar"] == 554


def test_cascade_step_3_pillar():
    assert DM31_CORRECTION_CASCADE[2]["pillar"] == 555


def test_cascade_step_1_correction():
    # WS-V correction ~5% central
    correction = DM31_CORRECTION_CASCADE[0]["correction_percent"]
    assert 2.0 <= correction <= 8.0


def test_cascade_step_2_correction():
    # ν_R orbifold BC +0.40%
    correction = DM31_CORRECTION_CASCADE[1]["correction_percent"]
    assert abs(correction - 0.40) < 0.05


def test_cascade_step_3_correction():
    # Two-loop seesaw +0.169%
    correction = DM31_CORRECTION_CASCADE[2]["correction_percent"]
    assert abs(correction - 0.169) < 0.05


def test_cascade_all_executed():
    statuses = [s["status"] for s in DM31_CORRECTION_CASCADE]
    assert all(s == "EXECUTED" for s in statuses)


def test_step_1_tension_reduction():
    # Step 1 should reduce tension from 3.33σ toward ~2.9σ
    t_after = DM31_CORRECTION_CASCADE[0]["tension_sigma_after"]
    assert t_after < 3.33


def test_step_2_tension_below_1sigma():
    # After step 2, tension should be well below 1σ
    t_after = DM31_CORRECTION_CASCADE[1]["tension_sigma_after"]
    assert t_after < 1.0


def test_step_3_tension_near_zero():
    # After step 3, tension should be very small
    t_after = DM31_CORRECTION_CASCADE[2]["tension_sigma_after"]
    assert t_after < 0.5


# ─── Closure verdict ─────────────────────────────────────────────────────────

def test_closure_verdict():
    assert DM31_CLOSURE_VERDICT["verdict"] == "DM31_CLOSED"


def test_closure_verdict_initial_tension():
    assert abs(DM31_CLOSURE_VERDICT["initial_tension_sigma"] - 3.33) < 0.01


def test_closure_verdict_final_tension():
    t = DM31_CLOSURE_VERDICT["final_tension_sigma"]
    assert t < 1.0  # within measurement uncertainty


def test_closure_verdict_condition_met():
    assert DM31_CLOSURE_VERDICT["closure_condition_met"] is True


def test_closure_verdict_epistemic():
    assert DM31_CLOSURE_VERDICT["epistemic_status"] == "CONDITIONAL_DERIVATION"


def test_closure_verdict_has_conditions():
    assert len(DM31_CLOSURE_VERDICT["conditions"]) >= 3


# ─── compute_final_tension ───────────────────────────────────────────────────

def test_final_tension_value():
    result = compute_final_tension()
    assert result["tension_sigma"] < 1.0


def test_final_tension_within_1sigma():
    result = compute_final_tension()
    assert result["within_1sigma"] is True


def test_final_tension_verdict():
    result = compute_final_tension()
    assert result["verdict"] == "CLOSED"


def test_final_tension_estimate_close_to_juno():
    result = compute_final_tension()
    # Final estimate should be within 0.5% of JUNO
    juno = result["juno_measurement_eV2"]
    est = result["final_estimate_eV2"]
    assert abs(est - juno) / juno < 0.005


def test_final_tension_residual_small():
    result = compute_final_tension()
    assert result["residual_percent"] < 1.0


def test_final_tension_keys():
    result = compute_final_tension()
    for key in ["juno_measurement_eV2", "final_estimate_eV2", "residual_eV2",
                "residual_percent", "tension_sigma", "within_1sigma", "verdict"]:
        assert key in result


# ─── correction_cascade_summary ──────────────────────────────────────────────

def test_cascade_summary_length():
    summary = correction_cascade_summary()
    assert len(summary) == 3


def test_cascade_summary_cumulative_positive():
    summary = correction_cascade_summary()
    for item in summary:
        assert item["cumulative_correction_percent"] > 0


def test_cascade_summary_cumulative_monotone():
    summary = correction_cascade_summary()
    cumulative = [item["cumulative_correction_percent"] for item in summary]
    assert cumulative[0] < cumulative[1] < cumulative[2]


def test_cascade_summary_step_numbers():
    summary = correction_cascade_summary()
    assert [item["step"] for item in summary] == [1, 2, 3]


# ─── formal_closure_conditions ───────────────────────────────────────────────

def test_formal_closure_overall():
    conditions = formal_closure_conditions()
    assert conditions["overall_closure"] is True


def test_formal_closure_tension_condition():
    conditions = formal_closure_conditions()
    assert conditions["condition_1"]["satisfied"] is True


def test_formal_closure_steps_condition():
    conditions = formal_closure_conditions()
    assert conditions["condition_2"]["satisfied"] is True


def test_formal_closure_architecture_condition():
    conditions = formal_closure_conditions()
    assert conditions["condition_3"]["satisfied"] is True


# ─── juno_phase2_prediction ──────────────────────────────────────────────────

def test_juno_phase2_has_prediction():
    pred = juno_phase2_prediction()
    assert "predicted_phase2_tension" in pred


def test_juno_phase2_improvement_factor():
    pred = juno_phase2_prediction()
    assert pred["juno_phase2_projected_sigma_improvement"] == 3.0


def test_juno_phase2_tension_reduced():
    pred = juno_phase2_prediction()
    assert pred["predicted_phase2_tension"] < pred["juno_phase1_tension"]


def test_juno_phase2_preregistered():
    pred = juno_phase2_prediction()
    assert pred["prediction_status"] == "PREREGISTERED"


def test_juno_phase2_falsification_condition():
    pred = juno_phase2_prediction()
    assert "falsification_condition" in pred
    assert "JUNO" in pred["falsification_condition"]


# ─── closure_certificate ─────────────────────────────────────────────────────

def test_closure_certificate_all_conditions():
    cert = closure_certificate()
    assert cert["all_conditions_met"] is True


def test_closure_certificate_toe_delta():
    cert = closure_certificate()
    assert cert["toe_score_delta"] == 0.5


def test_closure_certificate_p17_new_label():
    cert = closure_certificate()
    assert "DM31_CLOSED" in cert["p17_new_label"]


def test_closure_certificate_tension_before():
    cert = closure_certificate()
    assert abs(cert["tension_before_sigma"] - 3.33) < 0.01


def test_closure_certificate_tension_after():
    cert = closure_certificate()
    assert cert["tension_after_sigma"] < 1.0


def test_closure_certificate_reduction_factor():
    cert = closure_certificate()
    assert cert["reduction_factor"] >= 10.0  # 3.33 / 0.12 ≈ 28


def test_closure_certificate_has_claims():
    cert = closure_certificate()
    assert len(cert["what_is_claimed"]) >= 4


def test_closure_certificate_has_anti_claims():
    cert = closure_certificate()
    assert len(cert["what_is_NOT_claimed"]) >= 3


def test_closure_certificate_status_before():
    cert = closure_certificate()
    assert "ARCHITECTURE_LIMIT" in cert["status_before"]


def test_closure_certificate_status_after():
    cert = closure_certificate()
    assert "DM31_CLOSED" in cert["status_after"]


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version",
                "final_tension", "closure_certificate", "toe_score_delta"]:
        assert key in report


def test_pillar_report_toe_delta():
    report = pillar_report()
    assert report["toe_score_delta"] == 0.5


def test_pillar_report_hardgate_no_change():
    report = pillar_report()
    assert report["hardgate_score_delta"] == 0.0


def test_pillar_report_not_adjacent():
    report = pillar_report()
    assert report["adjacent_track"] is False


def test_pillar_report_parent_pillars():
    report = pillar_report()
    assert 544 in report["parent_pillars"]
    assert 555 in report["parent_pillars"]
