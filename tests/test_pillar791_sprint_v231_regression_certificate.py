# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 791 — SPRINT_V231_REGRESSION_CERTIFICATE (15 tests)."""

import pytest
from src.core.pillar791_sprint_v231_regression_certificate import (
    SprintV231Certificate, run_pillar791,
    SPRINT_VERSION, PILLARS_THIS_SPRINT,
    LEAN4_START, LEAN4_END, LEAN4_DELTA,
    TESTS_START, TESTS_NEW, TESTS_END,
    NEXT_PILLAR_SLOT, LEAN4_MILESTONE, APP_MILESTONE,
)


class TestSprintV231Certificate:
    def setup_method(self):
        self.cert = run_pillar791()

    def test_version(self):
        assert self.cert.version == "v23.1"

    def test_name(self):
        assert self.cert.name == "The Living Theory"

    def test_pillars_include_789(self):
        assert 789 in self.cert.pillars

    def test_pillars_include_790(self):
        assert 790 in self.cert.pillars

    def test_pillars_include_791(self):
        assert 791 in self.cert.pillars

    def test_lean4_delta(self):
        assert self.cert.lean4_delta == LEAN4_END - LEAN4_START

    def test_lean4_end_above_1030(self):
        assert self.cert.lean4_end >= 1030

    def test_tests_end(self):
        assert self.cert.tests_end == TESTS_START + TESTS_NEW

    def test_regression_passed(self):
        assert self.cert.regression_status == "PASSED"

    def test_zero_failures(self):
        assert self.cert.failures == 0

    def test_next_slot(self):
        assert self.cert.next_pillar_slot == NEXT_PILLAR_SLOT

    def test_new_app_listed(self):
        assert "interrogator" in self.cert.new_app

    def test_lean4_milestone(self):
        assert "1036" in self.cert.lean4_milestone

    def test_app_milestone(self):
        assert "INTERROGATOR" in self.cert.app_milestone

    def test_pillar_count(self):
        assert len(self.cert.pillars) == 3
