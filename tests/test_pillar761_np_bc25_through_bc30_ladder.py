# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 761: NP-BC-25 through BC-30 ladder."""
import pytest
from src.core.pillar761_np_bc25_through_bc30_ladder import (
    np_bc25_bc30_ladder,
    np_bc25_radion_self_energy, np_bc26_casimir_winding,
    np_bc27_gravitino_stability, np_bc28_yukawa_threshold,
    np_bc29_baryogenesis_6d_tower, np_bc30_weyl_anomaly,
    PILLAR, STATUS, K_CS, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 761
    def test_status(self): assert STATUS == 'CLOSED'
    def test_k_cs(self): assert K_CS == 74
    def test_no_toe_score(self): import src.core.pillar761_np_bc25_through_bc30_ladder as m; assert not hasattr(m, 'toe_score')


class TestSubGaps:
    def test_bc25_within_limit(self):
        r = np_bc25_radion_self_energy()
        assert r['within_limit']
        assert r['delta_m_over_m'] < 0.003

    def test_bc26_planck_suppressed(self):
        r = np_bc26_casimir_winding()
        assert r['architecture_limit']
        assert r['casimir_prefactor'] < 0
        assert r['e_casimir_over_mpl4'] < 1e-50

    def test_bc27_stable(self):
        r = np_bc27_gravitino_stability()
        assert r['stable']
        assert r['radiative_shift'] < 1e-10

    def test_bc28_within_2loop(self):
        r = np_bc28_yukawa_threshold()
        assert r['within_2loop']
        assert r['delta_Y_over_Y'] < 0.01

    def test_bc29_adjacent_track(self):
        r = np_bc29_baryogenesis_6d_tower()
        assert r.get('adjacent_track')
        assert r['status'] == 'ADJACENT_TRACK'

    def test_bc30_weyl_ratio(self):
        r = np_bc30_weyl_anomaly()
        assert 0 < r['ratio'] < 0.1


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return np_bc25_bc30_ladder()

    def test_pillar_field(self, result): assert result['pillar'] == 761
    def test_six_sub_gaps(self, result): assert len(result['sub_gaps']) == 6
    def test_no_hardgate_promotions(self, result): assert result['summary']['no_hardgate_promotions']
    def test_extends_p741(self, result): assert '741' in result['extends']
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_all_gaps_present(self, result):
        for bc in [f'NP-BC-{i}' for i in range(25, 31)]:
            assert bc in result['sub_gaps']
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar761_np_bc25_through_bc30_ladder as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s)
