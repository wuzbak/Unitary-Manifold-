# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 763: Jarlskog Layer-3 Sub-Leading FN."""
import pytest
from src.core.pillar763_jarlskog_layer3_subleading_fn import (
    jarlskog_layer3_subleading_fn, jarlskog_baseline, jarlskog_exact,
    jarlskog_layer2, jarlskog_layer3,
    J_PDG, J_PDG_ERR, LAMBDA_C, PILLAR, STATUS, EPISTEMIC_LABEL, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 763
    def test_status(self): assert STATUS == 'CLOSED'
    def test_epistemic(self): assert EPISTEMIC_LABEL == 'CONDITIONAL_DERIVATION'
    def test_lambda_c_range(self): assert 0.224 < LAMBDA_C < 0.227
    def test_j_pdg_range(self): assert 3.0e-5 < J_PDG < 3.4e-5
    def test_no_toe_score(self):
        import src.core.pillar763_jarlskog_layer3_subleading_fn as m
        assert not hasattr(m, 'toe_score')


class TestChain:
    def test_exact_positive(self): assert jarlskog_exact() > 0
    def test_exact_order_magnitude(self):
        j = jarlskog_exact()
        assert 2.5e-5 < j < 3.5e-5, f"J_exact = {j}"

    def test_exact_within_5pct_pdg(self):
        j = jarlskog_exact()
        assert abs(j - J_PDG) / J_PDG < 0.05

    def test_baseline_positive(self): assert jarlskog_baseline() > 0
    def test_baseline_order_magnitude(self):
        j = jarlskog_baseline()
        assert 1e-6 < j < 1e-4

    def test_layer2_increases_j(self):
        j_bl = jarlskog_baseline()
        l2 = jarlskog_layer2(j_bl)
        assert l2['j_l2'] > j_bl

    def test_layer3_increases_j(self):
        j_bl = jarlskog_baseline()
        l2 = jarlskog_layer2(j_bl)
        l3 = jarlskog_layer3(l2['j_l2'])
        assert l3['j_l3'] > l2['j_l2']

    def test_layer3_closed(self):
        j_bl = jarlskog_baseline()
        l2 = jarlskog_layer2(j_bl)
        l3 = jarlskog_layer3(l2['j_l2'])
        assert l3['closed']
        assert l3['pdg_residual_pct'] < 1.0


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return jarlskog_layer3_subleading_fn()

    def test_pillar_field(self, result): assert result['pillar'] == 763
    def test_residual_sub_1pct(self, result): assert result['result']['residual_pct'] < 1.0
    def test_extends(self, result): assert '682' in result['extends']
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_prediction_label(self, result):
        assert result['result']['label'] == 'CONDITIONAL_DERIVATION'
    def test_chain_has_exact(self, result): assert 'j_exact' in result['chain']
    def test_honest_note_calibrated(self, result):
        assert 'calibrated' in result['honest_note']
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar763_jarlskog_layer3_subleading_fn as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s), f"Missing symbol: {s}"
