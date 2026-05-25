# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 449 — Fermion Hierarchy 9/9 Audit."""
import math
import pytest
from src.core.pillar449_fermion_hierarchy_99_audit import (
    PILLAR_STATUS, VERSION,
    YUKAWA_EXPONENT, NATURALNESS_THRESHOLD, TOL_DEX,
    SM_FERMION_TABLE, FN_ASSIGNMENTS, SM_FERMION_MASSES_GEV, EXCEPTIONAL_P411,
    compute_fn_assignment, yukawa_residual_dex,
    audit_all_fermions, hierarchy_verdict, pillar_report,
)


class TestConstants:
    def test_yukawa_exponent(self):
        assert abs(YUKAWA_EXPONENT - 5.0) < 1e-10

    def test_naturalness_threshold(self):
        assert NATURALNESS_THRESHOLD == 0.6

    def test_tol_dex(self):
        assert TOL_DEX == 0.5

    def test_9_fermions_in_table(self):
        assert len(SM_FERMION_TABLE) == 9

    def test_exceptional_p411(self):
        # Strange and muon were the exceptions
        assert 's' in EXCEPTIONAL_P411
        assert 'mu' in EXCEPTIONAL_P411


class TestFNAssignment:
    def test_top_quark_ell_zero(self):
        fn = compute_fn_assignment(173.0)  # top mass
        assert fn['ell_eff'] == pytest.approx(0.0, abs=0.01)

    def test_delta_fn_lt_threshold(self):
        for f in SM_FERMION_TABLE:
            fn = compute_fn_assignment(f['m_GeV'])
            assert fn['is_natural'], (
                f"Fermion {f['name']} has delta_fn={fn['delta_fn']:.3f} >= {NATURALNESS_THRESHOLD}"
            )

    def test_ell_eff_positive_for_light_fermions(self):
        for f in SM_FERMION_TABLE:
            fn = compute_fn_assignment(f['m_GeV'])
            assert fn['ell_eff'] >= 0.0

    def test_invalid_mass_raises(self):
        with pytest.raises((ValueError, ZeroDivisionError, Exception)):
            compute_fn_assignment(-1.0)

    def test_formula_ell_eff_charm(self):
        m_c = 1.27
        m_t = 173.0
        expected = -math.log(m_c / m_t) / YUKAWA_EXPONENT
        fn = compute_fn_assignment(m_c)
        assert abs(fn['ell_eff'] - expected) < 1e-10


class TestYukawaResidual:
    @pytest.mark.parametrize('fermion', ['t', 'c', 'u', 'b', 's', 'd', 'tau', 'mu', 'e'])
    def test_all_natural(self, fermion):
        r = yukawa_residual_dex(fermion)
        assert r['natural'] is True, (
            f"{fermion}: delta_fn={r['fn_delta']:.3f}"
        )

    def test_strange_exceptional_in_p411(self):
        r = yukawa_residual_dex('s')
        assert r['was_exceptional_p411'] is True

    def test_muon_exceptional_in_p411(self):
        r = yukawa_residual_dex('mu')
        assert r['was_exceptional_p411'] is True

    def test_top_not_exceptional(self):
        r = yukawa_residual_dex('t')
        assert r['was_exceptional_p411'] is False

    def test_unknown_fermion_raises(self):
        with pytest.raises((ValueError, KeyError)):
            yukawa_residual_dex('x')


class TestAudit:
    def test_all_9_natural(self):
        r = audit_all_fermions()
        assert r['n_natural'] == 9
        assert r['all_natural'] is True

    def test_no_exceptional_remaining(self):
        r = audit_all_fermions()
        assert len(r['exceptional_fermions']) == 0

    def test_max_delta_fn_lt_threshold(self):
        r = audit_all_fermions()
        assert r['max_delta_fn'] < NATURALNESS_THRESHOLD

    def test_formerly_exceptional(self):
        r = audit_all_fermions()
        assert set(r['formerly_exceptional']) == set(EXCEPTIONAL_P411)

    def test_all_natural_with_2loop(self):
        r = audit_all_fermions()
        assert r['all_natural_with_2loop'] is True


class TestHierarchyVerdict:
    def test_all_9_9(self):
        v = hierarchy_verdict()
        assert v['all_9_9'] is True

    def test_verdict_certified(self):
        v = hierarchy_verdict()
        assert v['verdict'] == 'FERMION_HIERARCHY_99_AUDIT_CERTIFIED'

    def test_strange_natural(self):
        v = hierarchy_verdict()
        assert v['strange_quark']['natural'] is True

    def test_muon_natural(self):
        v = hierarchy_verdict()
        assert v['muon']['natural'] is True

    def test_max_delta_lt_threshold(self):
        v = hierarchy_verdict()
        assert v['max_delta_fn'] < NATURALNESS_THRESHOLD


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 449

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS
