# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 768: Sprint AG Regression Certificate."""
import pytest
from src.core.pillar768_sprint_ag_regression_certificate import (
    sprint_ag_certificate, SPRINT_AG_CERTIFICATE,
    PILLAR, STATUS, EPISTEMIC_LABEL, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 768
    def test_status(self): assert STATUS == 'CERTIFIED'
    def test_epistemic(self): assert EPISTEMIC_LABEL == 'DERIVED'
    def test_no_toe_score(self): import src.core.pillar768_sprint_ag_regression_certificate as m; assert not hasattr(m, 'toe_score')


class TestCertificate:
    def test_version(self): assert SPRINT_AG_CERTIFICATE['version'] == 'v22.3'
    def test_sprint(self): assert SPRINT_AG_CERTIFICATE['sprint'] == 'Sprint AG'
    def test_pillar_range(self): assert SPRINT_AG_CERTIFICATE['pillar_range'] == '759–768'
    def test_pillar_total(self): assert SPRINT_AG_CERTIFICATE['pillar_total'] == 768
    def test_new_pillars(self): assert SPRINT_AG_CERTIFICATE['new_pillars'] == 10
    def test_lean4_prev(self): assert SPRINT_AG_CERTIFICATE['lean4_summary']['prev_total'] == 762
    def test_lean4_new(self): assert SPRINT_AG_CERTIFICATE['lean4_summary']['new_theorems'] == 58
    def test_lean4_total(self): assert SPRINT_AG_CERTIFICATE['lean4_summary']['new_total'] == 820
    def test_lean4_milestone(self): assert '800' in SPRINT_AG_CERTIFICATE['lean4_summary']['milestone']
    def test_no_toe_in_cert(self): assert 'toe_score' not in SPRINT_AG_CERTIFICATE


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return sprint_ag_certificate()

    def test_pillar_field(self, result): assert result['pillar'] == 768
    def test_label(self, result): assert result['label'] == 'SPRINT_AG_REGRESSION_CERTIFICATE'
    def test_status_certified(self, result): assert result['status'] == 'CERTIFIED'
    def test_next_sprint_ah(self, result): assert result['next_sprint']['label'] == 'AH'
    def test_next_slot_769(self, result): assert result['next_sprint']['next_pillar_slot'] == 769
    def test_candidates_present(self, result): assert len(result['next_sprint']['candidates']) >= 5
    def test_honest_note(self, result): assert 'Admission 1' in result['honest_note']
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar768_sprint_ag_regression_certificate as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s)
