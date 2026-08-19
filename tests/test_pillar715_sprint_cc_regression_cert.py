# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 715 — Sprint CC regression certificate."""
from __future__ import annotations

from src.core.pillar715_sprint_cc_regression_cert import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    sprint_cc_regression_cert,
)

CERT = sprint_cc_regression_cert()


class TestConstants:
    def test_identity(self):
        assert PILLAR_NUMBER == 715
        assert PILLAR_STATUS == "SPRINT_CC_REGRESSION_CERTIFIED"
        assert PILLAR_TITLE == "Sprint CC Regression Certificate"


class TestCertificate:
    def test_status(self):
        assert CERT["status"] == PILLAR_STATUS

    def test_modules_list(self):
        assert CERT["validated_modules"] == [711, 712, 713, 714]

    def test_all_dicts_valid(self):
        assert CERT["all_dicts_valid"] is True

    def test_dashboard_count(self):
        assert CERT["dashboard_experiment_count"] == 5

    def test_joint_probability_range(self):
        assert 0.0 < CERT["joint_survival_probability"] < 1.0
