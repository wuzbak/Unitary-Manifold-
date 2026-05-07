# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for 6D T²/Z₃ Metric (Track B, Rung 1)."""

import math
import pytest

from src.sixd.metric_6d import (
    N_W, K_CS,
    TAU_T2,
    Z3_FIXED_POINTS,
    N_FIXED_POINTS,
    N_GEN_FROM_T2Z3,
    SU3_ROOT_ANGLE_DEG,
    R_T2_OVER_R_S1,
    t2_lattice_vectors,
    z3_fixed_points,
    kk_mass_spectrum_6d,
    t2_metric_tensor,
    sixd_metric_components,
    generation_fixed_point_positions,
    k_cs_6d_compatibility,
    metric_6d_summary,
)


class TestModuleConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_tau_t2_equilateral(self):
        # τ = e^{2πi/3}: |τ| = 1
        assert abs(TAU_T2) == pytest.approx(1.0, rel=1e-10)

    def test_tau_t2_cubed_is_1(self):
        assert abs(TAU_T2 ** 3 - 1.0) < 1e-10

    def test_tau_t2_angle(self):
        # Angle of τ = 2π/3 = 120°
        import cmath
        angle_deg = math.degrees(cmath.phase(TAU_T2))
        assert angle_deg == pytest.approx(120.0, abs=1e-6)

    def test_n_fixed_points(self):
        assert N_FIXED_POINTS == 3

    def test_n_gen_from_t2z3(self):
        assert N_GEN_FROM_T2Z3 == 3

    def test_su3_root_angle(self):
        assert SU3_ROOT_ANGLE_DEG == pytest.approx(120.0)

    def test_r_t2_over_r_s1_is_1_over_kcs(self):
        assert R_T2_OVER_R_S1 == pytest.approx(1.0 / K_CS)

    def test_z3_fixed_points_is_tuple_of_3(self):
        assert isinstance(Z3_FIXED_POINTS, tuple)
        assert len(Z3_FIXED_POINTS) == 3

    def test_first_fixed_point_is_zero(self):
        assert abs(Z3_FIXED_POINTS[0]) < 1e-10


class TestT2LatticeVectors:
    def test_returns_two_vectors(self):
        e1, e2 = t2_lattice_vectors()
        assert isinstance(e1, complex)
        assert isinstance(e2, complex)

    def test_e1_is_real(self):
        e1, _ = t2_lattice_vectors(L=1.0)
        assert abs(e1.imag) < 1e-10

    def test_e1_magnitude_equals_L(self):
        L = 2.5
        e1, _ = t2_lattice_vectors(L)
        assert abs(e1) == pytest.approx(L)

    def test_e2_magnitude_equals_L(self):
        L = 2.5
        _, e2 = t2_lattice_vectors(L)
        assert abs(e2) == pytest.approx(L)

    def test_angle_between_e1_e2_is_120_deg(self):
        e1, e2 = t2_lattice_vectors(L=1.0)
        import cmath
        angle_diff = cmath.phase(e2 / e1)
        angle_deg = math.degrees(angle_diff)
        assert abs(angle_deg) == pytest.approx(120.0, abs=1e-5)


class TestZ3FixedPoints:
    def test_returns_list_of_3(self):
        fps = z3_fixed_points()
        assert len(fps) == 3

    def test_all_entries_are_dicts(self):
        for fp in z3_fixed_points():
            assert isinstance(fp, dict)

    def test_first_fp_at_origin(self):
        fps = z3_fixed_points(L=1.0)
        assert abs(fps[0]["position"]) < 1e-10

    def test_all_have_generation_label(self):
        for fp in z3_fixed_points():
            assert "generation_label" in fp

    def test_all_have_physical_role(self):
        for fp in z3_fixed_points():
            assert "physical_role" in fp


class TestKKMassSpectrum6D:
    def test_returns_list(self):
        result = kk_mass_spectrum_6d()
        assert isinstance(result, list)
        assert len(result) > 0

    def test_all_masses_positive(self):
        for mode in kk_mass_spectrum_6d():
            assert mode["mass_in_mkk"] > 0

    def test_sorted_by_mass(self):
        spectrum = kk_mass_spectrum_6d()
        masses = [m["mass_in_mkk"] for m in spectrum]
        assert masses == sorted(masses)

    def test_rs1_modes_present(self):
        types = [m["type"] for m in kk_mass_spectrum_6d()]
        assert "RS1" in types

    def test_t2_modes_heavier_than_rs1(self):
        spectrum = kk_mass_spectrum_6d()
        rs1_masses = [m["mass_in_mkk"] for m in spectrum if m["type"] == "RS1"]
        t2_masses = [m["mass_in_mkk"] for m in spectrum if m["type"] == "T²"]
        if rs1_masses and t2_masses:
            assert min(t2_masses) > min(rs1_masses)


class TestT2MetricTensor:
    def test_returns_dict(self):
        result = t2_metric_tensor()
        assert isinstance(result, dict)

    def test_g11_is_L_squared(self):
        result = t2_metric_tensor(L=2.0)
        assert result["g_11"] == pytest.approx(4.0)

    def test_g22_equals_g11(self):
        result = t2_metric_tensor()
        assert result["g_22"] == result["g_11"]

    def test_g12_is_minus_half_g11(self):
        result = t2_metric_tensor(L=1.0)
        assert result["g_12"] == pytest.approx(-0.5 * result["g_11"])

    def test_area_is_sqrt3_over_2(self):
        result = t2_metric_tensor(L=1.0)
        assert result["area"] == pytest.approx(math.sqrt(3.0) / 2.0, rel=1e-6)

    def test_determinant_positive(self):
        result = t2_metric_tensor()
        assert result["determinant"] > 0


class TestSixDMetricComponents:
    def test_returns_dict(self):
        result = sixd_metric_components()
        assert isinstance(result, dict)

    def test_warp_at_uv_brane_is_1(self):
        # y/πR = 0 → warp = exp(0) = 1
        result = sixd_metric_components(y_over_pi_r=0.0)
        assert result["warp_factor_4d"] == pytest.approx(1.0)

    def test_warp_decreases_with_y(self):
        r0 = sixd_metric_components(y_over_pi_r=0.0)
        r1 = sixd_metric_components(y_over_pi_r=1.0)
        assert r0["warp_factor_4d"] > r1["warp_factor_4d"]

    def test_total_dimensions_is_6(self):
        result = sixd_metric_components()
        assert result["total_dimensions"] == 6

    def test_g_yy_is_1(self):
        result = sixd_metric_components()
        assert result["g_yy"] == pytest.approx(1.0)


class TestGenerationFixedPointPositions:
    def test_returns_dict(self):
        result = generation_fixed_point_positions()
        assert isinstance(result, dict)

    def test_n_fixed_points_is_3(self):
        result = generation_fixed_point_positions()
        assert result["n_fixed_points"] == 3

    def test_n_gen_is_3(self):
        result = generation_fixed_point_positions()
        assert result["n_gen_from_geometry"] == 3

    def test_kill_switch_passes(self):
        result = generation_fixed_point_positions()
        assert result["bootstrap_kill_switch"]["result"] is True

    def test_su3_connection_present(self):
        result = generation_fixed_point_positions()
        assert "SU(3)" in result["su3_connection"]

    def test_anchor_status_derived(self):
        result = generation_fixed_point_positions()
        assert "ANCHOR DERIVED" in result["anchor_status"]


class TestKCS6DCompatibility:
    def test_returns_dict(self):
        result = k_cs_6d_compatibility()
        assert isinstance(result, dict)

    def test_compatible_is_true(self):
        result = k_cs_6d_compatibility()
        assert result["compatible"] is True

    def test_k_cs_rs1_matches(self):
        result = k_cs_6d_compatibility()
        assert result["k_cs_rs1"] == K_CS

    def test_t2_contribution_is_1(self):
        result = k_cs_6d_compatibility()
        assert result["k_cs_t2_contribution"] == pytest.approx(1.0)


class TestMetric6DSummary:
    def test_returns_dict(self):
        result = metric_6d_summary()
        assert isinstance(result, dict)

    def test_n_fixed_points_is_3(self):
        result = metric_6d_summary()
        assert result["n_fixed_points"] == 3

    def test_n_gen_from_t2z3_is_3(self):
        result = metric_6d_summary()
        assert result["n_gen_from_t2z3"] == 3

    def test_bootstrap_status_solid(self):
        result = metric_6d_summary()
        assert "SOLID" in result["bootstrap_status"]
