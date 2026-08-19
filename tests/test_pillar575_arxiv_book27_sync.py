# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 575 — Book 27 + arXiv v20.0 Sync Certificate."""
from __future__ import annotations

import pytest
from pathlib import Path
from src.core.pillar575_arxiv_book27_sync import (
    ARXIV_SYNC,
    BOOK_27,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPRINT_V19_4,
    SPRINT_V20_0,
    TEST_COUNT_DELTA,
    TOE_SCORE_AT_SYNC,
    VERSION,
    arxiv_abstract_draft,
    lean4_advancement,
    pillar_report,
    sync_certificate,
    sync_covers,
    toe_score_summary,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 575


def test_pillar_status():
    assert PILLAR_STATUS == "ARXIV_BOOK27_SYNC_V200_CERTIFIED"


def test_pillar_title_contains_book27():
    assert "Book 27" in PILLAR_TITLE or "arXiv" in PILLAR_TITLE


def test_version():
    assert VERSION == "v20.1"


def test_lean4_total():
    assert LEAN4_TOTAL == 240


def test_test_count_delta_positive():
    assert TEST_COUNT_DELTA > 0


# ─── ARXIV_SYNC ───────────────────────────────────────────────────────────────

def test_arxiv_sync_previous_pillar():
    assert ARXIV_SYNC["previous_sync_pillar"] == 563


def test_arxiv_sync_previous_version():
    assert ARXIV_SYNC["previous_sync_version"] == "v19.3"


def test_arxiv_sync_current_version():
    assert ARXIV_SYNC["current_sync_version"] == "v20.0"


def test_arxiv_sync_pillars_covered():
    pillars = ARXIV_SYNC["new_pillars_since_last_sync"]
    assert 564 in pillars
    assert 574 in pillars
    assert len(pillars) == 11


def test_arxiv_sync_v19_4_tests():
    assert ARXIV_SYNC["v19_4_tests_added"] == 513


def test_arxiv_sync_v20_0_tests():
    assert ARXIV_SYNC["v20_0_tests_added"] == 285


def test_arxiv_sync_lean4_added():
    assert ARXIV_SYNC["lean4_theorems_added_since_v19_3"] == 67


def test_arxiv_sync_headline_count():
    assert len(ARXIV_SYNC["headline_advances"]) >= 4


def test_arxiv_sync_abstract_status():
    assert "PREPARED" in ARXIV_SYNC["abstract_status"]


def test_arxiv_sync_nine_subgap_milestone():
    assert ARXIV_SYNC["all_nine_subgap_milestone"] is True


def test_arxiv_sync_ftheory_milestone():
    assert ARXIV_SYNC["ftheory_rung7_milestone"] is True


def test_arxiv_sync_headline_mentions_101():
    headlines = " ".join(ARXIV_SYNC["headline_advances"])
    assert "101" in headlines


def test_arxiv_sync_headline_mentions_240():
    headlines = " ".join(ARXIV_SYNC["headline_advances"])
    assert "240" in headlines


def test_arxiv_sync_headline_mentions_gap_b():
    headlines = " ".join(ARXIV_SYNC["headline_advances"])
    assert "Gap B" in headlines or "GAP_B" in headlines or "c_L" in headlines


# ─── SPRINT_V19_4 ─────────────────────────────────────────────────────────────

def test_sprint_v19_4_length():
    assert len(SPRINT_V19_4) == 6


def test_sprint_v19_4_pillars():
    pillars = [p["pillar"] for p in SPRINT_V19_4]
    assert pillars == [564, 565, 566, 567, 568, 569]


def test_sprint_v19_4_total_tests():
    total = sum(p["tests"] for p in SPRINT_V19_4)
    assert total == 513


def test_sprint_v19_4_total_lean4():
    total = sum(p["lean4_new"] for p in SPRINT_V19_4)
    assert total == 67


def test_sprint_v19_4_p569_theorems():
    p569 = next(p for p in SPRINT_V19_4 if p["pillar"] == 569)
    assert p569["lean4_new"] == 12


def test_sprint_v19_4_p564_status():
    p564 = next(p for p in SPRINT_V19_4 if p["pillar"] == 564)
    assert "SUBGAP_D" in p564["name"] or "MIXING" in p564["name"]


def test_sprint_v19_4_np_bc2_subgaps():
    np2 = [p for p in SPRINT_V19_4 if p["pillar"] in (564, 565, 566)]
    assert len(np2) == 3


def test_sprint_v19_4_np_bc3_subgaps():
    np3 = [p for p in SPRINT_V19_4 if p["pillar"] in (567, 568, 569)]
    assert len(np3) == 3


def test_sprint_v19_4_no_toe_delta():
    for p in SPRINT_V19_4:
        assert p["toe_delta"] == 0.0


# ─── SPRINT_V20_0 ─────────────────────────────────────────────────────────────

def test_sprint_v20_0_length():
    assert len(SPRINT_V20_0) == 5


def test_sprint_v20_0_pillars():
    pillars = [p["pillar"] for p in SPRINT_V20_0]
    assert pillars == [570, 571, 572, 573, 574]


def test_sprint_v20_0_total_tests():
    total = sum(p["tests"] for p in SPRINT_V20_0)
    assert total == 285


def test_sprint_v20_0_no_lean4():
    total_lean4 = sum(p["lean4_new"] for p in SPRINT_V20_0)
    assert total_lean4 == 0


def test_sprint_v20_0_all_adjacent_track():
    for p in SPRINT_V20_0:
        # Either explicitly marked or description contains 🔵
        desc = p.get("description", "")
        adjacent = p.get("adjacent_track", False)
        assert adjacent or "🔵" in desc or "ADJACENT" in p["name"]


def test_sprint_v20_0_no_toe_delta():
    for p in SPRINT_V20_0:
        assert p["toe_delta"] == 0.0


def test_sprint_v20_0_p570_scaffold():
    p570 = next(p for p in SPRINT_V20_0 if p["pillar"] == 570)
    assert "SCAFFOLD" in p570["name"] or "RUNG7" in p570["name"]


def test_sprint_v20_0_p573_gap_b():
    p573 = next(p for p in SPRINT_V20_0 if p["pillar"] == 573)
    assert "CL" in p573["name"] or "MATTER" in p573["name"]


# ─── LEAN4_THEOREM_COUNT ──────────────────────────────────────────────────────

def test_lean4_total_at_v20_0():
    assert LEAN4_THEOREM_COUNT["total_at_v20_0"] == 240


def test_lean4_at_v19_3_sync():
    assert LEAN4_THEOREM_COUNT["at_v19_3_sync"] == 173


def test_lean4_v19_4_additions():
    assert LEAN4_THEOREM_COUNT["v19_4_additions"] == 67


def test_lean4_v20_0_additions():
    assert LEAN4_THEOREM_COUNT["v20_0_additions"] == 0


def test_lean4_arithmetic():
    calc = LEAN4_THEOREM_COUNT["at_v19_3_sync"] + LEAN4_THEOREM_COUNT["v19_4_additions"]
    assert calc == LEAN4_THEOREM_COUNT["total_at_v20_0"]


def test_lean4_subgap_total():
    assert LEAN4_THEOREM_COUNT["np_bc_subgap_theorems_total"] == 101


def test_lean4_new_files_v19_4():
    files = LEAN4_THEOREM_COUNT["new_files_v19_4"]
    assert len(files) == 6
    assert any("NPBC2SubgapD" in f for f in files)
    assert any("NPBC3SubgapI" in f for f in files)


def test_lean4_no_new_files_v20_0():
    assert LEAN4_THEOREM_COUNT["new_files_v20_0"] == []


# ─── BOOK_27 ──────────────────────────────────────────────────────────────────

def test_book_27_title_contains_nine():
    assert "Nine" in BOOK_27["title"] or "nine" in BOOK_27["title"] or "Sub-Gap" in BOOK_27["title"]


def test_book_27_version():
    assert BOOK_27["version"] == "v20.0"


def test_book_27_chapters():
    assert BOOK_27["chapters"] == 8


def test_book_27_substack_post():
    posts = BOOK_27["substack_posts"]
    assert "#273" in posts[0]


def test_book_27_themes_count():
    assert len(BOOK_27["themes"]) == 8


def test_book_27_file_path():
    assert "book27" in BOOK_27["file"]


def test_book_27_date():
    assert BOOK_27["date"] == "2026-08-01"


# ─── TOE_SCORE_AT_SYNC ───────────────────────────────────────────────────────

def test_toe_score_value():
    assert TOE_SCORE_AT_SYNC["score"] == 29.0


def test_toe_score_max_hardgate():
    assert TOE_SCORE_AT_SYNC["max_hardgate"] == 28.0


def test_toe_score_partial_credit():
    assert TOE_SCORE_AT_SYNC["partial_credit"] == 1.0


def test_toe_score_no_delta_v19_4():
    assert TOE_SCORE_AT_SYNC["v19_4_toe_delta"] == 0.0


def test_toe_score_no_delta_v20_0():
    assert TOE_SCORE_AT_SYNC["v20_0_toe_delta"] == 0.0


def test_toe_score_comment_not_empty():
    assert len(TOE_SCORE_AT_SYNC["comment"]) > 20


def test_toe_score_comment_mentions_adjacent():
    comment = TOE_SCORE_AT_SYNC["comment"]
    assert "ADJACENT" in comment or "adjacent" in comment


# ─── sync_covers() ────────────────────────────────────────────────────────────

def test_sync_covers_previous():
    covers = sync_covers()
    assert covers["previous_sync"] == 563


def test_sync_covers_this_sync():
    covers = sync_covers()
    assert covers["this_sync"] == 575


def test_sync_covers_v19_4_pillars():
    covers = sync_covers()
    assert 564 in covers["v19_4"]["pillars"]
    assert 569 in covers["v19_4"]["pillars"]


def test_sync_covers_v20_0_pillars():
    covers = sync_covers()
    assert 570 in covers["v20_0"]["pillars"]
    assert 574 in covers["v20_0"]["pillars"]


def test_sync_covers_v19_4_tests():
    covers = sync_covers()
    assert covers["v19_4"]["total_tests"] == 513


def test_sync_covers_v20_0_tests():
    covers = sync_covers()
    assert covers["v20_0"]["total_tests"] == 285


def test_sync_covers_v20_0_adjacent_track():
    covers = sync_covers()
    assert covers["v20_0"]["adjacent_track"] is True


def test_sync_covers_combined_tests():
    covers = sync_covers()
    assert covers["combined_tests"] == 513 + 285


def test_sync_covers_milestone_nine_subgaps():
    covers = sync_covers()
    assert "ALL_NINE" in covers["v19_4"]["milestone"]


def test_sync_covers_milestone_rung7():
    covers = sync_covers()
    assert "RUNG7" in covers["v20_0"]["milestone"]


# ─── lean4_advancement() ─────────────────────────────────────────────────────

def test_lean4_advancement_before():
    adv = lean4_advancement()
    assert adv["before_sync"] == 173


def test_lean4_advancement_after():
    adv = lean4_advancement()
    assert adv["after_sync"] == 240


def test_lean4_advancement_new():
    adv = lean4_advancement()
    assert adv["new_theorems"] == 67


def test_lean4_advancement_np_bc2():
    adv = lean4_advancement()
    assert adv["np_bc2_subgap_theorems"] == 33


def test_lean4_advancement_np_bc3():
    adv = lean4_advancement()
    assert adv["np_bc3_subgap_theorems"] == 34


def test_lean4_advancement_total_subgaps():
    adv = lean4_advancement()
    assert adv["total_subgap_theorems"] == 101


def test_lean4_advancement_milestone():
    adv = lean4_advancement()
    assert adv["milestone"] == "ALL_NINE_SUBGAP_KERNELS_PROVED"


def test_lean4_advancement_notes_open():
    adv = lean4_advancement()
    note = adv["progress_note"]
    assert "OPEN" in note or "remain" in note


def test_lean4_advancement_new_files_count():
    adv = lean4_advancement()
    assert len(adv["new_files"]) == 6


# ─── arxiv_abstract_draft() ──────────────────────────────────────────────────

def test_abstract_mentions_nine_subgaps():
    abstract = arxiv_abstract_draft()
    assert "ALL_NINE" in abstract or "nine" in abstract.lower()


def test_abstract_mentions_101():
    abstract = arxiv_abstract_draft()
    assert "101" in abstract


def test_abstract_mentions_240():
    abstract = arxiv_abstract_draft()
    assert "240" in abstract


def test_abstract_mentions_ftheory():
    abstract = arxiv_abstract_draft()
    assert "F-theory" in abstract or "F-Theory" in abstract


def test_abstract_honest_open():
    abstract = arxiv_abstract_draft()
    # Abstract must contain honest language about limitations or open gaps.
    assert (
        "OPEN" in abstract
        or "remains" in abstract.lower()
        or "non-perturbative" in abstract.lower()
        or "maximum advance achievable" in abstract.lower()
    )


def test_abstract_mentions_toe():
    abstract = arxiv_abstract_draft()
    assert "29.0" in abstract or "ToE" in abstract or "hardgate" in abstract


def test_abstract_mentions_cl_min():
    abstract = arxiv_abstract_draft()
    assert "c_L" in abstract or "0.917" in abstract


# ─── sync_certificate() ──────────────────────────────────────────────────────

def test_cert_pillar():
    cert = sync_certificate()
    assert cert["pillar"] == 575


def test_cert_status():
    cert = sync_certificate()
    assert cert["status"] == "ARXIV_BOOK27_SYNC_V200_CERTIFIED"


def test_cert_lean4_total():
    cert = sync_certificate()
    assert cert["lean4_theorems_at_sync"] == 240


def test_cert_toe_score():
    cert = sync_certificate()
    assert cert["toe_score"] == 29.0


def test_cert_nine_subgaps():
    cert = sync_certificate()
    assert cert["all_nine_subgap_kernels_proved"] is True


def test_cert_ftheory_rung7():
    cert = sync_certificate()
    assert cert["ftheory_rung7_scaffold"] is True


def test_cert_next_pillar():
    cert = sync_certificate()
    assert cert["next_pillar_slot"] == 576


def test_cert_next_substack():
    cert = sync_certificate()
    assert "#274" in cert["next_substack_post"]


def test_cert_pillars_synced():
    cert = sync_certificate()
    assert len(cert["pillars_synced"]) == 11


def test_cert_not_claimed_erepr():
    cert = sync_certificate()
    not_claimed = " ".join(cert["what_is_not_claimed"])
    assert "NOT proved" in not_claimed or "ER=EPR" in not_claimed


def test_cert_not_claimed_adjacent():
    cert = sync_certificate()
    not_claimed = " ".join(cert["what_is_not_claimed"])
    assert "ADJACENT" in not_claimed or "adjacent" in not_claimed


# ─── pillar_report() ─────────────────────────────────────────────────────────

def test_pillar_report_complete():
    report = pillar_report()
    for key in ["pillar", "title", "status", "version", "arxiv_sync",
                "book_27", "lean4_theorem_count", "toe_score",
                "sprint_v19_4", "sprint_v20_0", "sync_covers",
                "lean4_advancement", "arxiv_abstract", "certificate"]:
        assert key in report


def test_pillar_report_number():
    report = pillar_report()
    assert report["pillar"] == 575


def test_pillar_report_lean4():
    report = pillar_report()
    assert report["lean4_theorem_count"]["total_at_v20_0"] == 240


def test_pillar_report_certificate_nine_subgaps():
    report = pillar_report()
    assert report["certificate"]["all_nine_subgap_kernels_proved"] is True


def test_pillar_report_sprint_v19_4_list():
    report = pillar_report()
    assert isinstance(report["sprint_v19_4"], list)
    assert len(report["sprint_v19_4"]) == 6


def test_pillar_report_sprint_v20_0_list():
    report = pillar_report()
    assert isinstance(report["sprint_v20_0"], list)
    assert len(report["sprint_v20_0"]) == 5


def test_toe_score_summary():
    summary = toe_score_summary()
    assert summary["score"] == 29.0
    assert summary["partial_credit"] == 1.0
