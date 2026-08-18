# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 687 — Sprint X regression certificate."""
import pytest
from src.core.pillar687_sprint_x_regression_certificate import (
    SPRINT_X_PILLARS,
    NEXT_PILLAR_SLOT,
    TOE_SCORE,
    LEAN4_THEOREMS,
    sprint_x_regression_certificate,
)


def test_sprint_x_pillars():
    assert set(SPRINT_X_PILLARS) == {"682", "683", "684", "685", "686", "687"}

def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 688

def test_toe_score():
    assert abs(TOE_SCORE - 30.0) < 1e-6

def test_lean4_theorems():
    assert LEAN4_THEOREMS == 365

def test_regression_status():
    cert = sprint_x_regression_certificate()
    assert cert["status"] == "SPRINT_X_REGRESSION_PASSED"

def test_regression_all_passed():
    cert = sprint_x_regression_certificate()
    assert cert["all_passed"] is True

def test_regression_pillar_checks_all_pass():
    cert = sprint_x_regression_certificate()
    for check in cert["pillar_checks"]:
        assert check["passed"], (
            f"Pillar {check['pillar']} failed: expected {check['expected_status']}, "
            f"got {check['actual_status']}"
        )

def test_regression_toe_unchanged():
    cert = sprint_x_regression_certificate()
    assert abs(cert["toe_score"] - 30.0) < 1e-6

def test_regression_next_slot():
    cert = sprint_x_regression_certificate()
    assert cert["next_pillar_slot"] == 688

def test_regression_broken_test_fixed():
    cert = sprint_x_regression_certificate()
    assert cert["broken_test_fix"]["status"] == "FIXED"

def test_regression_honest_note():
    cert = sprint_x_regression_certificate()
    assert "ToE" in cert["honest_note"]
    assert "falsifier" in cert["honest_note"].lower()
