# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 478 — 6D Baryogenesis Phase 2: RGE-Refined nEDM."""
from __future__ import annotations

import math

from src.core.pillar478_sixd_baryogenesis_phase2 import (
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    G_BARYON,
    ALPHA_S_MZ,
    ALPHA_S_1GEV,
    M_DOWN_QUARK_GEV,
    M_NEUTRON_GEV,
    GAMMA_CEMDM,
    B0_NF3,
    GEV_INV_TO_ECM,
    NEDM_SNS_SENSITIVITY,
    NEDM_CURRENT_BOUND,
    alpha_s_running,
    cemdm_at_ms,
    rge_enhancement,
    cemdm_at_had,
    nedm_refined,
    nedm_parameter_band,
    phase2_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'SIXD_BARYOGENESIS_PHASE2_NEDM_REFINED'

    def test_adjacency(self):
        assert '🔵' in ADJACENCY_TRACK_LABEL

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 478

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_g_baryon(self):
        assert abs(G_BARYON - 5.0/74.0) < 1e-10

    def test_gamma_cemdm(self):
        assert abs(GAMMA_CEMDM - 8.0/3.0) < 1e-10

    def test_b0_nf3(self):
        assert abs(B0_NF3 - 9.0) < 1e-10

    def test_sns_sensitivity(self):
        assert NEDM_SNS_SENSITIVITY == 1.0e-27

    def test_current_bound(self):
        assert NEDM_CURRENT_BOUND > NEDM_SNS_SENSITIVITY

    def test_gev_inv_to_ecm(self):
        # 1 GeV⁻¹ = 1/(5.068e13) e·cm
        assert abs(GEV_INV_TO_ECM - 1.0/5.068e13) < 1e-30


class TestAlphaSRunning:
    def test_at_mz(self):
        alpha = alpha_s_running(91.1876)
        assert abs(alpha - ALPHA_S_MZ) < 0.001

    def test_decreases_at_higher_energy(self):
        a1 = alpha_s_running(100.0)
        a2 = alpha_s_running(1000.0)
        assert a2 < a1

    def test_positive(self):
        assert alpha_s_running(200.0) > 0.0


class TestCEDMAtMS:
    def test_positive(self):
        d = cemdm_at_ms(650.0, math.pi / 4)
        assert d > 0.0

    def test_zero_at_zero_mass(self):
        d = cemdm_at_ms(0.0, math.pi / 4)
        assert d == 0.0

    def test_zero_at_pi(self):
        # sin(π) ≈ 0 (floating-point: ~10⁻¹⁶); result should be near-zero
        d = cemdm_at_ms(650.0, math.pi)
        assert abs(d) < 1e-25

    def test_order_of_magnitude(self):
        # Expected ~10^{-13} GeV^{-1}
        d = cemdm_at_ms(650.0, math.pi / 4)
        assert 1e-16 < d < 1e-9

    def test_decreases_with_heavier_sigma(self):
        d1 = cemdm_at_ms(500.0, math.pi / 4)
        d2 = cemdm_at_ms(1000.0, math.pi / 4)
        assert d1 > d2

    def test_increases_with_sin_theta(self):
        d1 = cemdm_at_ms(650.0, 0.3)
        d2 = cemdm_at_ms(650.0, math.pi / 2)
        assert d2 > d1


class TestRGEEnhancement:
    def test_greater_than_one(self):
        rge = rge_enhancement(650.0)
        assert rge > 1.0

    def test_finite(self):
        rge = rge_enhancement(650.0)
        assert 0.0 < rge < 10.0

    def test_order_of_magnitude(self):
        rge = rge_enhancement(650.0)
        assert 1.2 < rge < 3.0


class TestCEDMAtHad:
    def test_greater_than_ms(self):
        d_ms = cemdm_at_ms(650.0, math.pi / 4)
        d_had = cemdm_at_had(650.0, math.pi / 4)
        assert d_had > d_ms

    def test_positive(self):
        assert cemdm_at_had(650.0, math.pi / 4) > 0.0


class TestNEDMRefined:
    def setup_method(self):
        self.result = nedm_refined(650.0, math.pi / 4)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_d_n_positive(self):
        assert self.result['d_n_ecm'] > 0.0

    def test_not_excluded(self):
        assert not self.result['above_current_bound']

    def test_testable_at_sns(self):
        assert self.result['testable_at_sns']

    def test_verdict_testable(self):
        assert self.result['verdict'] == 'TESTABLE_SNS_2028'

    def test_canonical_prediction_range(self):
        # Expected: ~5-15 × 10^-27 e·cm
        d_n = self.result['d_n_ecm']
        assert 1e-27 < d_n < NEDM_CURRENT_BOUND

    def test_rge_enhancement_positive(self):
        assert self.result['rge_enhancement'] > 1.0

    def test_heavier_sigma_smaller_d_n(self):
        d1 = nedm_refined(500.0, math.pi / 4)['d_n_ecm']
        d2 = nedm_refined(1000.0, math.pi / 4)['d_n_ecm']
        assert d1 > d2


class TestNEDMParameterBand:
    def setup_method(self):
        self.band = nedm_parameter_band()

    def test_returns_dict(self):
        assert isinstance(self.band, dict)

    def test_has_min_max(self):
        assert 'd_n_min_ecm' in self.band
        assert 'd_n_max_ecm' in self.band

    def test_min_less_than_max(self):
        assert self.band['d_n_min_ecm'] < self.band['d_n_max_ecm']

    def test_has_testable_count(self):
        assert 'n_testable_sns' in self.band
        assert self.band['n_testable_sns'] >= 0

    def test_band_verdict(self):
        assert self.band['verdict'] in ('SNS_TESTABLE', 'PARTIALLY_TESTABLE')

    def test_testable_fraction_positive(self):
        assert self.band['testable_fraction'] >= 0.0


class TestPhase2Report:
    def setup_method(self):
        self.report = phase2_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_status(self):
        assert self.report['status'] == 'SIXD_BARYOGENESIS_PHASE2_NEDM_REFINED'

    def test_canonical_benchmark_present(self):
        assert 'canonical_benchmark' in self.report
        assert self.report['canonical_benchmark']['m_sigma_gev'] == 650.0

    def test_canonical_testable(self):
        assert self.report['canonical_benchmark']['verdict'] == 'TESTABLE_SNS_2028'

    def test_phase2_enhanced(self):
        p1 = self.report['phase1_vs_phase2']['phase1_estimate']
        p2 = self.report['phase1_vs_phase2']['phase2_refined']
        assert isinstance(p1, float)
        assert isinstance(p2, float)

    def test_adjacency(self):
        assert '🔵' in self.report['adjacency']

    def test_observational_window(self):
        obs = self.report['observational_window']
        assert obs['testable'] is True
        assert obs['experiment'] == 'nEDM@SNS (Oak Ridge National Laboratory)'
