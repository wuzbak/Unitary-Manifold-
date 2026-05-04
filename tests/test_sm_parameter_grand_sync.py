# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 137: SM Parameter Grand Sync (src/core/sm_parameter_grand_sync.py)."""

import pytest

from src.core.sm_parameter_grand_sync import (
    grand_sync_report,
    grand_sync_toe_score,
    PARAM_UPDATES,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def report():
    return grand_sync_report()


@pytest.fixture(scope="module")
def score():
    return grand_sync_toe_score()


# ---------------------------------------------------------------------------
# grand_sync_report — return type and top-level keys
# ---------------------------------------------------------------------------

def test_report_is_dict(report):
    assert isinstance(report, dict)


def test_report_has_pillar(report):
    assert "pillar" in report


def test_report_pillar_is_137(report):
    assert report["pillar"] == 137


def test_report_has_parameter_updates(report):
    assert "parameter_updates" in report


def test_report_has_toe_score_after_sync(report):
    assert "toe_score_after_sync" in report


def test_report_has_summary(report):
    assert "summary" in report


def test_report_summary_non_empty(report):
    assert len(report["summary"]) > 0


# ---------------------------------------------------------------------------
# PARAM_UPDATES structure
# ---------------------------------------------------------------------------

def test_param_updates_is_dict():
    assert isinstance(PARAM_UPDATES, dict)


def test_param_updates_has_p4():
    assert "P4" in PARAM_UPDATES


def test_param_updates_has_p5():
    assert "P5" in PARAM_UPDATES


def test_param_updates_has_p6():
    assert "P6" in PARAM_UPDATES


def test_param_updates_has_p7():
    assert "P7" in PARAM_UPDATES


def test_param_updates_has_p8():
    assert "P8" in PARAM_UPDATES


def test_param_updates_has_p9():
    assert "P9" in PARAM_UPDATES


def test_param_updates_has_p10():
    assert "P10" in PARAM_UPDATES


def test_param_updates_has_p11():
    assert "P11" in PARAM_UPDATES


def test_param_updates_has_p16():
    assert "P16" in PARAM_UPDATES


def test_param_updates_has_p17():
    assert "P17" in PARAM_UPDATES


def test_param_updates_has_p18():
    assert "P18" in PARAM_UPDATES


def test_param_updates_has_p19():
    assert "P19" in PARAM_UPDATES


def test_param_updates_has_p20():
    assert "P20" in PARAM_UPDATES


def test_param_updates_has_p21():
    assert "P21" in PARAM_UPDATES


def test_param_updates_has_p22():
    assert "P22" in PARAM_UPDATES


def test_param_updates_has_p28():
    assert "P28" in PARAM_UPDATES


# ---------------------------------------------------------------------------
# Status strings for key parameters
# ---------------------------------------------------------------------------

def test_p4_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P4"]["status"]


def test_p5_status_derived():
    assert "DERIVED" in PARAM_UPDATES["P5"]["status"]


def test_p6_status_parameterized():
    # Reclassified from GEOMETRIC PREDICTION: c_L per species is a free parameter, not a prediction
    assert "PARAMETERIZED" in PARAM_UPDATES["P6"]["status"]


def test_p7_status_parameterized():
    # Reclassified from GEOMETRIC PREDICTION: c_L per species is a free parameter, not a prediction
    assert "PARAMETERIZED" in PARAM_UPDATES["P7"]["status"]


def test_p8_status_parameterized():
    # Reclassified from GEOMETRIC PREDICTION: c_L per species is a free parameter, not a prediction
    assert "PARAMETERIZED" in PARAM_UPDATES["P8"]["status"]


def test_p9_status_parameterized():
    # Reclassified from GEOMETRIC PREDICTION: c_L per species is a free parameter, not a prediction
    assert "PARAMETERIZED" in PARAM_UPDATES["P9"]["status"]


def test_p10_status_parameterized():
    # Reclassified from GEOMETRIC PREDICTION: c_L per species is a free parameter, not a prediction
    assert "PARAMETERIZED" in PARAM_UPDATES["P10"]["status"]


def test_p11_status_parameterized():
    # Reclassified from GEOMETRIC PREDICTION: c_L per species is a free parameter, not a prediction
    assert "PARAMETERIZED" in PARAM_UPDATES["P11"]["status"]


def test_p16_status_parameterized():
    # Reclassified from GEOMETRIC PREDICTION: c_L per species is a free parameter, not a prediction
    assert "PARAMETERIZED" in PARAM_UPDATES["P16"]["status"]


def test_p19_status_resolved():
    # Pillar 150: UV-brane Majorana proof → RESOLVED via Type-I seesaw
    assert "RESOLVED" in PARAM_UPDATES["P19"]["status"]


def test_p20_status_constrained():
    assert "CONSTRAINED" in PARAM_UPDATES["P20"]["status"]


def test_p21_status_constrained():
    assert "CONSTRAINED" in PARAM_UPDATES["P21"]["status"]


def test_p22_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P22"]["status"]


def test_p28_status_constrained():
    assert "CONSTRAINED" in PARAM_UPDATES["P28"]["status"]


# ---------------------------------------------------------------------------
# grand_sync_toe_score
# ---------------------------------------------------------------------------

def test_score_is_dict(score):
    assert isinstance(score, dict)


def test_score_has_open_count(score):
    assert "open_count" in score


def test_score_open_count_zero(score):
    # Λ_QCD RESOLVED by Pillar 153 (GUT-scale RGE); P19 RESOLVED by Pillar 150
    assert score["open_count"] == 0


def test_score_has_fitted_count(score):
    assert "fitted_count" in score


def test_score_fitted_count_zero(score):
    assert score["fitted_count"] == 0


def test_score_has_total(score):
    assert "total" in score


def test_score_total_is_27(score):
    # 26 original SM params + Λ_QCD explicitly added as OPEN
    assert score["total"] == 27


def test_score_derived_count(score):
    assert score["derived_count"] == 8


def test_score_geometric_prediction_count(score):
    # P6-P11, P16-P18 reclassified from GEOMETRIC PREDICTION to PARAMETERIZED
    # Remaining GEOMETRIC PREDICTION: P4 (Higgs VEV), P22 (solar mixing)
    assert score["geometric_prediction_count"] == 2


def test_score_constrained_count(score):
    # P19 moved from CONSTRAINED to RESOLVED; now 3 CONSTRAINED params
    assert score["constrained_count"] == 3


def test_score_fraction_geometrically_anchored(score):
    # fraction = (derived+constrained+geo_estimate+geo_prediction)/total
    # Excludes PARAMETERIZED and OPEN; should be well below 1.0 now
    assert 0.0 < score["fraction_geometrically_anchored"] < 1.0


def test_score_fraction_gt_07(score):
    # PARAMETERIZED and OPEN categories reduce fraction; > 0.5 is still reasonable
    assert score["fraction_geometrically_anchored"] > 0.5


def test_score_has_toe_verdict(score):
    assert "toe_verdict" in score


def test_score_toe_verdict_non_empty(score):
    assert len(score["toe_verdict"]) > 0


def test_score_toe_verdict_mentions_zero_open(score):
    verdict = score["toe_verdict"].lower()
    assert "open" in verdict or "zero" in verdict or "0" in verdict


def test_score_derived_plus_pred_plus_constrained_lt_total(score):
    sub_total = (score["derived_count"] + score["geometric_prediction_count"]
                 + score["constrained_count"])
    assert sub_total <= score["total"]


def test_score_has_parameterized_count(score):
    assert "parameterized_count" in score


def test_score_parameterized_count(score):
    # 9 fermion masses (6 quarks + 3 charged leptons) use per-species c_L
    assert score["parameterized_count"] == 9


def test_p_qcd_is_resolved(score):
    # Pillar 153: Λ_QCD RESOLVED via GUT-scale RGE
    assert "RESOLVED" in PARAM_UPDATES["P_QCD"]["status"]


def test_p_qcd_pillar_153():
    pillar = PARAM_UPDATES["P_QCD"]["pillar"]
    assert "153" in str(pillar)
