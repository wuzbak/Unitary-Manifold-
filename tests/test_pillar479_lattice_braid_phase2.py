# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 479 — Lattice Braid QFT Phase 2: 2D Transfer Matrix."""
from __future__ import annotations

import math

from src.core.pillar479_lattice_braid_phase2 import (
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    BETA_BRAID,
    BETA_BKT,
    ETA_BKT_CRITICAL,
    ETA_BRAID,
    anomalous_dimension,
    helicity_modulus,
    correlation_function_2d,
    c1_lattice_2d,
    string_tension_2d,
    finite_size_helicity,
    bkt_phase_verdict,
    phase2_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'LATTICE_BRAID_PHASE2_2D_COMPUTED'

    def test_adjacency(self):
        assert '🔵' in ADJACENCY_TRACK_LABEL

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 479

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0/37.0) < 1e-10

    def test_beta_braid(self):
        expected = 74 / (4 * math.pi ** 2)
        assert abs(BETA_BRAID - expected) < 1e-10

    def test_beta_bkt(self):
        assert BETA_BKT > 0.0
        assert BETA_BKT < 2.0

    def test_beta_braid_above_bkt(self):
        assert BETA_BRAID > BETA_BKT

    def test_eta_bkt_critical(self):
        assert abs(ETA_BKT_CRITICAL - 0.25) < 1e-10

    def test_eta_braid(self):
        expected = 1.0 / (2.0 * math.pi * BETA_BRAID)
        assert abs(ETA_BRAID - expected) < 1e-10

    def test_eta_braid_less_than_bkt(self):
        # In QLRO phase: η < η_BKT = 0.25
        assert ETA_BRAID < ETA_BKT_CRITICAL


class TestAnomalousDimension:
    def test_at_braid_coupling(self):
        eta = anomalous_dimension(BETA_BRAID)
        assert abs(eta - ETA_BRAID) < 1e-10

    def test_decreases_with_beta(self):
        # η = 1/(2πβ) decreases as β increases
        e1 = anomalous_dimension(1.0)
        e2 = anomalous_dimension(2.0)
        assert e2 < e1

    def test_at_bkt_critical(self):
        # At β_BKT: η = 1/(2π × 1.1) ≈ 0.145, not exactly 0.25
        # But η_BKT = 0.25 is the SPECIAL value at the BKT transition
        # Our formula η(β) = 1/(2πβ); at β=1/(2π × 0.25) ≈ 0.637
        eta = anomalous_dimension(1.0 / (2.0 * math.pi * 0.25))
        assert abs(eta - 0.25) < 0.01

    def test_positive(self):
        assert anomalous_dimension(BETA_BRAID) > 0.0

    def test_less_than_quarter_at_braid(self):
        assert anomalous_dimension(BETA_BRAID) < 0.25

    def test_order_of_magnitude(self):
        # Expected ~0.0849
        eta = anomalous_dimension(BETA_BRAID)
        assert 0.05 < eta < 0.15


class TestHelicityModulus:
    def test_positive_in_qlro(self):
        # β_braid >> β_BKT → QLRO → Υ > 0
        assert helicity_modulus(BETA_BRAID) > 0.0

    def test_less_than_beta(self):
        # Υ < β (correction is negative)
        assert helicity_modulus(BETA_BRAID) < BETA_BRAID

    def test_zero_or_low_at_small_beta(self):
        # Very small β → disordered → Υ ≈ 0
        assert helicity_modulus(0.1, l_size=100) < 0.1

    def test_increases_with_beta(self):
        u1 = helicity_modulus(1.5)
        u2 = helicity_modulus(2.5)
        assert u2 > u1


class TestCorrelationFunction2D:
    def test_at_zero_is_one(self):
        assert correlation_function_2d(0.0, BETA_BRAID) == 1.0

    def test_positive(self):
        assert correlation_function_2d(5.0, BETA_BRAID) > 0.0

    def test_decreases_with_distance(self):
        g1 = correlation_function_2d(1.0, BETA_BRAID)
        g2 = correlation_function_2d(10.0, BETA_BRAID)
        assert g2 < g1

    def test_algebraic_decay(self):
        # G(r) = r^(-η); check ratio
        eta = anomalous_dimension(BETA_BRAID)
        r1, r2 = 2.0, 8.0
        g1 = correlation_function_2d(r1, BETA_BRAID)
        g2 = correlation_function_2d(r2, BETA_BRAID)
        # g2/g1 should equal (r2/r1)^(-η)
        expected_ratio = (r2 / r1) ** (-eta)
        assert abs(g2 / g1 - expected_ratio) < 1e-10


class TestC1Lattice2D:
    def setup_method(self):
        self.result = c1_lattice_2d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_c1_positive(self):
        assert self.result['c1_lattice_2d'] > 0.0

    def test_convergence_fraction(self):
        assert 0.0 < self.result['convergence_fraction'] <= 2.0

    def test_verdict_set(self):
        assert self.result['verdict'] in ('CONVERGENT_2D', 'INSUFFICIENT')

    def test_has_eta(self):
        assert 'eta_beta' in self.result

    def test_eta_matches_anomalous_dim(self):
        assert abs(self.result['eta_beta'] - anomalous_dimension(BETA_BRAID)) < 1e-10


class TestStringTension2D:
    def setup_method(self):
        self.result = string_tension_2d()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_true_string_tension_zero(self):
        # In QLRO phase: true string tension = 0
        assert self.result['true_string_tension'] == 0.0

    def test_phase_is_qlro(self):
        assert self.result['phase'] == 'QLRO_BKT'

    def test_has_profile(self):
        assert 'profile' in self.result
        assert len(self.result['profile']) > 0

    def test_profile_decreasing_correlation(self):
        profile = self.result['profile']
        corrs = [p['correlation'] for p in profile]
        for i in range(len(corrs) - 1):
            assert corrs[i] > corrs[i + 1]


class TestFiniteSizeHelicity:
    def setup_method(self):
        self.result = finite_size_helicity()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_qlro_phase(self):
        assert self.result['phase'] == 'QLRO'

    def test_positive_extrapolated(self):
        assert self.result['upsilon_extrapolated'] > 0.0

    def test_verdict_bkt_confirmed(self):
        assert self.result['verdict'] == 'BKT_QLRO_CONFIRMED'

    def test_l_values_match_upsilon(self):
        assert len(self.result['l_values']) == len(self.result['upsilon_values'])


class TestBKTPhaseVerdict:
    def setup_method(self):
        self.verdict = bkt_phase_verdict()

    def test_returns_dict(self):
        assert isinstance(self.verdict, dict)

    def test_above_bkt(self):
        assert self.verdict['above_bkt'] is True

    def test_phase_qlro(self):
        assert self.verdict['phase'] == 'QLRO'

    def test_eta_correct(self):
        assert abs(self.verdict['eta'] - ETA_BRAID) < 1e-10


class TestPhase2Report:
    def setup_method(self):
        self.report = phase2_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_status(self):
        assert self.report['status'] == 'LATTICE_BRAID_PHASE2_2D_COMPUTED'

    def test_adjacency(self):
        assert '🔵' in self.report['adjacency']

    def test_has_observables(self):
        assert 'observables' in self.report
        assert 'eta_anomalous_dim' in self.report['observables']

    def test_eta_reasonable(self):
        eta = self.report['observables']['eta_anomalous_dim']
        assert 0.05 < eta < 0.15

    def test_has_phase_diagnosis(self):
        assert self.report['phase_diagnosis']['phase'] == 'QLRO'

    def test_l2_status_present(self):
        assert 'l2_status' in self.report
