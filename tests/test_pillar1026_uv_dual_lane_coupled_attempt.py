# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 1026 — UV dual-lane coupled attempt."""

from src.core.pillar1026_uv_dual_lane_coupled_attempt import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SHARED_UV_OBJECT,
    pillar1026_summary,
    uv_dual_lane_coupled_attempt,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1026
    assert PILLAR_GATE == "UV_DUAL_LANE_COUPLED_ATTEMPT"
    assert PILLAR_STATUS == "UV_DUAL_LANE_COUPLED_ATTEMPT_COMPLETE"
    assert PILLAR_VALID is True


def test_guardrails_and_residual_deltas() -> None:
    report = uv_dual_lane_coupled_attempt()
    assert report["shared_uv_object"] == SHARED_UV_OBJECT
    assert report["per_lane_rescue_parameters_added"] == 0
    assert report["coupled_only_guard"] is True
    deltas = report["before_after_residuals"]
    assert deltas["alpha_s_after"] <= deltas["alpha_s_before"]
    assert deltas["higgs_after"] <= deltas["higgs_before"]


def test_summary() -> None:
    summary = pillar1026_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True
