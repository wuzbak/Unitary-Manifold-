# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 415 — FN charge from orbifold boundary conditions."""
import math
import pytest

from src.core.pillar415_fn_charge_orbifold_bc import (
    PILLAR_STATUS,
    FERMION_HIERARCHY_STATUS,
    N_W,
    K_CS,
    fn_phase_shift,
    fn_charge_from_bc,
    fermion_hierarchy_closure_check,
    hierarchy_geometrically_constrained_verdict,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'HIERARCHY_GEOMETRICALLY_CONSTRAINED'

    def test_hierarchy_status(self):
        assert FERMION_HIERARCHY_STATUS == 'HIERARCHY_GEOMETRICALLY_CONSTRAINED'

    def test_nw(self):
        assert N_W == 5

    def test_kcs(self):
        assert K_CS == 74


class TestFnPhaseShift:
    def test_zero_delta_ell(self):
        assert fn_phase_shift(0.0, K_CS) == pytest.approx(0.0)

    def test_formula(self):
        assert fn_phase_shift(1.0, 74) == pytest.approx(2 * math.pi / 74)

    def test_positive_for_positive_delta_ell(self):
        assert fn_phase_shift(1.39, K_CS) > 0

    def test_scales_linearly(self):
        assert fn_phase_shift(2.0, K_CS) == pytest.approx(2 * fn_phase_shift(1.0, K_CS))


class TestFnChargeFromBC:
    def test_returns_dict(self):
        assert isinstance(fn_charge_from_bc(0.0694, 0.5, 74), dict)

    def test_formula_overlap_exponent(self):
        data = fn_charge_from_bc(0.0694, 0.5, 74)
        assert data['overlap_exponent'] == pytest.approx((1 - 2 * 0.0694) * 0.5)

    def test_delta_ell_effective_reasonable(self):
        data = fn_charge_from_bc(0.0694, 0.5, 74)
        assert 5.0 < data['delta_ell_effective'] < 5.2

    def test_theta_matches_phase_function(self):
        data = fn_charge_from_bc(0.0694, 0.5, 74)
        assert data['theta_fn'] == pytest.approx(fn_phase_shift(data['delta_ell_effective'], 74))

    def test_charge_type(self):
        assert fn_charge_from_bc(0.0694, 0.5, 74)['charge_type'] == 'continuous_orbifold_phase'

    def test_larger_kepsilon_gives_larger_charge(self):
        d1 = fn_charge_from_bc(0.0694, 0.25, 74)
        d2 = fn_charge_from_bc(0.0694, 0.5, 74)
        assert d2['delta_ell_effective'] > d1['delta_ell_effective']

    def test_larger_cl_gives_smaller_charge(self):
        d1 = fn_charge_from_bc(0.05, 0.5, 74)
        d2 = fn_charge_from_bc(0.10, 0.5, 74)
        assert d1['delta_ell_effective'] > d2['delta_ell_effective']


class TestFermionHierarchyClosureCheck:
    def test_returns_dict(self):
        assert isinstance(fermion_hierarchy_closure_check(), dict)

    def test_total_fermions(self):
        assert fermion_hierarchy_closure_check()['n_total_fermions'] == 9

    def test_previously_constrained(self):
        assert fermion_hierarchy_closure_check()['previously_within_architecture'] == 7

    def test_newly_constrained(self):
        assert fermion_hierarchy_closure_check()['newly_constrained_by_fn_phase'] == 2

    def test_all_nine_within_architecture(self):
        assert fermion_hierarchy_closure_check()['n_within_architecture'] == 9

    def test_closure_fraction(self):
        assert fermion_hierarchy_closure_check()['closure_fraction'] == pytest.approx(1.0)

    def test_delta_ell_effective_positive(self):
        assert fermion_hierarchy_closure_check()['delta_ell_effective'] > 0

    def test_mechanism_mentions_phase(self):
        assert 'phase' in fermion_hierarchy_closure_check()['mechanism']


class TestHierarchyVerdict:
    def test_returns_dict(self):
        assert isinstance(hierarchy_geometrically_constrained_verdict(), dict)

    def test_status(self):
        assert hierarchy_geometrically_constrained_verdict()['status'] == 'HIERARCHY_GEOMETRICALLY_CONSTRAINED'

    def test_previous_status(self):
        assert hierarchy_geometrically_constrained_verdict()['previous_status'] == 'HIERARCHY_PARTIALLY_CONSTRAINED'

    def test_new_status(self):
        assert hierarchy_geometrically_constrained_verdict()['new_status'] == 'HIERARCHY_GEOMETRICALLY_CONSTRAINED'

    def test_all_nine_recorded(self):
        verdict = hierarchy_geometrically_constrained_verdict()
        assert verdict['n_within_architecture'] == 9
        assert verdict['n_total_fermions'] == 9

    def test_verdict_mentions_boundary(self):
        assert 'boundary' in hierarchy_geometrically_constrained_verdict()['verdict']
