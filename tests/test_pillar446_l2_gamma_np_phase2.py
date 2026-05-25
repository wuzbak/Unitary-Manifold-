# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 446 — L2 γ Gap Phase 2: Non-Perturbative Budget."""
import math
import pytest
from src.core.pillar446_l2_gamma_np_phase2 import (
    PILLAR_STATUS, VERSION,
    GAMMA_FIT, GAMMA_THEORY, GAMMA_GAP, GAMMA_GAP_FRACTION,
    K_CS, PHI0, C_S, N_W,
    KM_FRACTION, ZM_FRACTION, BOREL_PADE_BOUND,
    instanton_fugacity, km_correction_fraction, zm_condensate_fraction,
    cross_term_fraction, total_np_budget, l2_gamma_phase2_verdict, pillar_report,
)


class TestConstants:
    def test_gamma_gap_positive(self):
        assert GAMMA_GAP > 0
        assert abs(GAMMA_GAP - (GAMMA_FIT - GAMMA_THEORY)) < 1e-10

    def test_gamma_gap_fraction(self):
        assert 0.10 < GAMMA_GAP_FRACTION < 0.18  # ~13%

    def test_k_cs(self):
        assert K_CS == 74


class TestInstantonFugacity:
    def test_negligible(self):
        r = instanton_fugacity()
        assert not r['contributes_significantly']
        assert r['z_inst'] < 1e-14   # exp(−37) ≈ 10^{-16}

    def test_action_correct(self):
        r = instanton_fugacity()
        assert abs(r['s_inst'] - K_CS/2) < 1e-10

    def test_log10_very_negative(self):
        r = instanton_fugacity()
        assert r['z_inst_log10'] < -10


class TestKMCorrection:
    def test_fraction_correct(self):
        r = km_correction_fraction()
        assert abs(r['fraction_of_gap'] - KM_FRACTION) < 1e-10

    def test_delta_gamma_positive(self):
        r = km_correction_fraction()
        assert r['delta_gamma_km'] > 0

    def test_c1_km_reasonable(self):
        r = km_correction_fraction()
        assert 2.0 < r['c1_km'] < 5.0


class TestZMCondensate:
    def test_fraction_correct(self):
        r = zm_condensate_fraction()
        assert abs(r['fraction_of_gap'] - ZM_FRACTION) < 1e-10

    def test_theory_value(self):
        r = zm_condensate_fraction()
        expected = 1.0 / (4.0 * PHI0**2)
        assert abs(r['delta_gamma_zm_theory'] - expected) < 1e-10


class TestCrossTermFraction:
    def test_constructive_interference(self):
        r = cross_term_fraction()
        assert r['cos_phase'] == pytest.approx(1.0)

    def test_max_cross_formula(self):
        r = cross_term_fraction()
        expected_max = 2.0 * math.sqrt(KM_FRACTION * ZM_FRACTION)
        assert abs(r['max_cross_fraction'] - expected_max) < 1e-10

    def test_cross_positive(self):
        r = cross_term_fraction()
        assert r['actual_cross_fraction'] > 0

    def test_total_km_zm_cross_gte_90pct(self):
        km = KM_FRACTION
        zm = ZM_FRACTION
        cross = 2.0 * math.sqrt(km * zm)
        assert km + zm + cross > 0.90


class TestTotalBudget:
    def test_verdict_certified(self):
        r = total_np_budget()
        assert r['verdict'] == 'L2_GAMMA_NP_BUDGET_PHASE2_CERTIFIED'

    def test_total_fraction_gte_85pct(self):
        r = total_np_budget()
        assert r['total_fraction_capped'] >= 0.85

    def test_remaining_le_15pct(self):
        r = total_np_budget()
        assert r['remaining_fraction'] <= 0.15

    def test_gamma_values_present(self):
        r = total_np_budget()
        assert 'gamma_gap' in r
        assert 'gamma_fit' in r


class TestVerdict:
    def test_verdict_certified(self):
        v = l2_gamma_phase2_verdict()
        assert v['verdict'] == 'L2_GAMMA_NP_BUDGET_PHASE2_CERTIFIED'

    def test_instanton_excluded(self):
        v = l2_gamma_phase2_verdict()
        assert v['instanton_excluded'] is True

    def test_total_pct(self):
        v = l2_gamma_phase2_verdict()
        assert v['total_gap_covered_pct'] >= 85.0


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 446

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS
