# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 692 — Sprint Y regression certificate."""
from __future__ import annotations

import pytest

from src.core.pillar692_sprint_y_regression_cert import (
    EXPECTED_TEST_COUNT,
    SPRINT_Y_PILLARS,
    sprint_y_regression_cert,
)


@pytest.fixture(scope="module")
def cert():
    return sprint_y_regression_cert()


def test_pillars_constant():
    assert SPRINT_Y_PILLARS == [688, 689, 690, 691, 692]


def test_expected_test_count():
    assert EXPECTED_TEST_COUNT == 105


def test_cert_is_dict(cert):
    assert isinstance(cert, dict)


def test_cert_pillar(cert):
    assert cert["pillar"] == 692


def test_cert_status(cert):
    assert cert["status"] == "SPRINT_Y_REGRESSION_PASSED"


def test_cert_sprint(cert):
    assert cert["sprint"] == "Sprint Y"


def test_cert_pillar_count(cert):
    assert cert["pillar_count"] == 5


def test_cert_pillars(cert):
    assert cert["pillars"] == SPRINT_Y_PILLARS


def test_cert_checks_is_list(cert):
    assert isinstance(cert["checks"], list)


def test_cert_check_count(cert):
    assert len(cert["checks"]) == 14


def test_all_checks_pass(cert):
    assert all(item["passed"] for item in cert["checks"])


def test_layer_table_check_present(cert):
    assert any(item["function"] == "layer_improvement_table" for item in cert["checks"])


def test_expected_test_count_embedded(cert):
    assert cert["expected_test_count"] == 105


def test_next_pillar_slot(cert):
    assert cert["next_pillar_slot"] == 693


def test_all_passed_true(cert):
    assert cert["all_passed"] is True
