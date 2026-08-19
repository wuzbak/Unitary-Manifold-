# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 650 — framework derivation coverage ledger v20.9."""
from __future__ import annotations

from src.core.pillar650_toe_score_ledger_v209 import (
    HARDGATE_SCORE,
    NEXT_OPPORTUNITIES,
    PARTIAL_CREDIT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    TOE_SCORE,
    VERSION,
    next_score_opportunities,
    pillar_report,
    toe_ledger,
)

REPORT = pillar_report()
LEDGER = toe_ledger()
OPPS = next_score_opportunities()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 650

    def test_toe_score(self):
        assert abs(TOE_SCORE - 30.0) < 1e-9

    def test_hardgate_score(self):
        assert abs(HARDGATE_SCORE - 28.0) < 1e-9

    def test_partial_credit(self):
        assert abs(PARTIAL_CREDIT - 2.0) < 1e-9

    def test_sum_correct(self):
        assert abs(HARDGATE_SCORE + PARTIAL_CREDIT - TOE_SCORE) < 1e-9


class TestLedger:
    def test_v209_delta_zero(self):
        assert LEDGER["v209_delta"] == 0.0

    def test_max_possible_gt_toe(self):
        assert LEDGER["max_possible"] > TOE_SCORE


class TestNextOpportunities:
    def test_at_least_3_opportunities(self):
        assert len(OPPS) >= 3

    def test_litebird_opportunity(self):
        lit = next((o for o in OPPS if "LiteBIRD" in o["condition"]), None)
        assert lit is not None
        assert lit["delta"] > 0.0


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0
