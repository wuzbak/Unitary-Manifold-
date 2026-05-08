# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/p3_p5_hard_gate_evidence.py."""
from __future__ import annotations

from src.core.p3_p5_hard_gate_evidence import (
    HARD_GATE_THRESHOLD_PCT,
    p3_p5_hard_gate_evidence,
)


def test_hard_gate_threshold_constant():
    assert HARD_GATE_THRESHOLD_PCT == 5.0


def test_hard_gate_report_structure():
    report = p3_p5_hard_gate_evidence()
    for key in ("threshold_pct", "p5", "p3", "promotion_candidate", "status", "policy"):
        assert key in report


def test_hard_gate_substructures():
    report = p3_p5_hard_gate_evidence()
    for key in ("ws_i_gate_pass", "ws_i_residual_pct", "ws_v_residual_pct", "hard_gate_pass"):
        assert key in report["p5"]
    for key in ("ws_vi_residual_pct", "hard_gate_pass"):
        assert key in report["p3"]


def test_hard_gate_threshold_enforced():
    report = p3_p5_hard_gate_evidence()
    assert report["p5"]["ws_v_residual_pct"] < HARD_GATE_THRESHOLD_PCT
    assert report["p3"]["ws_vi_residual_pct"] < HARD_GATE_THRESHOLD_PCT


def test_status_matches_candidate_boolean():
    report = p3_p5_hard_gate_evidence()
    if report["promotion_candidate"]:
        assert "PROMOTION_CANDIDATE_READY" in report["status"]
    else:
        assert "HARD_GATE_NOT_MET" in report["status"]
