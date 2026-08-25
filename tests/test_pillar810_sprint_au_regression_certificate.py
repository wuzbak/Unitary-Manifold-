# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 810 — Sprint AU Regression Certificate."""

import pytest

from src.core.pillar810_sprint_au_regression_certificate import (
    CL_AGREEMENT,
    CL_DERIVED,
    KEY_RESULTS,
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


class TestPillar810Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 810

    def test_gate_string(self):
        assert PILLAR_GATE == "SPRINT_AU_REGRESSION_CERTIFICATE"

    def test_sprint_name_contains_radion(self):
        assert "Radion" in SPRINT_NAME

    def test_sprint_version(self):
        assert SPRINT_VERSION == "v24.2"

    def test_next_pillar_slot(self):
        assert NEXT_PILLAR_SLOT == 811

    def test_lean4_start(self):
        assert LEAN4_START == 1246

    def test_lean4_end(self):
        assert LEAN4_END == 1306

    def test_lean4_delta(self):
        assert LEAN4_DELTA == 60

    def test_pillars_count(self):
        assert len(PILLARS) == 4

    def test_open_items_count(self):
        assert len(OPEN_ITEMS) >= 4

    def test_cl_derived_exact(self):
        assert abs(CL_DERIVED - 71.0 / 74.0) < 1e-15

    def test_cl_agreement(self):
        assert CL_AGREEMENT is True


class TestValidateSprint:
    def test_returns_dict(self):
        result = validate_sprint()
        assert isinstance(result, dict)

    def test_status_pass(self):
        result = validate_sprint()
        assert result["status"] == "PASS", f"Errors: {result['errors']}"

    def test_no_errors(self):
        result = validate_sprint()
        assert result["errors"] == []

    def test_pillars_validated(self):
        result = validate_sprint()
        assert result["pillars_validated"] == 4

    def test_lean4_chain_correct(self):
        result = validate_sprint()
        assert result["lean4_delta"] == 60

    def test_next_slot_correct(self):
        result = validate_sprint()
        assert result["next_slot"] == 811


class TestKeyResults:
    def test_qcd_suppression_near_7(self):
        assert abs(KEY_RESULTS["qcd_suppression_orders"] - 7.0) < 0.01

    def test_cmb_partial_closure_positive(self):
        assert KEY_RESULTS["cmb_partial_closure_fraction"] > 0.0

    def test_wa_is_float(self):
        assert isinstance(KEY_RESULTS["wa_radion_predicted"], float)

    def test_cl_derived_correct(self):
        assert abs(KEY_RESULTS["cl_derived"] - 71.0 / 74.0) < 1e-15

    def test_cl_geometric_locking_true(self):
        assert KEY_RESULTS["cl_geometric_locking"] is True


class TestPillarManifest:
    def test_pillar_numbers_sequential(self):
        for i, p in enumerate(PILLARS):
            assert p["number"] == 806 + i

    def test_all_gates_non_empty(self):
        for p in PILLARS:
            assert isinstance(p["gate"], str)
            assert len(p["gate"]) > 0

    def test_all_lean4_counts_15(self):
        for p in PILLARS:
            assert p["lean4_theorems"] == 15
