# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 616 — Book 29 + arXiv v20.6 sync."""
from __future__ import annotations

import pytest

from src.core.pillar616_book29_arxiv_v206_sync import (
    ARXIV_VERSION,
    BOOK_NUMBER,
    BOOK_TITLE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    PILLARS_COVERED,
    SUBSTACK_POST,
    TESTS_ADDED_THIS_SPRINT,
    TOE_SCORE,
    VERSION,
    arxiv_sync_certificate,
    book_summary,
    pillar_report,
)

BOOK = book_summary()
CERT = arxiv_sync_certificate()
REPORT = pillar_report()

NUMERIC_CHECKS = [
    BOOK_NUMBER == 29,
    TOE_SCORE == 30.0,
    TESTS_ADDED_THIS_SPRINT == 150,
    PILLARS_COVERED == list(range(613, 616)),
    len(PILLARS_COVERED) == 3,
    CERT["synchronized"] is True,
]

STRING_CHECKS = [
    PILLAR_STATUS == "BOOK29_ARXIV_V206_SYNC_CERTIFIED",
    "Book 29" in PILLAR_TITLE,
    VERSION == "v20.6",
    ARXIV_VERSION == "v20.6",
    SUBSTACK_POST == "#282 S03E060",
    "DM21" in BOOK_TITLE,
    REPORT["adjacent_track"] is False,
]


def test_identity() -> None:
    assert PILLAR_NUMBER == 616
    assert PILLAR_STATUS == "BOOK29_ARXIV_V206_SYNC_CERTIFIED"


def test_toe_score_is_30() -> None:
    assert abs(TOE_SCORE - 30.0) < 1e-9


def test_pillars_covered() -> None:
    assert 613 in PILLARS_COVERED
    assert 615 in PILLARS_COVERED


@pytest.mark.parametrize("ok", NUMERIC_CHECKS)
def test_numeric_checks(ok: bool) -> None:
    assert ok


@pytest.mark.parametrize("ok", STRING_CHECKS)
def test_string_checks(ok: bool) -> None:
    assert ok
