# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.three_sector_cosmology import (
    three_sector_modifiers,
    three_sector_predictions,
    architecture_limit_delta_report,
)


def test_modifiers_are_reductive():
    m = three_sector_modifiers()
    assert 0.0 < m["modifier_as"] < 1.0
    assert 0.0 < m["modifier_r"] < 1.0
    assert 0.0 < m["modifier_wa"] < 1.0
    assert 0.0 < m["modifier_lambda_gap"] < 1.0


def test_predictions_reduce_but_not_resolve():
    pred = three_sector_predictions()
    assert pred["as_suppression_factor"] < 5.3
    assert pred["r_prediction"] < 0.0315
    assert pred["wa_prediction"] < 0.0
    assert pred["lambda_log10_gap"] < 55.0


def test_architecture_limits_still_open():
    rep = architecture_limit_delta_report()
    assert rep["resolved"]["AL1"] is False
    assert rep["resolved"]["AL2"] is False
    assert rep["resolved"]["AL3"] is False
    assert rep["resolved"]["AL4"] is False
    assert rep["status"] == "OPEN_GAP"
