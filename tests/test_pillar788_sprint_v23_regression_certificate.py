# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 788 — SPRINT_V23_REGRESSION_CERTIFICATE (15 tests)."""

import pytest
from src.core.pillar788_sprint_v23_regression_certificate import (
    SprintV23Certificate,
    run_pillar788,
    SPRINT_VERSION, PILLARS_THIS_SPRINT,
    LEAN4_START, LEAN4_END, LEAN4_DELTA,
    TESTS_START, TESTS_NEW, TESTS_END,
    NEXT_PILLAR_SLOT,
)


class TestSprintV23Certificate:
    def setup_method(self):
        self.cert = run_pillar788()

    def test_version(self):
        assert self.cert.version == "v23"

    def test_pillars(self):
        assert 786 in self.cert.pillars
        assert 787 in self.cert.pillars
        assert 788 in self.cert.pillars

    def test_lean4_delta(self):
        assert self.cert.lean4_delta == LEAN4_END - LEAN4_START

    def test_lean4_end_above_1000(self):
        assert self.cert.lean4_end >= 1000

    def test_tests_new_positive(self):
        assert self.cert.tests_new > 0

    def test_tests_end_equals_start_plus_new(self):
        assert self.cert.tests_end == TESTS_START + TESTS_NEW

    def test_regression_passed(self):
        assert self.cert.regression_status == "PASSED"

    def test_zero_failures(self):
        assert self.cert.failures == 0

    def test_next_slot(self):
        assert self.cert.next_pillar_slot == NEXT_PILLAR_SLOT

    def test_new_app_listed(self):
        assert "falsification-observatory" in self.cert.new_app

    def test_milestone_flag(self):
        assert "1000" in self.cert.milestone

    def test_pillar_count(self):
        assert len(self.cert.pillars) == 3

    def test_lean4_delta_positive(self):
        assert self.cert.lean4_delta > 0

    def test_sprint_name_nonempty(self):
        assert len(self.cert.name) > 0

    def test_date_format(self):
        assert "-" in self.cert.date
