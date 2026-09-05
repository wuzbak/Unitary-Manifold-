# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

from src.core.pillar817_sprint_aw_regression_certificate import (
    LEAN4_DELTA,
    LEAN4_END,
    LEAN4_START,
    NEXT_PILLAR_SLOT,
    OPEN_ITEMS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLARS,
    SPRINT_NAME,
    SPRINT_VERSION,
    validate_sprint,
)


class TestCertificate:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 817

    def test_gate(self):
        assert PILLAR_GATE == "SPRINT_AW_REGRESSION_CERTIFICATE"

    def test_sprint_name(self):
        assert "Sprint AW" in SPRINT_NAME

    def test_sprint_version(self):
        assert SPRINT_VERSION == "v24.4"

    def test_pillars_count(self):
        assert len(PILLARS) == 3

    def test_pillar_numbers(self):
        nums = [p["number"] for p in PILLARS]
        assert nums == [814, 815, 816]

    def test_lean4_start(self):
        assert LEAN4_START == 1336

    def test_lean4_end(self):
        assert LEAN4_END == 1386

    def test_lean4_delta(self):
        assert LEAN4_DELTA == 50

    def test_next_slot(self):
        assert NEXT_PILLAR_SLOT == 818

    def test_open_items_non_empty(self):
        assert len(OPEN_ITEMS) >= 3

    def test_boltzmann_open_in_items(self):
        assert any("BOLTZMANN" in item for item in OPEN_ITEMS)

    def test_g1_floor_in_items(self):
        assert any("G1" in item for item in OPEN_ITEMS)


class TestValidateSprint:
    def test_returns_dict(self):
        result = validate_sprint()
        assert isinstance(result, dict)

    def test_status_pass(self):
        result = validate_sprint()
        assert result["status"] == "PASS", result.get("errors", [])

    def test_no_errors(self):
        result = validate_sprint()
        assert result["errors"] == []

    def test_pillars_validated(self):
        result = validate_sprint()
        assert result["pillars_validated"] == 3

    def test_lean4_end(self):
        result = validate_sprint()
        assert result["lean4_end"] == 1386

    def test_toy_bookkeeping_does_not_certify_cmb_closure(self):
        result = validate_sprint()
        assert result["cmb_gate"] == "ZPH_CAMB_BRIDGE_UM_TRANSFER_UNSUPPORTED"
        assert result["cmb_backend"] == "toy"
        assert result["cmb_closure_earned"] is False
        assert "not a CMB solver certificate" in result["validation_scope"]
