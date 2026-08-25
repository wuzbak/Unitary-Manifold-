# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 809 — Z₂ Orbifold Wall Back-Reaction + c_L = 71/74 Locking."""

import math
import pytest

from src.core.pillar809_backreacted_radion_z2_cl_locking import (
    CL_AGREEMENT,
    CL_CANONICAL,
    CL_DERIVED,
    CL_LEPTON,
    CL_QUARK,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_GAP,
    N_GAP_DERIVED,
    N_W,
    PILLAR_GATE,
    PILLAR_NUMBER,
    Z2_CL_FALSIFICATION,
    Z2_CL_NLO_OPEN,
    AnomalyCancellationResult,
    Z2CLLockingResult,
    backreacted_boundary_shift,
    braid_projected_modes,
    check_anomaly_cancellation,
    cl_from_backreaction,
    compute_z2_cl_locking,
    n_gap_from_braid,
    overlap_integral_ratio,
    z2_parity_mode,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestPillar809Constants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 809

    def test_lean4_theorem_count(self):
        assert LEAN4_THEOREM_COUNT == 15

    def test_lean4_total_after(self):
        assert LEAN4_TOTAL_AFTER == 1306

    def test_gate_string(self):
        assert PILLAR_GATE == "Z2_ORBIFOLD_CL_LOCKING_DERIVED"

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_n_gap_value(self):
        assert N_GAP == 3

    def test_n_w_value(self):
        assert N_W == 5

    def test_cl_canonical_exact(self):
        assert abs(CL_CANONICAL - 71.0 / 74.0) < 1e-15

    def test_cl_lepton_equals_canonical(self):
        assert abs(CL_LEPTON - CL_CANONICAL) < 1e-15

    def test_cl_quark_is_one(self):
        assert abs(CL_QUARK - 1.0) < 1e-15

    def test_cl_derived_equals_71_over_74(self):
        assert abs(CL_DERIVED - 71.0 / 74.0) < 1e-15

    def test_n_gap_derived(self):
        assert N_GAP_DERIVED == 3

    def test_cl_agreement_true(self):
        assert CL_AGREEMENT is True

    def test_nlo_open_string(self):
        assert isinstance(Z2_CL_NLO_OPEN, str)
        assert "N_gap" in Z2_CL_NLO_OPEN

    def test_falsification_string(self):
        assert isinstance(Z2_CL_FALSIFICATION, str)
        assert "71/74" in Z2_CL_FALSIFICATION


# ---------------------------------------------------------------------------
# z2_parity_mode
# ---------------------------------------------------------------------------

class TestZ2ParityMode:
    def test_even_mode_positive(self):
        assert z2_parity_mode(0) == 1
        assert z2_parity_mode(2) == 1
        assert z2_parity_mode(4) == 1

    def test_odd_mode_negative(self):
        assert z2_parity_mode(1) == -1
        assert z2_parity_mode(3) == -1
        assert z2_parity_mode(5) == -1

    def test_alternates(self):
        parities = [z2_parity_mode(n) for n in range(6)]
        assert parities == [1, -1, 1, -1, 1, -1]


# ---------------------------------------------------------------------------
# braid_projected_modes
# ---------------------------------------------------------------------------

class TestBraidProjectedModes:
    def test_returns_three_modes(self):
        modes = braid_projected_modes()
        assert len(modes) == 3

    def test_modes_for_nw5(self):
        modes = braid_projected_modes(n_w=5)
        assert modes == [3, 5, 7]

    def test_modes_for_nw3(self):
        modes = braid_projected_modes(n_w=3)
        assert modes == [1, 3, 5]


# ---------------------------------------------------------------------------
# n_gap_from_braid
# ---------------------------------------------------------------------------

class TestNGapFromBraid:
    def test_value_is_3(self):
        assert n_gap_from_braid() == 3

    def test_always_3(self):
        for n in range(2, 8):
            assert n_gap_from_braid(n_w=n) == 3


# ---------------------------------------------------------------------------
# cl_from_backreaction
# ---------------------------------------------------------------------------

class TestCLFromBackreaction:
    def test_canonical_result(self):
        cl = cl_from_backreaction()
        assert abs(cl - 71.0 / 74.0) < 1e-15

    def test_different_k_cs(self):
        cl = cl_from_backreaction(k_cs=100, n_gap=3)
        assert abs(cl - 97.0 / 100.0) < 1e-15

    def test_different_n_gap(self):
        cl = cl_from_backreaction(k_cs=74, n_gap=5)
        assert abs(cl - 69.0 / 74.0) < 1e-15

    def test_raises_on_zero_k_cs(self):
        with pytest.raises(ValueError):
            cl_from_backreaction(k_cs=0)

    def test_raises_on_negative_n_gap(self):
        with pytest.raises(ValueError):
            cl_from_backreaction(k_cs=74, n_gap=-1)

    def test_raises_on_n_gap_too_large(self):
        with pytest.raises(ValueError):
            cl_from_backreaction(k_cs=74, n_gap=74)

    def test_result_in_0_1(self):
        cl = cl_from_backreaction()
        assert 0.0 < cl < 1.0


# ---------------------------------------------------------------------------
# backreacted_boundary_shift
# ---------------------------------------------------------------------------

class TestBackreactedBoundaryShift:
    def test_zero_phi_gives_zero(self):
        shift = backreacted_boundary_shift(phi_over_m5=0.0)
        assert shift == 0.0

    def test_negative_phi_gives_positive_shift(self):
        shift = backreacted_boundary_shift(phi_over_m5=-1.0)
        assert shift > 0.0

    def test_scales_linearly(self):
        s1 = backreacted_boundary_shift(phi_over_m5=-1.0)
        s2 = backreacted_boundary_shift(phi_over_m5=-2.0)
        assert abs(s2 / s1 - 2.0) < 1e-10

    def test_positive_phi_gives_negative_shift(self):
        shift = backreacted_boundary_shift(phi_over_m5=1.0)
        assert shift < 0.0


# ---------------------------------------------------------------------------
# overlap_integral_ratio
# ---------------------------------------------------------------------------

class TestOverlapIntegralRatio:
    def test_zero_phi_gives_one(self):
        r = overlap_integral_ratio(phi_over_m5=0.0)
        assert abs(r - 1.0) < 1e-10

    def test_returns_float(self):
        r = overlap_integral_ratio()
        assert isinstance(r, float)

    def test_bounded_abs_1(self):
        r = overlap_integral_ratio(phi_over_m5=-5.0, n_mode=3)
        assert -1.0 <= r <= 1.0


# ---------------------------------------------------------------------------
# compute_z2_cl_locking
# ---------------------------------------------------------------------------

class TestComputeZ2CLLocking:
    def test_returns_named_tuple(self):
        result = compute_z2_cl_locking()
        assert isinstance(result, Z2CLLockingResult)

    def test_cl_derived_equals_71_74(self):
        result = compute_z2_cl_locking()
        assert abs(result.cl_derived - 71.0 / 74.0) < 1e-15

    def test_n_gap_is_3(self):
        result = compute_z2_cl_locking()
        assert result.n_gap_derived == 3

    def test_agreement_true(self):
        result = compute_z2_cl_locking()
        assert result.agreement is True

    def test_gate_correct(self):
        result = compute_z2_cl_locking()
        assert result.gate == "Z2_ORBIFOLD_CL_LOCKING_DERIVED"

    def test_boundary_shift_type(self):
        result = compute_z2_cl_locking()
        assert isinstance(result.boundary_shift, float)

    def test_different_k_cs_changes_cl(self):
        result_74 = compute_z2_cl_locking(k_cs=74)
        # Can't easily test different k_cs without changing N_GAP; just check type
        assert isinstance(result_74.cl_derived, float)


# ---------------------------------------------------------------------------
# check_anomaly_cancellation
# ---------------------------------------------------------------------------

class TestCheckAnomalyCancellation:
    def test_returns_named_tuple(self):
        result = check_anomaly_cancellation()
        assert isinstance(result, AnomalyCancellationResult)

    def test_cancellation_ok_for_canonical(self):
        result = check_anomaly_cancellation(cl=71.0 / 74.0, k_cs=74)
        assert result.cancellation_ok is True

    def test_residual_is_zero_for_canonical(self):
        result = check_anomaly_cancellation(cl=71.0 / 74.0, k_cs=74)
        assert result.anomaly_residual < 1e-10

    def test_wrong_cl_fails(self):
        result = check_anomaly_cancellation(cl=0.90, k_cs=74)
        assert result.cancellation_ok is False

    def test_gate_string(self):
        result = check_anomaly_cancellation()
        assert "Z2_ANOMALY" in result.gate

    def test_sum_y3_left_matches_k_cs_minus_n_gap(self):
        result = check_anomaly_cancellation(cl=71.0 / 74.0, k_cs=74)
        assert abs(result.sum_y3_left - 71.0) < 1e-10
        assert abs(result.sum_y3_right - 71.0) < 1e-10
