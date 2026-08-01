# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 594 — Book 28 arXiv sync."""
from __future__ import annotations

import pytest

from src.core.pillar594_book28_arxiv_v201_sync import (
    ARXIV_VERSION,
    BOOK_NUMBER,
    BOOK_TITLE,
    PILLARS_COVERED,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    TESTS_ADDED_THIS_SPRINT,
    VERSION,
    arxiv_sync_certificate,
    book_summary,
    pillar_report,
)

PRIMARY = arxiv_sync_certificate()
REPORT = pillar_report()

PRIMARY_KEYS = ["pillar", "status", "book_number", "arxiv_version", "pillars_covered", "synchronized"]
REPORT_KEYS = ["pillar", "title", "status", "version", "adjacent_track", "book_summary", "arxiv_sync_certificate", "toe_score_delta"]
NUMERIC_CHECKS = [
    BOOK_NUMBER == 28,
    PILLARS_COVERED == [591, 592, 593],
    TESTS_ADDED_THIS_SPRINT == 150,
    book_summary()["tests_added"] == TESTS_ADDED_THIS_SPRINT,
    PRIMARY["book_number"] == BOOK_NUMBER,
    REPORT["hardgate_score_delta"] == 0.0,
]
STRING_CHECKS = [
    PILLAR_STATUS == "BOOK28_ARXIV_V201_SYNC_CERTIFIED",
    ARXIV_VERSION == "v20.1",
    BOOK_TITLE == "DM21 Approaching Closure + v20.2 Cascade",
    "Book 28" in PILLAR_TITLE,
    PRIMARY["synchronized"] is True,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 594
    assert PILLAR_STATUS == "BOOK28_ARXIV_V201_SYNC_CERTIFIED"



def test_constants() -> None:
    assert VERSION == "v20.2"
    assert len(PILLARS_COVERED) == 3
    assert PILLARS_COVERED[0] == 591


@pytest.mark.parametrize("key", PRIMARY_KEYS)
def test_primary_keys(key: str) -> None:
    assert key in PRIMARY


@pytest.mark.parametrize("key", REPORT_KEYS)
def test_report_keys(key: str) -> None:
    assert key in REPORT


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
