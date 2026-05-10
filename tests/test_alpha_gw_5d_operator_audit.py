# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for the α_GW 5D operator audit."""

from __future__ import annotations

import pytest

from src.core.alpha_gw_5d_operator_audit import (
    ALPHA_GW_TARGET_LOWER,
    ALPHA_GW_TARGET_UPPER,
    audit_current_rs1_transfer_law,
    alpha_gw_5d_operator_assessment,
    evaluate_candidate_5d_closure_lanes,
    freeze_5d_only_target,
    separate_alpha_gw_closure_problems,
)


def test_frozen_target_retains_rs1_baseline_and_interval():
    result = freeze_5d_only_target()
    low, high = result["alpha_gw_target_interval"]
    assert result["status"] == "TARGET_FROZEN"
    assert result["rs1_only_alpha_gw"] > 0.0
    assert result["rs1_only_alpha_gw"] < ALPHA_GW_TARGET_LOWER
    assert low == pytest.approx(ALPHA_GW_TARGET_LOWER)
    assert high == pytest.approx(ALPHA_GW_TARGET_UPPER)


def test_problem_split_keeps_absolute_scale_and_transfer_law_separate():
    result = separate_alpha_gw_closure_problems()
    assert result["problem_a_absolute_scale"]["same_decade_as_target"] is True
    assert result["problem_a_absolute_scale"]["derived_purely_in_5d"] is False
    assert result["problem_b_transfer_law"]["gap_to_target_log10"] > 50.0


def test_transfer_law_audit_rejects_present_bulk_identification():
    result = audit_current_rs1_transfer_law()
    assert result["present_bulk_transfer_viable"] is False
    assert result["required_enhancement_log10"] > 50.0
    assert result["radion_residual_log10"] > 5.0
    assert result["topological_residual_log10"] > 40.0


def test_candidate_lanes_identify_induced_gravity_as_best_but_not_pure_5d():
    result = evaluate_candidate_5d_closure_lanes()
    lanes = {lane["lane"]: lane for lane in result["lanes"]}
    assert result["best_lane"] == "induced_gravity_uv_localized"
    assert result["best_lane_requires_non_5d_input"] is True
    assert result["any_pure_5d_full_closure"] is False
    assert lanes["induced_gravity_uv_localized"]["numerically_viable"] is True
    assert lanes["induced_gravity_uv_localized"]["full_5d_closure"] is False
    assert lanes["radion_normalization"]["numerically_viable"] is False
    assert lanes["topological_anomaly"]["numerically_viable"] is False


def test_full_assessment_reports_operator_reclassification_without_5d_closure():
    result = alpha_gw_5d_operator_assessment()
    assert result["status"] == "OPERATOR_RECLASSIFICATION_NEEDED_BUT_NOT_CLOSED_IN_5D"
    assert result["present_transfer_law_survives"] is False
    assert result["best_candidate_lane"] == "induced_gravity_uv_localized"
    assert result["best_candidate_requires_non_5d_input"] is True
    assert result["any_pure_5d_full_closure"] is False
