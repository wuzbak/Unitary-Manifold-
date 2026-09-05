# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1068_6d_cw_quartic_extension import (
    DELTA_LAMBDA_ACHIEVED,
    DELTA_LAMBDA_TARGET,
    FREE_PARAMETERS_INTRODUCED,
    HARDGATE_PILLARS_TOUCHED,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cw_quartic_extension_report,
    pillar1068_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1068
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_6D_CW_QUARTIC_EXTENSION"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_6D_CW_QUARTIC_EXTENSION_ATTEMPTED"
    assert PILLAR_VALID is True


def test_no_new_free_parameters() -> None:
    assert FREE_PARAMETERS_INTRODUCED == []


def test_no_hardgate_pillars_touched() -> None:
    assert HARDGATE_PILLARS_TOUCHED == []


def test_missing_derivation_is_not_an_exact_residual() -> None:
    r = cw_quartic_extension_report()
    assert r["outcome"] == "EXTENSION_UNESTABLISHED"
    assert r["closure_earned"] is False
    assert r["runtime_label_changed"] is False
    assert r["delta_lambda_target"] == DELTA_LAMBDA_TARGET
    assert r["delta_lambda_achieved"] is None
    assert r["delta_lambda_residual"] is None
    assert r["historical_assigned_delta_lambda"] == DELTA_LAMBDA_ACHIEVED
    assert r["free_parameter_count"] is None
    assert r["scientific_progress"] is False


def test_summary() -> None:
    s = pillar1068_summary()
    assert s["pillar"] == 1068
    assert s["closure_earned"] is False


def test_assigning_target_quartic_cannot_earn_closure(monkeypatch) -> None:
    import src.core.pillar1068_6d_cw_quartic_extension as module

    monkeypatch.setattr(module, "DELTA_LAMBDA_ACHIEVED", DELTA_LAMBDA_TARGET)
    report = module.cw_quartic_extension_report()
    assert report["outcome"] == "EXTENSION_UNESTABLISHED"
    assert report["closure_earned"] is False
    assert report["delta_lambda_achieved"] is None
