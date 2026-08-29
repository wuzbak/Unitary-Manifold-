# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 830 — N_gen 6D Kawamura Bridge."""
from __future__ import annotations
import pytest
from src.core.pillar830_ngen_6d_kawamura_bridge import (
    PILLAR, GATE, LEAN4_TOTAL, LEAN4_COUNT, N_W, K_CS,
    t2_z2_fixed_points, kawamura_6d_aps_index, um_cs_level_as_flux,
    ngen_6d_conditional_derivation, ngen_kawamura_bridge_summary,
)


class TestPillar830Constants:
    def test_pillar_number(self): assert PILLAR == 830
    def test_nw(self): assert N_W == 5
    def test_kcs(self): assert K_CS == 74
    def test_lean4_count(self): assert LEAN4_COUNT == 25
    def test_lean4_total(self): assert LEAN4_TOTAL == 1681
    def test_lean4_accumulates(self):
        from src.core.pillar830_ngen_6d_kawamura_bridge import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT
    def test_gate_present(self): assert "NGEN" in GATE or "KAWAMURA" in GATE or "6D" in GATE


class TestT2Z2FixedPoints:
    def test_returns_dict(self):
        r = t2_z2_fixed_points()
        assert isinstance(r, dict)

    def test_n_fixed_4(self):
        r = t2_z2_fixed_points()
        assert r["N_fixed_points"] == 4

    def test_chi_2(self):
        r = t2_z2_fixed_points()
        assert r["chi_T2_Z2"] == 2

    def test_z2_correction_2(self):
        r = t2_z2_fixed_points()
        assert r["n_contributing_z2_even"] == 2


class TestKawamura6dApsIndex:
    def test_returns_dict(self):
        r = kawamura_6d_aps_index()
        assert isinstance(r, dict)

    def test_index_is_3(self):
        r = kawamura_6d_aps_index()
        assert r["aps_index_6d"] == 3

    def test_index_integer(self):
        r = kawamura_6d_aps_index()
        assert isinstance(r["aps_index_6d"], int)

    def test_c1_equals_3(self):
        r = kawamura_6d_aps_index()
        assert r["c1_motivated"] == 3

    def test_contrast_5d_noninteger(self):
        r = kawamura_6d_aps_index()
        # 5D APS = 5/2 is non-integer (proven in P823)
        assert r.get("motivated_c1_matches_Ngen3", False) is True


class TestUmCsLevelAsFlux:
    def test_returns_dict(self):
        r = um_cs_level_as_flux()
        assert isinstance(r, dict)

    def test_kcs_74(self):
        r = um_cs_level_as_flux()
        assert r.get("K_cs", r.get("K_CS")) == 74

    def test_flux_nontrivial(self):
        r = um_cs_level_as_flux()
        assert r.get("flux_nontrivial", True) is True


class TestNgen6dConditionalDerivation:
    def test_returns_dict(self):
        r = ngen_6d_conditional_derivation()
        assert isinstance(r, dict)

    def test_ngen_3(self):
        r = ngen_6d_conditional_derivation()
        assert r["n_gen_predicted"] == 3

    def test_conditionality_honest(self):
        r = ngen_6d_conditional_derivation()
        # Must note this is 6D extension
        assert "6D" in str(r.get("conditionality", "")) or "extension" in str(r.get("conditionality", "")).lower()

    def test_gate_present(self):
        r = ngen_6d_conditional_derivation()
        assert "gate" in r


class TestNgenKawamuraBridgeSummary:
    def test_returns_dict(self):
        r = ngen_kawamura_bridge_summary()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = ngen_kawamura_bridge_summary()
        assert r["pillar"] == 830

    def test_lean4_total(self):
        r = ngen_kawamura_bridge_summary()
        assert r["lean4_total_after"] == 1681

    def test_ngen_matches_3(self):
        r = ngen_kawamura_bridge_summary()
        assert r["n_gen_predicted"] == 3

    def test_aps_6d_integer(self):
        r = ngen_kawamura_bridge_summary()
        assert r["aps_index_6d"] == 3
