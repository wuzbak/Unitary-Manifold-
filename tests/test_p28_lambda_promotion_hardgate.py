# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for P28 promotion hardgate package."""
from __future__ import annotations

import pytest

from src.core.p28_lambda_promotion_hardgate import (
    CURRENT_TOE_SCORE,
    NON_ACTIONABLE_MEASUREMENT_GATED,
    P28_CURRENT_STATUS,
    P28_PROMOTION_DELTA,
    P28_TARGET_STATUS,
    TARGET_TOE_SCORE_MIN,
    evaluate_p28_promotion_candidate,
    p28_promotion_hardgate_report,
    p28_promotion_hardgate_summary,
)


def test_default_report_is_certified_non_promotion():
    report = p28_promotion_hardgate_report()
    assert report["all_gates_pass"] is False
    assert report["status_after"] == P28_CURRENT_STATUS
    assert report["toe_score_delta"] == pytest.approx(0.0, abs=1e-12)


def test_default_target_locked_but_not_met():
    report = p28_promotion_hardgate_report()
    assert report["target_locked"]["minimum_toe_score"] == pytest.approx(TARGET_TOE_SCORE_MIN, abs=1e-12)
    assert report["target_locked"]["is_met"] is False


def test_default_axiomzero_inputs_empty():
    report = p28_promotion_hardgate_report()
    assert report["axiomzero_pdg_inputs"] == []


def test_default_non_actionable_measurement_gated_list():
    report = p28_promotion_hardgate_report()
    assert tuple(report["non_actionable_measurement_gated"]) == NON_ACTIONABLE_MEASUREMENT_GATED


def test_candidate_can_promote_if_all_gates_pass():
    report = evaluate_p28_promotion_candidate(
        n_flux=61,
        has_explicit_selection_mechanism=True,
    )
    assert report["all_gates_pass"] is True
    assert report["status_after"] == P28_TARGET_STATUS
    assert report["toe_score_delta"] == pytest.approx(P28_PROMOTION_DELTA, abs=1e-12)
    assert report["toe_score_after"] == pytest.approx(CURRENT_TOE_SCORE + P28_PROMOTION_DELTA, abs=1e-12)
    assert report["target_locked"]["is_met"] is True


def test_candidate_fails_without_selection_mechanism():
    report = evaluate_p28_promotion_candidate(
        n_flux=70,
        has_explicit_selection_mechanism=False,
    )
    assert report["gates"]["gate4_falsifier_integrity_preserved"] is False
    assert report["all_gates_pass"] is False
    assert report["status_after"] == P28_CURRENT_STATUS


def test_candidate_fails_below_flux_threshold():
    report = evaluate_p28_promotion_candidate(
        n_flux=60,
        has_explicit_selection_mechanism=True,
    )
    assert report["gates"]["gate1_closure_evidence_n_flux_ge_required"] is False
    assert report["gates"]["gate2_robustness_sweep_spacing_pass"] is False
    assert report["all_gates_pass"] is False


def test_summary_matches_report():
    report = p28_promotion_hardgate_report()
    summary = p28_promotion_hardgate_summary()
    assert summary["parameter"] == "P28"
    assert summary["status_after"] == report["status_after"]
    assert summary["toe_score_delta"] == report["toe_score_delta"]
    assert summary["all_gates_pass"] == report["all_gates_pass"]

