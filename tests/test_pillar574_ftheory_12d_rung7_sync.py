# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 574 — F-theory / 12D DBP Rung 7 Sync Certificate."""
from __future__ import annotations

from src.core.pillar574_ftheory_12d_rung7_sync import (
    ADJACENCY_TRACK_LABEL,
    CANONICAL_FILES_SYNCED,
    LEAN4_THEOREMS_ADDED,
    NEW_TESTS_ADDED_BY_SPRINT,
    NEXT_PILLAR_SLOT,
    NEXT_SUBSTACK_POST,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    SPRINT_PILLARS,
    SYNC_DATE,
    VERSION,
    pillar_report,
    separation_guard,
    sync_certificate,
    sync_covers,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 574


def test_pillar_gate():
    assert PILLAR_GATE == "FTHEORY_12D_RUNG7_SYNC"


def test_version():
    assert VERSION == "v20.0"


def test_sync_date():
    assert SYNC_DATE == "2026-08-01"


def test_sprint_pillars():
    assert SPRINT_PILLARS == [570, 571, 572, 573]


def test_canonical_files_synced_nonempty():
    assert len(CANONICAL_FILES_SYNCED) >= 4


def test_canonical_files_include_status_md():
    assert "STATUS.md" in CANONICAL_FILES_SYNCED


def test_lean4_theorems_added_zero():
    assert LEAN4_THEOREMS_ADDED == 0


def test_new_tests_added_matches_sprint_total():
    assert NEW_TESTS_ADDED_BY_SPRINT == 285


def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 575


def test_next_substack_post():
    assert "#273" in NEXT_SUBSTACK_POST


class TestSeparationGuard:
    def test_not_hardgate(self):
        guard = separation_guard()
        assert guard["is_hardgate"] is False

    def test_adjacency_label(self):
        guard = separation_guard()
        assert guard["adjacency_label"] == ADJACENCY_TRACK_LABEL

    def test_documentation_only(self):
        assert separation_guard()["is_documentation_sync_only"] is True


class TestSyncCovers:
    def test_pillar(self):
        assert sync_covers()["pillar"] == 574

    def test_sprint_pillars_count(self):
        assert sync_covers()["n_sprint_pillars"] == 4

    def test_files_count_matches(self):
        covers = sync_covers()
        assert covers["n_canonical_files_synced"] == len(CANONICAL_FILES_SYNCED)


class TestSyncCertificate:
    def test_gate(self):
        assert sync_certificate()["gate"] == PILLAR_GATE

    def test_all_adjacent_track(self):
        assert sync_certificate()["all_sprint_pillars_adjacent_track"] is True

    def test_not_claimed_mentions_adjacent(self):
        cert = sync_certificate()
        joined = " ".join(cert["what_is_not_claimed"])
        assert "ADJACENT" in joined

    def test_not_claimed_mentions_no_hardgate(self):
        cert = sync_certificate()
        joined = " ".join(cert["what_is_not_claimed"])
        assert "hardgate" in joined.lower()


class TestPillarReport:
    def test_report_keys(self):
        report = pillar_report()
        for key in ("pillar", "title", "gate", "version", "sync_date",
                    "separation_guard", "sync_covers", "certificate"):
            assert key in report

    def test_report_pillar_number(self):
        assert pillar_report()["pillar"] == 574

    def test_report_title_mentions_sync(self):
        assert "Sync" in pillar_report()["title"]
        assert PILLAR_TITLE == pillar_report()["title"]
