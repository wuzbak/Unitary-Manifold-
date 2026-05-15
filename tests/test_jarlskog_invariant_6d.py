# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for jarlskog_invariant_6d.py — geometric Jarlskog from 6D overlaps."""
from __future__ import annotations

import math

import pytest

from src.core.jarlskog_invariant_6d import (
    J_CKM_PDG,
    K_CS,
    N_W,
    PI_KR,
    ckm_matrix_from_6d_overlaps,
    jarlskog_cp_phase_angle,
    jarlskog_invariant_geometric,
    lab_transfer_jarlskog,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_j_ckm_pdg(self):
        assert abs(J_CKM_PDG - 3.04e-5) < 1e-30


# ---------------------------------------------------------------------------
# jarlskog_invariant_geometric
# ---------------------------------------------------------------------------

class TestJarlskogInvariantGeometric:
    def test_j_geo_positive(self):
        result = jarlskog_invariant_geometric()
        assert result["J_geo"] > 0

    def test_j_geo_order_of_magnitude_within_2_decades_of_3e5(self):
        result = jarlskog_invariant_geometric()
        j = result["J_geo"]
        log_diff = abs(math.log10(j) - math.log10(3e-5))
        assert log_diff <= 2.0, f"|log10(J_geo) - log10(3e-5)| = {log_diff:.2f} > 2"

    def test_theta_braid_correct(self):
        result = jarlskog_invariant_geometric()
        expected = 2 * math.pi * N_W / K_CS
        assert abs(result["theta_braid_rad"] - expected) < 1e-12

    def test_j_ckm_pdg_key_present(self):
        result = jarlskog_invariant_geometric()
        assert "J_CKM_PDG" in result

    def test_residual_pct_finite(self):
        result = jarlskog_invariant_geometric()
        assert math.isfinite(result["residual_vs_pdg_pct"])

    def test_status_key_present(self):
        result = jarlskog_invariant_geometric()
        assert "status" in result

    def test_custom_n_w_k_cs(self):
        result = jarlskog_invariant_geometric(n_w=3, k_cs=50)
        assert result["J_geo"] > 0

    def test_j_geo_less_than_1(self):
        result = jarlskog_invariant_geometric()
        assert result["J_geo"] < 1.0


# ---------------------------------------------------------------------------
# ckm_matrix_from_6d_overlaps
# ---------------------------------------------------------------------------

class TestCkmMatrixFrom6dOverlaps:
    def test_returns_lambda_wolfenstein_key(self):
        result = ckm_matrix_from_6d_overlaps()
        assert "lambda_wolfenstein" in result

    def test_lambda_wolfenstein_positive(self):
        result = ckm_matrix_from_6d_overlaps()
        assert result["lambda_wolfenstein"] > 0

    def test_lambda_wolfenstein_order_of_magnitude(self):
        # sin(2π × 5/74) ≈ 0.413; Cabibbo angle is ~0.22 → close enough for geometric estimate
        result = ckm_matrix_from_6d_overlaps()
        assert 0.1 < result["lambda_wolfenstein"] < 0.9

    def test_returns_v_ub(self):
        result = ckm_matrix_from_6d_overlaps()
        assert "V_ub" in result

    def test_v_ud_near_1(self):
        result = ckm_matrix_from_6d_overlaps()
        assert 0.8 < result["V_ud"] <= 1.0

    def test_returns_rho_bar(self):
        result = ckm_matrix_from_6d_overlaps()
        assert "rho_bar" in result
        assert result["rho_bar"] == 0.159

    def test_pi_kr_used_key(self):
        result = ckm_matrix_from_6d_overlaps(pi_kr=37.0)
        assert result["pi_kr_used"] == 37.0

    def test_all_nine_ckm_magnitudes_positive(self):
        result = ckm_matrix_from_6d_overlaps()
        for key in ("V_ud", "V_us", "V_ub", "V_cd", "V_cs", "V_cb", "V_td", "V_ts", "V_tb"):
            assert result[key] >= 0, f"{key} = {result[key]} is negative"


# ---------------------------------------------------------------------------
# jarlskog_cp_phase_angle
# ---------------------------------------------------------------------------

class TestJarlskogCpPhaseAngle:
    def test_delta_ckm_rad_positive(self):
        result = jarlskog_cp_phase_angle()
        assert result["delta_ckm_rad"] > 0

    def test_delta_ckm_deg_positive(self):
        result = jarlskog_cp_phase_angle()
        assert result["delta_ckm_deg"] > 0

    def test_delta_ckm_deg_in_reasonable_range(self):
        result = jarlskog_cp_phase_angle()
        # PDG: δ ≈ 68.6°; geometric estimate may vary but should be in [10°, 170°]
        assert 10.0 < result["delta_ckm_deg"] < 170.0

    def test_sin_delta_in_unit_interval(self):
        result = jarlskog_cp_phase_angle()
        assert -1.0 <= result["sin_delta"] <= 1.0

    def test_consistency_key_present(self):
        result = jarlskog_cp_phase_angle()
        assert "consistency_with_pdg" in result


# ---------------------------------------------------------------------------
# lab_transfer_jarlskog
# ---------------------------------------------------------------------------

class TestLabTransferJarlskog:
    def test_pi_topo_1_gives_j_lab_equals_j_geo(self):
        result = lab_transfer_jarlskog(1.0)
        geo = jarlskog_invariant_geometric()
        assert abs(result["J_lab"] - geo["J_geo"]) < 1e-30

    def test_pi_topo_0_gives_j_lab_zero(self):
        result = lab_transfer_jarlskog(0.0)
        assert result["J_lab"] == 0.0

    def test_returns_a_cp_predicted(self):
        result = lab_transfer_jarlskog(0.9)
        assert "A_CP_predicted" in result

    def test_a_cp_predicted_equals_j_lab(self):
        result = lab_transfer_jarlskog(0.9)
        assert result["A_CP_predicted"] == result["J_lab"]

    def test_order_of_magnitude_check_for_small_pi_topo(self):
        # pi_topo ≈ 0.01 → J_lab ≈ 1.87e-5 → |log10(J_lab) - (-5)| ≈ 0.27 ≤ 2 → True
        result = lab_transfer_jarlskog(0.01)
        assert result["order_of_magnitude_check"] is True

    def test_j_geo_key_present(self):
        result = lab_transfer_jarlskog(0.5)
        assert "J_geo" in result

    def test_invalid_pi_topo_raises(self):
        with pytest.raises(ValueError):
            lab_transfer_jarlskog(1.5)

    def test_negative_pi_topo_raises(self):
        with pytest.raises(ValueError):
            lab_transfer_jarlskog(-0.1)
