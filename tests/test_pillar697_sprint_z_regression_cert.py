# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 697 — Sprint Z regression certificate."""

from src.core.pillar697_sprint_z_regression_cert import (
    SPRINT_Z_PILLARS,
    NEXT_PILLAR_SLOT,
    sprint_z_regression_cert,
)


def test_sprint_z_pillars():
    assert SPRINT_Z_PILLARS == ["693", "694", "695", "696", "697"]


def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 698


def test_cert_returns_dict():
    assert isinstance(sprint_z_regression_cert(), dict)


def test_cert_status():
    cert = sprint_z_regression_cert()
    assert cert["status"] == "SPRINT_Z_REGRESSION_PASSED"


def test_cert_all_passed():
    cert = sprint_z_regression_cert()
    assert cert["all_passed"] is True


def test_cert_checks_count():
    cert = sprint_z_regression_cert()
    assert len(cert["module_checks"]) == 4


def test_each_module_passes():
    cert = sprint_z_regression_cert()
    assert all(item["passed"] for item in cert["module_checks"])


def test_module_pillars():
    cert = sprint_z_regression_cert()
    assert {item["pillar"] for item in cert["module_checks"]} == {"693", "694", "695", "696"}


def test_next_slot_in_cert():
    cert = sprint_z_regression_cert()
    assert cert["next_pillar_slot"] == 698


def test_honest_note_mentions_residual():
    cert = sprint_z_regression_cert()
    assert "residual" in cert["honest_note"]
