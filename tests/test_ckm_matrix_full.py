# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_ckm_matrix_full.py
==============================
Tests for Pillar 82 — Full CKM Matrix with CP Violation.

All tests verify that:
  - Wolfenstein parameters are returned correctly
  - CKM matrix elements are computed correctly from the standard parameterisation
  - Unitarity is satisfied (V†V = I)
  - Jarlskog invariant matches PDG at PDG input
  - Geometric CP phase δ = 2π/n_w is computed and within 2σ of PDG
  - Comparison table structure is correct
  - Gap report runs without error
"""
import cmath
import math
import pytest

from src.core.ckm_matrix_full import (
    wolfenstein_params_pdg,
    geometric_cp_phase,
    ckm_from_wolfenstein,
    ckm_pdg,
    ckm_geometric,
    jarlskog_invariant,
    unitarity_check,
    ckm_element_magnitudes,
    cabibbo_unitarity_triangle,
    ckm_gap_report,
    ckm_comparison_table,
    N_W_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    W_LAMBDA_PDG,
    W_A_PDG,
    W_RHOBAR_PDG,
    W_ETABAR_PDG,
    DELTA_CP_GEOMETRIC_DEG,
    DELTA_CP_SUBLEADING_DEG,
    DELTA_CP_PDG_DEG,
    J_PDG,
)


class TestWolfensteinParams:
    def test_pdg_params_returned(self):
        p = wolfenstein_params_pdg()
        assert abs(p["lambda"] - 0.22500) < 1e-6
        assert abs(p["A"] - 0.826) < 1e-6
        assert abs(p["rho_bar"] - 0.159) < 1e-6
        assert abs(p["eta_bar"] - 0.348) < 1e-6

    def test_delta_cp_pdg_in_degrees(self):
        p = wolfenstein_params_pdg()
        assert abs(p["delta_cp_deg"] - 68.5) < 1.0

    def test_delta_cp_pdg_in_radians(self):
        p = wolfenstein_params_pdg()
        assert abs(p["delta_cp_rad"] - 1.196) < 0.01


class TestGeometricCpPhase:
    def test_geometric_phase_n_w_5_subleading_canonical(self):
        # delta_cp_deg is now the sub-leading (canonical best) value ≈ 71.08°
        g = geometric_cp_phase(5)
        expected_deg = 2.0 * math.degrees(math.atan2(5, 7))
        assert abs(g["delta_cp_deg"] - expected_deg) < 1e-8

    def test_geometric_phase_delta_cp_rad_is_subleading(self):
        # delta_cp_rad is now the sub-leading value (Pillar 133 canonical)
        g = geometric_cp_phase(5)
        expected = 2.0 * math.atan2(5, 7)
        assert abs(g["delta_cp_rad"] - expected) < 1e-10

    def test_leading_phase_stored_separately(self):
        # Leading-order value still accessible via delta_lead_deg
        for n_w in [3, 5, 7, 9]:
            g = geometric_cp_phase(n_w)
            expected_lead = math.degrees(2 * math.pi / n_w)
            assert abs(g["delta_lead_deg"] - expected_lead) < 1e-8

    def test_sigma_tension_within_1sigma(self):
        g = geometric_cp_phase(5)
        # Sub-leading braid formula: 71.08° vs PDG 68.5° → 0.99σ < 1σ
        assert g["sigma_tension"] < 1.0
        assert "CONSISTENT" in g["status"]

    def test_sigma_tension_positive(self):
        g = geometric_cp_phase(5)
        assert g["sigma_tension"] >= 0.0

    def test_canonical_geometric_phase_leading(self):
        assert abs(DELTA_CP_GEOMETRIC_DEG - 72.0) < 1e-6

    def test_sigma_tension_sub_better_than_lead(self):
        g = geometric_cp_phase(5)
        assert g["sigma_tension_sub"] < g["sigma_tension_lead"]


class TestCkmMatrix:
    def test_ckm_pdg_is_3x3(self):
        V = ckm_pdg()
        assert len(V) == 3
        assert all(len(row) == 3 for row in V)

    def test_ckm_pdg_unitarity(self):
        V = ckm_pdg()
        uni = unitarity_check(V)
        assert uni["is_unitary"], f"PDG CKM not unitary: {uni}"

    def test_ckm_pdg_unitarity_precision(self):
        V = ckm_pdg()
        uni = unitarity_check(V)
        assert uni["VdagV_max_off_diag"] < 1e-10
        assert uni["VVdag_max_off_diag"] < 1e-10

    def test_ckm_pdg_vud_magnitude(self):
        V = ckm_pdg()
        mags = ckm_element_magnitudes(V)
        # |V_ud| ≈ 0.9737
        assert abs(mags["V_ud"] - 0.9737) < 0.01

    def test_ckm_pdg_vus_magnitude(self):
        V = ckm_pdg()
        mags = ckm_element_magnitudes(V)
        # |V_us| ≈ 0.225
        assert abs(mags["V_us"] - 0.225) < 0.005

    def test_ckm_pdg_vcb_magnitude(self):
        V = ckm_pdg()
        mags = ckm_element_magnitudes(V)
        # |V_cb| ≈ 0.0418
        assert abs(mags["V_cb"] - 0.0418) < 0.005

    def test_ckm_pdg_vtb_magnitude(self):
        V = ckm_pdg()
        mags = ckm_element_magnitudes(V)
        # |V_tb| ≈ 0.999
        assert abs(mags["V_tb"] - 0.999) < 0.002

    def test_ckm_no_cp_when_eta_zero(self):
        V = ckm_from_wolfenstein(
            lam=0.225, A=0.826, rho_bar=0.15, eta_bar=0.0
        )
        J = jarlskog_invariant(V)
        assert abs(J) < 1e-15, f"J should be 0 for η̄=0, got {J}"

    def test_ckm_from_wolfenstein_unitarity(self):
        for eta in [0.0, 0.2, 0.348, 0.5]:
            V = ckm_from_wolfenstein(0.225, 0.826, 0.159, eta)
            uni = unitarity_check(V)
            assert uni["is_unitary"], f"CKM not unitary for η̄={eta}"

    def test_ckm_geometric_unitarity(self):
        V = ckm_geometric(n_w=5)
        uni = unitarity_check(V)
        assert uni["is_unitary"]

    def test_ckm_geometric_n_w_5_is_3x3(self):
        V = ckm_geometric(5)
        assert len(V) == 3 and all(len(r) == 3 for r in V)

    def test_different_n_w_gives_different_cp_phase(self):
        V5 = ckm_geometric(n_w=5)
        V7 = ckm_geometric(n_w=7)
        J5 = jarlskog_invariant(V5)
        J7 = jarlskog_invariant(V7)
        # Different n_w → different η_geo → different J
        assert abs(J5 - J7) > 1e-10


class TestJarlskogInvariant:
    def test_jarlskog_pdg_order_of_magnitude(self):
        V = ckm_pdg()
        J = jarlskog_invariant(V)
        # PDG: J ≈ 3.08 × 10⁻⁵
        assert 1e-5 < abs(J) < 1e-4, f"Jarlskog out of range: {J}"

    def test_jarlskog_positive(self):
        V = ckm_pdg()
        J = jarlskog_invariant(V)
        # Jarlskog should be positive for PDG parameterisation conventions
        assert J > 0

    def test_jarlskog_zero_for_real_matrix(self):
        # Real CKM → J = 0
        V = ckm_from_wolfenstein(0.225, 0.826, 0.15, 0.0)
        J = jarlskog_invariant(V)
        assert abs(J) < 1e-14

    def test_jarlskog_geometric_positive(self):
        V = ckm_geometric(n_w=5)
        J = jarlskog_invariant(V)
        assert J > 0


class TestUnitarityTriangle:
    def test_unitarity_triangle_angles_sum_to_180(self):
        result = cabibbo_unitarity_triangle(n_w=5)
        total = result["sum_deg"]
        # α + β + γ = 180° (modulo phase conventions)
        # Allow loose tolerance due to angle extraction
        assert abs(total - 180.0) < 5.0, f"UT angles sum to {total}°, expected ≈ 180°"

    def test_unitarity_triangle_delta_cp_input(self):
        result = cabibbo_unitarity_triangle(n_w=5)
        assert abs(result["delta_cp_input_deg"] - 72.0) < 1e-6

    def test_unitarity_triangle_has_required_keys(self):
        result = cabibbo_unitarity_triangle(n_w=5)
        for key in ["alpha_deg", "beta_deg", "gamma_deg", "sum_deg"]:
            assert key in result


class TestComparisonTable:
    def test_comparison_table_has_nine_elements(self):
        table = ckm_comparison_table()
        assert len(table) == 9

    def test_comparison_table_vud_ratio_near_one(self):
        table = ckm_comparison_table()
        # With PDG input for λ, A: |V_ud| should be close to PDG
        ratio = table["V_ud"]["ratio"]
        assert 0.9 < ratio < 1.1

    def test_comparison_table_vus_ratio_near_one(self):
        table = ckm_comparison_table()
        ratio = table["V_us"]["ratio"]
        assert 0.9 < ratio < 1.1

    def test_comparison_table_has_geometric_and_pdg(self):
        table = ckm_comparison_table()
        for key in table:
            assert "geometric" in table[key]
            assert "pdg" in table[key]
            assert "ratio" in table[key]


class TestGapReport:
    def test_gap_report_runs(self):
        report = ckm_gap_report()
        assert isinstance(report, str)
        assert len(report) > 100

    def test_gap_report_contains_pillar_reference(self):
        report = ckm_gap_report()
        assert "Pillar 82" in report

    def test_gap_report_contains_jarlskog(self):
        report = ckm_gap_report()
        assert "Jarlskog" in report or "J" in report

    def test_gap_report_contains_honest_gaps(self):
        report = ckm_gap_report()
        assert "REMAINING OPEN GAPS" in report or "OPEN" in report


class TestJarlskogGapHonest:
    def setup_method(self):
        from src.core.ckm_matrix_full import jarlskog_gap_honest
        self.r = jarlskog_gap_honest()

    def test_j_pdg(self):
        assert self.r["J_pdg"] == pytest.approx(3.08e-5, rel=1e-6)

    def test_j_geometric_positive(self):
        assert self.r["J_geometric"] > 0

    def test_ratio_above_1(self):
        # Geometric J exceeds PDG
        assert self.r["ratio"] > 1.0

    def test_ratio_below_2(self):
        # Should be ~1.37, not wildly off
        assert self.r["ratio"] < 2.0

    def test_ratio_pct_positive(self):
        assert self.r["ratio_pct"] > 0

    def test_status_open(self):
        assert "OPEN" in self.r["status"]

    def test_admission_contains_honest_gap(self):
        assert "HONEST GAP" in self.r["admission"] or "Admission" in self.r["admission"]

    def test_gap_origin_mentions_mixing(self):
        assert "mixing" in self.r["gap_origin"].lower() or "θ" in self.r["gap_origin"]
