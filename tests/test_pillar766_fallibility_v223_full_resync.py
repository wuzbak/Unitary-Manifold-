# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 766: FALLIBILITY v22.3 Resync."""
import pytest
from src.core.pillar766_fallibility_v223_full_resync import (
    fallibility_v223_full_resync, ADMISSIONS, ARCHITECTURE_LIMITS,
    EXTERNAL_FALSIFIERS, OPEN_ADMISSIONS,
    PILLAR, STATUS, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 766
    def test_status(self): assert STATUS == 'CLOSED'
    def test_admissions_count(self): assert len(ADMISSIONS) == 13
    def test_arch_limits_count(self): assert len(ARCHITECTURE_LIMITS) == 8
    def test_open_admissions(self): assert 1 in OPEN_ADMISSIONS
    def test_no_toe_score(self): import src.core.pillar766_fallibility_v223_full_resync as m; assert not hasattr(m, 'toe_score')


class TestAdmissions:
    def test_admission_3_closed(self): assert ADMISSIONS[3]['status'] == 'CLOSED'
    def test_admission_7_layer3_closed(self): assert ADMISSIONS[7]['status'] == 'LAYER3_CLOSED'
    def test_admission_1_open(self): assert ADMISSIONS[1]['status'] == 'OPEN'
    def test_all_admissions_have_text(self):
        for v in ADMISSIONS.values():
            assert len(v['text']) > 5
    def test_all_admissions_have_addressed_by(self):
        for v in ADMISSIONS.values():
            assert 'addressed_by' in v


class TestFalsifiers:
    def test_litebird_present(self): assert 'LiteBIRD_birefringence' in EXTERNAL_FALSIFIERS
    def test_cmb_s4_present(self): assert 'CMB_S4_r_tensor' in EXTERNAL_FALSIFIERS
    def test_desi_present(self): assert 'DESI_DR3_wa' in EXTERNAL_FALSIFIERS
    def test_six_falsifiers(self): assert len(EXTERNAL_FALSIFIERS) >= 5


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return fallibility_v223_full_resync()

    def test_pillar_field(self, result): assert result['pillar'] == 766
    def test_version(self, result): assert result['version'] == 'v22.3'
    def test_sprint(self, result): assert result['sprint'] == 'Sprint AG'
    def test_admissions_total(self, result): assert result['admissions']['total'] == 13
    def test_open_admissions(self, result): assert result['admissions']['open'] == 1
    def test_sprint_ag_deltas(self, result): assert 'P762' in str(result['sprint_ag_epistemic_deltas'])
    def test_honest_note(self, result): assert 'Admission 1' in result['honest_note']
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar766_fallibility_v223_full_resync as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s)
