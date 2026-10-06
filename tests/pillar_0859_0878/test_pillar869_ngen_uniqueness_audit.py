# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 869 — N_gen bundle degeneracy audit."""
from __future__ import annotations

import pytest

from src.sixd.pillar869_ngen_uniqueness_audit import (
    DEGENERACY_IS_ONE,
    DEGENERACY_N,
    FILTERS,
    FILTER_REDUCTION,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    MAX_U1_CHARGE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SURVIVING_BUNDLES,
    apply_filters,
    charge_bound_filter,
    ngen_uniqueness_audit_summary,
    z2_parity_filter,
)


class TestPillar869Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 869
    def test_gate(self): assert PILLAR_GATE == "NGEN_6D_BUNDLE_DEGENERACY_COMPUTED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2386
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2406
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_max_u1_charge(self): assert MAX_U1_CHARGE == 4


class TestPillar869Filters:
    def test_filter_count(self): assert len(FILTERS) == 2
    def test_filter_names(self):
        assert FILTERS == ("F1_Z2_PARITY_ODD_FLUX", "F2_E8_CHARGE_BOUND")
    def test_z2_filter_accepts_odd_flux(self):
        assert z2_parity_filter({"flux": 3, "u1_charge": 1}) is True
    def test_z2_filter_rejects_even_flux(self):
        assert z2_parity_filter({"flux": 2, "u1_charge": 1}) is False
    def test_charge_filter_accepts_small_charge(self):
        assert charge_bound_filter({"flux": 1, "u1_charge": 3}) is True
    def test_charge_filter_rejects_large_charge(self):
        assert charge_bound_filter({"flux": 1, "u1_charge": 9}) is False
    def test_charge_filter_boundary(self):
        assert charge_bound_filter({"flux": 1, "u1_charge": MAX_U1_CHARGE}) is True
    def test_apply_filters_empty_input(self): assert apply_filters([]) == []
    def test_apply_filters_removes_even_flux(self):
        rows = [{"flux": 2, "u1_charge": 1}, {"flux": 1, "u1_charge": 1}]
        assert len(apply_filters(rows)) == 1


class TestPillar869Degeneracy:
    def test_degeneracy_value(self): assert DEGENERACY_N == 2
    def test_degeneracy_not_one(self): assert DEGENERACY_IS_ONE is False
    def test_survivors_length(self): assert len(SURVIVING_BUNDLES) == DEGENERACY_N
    def test_filter_reduction(self): assert FILTER_REDUCTION == 0
    def test_all_survivors_odd_flux(self):
        assert all(row["flux"] % 2 == 1 for row in SURVIVING_BUNDLES)
    def test_all_survivors_within_charge_bound(self):
        assert all(abs(row["u1_charge"]) <= MAX_U1_CHARGE for row in SURVIVING_BUNDLES)
    def test_all_survivors_target_c1(self):
        assert all(row["c1"] == 3 for row in SURVIVING_BUNDLES)
    def test_survivor_charges(self):
        assert sorted(row["u1_charge"] for row in SURVIVING_BUNDLES) == [1, 3]
    def test_survivor_fluxes(self):
        assert sorted(row["flux"] for row in SURVIVING_BUNDLES) == [1, 3]
    def test_degeneracy_honest_not_claimed_unique(self): assert DEGENERACY_N != 1


class TestPillar869Summary:
    def test_summary_gate(self): assert ngen_uniqueness_audit_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert ngen_uniqueness_audit_summary()["pillar"] == 869
    def test_summary_lean4(self): assert ngen_uniqueness_audit_summary()["lean4_total_after"] == 2406
    def test_summary_degeneracy(self): assert ngen_uniqueness_audit_summary()["degeneracy_n"] == 2
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_remaining_open_labelled(self):
        assert all("OPEN" in item or "LIMIT" in item for item in REMAINING_OPEN)
    def test_epistemic_status_reports_degeneracy(self):
        assert "DEGENERAC" in ngen_uniqueness_audit_summary()["epistemic_status"].upper()
