# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 765: LiteBIRD v2 Falsification Audit."""
import pytest
from src.core.pillar765_litebird_v2_falsification_audit import (
    litebird_v2_falsification_audit, canonical_beta, nlo_beta_correction,
    admissible_window_check, K_CS, K_CS_SHADOW, LEAN4_TOTAL,
    BETA_PRIMARY_DEG, BETA_SHADOW_DEG,
    BETA_WINDOW_MIN, BETA_WINDOW_MAX, GAP_MIN, GAP_MAX,
    PILLAR, STATUS, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 765
    def test_status(self): assert STATUS == 'CLOSED'
    def test_lean4_total(self): assert LEAN4_TOTAL == 820
    def test_k_cs(self): assert K_CS == 74
    def test_k_cs_shadow(self): assert K_CS_SHADOW == 61
    def test_beta_primary(self): assert abs(BETA_PRIMARY_DEG - 0.331) < 0.002
    def test_beta_shadow_approx(self): assert abs(BETA_SHADOW_DEG - 0.273) < 0.003
    def test_shadow_ratio(self):
        assert abs(BETA_SHADOW_DEG / BETA_PRIMARY_DEG - K_CS_SHADOW / K_CS) < 1e-9
    def test_no_toe_score(self):
        import src.core.pillar765_litebird_v2_falsification_audit as m
        assert not hasattr(m, 'toe_score')


class TestBetaComputation:
    def test_beta_primary_in_window(self):
        b = canonical_beta(K_CS)
        assert BETA_WINDOW_MIN < b < BETA_WINDOW_MAX

    def test_beta_shadow_in_window(self):
        b = canonical_beta(K_CS_SHADOW)
        assert BETA_WINDOW_MIN < b < BETA_WINDOW_MAX

    def test_beta_primary_gt_shadow(self):
        assert canonical_beta(K_CS) > canonical_beta(K_CS_SHADOW)

    def test_beta_primary_approx_0331(self):
        assert abs(canonical_beta(K_CS) - 0.331) < 0.001

    def test_beta_shadow_approx_0273(self):
        assert abs(canonical_beta(K_CS_SHADOW) - 0.273) < 0.003

    def test_nlo_correction_positive(self):
        b = canonical_beta(K_CS)
        assert nlo_beta_correction(b) > 0

    def test_nlo_correction_small(self):
        b = canonical_beta(K_CS)
        assert nlo_beta_correction(b) < 0.05 * b


class TestAdmissibleWindow:
    def test_primary_in_window_consistent(self):
        assert admissible_window_check(0.331) == 'CONSISTENT'

    def test_shadow_in_window_consistent(self):
        assert admissible_window_check(0.273) == 'CONSISTENT'

    def test_in_gap_falsified(self):
        assert admissible_window_check(0.300) == 'FALSIFIED_BRAIDED_MECHANISM'

    def test_outside_window_falsified(self):
        assert admissible_window_check(0.10) == 'FALSIFIED'
        assert admissible_window_check(0.50) == 'FALSIFIED'


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return litebird_v2_falsification_audit()

    def test_pillar_field(self, result): assert result['pillar'] == 765
    def test_all_predictions_consistent(self, result):
        assert result['all_predictions_consistent']
    def test_lean4_new(self, result): assert result['lean4']['new_theorems'] == 8
    def test_lean4_total(self, result): assert result['lean4']['new_total'] == 820
    def test_four_branches(self, result): assert len(result['verdict_branches']) == 4
    def test_primary_lo_consistent(self, result):
        assert result['consistency_checks']['primary_lo'] == 'CONSISTENT'
    def test_shadow_lo_consistent(self, result):
        assert result['consistency_checks']['shadow_lo'] == 'CONSISTENT'
    def test_primary_nlo_consistent(self, result):
        assert result['consistency_checks']['primary_nlo'] == 'CONSISTENT'
    def test_honest_note(self, result): assert 'PRIMARY' in result['honest_note']
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_canonical_primary(self, result):
        assert abs(result['predictions']['canonical']['beta_primary'] - 0.331) < 0.001
    def test_canonical_shadow(self, result):
        assert abs(result['predictions']['canonical']['beta_shadow'] - 0.273) < 0.003
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar765_litebird_v2_falsification_audit as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s), f"Missing symbol: {s}"
