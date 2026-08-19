# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 762: PMNS Solar Angle Full Closure."""
import pytest
from src.core.pillar762_pmns_solar_angle_full_closure import (
    pmns_solar_angle_full_closure, fn_sublattice_correction, nlo_loop_correction,
    SIN2_THETA12_BL, SIN2_THETA12_PDG, SIN2_THETA12_PDG_ERR,
    PILLAR, STATUS, EPISTEMIC_LABEL, TEST_EXPECTATIONS,
)


class TestScalars:
    def test_pillar(self): assert PILLAR == 762
    def test_status(self): assert STATUS == 'CLOSED'
    def test_epistemic(self): assert EPISTEMIC_LABEL == 'GEOMETRIC_PREDICTION'
    def test_bl_baseline(self): assert abs(SIN2_THETA12_BL - 0.300) < 1e-9
    def test_pdg_range(self): assert 0.305 < SIN2_THETA12_PDG < 0.310
    def test_no_toe_score(self): import src.core.pillar762_pmns_solar_angle_full_closure as m; assert not hasattr(m, 'toe_score')


class TestStepA:
    @pytest.fixture(scope='class')
    def step_a(self):
        return fn_sublattice_correction()

    def test_delta_positive(self, step_a): assert step_a['delta_sin2_theta12'] > 0
    def test_s12_improved(self, step_a): assert step_a['s12_after_step_A'] > SIN2_THETA12_BL
    def test_residual_reduced(self, step_a): assert step_a['pdg_residual_pct'] < 2.5


class TestStepB:
    def test_delta_positive(self):
        r = nlo_loop_correction(0.3064)
        assert r['delta_sin2_theta12_loop'] > 0
    def test_final_closer_to_pdg(self):
        r = nlo_loop_correction(0.3064)
        assert abs(r['s12_final'] - SIN2_THETA12_PDG) < abs(0.3064 - SIN2_THETA12_PDG)


class TestMasterResult:
    @pytest.fixture(scope='class')
    def result(self):
        return pmns_solar_angle_full_closure()

    def test_pillar_field(self, result): assert result['pillar'] == 762
    def test_label(self, result): assert 'SOLAR_ANGLE' in result['label']
    def test_baseline_correct(self, result): assert abs(result['baseline_braid_lock'] - 0.300) < 1e-9
    def test_residual_sub_half_pct(self, result): assert result['result']['residual_pct'] < 0.5
    def test_within_1sigma(self, result): assert result['result']['within_1sigma']
    def test_prediction_label(self, result): assert result['result']['label'] == 'GEOMETRIC_PREDICTION'
    def test_no_forbidden(self, result): assert 'toe_score' not in result
    def test_required_keys(self, result):
        for k in TEST_EXPECTATIONS['required_keys']:
            assert k in result


class TestSymbols:
    def test_all_symbols(self):
        import src.core.pillar762_pmns_solar_angle_full_closure as m
        for s in TEST_EXPECTATIONS['required_symbols']:
            assert hasattr(m, s)
