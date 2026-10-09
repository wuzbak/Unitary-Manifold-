# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 759: P8 Full Functional-Space Lean4 Proof."""
import pytest
from src.core.pillar759_p8_full_functional_lean4_proof import (
    p8_full_functional_proof, coercivity_bound, uniqueness_certificate,
    lsc_check, second_variation, poincare_constant,
    PILLAR, STATUS, EPISTEMIC_LABEL, ALPHA_COERCE, BETA_COERCE, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar_number(self): assert PILLAR == 759
    def test_status(self): assert STATUS == 'OPEN'
    def test_epistemic_label(self): assert EPISTEMIC_LABEL == 'FINITE_PROXY_ONLY'
    def test_alpha_range(self): assert 0.7 < ALPHA_COERCE < 0.8
    def test_beta_range(self): assert 0.0 < BETA_COERCE < 0.05
    def test_no_toe_score(self): import src.core.pillar759_p8_full_functional_lean4_proof as m; assert not hasattr(m, 'toe_score')


class TestCoercivity:
    def test_positive_at_unit_norm(self): assert coercivity_bound(1.0) > -BETA_COERCE
    def test_grows_with_norm(self): assert coercivity_bound(2.0) > coercivity_bound(1.0)
    def test_poincare_positive(self): assert poincare_constant() > 0
    def test_poincare_approx(self):
        # πkR / K_CS ≈ π*37 / 74 ≈ π/2 ≈ 1.57
        import numpy as np
        assert abs(poincare_constant() - np.pi / 2) < 0.01


class TestLSC:
    def test_lsc_convergent_sequence(self):
        r = lsc_check([0.5, 0.42, 0.38, 0.36, 0.35])
        assert r['lsc']
    def test_lsc_empty(self):
        r = lsc_check([])
        assert not r['lsc']
    def test_lsc_monotone(self):
        r = lsc_check([1.0, 0.9, 0.8])
        assert r['lim_inf'] <= r['s_final']


class TestUniqueness:
    def test_second_variation_positive(self): assert second_variation(1.0) > 0
    def test_unique_at_phi_star(self):
        u = uniqueness_certificate()
        assert not u['unique']
        assert u['sample_positive']
        assert u['second_variation'] > 0
    def test_label_correct(self):
        u = uniqueness_certificate()
        assert 'UNIQUENESS' in u['label']


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return p8_full_functional_proof()

    def test_pillar_field(self, result): assert result['pillar'] == 759
    def test_coercivity_step(self, result): assert result['steps']['coercivity']['passed']
    def test_lsc_step(self, result): assert result['steps']['lower_semi_continuity']['lsc']
    def test_uniqueness_step(self, result): assert not result['steps']['uniqueness']['unique']
    def test_lean4_new(self, result): assert result['lean4']['new_theorems'] == 0
    def test_lean4_total(self, result): assert result['lean4']['new_total'] == 762
    def test_extends_p752(self, result): assert '752' in result['extends']
    def test_honest_note_present(self, result): assert len(result['honest_note']) > 10
    def test_no_forbidden_keys(self, result): assert 'toe_score' not in result
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestExpectations:
    def test_all_required_symbols_present(self):
        import src.core.pillar759_p8_full_functional_lean4_proof as m
        for sym in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, sym), f"Missing symbol: {sym}"


def test_finite_checks_do_not_promote_functional_proof():
    result = p8_full_functional_proof()
    assert result['label'] == 'P8_FULL_FUNCTIONAL_PROOF_WITHDRAWN'
    assert not result['steps']['lower_semi_continuity']['functional_lsc_proved']
    assert not lsc_check([])['functional_lsc_proved']
    assert result['lean4']['historical_claimed_increment'] == 18
    assert 'remain open' in result['honest_note']


@pytest.mark.parametrize('phi_star', [0.0, 1.0, -1.0, float('nan')])
def test_positive_sample_is_not_a_uniqueness_certificate(phi_star):
    result = uniqueness_certificate(phi_star)
    assert not result['unique']
    assert result['sample_positive']
