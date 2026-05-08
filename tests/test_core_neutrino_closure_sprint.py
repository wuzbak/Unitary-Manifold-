# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/neutrino_closure_sprint.py."""
from __future__ import annotations

from src.core.neutrino_closure_sprint import (
    SPRINT_VERSION,
    P17_RESIDUAL_PCT,
    P17_STATUS,
    P18_RESIDUAL_PCT,
    P18_STATUS,
    P20_RESIDUAL_PCT,
    P20_STATUS,
    SPRINT_TOE_DELTA,
    TOE_SCORE_BEFORE,
    TOE_SCORE_AFTER,
    neutrino_closure_sprint_certificate,
    sprint_summary,
)


def test_sprint_version():
    assert SPRINT_VERSION == "v10.27"


def test_p17_still_constrained():
    # P17 is still CONSTRAINED at 6.87% 2NLO (above 5% gate)
    assert P17_STATUS == "CONSTRAINED"
    assert P17_RESIDUAL_PCT > 5.0


def test_p18_promoted():
    assert P18_STATUS == "GEOMETRIC_PREDICTION"
    assert P18_RESIDUAL_PCT < 5.0


def test_p20_promoted():
    assert P20_STATUS == "GEOMETRIC_PREDICTION"
    assert P20_RESIDUAL_PCT < 5.0


def test_sprint_toe_delta():
    # P18 (+0.3) + P20 (+0.3) = +0.6
    assert abs(SPRINT_TOE_DELTA - 0.6) < 1e-10


def test_toe_scores():
    assert abs(TOE_SCORE_BEFORE - 18.9) < 1e-10
    assert abs(TOE_SCORE_AFTER - 19.5) < 1e-10


def test_certificate_structure():
    cert = neutrino_closure_sprint_certificate()
    assert cert["sprint"] == "v10.27"
    assert set(cert["parameters"].keys()) == {"P17", "P18", "P20"}
    assert cert["parameters"]["P17"]["promotion"] is False
    assert cert["parameters"]["P18"]["promotion"] is True
    assert cert["parameters"]["P20"]["promotion"] is True
    assert abs(cert["sprint_toe_delta"] - 0.6) < 1e-10
    assert abs(cert["toe_score_before"] - 18.9) < 1e-10
    assert abs(cert["toe_score_after"] - 19.5) < 1e-10


def test_certificate_p17_honest_note():
    cert = neutrino_closure_sprint_certificate()
    note = cert["parameters"]["P17"]["honest_note"]
    assert "6.87%" in note or "2NLO" in note


def test_certificate_policy():
    cert = neutrino_closure_sprint_certificate()
    assert cert["policy"]["promotion_policy"] == "hardgate_only"
    assert cert["policy"]["mas_reopen_allowed"] is False


def test_sprint_summary_promoted_list():
    summary = sprint_summary()
    assert "P18" in summary["promoted_parameters"]
    assert "P20" in summary["promoted_parameters"]
    assert "P17" in summary["constrained_parameters"]


def test_sprint_summary_score_consistency():
    summary = sprint_summary()
    assert abs(summary["toe_score_after"] - summary["toe_score_before"] - summary["sprint_toe_delta"]) < 1e-10
