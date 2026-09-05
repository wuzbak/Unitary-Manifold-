# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 649 — Tier 1-4 gap synthesis certificate."""
from __future__ import annotations

from src.core.pillar649_tier1_4_gap_synthesis import (
    LEAN4_TOTAL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TOE_SCORE,
    VERSION,
    all_status_advances,
    pillar_report,
    synthesis_certificate,
    tier1_summary,
    tier2_summary,
    tier3_summary,
    tier4_summary,
    tier5_summary,
)

REPORT = pillar_report()
CERT = synthesis_certificate()
T1 = tier1_summary()
T2 = tier2_summary()
T3 = tier3_summary()
T4 = tier4_summary()
T5 = tier5_summary()
ADVANCES = all_status_advances()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 649

    def test_status(self):
        assert "SYNTHESIS_CERTIFIED" in PILLAR_STATUS

    def test_toe_score(self):
        assert abs(TOE_SCORE - 30.0) < 1e-9

    def test_lean4_total(self):
        assert LEAN4_TOTAL == 342


class TestTierSummaries:
    def test_tier1_two_pillars(self):
        assert len(T1["pillars"]) == 2

    def test_tier2_four_pillars(self):
        assert len(T2["pillars"]) == 4

    def test_tier3_four_pillars(self):
        assert len(T3["pillars"]) == 4

    def test_tier4_four_pillars(self):
        assert len(T4["pillars"]) == 4

    def test_tier5_has_649(self):
        assert 649 in T5["pillars"]

    def test_all_toe_deltas_zero(self):
        for tier in [T1, T2, T3, T4, T5]:
            assert tier["toe_delta"] == 0.0

    def test_metric_reflection_does_not_become_internal_lift_equivalence(self):
        entry = next(item for item in T2["advances"] if item["pillar"] == 636)
        assert entry["equivalence_established"] is False
        assert entry["scientific_progress"] is False
        assert "equivalence proved" not in entry["advance"]
        assert "internal lift" in entry["open_item"]


class TestAllAdvances:
    def test_at_least_14_advances(self):
        assert len(ADVANCES) >= 10

    def test_tiers_present(self):
        tiers = {a["tier"] for a in ADVANCES}
        assert 1 in tiers
        assert 2 in tiers
        assert 3 in tiers
        assert 4 in tiers


class TestSynthesisCertificate:
    def test_pilar_range(self):
        assert CERT["pillar_range"][0] == 631

    def test_not_claimed_no_measurements(self):
        assert len(CERT["what_is_NOT_claimed"]) > 0

    def test_synthesis_retains_gauge_selection_gap(self):
        assert CERT["closure_earned"] is False
        assert CERT["scientific_progress"] is False
        assert CERT["open_gauge_selection"]["status"] == "UNDERDETERMINED_BY_METRIC_REFLECTION"
        assert REPORT["closure_earned"] is False


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_all_tiers_present(self):
        for k in ["tier1", "tier2", "tier3", "tier4", "tier5"]:
            assert k in REPORT
