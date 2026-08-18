# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 691 — CKM Jarlskog hardgate assessment."""
from __future__ import annotations

import pytest

from src.core.pillar691_ckm_jarlskog_hardgate_assessment import (
    ckm_hardgate_assessment,
    jarlskog_hardgate_verdict,
    sprint_y_summary,
)


@pytest.fixture(scope="module")
def assessment():
    return ckm_hardgate_assessment()


@pytest.fixture(scope="module")
def verdict():
    return jarlskog_hardgate_verdict()


@pytest.fixture(scope="module")
def summary():
    return sprint_y_summary()


def test_assessment_is_dict(assessment):
    assert isinstance(assessment, dict)


def test_assessment_status(assessment):
    assert assessment["status"] == "CKM_HARDGATE_ASSESSED"


def test_rho_bar_fails(assessment):
    assert assessment["rho_bar"]["passes_5_percent"] is False


def test_rho_bar_gap_value(assessment):
    assert assessment["rho_bar"]["gap_percent"] == pytest.approx(39.5506113051, abs=1e-8)


def test_eta_bar_passes(assessment):
    assert assessment["eta_bar"]["passes_5_percent"] is True


def test_eta_bar_gap_value(assessment):
    assert assessment["eta_bar"]["gap_percent"] == pytest.approx(1.8684413165, abs=1e-8)


def test_jcp_passes(assessment):
    assert assessment["J_CP"]["passes_5_percent"] is True


def test_jcp_gap_value(assessment):
    assert assessment["J_CP"]["gap_percent"] == pytest.approx(2.9157932117, abs=1e-8)


def test_overall_pass_false(assessment):
    assert assessment["overall_pass"] is False


def test_verdict_is_dict(verdict):
    assert isinstance(verdict, dict)


def test_verdict_architecture_limit(verdict):
    assert verdict["overall_verdict"] == "ARCHITECTURE_LIMIT"


def test_verdict_only_rho_fails(verdict):
    assert verdict["failing_observables"] == ["rho_bar"]


def test_verdict_eta_and_j_pass(verdict):
    assert set(verdict["passing_observables"]) == {"eta_bar", "J_CP"}


def test_verdict_rule_is_5_percent(verdict):
    assert verdict["hardgate_rule_percent"] == 5.0


def test_summary_is_dict(summary):
    assert isinstance(summary, dict)


def test_summary_sprint_name(summary):
    assert summary["sprint"] == "Sprint Y"


def test_summary_status(summary):
    assert summary["status"] == "ARCHITECTURE_LIMIT"


def test_summary_embeds_assessment(summary, assessment):
    assert summary["assessment"]["rho_bar"]["gap_percent"] == pytest.approx(assessment["rho_bar"]["gap_percent"])


def test_summary_embeds_verdict(summary, verdict):
    assert summary["verdict"]["overall_verdict"] == verdict["overall_verdict"]


def test_summary_note_mentions_eta_and_j(summary):
    note = summary["honest_note"].lower()
    assert "eta" in note and "j_cp" in note
