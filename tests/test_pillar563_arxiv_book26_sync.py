# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 563 — Book 26 + arXiv v19.3 Sync Certificate."""
from __future__ import annotations

import pytest
from src.core.pillar563_arxiv_book26_sync import (
    ARXIV_SYNC,
    BOOK_26,
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPRINT_SUMMARY,
    TEST_COUNT_DELTA,
    VERSION,
    arxiv_abstract_draft,
    lean4_advancement,
    pillar_report,
    sprint_pillars,
    sync_certificate,
    toe_score_summary,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 563


def test_pillar_status():
    assert PILLAR_STATUS == "ARXIV_BOOK26_SYNC_V193_CERTIFIED"


def test_version():
    assert VERSION == "v19.3"


# ─── Constants ────────────────────────────────────────────────────────────────

def test_lean4_total():
    assert LEAN4_TOTAL == 173


def test_test_count_delta():
    assert TEST_COUNT_DELTA >= 150  # Sprint 1 ~200 tests


# ─── Sprint summary ───────────────────────────────────────────────────────────

def test_sprint_summary_five_pillars():
    assert len(SPRINT_SUMMARY) == 5


def test_sprint_summary_pillar_numbers():
    pillars = [p["pillar"] for p in SPRINT_SUMMARY]
    assert pillars == [559, 560, 561, 562, 563]


def test_sprint_summary_dm31_closure():
    p559 = SPRINT_SUMMARY[0]
    assert p559["pillar"] == 559
    assert "DM31" in p559["name"]
    assert p559["toe_delta"] == 0.5


def test_sprint_summary_subgap_a():
    p560 = SPRINT_SUMMARY[1]
    assert p560["lean4_new"] == 12


def test_sprint_summary_subgap_b():
    p561 = SPRINT_SUMMARY[2]
    assert p561["lean4_new"] == 11


def test_sprint_summary_subgap_c():
    p562 = SPRINT_SUMMARY[3]
    assert p562["lean4_new"] == 11


# ─── arXiv sync ───────────────────────────────────────────────────────────────

def test_arxiv_sync_previous():
    assert ARXIV_SYNC["previous_sync_pillar"] == 552
    assert ARXIV_SYNC["previous_sync_version"] == "v19.1"


def test_arxiv_sync_current():
    assert ARXIV_SYNC["current_sync_version"] == "v19.3"


def test_arxiv_sync_headlines():
    headlines = ARXIV_SYNC["headline_advances"]
    assert any("DM31" in h or "P17" in h for h in headlines)
    assert any("gen-1" in h or "AB" in h or "fermion" in h for h in headlines)


def test_arxiv_sync_lean4_added():
    assert ARXIV_SYNC["lean4_theorems_added"] == 173 - 109  # 64


# ─── Book 26 ─────────────────────────────────────────────────────────────────

def test_book_26_title():
    assert "Book 26" in BOOK_26["title"]
    assert "Closing" in BOOK_26["title"]


def test_book_26_chapters():
    assert BOOK_26["chapters"] >= 5


def test_book_26_has_file():
    assert BOOK_26["file"].endswith(".md")


def test_book_26_substack_posts():
    posts = BOOK_26["substack_posts"]
    assert "#268" in str(posts) or "268" in str(posts)
    assert "#269" in str(posts) or "269" in str(posts)


def test_book_26_themes():
    assert len(BOOK_26["themes"]) >= 3
    themes_text = " ".join(BOOK_26["themes"])
    assert "DM31" in themes_text or "closure" in themes_text.lower()


# ─── sprint_pillars ───────────────────────────────────────────────────────────

def test_sprint_pillars_totals():
    result = sprint_pillars()
    assert result["total_tests"] >= 150
    assert result["total_lean4_theorems_added"] == 34  # 12+11+11
    assert result["total_toe_delta"] == 0.5


def test_sprint_pillars_next_slot():
    result = sprint_pillars()
    assert result["next_pillar_slot"] == 564


def test_sprint_pillars_next_substack():
    result = sprint_pillars()
    assert "#270" in result["next_substack"]


# ─── lean4_advancement ───────────────────────────────────────────────────────

def test_lean4_advancement_before():
    adv = lean4_advancement()
    assert adv["before_sprint"] == 139


def test_lean4_advancement_after():
    adv = lean4_advancement()
    assert adv["after_sprint"] == 173


def test_lean4_advancement_new():
    adv = lean4_advancement()
    assert adv["new_theorems"] == 34


def test_lean4_advancement_np_bc1():
    adv = lean4_advancement()
    assert adv["np_bc1_total"] == 52


def test_lean4_advancement_files():
    adv = lean4_advancement()
    assert len(adv["new_files"]) == 3
    assert any("SubgapA" in f for f in adv["new_files"])
    assert any("SubgapB" in f for f in adv["new_files"])
    assert any("SubgapC" in f for f in adv["new_files"])


# ─── toe_score_summary ───────────────────────────────────────────────────────

def test_toe_score_before():
    score = toe_score_summary()
    assert score["before_v19_3"] == 28.5


def test_toe_score_after():
    score = toe_score_summary()
    assert score["after_v19_3"] == 29.0


def test_toe_score_delta():
    score = toe_score_summary()
    assert score["delta"] == 0.5


def test_toe_score_p17_upgrade():
    score = toe_score_summary()
    assert "ARCHITECTURE_LIMIT" in score["p17_status_before"]
    assert "DM31_CLOSED" in score["p17_status_after"]


# ─── arxiv_abstract_draft ────────────────────────────────────────────────────

def test_abstract_mentions_dm31():
    abstract = arxiv_abstract_draft()
    assert "Δm²₃₁" in abstract or "DM31" in abstract or "neutrino" in abstract.lower()


def test_abstract_mentions_lean4():
    abstract = arxiv_abstract_draft()
    assert "Lean" in abstract or "machine-verified" in abstract


def test_abstract_mentions_litebird():
    abstract = arxiv_abstract_draft()
    assert "LiteBIRD" in abstract


def test_abstract_mentions_juno():
    abstract = arxiv_abstract_draft()
    assert "JUNO" in abstract


def test_abstract_is_substantial():
    abstract = arxiv_abstract_draft()
    assert len(abstract) > 500


# ─── sync_certificate ────────────────────────────────────────────────────────

def test_sync_cert_version():
    cert = sync_certificate()
    assert cert["version"] == "v19.3"


def test_sync_cert_next_pillar():
    cert = sync_certificate()
    assert cert["next_pillar_slot"] == 564


def test_sync_cert_ledgers():
    cert = sync_certificate()
    ledgers = cert["canonical_ledgers_updated"]
    assert "STATUS.md" in ledgers
    assert "README.md" in ledgers


def test_sync_cert_substack_posts():
    cert = sync_certificate()
    posts = str(cert["substack_posts_created"])
    assert "268" in posts
    assert "269" in posts


# ─── pillar_report ────────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version",
                "sprint_summary", "lean4_advancement",
                "toe_score", "sync_certificate"]:
        assert key in report


def test_pillar_report_toe_delta_zero():
    report = pillar_report()
    assert report["toe_score_delta"] == 0.0


def test_pillar_report_not_adjacent():
    report = pillar_report()
    assert report["adjacent_track"] is False
