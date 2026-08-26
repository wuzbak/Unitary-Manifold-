# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 825 — Sprint AY Regression Certificate."""
from __future__ import annotations

import pytest

from src.core.pillar825_sprint_ay_regression_certificate import (
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


class TestSprintAYCertificate:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 825

    def test_pillar_gate(self):
        assert PILLAR_GATE == "SPRINT_AY_REGRESSION_CERTIFICATE"

    def test_sprint_name_contains_nlo(self):
        assert "NLO" in SPRINT_NAME

    def test_sprint_version(self):
        assert SPRINT_VERSION == "v24.6"

    def test_pillars_list(self):
        assert [p["number"] for p in PILLARS] == [820, 821, 822, 823, 824]

    def test_lean4_start(self):
        assert LEAN4_START == 1411

    def test_lean4_end(self):
        assert LEAN4_END == 1506

    def test_lean4_delta(self):
        assert LEAN4_DELTA == 95

    def test_lean4_delta_arithmetic(self):
        assert LEAN4_END - LEAN4_START == LEAN4_DELTA

    def test_next_pillar_slot(self):
        assert NEXT_PILLAR_SLOT == 826

    def test_sprint_valid(self):
        assert SPRINT_VALID is True

    def test_open_items_nonempty(self):
        assert len(OPEN_ITEMS) >= 8

    def test_open_items_mention_nw_uniqueness(self):
        text = " ".join(OPEN_ITEMS)
        assert "NW_UNIQUENESS" in text or "UNIQUENESS" in text

    def test_open_items_mention_ngen(self):
        text = " ".join(OPEN_ITEMS)
        assert "NGEN" in text or "N_gen" in text

    def test_open_items_mention_desi(self):
        text = " ".join(OPEN_ITEMS)
        assert "DESI" in text

    def test_pillar_gates_correct(self):
        gates = {p["number"]: p["gate"] for p in PILLARS}
        assert gates[820] == "ISW_NLO_PERTURBATIVE_CLOSED"
        assert gates[821] == "Z2_NGAP_NLO_CONFIRMED"
        assert gates[822] == "NW_NARROWED_TO_5_7_GEOMETRIC"
        assert gates[823] == "NGEN_5D_EFT_NOGO_PROVED"
        assert gates[824] == "DESI_DR3_PREREGISTERED"


class TestValidateSprint:
    def test_validate_sprint_runs(self):
        result = validate_sprint()
        assert result is not None

    def test_validate_sprint_valid(self):
        result = validate_sprint()
        assert result["valid"] is True

    def test_validate_sprint_no_errors(self):
        result = validate_sprint()
        assert result["errors"] == []

    def test_validate_sprint_gate(self):
        result = validate_sprint()
        assert result["gate"] == PILLAR_GATE

    def test_validate_sprint_version(self):
        result = validate_sprint()
        assert result["version"] == "v24.6"

    def test_validate_sprint_lean4_start(self):
        result = validate_sprint()
        assert result["lean4_start"] == 1411

    def test_validate_sprint_lean4_end(self):
        result = validate_sprint()
        assert result["lean4_end"] == 1506

    def test_validate_sprint_lean4_delta(self):
        result = validate_sprint()
        assert result["lean4_delta"] == 95

    def test_validate_sprint_next_slot(self):
        result = validate_sprint()
        assert result["next_pillar_slot"] == 826

    def test_validate_sprint_pillars_count(self):
        result = validate_sprint()
        assert len(result["pillars"]) == 5

    def test_validate_sprint_open_items_nonempty(self):
        result = validate_sprint()
        assert len(result["open_items"]) >= 8
