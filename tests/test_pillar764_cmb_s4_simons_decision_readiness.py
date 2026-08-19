# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 764: CMB-S4/SO Decision Readiness."""
import pytest
from src.core.pillar764_cmb_s4_simons_decision_readiness import (
    cmb_s4_simons_readiness, r_discrimination_power, ns_discrimination_power,
    verdict_routing, R_UM, NS_UM, SIGMA_R_S4, PILLAR, STATUS, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 764
    def test_status(self): assert STATUS == 'CLOSED'
    def test_r_um_range(self): assert 0.030 < R_UM < 0.035
    def test_ns_um_range(self): assert 0.960 < NS_UM < 0.967
    def test_no_toe_score(self): import src.core.pillar764_cmb_s4_simons_decision_readiness as m; assert not hasattr(m, 'toe_score')


class TestDiscrimination:
    def test_r_disc_decision_grade(self):
        d = r_discrimination_power()
        assert d['decision_grade_s4']
        assert d['discrimination_sigma_s4'] > 5.0

    def test_ns_planck_compatible(self):
        n = ns_discrimination_power()
        assert n['compatible_1sigma_planck']

    def test_ns_s4_tension(self):
        n = ns_discrimination_power()
        # UM n_s is 0.14σ from PDG with Planck errors → should be <1σ even with S4
        assert n['tension_s4_sigma'] < 2.0


class TestVerdictRouting:
    def test_branch_a_for_um(self):
        v = verdict_routing(R_UM, SIGMA_R_S4)
        assert v == 'BRANCH_A_STRONG_SUPPORT'

    def test_branch_c_for_zero(self):
        v = verdict_routing(0.005, 0.003)
        assert 'FALSIFIED' in v

    def test_branch_d_for_high(self):
        v = verdict_routing(0.050, 0.003)
        assert 'OVER' in v or 'TENSION' in v


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return cmb_s4_simons_readiness()

    def test_pillar_field(self, result): assert result['pillar'] == 764
    def test_four_branches(self, result): assert len(result['verdict_branches']) == 4
    def test_self_verdict_branch_a(self, result): assert result['um_self_verdict'] == 'BRANCH_A_STRONG_SUPPORT'
    def test_cmb_s4_decision_grade(self, result): assert result['experiments']['CMB-S4']['decision_grade']
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar764_cmb_s4_simons_decision_readiness as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s)
