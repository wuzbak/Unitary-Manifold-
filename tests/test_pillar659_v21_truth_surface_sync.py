# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 659 — v21 truth-surface sync."""
from __future__ import annotations

from src.core.pillar659_v21_truth_surface_sync import (
    ADJACENT_TRACK,
    FTHEORY_RUNGS,
    LEAN4_THEOREMS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPRINT_R_PILLARS_PART1,
    TOE_DENOMINATOR,
    TOE_SCORE,
    TRUTH_SURFACES,
    VERSION,
    pillar_report,
    substack_draft_286,
    truth_surface_sync_certificate,
)

REPORT = pillar_report()
CERT = truth_surface_sync_certificate()
DRAFT = substack_draft_286()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 659

    def test_status(self):
        assert PILLAR_STATUS == 'V21_TRUTH_SURFACE_SYNC_CERTIFIED'

    def test_version(self):
        assert VERSION == 'v21.0'

    def test_toe_score(self):
        assert TOE_SCORE == 30.0
        assert TOE_DENOMINATOR == 28

    def test_lean4(self):
        assert LEAN4_THEOREMS == 342

    def test_ftheory_rungs(self):
        assert FTHEORY_RUNGS == '10/12'

    def test_truth_surfaces_count(self):
        assert len(TRUTH_SURFACES) == 6

    def test_sprint_range(self):
        assert SPRINT_R_PILLARS_PART1 == list(range(653, 661))

    def test_adjacent_track(self):
        assert ADJACENT_TRACK is False


class TestFunctions:
    def test_certificate_keys(self):
        for key in ['version', 'toe_score', 'toe_denominator', 'lean4_theorems', 'ftheory_rungs', 'truth_surfaces', 'sprint_r_part1_pillars', 'surface_count', 'sync_certified']:
            assert key in CERT

    def test_certificate_flag(self):
        assert CERT['sync_certified'] is True

    def test_draft_number(self):
        assert DRAFT['draft_number'] == 286

    def test_draft_coverage(self):
        assert DRAFT['pillars_covered'] == SPRINT_R_PILLARS_PART1


class TestReport:
    def test_report_keys(self):
        for key in ['pillar', 'title', 'status', 'version', 'adjacent_track', 'truth_surface_sync_certificate', 'substack_draft_286', 'toe_score_delta', 'hardgate_score_delta']:
            assert key in REPORT

    def test_toe_delta(self):
        assert REPORT['toe_score_delta'] == 0.0
        assert REPORT['hardgate_score_delta'] == 0.0
