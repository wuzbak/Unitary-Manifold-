# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 855 — cross-dimensional swampland audit."""
from __future__ import annotations

from src.core.pillar855_swampland_cross_dimensional_audit import (
    ALL_DIMENSIONS_CONSISTENT,
    COBORDISM_PASS,
    CROSS_DIMENSIONAL_AUDIT,
    DE_SITTER_PASS,
    DIMENSIONS_AUDITED,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    NO_GLOBAL_SYM_PASS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    SDC_PASS_DIMS,
    SDC_TENSION_10D_REGISTERED,
    WGC_PASS,
    swampland_cross_dim_summary,
)


class TestPillar855Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 855
    def test_gate(self): assert PILLAR_GATE == "SWAMPLAND_CROSS_DIMENSIONAL_PASS"
    def test_dimensions(self): assert DIMENSIONS_AUDITED == [5, 6, 7, 9, 10, 11]
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total(self): assert LEAN4_TOTAL_AFTER == 2116
    def test_sdc_pass_dims(self): assert SDC_PASS_DIMS == [5, 6, 7, 9, 11]
    def test_sdc_10d_registered(self): assert SDC_TENSION_10D_REGISTERED is True
    def test_de_sitter_pass(self): assert DE_SITTER_PASS is True
    def test_wgc_pass(self): assert WGC_PASS is True
    def test_no_global_symmetry_pass(self): assert NO_GLOBAL_SYM_PASS is True
    def test_cobordism_pass(self): assert COBORDISM_PASS is True
    def test_all_dimensions_consistent(self): assert ALL_DIMENSIONS_CONSISTENT is True


class TestPillar855AuditRows:
    def test_row_count(self): assert len(CROSS_DIMENSIONAL_AUDIT) == 6

    def test_all_rows_have_dimension(self):
        for row in CROSS_DIMENSIONAL_AUDIT:
            assert "dimension" in row

    def test_all_rows_have_sdc(self):
        for row in CROSS_DIMENSIONAL_AUDIT:
            assert "sdc" in row

    def test_all_rows_have_wgc_pass(self):
        for row in CROSS_DIMENSIONAL_AUDIT:
            assert row["wgc_pass"] is True

    def test_ten_dimensional_row_registered(self):
        row10 = next(row for row in CROSS_DIMENSIONAL_AUDIT if row["dimension"] == 10)
        assert row10["sdc"] == "SDC_TENSION_REGISTERED"


class TestPillar855Summary:
    def test_returns_dict(self): assert isinstance(swampland_cross_dim_summary(), dict)
    def test_summary_gate(self): assert swampland_cross_dim_summary()["gate"] == PILLAR_GATE
    def test_summary_consistent(self): assert swampland_cross_dim_summary()["all_dimensions_consistent"] is True
    def test_summary_open_item(self): assert swampland_cross_dim_summary()["remaining_open"] == ["SDC_10D_QCD_TENSION_REGISTERED"]
    def test_summary_honest_note(self): assert "registered tension" in swampland_cross_dim_summary()["honest_note"]
