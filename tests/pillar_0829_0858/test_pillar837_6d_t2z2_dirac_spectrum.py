# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 837 — conditional 6D T²/Z₂ Dirac spectrum."""
from __future__ import annotations

from src.core.pillar837_6d_t2z2_dirac_spectrum import (
    CHERN_NUMBER_C1,
    FIXED_POINT_COUNT,
    GATE,
    LEAN4_COUNT,
    LEAN4_PRIOR,
    LEAN4_TOTAL,
    N_GEN_DERIVED,
    NGEN_6D_BUNDLE_CONDITION,
    PILLAR,
    WINDING_NUMBER,
    conditional_dirac_index,
    dirac_spectrum_t2z2_summary,
    t2z2_fixed_points,
    z2_parity_split,
)


class TestPillar837Constants:
    def test_pillar_number(self): assert PILLAR == 837
    def test_gate(self): assert GATE == "NGEN_6D_T2Z2_DIRAC_CLOSED"
    def test_nw(self): assert WINDING_NUMBER == 5
    def test_fixed_point_count(self): assert FIXED_POINT_COUNT == 4
    def test_chern_number(self): assert CHERN_NUMBER_C1 == 3
    def test_ngen(self): assert N_GEN_DERIVED == 3
    def test_lean4_count(self): assert LEAN4_COUNT == 30
    def test_lean4_total(self): assert LEAN4_TOTAL == 1851
    def test_lean4_accumulates(self): assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT


class TestT2Z2Geometry:
    def test_fixed_points_list(self):
        assert len(t2z2_fixed_points()) == 4

    def test_fixed_points_are_corners(self):
        pts = t2z2_fixed_points()
        assert (0.0, 0.0) in pts and (3.141592653589793, 3.141592653589793) in pts

    def test_parity_split(self):
        split = z2_parity_split()
        assert split["z2_even_count"] == 2
        assert split["z2_odd_count"] == 2

    def test_parity_exhausts_fixed_points(self):
        split = z2_parity_split()
        assert split["z2_even_count"] + split["z2_odd_count"] == split["fixed_point_count"]


class TestConditionalIndex:
    def test_default_index(self):
        data = conditional_dirac_index()
        assert data["aps_index"] == 3

    def test_bundle_condition(self):
        data = conditional_dirac_index()
        assert data["bundle_condition_satisfied"] is True

    def test_conditionality_is_honest(self):
        assert "Conditional" in NGEN_6D_BUNDLE_CONDITION or "c₁ = 3" in NGEN_6D_BUNDLE_CONDITION

    def test_nondefault_c1_tracks_input(self):
        data = conditional_dirac_index(c1=5)
        assert data["aps_index"] == 5 and data["bundle_condition_satisfied"] is False


class TestPillar837Summary:
    def test_summary_pillar(self):
        assert dirac_spectrum_t2z2_summary()["pillar"] == 837

    def test_summary_gate(self):
        assert dirac_spectrum_t2z2_summary()["gate"] == GATE

    def test_summary_conditional(self):
        assert dirac_spectrum_t2z2_summary()["conditional"] is True

    def test_summary_honest_status(self):
        assert "conditional" in dirac_spectrum_t2z2_summary()["honest_status"].lower()

    def test_summary_remaining_open(self):
        assert "BUNDLE" in dirac_spectrum_t2z2_summary()["remaining_open"][0]
