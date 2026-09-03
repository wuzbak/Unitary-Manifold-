# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 999 — CMB amplitude calibration/prediction boundary."""
from __future__ import annotations

import pytest

from src.core.pillar999_cmb_amplitude_calibration_boundary import (
    CMB_AMPLITUDE_TARGET,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    REQUIRED_RECOVERY_FACTOR,
    calibration_prediction_boundary,
    cmb_amplitude_evidence_ledger,
    pillar999_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 999
    assert PILLAR_GATE == "CMB_AMPLITUDE_CALIBRATION_PREDICTION_BOUNDARY"
    assert PILLAR_STATUS == "CMB_AMP_CALIBRATION_BOUNDARY_COMPLETE"
    assert PILLAR_VALID is True


def test_calibration_is_not_prediction() -> None:
    result = calibration_prediction_boundary()
    assert result["external_target_used"] is True
    assert result["pivot_amplitude_calibrated"] is True
    assert result["pivot_amplitude_predicted"] is False
    assert result["calibrated_not_predicted"] is True
    assert result["closure_claimed"] is False


def test_lambda_scales_with_external_target() -> None:
    result = calibration_prediction_boundary()
    assert result["lambda_scales_with_target"] is True
    assert result["target_doubling_lambda_ratio"] == pytest.approx(2.0)


def test_rejects_nonpositive_target() -> None:
    with pytest.raises(ValueError, match="positive"):
        calibration_prediction_boundary(0.0)


def test_evidence_ledger_keeps_terminal_limit_explicit() -> None:
    ledger = cmb_amplitude_evidence_ledger()
    assert ledger["terminal_eft_routes"] is True
    assert ledger["status"] == "CONFIRMED_IRREDUCIBLE"
    assert len(ledger["mechanisms"]) == 4
    assert all(row["terminal"] for row in ledger["mechanisms"])
    assert ledger["recovery_factor_required"] == REQUIRED_RECOVERY_FACTOR


def test_evidence_ledger_links_residual_budget_registry() -> None:
    budget = cmb_amplitude_evidence_ledger()["residual_budget"]
    assert budget["lane"] == "CMB_AMP"
    assert budget["normalized"] is True
    assert budget["has_registry_row"] is True
    assert budget["eft_exhausted"] == pytest.approx(0.85)
    assert budget["uv_missing"] == pytest.approx(0.15)


def test_summary_is_valid_but_not_a_closure_claim() -> None:
    summary = pillar999_summary()
    assert summary["valid"] is True
    assert summary["calibration_boundary"]["closure_claimed"] is False
    assert "not an A_s prediction" in summary["honest_verdict"]
    assert CMB_AMPLITUDE_TARGET > 0.0
