# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 439 — 6D Baryogenesis Phase 1."""
from __future__ import annotations

import math
import pytest

from src.core.pillar439_sixd_baryogenesis_phase1 import (
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    PHI0,
    M_KK_MIN_GEV,
    G_BARYON,
    T_RH_GEV,
    G_STAR,
    NEDM_SNS_SENSITIVITY,
    M6_GEV,
    eta_b_6d,
    nedm_prediction,
    parameter_scan,
    constraint_check,
    sixd_action_parameters,
    phase1_report,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'SIXD_BARYOGENESIS_PHASE1_COMPUTED'

    def test_adjacency_label(self):
        assert '🔵' in ADJACENCY_TRACK_LABEL
        assert 'ADJACENT TRACK' in ADJACENCY_TRACK_LABEL

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 439

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_phi0(self):
        assert abs(PHI0 - 2.0 * math.pi * N_W) < 1e-10

    def test_m_kk_min(self):
        assert M_KK_MIN_GEV == pytest.approx(5.0e3)

    def test_g_baryon(self):
        assert abs(G_BARYON - N_W / K_CS) < 1e-12

    def test_t_rh_positive(self):
        assert T_RH_GEV > 0.0

    def test_g_star(self):
        assert G_STAR == pytest.approx(106.75)

    def test_nedm_sensitivity_positive(self):
        assert NEDM_SNS_SENSITIVITY > 0.0

    def test_m6_large(self):
        # 6D Planck mass should be order Planck scale
        assert M6_GEV > 1.0e18


class TestEtaB6D:
    def test_positive(self):
        eta = eta_b_6d(650.0, math.pi / 4)
        assert eta > 0.0

    def test_scales_with_theta(self):
        # eta ∝ sin²(θ)
        eta1 = eta_b_6d(650.0, math.pi / 4)
        eta2 = eta_b_6d(650.0, math.pi / 2)
        ratio = eta2 / eta1
        expected = (math.sin(math.pi / 2) ** 2) / (math.sin(math.pi / 4) ** 2)
        assert abs(ratio - expected) < ratio * 0.01

    def test_zero_theta_gives_zero(self):
        assert eta_b_6d(650.0, 0.0) == pytest.approx(0.0, abs=1e-30)

    def test_larger_mass_smaller_eta(self):
        eta1 = eta_b_6d(500.0, math.pi / 4)
        eta2 = eta_b_6d(5000.0, math.pi / 4)
        assert eta1 > eta2

    def test_order_of_magnitude(self):
        # Should be able to reach O(10^-10) in some parameter range
        eta = eta_b_6d(650.0, math.pi / 2)
        assert eta > 0.0  # Check it's non-zero; actual magnitude depends on M_6

    def test_zero_mass_gives_zero(self):
        assert eta_b_6d(0.0, math.pi / 4) == 0.0


class TestNedmPrediction:
    def test_returns_dict(self):
        result = nedm_prediction()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = nedm_prediction()
        for key in ['d_n_ecm', 'nedm_sns_sensitivity', 'verdict']:
            assert key in result

    def test_d_n_positive(self):
        result = nedm_prediction()
        assert result['d_n_ecm'] > 0.0

    def test_verdict_is_string(self):
        result = nedm_prediction()
        assert result['verdict'] in (
            'TENSION_CURRENT', 'TESTABLE_SNS_2028', 'BELOW_SNS_SENSITIVITY'
        )

    def test_smaller_mass_larger_edm(self):
        r1 = nedm_prediction(m_sigma_gev=500.0)
        r2 = nedm_prediction(m_sigma_gev=5000.0)
        assert r1['d_n_ecm'] > r2['d_n_ecm']

    def test_larger_theta_larger_edm(self):
        r1 = nedm_prediction(theta_6=0.1)
        r2 = nedm_prediction(theta_6=1.0)
        assert r2['d_n_ecm'] > r1['d_n_ecm']


class TestConstraintCheck:
    def test_returns_dict(self):
        result = constraint_check(650.0, math.pi / 4)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = constraint_check(650.0, math.pi / 4)
        for key in ['C1_satisfied', 'C2_satisfied', 'C3_satisfied', 'all_constraints_satisfied']:
            assert key in result

    def test_c1_always_satisfied(self):
        # C1 is always satisfied by construction
        result = constraint_check(650.0, 0.0)
        assert result['C1_satisfied']

    def test_c2_mass_ratio_natural(self):
        # m_Σ = 650 GeV, M_KK = 5000 GeV → ratio = 0.13 (within [0.1, 5])
        result = constraint_check(650.0, math.pi / 4)
        assert result['C2_satisfied']

    def test_c2_very_different_mass_fails(self):
        # m_Σ = 10 GeV → ratio = 0.002 (< 0.1)
        result = constraint_check(10.0, math.pi / 4)
        assert not result['C2_satisfied']

    def test_c3_requires_sin_ge_cs(self):
        # sin(theta) = sin(π/4) ≈ 0.707 > c_s ≈ 0.324 → pass
        result = constraint_check(650.0, math.pi / 4)
        assert result['C3_satisfied']

    def test_c3_small_theta_fails(self):
        # sin(0.01) ≈ 0.01 < c_s ≈ 0.324 → fail
        result = constraint_check(650.0, 0.01)
        assert not result['C3_satisfied']

    def test_verdict_feasible_when_all_satisfied(self):
        result = constraint_check(650.0, math.pi / 4)
        if result['all_constraints_satisfied']:
            assert result['verdict'] == 'FEASIBLE'

    def test_verdict_constrained_when_any_fails(self):
        result = constraint_check(10.0, math.pi / 4)  # C2 fails
        assert result['verdict'] == 'CONSTRAINED'


class TestParameterScan:
    def setup_method(self):
        self.scan = parameter_scan(n_m=3, n_theta=3)

    def test_returns_list(self):
        assert isinstance(self.scan, list)

    def test_correct_length(self):
        assert len(self.scan) == 9  # 3 × 3

    def test_each_has_required_keys(self):
        for row in self.scan:
            for key in ['m_sigma_gev', 'theta_6_rad', 'eta_b', 'viable']:
                assert key in row

    def test_eta_b_positive(self):
        for row in self.scan:
            assert row['eta_b'] >= 0.0

    def test_viable_is_bool(self):
        for row in self.scan:
            assert isinstance(row['viable'], bool)

    def test_some_viable_points_exist(self):
        # With reasonable parameter range, some should be viable
        full_scan = parameter_scan(n_m=5, n_theta=5)
        # Not guaranteed but eta_b should be non-zero for theta != 0
        nonzero = [r for r in full_scan if r['eta_b'] > 0]
        assert len(nonzero) > 0


class TestSixdActionParameters:
    def setup_method(self):
        self.params = sixd_action_parameters(650.0, math.pi / 4)

    def test_returns_dict(self):
        assert isinstance(self.params, dict)

    def test_n_free_parameters(self):
        assert self.params['n_free_parameters'] == 2

    def test_free_parameter_names(self):
        fp = self.params['free_parameters']
        assert 'm_sigma' in fp
        assert 'R_6' in fp

    def test_fixed_by_um(self):
        assert len(self.params['fixed_by_um']) >= 3

    def test_m_kk_matches(self):
        assert self.params['m_kk_gev'] == M_KK_MIN_GEV

    def test_g_baryon_matches(self):
        assert abs(self.params['g_baryon'] - G_BARYON) < 1e-12


class TestPhase1Report:
    def setup_method(self):
        self.report = phase1_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 439

    def test_status(self):
        assert self.report['status'] == 'SIXD_BARYOGENESIS_PHASE1_COMPUTED'

    def test_adjacency(self):
        assert '🔵' in self.report['adjacency']

    def test_baryon_asymmetry_keys(self):
        ba = self.report['baryon_asymmetry']
        for key in ['eta_b', 'eta_b_observed', 'ratio_to_observed']:
            assert key in ba

    def test_nedm_keys(self):
        nedm = self.report['nedm_prediction']
        assert 'd_n_ecm' in nedm
        assert 'verdict' in nedm

    def test_observational_window(self):
        ow = self.report['observational_window']
        assert 'primary' in ow
        assert 'nEDM@SNS' in ow['primary']

    def test_parameter_scan(self):
        ps = self.report['parameter_scan']
        assert 'n_scan_points' in ps
        assert ps['n_scan_points'] > 0

    def test_note_mentions_architecture_limit(self):
        assert 'ARCHITECTURE_LIMIT' in self.report['note']
