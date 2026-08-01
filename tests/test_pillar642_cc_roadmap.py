# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 642 — CC 10D path roadmap."""
from __future__ import annotations

from src.core.pillar642_cc_10d_path_roadmap import (
    CC_TOTAL_ORDERS,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    RESIDUAL_ORDERS,
    RS1_GB_CLOSES_ORDERS,
    STEP1_FLUX_ORDERS,
    STEP2_KKLT_ORDERS,
    STEP3_SWAMPLAND_ORDERS,
    STEP4_ANTHROPIC_ORDERS,
    VERSION,
    architecture_limit_statement,
    closure_accounting,
    pillar_report,
    roadmap_steps,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
STEPS = roadmap_steps()
ACCOUNTING = closure_accounting()
LIMIT = architecture_limit_statement()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 642

    def test_status(self):
        assert "CC_10D_PATH_ROADMAP" in PILLAR_STATUS

    def test_residual_orders(self):
        expected = CC_TOTAL_ORDERS - RS1_GB_CLOSES_ORDERS
        assert abs(RESIDUAL_ORDERS - expected) < 0.01

    def test_total_steps(self):
        assert len(STEPS) == 4

    def test_orders_sum(self):
        total = STEP1_FLUX_ORDERS + STEP2_KKLT_ORDERS + STEP3_SWAMPLAND_ORDERS + STEP4_ANTHROPIC_ORDERS
        assert abs(total - RESIDUAL_ORDERS) < 1.0


class TestRoadmapSteps:
    def test_step_numbers(self):
        for i, step in enumerate(STEPS, 1):
            assert step["step"] == i

    def test_step1_adjacent_track(self):
        assert "ADJACENT_TRACK" in STEPS[0]["status"]

    def test_step4_non_derivable(self):
        assert "NON_DERIVABLE" in STEPS[3]["status"]


class TestClosureAccounting:
    def test_fully_accounted(self):
        assert ACCOUNTING["fully_accounted"] is True

    def test_5_steps(self):
        # 4 roadmap steps + base RS1/GB
        assert ACCOUNTING["steps"] == 4


class TestArchitectureLimit:
    def test_label(self):
        assert LIMIT["label"] == "ARCHITECTURE_LIMIT_CERTIFIED"

    def test_flag(self):
        assert "ARCHITECTURE_LIMIT = True" in LIMIT["flag"]


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
