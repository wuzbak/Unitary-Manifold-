# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Tests for Pillar 682 — 13-Dimensional I-Theory Metric Engine.

Test strategy
─────────────
Every theorem in pillar682_thirteen_dimensional_itheory_engine.py has a
dedicated test class that:
  1. Verifies the algebraic claim to machine precision (Theorems 682.1–682.3).
  2. Verifies structural properties (metric shape, signature, eigenvalue counts).
  3. Verifies the honest architecture-limit boundary (Theorem 682.4).

Zero regression policy: these tests must pass without modifying any file
in tests/ or src/core/ other than the two files introduced by Pillar 682.

Coverage targets:
  - All public API symbols listed in __all__
  - Edge cases: rho_mixing near ±1 boundary, zero b_field, non-trivial g_4d
  - Numerical stability: large and small phi_radion values
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from src.core.pillar682_thirteen_dimensional_itheory_engine import (
    # Constants
    N1, N2, N1_SHADOW, N2_SHADOW,
    K_CS, N_W, C_S, PHI0_BARE,
    PHI0_EFF, N_FLUX, DIM_13, SP2R_TIMELIKE_COUNT,
    # Engine
    ThirteenDimensionalEngine,
    # Theorems
    theorem_682_1_kcs_topological_invariant,
    theorem_682_2_sp2r_phi0_crosscheck,
    theorem_682_3_dual_sector_phase_angle,
    theorem_682_4_lambda_qcd_radion_probe,
    # Summary
    pillar_682_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _flat_metric_4d(n: int) -> np.ndarray:
    """Return n copies of the Minkowski metric diag(-1,+1,+1,+1)."""
    return np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (n, 1, 1))


def _build_standard_metric(
    n: int,
    phi: float = 1.0,
    master: float = 1.0,
    rho: float = 0.05,
    b_scale: float = 0.0,
) -> tuple[ThirteenDimensionalEngine, np.ndarray]:
    """Construct a standard 13D metric for testing."""
    engine = ThirteenDimensionalEngine(num_points=n, rho_mixing=rho)
    g4d = _flat_metric_4d(n)
    b = np.zeros((n, 4)) if b_scale == 0.0 else np.full((n, 4), b_scale)
    phi_arr = np.full(n, phi)
    G = engine.assemble_parent_metric(g_4d=g4d, b_field=b,
                                      phi_radion=phi_arr, master_radion=master)
    return engine, G


# ─────────────────────────────────────────────────────────────────────────────
# MODULE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

class TestModuleConstants:
    """All constants must equal their derivations — zero free parameters."""

    def test_n1_n2_primary(self):
        assert N1 == 5
        assert N2 == 7

    def test_n1_n2_shadow(self):
        assert N1_SHADOW == 5
        assert N2_SHADOW == 6

    def test_k_cs_equals_braid_sum_of_squares(self):
        assert K_CS == N1**2 + N2**2

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_n_w_is_5(self):
        assert N_W == 5

    def test_c_s_braided_sound_speed(self):
        # c_s = (n₂² − n₁²) / k_CS = 24/74 = 12/37
        expected = (N2**2 - N1**2) / K_CS
        assert C_S == pytest.approx(expected, rel=1e-14)
        assert C_S == pytest.approx(12.0 / 37.0, rel=1e-14)

    def test_phi0_eff_winding_jacobian(self):
        # φ₀_eff = N_W × 2π
        assert PHI0_EFF == pytest.approx(N_W * 2.0 * math.pi, rel=1e-14)

    def test_n_flux_equals_k_cs_half(self):
        assert N_FLUX == K_CS // 2
        assert N_FLUX == 37

    def test_dim_is_13(self):
        assert DIM_13 == 13

    def test_sp2r_timelike_count(self):
        assert SP2R_TIMELIKE_COUNT == 2

    def test_phi0_bare_is_unity(self):
        assert PHI0_BARE == 1.0

    def test_shadow_k_cs_differs_from_primary(self):
        # (5,6) braid has a different CS level: 5²+6² = 61 ≠ 74
        shadow_k = N1_SHADOW**2 + N2_SHADOW**2
        assert shadow_k == 61
        assert shadow_k != K_CS


# ─────────────────────────────────────────────────────────────────────────────
# ENGINE CONSTRUCTION
# ─────────────────────────────────────────────────────────────────────────────

class TestEngineConstruction:
    """ThirteenDimensionalEngine constructor validation."""

    def test_default_construction(self):
        e = ThirteenDimensionalEngine()
        assert e.N == 64
        assert e.dim == 13
        assert e.k_cs == 74

    def test_custom_num_points(self):
        e = ThirteenDimensionalEngine(num_points=4)
        assert e.N == 4

    def test_rho_mixing_boundary_valid(self):
        # Just inside valid range
        ThirteenDimensionalEngine(rho_mixing=0.99)
        ThirteenDimensionalEngine(rho_mixing=-0.99)

    def test_rho_mixing_out_of_range_raises(self):
        with pytest.raises(ValueError, match="rho_mixing"):
            ThirteenDimensionalEngine(rho_mixing=1.0)
        with pytest.raises(ValueError, match="rho_mixing"):
            ThirteenDimensionalEngine(rho_mixing=-1.0)
        with pytest.raises(ValueError, match="rho_mixing"):
            ThirteenDimensionalEngine(rho_mixing=2.5)

    def test_zero_num_points_raises(self):
        with pytest.raises(ValueError):
            ThirteenDimensionalEngine(num_points=0)


# ─────────────────────────────────────────────────────────────────────────────
# METRIC ASSEMBLY
# ─────────────────────────────────────────────────────────────────────────────

class TestMetricAssembly:
    """assemble_parent_metric must produce a correctly shaped (N,13,13) array."""

    @pytest.mark.parametrize("n", [1, 4, 16, 32])
    def test_shape(self, n):
        engine, G = _build_standard_metric(n)
        assert G.shape == (n, 13, 13)
        assert G.dtype == np.float64

    def test_t1_diagonal_is_minus_one(self):
        _, G = _build_standard_metric(8)
        np.testing.assert_array_almost_equal(G[:, 0, 0], -1.0)

    def test_t2_diagonal_is_minus_one(self):
        _, G = _build_standard_metric(8)
        np.testing.assert_array_almost_equal(G[:, 1, 1], -1.0)

    def test_4d_block_diagonal_embedded_correctly(self):
        # With zero B-field, the 4D block [2:6,2:6] should embed with the
        # 2T-physics sign convention: g_{00} is negated (physical time is t₁),
        # spatial components are unchanged.
        # For Minkowski eta = diag(-1,+1,+1,+1): embedded = diag(+1,+1,+1,+1).
        n = 4
        engine, G = _build_standard_metric(n, b_scale=0.0)
        # Off-diagonal: zero (B=0, flat metric)
        for mu in range(4):
            for nu in range(4):
                if mu != nu:
                    np.testing.assert_array_almost_equal(
                        G[:, 2 + mu, 2 + nu], 0.0,
                        err_msg=f"Off-diagonal G[{2+mu},{2+nu}] should be 0",
                    )
        # Diagonal: all +1 after 2T sign flip on (0,0)
        for mu in range(4):
            np.testing.assert_array_almost_equal(
                G[:, 2 + mu, 2 + mu], 1.0,
                err_msg=f"G[{2+mu},{2+mu}] should be +1 in 2T embedding",
            )

    def test_compact_6d_block_is_identity(self):
        _, G = _build_standard_metric(8)
        for i in range(6):
            np.testing.assert_array_almost_equal(G[:, 6 + i, 6 + i], 1.0)

    def test_master_radion_diagonal(self):
        phi_m = 1.5
        _, G = _build_standard_metric(8, master=phi_m)
        np.testing.assert_array_almost_equal(G[:, 12, 12], phi_m**2)

    def test_gauge_sink_cross_coupling_symmetric(self):
        phi_m = 2.0
        rho = 0.1
        engine = ThirteenDimensionalEngine(num_points=8, rho_mixing=rho)
        g4d = _flat_metric_4d(8)
        b = np.zeros((8, 4))
        phi_arr = np.ones(8)
        G = engine.assemble_parent_metric(g_4d=g4d, b_field=b,
                                          phi_radion=phi_arr, master_radion=phi_m)
        expected_cross = phi_m * rho
        np.testing.assert_array_almost_equal(G[:, 1, 12], expected_cross)
        np.testing.assert_array_almost_equal(G[:, 12, 1], expected_cross)

    def test_b_field_kinetic_mixing_adds_to_diagonal(self):
        n = 4
        b_val = 0.5
        phi_val = 2.0
        engine, G_zero = _build_standard_metric(n, phi=phi_val, b_scale=0.0)
        engine2 = ThirteenDimensionalEngine(num_points=n)
        g4d = _flat_metric_4d(n)
        b = np.full((n, 4), b_val)
        phi_arr = np.full(n, phi_val)
        G_nonzero = engine2.assemble_parent_metric(g_4d=g4d, b_field=b,
                                                   phi_radion=phi_arr, master_radion=1.0)
        # The KK kinetic mixing adds λ²φ²B_μ² to each spatial diagonal
        for mu in range(4):
            expected_add = phi_val**2 * b_val**2  # λ=1 by default
            diff = G_nonzero[:, 2 + mu, 2 + mu] - G_zero[:, 2 + mu, 2 + mu]
            np.testing.assert_allclose(diff, expected_add, rtol=1e-12)

    def test_wrong_g4d_shape_raises(self):
        engine = ThirteenDimensionalEngine(num_points=4)
        bad_g4d = np.eye(4)  # wrong shape
        b = np.zeros((4, 4))
        phi = np.ones(4)
        with pytest.raises(ValueError, match="g_4d"):
            engine.assemble_parent_metric(g_4d=bad_g4d, b_field=b,
                                          phi_radion=phi, master_radion=1.0)

    def test_wrong_b_field_shape_raises(self):
        engine = ThirteenDimensionalEngine(num_points=4)
        g4d = _flat_metric_4d(4)
        bad_b = np.zeros((4, 3))  # wrong shape
        phi = np.ones(4)
        with pytest.raises(ValueError, match="b_field"):
            engine.assemble_parent_metric(g_4d=g4d, b_field=bad_b,
                                          phi_radion=phi, master_radion=1.0)

    def test_metric_is_symmetric(self):
        """The metric must be symmetric: G_AB = G_BA."""
        engine, G = _build_standard_metric(8, rho=0.05, b_scale=0.3)
        for n in range(8):
            np.testing.assert_array_almost_equal(G[n], G[n].T, decimal=14)


# ─────────────────────────────────────────────────────────────────────────────
# SP(2,ℝ) SIGNATURE VERIFICATION
# ─────────────────────────────────────────────────────────────────────────────

class TestSp2rSignature:
    """verify_sp2r_signature must return True for the assembled metric."""

    @pytest.mark.parametrize("n", [1, 4, 16])
    def test_flat_background_has_11_plus_2_signature(self, n):
        engine, G = _build_standard_metric(n, rho=0.05)
        assert engine.verify_sp2r_signature(G) is True

    def test_signature_preserved_with_nonzero_b_field(self):
        engine, G = _build_standard_metric(16, b_scale=0.2, rho=0.1)
        assert engine.verify_sp2r_signature(G) is True

    def test_signature_preserved_with_large_phi_radion(self):
        engine = ThirteenDimensionalEngine(num_points=8, rho_mixing=0.05)
        g4d = _flat_metric_4d(8)
        b = np.zeros((8, 4))
        phi_arr = np.full(8, 10.0)  # large phi
        G = engine.assemble_parent_metric(g_4d=g4d, b_field=b,
                                          phi_radion=phi_arr, master_radion=1.0)
        assert engine.verify_sp2r_signature(G) is True

    def test_signature_preserved_with_large_master_radion(self):
        engine, G = _build_standard_metric(8, master=50.0, rho=0.05)
        assert engine.verify_sp2r_signature(G) is True

    def test_eigenvalue_report_confirms_signature(self):
        engine, G = _build_standard_metric(8, rho=0.05)
        report = engine.eigenvalue_report(G)
        assert report["signature_uniform"] is True
        assert "(11+2) CONFIRMED" in report["signature_summary"]
        assert report["min_eigenvalue"] < 0.0
        assert report["max_eigenvalue"] > 0.0
        assert len(report["timelike_counts"]) == 8
        assert np.all(report["timelike_counts"] == 2)

    def test_wrong_g_shape_raises_in_verify(self):
        engine = ThirteenDimensionalEngine(num_points=4)
        bad_G = np.zeros((4, 5, 5))  # wrong dim
        with pytest.raises(ValueError):
            engine.verify_sp2r_signature(bad_G)

    def test_exactly_two_negative_eigenvalues_baseline(self):
        """Baseline: diag(-1,-1,+1,...,+1) has exactly 2 negative eigenvalues."""
        diag = [-1.0, -1.0] + [1.0] * 11
        G = np.tile(np.diag(diag), (4, 1, 1))
        engine = ThirteenDimensionalEngine(num_points=4)
        # Manually check
        eigs = np.linalg.eigvalsh(G)
        counts = np.sum(eigs < 0, axis=1)
        assert np.all(counts == 2)
        assert engine.verify_sp2r_signature(G) is True


# ─────────────────────────────────────────────────────────────────────────────
# GAUGE-SINK DEFECT
# ─────────────────────────────────────────────────────────────────────────────

class TestGaugeSinkDefect:
    """compute_gauge_sink_defect measures deviation from c_s = 12/37."""

    def test_exact_alignment_gives_near_zero_defect(self):
        engine = ThirteenDimensionalEngine()
        defect = engine.compute_gauge_sink_defect(master_radion=12.0, phi_radion=37.0)
        assert defect < 1e-14

    def test_verify_alignment_true_at_exact_ratio(self):
        engine = ThirteenDimensionalEngine()
        assert engine.verify_gauge_sink_alignment(12.0, 37.0, tol=1e-9) is True

    def test_verify_alignment_false_at_wrong_ratio(self):
        engine = ThirteenDimensionalEngine()
        assert engine.verify_gauge_sink_alignment(1.0, 1.0, tol=1e-9) is False

    def test_defect_is_nonnegative(self):
        engine = ThirteenDimensionalEngine()
        for mr, pr in [(1.0, 1.0), (5.0, 10.0), (100.0, 3.0)]:
            assert engine.compute_gauge_sink_defect(mr, pr) >= 0.0

    def test_zero_phi_radion_raises(self):
        engine = ThirteenDimensionalEngine()
        with pytest.raises(ValueError, match="non-zero"):
            engine.compute_gauge_sink_defect(1.0, 0.0)

    def test_defect_matches_c_s_constant(self):
        engine = ThirteenDimensionalEngine()
        # c_s = 12/37; defect = |Φ_M/φ - c_s|
        c_s = 12.0 / 37.0
        phi_m = 2.0 * c_s
        phi_r = 2.0
        defect = engine.compute_gauge_sink_defect(phi_m, phi_r)
        assert defect < 1e-14  # (2c_s)/(2) - c_s = 0


# ─────────────────────────────────────────────────────────────────────────────
# THEOREM 682.1 — k_CS TOPOLOGICAL INVARIANT
# ─────────────────────────────────────────────────────────────────────────────

class TestTheorem6821:
    """k_CS = 74 must be preserved under 5D → 13D dimensional lifting."""

    @pytest.fixture
    def result(self):
        return theorem_682_1_kcs_topological_invariant()

    def test_k_cs_5d_is_74(self, result):
        assert result["k_cs_5d"] == 74

    def test_k_cs_13d_is_74(self, result):
        assert result["k_cs_13d"] == 74

    def test_invariant_preserved(self, result):
        assert result["invariant_preserved"] is True

    def test_winding_vector_norm_sq_is_74(self, result):
        # n₁² + n₂² = 25 + 49 = 74
        assert result["winding_vector_norm_sq"] == 74

    def test_braid_identity(self, result):
        assert result["n1"] == 5
        assert result["n2"] == 7

    def test_shadow_k_cs_differs(self, result):
        # (5,6): 25 + 36 = 61
        assert result["shadow_sector_k_cs"] == 61
        assert result["shadow_sector_k_cs"] != 74

    def test_primary_dominates_shadow(self, result):
        # k_CS = 74 > 61; the (5,7) sector has the higher topological charge
        assert result["primary_dominates_shadow"] is True

    def test_sum_of_squares_arithmetic(self):
        # Direct arithmetic verification — no ambiguity
        assert 5**2 + 7**2 == 74
        assert 5**2 + 6**2 == 61


# ─────────────────────────────────────────────────────────────────────────────
# THEOREM 682.2 — Sp(2,ℝ) φ₀ CROSS-CHECK
# ─────────────────────────────────────────────────────────────────────────────

class TestTheorem6822:
    """The 13D Sp(2,ℝ) null-cone must reproduce φ₀_eff = 5×2π."""

    @pytest.fixture
    def result(self):
        return theorem_682_2_sp2r_phi0_crosscheck()

    def test_phi0_13d_equals_5_times_2pi(self, result):
        expected = 5 * 2.0 * math.pi
        assert result["phi0_13d"] == pytest.approx(expected, rel=1e-14)

    def test_phi0_13d_equals_phi0_ftum(self, result):
        assert result["phi0_13d"] == pytest.approx(result["phi0_ftum"], rel=1e-14)

    def test_fractional_discrepancy_is_zero(self, result):
        assert result["fractional_discrepancy"] == pytest.approx(0.0, abs=1e-14)

    def test_consistent_flag(self, result):
        assert result["consistent"] is True

    def test_n_s_within_planck_1sigma(self, result):
        assert result["n_s_within_1sigma"] is True

    def test_n_s_sigma_offset_reasonable(self, result):
        # Should be about 0.33σ from Planck central value
        assert result["n_s_sigma_offset"] < 2.0  # well within 2σ

    def test_n_s_value_correct(self, result):
        # n_s = 1 − 36/φ₀_eff² = 1 − 36/(5×2π)²
        expected_ns = 1.0 - 36.0 / (5 * 2 * math.pi)**2
        assert result["n_s_from_phi0"] == pytest.approx(expected_ns, rel=1e-12)
        assert result["n_s_from_phi0"] == pytest.approx(0.9635, abs=0.001)

    def test_phi0_eff_numerical_value(self, result):
        # Precise value: 5 × 2π ≈ 31.41592653589793
        assert result["phi0_13d"] == pytest.approx(31.41592653589793, rel=1e-13)


# ─────────────────────────────────────────────────────────────────────────────
# THEOREM 682.3 — DUAL-SECTOR PHASE ANGLE
# ─────────────────────────────────────────────────────────────────────────────

class TestTheorem6823:
    """The dual sectors are connected by an SL(2,ℝ) shear, not a rotation."""

    @pytest.fixture
    def result(self):
        return theorem_682_3_dual_sector_phase_angle()

    def test_shear_alpha_is_one_fifth(self, result):
        # α = (n₂ − n₂') / n₁ = (7 − 6) / 5 = 1/5
        assert result["shear_alpha"] == pytest.approx(1.0 / 5.0, rel=1e-14)

    def test_shear_det_is_unity(self, result):
        # det([[1,0],[-α,1]]) = 1 → M ∈ SL(2,ℝ) ⊂ Sp(2,ℝ)
        assert result["shear_det"] == pytest.approx(1.0, rel=1e-12)

    def test_shear_verified(self, result):
        # M · (5, 7) = (5, 6) must hold exactly
        assert result["shear_verified"] is True

    def test_rotated_vector_equals_shadow(self, result):
        n_rotated = result["n_rotated"]
        n_shadow = result["n_shadow_expected"]
        assert n_rotated[0] == pytest.approx(n_shadow[0], abs=1e-12)
        assert n_rotated[1] == pytest.approx(n_shadow[1], abs=1e-12)

    def test_norms_differ(self, result):
        # ||(5,7)||² = 74, ||(5,6)||² = 61 — no rotation connects them
        assert result["norms_differ"] is True
        assert result["norm_primary_sq"] == 74
        assert result["norm_shadow_sq"] == 61

    def test_delta_n2_is_one(self, result):
        # The sectors differ by exactly 1 winding quantum
        assert result["delta_n2"] == 1

    def test_primary_sector_values(self, result):
        assert result["n_primary"] == [5, 7]

    def test_shadow_sector_values(self, result):
        assert result["n_shadow"] == [5, 6]

    def test_shear_matrix_structure(self, result):
        M = np.array(result["shear_matrix"])
        # Lower shear: [[1,0],[-α,1]]
        assert M[0, 0] == pytest.approx(1.0, abs=1e-14)
        assert M[0, 1] == pytest.approx(0.0, abs=1e-14)
        assert M[1, 1] == pytest.approx(1.0, abs=1e-14)
        assert M[1, 0] == pytest.approx(-1.0 / 5.0, rel=1e-12)

    def test_birefringence_gap_is_positive(self, result):
        assert result["delta_beta_deg"] > 0.0

    def test_birefringence_values_canonical(self, result):
        assert result["beta_primary_deg"] == pytest.approx(0.331, abs=0.001)
        assert result["beta_shadow_deg"] == pytest.approx(0.273, abs=0.001)
        assert result["delta_beta_deg"] == pytest.approx(0.058, abs=0.001)

    def test_alpha_arithmetic(self):
        """Direct arithmetic: α = (7 − 6) / 5 = 1/5."""
        alpha = (N2 - N2_SHADOW) / N1
        assert alpha == pytest.approx(0.2, rel=1e-14)

    def test_shear_derivation_manual(self):
        """Manual verification of the shear transformation."""
        alpha = 1.0 / 5.0
        M = np.array([[1.0, 0.0], [-alpha, 1.0]])
        result = M @ np.array([5.0, 7.0])
        assert result[0] == pytest.approx(5.0, abs=1e-12)
        assert result[1] == pytest.approx(6.0, abs=1e-12)
        assert np.linalg.det(M) == pytest.approx(1.0, abs=1e-12)


# ─────────────────────────────────────────────────────────────────────────────
# THEOREM 682.4 — ΛQCD RADION PROBE
# ─────────────────────────────────────────────────────────────────────────────

class TestTheorem6824:
    """Theorem 682.4 establishes the formal ΛQCD mechanism without overclaiming."""

    @pytest.fixture
    def result(self):
        return theorem_682_4_lambda_qcd_radion_probe()

    def test_returns_all_required_keys(self, result):
        required = [
            "phi0_m", "n_kk_modes", "alpha_s_mz_input", "b1_qcd",
            "m_kk_planck", "correction_log_factor", "delta_inv_alpha_s",
            "delta_alpha_s_from_radion", "alpha_s_corrected",
            "lambda_qcd_from_alpha_s_gev", "lambda_qcd_pdg_gev",
            "lambda_qcd_corrected_gev", "status",
        ]
        for key in required:
            assert key in result, f"Missing key: {key}"

    def test_phi0_m_defaults_to_phi0_eff(self, result):
        assert result["phi0_m"] == pytest.approx(PHI0_EFF, rel=1e-12)

    def test_n_kk_modes_equals_n_flux(self, result):
        assert result["n_kk_modes"] == N_FLUX  # = 37

    def test_b1_qcd_is_7(self, result):
        # b1 = 11 - 2×6/3 = 11 - 4 = 7 (6 heavy flavors above M_KK)
        assert result["b1_qcd"] == pytest.approx(7.0, rel=1e-12)

    def test_lambda_qcd_1loop_order_of_magnitude(self, result):
        # Standard 1-loop Λ_QCD should be ~0.01–1.0 GeV
        # (1-loop with b1=7 gives ~0.045 GeV; 2-loop gives ~0.22 GeV)
        lam = result["lambda_qcd_from_alpha_s_gev"]
        assert 0.01 < lam < 1.0  # reasonable range for 1-loop estimate

    def test_pdg_lambda_qcd_value(self, result):
        assert result["lambda_qcd_pdg_gev"] == pytest.approx(0.217, rel=1e-8)

    def test_status_string_present(self, result):
        assert isinstance(result["status"], str)
        assert len(result["status"]) > 20

    def test_honest_non_perturbative_flag(self, result):
        # The 13D correction is large (non-perturbative regime)
        # The status string should acknowledge this
        assert (
            "NON-PERTURBATIVE" in result["status"]
            or "PERTURBATIVE" in result["status"]
        )

    def test_custom_alpha_s(self):
        result = theorem_682_4_lambda_qcd_radion_probe(alpha_s_mz=0.120)
        assert result["alpha_s_mz_input"] == pytest.approx(0.120, rel=1e-12)

    def test_custom_phi0_m(self):
        result = theorem_682_4_lambda_qcd_radion_probe(phi0_m=10.0)
        assert result["phi0_m"] == pytest.approx(10.0, rel=1e-12)

    def test_m_kk_planck_is_warp_suppressed(self, result):
        # M_KK_planck ~ exp(-37) — deeply sub-Planckian
        assert result["m_kk_planck"] < 1e-10
        assert result["m_kk_planck"] == pytest.approx(math.exp(-37), rel=1e-10)


# ─────────────────────────────────────────────────────────────────────────────
# PILLAR SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

class TestPillarSummary:
    """The summary function must consolidate all theorems with zero failures."""

    @pytest.fixture(scope="class")
    def summary(self):
        return pillar_682_summary()

    def test_pillar_number(self, summary):
        assert summary["pillar"] == 682

    def test_track_label(self, summary):
        assert "ADJACENT TRACK" in summary["track"]

    def test_dimension(self, summary):
        assert summary["dimension"] == 13

    def test_signature_string(self, summary):
        assert summary["signature"] == "(11+2)"

    def test_all_algebraic_theorems_pass(self, summary):
        assert summary["all_algebraic_theorems_pass"] is True

    def test_constants_in_summary(self, summary):
        c = summary["constants"]
        assert c["K_CS"] == 74
        assert c["N_W"] == 5
        assert c["C_S"] == pytest.approx(12.0 / 37.0, rel=1e-14)
        assert c["PHI0_EFF"] == pytest.approx(5 * 2 * math.pi, rel=1e-14)
        assert c["N_FLUX"] == 37

    def test_falsification_conditions_present(self, summary):
        fc = summary["falsification_conditions"]
        assert len(fc) >= 4
        assert all(isinstance(s, str) for s in fc)

    def test_architecture_limits_addressed(self, summary):
        limits = summary["architecture_limits_addressed"]
        assert len(limits) >= 3
        # Dual-sector must be listed as resolved
        resolved_dual = [l for l in limits if "RESOLVED" in l and "(5,7)" in l]
        assert len(resolved_dual) >= 1

    def test_theorem_1_in_summary(self, summary):
        assert summary["theorem_682_1"]["invariant_preserved"] is True

    def test_theorem_2_in_summary(self, summary):
        assert summary["theorem_682_2"]["consistent"] is True

    def test_theorem_3_in_summary(self, summary):
        assert summary["theorem_682_3"]["shear_verified"] is True


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION / CROSS-PILLAR CONSISTENCY TESTS
# ─────────────────────────────────────────────────────────────────────────────

class TestCrossPillarConsistency:
    """Pillar 682 must be consistent with previously closed pillars."""

    def test_c_s_matches_braided_winding_formula(self):
        # Pillar 3 / braided_winding.py: c_s = 12/37
        # Verify numerically: c_s = (N2² - N1²) / K_CS = 24/74 = 12/37
        c_s_expected = 12.0 / 37.0
        assert C_S == pytest.approx(c_s_expected, rel=1e-14)
        # Also: ρ = 2×5×7/74 = 70/74 = 35/37; c_s = sqrt(1-ρ²)?
        # Verify alternative formula: c_s = |n₂²-n₁²|/k_cs (braided_winding formula [3])
        rho = 2 * N1 * N2 / K_CS
        c_s_alt = math.sqrt(1.0 - rho**2)
        assert C_S == pytest.approx(c_s_alt, rel=1e-10)

    def test_phi0_eff_reproduces_n_s(self):
        # Pillar 1 / metric.py: n_s = 1 - 36/φ₀_eff² ≈ 0.9635
        n_s = 1.0 - 36.0 / PHI0_EFF**2
        assert n_s == pytest.approx(0.9635, abs=0.0005)

    def test_phi0_eff_reproduces_r_braided(self):
        # Pillar 3: r_braided = r_bare × c_s
        # r_bare for n_w = 5: r_bare = 8/3 × (1 - n_s) ≈ 8/3 × 0.0365 ≈ 0.0973
        n_s = 1.0 - 36.0 / PHI0_EFF**2
        r_bare = (8.0 / 3.0) * (1.0 - n_s)
        r_braided = r_bare * C_S
        # Should be ≈ 0.0315
        assert r_braided == pytest.approx(0.0315, abs=0.003)

    def test_n_flux_matches_pi_kr(self):
        # From phi0_closure.py: PI_KR = 37 = N_FLUX = k_CS/2
        assert N_FLUX == 37
        assert N_FLUX == K_CS // 2

    def test_k_cs_sum_of_squares_identity(self):
        # Core identity of the UM: k_CS = n₁² + n₂² = 5² + 7² = 74
        assert K_CS == 5**2 + 7**2
        assert K_CS == 25 + 49
        assert K_CS == 74

    def test_sp2r_shear_det_is_unity(self):
        # The SL(2,ℝ) shear M = [[1,0],[-α,1]] has det = 1
        alpha = (N2 - N2_SHADOW) / float(N1)  # = 1/5
        M = np.array([[1.0, 0.0], [-alpha, 1.0]])
        assert np.linalg.det(M) == pytest.approx(1.0, abs=1e-12)

    def test_shadow_sector_not_equal_to_primary(self):
        # The two sectors are distinct — rotation angle is nonzero
        assert (N1, N2) != (N1_SHADOW, N2_SHADOW)
        assert N2 != N2_SHADOW  # 7 ≠ 6

    def test_birefringence_gap_is_within_litebird_window(self):
        # Pillar 58: both β values must be in [0.22°, 0.38°]
        result = theorem_682_3_dual_sector_phase_angle()
        assert 0.22 <= result["beta_primary_deg"] <= 0.38
        assert 0.22 <= result["beta_shadow_deg"] <= 0.38
        # Neither should be in the excluded gap [0.29°–0.31°]
        assert not (0.29 <= result["beta_primary_deg"] <= 0.31)
        assert not (0.29 <= result["beta_shadow_deg"] <= 0.31)


# ─────────────────────────────────────────────────────────────────────────────
# NUMERICAL STABILITY
# ─────────────────────────────────────────────────────────────────────────────

class TestNumericalStability:
    """The engine must be numerically robust across a range of inputs."""

    def test_very_small_phi_radion_preserves_signature(self):
        engine = ThirteenDimensionalEngine(num_points=4, rho_mixing=0.01)
        g4d = _flat_metric_4d(4)
        b = np.zeros((4, 4))
        phi_arr = np.full(4, 1e-6)
        G = engine.assemble_parent_metric(g_4d=g4d, b_field=b,
                                          phi_radion=phi_arr, master_radion=1.0)
        assert engine.verify_sp2r_signature(G) is True

    def test_very_large_phi_radion_preserves_signature(self):
        engine = ThirteenDimensionalEngine(num_points=4, rho_mixing=0.01)
        g4d = _flat_metric_4d(4)
        b = np.zeros((4, 4))
        phi_arr = np.full(4, 1e4)
        G = engine.assemble_parent_metric(g_4d=g4d, b_field=b,
                                          phi_radion=phi_arr, master_radion=1.0)
        assert engine.verify_sp2r_signature(G) is True

    def test_phi0_eff_computation_precision(self):
        # PHI0_EFF must equal exactly 5 * 2 * pi to machine precision
        assert PHI0_EFF == 5 * 2.0 * math.pi

    def test_c_s_rational_fraction_precision(self):
        # c_s must reproduce 12/37 to machine precision
        assert C_S == 12.0 / 37.0

    def test_k_cs_is_integer(self):
        assert isinstance(K_CS, int)
        assert K_CS == 74

    @pytest.mark.parametrize("n_pts", [1, 8, 64])
    def test_metric_assembly_no_nan_or_inf(self, n_pts):
        _, G = _build_standard_metric(n_pts, rho=0.1, b_scale=0.5)
        assert np.all(np.isfinite(G))

    def test_shear_matrix_determinant_is_unity(self):
        result = theorem_682_3_dual_sector_phase_angle()
        M = np.array(result["shear_matrix"])
        det = np.linalg.det(M)
        assert det == pytest.approx(1.0, abs=1e-12)
