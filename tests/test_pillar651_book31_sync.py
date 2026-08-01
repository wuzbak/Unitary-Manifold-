# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 651 — Book 31 + arXiv v20.9 sync."""
from __future__ import annotations

from src.core.pillar651_book31_arxiv_v209_sync import (
    ARXIV_VERSION,
    BOOK_NUMBER,
    LEAN4_TOTAL,
    PILLAR_COUNT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPRINT_SUMMARY,
    TOE_SCORE,
    VERSION,
    book_sync_certificate,
    pillar_report,
)

REPORT = pillar_report()
CERT = book_sync_certificate()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 651

    def test_status(self):
        assert "BOOK31" in PILLAR_STATUS or "SYNC" in PILLAR_STATUS

    def test_book_number(self):
        assert BOOK_NUMBER == 31

    def test_arxiv_version(self):
        assert ARXIV_VERSION == "v20.9"

    def test_pillar_count(self):
        assert PILLAR_COUNT >= 651


class TestSyncCertificate:
    def test_certified(self):
        assert CERT["certified"] is True

    def test_tiers_completed(self):
        for t in [1, 2, 3, 4, 5]:
            assert t in CERT["tiers_completed"]

    def test_sprints(self):
        for s in ["M", "N", "O", "P", "Q"]:
            assert s in CERT["sprints"]

    def test_synced_docs(self):
        assert len(CERT["synced_documents"]) >= 3


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0
