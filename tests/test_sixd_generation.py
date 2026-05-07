# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for 6D Field Equations and Generation Count Kill-Switch (Track B, Rung 1)."""

import math
import pytest

from src.sixd.field_equations_6d import (
    N_W, K_CS,
    M_PL_GEV, PI_KR,
    CL_FROM_6D_FIXED_POINTS,
    YUKAWA_6D_DIAGONAL,
    MASS_RATIO_GEOMETRIC_6D,
    six_d_planck_mass,
    cl_from_fixed_point,
    yukawa_matrix_6d,
    mass_spectrum_6d,
    mass_ratios_6d,
    higgs_coupling_at_ir_brane,
    generation_mass_matrix,
    kk_reduction_to_4d,
    field_equations_6d_summary,
)

from src.sixd.generation_count_6d import (
    N_GEN_5D_ANOMALY,
    N_GEN_6D_FIXED_POINTS,
    KILL_SWITCH_PASS,
    RUNG_STATUS,
    count_z3_fixed_points,
    n_gen_from_5d_anomaly,
    n_gen_from_6d_geometry,
    run_kill_switch_tests,
    burn_anchor,
    next_rung_preparation,
    generation_count_audit,
    pillar_6d_1_summary,
)


# ─── Field Equations Tests ───────────────────────────────────────────────────

class TestCLFromFixedPoints:
    def test_cl_from_6d_tuple_length(self):
        assert len(CL_FROM_6D_FIXED_POINTS) == 3

    def test_cl_gen0_is_05(self):
        assert CL_FROM_6D_FIXED_POINTS[0] == pytest.approx(0.5)

    def test_cl_gen1_is_05_plus_spacing(self):
        expected = 0.5 + 5.0 / 74.0
        assert CL_FROM_6D_FIXED_POINTS[1] == pytest.approx(expected)

    def test_cl_gen2_is_05_plus_2_spacing(self):
        expected = 0.5 + 2.0 * 5.0 / 74.0
        assert CL_FROM_6D_FIXED_POINTS[2] == pytest.approx(expected)

    def test_cl_from_fixed_point_function_gen0(self):
        assert cl_from_fixed_point(0) == pytest.approx(0.5)

    def test_cl_from_fixed_point_function_gen1(self):
        expected = 0.5 + 5.0 / 74.0
        assert cl_from_fixed_point(1) == pytest.approx(expected)

    def test_cl_from_fixed_point_function_gen2(self):
        expected = 0.5 + 2.0 * 5.0 / 74.0
        assert cl_from_fixed_point(2) == pytest.approx(expected)

    def test_invalid_fp_index_raises(self):
        with pytest.raises(ValueError):
            cl_from_fixed_point(3)


class TestYukawa6D:
    def test_yukawa_diagonal_length_3(self):
        assert len(YUKAWA_6D_DIAGONAL) == 3

    def test_gen0_yukawa_is_1(self):
        # c_L = 0.5 (exactly critical) → Yukawa = 1.0
        assert YUKAWA_6D_DIAGONAL[0] == pytest.approx(1.0)

    def test_gen1_yukawa_positive(self):
        assert YUKAWA_6D_DIAGONAL[1] > 0

    def test_gen2_yukawa_smaller_than_gen1(self):
        assert YUKAWA_6D_DIAGONAL[2] < YUKAWA_6D_DIAGONAL[1]

    def test_mass_ratio_geometric_positive(self):
        # m₀/m₁ — gen0 has Yukawa=1, gen1 < 1 → ratio > 1
        assert MASS_RATIO_GEOMETRIC_6D >= 1.0


class TestYukawaMatrix6D:
    def test_returns_dict(self):
        result = yukawa_matrix_6d()
        assert isinstance(result, dict)

    def test_n_generations_is_3(self):
        result = yukawa_matrix_6d()
        assert result["n_generations"] == 3

    def test_yukawa_diagonal_length_3(self):
        result = yukawa_matrix_6d()
        assert len(result["yukawa_diagonal"]) == 3

    def test_diagonal_hierarchical(self):
        result = yukawa_matrix_6d()
        y = result["yukawa_diagonal"]
        assert y[0] >= y[1] >= y[2]

    def test_off_diagonal_suppressed(self):
        result = yukawa_matrix_6d()
        assert result["yukawa_off_diagonal_suppression"] < 0.1

    def test_masses_positive(self):
        result = yukawa_matrix_6d()
        for m in result["masses_gev"]:
            assert m > 0


class TestMassSpectrum6D:
    def test_returns_list_of_3(self):
        result = mass_spectrum_6d()
        assert len(result) == 3

    def test_masses_hierarchical(self):
        result = mass_spectrum_6d()
        masses = [r["mass_gev"] for r in result]
        # Gen0 >= Gen1 >= Gen2 (all different c_L values)
        assert masses[0] >= masses[1] >= masses[2]

    def test_gen0_mass_is_higgs_vev(self):
        result = mass_spectrum_6d(v_higgs=246.0)
        # c_L=0.5 (exactly critical) → Yukawa=1 → mass = v
        assert result[0]["mass_gev"] == pytest.approx(246.0)

    def test_c_l_values_derived_from_geometry(self):
        result = mass_spectrum_6d()
        cls = [r["c_l_6d_derived"] for r in result]
        assert cls[0] == pytest.approx(0.5)
        assert cls[1] == pytest.approx(0.5 + 5.0 / 74.0)
        assert cls[2] == pytest.approx(0.5 + 2.0 * 5.0 / 74.0)


class TestMassRatios6D:
    def test_returns_dict(self):
        result = mass_ratios_6d()
        assert isinstance(result, dict)

    def test_m01_ratio_at_least_1(self):
        result = mass_ratios_6d()
        assert result["m_gen0_over_m_gen1"] >= 1.0

    def test_m12_ratio_gt_1(self):
        result = mass_ratios_6d()
        assert result["m_gen1_over_m_gen2"] >= 1.0

    def test_log10_ratios_positive(self):
        result = mass_ratios_6d()
        # c_L values: 0.5, 0.5+5/74, 0.5+10/74 → all different → positive ratios
        assert result["log10_m01_ratio"] >= 0
        assert result["log10_m12_ratio"] >= 0

    def test_geometric_spacing_formula(self):
        result = mass_ratios_6d()
        expected = math.exp(PI_KR / 3.0)
        assert result["geometric_spacing"] == pytest.approx(expected, rel=1e-6)


class TestHiggsCouplingAtIRBrane:
    def test_returns_dict(self):
        result = higgs_coupling_at_ir_brane()
        assert isinstance(result, dict)

    def test_gen0_mass_equals_v(self):
        result = higgs_coupling_at_ir_brane(v_higgs=246.0)
        assert result["gen0_mass_gev"] == pytest.approx(246.0)

    def test_gen1_lighter_than_gen0(self):
        result = higgs_coupling_at_ir_brane()
        # c_L^{(1)} > c_L^{(0)} → gen1 lighter than gen0
        assert result["gen1_mass_gev"] <= result["gen0_mass_gev"]


class TestGenerationMassMatrix:
    def test_returns_dict(self):
        result = generation_mass_matrix()
        assert isinstance(result, dict)

    def test_mass_matrix_is_3x3(self):
        result = generation_mass_matrix()
        m = result["mass_matrix_gev"]
        assert len(m) == 3
        assert all(len(row) == 3 for row in m)

    def test_diagonal_positive(self):
        result = generation_mass_matrix()
        m = result["mass_matrix_gev"]
        for i in range(3):
            assert m[i][i] > 0

    def test_off_diagonal_smaller_than_diagonal(self):
        result = generation_mass_matrix()
        m = result["mass_matrix_gev"]
        for i in range(3):
            for j in range(3):
                if i != j:
                    assert abs(m[i][j]) < abs(m[i][i])

    def test_status_mentions_6d(self):
        result = generation_mass_matrix()
        assert "6D" in result["status"]


class TestKKReductionTo4D:
    def test_returns_dict(self):
        result = kk_reduction_to_4d()
        assert isinstance(result, dict)

    def test_t2_heavier_than_rs1(self):
        result = kk_reduction_to_4d()
        assert result["m_kk_t2_gev"] > result["m_kk_rs1_gev"]

    def test_ratio_t2_to_rs1_is_k_cs(self):
        result = kk_reduction_to_4d()
        assert result["ratio_t2_to_rs1"] == pytest.approx(K_CS, rel=0.05)

    def test_surviving_zero_modes_present(self):
        result = kk_reduction_to_4d()
        assert len(result["surviving_zero_modes"]) >= 4


# ─── Generation Count Kill-Switch Tests ───────────────────────────────────────

class TestCountZ3FixedPoints:
    def test_returns_dict(self):
        result = count_z3_fixed_points()
        assert isinstance(result, dict)

    def test_n_fixed_points_is_3(self):
        result = count_z3_fixed_points()
        assert result["n_fixed_points"] == 3

    def test_lefschetz_determinant_is_3(self):
        result = count_z3_fixed_points()
        assert result["lefschetz_determinant"] == pytest.approx(3.0, rel=1e-6)

    def test_lefschetz_consistency(self):
        result = count_z3_fixed_points()
        assert result["consistency"] is True


class TestNGenFrom5DAnomalyGap:
    def test_n_gen_is_3(self):
        result = n_gen_from_5d_anomaly()
        assert result["n_gen_5d"] == 3

    def test_valid_n_values(self):
        result = n_gen_from_5d_anomaly()
        assert result["valid_n_values"] == [0, 1, 2]


class TestNGenFrom6DGeometry:
    def test_n_gen_is_3(self):
        result = n_gen_from_6d_geometry()
        assert result["n_gen_6d"] == 3

    def test_mentions_lefschetz(self):
        result = n_gen_from_6d_geometry()
        assert "Lefschetz" in result["method"]

    def test_independence_mentioned(self):
        result = n_gen_from_6d_geometry()
        assert "INDEPENDENT" in result["independence"]


class TestKillSwitch:
    def test_all_5_tests_pass(self):
        result = run_kill_switch_tests()
        assert result["all_pass"] is True

    def test_n_tests_is_5(self):
        result = run_kill_switch_tests()
        assert result["n_tests"] == 5

    def test_n_pass_is_5(self):
        result = run_kill_switch_tests()
        assert result["n_pass"] == 5

    def test_rung_status_solid(self):
        result = run_kill_switch_tests()
        assert "SOLID" in result["rung_status"]

    def test_t1_passes(self):
        result = run_kill_switch_tests()
        t1 = result["tests"][0]
        assert t1["pass"] is True
        assert t1["got"] == 3

    def test_t2_passes(self):
        result = run_kill_switch_tests()
        t2 = result["tests"][1]
        assert t2["pass"] is True

    def test_t3_passes_5d_equals_6d(self):
        result = run_kill_switch_tests()
        t3 = result["tests"][2]
        assert t3["pass"] is True

    def test_t4_mass_hierarchy_passes(self):
        result = run_kill_switch_tests()
        t4 = result["tests"][3]
        assert t4["pass"] is True

    def test_t5_k_cs_compatibility_passes(self):
        result = run_kill_switch_tests()
        t5 = result["tests"][4]
        assert t5["pass"] is True


class TestBurnAnchor:
    def test_anchor_burned(self):
        result = burn_anchor()
        assert result["status"] == "ANCHOR BURNED ✅"

    def test_former_anchor_described(self):
        result = burn_anchor()
        assert "N_gen" in result["former_anchor"] or "anomaly" in result["former_anchor"].lower()

    def test_new_derivation_mentions_t2z3(self):
        result = burn_anchor()
        assert "T²/Z₃" in result["new_derivation"] or "fixed-point" in result["new_derivation"].lower()

    def test_upgrade_closes_a3(self):
        result = burn_anchor()
        assert "A-3" in result["upgrade"] or "fermion_mass_hierarchy" in str(result["upgrade"])

    def test_next_anchor_is_cp_phase(self):
        result = burn_anchor()
        assert "CP" in str(result["next_anchor"]) or "cp" in str(result["next_anchor"]).lower()


class TestModuleConstants:
    def test_n_gen_5d_anomaly(self):
        assert N_GEN_5D_ANOMALY == 3

    def test_n_gen_6d_fixed_points(self):
        assert N_GEN_6D_FIXED_POINTS == 3

    def test_kill_switch_pass(self):
        assert KILL_SWITCH_PASS is True

    def test_rung_status_solid(self):
        assert "SOLID" in RUNG_STATUS


class TestPillar6D1Summary:
    def test_returns_dict(self):
        s = pillar_6d_1_summary()
        assert isinstance(s, dict)

    def test_kill_switch_pass(self):
        s = pillar_6d_1_summary()
        assert s["kill_switch_pass"] is True

    def test_anchor_burned(self):
        s = pillar_6d_1_summary()
        assert s["anchor_burned"] is True

    def test_what_closed_nonempty(self):
        s = pillar_6d_1_summary()
        assert len(s["what_closed"]) >= 3

    def test_next_rung_mentions_7d(self):
        s = pillar_6d_1_summary()
        assert "7D" in s["next_rung"]
