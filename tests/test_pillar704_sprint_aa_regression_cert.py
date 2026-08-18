# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 704 — Sprint AA regression certificate."""
from __future__ import annotations

from src.core.pillar704_sprint_aa_regression_cert import (
    PILLAR_NUMBER,
    sprint_aa_regression_cert,
)

CERT = sprint_aa_regression_cert()


def test_pillar_number():
    assert PILLAR_NUMBER == 704


def test_cert_is_dict():
    assert isinstance(CERT, dict)


def test_cert_status_ok():
    assert CERT["status"] == "REGRESSION_CERTIFIED"


def test_all_dicts_true():
    assert CERT["all_dicts"] is True


def test_has_expected_check_keys():
    assert "p698_solver" in CERT["checks"]
    assert "p703_summary" in CERT["checks"]


def test_all_checks_true():
    assert all(CERT["checks"].values())


def test_artifacts_include_public_results():
    assert "p699_total" in CERT["artifacts"]
    assert "p702_planck" in CERT["artifacts"]
