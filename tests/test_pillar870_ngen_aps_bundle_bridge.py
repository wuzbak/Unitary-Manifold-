# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 870 — APS ↔ bundle bridge for N_gen."""
from __future__ import annotations

from fractions import Fraction

import pytest

from src.sixd.pillar870_ngen_aps_bundle_bridge import (
    APS_DEFECT,
    BRIDGE_VERIFIED,
    DEGENERACY_INDEPENDENT,
    ETA_BAR_MINIMAL,
    FIVE_D_NOGO_REPRODUCED,
    IND_5D,
    IND_5D_EXPECTED,
    IND_6D,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    N_FIXED_POINTS,
    N_GEN_6D,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    aps_bundle_bridge_summary,
    aps_defect,
    five_d_index,
    six_d_index,
)


class TestPillar870Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 870
    def test_gate(self): assert PILLAR_GATE == "NGEN_6D_APS_BUNDLE_BRIDGE_VERIFIED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 25
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2406
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2431
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_fixed_points(self): assert N_FIXED_POINTS == 4
    def test_eta_bar(self): assert ETA_BAR_MINIMAL == Fraction(1, 4)
    def test_eta_bar_is_exact_fraction(self): assert isinstance(ETA_BAR_MINIMAL, Fraction)


class TestPillar870APSDefect:
    def test_defect_value(self): assert APS_DEFECT == Fraction(1, 2)
    def test_defect_function(self): assert aps_defect() == APS_DEFECT
    def test_defect_scales_with_fixed_points(self):
        assert aps_defect(n_fixed=8) == Fraction(1, 1)
    def test_defect_rejects_zero_fixed_points(self):
        with pytest.raises(ValueError):
            aps_defect(n_fixed=0)
    def test_defect_is_exact(self): assert isinstance(aps_defect(), Fraction)
    def test_defect_half_integer(self): assert APS_DEFECT.denominator == 2


class TestPillar870Indices:
    def test_ind_6d(self): assert IND_6D == Fraction(3, 1)
    def test_ind_6d_integer(self): assert IND_6D.denominator == 1
    def test_ind_5d(self): assert IND_5D == Fraction(5, 2)
    def test_ind_5d_expected(self): assert IND_5D_EXPECTED == Fraction(5, 2)
    def test_ind_5d_matches_expected(self): assert IND_5D == IND_5D_EXPECTED
    def test_six_d_index_function(self): assert six_d_index(3) == Fraction(3, 1)
    def test_five_d_index_function(self): assert five_d_index(3) == Fraction(5, 2)
    def test_index_difference_is_defect(self): assert IND_6D - IND_5D == APS_DEFECT
    def test_five_d_index_other_c1(self): assert five_d_index(4) == Fraction(7, 2)


class TestPillar870Bridge:
    def test_n_gen_6d(self): assert N_GEN_6D == 3
    def test_bridge_verified(self): assert BRIDGE_VERIFIED is True
    def test_five_d_nogo_reproduced(self): assert FIVE_D_NOGO_REPRODUCED is True
    def test_five_d_index_non_integer(self): assert IND_5D.denominator != 1
    def test_degeneracy_independent(self): assert DEGENERACY_INDEPENDENT is True
    def test_n_gen_matches_6d_index(self): assert Fraction(N_GEN_6D, 1) == IND_6D


class TestPillar870Summary:
    def test_summary_gate(self): assert aps_bundle_bridge_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert aps_bundle_bridge_summary()["pillar"] == 870
    def test_summary_lean4(self): assert aps_bundle_bridge_summary()["lean4_total_after"] == 2431
    def test_summary_bridge_verified(self):
        assert aps_bundle_bridge_summary()["bridge_verified"] is True
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_present(self):
        assert len(aps_bundle_bridge_summary()["epistemic_status"]) > 10
