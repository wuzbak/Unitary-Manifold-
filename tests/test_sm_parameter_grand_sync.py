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


def test_p6_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P6"]["status"]


def test_p7_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P7"]["status"]


def test_p8_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P8"]["status"]


def test_p9_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P9"]["status"]


def test_p10_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P10"]["status"]


def test_p11_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P11"]["status"]


def test_p16_status_geometric_prediction():
    assert "GEOMETRIC PREDICTION" in PARAM_UPDATES["P16"]["status"]


def test_p19_status_constrained():
    assert "CONSTRAINED" in PARAM_UPDATES["P19"]["status"]


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
    assert score["open_count"] == 0


def test_score_has_fitted_count(score):
    assert "fitted_count" in score


def test_score_fitted_count_zero(score):
    assert score["fitted_count"] == 0


def test_score_has_total(score):
    assert "total" in score


def test_score_total_is_26(score):
    assert score["total"] == 26


def test_score_derived_count(score):
    assert score["derived_count"] == 8


def test_score_geometric_prediction_count(score):
    assert score["geometric_prediction_count"] == 11


def test_score_constrained_count(score):
    assert score["constrained_count"] == 4


def test_score_fraction_geometrically_anchored(score):
    assert abs(score["fraction_geometrically_anchored"] - 1.0) < 1e-10


def test_score_fraction_gt_07(score):
    assert score["fraction_geometrically_anchored"] > 0.7


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
