# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 819 — Sprint AX Regression Certificate."""
from __future__ import annotations

import pytest

from src.core.pillar819_sprint_ax_regression_certificate import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    OPEN_ITEMS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLARS,
    SPRINT_NAME,
    SPRINT_VALID,
    SPRINT_VERSION,
    validate_sprint,
)


class TestSprintAXCertificate:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 819

    def test_pillar_gate(self):
        assert PILLAR_GATE == "SPRINT_AX_REGRESSION_CERTIFICATE"

    def test_sprint_name_contains_boltzmann(self):
        assert "Boltzmann" in SPRINT_NAME

    def test_sprint_version(self):
        assert SPRINT_VERSION == "v24.5"

    def test_pillars_list(self):
        assert [p["number"] for p in PILLARS] == [818]

    def test_lean4_start(self):
        assert LEAN4_START == 1386

    def test_lean4_end(self):
        assert LEAN4_END == 1411

    def test_lean4_delta(self):
        assert LEAN4_DELTA == 25

    def test_next_pillar_slot(self):
        assert NEXT_PILLAR_SLOT == 820

    def test_sprint_valid(self):
        assert SPRINT_VALID is True

    def test_open_items_count(self):
        assert len(OPEN_ITEMS) >= 5

    def test_adm_open_registered(self):
        assert any("ADM" in s for s in OPEN_ITEMS)

    def test_isw_open_registered(self):
        assert any("ISW" in s for s in OPEN_ITEMS)

    def test_g1_floor_registered(self):
        assert any("G1" in s for s in OPEN_ITEMS)


class TestValidateSprint:
    @pytest.fixture(scope="class")
    def result(self):
        return validate_sprint()

    def test_valid(self, result):
        assert result["valid"] is True

    def test_no_errors(self, result):
        assert result["errors"] == []

    def test_full_5d_closed(self, result):
        assert result["full_5d_boltzmann_closed"] is True

    def test_a_br_small(self, result):
        assert result["a_br_max"] < 1.0e-2
