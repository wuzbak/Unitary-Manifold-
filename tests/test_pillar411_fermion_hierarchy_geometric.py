# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 411 — Fermion Bulk Mass Hierarchy Geometric Closure."""
import math
import pytest

from src.core.pillar411_fermion_hierarchy_geometric import (
    PILLAR_STATUS,
    HIERARCHY_STATUS,
    N_W,
    K_CS,
    PI_KR,
    DELTA_C,
    SUPPRESSION_PER_UNIT,
    SM_FERMION_TABLE,
    yukawa_ratio,
    required_lattice_index,
    fermion_hierarchy_table,
    lattice_assignment_residuals,
    hierarchy_closure_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == "HIERARCHY_PARTIALLY_CONSTRAINED"

    def test_hierarchy_status(self):
        assert HIERARCHY_STATUS == "HIERARCHY_PARTIALLY_CONSTRAINED"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37

    def test_delta_c(self):
        assert abs(DELTA_C - 5.0 / 74.0) < 1e-12

    def test_suppression_formula(self):
        # exp(-2 × (5/74) × 37) = exp(-5)
        expected = math.exp(-5.0)
        assert abs(SUPPRESSION_PER_UNIT - expected) < 1e-10

    def test_sm_fermion_table_9_entries(self):
        assert len(SM_FERMION_TABLE) == 9

    def test_top_is_first(self):
        assert SM_FERMION_TABLE[0]["name"] == "top"

    def test_electron_is_last(self):
        assert SM_FERMION_TABLE[-1]["name"] == "electron"


class TestYukawaRatio:
    def test_top_ratio_is_1(self):
        assert abs(yukawa_ratio(0.0) - 1.0) < 1e-12

    def test_ratio_decreasing(self):
        y0 = yukawa_ratio(0.0)
        y1 = yukawa_ratio(1.0)
        y2 = yukawa_ratio(2.0)
        assert y0 > y1 > y2

    def test_formula(self):
        ell_m = 1.5
        expected = math.exp(-2.0 * DELTA_C * PI_KR * ell_m)
        result = yukawa_ratio(ell_m)
        assert abs(result - expected) < 1e-12

    def test_suppression_factor_per_unit(self):
        # yukawa_ratio(1) should equal SUPPRESSION_PER_UNIT
        assert abs(yukawa_ratio(1.0) - SUPPRESSION_PER_UNIT) < 1e-10

    def test_exp_minus_5_per_unit(self):
        # 2 × (5/74) × 37 = 5.0 exactly
        factor = 2.0 * DELTA_C * PI_KR
        assert abs(factor - 5.0) < 1e-10
        assert abs(yukawa_ratio(1.0) - math.exp(-5.0)) < 1e-10


class TestRequiredLatticeIndex:
    def test_top_is_zero(self):
        idx = required_lattice_index(173.0, 173.0)
        assert abs(idx) < 1e-10

    def test_lighter_needs_larger_index(self):
        idx_b = required_lattice_index(4.18, 173.0)
        idx_mu = required_lattice_index(0.106, 173.0)
        idx_e = required_lattice_index(0.000511, 173.0)
        assert 0 < idx_b < idx_mu < idx_e

    def test_electron_span(self):
        # Electron is ~6 orders below top → ℓ+m ≈ 6/log10(e⁵) ≈ 6/2.17 ≈ 2.8
        # but the factor is 2×(5/74)×37=5, so log reduction per unit = 5/ln(10) ≈ 2.17 decades
        idx = required_lattice_index(0.000511, 173.0)
        assert 2.0 < idx < 4.0

    def test_formula(self):
        m = 4.18
        m_top = 173.0
        factor = 2.0 * DELTA_C * PI_KR
        expected = -math.log(m / m_top) / factor
        result = required_lattice_index(m, m_top)
        assert abs(result - expected) < 1e-10


class TestFermionHierarchyTable:
    def test_returns_9_rows(self):
        table = fermion_hierarchy_table()
        assert len(table) == 9

    def test_top_ell_m_zero(self):
        table = fermion_hierarchy_table()
        top = next(r for r in table if r["name"] == "top")
        assert abs(top["ell_m_required"]) < 1e-10

    def test_hierarchy_ordering(self):
        # Top has smallest ℓ+m, electron has largest
        table = fermion_hierarchy_table()
        top = next(r for r in table if r["name"] == "top")
        electron = next(r for r in table if r["name"] == "electron")
        assert electron["ell_m_required"] > top["ell_m_required"]

    def test_all_mass_ratios_positive(self):
        table = fermion_hierarchy_table()
        for row in table:
            assert row["mass_ratio"] > 0

    def test_log10_residual_nonneg(self):
        table = fermion_hierarchy_table()
        for row in table:
            assert row["log10_residual_dex"] >= 0


class TestLatticeAssignmentResiduals:
    def test_returns_dict(self):
        data = lattice_assignment_residuals()
        assert isinstance(data, dict)

    def test_n_fermions_9(self):
        data = lattice_assignment_residuals()
        assert data["n_fermions"] == 9

    def test_suppression_per_unit(self):
        data = lattice_assignment_residuals()
        assert abs(data["suppression_per_unit"] - SUPPRESSION_PER_UNIT) < 1e-6

    def test_factor_5(self):
        # 2 × Δc × πkR = 5.0
        data = lattice_assignment_residuals()
        assert abs(data["factor_2_x_Dc_x_piKR"] - 5.0) < 0.001

    def test_within_05dex_count_positive(self):
        data = lattice_assignment_residuals()
        assert data["n_within_05dex"] > 0

    def test_span_covers_full_hierarchy(self):
        # At least 2.5 lattice units for 6 decades of hierarchy
        data = lattice_assignment_residuals()
        assert data["lattice_span_ell_m"] > 2.0


class TestHierarchyClosureVerdict:
    def test_status(self):
        verdict = hierarchy_closure_verdict()
        assert verdict["status"] == "HIERARCHY_PARTIALLY_CONSTRAINED"

    def test_previous_status(self):
        verdict = hierarchy_closure_verdict()
        assert verdict["previous_status"] == "HIERARCHY_OPEN"

    def test_n_total_is_9(self):
        verdict = hierarchy_closure_verdict()
        assert verdict["residual_summary"]["n_total"] == 9

    def test_max_residual_present(self):
        verdict = hierarchy_closure_verdict()
        assert "max_log10_residual" in verdict["residual_summary"]
        assert verdict["residual_summary"]["max_log10_residual"] >= 0

    def test_lattice_mechanism_present(self):
        verdict = hierarchy_closure_verdict()
        # String uses Unicode minus sign (−) not ASCII (-)
        assert "exp" in verdict["lattice_mechanism"]
        assert "Yukawa" in verdict["lattice_mechanism"]

    def test_verdict_contains_lattice(self):
        verdict = hierarchy_closure_verdict()
        assert "lattice" in verdict["verdict"].lower()
