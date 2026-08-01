# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 629 — Book 30 F-theory DBP sync."""
import pytest
from src.core.pillar629_book30_ftheory_dbp_sync import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    BOOK_NUMBER,
    BOOK_TITLE,
    PILLARS_COVERED,
    SUBSTACK_POST,
    TESTS_ADDED_THIS_SPRINT,
    TOE_SCORE,
    book_summary,
    arxiv_sync_certificate,
    pillar_report,
)

NUMERIC_CHECKS = [
    ("PILLAR_NUMBER", PILLAR_NUMBER, 629),
    ("BOOK_NUMBER", BOOK_NUMBER, 30),
    ("TESTS_ADDED_THIS_SPRINT", TESTS_ADDED_THIS_SPRINT, 175),
    ("TOE_SCORE", TOE_SCORE, 30.0),
]

STRING_CHECKS = [
    ("PILLAR_STATUS", PILLAR_STATUS, "BOOK30_FTHEORY_DBP_COMPLETE_SYNC_CERTIFIED"),
    ("SUBSTACK_POST", SUBSTACK_POST, "#284 S03E062"),
]


@pytest.mark.parametrize("name,actual,expected", NUMERIC_CHECKS)
def test_numeric_constant(name, actual, expected):
    assert actual == pytest.approx(expected, rel=1e-10), f"{name} mismatch"


@pytest.mark.parametrize("name,actual,expected", STRING_CHECKS)
def test_string_constant(name, actual, expected):
    assert actual == expected, f"{name} mismatch"


def test_pillars_covered():
    assert PILLARS_COVERED == list(range(624, 629))
    assert len(PILLARS_COVERED) == 5


def test_book_summary_structure():
    summary = book_summary()
    assert summary["book_number"] == 30
    assert summary["adjacent_track"] is True
    assert summary["toe_score"] == 30.0
    assert summary["tests_added"] == TESTS_ADDED_THIS_SPRINT


def test_arxiv_sync_certificate():
    cert = arxiv_sync_certificate()
    assert cert["synchronized"] is True
    assert cert["arxiv_version"] == "v20.8"
    assert "honest_note" in cert


def test_pillar_report_structure():
    rpt = pillar_report()
    assert rpt["pillar"] == 629
    assert rpt["adjacent_track"] is True
    assert rpt["toe_score_delta"] == 0.0
    assert rpt["hardgate_score_delta"] == 0.0
    assert "book_summary" in rpt
    assert "arxiv_sync_certificate" in rpt
