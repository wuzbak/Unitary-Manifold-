# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 721 — Sprints Y–DD Master Regression Certificate."""
from __future__ import annotations

import pytest
from src.core.pillar721_sprints_y_through_dd_regression_cert import (
    SPRINT_CLUSTER_SUMMARY,
    all_sprint_summaries,
    sprint_y_through_dd_regression_cert,
)


# ---------------------------------------------------------------------------
# SPRINT_CLUSTER_SUMMARY structure
# ---------------------------------------------------------------------------

def test_summary_version():
    assert SPRINT_CLUSTER_SUMMARY["version"].startswith("v21")


def test_summary_has_six_sprints():
    assert len(SPRINT_CLUSTER_SUMMARY["sprints"]) == 6


def test_sprint_ids():
    ids = [s["id"] for s in SPRINT_CLUSTER_SUMMARY["sprints"]]
    assert ids == ["Y", "Z", "AA", "BB", "CC", "DD"]


def test_total_new_tests():
    assert SPRINT_CLUSTER_SUMMARY["total_new_tests"] == 486


def test_total_new_pillars():
    assert SPRINT_CLUSTER_SUMMARY["total_new_pillars"] == 33


def test_next_pillar_slot():
    assert SPRINT_CLUSTER_SUMMARY["next_pillar_slot"] == 722


def test_toe_score_unchanged():
    assert SPRINT_CLUSTER_SUMMARY["toe_score"] == "30.0/28"


def test_lean4_unchanged():
    assert SPRINT_CLUSTER_SUMMARY["lean4_total"] == 365


def test_regression_status_passed():
    assert SPRINT_CLUSTER_SUMMARY["regression_status"] == "PASSED"


# ---------------------------------------------------------------------------
# Per-sprint checks
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sprint_id,expected_pillars", [
    ("Y",  list(range(688, 693))),
    ("Z",  list(range(693, 698))),
    ("AA", list(range(698, 705))),
    ("BB", list(range(705, 711))),
    ("CC", list(range(711, 716))),
    ("DD", list(range(716, 721))),
])
def test_sprint_pillar_range(sprint_id, expected_pillars):
    sprints = {s["id"]: s for s in SPRINT_CLUSTER_SUMMARY["sprints"]}
    assert sprints[sprint_id]["pillars"] == expected_pillars


@pytest.mark.parametrize("sprint_id,min_tests", [
    ("Y",  100),
    ("Z",  80),
    ("AA", 80),
    ("BB", 60),
    ("CC", 40),
    ("DD", 80),
])
def test_sprint_test_counts(sprint_id, min_tests):
    sprints = {s["id"]: s for s in SPRINT_CLUSTER_SUMMARY["sprints"]}
    assert sprints[sprint_id]["new_tests"] >= min_tests


def test_all_sprints_have_key_result():
    for s in SPRINT_CLUSTER_SUMMARY["sprints"]:
        assert isinstance(s["key_result"], str) and len(s["key_result"]) > 20


# ---------------------------------------------------------------------------
# all_sprint_summaries()
# ---------------------------------------------------------------------------

def test_all_sprint_summaries_returns_list():
    result = all_sprint_summaries()
    assert isinstance(result, list)
    assert len(result) == 6


def test_all_sprint_summaries_keys():
    for s in all_sprint_summaries():
        for key in ("id", "pillars", "title", "new_tests", "status", "key_result"):
            assert key in s, f"Missing key '{key}' in sprint {s.get('id')}"


# ---------------------------------------------------------------------------
# sprint_y_through_dd_regression_cert()
# ---------------------------------------------------------------------------

def test_cert_returns_dict():
    cert = sprint_y_through_dd_regression_cert()
    assert isinstance(cert, dict)


def test_cert_pillar_number():
    cert = sprint_y_through_dd_regression_cert()
    assert cert["pillar"] == 721


def test_cert_sprints_covered():
    cert = sprint_y_through_dd_regression_cert()
    assert cert["sprints_covered"] == ["Y", "Z", "AA", "BB", "CC", "DD"]


def test_cert_pillars_covered_range():
    cert = sprint_y_through_dd_regression_cert()
    assert cert["pillars_covered"] == list(range(688, 721))


def test_cert_total_tests():
    cert = sprint_y_through_dd_regression_cert()
    assert cert["total_new_tests"] == 486


def test_cert_regression_passed():
    cert = sprint_y_through_dd_regression_cert()
    assert cert["regression_status"] == "PASSED"


def test_cert_all_statuses_valid():
    cert = sprint_y_through_dd_regression_cert()
    assert cert["all_statuses_valid"] is True


def test_cert_has_honest_note():
    cert = sprint_y_through_dd_regression_cert()
    assert "ARCHITECTURE_LIMIT" in cert["honest_note"]


def test_cert_next_pillar_slot():
    cert = sprint_y_through_dd_regression_cert()
    assert cert["next_pillar_slot"] == 722


def test_cert_per_sprint_count():
    cert = sprint_y_through_dd_regression_cert()
    assert len(cert["per_sprint"]) == 6
