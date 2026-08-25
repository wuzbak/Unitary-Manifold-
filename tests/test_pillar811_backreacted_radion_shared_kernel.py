# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import math

import pytest

from src.core.pillar811_backreacted_radion_shared_kernel import (
    BOUNDARY_SHIFT_SHARED,
    CL_SHARED,
    DELTA_PHI_SHARED,
    GAMMA_V,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_GAP_SHARED,
    N_W,
    PI_KR,
    PILLAR_GATE,
    PILLAR_NUMBER,
    SWAMPLAND_DISTANCE_BOUND,
    TAIL_BOUND_CERTIFIED,
    TARGET_QCD_ORDERS,
    KKTruncationResult,
    ProjectionResult,
    SharedKernelResult,
    backreacted_volume_ratio,
    controlled_kk_truncation,
    effective_boundary_shift,
    explicit_radion_source_term,
    iterate_shared_backreaction_kernel,
    project_n_gap_from_boundary,
    project_shared_observables,
    required_delta_phi,
    shared_kernel_summary,
)


class TestConstants:
    def test_pillar_number_and_gate(self):
        assert PILLAR_NUMBER == 811
        assert PILLAR_GATE == "BACKREACTED_RADION_SHARED_KERNEL_CONVERGED"

    def test_lean4_accounting(self):
        assert LEAN4_THEOREM_COUNT == 15
        assert LEAN4_TOTAL_AFTER == 1321

    def test_core_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert PI_KR == 37.0
        assert abs(GAMMA_V - 0.5) < 1e-15
        assert TARGET_QCD_ORDERS == 7.0
        assert SWAMPLAND_DISTANCE_BOUND == 30.0


class TestTruncation:
    def test_controlled_kk_truncation_returns_namedtuple(self):
        result = controlled_kk_truncation()
        assert isinstance(result, KKTruncationResult)

    def test_tail_bound_is_tiny(self):
        assert TAIL_BOUND_CERTIFIED < 1e-12

    def test_suppression_ratio_in_unit_interval(self):
        result = controlled_kk_truncation()
        assert 0.0 < result.suppression_ratio < 1.0

    def test_invalid_n_modes_raises(self):
        with pytest.raises(ValueError):
            controlled_kk_truncation(n_modes=0)


class TestKernelMap:
    def test_required_delta_phi_matches_target_formula(self):
        expected = -TARGET_QCD_ORDERS * math.log(10.0) / GAMMA_V
        assert abs(required_delta_phi() - expected) < 1e-15

    def test_volume_ratio_is_exponential(self):
        assert abs(backreacted_volume_ratio(-1.0) - math.exp(-1.0)) < 1e-15

    def test_source_term_is_negative(self):
        truncation = controlled_kk_truncation()
        assert explicit_radion_source_term(-32.0, truncation) < 0.0

    def test_boundary_shift_saturates_below_half(self):
        shift = effective_boundary_shift(-32.0, -1e-8)
        assert 0.49 < shift <= 0.5

    def test_kernel_converges(self):
        result = iterate_shared_backreaction_kernel()
        assert isinstance(result, SharedKernelResult)
        assert result.converged is True
        assert result.iterations >= 1
        assert result.gate == "BACKREACTED_RADION_SHARED_KERNEL_CONVERGED"

    def test_shared_delta_is_more_negative_than_minus_30(self):
        assert DELTA_PHI_SHARED < -30.0

    def test_swampland_tension_registered(self):
        result = iterate_shared_backreaction_kernel()
        assert result.swampland_tension is True


class TestProjections:
    def test_projected_ngap_is_three(self):
        assert N_GAP_SHARED == 3

    def test_projected_cl_is_71_over_74(self):
        assert abs(CL_SHARED - 71.0 / 74.0) < 1e-15

    def test_boundary_projection_from_shared_shift(self):
        assert project_n_gap_from_boundary(BOUNDARY_SHIFT_SHARED) == 3

    def test_projection_result_passes(self):
        result = project_shared_observables()
        assert isinstance(result, ProjectionResult)
        assert result.gate == "BACKREACTED_RADION_SHARED_PROJECTIONS_PASS"
        assert abs(result.qcd_suppression_orders - 7.0) < 0.05
        assert result.cmb_partial_closure_fraction > 0.0
        assert result.wa_radion < 0.0

    def test_summary_contains_expected_fields(self):
        result = shared_kernel_summary()
        assert result["pillar"] == 811
        assert result["projection_gate"] == "BACKREACTED_RADION_SHARED_PROJECTIONS_PASS"
        assert result["n_gap"] == 3
        assert abs(result["cl_value"] - 71.0 / 74.0) < 1e-15
